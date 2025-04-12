from django.urls import path
from . import views

app_name = 'notificaciones'

urlpatterns = [
    path('', views.NotificacionListView.as_view(), name='lista'),
    path('<int:pk>/', views.NotificacionDetailView.as_view(), name='detalle'),
    path('<int:pk>/marcar-leida/', views.MarcarNotificacionLeidaView.as_view(), name='marcar_leida'),
    path('marcar-todas-leidas/', views.MarcarTodasLeidasView.as_view(), name='marcar_todas_leidas'),
]