import unittest
import pytest
from django.urls import reverse
from django.test import Client
from django.utils import timezone
from django.contrib.auth import get_user_model

from apps.medidas.models import Componente, Medida, RegistroAvance
from apps.organismos.models import Organismo, TipoOrganismo

@pytest.mark.django_db
class DashboardSMAViewTest(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.client = Client()
        User = get_user_model()

        self.user_superadmin = User.objects.create_user(
            username="superadmin",
            password="testpassword",
            rol="superadmin"
        )
        assert self.client.login(username="superadmin", password="testpassword")

        self.url = reverse("medidas:dashboard_sma")

        self.componente = Componente.objects.create(nombre="Calidad del Aire")

        self.tipo_org = TipoOrganismo.objects.create(nombre="Tipo Prueba")
        self.organismo = Organismo.objects.create(
            nombre="Municipalidad",
            tipo=self.tipo_org,
            rut="11111111-1",
            direccion="Calle Falsa 123",
            comuna="Comuna X",
            region="Región Y",
            telefono="123456789",
            email_contacto="contacto@muni.cl",
        )

        today = timezone.now().date()

        self.medida1 = Medida.objects.create(
            nombre="Medida 1",
            codigo="M1",
            descripcion="Desc",
            componente=self.componente,
            fecha_inicio=today,
            fecha_termino=today + timezone.timedelta(days=10),
        )
        self.medida2 = Medida.objects.create(
            nombre="Medida 2",
            codigo="M2",
            descripcion="Desc",
            componente=self.componente,
            fecha_inicio=today,
            fecha_termino=today,  # obligatorio no nulo
            estado="completada",
        )
        self.medida3 = Medida.objects.create(
            nombre="Medida 3",
            codigo="M3",
            descripcion="Desc",
            componente=self.componente,
            fecha_inicio=today - timezone.timedelta(days=15),
            fecha_termino=today - timezone.timedelta(days=5),
        )

        self.registro1 = RegistroAvance.objects.create(
            medida=self.medida1,
            organismo=self.organismo,
            fecha_registro=today,
            porcentaje_avance=50,
            descripcion="Avance 1",
            created_by=self.user_superadmin,
        )
        self.registro2 = RegistroAvance.objects.create(
            medida=self.medida2,
            organismo=self.organismo,
            fecha_registro=today,
            porcentaje_avance=75,
            descripcion="Avance 2",
            created_by=self.user_superadmin,
        )

    def test_dashboard_sma_view_access(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)

    def test_dashboard_sma_view_context(self):
        resp = self.client.get(self.url)
        expected_keys = [
            "total_medidas",
            "medidas_completadas",
            "componentes",
            "medidas_proximas_vencer",
            "medidas_retrasadas_list",
            "mejores_organismos",
            "peores_organismos",
            "ultimos_avances",
        ]
        for key in expected_keys:
            with self.subTest(key=key):
                self.assertIn(key, resp.context)
