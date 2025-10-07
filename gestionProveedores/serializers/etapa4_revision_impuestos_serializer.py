from rest_framework import serializers
from gestionProveedores.models.etapa4_revision_impuestos import RevisionImpuestos
from rest_framework import serializers
from gestionProveedores.models.factura import Factura
from .causal_devolucion_serializer import CausalDevolucionSerializer
from .factura_detalle_serializer import FacturaElectronicaDetalleSerializer
from .etapa2_pendiente_revision_serializer import PendienteRevisionSerializer

class RevisionImpuestosSerializer(serializers.ModelSerializer):
    class Meta:
        model = RevisionImpuestos
        fields = '__all__'



