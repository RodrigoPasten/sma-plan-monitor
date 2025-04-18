from django.shortcuts import render
from rest_framework import viewsets
from .models import Organismo
from .serializers import OrganismoSerializer
from django.views.generic import TemplateView

# Create your views here.
class OrganismoViewSet(viewsets.ModelViewSet):
    queryset = Organismo.objects.all()
    serializer_class = OrganismoSerializer




# apps/organismos/views.py

from django.views.generic import TemplateView
from .models import Organismo

class DashboardOrganismoView(TemplateView):
    template_name = 'organismos/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['organismos'] = Organismo.objects.all()
        return context

