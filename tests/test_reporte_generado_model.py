import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.reportes.models import TipoReporte, ReporteGenerado

@pytest.mark.django_db
class ReporteGeneradoModelTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username="testuser",
            password="testpassword",
            rol="superadmin",
        )
        self.tipo_reporte = TipoReporte.objects.create(
            nombre="Reporte General",
            tipo="general"
        )
        self.reporte_data = {
            "tipo_reporte": self.tipo_reporte,
            "usuario": self.user,
            "titulo": "Reporte de prueba",
        }
        self.reporte_generado = ReporteGenerado.objects.create(**self.reporte_data)

    def test_reporte_generado_creacion(self):
        self.assertIsInstance(self.reporte_generado, ReporteGenerado)

        for campo, valor_esperado in self.reporte_data.items():
            valor_real = getattr(self.reporte_generado, campo)
            self.assertEqual(
                valor_real, valor_esperado,
                f"Campo {campo!r}: esperado {valor_esperado!r} pero fue {valor_real!r}"
            )

        self.assertIsNotNone(
            self.reporte_generado.fecha_generacion,
            "fecha_generacion no debe ser None"
        )

        self.assertEqual(
            self.reporte_generado.parametros,
            {},
            f"parametros por defecto debe ser {{}} pero fue {self.reporte_generado.parametros!r}"
        )
