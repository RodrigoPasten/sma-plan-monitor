
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, View
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from .models import TipoReporte, ReporteGenerado
from .services import ReporteService
from apps.organismos.models import Organismo
from apps.medidas.models import Componente


class ReporteListView(LoginRequiredMixin, ListView):
    """Vista para listar los tipos de reportes disponibles"""
    model = TipoReporte
    template_name = 'reportes/lista_tipos.html'
    context_object_name = 'tipos_reporte'

    def get_queryset(self):
        # Filtrar tipos de reporte según el rol del usuario
        queryset = TipoReporte.objects.all()

        if self.request.user.rol == 'superadmin':
            queryset = queryset.filter(acceso_superadmin=True)
        elif self.request.user.rol == 'admin_sma':
            queryset = queryset.filter(acceso_admin_sma=True)
        elif self.request.user.rol == 'organismo':
            queryset = queryset.filter(acceso_organismos=True)
        else:
            queryset = queryset.none()

        return queryset


class MisReportesListView(LoginRequiredMixin, ListView):
    """Vista para listar los reportes generados por el usuario"""
    model = ReporteGenerado
    template_name = 'reportes/mis_reportes.html'
    context_object_name = 'reportes'
    paginate_by = 10

    def get_queryset(self):
        # Mostrar solo los reportes del usuario actual
        return ReporteGenerado.objects.filter(
            usuario=self.request.user
        ).order_by('-fecha_generacion')


@login_required
def generar_reporte(request, tipo_id):
    """Vista para generar un nuevo reporte"""
    tipo_reporte = get_object_or_404(TipoReporte, pk=tipo_id)

    # Verificar permisos
    if request.user.rol == 'organismo' and not tipo_reporte.acceso_organismos:
        messages.error(request, _("No tienes permiso para generar este tipo de reporte."))
        return redirect('reportes:lista_tipos')
    elif request.user.rol == 'admin_sma' and not tipo_reporte.acceso_admin_sma:
        messages.error(request, _("No tienes permiso para generar este tipo de reporte."))
        return redirect('reportes:lista_tipos')

    if request.method == 'POST':
        # Procesar formulario
        titulo = request.POST.get('titulo')
        organismo_id = request.POST.get('organismo')
        componente_id = request.POST.get('componente')

        # Si es usuario de organismo, forzar su propio organismo
        if request.user.rol == 'organismo':
            organismo_id = request.user.organismo.id

        # Generar el reporte
        reporte = ReporteService.generar_reporte(
            usuario=request.user,
            tipo_reporte_id=tipo_id,
            titulo=titulo,
            organismo_id=organismo_id if organismo_id else None,
            componente_id=componente_id if componente_id else None
        )

        if reporte:
            messages.success(request, _("Reporte generado exitosamente."))
            return redirect('reportes:detalle_reporte', pk=reporte.id)
        else:
            messages.error(request, _("Error al generar el reporte. Intente nuevamente."))

    # Preparar datos para el formulario
    context = {
        'tipo_reporte': tipo_reporte,
        'organismos': Organismo.objects.all() if request.user.rol != 'organismo' else None,
        'componentes': Componente.objects.all(),
    }

    return render(request, 'reportes/generar_reporte.html', context)


class ReporteDetailView(LoginRequiredMixin, DetailView):
    """Vista para ver detalles de un reporte generado"""
    model = ReporteGenerado
    template_name = 'reportes/detalle_reporte.html'
    context_object_name = 'reporte'

    def get_queryset(self):
        # Un usuario solo puede ver sus propios reportes (excepto superadmin y admin_sma)
        if self.request.user.rol in ['superadmin', 'admin_sma']:
            return ReporteGenerado.objects.all()
        return ReporteGenerado.objects.filter(usuario=self.request.user)


@login_required
def descargar_reporte(request, pk):
    """Vista para descargar un reporte PDF"""
    reporte = get_object_or_404(ReporteGenerado, pk=pk)

    # Verificar permisos
    if reporte.usuario != request.user and request.user.rol not in ['superadmin', 'admin_sma']:
        messages.error(request, _("No tienes permiso para descargar este reporte."))
        return redirect('reportes:mis_reportes')

    # Verificar que el archivo exista
    if not reporte.archivo:
        messages.error(request, _("El archivo no está disponible."))
        return redirect('reportes:detalle_reporte', pk=pk)

    # Establecer el nombre del archivo para la descarga
    filename = f"reporte_{reporte.tipo_reporte.tipo}_{reporte.id}.pdf"

    response = HttpResponse(reporte.archivo.read(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    return response