
import os

from datetime import datetime
from django.conf import settings
from django.db.models import Avg, Count, Sum, Q
from django.core.files.base import ContentFile

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import renderPDF

from apps.medidas.models import Medida, Componente, RegistroAvance
from apps.organismos.models import Organismo
from .models import TipoReporte, ReporteGenerado


class ReporteService:
    @staticmethod
    def generar_reporte(
            usuario,
            tipo_reporte_id,
            titulo=None,
            organismo_id=None,
            componente_id=None,
            fecha_inicio=None,
            fecha_fin=None,
            **kwargs
    ):
        """
        Genera un reporte PDF según los parámetros especificados.

        Args:
            usuario: Usuario que genera el reporte
            tipo_reporte_id: ID del tipo de reporte a generar
            titulo: Título personalizado (opcional)
            organismo_id: ID del organismo (para reportes por organismo)
            componente_id: ID del componente (para reportes por componente)
            fecha_inicio: Fecha de inicio del período a reportar
            fecha_fin: Fecha de fin del período a reportar
            **kwargs: Parámetros adicionales específicos del reporte

        Returns:
            ReporteGenerado: Objeto del reporte generado con el archivo PDF
        """
        try:
            # Obtener el tipo de reporte
            tipo_reporte = TipoReporte.objects.get(pk=tipo_reporte_id)

            # Verificar permisos
            if usuario.rol == 'organismo' and not tipo_reporte.acceso_organismos:
                return None
            elif usuario.rol == 'admin_sma' and not tipo_reporte.acceso_admin_sma:
                return None

            # Si es usuario de organismo, solo puede reportar sobre su organismo
            if usuario.rol == 'organismo':
                if organismo_id and usuario.organismo.id != organismo_id:
                    return None
                organismo_id = usuario.organismo.id

            # Establecer valores por defecto
            if not titulo:
                titulo = f"{tipo_reporte.nombre} - {datetime.now().strftime('%d/%m/%Y')}"

            # Crear objeto de reporte
            reporte = ReporteGenerado(
                tipo_reporte=tipo_reporte,
                usuario=usuario,
                titulo=titulo,
                parametros={
                    'organismo_id': organismo_id,
                    'componente_id': componente_id,
                    'fecha_inicio': fecha_inicio.isoformat() if fecha_inicio else None,
                    'fecha_fin': fecha_fin.isoformat() if fecha_fin else None,
                    **kwargs
                }
            )

            if organismo_id:
                reporte.organismo_id = organismo_id

            if componente_id:
                reporte.componente_id = componente_id

            # Generar el PDF según el tipo de reporte
            if tipo_reporte.tipo == 'general':
                pdf_content = ReporteService._generar_reporte_general(reporte)
            elif tipo_reporte.tipo == 'organismo':
                pdf_content = ReporteService._generar_reporte_organismo(reporte)
            elif tipo_reporte.tipo == 'componente':
                pdf_content = ReporteService._generar_reporte_componente(reporte)
            else:
                return None

            # Guardar el archivo PDF
            filename = f"reporte_{tipo_reporte.tipo}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            reporte.archivo.save(filename, ContentFile(pdf_content.getvalue()))
            reporte.save()

            return reporte

        except Exception as e:
            import traceback
            print(f"Error al generar reporte: {e}")
            print(traceback.format_exc())
            return None

    @staticmethod
    def _generar_reporte_general(reporte):
        """Genera un reporte general del plan de descontaminación"""
        # Crear un buffer para el PDF
        from io import BytesIO
        buffer = BytesIO()

        # Crear el documento
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=72, leftMargin=72,
            topMargin=72, bottomMargin=72
        )

        # Contenedor de elementos
        elements = []

        # Estilos
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(
            name='Titulo',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=12
        ))
        styles.add(ParagraphStyle(
            name='Subtitulo',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=8
        ))

        # Título del reporte
        elements.append(Paragraph(f"REPORTE GENERAL DEL PLAN DE DESCONTAMINACIÓN", styles['Titulo']))
        elements.append(Paragraph(f"{reporte.titulo}", styles['Subtitulo']))
        elements.append(Spacer(1, 12))

        # Fecha de generación
        elements.append(
            Paragraph(f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
        elements.append(
            Paragraph(f"Generado por: {reporte.usuario.get_full_name() or reporte.usuario.username}", styles['Normal']))
        elements.append(Spacer(1, 24))

        # Resumen general
        elements.append(Paragraph("1. RESUMEN GENERAL", styles['Heading2']))

        # Estadísticas generales
        total_medidas = Medida.objects.count()
        medidas_completadas = Medida.objects.filter(estado='completada').count()
        porcentaje_avance = Medida.objects.aggregate(avg=Avg('porcentaje_avance'))['avg'] or 0

        data = [
            ["Métricas", "Valores"],
            ["Total de Medidas", str(total_medidas)],
            ["Medidas Completadas", str(medidas_completadas)],
            ["Porcentaje de Avance Global", f"{porcentaje_avance:.2f}%"]
        ]

        table = Table(data, colWidths=[doc.width / 2.0] * 2)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (1, 0), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (1, 0), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ]))

        elements.append(table)
        elements.append(Spacer(1, 12))

        # Distribución por estado
        elements.append(Paragraph("2. DISTRIBUCIÓN POR ESTADO", styles['Heading2']))

        # Obtener datos para el gráfico de estados
        estados = Medida.objects.values('estado').annotate(total=Count('id'))

        # Crear gráfico de torta para estados
        drawing = Drawing(400, 200)
        pie = Pie()
        pie.x = 150
        pie.y = 50
        pie.width = 100
        pie.height = 100

        pie_data = []
        pie_labels = []

        estado_nombre = {
            'pendiente': 'Pendiente',
            'en_proceso': 'En Proceso',
            'completada': 'Completada',
            'retrasada': 'Retrasada',
            'suspendida': 'Suspendida'
        }

        for estado in estados:
            pie_data.append(estado['total'])
            pie_labels.append(estado_nombre.get(estado['estado'], estado['estado']))

        pie.data = pie_data
        pie.labels = pie_labels
        pie.slices.strokeWidth = 0.5

        # Colores para cada estado
        colors_dict = {
            'Pendiente': colors.lavender,
            'En Proceso': colors.lightblue,
            'Completada': colors.lightgreen,
            'Retrasada': colors.pink,
            'Suspendida': colors.lightgrey
        }

        for i, label in enumerate(pie_labels):
            pie.slices[i].fillColor = colors_dict.get(label, colors.white)

        drawing.add(pie)
        elements.append(drawing)

        # Tabla con los datos de estado
        data = [["Estado", "Cantidad", "Porcentaje"]]
        for estado in estados:
            nombre = estado_nombre.get(estado['estado'], estado['estado'])
            porcentaje = (estado['total'] / total_medidas) * 100 if total_medidas > 0 else 0
            data.append([nombre, estado['total'], f"{porcentaje:.2f}%"])

        table = Table(data, colWidths=[doc.width / 3.0] * 3)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (2, 0), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (2, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 0), (2, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (2, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ]))

        elements.append(Spacer(1, 12))
        elements.append(table)
        elements.append(Spacer(1, 24))

        # Avance por componente
        elements.append(Paragraph("3. AVANCE POR COMPONENTE", styles['Heading2']))

        # Obtener datos por componente
        componentes = Componente.objects.annotate(
            total_medidas=Count('medidas'),
            avance_promedio=Avg('medidas__porcentaje_avance')
        ).order_by('-avance_promedio')

        data = [["Componente", "Medidas", "Avance"]]
        for comp in componentes:
            data.append([
                comp.nombre,
                comp.total_medidas,
                f"{comp.avance_promedio:.2f}%" if comp.avance_promedio else "0.00%"
            ])

        table = Table(data, colWidths=[doc.width / 2.0, doc.width / 4.0, doc.width / 4.0])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (2, 0), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (2, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 0), (2, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (2, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ]))

        elements.append(table)
        elements.append(Spacer(1, 24))

        # Construir el PDF
        doc.build(elements)

        return buffer

    @staticmethod
    def _generar_reporte_organismo(reporte):
        """Genera un reporte específico para un organismo"""
        # Implementación similar a la anterior pero enfocada en un organismo específico
        from io import BytesIO
        buffer = BytesIO()

        # Verificar que exista el organismo
        organismo_id = reporte.parametros.get('organismo_id')
        if not organismo_id:
            return None

        try:
            organismo = Organismo.objects.get(pk=organismo_id)
        except Organismo.DoesNotExist:
            return None

        # Crear el documento
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=72, leftMargin=72,
            topMargin=72, bottomMargin=72
        )

        # Contenedor de elementos
        elements = []

        # Estilos
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(
            name='Titulo',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=12
        ))

        # Título del reporte
        elements.append(Paragraph(f"REPORTE DEL ORGANISMO: {organismo.nombre.upper()}", styles['Titulo']))
        elements.append(Spacer(1, 12))

        # Fecha de generación
        elements.append(
            Paragraph(f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
        elements.append(
            Paragraph(f"Generado por: {reporte.usuario.get_full_name() or reporte.usuario.username}", styles['Normal']))
        elements.append(Spacer(1, 24))

        # Información del organismo
        elements.append(Paragraph("1. INFORMACIÓN DEL ORGANISMO", styles['Heading2']))

        data = [
            ["Dato", "Valor"],
            ["Nombre", organismo.nombre],
            ["Tipo", organismo.tipo.nombre if hasattr(organismo, 'tipo') and organismo.tipo else "No especificado"],
            ["Dirección", organismo.direccion if hasattr(organismo, 'direccion') else "No especificada"],
            ["Email de contacto",
             organismo.email_contacto if hasattr(organismo, 'email_contacto') else "No especificado"]
        ]

        table = Table(data, colWidths=[doc.width / 3.0, doc.width * 2 / 3.0])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (1, 0), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (1, 0), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ]))

        elements.append(table)
        elements.append(Spacer(1, 24))

        # Medidas asignadas
        elements.append(Paragraph("2. MEDIDAS ASIGNADAS", styles['Heading2']))

        # Obtener medidas asignadas al organismo
        medidas = Medida.objects.filter(responsables=organismo)

        if medidas.exists():
            # Resumen de medidas
            total_medidas = medidas.count()
            medidas_completadas = medidas.filter(estado='completada').count()
            porcentaje_avance = medidas.aggregate(avg=Avg('porcentaje_avance'))['avg'] or 0

            data = [
                ["Métrica", "Valor"],
                ["Total de Medidas Asignadas", str(total_medidas)],
                ["Medidas Completadas", str(medidas_completadas)],
                ["Porcentaje de Avance", f"{porcentaje_avance:.2f}%"]
            ]

            table = Table(data, colWidths=[doc.width / 2.0] * 2)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (1, 0), colors.lightblue),
                ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (1, 0), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ]))

            elements.append(table)
            elements.append(Spacer(1, 12))

            # Lista de medidas
            elements.append(Paragraph("Detalle de Medidas Asignadas:", styles['Heading3']))

            data = [["Código", "Nombre", "Estado", "Avance"]]
            for medida in medidas:
                data.append([
                    medida.codigo,
                    medida.nombre,
                    medida.get_estado_display() if hasattr(medida, 'get_estado_display') else medida.estado,
                    f"{medida.porcentaje_avance:.2f}%"
                ])

            table = Table(data, colWidths=[doc.width * 0.15, doc.width * 0.45, doc.width * 0.2, doc.width * 0.2])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('ALIGN', (3, 1), (3, -1), 'CENTER'),
            ]))

            elements.append(table)
        else:
            elements.append(Paragraph("No hay medidas asignadas a este organismo.", styles['Normal']))

        elements.append(Spacer(1, 24))

        # Últimos registros de avance
        elements.append(Paragraph("3. ÚLTIMOS REGISTROS DE AVANCE", styles['Heading2']))

        # Obtener últimos registros de avance
        registros = RegistroAvance.objects.filter(organismo=organismo).order_by('-fecha_registro')[:10]

        if registros.exists():
            data = [["Fecha", "Medida", "Avance", "Descripción"]]
            for registro in registros:
                data.append([
                    registro.fecha_registro.strftime('%d/%m/%Y'),
                    registro.medida.codigo,
                    f"{registro.porcentaje_avance:.2f}%",
                    registro.descripcion[:50] + ('...' if len(registro.descripcion) > 50 else '')
                ])

            table = Table(data, colWidths=[doc.width * 0.15, doc.width * 0.15, doc.width * 0.15, doc.width * 0.55])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('ALIGN', (2, 1), (2, -1), 'CENTER'),
            ]))

            elements.append(table)
        else:
            elements.append(Paragraph("No hay registros de avance para este organismo.", styles['Normal']))

        # Construir el PDF
        doc.build(elements)

        return buffer

    @staticmethod
    def _generar_reporte_componente(reporte):
        """Genera un reporte específico para un componente del plan"""
        # Implementación para reporte por componente (similar a las anteriores)
        # Dejamos solo la estructura básica para no extender demasiado el código
        from io import BytesIO
        buffer = BytesIO()

        # Verificar que exista el componente
        componente_id = reporte.parametros.get('componente_id')
        if not componente_id:
            return None

        try:
            componente = Componente.objects.get(pk=componente_id)
        except Componente.DoesNotExist:
            return None

        # Crear el documento
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=72, leftMargin=72,
            topMargin=72, bottomMargin=72
        )

        # Contenedor de elementos
        elements = []

        # Estilos
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(
            name='Titulo',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=12
        ))

        # Título del reporte
        elements.append(Paragraph(f"REPORTE DEL COMPONENTE: {componente.nombre.upper()}", styles['Titulo']))
        elements.append(Spacer(1, 12))

        # Aquí iría el contenido específico del reporte por componente
        # similar a los anteriores

        # Construir el PDF
        doc.build(elements)

        return buffer