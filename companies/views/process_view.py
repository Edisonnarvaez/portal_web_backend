from rest_framework import viewsets
from ..models import Process
from companies.serializers.process_serializer import ProcessSerializer
from rest_framework.permissions import IsAuthenticated


class ProcessViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Process.objects.all()
    serializer_class = ProcessSerializer