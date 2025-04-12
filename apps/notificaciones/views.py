from django.views.generic import ListView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.utils import timezone
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from .models import Notificacion
from .services import NotificacionService


class NotificacionListView(LoginRequiredMixin, ListView):
    """
    Vista para listar las notificaciones del usuario actual.
    """
    model = Notificacion
    template_name = 'notificaciones/lista_notificaciones.html'
    context_object_name = 'notificaciones'
    paginate_by = 10

    def get_queryset(self):
        """Filtrar notificaciones para el usuario actual."""
        return Notificacion.objects.filter(
            usuario=self.request.user
        ).select_related('tipo').order_by('-fecha_envio')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['notificaciones_no_leidas'] = NotificacionService.contar_notificaciones_no_leidas(self.request.user)
        return context


class NotificacionDetailView(LoginRequiredMixin, DetailView):
    """
    Vista para ver el detalle de una notificación y marcarla como leída.
    """
    model = Notificacion
    template_name = 'notificaciones/detalle_notificacion.html'
    context_object_name = 'notificacion'

    def get_queryset(self):
        """Asegurar que el usuario solo ve sus propias notificaciones."""
        return Notificacion.objects.filter(usuario=self.request.user)

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)

        # Marcar como leída si no lo está
        notificacion = self.object
        if not notificacion.leida:
            notificacion.marcar_como_leida()

        return response


class MarcarNotificacionLeidaView(LoginRequiredMixin, View):
    """
    Vista para marcar una notificación como leída vía AJAX.
    """

    def post(self, request, pk):
        notificacion = get_object_or_404(Notificacion, pk=pk, usuario=request.user)
        notificacion.marcar_como_leida()

        return JsonResponse({
            'success': True,
            'mensaje': _('Notificación marcada como leída'),
            'notificaciones_pendientes': NotificacionService.contar_notificaciones_no_leidas(request.user)
        })


class MarcarTodasLeidasView(LoginRequiredMixin, View):
    """
    Vista para marcar todas las notificaciones como leídas.
    """

    def post(self, request):
        notificaciones = Notificacion.objects.filter(usuario=request.user, leida=False)
        cantidad = notificaciones.count()

        if cantidad > 0:
            notificaciones.update(leida=True, fecha_lectura=timezone.now())
            messages.success(request, _(f'{cantidad} notificaciones marcadas como leídas.'))
        else:
            messages.info(request, _('No hay notificaciones pendientes por leer.'))

        return redirect('notificaciones:lista')