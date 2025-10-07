from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from gestionProveedores.models import Factura, Correo, ArchivoAdjunto
from django.core.mail import EmailMessage, get_connection
from django.conf import settings
import os
@api_view(['POST'])
def reenviar_correo_factura(request, factura_id):
    try:
        factura = Factura.objects.get(pk=factura_id)
        
        asunto = factura.factura_concepto.split(":")[-1].strip()
        correo = Correo.objects.filter(subject__icontains=asunto).first()

        if not correo:
            return Response({'error': 'Correo original no encontrado'}, status=404)

        archivos = ArchivoAdjunto.objects.filter(correo=correo)
        if not archivos.exists():
            return Response({'error': f'Factura {factura.id}: No hay archivos adjuntos'}, status=404)

        connection = get_connection(
            host='smtp.gmail.com',
            port=587,
            username='programador1@redmedicronips.com.co',
            password='pdyxmklodclisduu',
            use_tls=True
        )

        email = EmailMessage(
            subject="REENVÍO FACTURA XML",
            body="Adjunto nuevamente la factura no conforme.",
            from_email='programador1@redmedicronips.com.co',
            to=[correo.from_email],
            connection=connection
        )

        for archivo in archivos:
            nombre_archivo = archivo.archivo.name.strip().replace('\r', '').replace('\n', '')
            file_path = os.path.join(settings.MEDIA_ROOT, nombre_archivo)
            if os.path.exists(file_path):
                email.attach_file(file_path)

        email.send()
        return Response({'detail': 'Correo reenviado correctamente'}, status=200)

    except Factura.DoesNotExist:
        return Response({'error': 'Factura no encontrada'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)
