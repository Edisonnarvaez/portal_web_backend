from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from gestionProveedores.models import Factura, Correo
from gestionProveedores.reenviar_correo import reenviar_correo_factura


class ReenviarCorreoView(APIView):
    def post(self, request):
        factura_id = request.data.get('factura_id')
        asunto = request.data.get('asunto')

        if not factura_id or not asunto:
            return Response({'error': 'Faltan datos'}, status=status.HTTP_400_BAD_REQUEST)

        factura = Factura.objects.filter(factura_id_factura_electronica=factura_id).first()
        if not factura:
            return Response({'error': 'Factura no encontrada'}, status=status.HTTP_404_NOT_FOUND)

        correo = Correo.objects.filter(subject__icontains=factura_id).order_by('-date_received').first()
        if not correo:
            return Response({'error': 'Correo original no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        reenviar_correo_factura(correo.from_email, asunto, factura_id)
        return Response({'message': 'Correo enviado correctamente'})
