
from django.db import migrations

def forward_func(apps, schema_editor):
    # Este código no hace nada, pero la migración se aplicará
    pass

def backward_func(apps, schema_editor):
    pass

class Migration(migrations.Migration):
    dependencies = [
        ('reportes', '0003_remove_visualizacion_componentes_and_more'),  # Ajusta esto con tu última migración
    ]

    operations = [
        migrations.RunPython(forward_func, backward_func),
    ]