from rest_framework import viewsets
from ..models import ProcessType
from companies.serializers.process_type_serializer import ProcessTypeSerializer
from rest_framework.permissions import IsAuthenticated


class ProcessTypeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = ProcessType.objects.all()
    serializer_class = ProcessTypeSerializer