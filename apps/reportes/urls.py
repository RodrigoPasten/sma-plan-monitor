# apps/reportes/urls.py
from django.urls import path
from . import views

app_name = 'reportes'

urlpatterns = [
    path('', views.ReporteListView.as_view(), name='lista_tipos'),
    path('mis-reportes/', views.MisReportesListView.as_view(), name='mis_reportes'),
    path('generar/<int:tipo_id>/', views.generar_reporte, name='generar_reporte'),
    path('<int:pk>/', views.ReporteDetailView.as_view(), name='detalle_reporte'),
    path('descargar/<int:pk>/', views.descargar_reporte, name='descargar_reporte'),
]