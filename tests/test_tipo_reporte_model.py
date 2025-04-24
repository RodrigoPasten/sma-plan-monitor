import pytest
from django.test import TestCase
from apps.reportes.models import TipoReporte

@pytest.mark.django_db
class TipoReporteModelTest(TestCase):

    def setUp(self):
        self.tipo_reporte_data = {
            "nombre": "Reporte General",
            "descripcion": "Descripción del reporte general",
            "tipo": "general",
            "acceso_superadmin": True,
            "acceso_admin_sma": True,
            "acceso_organismos": False,
        }
        self.tipo_reporte = TipoReporte.objects.create(**self.tipo_reporte_data)

    def test_tipo_reporte_creacion(self):
        self.assertIsInstance(self.tipo_reporte, TipoReporte)

        for campo, valor_esperado in self.tipo_reporte_data.items():
            valor_real = getattr(self.tipo_reporte, campo)
            self.assertEqual(valor_real, valor_esperado,
                             f"El campo {campo} debería ser {valor_esperado!r} pero era {valor_real!r}")
