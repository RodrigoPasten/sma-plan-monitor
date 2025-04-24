import unittest
import pytest
from django.urls import reverse
from django.test import Client
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.messages import get_messages
from apps.reportes.models import TipoReporte, ReporteGenerado
from apps.organismos.models import Organismo, TipoOrganismo
from apps.medidas.models import Componente

@pytest.mark.django_db
class DescargarReporteViewTest(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.client = Client()
        User = get_user_model()
        self.user = User.objects.create_user(
            username="testuser", password="testpassword", rol="superadmin"
        )
        assert self.client.login(username="testuser", password="testpassword")

        self.tipo_reporte = TipoReporte.objects.create(
            nombre="Reporte de Prueba", tipo="general",
            acceso_superadmin=True, acceso_admin_sma=False, acceso_organismos=False
        )
        self.file_content = b"This is a dummy PDF file"
        self.uploaded_file = SimpleUploadedFile(
            "test.pdf", self.file_content, content_type="application/pdf"
        )

        self.reporte = ReporteGenerado.objects.create(
            tipo_reporte=self.tipo_reporte,
            usuario=self.user,
            titulo="Reporte de Prueba",
            archivo=self.uploaded_file
        )

        self.url = reverse("reportes:descargar_reporte", kwargs={"pk": self.reporte.pk})

    def test_descargar_reporte_access(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp["Content-Type"], "application/pdf")
        self.assertIn("Content-Disposition", resp)
        self.assertEqual(
            resp["Content-Disposition"],
            f'attachment; filename="reporte_general_{self.reporte.id}.pdf"'
        )
        self.assertEqual(resp.content, self.file_content)

    def test_descargar_reporte_file_not_exists(self):
        self.reporte.archivo.delete(save=True)

        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 302)
        expected = reverse("reportes:detalle_reporte", kwargs={"pk": self.reporte.pk})
        self.assertEqual(resp["Location"], expected)

        messages = list(get_messages(resp.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "El archivo no está disponible.")
