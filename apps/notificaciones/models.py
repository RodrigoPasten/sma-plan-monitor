from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.usuarios.models import Usuario
from apps.organismos.models import Organismo


class TipoNotificacion(models.Model):
    """
    Define los diferentes tipos de notificaciones que puede generar el sistema.
    """
    nombre = models.CharField(_("Nombre"), max_length=100)
    descripcion = models.TextField(_("Descripción"), blank=True)
    icono = models.CharField(_("Icono"), max_length=50, blank=True)
    color = models.CharField(_("Color"), max_length=20, blank=True)
    codigo = models.CharField(_("Código"), max_length=50, unique=True, blank=True, null=True)
    created_at = models.DateTimeField(_("Fecha de creación"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Fecha de actualización"), auto_now=True)

    para_superadmin = models.BooleanField(_("Para Superadmin"), default=False)
    para_admin_sma = models.BooleanField(_("Para Admin SMA"), default=False)
    para_organismos = models.BooleanField(_("Para Organismos"), default=False)
    para_ciudadanos = models.BooleanField(_("Para Ciudadanos"), default=False)

    created_at = models.DateTimeField(_("Fecha de creación"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Fecha de actualización"), auto_now=True)

    class Meta:
        verbose_name = _("Tipo de Notificación")
        verbose_name_plural = _("Tipos de Notificaciones")

    def __str__(self):
        return self.nombre



class Notificacion(models.Model):
    """
    Representa una notificación específica enviada a un usuario.
    """
    PRIORIDAD_CHOICES = [
        ('alta', _('Alta')),
        ('media', _('Media')),
        ('baja', _('Baja')),
    ]

    tipo = models.ForeignKey(
        TipoNotificacion,
        on_delete=models.CASCADE,
        verbose_name=_("Tipo"),
        related_name="notificaciones"
    )

    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        verbose_name=_("Usuario"),
        related_name="notificaciones"
    )

    titulo = models.CharField(_("Título"), max_length=200)
    mensaje = models.TextField(_("Mensaje"))
    enlace = models.CharField(_("Enlace"), max_length=255, blank=True)
    # Agregar estos campos
    medida = models.ForeignKey(
        'medidas.Medida',
        on_delete=models.SET_NULL,
        verbose_name=_("Medida"),
        related_name="notificaciones",
        blank=True,
        null=True
    )

    organismo = models.ForeignKey(
        'organismos.Organismo',
        on_delete=models.SET_NULL,
        verbose_name=_("Organismo"),
        related_name="notificaciones",
        blank=True,
        null=True
    )
    fecha_envio = models.DateTimeField(_("Fecha de envío"), auto_now_add=True)
    fecha_lectura = models.DateTimeField(_("Fecha de lectura"), null=True, blank=True)

    leida = models.BooleanField(_("Leída"), default=False)
    prioridad = models.CharField(_("Prioridad"), max_length=10, choices=PRIORIDAD_CHOICES, default='media')

    class Meta:
        verbose_name = _("Notificación")
        verbose_name_plural = _("Notificaciones")
        ordering = ['-fecha_envio']

    def __str__(self):
        return f"{self.titulo} - {self.usuario.username}"

    def marcar_como_leida(self):
        """
        Marca la notificación como leída y registra la fecha.
        """
        from django.utils import timezone

        self.leida = True
        self.fecha_lectura = timezone.now()
        self.save()