from django.utils import timezone
from django.db.models import Q
from django.conf import settings

from .models import Notificacion, TipoNotificacion


class NotificacionService:
    @staticmethod
    def enviar_notificacion(
            usuario,
            titulo,
            mensaje,
            tipo_nombre=None,
            prioridad='media',
            enlace='',
            enviar_email=False  # Cambiado a False por defecto para pruebas
    ):
        """
        Crea y envía una notificación a un usuario específico.
        """
        # Obtener usuario si se pasó un ID
        if isinstance(usuario, int):
            from apps.usuarios.models import Usuario
            try:
                usuario = Usuario.objects.get(pk=usuario)
            except Usuario.DoesNotExist:
                return None

        # Obtener tipo de notificación
        try:
            if tipo_nombre:
                tipo = TipoNotificacion.objects.get(nombre=tipo_nombre)
            else:
                tipo = TipoNotificacion.objects.get(nombre='General')
        except TipoNotificacion.DoesNotExist:
            # Crear tipo por defecto si no existe
            tipo = TipoNotificacion.objects.create(
                nombre='General',
                descripcion='Notificaciones generales del sistema',
                icono='info-circle',
                color='primary'
            )

        # Crear la notificación
        notificacion = Notificacion.objects.create(
            tipo=tipo,
            usuario=usuario,
            titulo=titulo,
            mensaje=mensaje,
            enlace=enlace,
            prioridad=prioridad
        )

        # Aquí iría el código para enviar email si está habilitado
        # Por ahora lo dejamos comentado
        # if enviar_email and usuario.email:
        #     NotificacionService._enviar_email_notificacion(notificacion)

        return notificacion

    @staticmethod
    def obtener_notificaciones_no_leidas(usuario):
        """
        Obtiene todas las notificaciones no leídas para un usuario.
        """
        if isinstance(usuario, int):
            usuario_id = usuario
        else:
            usuario_id = usuario.id

        return Notificacion.objects.filter(
            usuario_id=usuario_id,
            leida=False
        ).order_by('-prioridad', '-fecha_envio')

    @staticmethod
    def contar_notificaciones_no_leidas(usuario):
        """
        Cuenta las notificaciones no leídas de un usuario.
        """
        if isinstance(usuario, int):
            usuario_id = usuario
        else:
            usuario_id = usuario.id

        return Notificacion.objects.filter(
            usuario_id=usuario_id,
            leida=False
        ).count()