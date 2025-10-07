from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from ..models.entidad_auditoria import EntidadAuditoria
from ..serializers import EntidadAuditoriaSerializer


class FacturaViewSet(viewsets.ModelViewSet):
    queryset = EntidadAuditoria.objects.all()
    serializer_class = EntidadAuditoriaSerializer

    def get_queryset(self):
        return EntidadAuditoria.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        entidad_auditoria = self.get_object()
        entidad_auditoria.status = True  
        entidad_auditoria.save()
        return Response({'status': 'Entidad Auditoria activated'})
