# apps/reportes/forms.py
from django import forms
from .models import TipoReporte, ConfiguracionReporte, ReporteGenerado


class ReporteGeneradoForm(forms.ModelForm):
    """
    Formulario para solicitar un nuevo reporte.
    """
    FORMATO_CHOICES = [
        ('pdf', 'PDF'),
        ('xlsx', 'Excel'),
        ('csv', 'CSV'),
    ]

    formato = forms.ChoiceField(
        choices=FORMATO_CHOICES,
        initial='pdf',
        widget=forms.RadioSelect,
        label="Formato del reporte"
    )

    class Meta:
        model = ReporteGenerado
        fields = ['tipo_reporte', 'descripcion']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(ReporteGeneradoForm, self).__init__(*args, **kwargs)

        # Limitar tipos de reporte a los activos
        self.fields['tipo_reporte'].queryset = TipoReporte.objects.filter(activo=True)


class ConfiguracionReporteForm(forms.ModelForm):
    """
    Formulario para guardar configuraciones de reportes personalizadas.
    """

    class Meta:
        model = ConfiguracionReporte
        fields = ['tipo_reporte', 'nombre', 'descripcion', 'fecha_inicio', 'fecha_fin', 'organismos', 'formato']
        widgets = {
            'fecha_inicio': forms.DateInput(attrs={'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date'}),
            'descripcion': forms.Textarea(attrs={'rows': 3}),
        }