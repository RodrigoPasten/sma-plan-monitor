# apps/medidas/tests/test_medida_serializer.py
import pytest
import unittest
from rest_framework.test import APIClient
from apps.organismos.models import Organismo, TipoOrganismo 
from apps.medidas.models import Componente, Medida
from apps.medidas.serializers import MedidaSerializer
from datetime import date

@pytest.mark.django_db
class MedidaSerializerTest(unittest.TestCase):
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
        self.medida_data = {
            "nombre": "Reducción de emisiones",
            "codigo": "RED-002",
            "descripcion": "Implementar medidas para reducir las emisiones de gases",
            "componente": self.componente.id,
            "fecha_inicio": "2024-01-01",
            "fecha_termino": "2024-12-31",
            "estado": "pendiente",
            "prioridad": "media",
            "porcentaje_avance": 50.50,
        }

        
        self.medida = Medida.objects.create(
            nombre=self.medida_data["nombre"],
            codigo=self.medida_data["codigo"],
            descripcion=self.medida_data["descripcion"],
            componente=self.componente,
            fecha_inicio=self.medida_data["fecha_inicio"],
            fecha_termino=self.medida_data["fecha_termino"],
            estado=self.medida_data["estado"],
            prioridad=self.medida_data["prioridad"],
            porcentaje_avance=self.medida_data["porcentaje_avance"],
        )
        self.medida.responsables.add(self.organismo)

        self.client = APIClient()

    def test_medida_serializer_create(self):
        data = self.medida_data.copy()
        data["codigo"] = "RED-003"

        serializer = MedidaSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        medida = serializer.save()
        medida.responsables.add(self.organismo)

        self.assertIsInstance(medida, Medida)
        self.assertEqual(medida.nombre, data["nombre"])
        self.assertEqual(medida.codigo, data["codigo"])


    def test_medida_serializer_update(self):
        new_data = self.medida_data.copy()
        new_data["nombre"] = "Nuevo Nombre"

        serializer = MedidaSerializer(self.medida, data=new_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        self.medida.refresh_from_db()
        self.assertEqual(self.medida.nombre, "Nuevo Nombre")
