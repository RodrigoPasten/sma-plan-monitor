# apps/medidas/tests/test_modelo_medidas.py
import pytest
import unittest
from datetime import date
from django.core.exceptions import ValidationError
from apps.organismos.models import Organismo, TipoOrganismo
from apps.medidas.models import Componente, Medida

@pytest.mark.django_db
class TestMedidasModel(unittest.TestCase):
    def setUp(self):
        self.tipo = TipoOrganismo.objects.create(nombre="Municipalidad")
        self.organismo = Organismo.objects.create(
            nombre="Municipalidad",
            tipo=self.tipo,
            direccion="Calle Falsa 123",
            comuna="Curicó",
            region="Maule",
            telefono="123456789",
            email_contacto="contacto@municipalidad.cl"
        )
        self.componente = Componente.objects.create(
            nombre="Calidad del Aire",
            descripcion="Controlar emisiones"
        )
        self.medida_data = {
            "nombre": "Reducción de emisiones",
            "codigo": "RED-001",
            "descripcion": "Implementar medidas para reducir las emisiones de gases",
            "componente": self.componente,
            "fecha_inicio": date(2024, 1, 1),
            "fecha_termino": date(2024, 12, 31),
            "porcentaje_avance": 50.50,
        }
        self.medida = Medida.objects.create(**self.medida_data)

    def test_creacion_medida_valida(self):
        self.assertEqual(self.medida.nombre, "Reducción de emisiones")
    
    def test_medida_codigo_unique(self):
        with self.assertRaises(ValidationError) as context:
            medida_duplicada = Medida(
                nombre="Otra Medida",
                codigo=self.medida_data["codigo"],
                descripcion="Descripción",
                componente=self.componente,
                fecha_inicio=date(2024, 1, 1),
                fecha_termino=date(2024, 12, 31),
            )
            medida_duplicada.full_clean()
        self.assertIn("codigo", context.exception.error_dict)

    def test_medida_creation(self):
        self.assertIsInstance(self.medida, Medida)

        for field, value in self.medida_data.items():
            if field not in ["fecha_inicio", "fecha_termino", "componente"]:
                self.assertEqual(getattr(self.medida, field), value)

        self.assertEqual(self.medida.fecha_inicio, self.medida_data["fecha_inicio"])
        self.assertEqual(self.medida.fecha_termino, self.medida_data["fecha_termino"])
        self.assertEqual(self.medida.componente, self.componente)
        self.assertEqual(self.medida.estado, "pendiente")
        self.assertEqual(self.medida.prioridad, "media")
        self.assertTrue(self.medida.activo)
        self.assertIsNotNone(self.medida.created_at)
        self.assertIsNotNone(self.medida.updated_at)

    def test_medida_estado_choices(self):
        self.medida.estado = "invalido"
        with self.assertRaises(ValidationError) as context:
            self.medida.full_clean()
        self.assertIn("estado", context.exception.error_dict)

    def test_medida_prioridad_choices(self):
        self.medida.prioridad = "invalida"
        with self.assertRaises(ValidationError) as context:
            self.medida.full_clean()
        self.assertIn("prioridad", context.exception.error_dict)

    def test_medida_ordenamiento(self):
        medida1 = Medida.objects.create(
            nombre="Otra Medida",
            codigo="AAA-001",
            descripcion="Descripción",
            componente=self.componente,
            fecha_inicio=date(2024, 1, 1),
            fecha_termino=date(2024, 1, 31),
        )
        medida2 = Medida.objects.create(
            nombre="Y otra",
            codigo="BBB-002",
            descripcion="Descripción",
            componente=self.componente,
            fecha_inicio=date(2024, 1, 1),
            fecha_termino=date(2024, 1, 31),
        )

        queryset_codigos = list(Medida.objects.values_list("codigo", flat=True))
        esperado = sorted(queryset_codigos) 
        self.assertEqual(queryset_codigos, esperado)

