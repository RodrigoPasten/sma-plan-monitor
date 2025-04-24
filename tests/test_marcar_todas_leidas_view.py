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
from django.contrib.messages import get_messages

from apps.notificaciones.models import TipoNotificacion, Notificacion

@pytest.mark.django_db
class MarcarTodasLeidasViewTest(unittest.TestCase):
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
            leida=False,
        )
        self.notificacion2 = Notificacion.objects.create(
            tipo=self.tipo_notificacion,
            usuario=self.user,
            titulo="Alerta 2",
            mensaje="Mensaje de alerta 2",
            leida=False,
        )

        self.url = reverse("notificaciones:marcar_todas_leidas")

    def test_marcar_todas_leidas_post(self):
        pendiente = Notificacion.objects.filter(usuario=self.user, leida=False).count()
        self.assertEqual(pendiente, 2)

        response = self.client.post(self.url, {}, content_type="application/json")

        pendiente = Notificacion.objects.filter(usuario=self.user, leida=False).count()
        self.assertEqual(pendiente, 0)

        self.assertEqual(response.status_code, 302)

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            "2 notificaciones marcadas como leídas."
        )

    def test_marcar_todas_leidas_post_no_notificaciones(self):
        Notificacion.objects.all().delete()

        response = self.client.post(self.url, {}, content_type="application/json")

        self.assertEqual(response.status_code, 302)

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            "No hay notificaciones pendientes por leer."
        )
