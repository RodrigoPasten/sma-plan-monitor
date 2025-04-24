import unittest
import pytest
from django.urls import reverse
from django.test import Client
from django.utils import timezone
from django.contrib.auth import get_user_model

from apps.medidas.models import Componente, Medida, RegistroAvance
from apps.organismos.models import Organismo, TipoOrganismo

@pytest.mark.django_db
class MedidaDetailViewTest(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.client = Client()

        User = get_user_model()
        self.user = User.objects.create_user(
            username="testuser",
            password="testpassword",
            rol="admin",
        )
        assert self.client.login(username="testuser", password="testpassword")

        self.componente = Componente.objects.create(nombre="Calidad del Aire")

        today = timezone.now().date()
        self.medida = Medida.objects.create(
            nombre="Medida de Prueba",
            codigo="MP001",
            descripcion="Descripción de la medida",
            componente=self.componente,
            fecha_inicio=today,
            fecha_termino=today + timezone.timedelta(days=30),
            porcentaje_avance=0,
        )

        tipo = TipoOrganismo.objects.create(nombre="Tipo Prueba")
        self.organismo = Organismo.objects.create(
            nombre="Organismo de Prueba",
            tipo=tipo,
            rut="11111111-1",
            direccion="Calle Falsa 123",
            comuna="Comuna X",
            region="Región Y",
            telefono="123456789",
            email_contacto="contacto@org.test",
        )

        self.registro = RegistroAvance.objects.create(
            medida=self.medida,
            organismo=self.organismo,
            fecha_registro=today,
            porcentaje_avance=50,
            descripcion="Avance inicial",
        )

        self.url = reverse("medidas:detalle", kwargs={"pk": self.medida.id})

    def test_medida_detail_access(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)

    def test_medida_detail_context(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.context["medida"], self.medida)
        self.assertIn("registros_avance", resp.context)
        self.assertIn("asignaciones", resp.context)
