import unittest
import pytest
from django.urls import reverse
from django.test import Client
from django.utils import timezone
from django.contrib.auth import get_user_model

from apps.medidas.models import Componente, Medida
from apps.organismos.models import Organismo, TipoOrganismo

@pytest.mark.django_db
class RegistrarAvanceViewTest(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.client = Client()
        User = get_user_model()

        self.user_organismo = User.objects.create_user(
            username="organismo",
            password="testpassword",
            rol="organismo",
        )

        tipo = TipoOrganismo.objects.create(nombre="Tipo Prueba")

        self.organismo = Organismo.objects.create(
            nombre="Organismo de Prueba",
            tipo=tipo,
            rut="12345678-9",
            direccion="Calle Falsa 123",
            comuna="Comuna X",
            region="Región Y",
            telefono="987654321",
            email_contacto="contacto@org.test",
        )
        self.user_organismo.organismo = self.organismo
        self.user_organismo.save()

        assert self.client.login(username="organismo", password="testpassword")

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

        self.url = reverse("medidas:registrar_avance")

    def test_registrar_avance_access(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
