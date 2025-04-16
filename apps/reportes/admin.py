# apps/reportes/admin.py
from django.contrib import admin
from .models import TipoReporte, ReporteGenerado

@admin.register(TipoReporte)
class TipoReporteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'acceso_superadmin', 'acceso_admin_sma', 'acceso_organismos')
    list_filter = ('tipo', 'acceso_superadmin', 'acceso_admin_sma', 'acceso_organismos')
    search_fields = ('nombre', 'descripcion')

@admin.register(ReporteGenerado)
class ReporteGeneradoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'tipo_reporte', 'usuario', 'fecha_generacion', 'organismo')
    list_filter = ('tipo_reporte', 'fecha_generacion', 'organismo')
    search_fields = ('titulo', 'usuario__username', 'organismo__nombre')
    date_hierarchy = 'fecha_generacion'
    readonly_fields = ('fecha_generacion', 'archivo', 'parametros')