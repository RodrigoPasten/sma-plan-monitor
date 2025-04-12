from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import TipoNotificacion, Notificacion


@admin.register(TipoNotificacion)
class TipoNotificacionAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion', 'icono', 'color')
    search_fields = ('nombre', 'descripcion')
    list_filter = ('created_at',)


@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'tipo', 'usuario', 'fecha_envio', 'leida', 'prioridad')
    list_filter = ('tipo', 'leida', 'prioridad', 'fecha_envio')
    search_fields = ('titulo', 'mensaje', 'usuario__username', 'usuario__email')
    date_hierarchy = 'fecha_envio'
    readonly_fields = ('fecha_envio', 'fecha_lectura')

    actions = ['marcar_como_leidas', 'marcar_como_no_leidas']

    def marcar_como_leidas(self, request, queryset):
        from django.utils import timezone

        updated = queryset.update(leida=True, fecha_lectura=timezone.now())
        self.message_user(
            request,
            _(f"{updated} notificación(es) marcada(s) como leída(s)."),
        )

    marcar_como_leidas.short_description = _("Marcar notificaciones seleccionadas como leídas")

    def marcar_como_no_leidas(self, request, queryset):
        updated = queryset.update(leida=False, fecha_lectura=None)
        self.message_user(
            request,
            _(f"{updated} notificación(es) marcada(s) como no leída(s)."),
        )

    marcar_como_no_leidas.short_description = _("Marcar notificaciones seleccionadas como no leídas")