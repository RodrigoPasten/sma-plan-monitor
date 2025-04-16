from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect
from django.contrib import messages


class ReporteRolMixin(UserPassesTestMixin):
    """
    Mixin para verificar permisos de reportes según rol.
    """

    def test_func(self):
        # Verificar si el usuario está autenticado
        if not self.request.user.is_authenticated:
            return False

        # En esta versión simplificada, permitimos superadmin, admin_sma y organismos
        if (hasattr(self.request.user, 'rol') and
                self.request.user.rol in ['superadmin', 'admin_sma', 'organismo']):
            return True

        # Verificación alternativa usando properties si existen
        if (hasattr(self.request.user, 'is_superadmin') and self.request.user.is_superadmin) or \
                (hasattr(self.request.user, 'is_admin_sma') and self.request.user.is_admin_sma) or \
                (hasattr(self.request.user, 'is_organismo') and self.request.user.is_organismo):
            return True

        # Los ciudadanos no tienen acceso
        return False

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()

        messages.error(self.request, "No tiene permisos para acceder a los reportes.")
        return redirect('/')  # Redirigir a la página de inicio