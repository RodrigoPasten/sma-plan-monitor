import unittest
import pytest
from django.urls import reverse
from django.test import Client
from django.contrib.auth import get_user_model

from apps.reportes.models import TipoReporte, ReporteGenerado
from apps.organismos.models import Organismo, TipoOrganismo
from apps.medidas.models import Componente

@pytest.mark.django_db
class ReporteDetailViewTest(unittest.TestCase):
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

        self.tipo_reporte = TipoReporte.objects.create(
            nombre="Reporte de Prueba",
            tipo="general",
            acceso_superadmin=True,
            acceso_admin_sma=False,
            acceso_organismos=False,
        )

        tipo_org = TipoOrganismo.objects.create(nombre="Tipo Prueba")
        self.organismo = Organismo.objects.create(
            nombre="Organismo de Prueba",
            tipo=tipo_org,
            rut="12345678-9",
            direccion="Calle Falsa 123",
            comuna="Comuna X",
            region="Región Y",
            telefono="987654321",
            email_contacto="contacto@org.test",
        )
        self.componente = Componente.objects.create(nombre="Componente de Prueba")

        self.reporte = ReporteGenerado.objects.create(
            tipo_reporte=self.tipo_reporte,
            usuario=self.user,
            titulo="Reporte de Prueba",
        )

        self.url = reverse(
            "reportes:detalle_reporte",
            kwargs={"pk": self.reporte.pk}
        )

    def test_reporte_detail_access(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)

    def test_reporte_detail_context(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.context["reporte"], self.reporte)
        self.assertTrue(hasattr(resp.context["reporte"], "parametros"))
        self.assertIsInstance(resp.context["reporte"].parametros, dict)
        self.assertEqual(resp.context["reporte"].parametros, {})
