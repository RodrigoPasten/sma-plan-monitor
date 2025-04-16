# apps/api/serializers/reportes.py
from rest_framework import serializers
from apps.reportes.models import TipoReporte, ReporteGenerado
from apps.organismos.models import Organismo
from apps.medidas.models import Componente


class TipoReporteSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoReporte
        fields = ['id', 'nombre', 'descripcion', 'tipo', 'acceso_superadmin',
                  'acceso_admin_sma', 'acceso_organismos', 'created_at']


class ReporteGeneradoSerializer(serializers.ModelSerializer):
    tipo_reporte_nombre = serializers.ReadOnlyField(source='tipo_reporte.nombre')
    usuario_nombre = serializers.ReadOnlyField(source='usuario.username')
    organismo_nombre = serializers.ReadOnlyField(source='organismo.nombre', default=None)
    componente_nombre = serializers.ReadOnlyField(source='componente.nombre', default=None)
    archivo_url = serializers.SerializerMethodField()

    class Meta:
        model = ReporteGenerado
        fields = ['id', 'tipo_reporte', 'tipo_reporte_nombre', 'usuario', 'usuario_nombre',
                  'titulo', 'fecha_generacion', 'parametros', 'organismo', 'organismo_nombre',
                  'componente', 'componente_nombre', 'archivo_url']
        read_only_fields = ['fecha_generacion', 'archivo']

    def get_archivo_url(self, obj):
        if obj.archivo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.archivo.url)
        return None


class GenerarReporteSerializer(serializers.Serializer):
    tipo_reporte_id = serializers.IntegerField()
    titulo = serializers.CharField(max_length=200)
    organismo_id = serializers.IntegerField(required=False, allow_null=True)
    componente_id = serializers.IntegerField(required=False, allow_null=True)
    fecha_inicio = serializers.DateField(required=False, allow_null=True)
    fecha_fin = serializers.DateField(required=False, allow_null=True)

    def validate_tipo_reporte_id(self, value):
        try:
            tipo_reporte = TipoReporte.objects.get(pk=value)
        except TipoReporte.DoesNotExist:
            raise serializers.ValidationError("El tipo de reporte especificado no existe.")
        return value

    def validate_organismo_id(self, value):
        if value:
            try:
                Organismo.objects.get(pk=value)
            except Organismo.DoesNotExist:
                raise serializers.ValidationError("El organismo especificado no existe.")
        return value

    def validate_componente_id(self, value):
        if value:
            try:
                Componente.objects.get(pk=value)
            except Componente.DoesNotExist:
                raise serializers.ValidationError("El componente especificado no existe.")
        return value