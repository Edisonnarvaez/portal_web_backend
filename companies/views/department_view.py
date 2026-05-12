from rest_framework import viewsets
from companies.models.department import Department
from companies.serializers.department_serializer import DepartmentSerializer
from rest_framework.permissions import IsAuthenticated


class DepartmentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Department.objects.select_related('company').all()
    serializer_class = DepartmentSerializer