
from rest_framework import viewsets
from ..models.terceros_municipios import Municipio
from ..serializers.tercero_municipios_serializer import MunicipioSerializer

class MunicipioViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = MunicipioSerializer

    def get_queryset(self):
        qs = Municipio.objects.filter(municipio_departamento__departamento_pais__pais_nombre="Colombia")
        departamento_id = self.request.query_params.get('departamento_id')
        if departamento_id:
            qs = qs.filter(municipio_departamento_id=departamento_id)
        return qs
