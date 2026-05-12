from companies.models.company import Company
from companies.serializers.company_serializer import CompanySerializer
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


class CompanyViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Company.objects.all()
    serializer_class = CompanySerializer

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        company = self.get_object()
        company.status = True
        company.save()
        return Response({'status': 'Company activated'})

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        company = self.get_object()
        company.status = False
        company.save()
        return Response({'status': 'Company deactivated'})