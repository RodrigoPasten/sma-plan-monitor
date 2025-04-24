import unittest

import pytest
from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from apps.reportes.models import TipoReporte, ReporteGenerado

@pytest.mark.django_db
class MisReportesListViewTest(TestCase):
    def setUp(self):
        super().setUp()
        self.client = Client()
        User = get_user_model()

        self.user = User.objects.create_user(
            username="testuser", password="testpassword", rol="superadmin"
        )
        logged = self.client.login(username="testuser", password="testpassword")
        assert logged, "No se pudo loguear al testuser"

        self.tipo_reporte = TipoReporte.objects.create(
            nombre="Reporte de Prueba",
            tipo="general"
        )

        self.reporte1 = ReporteGenerado.objects.create(
            tipo_reporte=self.tipo_reporte,
            usuario=self.user,
            titulo="Reporte 1",
        )
        self.reporte2 = ReporteGenerado.objects.create(
            tipo_reporte=self.tipo_reporte,
            usuario=self.user,
            titulo="Reporte 2",
        )

        self.url = reverse("reportes:mis_reportes")

    def test_mis_reportes_list_view_queryset_order(self):
        response = self.client.get(self.url)
        reportes = list(response.context["reportes"])
        self.assertEqual(reportes, [self.reporte2, self.reporte1])
