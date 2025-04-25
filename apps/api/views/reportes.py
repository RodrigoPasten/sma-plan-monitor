# apps/api/views/reportes.py
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.reportes.models import TipoReporte, ReporteGenerado
from apps.reportes.services import ReporteService
from ..serializers.reportes import TipoReporteSerializer, ReporteGeneradoSerializer, GenerarReporteSerializer
from drf_yasg.utils import swagger_auto_schema

class TipoReporteViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint para consultar tipos de reportes disponibles.
    """
    queryset = TipoReporte.objects.all()
    serializer_class = TipoReporteSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(tags=['Reportes'])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Reportes'])
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def get_queryset(self):
        # Filtrar tipos de reporte según el rol del usuario
        user = self.request.user
        queryset = TipoReporte.objects.all()

        if user.rol == 'superadmin':
            queryset = queryset.filter(acceso_superadmin=True)
        elif user.rol == 'admin_sma':
            queryset = queryset.filter(acceso_admin_sma=True)
        elif user.rol == 'organismo':
            queryset = queryset.filter(acceso_organismos=True)
        else:
            queryset = queryset.none()

        return queryset


class ReporteGeneradoViewSet(viewsets.ModelViewSet):
    """
    API endpoint para gestionar reportes generados.
    """
    serializer_class = ReporteGeneradoSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(tags=['Reportes'])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Reportes'])
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['Reportes'])
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['Reportes'])
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['Reportes'])
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['Reportes'])
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    def get_queryset(self):
        # Un usuario solo puede ver sus propios reportes (excepto superadmin y admin_sma)
        user = self.request.user
        if user.rol in ['superadmin', 'admin_sma']:
            return ReporteGenerado.objects.all().order_by('-fecha_generacion')
        return ReporteGenerado.objects.filter(usuario=user).order_by('-fecha_generacion')

    @swagger_auto_schema(tags=['Reportes'])
    @action(detail=False, methods=['post'])
    def generar(self, request):
        """
        Genera un nuevo reporte basado en los parámetros proporcionados.
        """
        serializer = GenerarReporteSerializer(data=request.data)
        if serializer.is_valid():
            # Si es usuario de organismo, forzar su propio organismo
            organismo_id = serializer.validated_data.get('organismo_id')
            if request.user.rol == 'organismo':
                organismo_id = request.user.organismo.id

            # Generar el reporte
            reporte = ReporteService.generar_reporte(
                usuario=request.user,
                tipo_reporte_id=serializer.validated_data['tipo_reporte_id'],
                titulo=serializer.validated_data['titulo'],
                organismo_id=organismo_id,
                componente_id=serializer.validated_data.get('componente_id'),
                fecha_inicio=serializer.validated_data.get('fecha_inicio'),
                fecha_fin=serializer.validated_data.get('fecha_fin'),
            )

            if reporte:
                result_serializer = ReporteGeneradoSerializer(
                    reporte,
                    context={'request': request}
                )
                return Response(result_serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(
                    {"error": "No se pudo generar el reporte. Verifique los parámetros."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(tags=['Reportes'])
    @action(detail=True, methods=['get'])
    def descargar(self, request, pk=None):
        """
        Retorna la URL de descarga del reporte.
        """
        reporte = self.get_object()

        # Verificar que el archivo exista
        if not reporte.archivo:
            return Response(
                {"error": "El archivo del reporte no está disponible."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Retornar la URL
        return Response({
            "archivo_url": request.build_absolute_uri(reporte.archivo.url)
        })