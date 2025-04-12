from .services import NotificacionService


def notificaciones_context(request):
    """
    Añade el contador de notificaciones no leídas al contexto global.
    """
    context = {
        'notificaciones_no_leidas_count': 0,
        'ultimas_notificaciones': []
    }

    if request.user.is_authenticated:
        context['notificaciones_no_leidas_count'] = NotificacionService.contar_notificaciones_no_leidas(request.user)
        # Obtener las 5 últimas notificaciones no leídas
        context['ultimas_notificaciones'] = NotificacionService.obtener_notificaciones_no_leidas(request.user)[:5]

    return context