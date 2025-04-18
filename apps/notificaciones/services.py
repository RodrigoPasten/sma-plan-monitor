from django.utils import timezone
from django.db.models import Q
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

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
            enviar_email=True
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

        # Enviar correo electrónico si está habilitado
        if enviar_email and usuario.email and getattr(usuario, 'recibir_notificaciones_email', True):
            NotificacionService._enviar_email_notificacion(notificacion)

        return notificacion

    @staticmethod
    def _enviar_email_notificacion(notificacion):
        """
        Envía un correo electrónico para una notificación.
        """
        context = {
            'notificacion': notificacion,
            'site_url': getattr(settings, 'SITE_URL', 'http://localhost:8000'),
        }

        subject = f"[Plan de Descontaminación] {notificacion.titulo}"
        html_message = render_to_string('notificaciones/emails/notificacion.html', context)
        plain_message = render_to_string('notificaciones/emails/notificacion.txt', context)

        try:
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[notificacion.usuario.email],
                html_message=html_message,
                fail_silently=False
            )
            print(f"Correo enviado correctamente a {notificacion.usuario.email}")
            return True
        except Exception as e:
            print(f"Error al enviar email: {str(e)}")
            return False

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
            leida=False  # Asegurarse de que este filtro esté presente
        ).order_by('-prioridad', '-fecha_envio')

    @staticmethod
    def contar_notificaciones_no_leidas(usuario):
        """
        Cuenta las notificaciones no leídas de un usuario.

        Args:
            usuario: Usuario o ID de usuario

        Returns:
            int: Número de notificaciones no leídas
        """
        if isinstance(usuario, int):
            usuario_id = usuario
        else:
            usuario_id = usuario.id

        return Notificacion.objects.filter(
            usuario_id=usuario_id,
            leida=False
        ).count()