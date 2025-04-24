import os
import django
import pytest
import unittest

def setUpModule():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ppda_core.settings')
    django.setup()

from apps.notificaciones.models import TipoNotificacion

@pytest.mark.django_db
class TipoNotificacionModelTest(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.tipo_notificacion_data = {
            "nombre": "Alerta General",
            "descripcion": "Notificación de alerta general",
            "icono": "warning",
            "color": "#ff0000",
            "codigo": "ALERTA",
        }
        self.tipo_notificacion = TipoNotificacion.objects.create(
            **self.tipo_notificacion_data
        )

    def test_tipo_notificacion_creacion(self):
        self.assertIsInstance(self.tipo_notificacion, TipoNotificacion)
        for field, value in self.tipo_notificacion_data.items():
            self.assertEqual(getattr(self.tipo_notificacion, field), value)