import unittest
import pytest
from datetime import date
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from apps.medidas.models import Componente, Medida

@pytest.mark.django_db
class MedidaViewSetTest(unittest.TestCase):
    def setUp(self):
        self.client = APIClient()
        User = get_user_model()
        self.user = User.objects.create_superuser(
            username="testuser",
            password="testpassword",
            rol="superadmin"
        )
        self.client.force_authenticate(self.user)

        self.componente = Componente.objects.create(nombre="Calidad del Aire")

        self.medida = Medida.objects.create(
            nombre="Reducción de emisiones",
            codigo="RED-001",
            descripcion="Implementar medidas para reducir las emisiones de gases",
            componente=self.componente,
            fecha_inicio=date(2024, 1, 1),
            fecha_termino=date(2024, 12, 31),
            porcentaje_avance=50.50,
        )

        self.list_url = "/api/v1/medidas/"
        self.detail_url = f"/api/v1/medidas/{self.medida.id}/"

        self.medida_data = {
            "nombre": "Reducción de emisiones",
            "codigo": "RED-001",
            "descripcion": "Implementar medidas para reducir las emisiones de gases",
            "componente": self.componente.id,
            "fecha_inicio": "2024-01-01",
            "fecha_termino": "2024-12-31",
            "porcentaje_avance": 50.50,
        }

    def test_medida_list_view_acceso(self):
        resp = self.client.get(self.list_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_medida_create(self):
        data = self.medida_data.copy()
        data["nombre"] = "Nueva Medida"
        data["codigo"] = "RED-002"
        resp = self.client.post(self.list_url, data, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Medida.objects.count(), 2)
        self.assertEqual(Medida.objects.last().nombre, "Nueva Medida")

    def test_medida_retrieve(self):
        resp = self.client.get(self.detail_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["nombre"], self.medida.nombre)

    def test_medida_update(self):
        upd = {"nombre": "Medida Actualizada"}
        resp = self.client.patch(self.detail_url, upd, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.medida.refresh_from_db()
        self.assertEqual(self.medida.nombre, "Medida Actualizada")

    def test_medida_delete(self):
        resp = self.client.delete(self.detail_url)
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Medida.objects.filter(pk=self.medida.id, activo=True).exists())
