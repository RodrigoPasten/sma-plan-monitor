import os
import django

def setUpModule():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ppda_core.settings')
    django.setup()

import unittest
import pytest
from django.urls import reverse
from django.test import Client
from django.contrib.auth import get_user_model

from apps.notificaciones.models import TipoNotificacion, Notificacion

@pytest.mark.django_db
class MarcarNotificacionLeidaViewTest(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            username="testuser",
            password="testpassword"
        )
        assert self.client.login(username="testuser", password="testpassword")

        self.tipo_notificacion = TipoNotificacion.objects.create(
            nombre="Alerta General",
            descripcion="Notificación de alerta general",
            icono="warning",
            color="#ff0000",
            codigo="ALERTA",
        )
        self.notificacion = Notificacion.objects.create(
            tipo=self.tipo_notificacion,
            usuario=self.user,
            titulo="Alerta de Prueba",
            mensaje="Este es un mensaje de prueba",
        )

        self.url = reverse(
            "notificaciones:marcar_leida",
            kwargs={"pk": self.notificacion.pk}
        )

    def test_marcar_notificacion_leida_post(self):
        """Al enviar POST, la notificación debe marcarse como leída."""
        self.assertFalse(self.notificacion.leida)

        response = self.client.post(self.url, {}, content_type="application/json")
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn("success", data)
        self.assertTrue(data["success"])

        self.notificacion.refresh_from_db()
        self.assertTrue(self.notificacion.leida)
