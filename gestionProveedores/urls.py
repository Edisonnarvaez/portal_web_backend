from django.urls import path, include
from rest_framework.routers import DefaultRouter
from gestionProveedores import views
from .views.factura_view import FacturaViewSet
from .views.factura_detalle_view import FacturaDetalleViewSet
from .views.causal_devolucion_view import CausalDevolucionViewSet
from .views.centro_costo_view import CentroCostosViewSet
from .views.centro_operaciones_view import CentroOperacionesViewSet
from .views.estado_factura_view import EstadoFacturaViewSet
from .views.estado_impuestos_view import EstadoImpuestosViewSet
from .views.estado_pendiente_r_contable_view import EstadoPendienteRContableViewSet
from .views.estado_revision_view import EstadoRevisionViewSet
from .views.etapa1_gestionar_FE_view import GestionarFEViewSet
from .views.etapa2_pendiente_revision_view import PendienteRevisionViewSet
from .views.etapa3_pendiente_reconocimiento_contable_view import PendienteReconocimientoContableViewSet
from .views.etapa4_revision_impuestos_view import RevisionImpuestosViewSet
from .views.etapa5_revision_contraloria_view import RevisionContraloriaViewSet
from .views.etapa6_pendiente_pago_view import PendientePagoViewSet
from gestionProveedores.views.view import descargar_archivo
from .views.factura_view import FacturaRegistroView
from gestionProveedores.reenviar_correo import reenviar_correo_factura



router = DefaultRouter()
router.register(r'causales_devolucion', CausalDevolucionViewSet)
router.register(r'centro_costos', CentroCostosViewSet)
router.register(r'centro_operaciones', CentroOperacionesViewSet)
router.register(r'estado_facturas', EstadoFacturaViewSet)
router.register(r'estado_impuestos', EstadoImpuestosViewSet)
router.register(r'estado_pendiente_r_contable', EstadoPendienteRContableViewSet)
router.register(r'estado_revision', EstadoRevisionViewSet)
router.register(r'etapa1', GestionarFEViewSet)
router.register(r'etapa2', PendienteRevisionViewSet)
router.register(r'etapa3', PendienteReconocimientoContableViewSet)
router.register(r'etapa4', RevisionImpuestosViewSet)
router.register(r'etapa5', RevisionContraloriaViewSet)
router.register(r'etapa6', PendientePagoViewSet)
router.register(r'facturas_detalles', FacturaDetalleViewSet)
router.register(r'factura', FacturaViewSet)
from gestionProveedores.views.reenviar_correo_view import ReenviarCorreoView

urlpatterns = [
    path('', include(router.urls)),
    path(
        'descargar_archivo/<int:correo_id>/<str:filename>/',
        descargar_archivo,
        name='descargar_archivo'

    ), path(
        'gestionProveedores/facturaRegistro/<int:pk>/',
        FacturaRegistroView.as_view(),
        name='factura-registro'
    ),
    path('reenviar-correo/', ReenviarCorreoView.as_view(), name='reenviar-correo'),
]
