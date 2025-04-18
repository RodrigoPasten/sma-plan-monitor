from django.urls import path
from . import views

app_name = 'medidas'
urlpatterns = [
    path('dashboard/sma/', views.DashboardSMAView.as_view(), name='dashboard_sma'),
    path('avance/registrar/', views.registrar_avance, name='registrar_avance'),
    path('avance/registrar/<int:medida_id>/', views.registrar_avance, name='registrar_avance_medida'),
    path('<int:pk>/', views.MedidaDetailView.as_view(), name='detalle'),
    path('dashboard/organismo/', views.DashboardOrganismoView.as_view(), name='dashboard_organismo'),

]
