from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, Role
from .serializers import LoginSerializer, UserSerializer, RoleSerializer
from django.contrib.auth import authenticate
import pyotp
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from datetime import datetime
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import os
from email.mime.image import MIMEImage
from django.conf import settings
import logging
from django.core.cache import cache
import uuid
from rest_framework.parsers import MultiPartParser, FormParser

logger = logging.getLogger(__name__)

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        username = serializer.validated_data.get('username')
        password = serializer.validated_data.get('password')
        
        if not username or not password:
            return Response({
                'error': 'Se requieren usuario y contraseña'
            }, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=username, password=password)

        if not user:
            return Response({
                'error': 'Credenciales inválidas'
            }, status=status.HTTP_401_UNAUTHORIZED)

        if not user.is_active:
            return Response({
                'error': 'Cuenta desactivada'
            }, status=status.HTTP_401_UNAUTHORIZED)

        if user.is_2fa_enabled:
            temp_token = str(uuid.uuid4())
            cache.set(f'2fa_{temp_token}', user.id, timeout=300)
            
            return Response({
                'require_2fa': True,
                'temp_token': temp_token,
                'message': 'Verificación 2FA requerida'
            }, status=status.HTTP_200_OK)

        # Si no tiene 2FA, generar tokens JWT
        token = RefreshToken.for_user(user)
        return Response({
            'access': str(token.access_token),
            'refresh': str(token),
            'user': UserSerializer(user).data
        })

