from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action

from rest_framework import viewsets
from ..models import Result
from ..serializers.result_serializer import ResultSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser

class ResultViewSet(viewsets.ModelViewSet):
    #permission_classes = [IsAuthenticated]
    queryset = Result.objects.all()
    serializer_class = ResultSerializer
    
    # Método para listar todos los resultados (GET) con soporte de paginación y filtros
    def list(self, request, *args, **kwargs):
        qs = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    # Método para obtener un resultado específico (GET)
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    # Método para crear un nuevo resultado (POST)
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()  # guarda y devuelve la instancia
        # recalcula y guarda (calculate_indicator puede hacer save internamente)
        try:
            instance.calculate_indicator()
        except Exception:
            # no impedir la creación si el cálculo falla; reportarlo en la respuesta
            pass
        # re-serializar la instancia actualizada
        out_serializer = self.get_serializer(instance)
        headers = self.get_success_headers(out_serializer.data)
        return Response(out_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    # Método para actualizar un resultado existente (PUT/PATCH)
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        try:
            instance.calculate_indicator()
        except Exception:
            pass
        out_serializer = self.get_serializer(instance)
        return Response(out_serializer.data)

    # Método para eliminar un resultado (DELETE)
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=False, methods=['get'])
    def detailed(self, request):
        """
        Endpoint personalizado que retorna datos detallados de los resultados
        para el dashboard del frontend, manteniendo paginación si se solicita.
        """
        try:
            # Obtener queryset filtrado y optimizar con select_related para relaciones frecuentes
            qs = self.filter_queryset(self.get_queryset().select_related('indicator', 'headquarters', 'user'))
            page = self.paginate_queryset(qs)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                results_data = serializer.data
            else:
                serializer = self.get_serializer(qs, many=True)
                results_data = serializer.data

            # Estadísticas sobre el conjunto filtrado completo (no sólo la página)
            results_all = qs
            total_results = results_all.count()
            total_indicators = results_all.values('indicator').distinct().count()
            total_headquarters = results_all.values('headquarters').distinct().count()

            # Agrupar por indicador y calcular sumas para promedio
            indicators_data = {}
            for r in results_all:
                ind = r.indicator
                key = ind.id
                if key not in indicators_data:
                    indicators_data[key] = {
                        'id': ind.id,
                        'name': getattr(ind, 'name', None),
                        'code': getattr(ind, 'code', None),
                        'results_count': 0,
                        'values_sum': 0
                    }
                indicators_data[key]['results_count'] += 1
                indicators_data[key]['values_sum'] += (getattr(r, 'calculatedValue', 0) or 0)

            # Calcular promedios y formar el resumen
            indicators_summary = []
            for ind in indicators_data.values():
                count = ind['results_count']
                avg = (ind['values_sum'] / count) if count else 0
                indicators_summary.append({
                    'id': ind['id'],
                    'name': ind['name'],
                    'code': ind['code'],
                    'results_count': ind['results_count'],
                    'avg_value': avg
                })

            response_data = {
                'results': results_data,
                'statistics': {
                    'total_results': total_results,
                    'total_indicators': total_indicators,
                    'total_headquarters': total_headquarters,
                },
                'indicators_summary': indicators_summary
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': 'Error al obtener datos detallados', 'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
