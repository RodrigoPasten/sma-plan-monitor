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
class NotificacionDetailViewTest(unittest.TestCase):
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

        self.url = reverse("notificaciones:detalle", kwargs={"pk": self.notificacion.pk})

    def test_notificacion_detail_view_access(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)

    def test_notificacion_detail_context(self):
        resp = self.client.get(self.url)
        self.assertIn("notificacion", resp.context)
        self.assertEqual(resp.context["notificacion"], self.notificacion)
