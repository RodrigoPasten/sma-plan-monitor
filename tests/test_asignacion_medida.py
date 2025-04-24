import pytest
import unittest
from datetime import date
from apps.organismos.models import Organismo, TipoOrganismo
from apps.medidas.models import Componente, Medida, AsignacionMedida

@pytest.mark.django_db
class AsignacionMedidaModelTest(unittest.TestCase):
    def setUp(self):
        self.tipo = TipoOrganismo.objects.create(nombre="Municipalidad")
        self.componente = Componente.objects.create(nombre="Calidad del Aire")
        self.organismo = Organismo.objects.create(
            nombre="Municipalidad",
            tipo=self.tipo,
            direccion="",
            comuna="",
            region="",
            telefono="",
            email_contacto=""
        )
        self.medida = Medida.objects.create(
            nombre="Reducción de emisiones",
            codigo="RED-001",
            descripcion="Implementar medidas para reducir las emisiones de gases",
            componente=self.componente,
            fecha_inicio=date(2024, 1, 1),
            fecha_termino=date(2024, 12, 31),
        )
        self.asignacion_data = {
            "medida": self.medida,
            "organismo": self.organismo,
            "es_coordinador": True,
            "descripcion_responsabilidad": "Responsable de la implementación",
        }
        self.asignacion = AsignacionMedida.objects.create(**self.asignacion_data)

    def test_asignacion_medida_creacion(self):
        self.assertIsInstance(self.asignacion, AsignacionMedida)
        for field, value in self.asignacion_data.items():
            self.assertEqual(getattr(self.asignacion, field), value)
        self.assertIsNotNone(self.asignacion.fecha_asignacion)
        self.assertIsNotNone(self.asignacion.created_at)
        self.assertIsNotNone(self.asignacion.updated_at)

    def test_asignacion_medida_str(self):
        esperado = f"{self.medida.codigo} - {self.organismo.nombre}"
        self.assertEqual(str(self.asignacion), esperado)
        
    def test_asignacion_medida_creacion(self):
        self.assertIsInstance(self.asignacion, AsignacionMedida)
        for field, value in self.asignacion_data.items():
            self.assertEqual(getattr(self.asignacion, field), value)

            self.assertIsNotNone(self.asignacion.fecha_asignacion)
            self.assertIsNotNone(self.asignacion.created_at)
            self.assertIsNotNone(self.asignacion.updated_at)

    def test_asignacion_medida_str(self):
        esperado = f"{self.medida.codigo} - {self.organismo.nombre}"
        self.assertEqual(str(self.asignacion), esperado)
