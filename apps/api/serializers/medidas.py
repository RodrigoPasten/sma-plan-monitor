from rest_framework import serializers
from apps.medidas.models import Componente, Medida, AsignacionMedida, RegistroAvance
from .organismos import OrganismoSimpleSerializer


class ComponenteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Componente
        fields = ['id', 'nombre', 'descripcion', 'codigo', 'color'] #Revisar


class AsignacionMedidaSerializer(serializers.ModelSerializer):
    organismo = OrganismoSimpleSerializer(read_only=True)

    class Meta:
        model = AsignacionMedida
        fields = ['id', 'organismo', 'es_coordinador', 'descripcion_responsabilidad']


class MedidaListSerializer(serializers.ModelSerializer):
    componente = ComponenteSerializer(read_only=True)

    class Meta:

        model = Medida
        fields = ['id', 'codigo', 'nombre', 'componente', 'estado',
                  'porcentaje_avance', 'fecha_inicio', 'fecha_termino']




class RegistroAvanceSerializer(serializers.ModelSerializer):
    #organismo = OrganismoSimpleSerializer(read_only=True)
    #medidas = serializers.PrimaryKeyRelatedField(
     #   source='medida', 
      #  queryset=Medida.objects.all())

    class Meta:
        model = RegistroAvance
        

        fields = ['id', 'fecha_registro', 'porcentaje_avance', 'descripcion',
                  'evidencia', 'organismo', 'created_at']

        read_only_fields = ['created_at', 'created_by']

    def create(self, validated_data):
        # Asignar el usuario actual como creador
        validated_data['created_by'] = self.context['request'].user

        user = self.context['request'].user

        # Verifica que el usuario esté autenticado y tiene un organismo asignado
        if user.is_authenticated:
            if user.is_organismo:  # Solo los usuarios de organismo pueden registrar avances
                if hasattr(user, 'organismo') and user.organismo:
                    validated_data['organismo'] = user.organismo
                else:
                    raise serializers.ValidationError("El usuario no tiene un organismo asignado.")
            else:
                raise serializers.ValidationError("El usuario no tiene permiso para registrar avances.")
        else:
            raise serializers.ValidationError("El usuario no está autenticado.")

        return super().create(validated_data)

class MedidaDetailSerializer(serializers.ModelSerializer):
    componente = ComponenteSerializer(read_only=True)
    asignaciones = AsignacionMedidaSerializer(many=True, read_only=True)
    registros_avance = RegistroAvanceSerializer(many=True, read_only=True)

    class Meta:
        model = Medida
        fields = ['id', 'codigo', 'nombre', 'descripcion', 'componente',
                  'fecha_inicio', 'fecha_termino', 'estado', 'prioridad',

                  'porcentaje_avance', 'asignaciones', 'registros_avance']


class RegistroAvanceDetailSerializer(serializers.ModelSerializer):
    medida = MedidaDetailSerializer(read_only=True)
    organismo = OrganismoSimpleSerializer(read_only=True)
    
    class Meta:
        model = RegistroAvance
        fields = ['id', 'medida', 'fecha_registro', 'porcentaje_avance', 'descripcion', 'evidencia', 'organismo', 'created_at']

