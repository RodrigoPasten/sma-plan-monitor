from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from drf_yasg.views import get_schema_view
from drf_yasg.generators import OpenAPISchemaGenerator
from drf_yasg import openapi

from .views.organismos import OrganismoViewSet, TipoOrganismoViewSet
from .views.medidas import ComponenteViewSet, MedidaViewSet, RegistroAvanceViewSet
from .views.dashboard import DashboardView

from .views.auth import CustomAuthToken, LogoutView

from .views.reportes import TipoReporteViewSet, ReporteGeneradoViewSet

from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.permissions import AllowAny
from rest_framework.authentication import TokenAuthentication

class TaggedSchemaGenerator(OpenAPISchemaGenerator):
    def get_tags(self, endpoints):
        return [
            {'name': 'Autenticación', 'description': 'Endpoints de autenticación'},
            {'name': 'Organismos', 'description': 'Gestión de organismos'},
            {'name': 'Tipos de Organismo', 'description': 'Tipos de organismos'},
            {'name': 'Medidas', 'description': 'Gestión de medidas'},
            {'name': 'Componentes', 'description': 'Componentes del plan'},
            {'name': 'Avances', 'description': 'Registro de avances'},
            {'name': 'Reportes', 'description': 'Generación de reportes'},
            {'name': 'Dashboard', 'description': 'Paneles de control'},
            {'name': 'Notificaciones', 'description': 'Gestión de notificaciones'},
        ]


schema_view = get_schema_view(
    openapi.Info(
        title="API Plan de Descontaminación",
        default_version='v1',
        description="API para el sistema de monitoreo del Plan de Descontaminación",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="grupo5@talentofuturo.com"),
        license=openapi.License(name="License MIT"),
    ),
    public=True,
    permission_classes=(AllowAny,),
    generator_class=TaggedSchemaGenerator
)

app_name = 'api'
# Configuración del router para las vistas basadas en viewsets
router = DefaultRouter()
router.register(r'organismos', OrganismoViewSet)
router.register(r'tipos-organismo', TipoOrganismoViewSet)
router.register(r'componentes', ComponenteViewSet)
router.register(r'medidas', MedidaViewSet)
router.register(r'registros-avance', RegistroAvanceViewSet)
router.register(r'tipos-reporte', TipoReporteViewSet)
router.register(r'reportes', ReporteGeneradoViewSet, basename='reportes')

# URLs de la API
urlpatterns = [

    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # Endpoints drf-yasg (Swagger)
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # Endpoints de la API
    path('', include(router.urls)),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),

    # Autenticación
    path('auth/token/', CustomAuthToken.as_view(), name='api-token'),
    path('auth/logout/', LogoutView.as_view(), name='api-logout'),
    path('notificaciones/', include('apps.api.urls_notificaciones')),


]



