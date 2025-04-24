import pytest
import unittest

from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from apps.reportes.models import TipoReporte

@pytest.mark.django_db
class ReporteListViewTest(TestCase):
    def setUp(self):
        super().setUp()
        self.client = Client()

        User = get_user_model()
        self.user = User.objects.create_user(
            username="testuser",
            password="testpassword",
            rol="superadmin",
        )
        assert self.client.login(username="testuser", password="testpassword")

        self.tipo_super = TipoReporte.objects.create(
            nombre="Reporte Superadmin",
            tipo="general",
            acceso_superadmin=True,
            acceso_admin_sma=False,
            acceso_organismos=False,
        )
        self.tipo_admin_sma = TipoReporte.objects.create(
            nombre="Reporte Admin SMA",
            tipo="general",
            acceso_superadmin=False,
            acceso_admin_sma=True,
            acceso_organismos=False,
        )
        self.tipo_organismo = TipoReporte.objects.create(
            nombre="Reporte Organismo",
            tipo="general",
            acceso_superadmin=False,
            acceso_admin_sma=False,
            acceso_organismos=True,
        )

        self.url = reverse("reportes:lista_tipos")

    def test_reporte_list_view_filter_superadmin(self):
        self.user.rol = "superadmin"
        self.user.save()
        resp = self.client.get(self.url)
        tipos = resp.context["tipos_reporte"]

        self.assertIn(self.tipo_super, tipos)
        self.assertNotIn(self.tipo_admin_sma, tipos)
        self.assertNotIn(self.tipo_organismo, tipos)

    def test_reporte_list_view_filter_admin_sma(self):
        self.user.rol = "admin_sma"
        self.user.save()
        resp = self.client.get(self.url)
        tipos = resp.context["tipos_reporte"]

        self.assertNotIn(self.tipo_super, tipos)
        self.assertIn(self.tipo_admin_sma, tipos)
        self.assertNotIn(self.tipo_organismo, tipos)

    def test_reporte_list_view_filter_organismo(self):
        self.user.rol = "organismo"
        self.user.save()
        resp = self.client.get(self.url)
        tipos = resp.context["tipos_reporte"]

        self.assertNotIn(self.tipo_super, tipos)
        self.assertNotIn(self.tipo_admin_sma, tipos)
        self.assertIn(self.tipo_organismo, tipos)

    def test_reporte_list_view_filter_ciudadano(self):
        self.user.rol = "ciudadano"
        self.user.save()
        resp = self.client.get(self.url)
        tipos = resp.context["tipos_reporte"]

        self.assertEqual(len(tipos), 0)
