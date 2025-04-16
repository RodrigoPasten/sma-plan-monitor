
from django.db import migrations

def forward_func(apps, schema_editor):
    # Este código no hace nada, pero la migración se aplicará
    pass

def backward_func(apps, schema_editor):
    pass

class Migration(migrations.Migration):
    dependencies = [
        ('reportes', '0001_initial'),  # Ajusta esto con tu última migración
    ]

    operations = [
        migrations.RunPython(forward_func, backward_func),
    ]