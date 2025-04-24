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
class NotificacionListViewTest(unittest.TestCase):
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

        self.notificacion1 = Notificacion.objects.create(
            tipo=self.tipo_notificacion,
            usuario=self.user,
            titulo="Alerta 1",
            mensaje="Mensaje de alerta 1",
        )
        self.notificacion2 = Notificacion.objects.create(
            tipo=self.tipo_notificacion,
            usuario=self.user,
            titulo="Alerta 2",
            mensaje="Mensaje de alerta 2",
        )

        self.url = reverse("notificaciones:lista")

    def test_notificacion_list_view_access(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)

    def test_notificacion_list_view_context(self):
        resp = self.client.get(self.url)
        self.assertIn("notificaciones", resp.context)
        qs = list(resp.context["notificaciones"])
        expected = [self.notificacion1, self.notificacion2]
        self.assertCountEqual(qs, expected)
