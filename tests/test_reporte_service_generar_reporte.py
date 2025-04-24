import unittest
import pytest
from django.contrib.auth import get_user_model

from apps.reportes.models import TipoReporte, ReporteGenerado
from apps.reportes.services import ReporteService
from apps.organismos.models import Organismo, TipoOrganismo
from apps.medidas.models import Componente


@pytest.mark.django_db
class ReporteServiceGenerarReporteTest(unittest.TestCase):
    def setUp(self):
        super().setUp()
        User = get_user_model()

        self.user_superadmin = User.objects.create_user(
            username="superadmin", password="testpassword", rol="superadmin"
        )
        self.user_admin_sma = User.objects.create_user(
            username="admin_sma", password="testpassword", rol="admin_sma"
        )
        self.user_organismo = User.objects.create_user(
            username="organismo", password="testpassword", rol="organismo"
        )

        tipo_org = TipoOrganismo.objects.create(nombre="Tipo Prueba")
        self.organismo = Organismo.objects.create(
            nombre="Organismo Prueba",
            tipo=tipo_org,
            rut="12345678-9",
            direccion="Calle Falsa",
            comuna="Comuna X",
            region="Región Y",
            telefono="987654321",
            email_contacto="org@test.com",
        )
        self.user_organismo.organismo = self.organismo
        self.user_organismo.save()

        self.componente = Componente.objects.create(nombre="Componente Prueba")

        self.tipo_reporte_general = TipoReporte.objects.create(
            nombre="Reporte General",
            tipo="general",
            acceso_superadmin=True,
            acceso_admin_sma=True,
            acceso_organismos=True
        )
        self.tipo_reporte_organismo = TipoReporte.objects.create(
            nombre="Reporte Organismo",
            tipo="organismo",
            acceso_superadmin=True,
            acceso_admin_sma=True,
            acceso_organismos=True
        )
        self.tipo_reporte_componente = TipoReporte.objects.create(
            nombre="Reporte Componente",
            tipo="componente",
            acceso_superadmin=True,
            acceso_admin_sma=True,
            acceso_organismos=True
        )

    def test_generar_reporte_permisos(self):
        tipo_sin_permiso = TipoReporte.objects.create(
            nombre="Sin permiso", tipo="general",
            acceso_superadmin=False, acceso_admin_sma=False, acceso_organismos=False
        )
        reporte_super = ReporteService.generar_reporte(
            self.user_superadmin,
            tipo_sin_permiso.id
        )
        self.assertIsInstance(reporte_super, ReporteGenerado)

        tipo_organismo_sin = TipoReporte.objects.create(
            nombre="Org sin permiso", tipo="organismo",
            acceso_superadmin=True, acceso_admin_sma=True, acceso_organismos=False
        )
        self.assertIsNone(
            ReporteService.generar_reporte(self.user_organismo, tipo_organismo_sin.id)
        )

        tipo_admin_sin = TipoReporte.objects.create(
            nombre="Admin SMA sin permiso", tipo="general",
            acceso_superadmin=True, acceso_admin_sma=False, acceso_organismos=True
        )
        self.assertIsNone(
            ReporteService.generar_reporte(self.user_admin_sma, tipo_admin_sin.id)
        )

    def test_generar_reporte_organismo_permisos(self):
        otro_org = Organismo.objects.create(
            nombre="Otro Org", tipo=TipoOrganismo.objects.first(),
            rut="87654321-0", direccion="", comuna="", region="", telefono="", email_contacto=""
        )

        rpt = ReporteService.generar_reporte(
            self.user_organismo,
            self.tipo_reporte_organismo.id,
            organismo_id=otro_org.id
        )
        self.assertIsNone(rpt)

        rpt = ReporteService.generar_reporte(
            self.user_organismo,
            self.tipo_reporte_organismo.id,
            organismo_id=self.organismo.id
        )
        self.assertIsInstance(rpt, ReporteGenerado)

    def test_generar_reporte_componente_permisos(self):
        rpt_sin = ReporteService.generar_reporte(
            self.user_superadmin,
            self.tipo_reporte_componente.id
        )
        self.assertIsNone(rpt_sin)

        rpt_con = ReporteService.generar_reporte(
            self.user_superadmin,
            self.tipo_reporte_componente.id,
            componente_id=self.componente.id
        )
        self.assertIsInstance(rpt_con, ReporteGenerado)

    def test_generar_reporte_titulo_default_y_personalizado(self):
        rpt_def = ReporteService.generar_reporte(
            self.user_superadmin,
            self.tipo_reporte_general.id
        )
        self.assertIn(self.tipo_reporte_general.nombre, rpt_def.titulo)

        titulo = "Mi Título"
        rpt_custom = ReporteService.generar_reporte(
            self.user_superadmin,
            self.tipo_reporte_general.id,
            titulo=titulo
        )
        self.assertEqual(rpt_custom.titulo, titulo)
