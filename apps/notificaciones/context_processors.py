from .models import Notificacion
from .services import NotificacionService


def notificaciones_context(request):
    """
    Añade información de notificaciones al contexto global.
    """
    context = {
        'notificaciones_no_leidas_count': 0,
        'ultimas_notificaciones': []
    }

    if request.user.is_authenticated:
        try:
            # Obtener todas las notificaciones no leídas en una sola consulta
            no_leidas = list(Notificacion.objects.filter(
                usuario=request.user,
                leida=False
            ).order_by('-fecha_envio'))

            # Asegurarse de que ambas variables usan la misma fuente de datos
            context['notificaciones_no_leidas_count'] = len(no_leidas)
            context['ultimas_notificaciones'] = no_leidas[:5]

            # Log para depuración
            print(f"Usuario: {request.user.username}")
            print(f"Notificaciones no leídas: {context['notificaciones_no_leidas_count']}")
            print(f"Últimas notificaciones: {[n.id for n in context['ultimas_notificaciones']]}")
        except Exception as e:
            print(f"Error en context processor: {str(e)}")

    return context