from django.urls import path
from .views import DashboardOrganismoView

app_name = 'organismos'

urlpatterns = [
    path('dashboard/', DashboardOrganismoView.as_view(), name='dashboard_organismo'),
]