class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        temp_token = request.data.get('temp_token')
        otp_code = request.data.get('otp_code')

        if not temp_token or not otp_code:
            return Response({
                'error': 'Se requieren temp_token y otp_code'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validar formato del código OTP
        if not otp_code.isdigit() or len(otp_code) != 6:
            return Response({
                'error': 'El código OTP debe ser de 6 dígitos'
            }, status=status.HTTP_400_BAD_REQUEST)

        user_id = cache.get(f'2fa_{temp_token}')
        if not user_id:
            return Response({
                'error': 'Token temporal inválido o expirado'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(id=user_id)
            
            if not user.is_active:
                return Response({
                    'error': 'La cuenta está desactivada'
                }, status=status.HTTP_401_UNAUTHORIZED)

            if user.verify_otp(otp_code):
                cache.delete(f'2fa_{temp_token}')
                token = RefreshToken.for_user(user)
                return Response({
                    'access': str(token.access_token),
                    'refresh': str(token),
                    'user': UserSerializer(user).data
                })
            
            return Response({
                'error': 'Código OTP inválido'
            }, status=status.HTTP_400_BAD_REQUEST)

        except User.DoesNotExist:
            return Response({
                'error': 'Usuario no encontrado'
            }, status=status.HTTP_404_NOT_FOUND)

# Add these new views
class Enable2FAView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        user.generate_otp_secret()
        user.is_2fa_enabled = True
        user.save()
        
        return Response({
            'secret': user.otp_secret,
            'uri': user.get_totp_uri()
        })

class Verify2FAView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logger.debug(f"Verify2FA request data: {request.data}")
        code = request.data.get('code')
        
        if not code:
            logger.warning("No code provided in 2FA verification request")
            return Response(
                {'error': 'El código es requerido'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        logger.debug(f"Verifying 2FA code for user {request.user.username}")
        if request.user.verify_otp(code):
            logger.info(f"2FA verification successful for user {request.user.username}")
            return Response({
                'valid': True,
                'message': 'Código verificado correctamente'
            })
            
        logger.warning(f"Invalid 2FA code provided for user {request.user.username}")
        return Response({
            'valid': False,
            'error': 'Código inválido'
        }, status=status.HTTP_400_BAD_REQUEST)

class RoleListCreateView(generics.ListCreateAPIView):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [permissions.IsAdminUser]

class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]  # <-- Agrega esto

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class Toggle2FAView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        enable_2fa = request.data.get("enable_2fa")

        if enable_2fa is None:
            return Response(
                {"error": "El parámetro 'enable_2fa' es requerido"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if enable_2fa:
            # ACTIVAR 2FA
            logger.info(f"Activando 2FA para usuario: {user.username}")
            
            # Generar nuevo secreto
            user.generate_otp_secret()
            totp_uri = user.get_totp_uri()
            user.is_2fa_enabled = True
            user.save()

            # Enviar email con QR
            try:
                logger.info(f"Enviando email de activación 2FA a: {user.email}")
                user.send_2fa_email(
                    "La autenticación en dos pasos ha sido activada",
                    otp_secret=user.otp_secret,
                    otp_uri=totp_uri,
                    enabled=True
                )
            except Exception as e:
                logger.error(f"Error sending 2FA email: {e}")

            return Response({
                'message': '2FA activado',
                'secret': user.otp_secret,
                'otp_uri': totp_uri,
                'is_2fa_enabled': True
            }, status=status.HTTP_200_OK)
        else:
            # DESACTIVAR 2FA
            logger.info(f"Desactivando 2FA para usuario: {user.username}")
            
            user.is_2fa_enabled = False
            user.otp_secret = None
            user.save()
            
            # ✅ AGREGAR: Enviar email de notificación de desactivación
            try:
                logger.info(f"Enviando email de desactivación 2FA a: {user.email}")
                user.send_2fa_email(
                    "La autenticación en dos pasos ha sido desactivada",
                    otp_secret=None,
                    otp_uri=None,
                    enabled=False
                )
                logger.info(f"Email de desactivación 2FA enviado exitosamente a: {user.email}")
            except Exception as e:
                logger.error(f"Error enviando email de desactivación 2FA: {str(e)}")
                # No fallar la operación por error de email

            return Response({
                'message': '2FA desactivado',
                'is_2fa_enabled': False
            }, status=status.HTTP_200_OK)

class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]  # Asegúrate que esta línea esté presente
    authentication_classes = []      # Añade esta línea para permitir acceso sin autenticación

    def post(self, request):
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email)
            token = PasswordResetTokenGenerator().make_token(user)
            #reset_url = f"http://localhost:5173/auth/reset-password/{user.pk}/{token}/"  # Ajusta esta URL según tu frontend
            reset_url = f"http://red.redmedicronips.com.co/auth/reset-password/{user.pk}/{token}/" 
            context = {
                'user': user,
                'reset_url': reset_url,
                'year': datetime.now().year
            }

            html_content = render_to_string('emails/password_reset.html', context)
            text_content = strip_tags(html_content)

            email_message = EmailMultiAlternatives(
                subject='Restablecimiento de contraseña',
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[email]
            )
            
            email_message.attach_alternative(html_content, "text/html")

            # Adjuntar logo
            logo_path = os.path.join(settings.BASE_DIR, 'users', 'templates', 'assets', 'logoslogan.png')
            if os.path.exists(logo_path):
                with open(logo_path, 'rb') as f:
                    logo = MIMEImage(f.read())
                    logo.add_header('Content-ID', '<logo_image>')
                    email_message.attach(logo)

            email_message.send()
            return Response({'message': 'Se ha enviado un correo con las instrucciones'}, 
                            status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({'error': 'No existe un usuario con ese correo'}, 
                            status=status.HTTP_404_NOT_FOUND)

class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []  # Añade esta línea

    def post(self, request, user_id, token):
        try:
            user = User.objects.get(pk=user_id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response({'error': 'Token inválido o expirado'}, 
                                status=status.HTTP_400_BAD_REQUEST)

            new_password = request.data.get('new_password')
            if not new_password:
                return Response({'error': 'La nueva contraseña es requerida'}, 
                                status=status.HTTP_400_BAD_REQUEST)

            user.set_password(new_password)
            user.save()
            return Response({'message': 'Contraseña actualizada exitosamente'}, 
                            status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({'error': 'Usuario no encontrado'}, 
                            status=status.HTTP_404_NOT_FOUND)

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        current_password = request.data.get("current_password")
        new_password = request.data.get("new_password")
        # print("Usuario:", user.username)
        # print("old_password recibido:", current_password)
        # print("new_password recibido:", new_password)
        # print("check_password:", user.check_password(current_password))
        if not user.check_password(current_password):
            return Response({"error": "Contraseña actual incorrecta."}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(new_password)
        user.save()
        return Response({"message": "Contraseña cambiada correctamente."}, status=status.HTTP_200_OK)
