from django.urls import path
from apps.api.views.notificaciones import notificaciones_no_leidas_api

urlpatterns = [
    path('no-leidas/', notificaciones_no_leidas_api, name='notificaciones_no_leidas'),
]