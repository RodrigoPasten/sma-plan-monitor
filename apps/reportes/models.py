from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.usuarios.models import Usuario
from apps.organismos.models import Organismo
from apps.medidas.models import Componente, Medida


class TipoReporte(models.Model):
    """
    Define los tipos básicos de reportes disponibles en el sistema.
    """
    TIPO_CHOICES = [
        ('general', _('Reporte General')),
        ('organismo', _('Reporte por Organismo')),
        ('componente', _('Reporte por Componente')),
    ]

    nombre = models.CharField(_("Nombre"), max_length=100)
    descripcion = models.TextField(_("Descripción"))
    tipo = models.CharField(_("Tipo"), max_length=20, choices=TIPO_CHOICES)

    # Controla qué perfiles pueden acceder a este tipo de reporte
    acceso_superadmin = models.BooleanField(_("Acceso Superadmin"), default=True)
    acceso_admin_sma = models.BooleanField(_("Acceso Admin SMA"), default=True)
    acceso_organismos = models.BooleanField(_("Acceso Organismos"), default=False)

    created_at = models.DateTimeField(_("Fecha de creación"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Fecha de actualización"), auto_now=True)

    class Meta:
        verbose_name = _("Tipo de Reporte")
        verbose_name_plural = _("Tipos de Reportes")

    def __str__(self):
        return self.nombre


class ReporteGenerado(models.Model):
    """
    Almacena los reportes generados por los usuarios.
    """
    tipo_reporte = models.ForeignKey(
        TipoReporte,
        on_delete=models.PROTECT,
        verbose_name=_("Tipo de reporte"),
        related_name="reportes_generados"
    )

    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        verbose_name=_("Usuario"),
        related_name="reportes_generados"
    )

    titulo = models.CharField(_("Título"), max_length=200)
    fecha_generacion = models.DateTimeField(_("Fecha de generación"), auto_now_add=True)

    # Parámetros usados para generar el reporte
    parametros = models.JSONField(_("Parámetros"), default=dict, blank=True)

    # El archivo PDF generado
    archivo = models.FileField(_("Archivo"), upload_to='reportes/%Y/%m/')

    # Referencias opcionales a entidades relacionadas
    organismo = models.ForeignKey(
        Organismo,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Organismo"),
        related_name="reportes"
    )

    componente = models.ForeignKey(
        Componente,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Componente"),
        related_name="reportes"
    )

    class Meta:
        verbose_name = _("Reporte Generado")
        verbose_name_plural = _("Reportes Generados")
        ordering = ['-fecha_generacion']

    def __str__(self):
        return f"{self.titulo} - {self.fecha_generacion.strftime('%d/%m/%Y')}"