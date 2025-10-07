from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import pyotp
import qrcode
from io import BytesIO
from email.mime.image import MIMEImage
import os
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class App(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
            return self.name

class Role(models.Model):
    name = models.CharField(max_length=50) #, unique=True
    app = models.ForeignKey(App, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} ({self.app.name})"

class User(AbstractUser):
    #role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    roles = models.ManyToManyField(Role, blank=True)
    otp_secret = models.CharField(max_length=32, null=True, blank=True)
    is_2fa_enabled = models.BooleanField(default=False)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)  # Nuevo campo

    def generate_otp_secret(self):
        """Generate a new OTP secret key."""
        self.otp_secret = pyotp.random_base32()
        self.save()

    def verify_otp(self, code):
        """Verify the OTP code."""
        if not self.otp_secret:
            return False
        totp = pyotp.TOTP(self.otp_secret)
        return totp.verify(code)

    def get_totp_uri(self):
        """Get the OTP URI for QR code generation."""
        if not self.otp_secret:
            return None
        totp = pyotp.TOTP(self.otp_secret)
        return totp.provisioning_uri(
            name=self.email,  # Usa el email como identificador
            issuer_name="Red Medicron IPS"  
        )

    def send_2fa_email(self, message, otp_secret=None, otp_uri=None, enabled=True):
        """Send 2FA setup/disable email with QR code if enabled."""
        logger.info(f"Preparando email 2FA para {self.email}, enabled: {enabled}")
        
        context = {
            'user': self,
            'message': message,
            'otp_secret': otp_secret,
            'enabled': enabled
        }

        try:
            html_content = render_to_string('emails/2fa_email.html', context)
            text_content = strip_tags(html_content)

            email = EmailMultiAlternatives(
                subject='Configuración de Autenticación en Dos Pasos',
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[self.email]
            )
            email.attach_alternative(html_content, "text/html")

            # Adjuntar logo
            logo_path = os.path.join(settings.BASE_DIR, 'users', 'templates', 'assets', 'logoslogan.png')
            if os.path.exists(logo_path):
                with open(logo_path, 'rb') as f:
                    logo = MIMEImage(f.read())
                    logo.add_header('Content-ID', '<logo_image>')
                    email.attach(logo)

            # Generar y adjuntar QR code SOLO si 2FA está siendo activado
            if enabled and otp_uri:
                logger.info("Generando código QR para 2FA")
                qr = qrcode.QRCode(version=1, box_size=10, border=5)
                qr.add_data(otp_uri)
                qr.make(fit=True)
                img = qr.make_image(fill_color="black", back_color="white")
                
                # Convertir imagen QR a bytes
                buffer = BytesIO()
                img.save(buffer, format='PNG')
                qr_image = MIMEImage(buffer.getvalue())
                qr_image.add_header('Content-ID', '<qr_code>')
                email.attach(qr_image)

            email.send()
            logger.info(f"Email 2FA enviado exitosamente a {self.email}")
            
        except Exception as e:
            logger.error(f"Error detallado al enviar email 2FA: {str(e)}")
            raise e
