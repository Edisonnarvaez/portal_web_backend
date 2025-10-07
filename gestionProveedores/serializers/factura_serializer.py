from rest_framework import serializers
from gestionProveedores.models.factura import Factura
from gestionProveedores.models.estado_factura import EstadoFactura  
from .estado_factura_serializer import EstadoFacturaSerializer
from .causal_devolucion_serializer import CausalDevolucionSerializer
from .factura_detalle_serializer import FacturaElectronicaDetalleSerializer
from .etapa1_gestion_FE_serializer import GestionarFESerializer
from .etapa2_pendiente_revision_serializer import PendienteRevisionSerializer
from .etapa3_pendiente_reconocimiento_contable_serializer import PendienteReconocimientoContableSerializer

class FacturaSerializer(serializers.ModelSerializer):

    factura_estado_factura_id = serializers.PrimaryKeyRelatedField(
        source='factura_estado_factura',
        queryset=EstadoFactura.objects.all(),
        write_only=True
    )

    factura_estado_factura = EstadoFacturaSerializer(read_only=True)
    
    causal_anulacion = CausalDevolucionSerializer(read_only=True)
    causal_contabilidad = CausalDevolucionSerializer(read_only=True)
    causal_revision = CausalDevolucionSerializer(read_only=True)
    causal_impuestos = CausalDevolucionSerializer(read_only=True)
    
    detalles = FacturaElectronicaDetalleSerializer(many=True, read_only=True)
    pendiente_revision = PendienteRevisionSerializer(many=True, read_only=True)
    pendiente_reconocimiento_contable = PendienteReconocimientoContableSerializer(many=True, read_only=True)

    factura_centro_operaciones_nombre = serializers.CharField(source="factura_centro_operaciones.operaciones_nombre", read_only=True)
    factura_centro_costo_nombre = serializers.CharField(source="factura_centro_costo.centro_costo_nombre", read_only=True)
    causal_anulacion_nombre = serializers.CharField(source="causal_anulacion.causal_nombre", read_only=True)
    causal_contabilidad_nombre = serializers.CharField(source="causal_contabilidad.causal_nombre", read_only=True)
    causal_revision_nombre = serializers.CharField(source="causal_revision.causal_nombre", read_only=True)
    causal_impuestos_nombre = serializers.CharField(source="causal_impuestos.causal_nombre", read_only=True)

    class Meta:
        model = Factura
        fields = '__all__'
