
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from apps.notificaciones.services import NotificacionService

@login_required
def notificaciones_no_leidas_api(request):
    """
    Retorna el número de notificaciones no leídas para el usuario actual.
    """
    try:
        cantidad = NotificacionService.contar_notificaciones_no_leidas(request.user)
        return JsonResponse({'cantidad': cantidad})
    except Exception as e:
        # Log the error for debugging
        print(f"Error al contar notificaciones: {str(e)}")
        return JsonResponse({'cantidad': 0, 'error': str(e)}, status=500)