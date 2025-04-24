import os
import django
import pytest
import unittest

def setUpModule():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ppda_core.settings')
    django.setup()

from django.contrib.auth import get_user_model
from apps.notificaciones.models import TipoNotificacion, Notificacion

@pytest.mark.django_db
class NotificacionModelTest(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.tipo_notificacion = TipoNotificacion.objects.create(
            nombre="Alerta General",
            descripcion="Notificación de alerta general",
            icono="warning",
            color="#ff0000",
            codigo="ALERTA",
        )
        self.usuario = get_user_model().objects.create_user(
            username="testuser",
            password="testpassword"
        )
        self.notificacion_data = {
            "tipo": self.tipo_notificacion,
            "usuario": self.usuario,
            "titulo": "Prueba de Alerta",
            "mensaje": "Este es un mensaje de prueba",
            "prioridad": "alta",
        }
        self.notificacion = Notificacion.objects.create(**self.notificacion_data)

    def test_notificacion_creacion(self):
        self.assertIsInstance(self.notificacion, Notificacion)
        for field, value in self.notificacion_data.items():
            self.assertEqual(getattr(self.notificacion, field), value)
        self.assertFalse(self.notificacion.leida)
        self.assertIsNotNone(self.notificacion.fecha_envio)
