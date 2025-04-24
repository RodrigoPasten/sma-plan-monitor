from django.conf import settings
from django.urls import path, include
from django.contrib import admin
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('admin/', admin.site.urls),

    # API Endpoint
    path('api/v1/', include('apps.api.urls')),

    # Esquemas OpenAPI y documentación
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/docs/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('api/docs/rapidoc/', TemplateView.as_view(
        template_name='rapidoc.html',
        extra_context={'schema_url': '/api/schema/'}  # Nota: se quitó format=openapi
    ), name='rapidoc'),

    # Tus otras URLs...
    path('medidas/', include('apps.medidas.urls')),
    path('organismos/', include('apps.organismos.urls')),
    path('reportes/', include('apps.reportes.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    # URLs de autenticación explícitas
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='registration/logged_out.html'), name='logout'),
    # Recuperar contraseña
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('notificaciones/', include('apps.notificaciones.urls')),

    # El portal público se mapea a la raíz del sitio
    path('', include('apps.publico.urls')),
]

# Agregar URLs para archivos estáticos y media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)