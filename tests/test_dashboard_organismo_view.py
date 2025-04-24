import pytest
import unittest
from django.test import Client
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from apps.organismos.models import Organismo, TipoOrganismo
from apps.medidas.models import Componente, Medida, RegistroAvance
from django.contrib.auth import get_user_model

@pytest.mark.django_db
class DashboardOrganismoViewTest(unittest.TestCase):
    def setUp(self):
        self.client = Client()
        self.tipo = TipoOrganismo.objects.create(nombre="Municipalidad")
        self.user_organismo = get_user_model().objects.create_user(
            username="organismo",
            password="testpassword",
            rol="organismo"
        )
        self.organismo = Organismo.objects.create(
            nombre="Organismo de Prueba",
            tipo=self.tipo
        )
        self.user_organismo.organismo = self.organismo
        self.user_organismo.save()
        self.client.force_login(self.user_organismo)

        self.componente = Componente.objects.create(nombre="Calidad del Aire")
        today = timezone.now().date()

        # Tres medidas con distintos estados/fechas
        self.medida1 = Medida.objects.create(
            nombre="Medida 1", codigo="M1", descripcion="Desc",
            componente=self.componente,
            fecha_inicio=today,
            fecha_termino=today + timedelta(days=10)
        )
        self.medida1.responsables.add(self.organismo)
        
        self.medida2 = Medida.objects.create(
            nombre="Medida 2", codigo="M2", descripcion="Desc",
            componente=self.componente,
            estado="completada",
            fecha_inicio=today,
            fecha_termino=today + timedelta(days=5)
        )
        self.medida2.responsables.add(self.organismo)
        
        self.medida3 = Medida.objects.create(
            nombre="Medida 3", codigo="M3", descripcion="Desc",
            componente=self.componente,
            fecha_inicio=today,
            fecha_termino=today - timedelta(days=5)
        )
        self.medida3.responsables.add(self.organismo)

        # Dos registros de avance
        RegistroAvance.objects.create(
            medida=self.medida1,
            organismo=self.organismo,
            fecha_registro=today,
            porcentaje_avance=50,
            descripcion="Avance 1"
        )
        RegistroAvance.objects.create(
            medida=self.medida2,
            organismo=self.organismo,
            fecha_registro=today,
            porcentaje_avance=75,
            descripcion="Avance 2"
        )

        self.url = reverse("medidas:dashboard_organismo")

    def test_dashboard_organismo_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("total_medidas", response.context)
        self.assertEqual(response.context["total_medidas"], 3)

    def test_dashboard_organismo_acceso(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        
    def test_dashboard_organismo_context(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        expected_keys = [
            "organismo",
            "medidas_asignadas",
            "total_medidas",
            "medidas_completadas",
            "medidas_en_proceso",
            "medidas_retrasadas",
            "avance_promedio",
            "ultimos_avances",
        ]
        for key in expected_keys:
            self.assertIn(key, response.context)
