from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiResponse
from ..filters import MedidaFilter, RegistroAvanceFilter
from apps.medidas.models import Componente, Medida, RegistroAvance
from ..serializers.medidas import (
    ComponenteSerializer,
    MedidaListSerializer,
    MedidaDetailSerializer,
    RegistroAvanceSerializer
)
from ..permissions import (
    IsPublicEndpoint,
    IsAdminSMA,
    IsSuperAdmin,
    IsOrganismoMember,
    IsOrganismoOwner
)
from apps.medidas.serializers import MedidaSerializer


@extend_schema_view(
    list=extend_schema(description="Listar todos los componentes del plan"),
    retrieve=extend_schema(description="Obtener un componente específico")
)
class ComponenteViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint para consultar componentes del plan.
    """
    queryset = Componente.objects.filter(activo=True)
    serializer_class = ComponenteSerializer
    permission_classes = [IsPublicEndpoint]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['nombre', 'codigo']


@extend_schema_view(
    list=extend_schema(description="Listar todas las medidas"),
    retrieve=extend_schema(description="Obtener una medida específica"),
    create=extend_schema(description="Crear una nueva medida", request=MedidaSerializer, responses={201: MedidaDetailSerializer}),
    update=extend_schema(description="Actualizar una medida existente"),
    partial_update=extend_schema(description="Actualizar parcialmente una medida"),
    destroy=extend_schema(description="Eliminar una medida")
)
class MedidaViewSet(viewsets.ModelViewSet):
    """
    API endpoint para consultar y gestionar medidas.
    """
    queryset = Medida.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['componente', 'estado', 'prioridad']
    search_fields = ['codigo', 'nombre', 'descripcion']
    filterset_class = MedidaFilter

    def get_queryset(self):
        user = self.request.user

        # Si es administrador, ve todas las medidas
        if user.is_authenticated and (user.is_superadmin or user.is_admin_sma):
            return Medida.objects.all()

        # Si es usuario de organismo, solo ve sus medidas asignadas
        if user.is_authenticated and user.is_organismo:
            return Medida.objects.filter(
                responsables=user.organismo
            )

        # Para usuarios no autenticados o ciudadanos
        return Medida.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return MedidaListSerializer
        elif self.action == 'create':
            return MedidaSerializer
        return MedidaDetailSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [IsPublicEndpoint]
        elif self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsSuperAdmin | IsAdminSMA]
        else:
            permission_classes = [IsPublicEndpoint]
        return [permission() for permission in permission_classes]

    @extend_schema(
        description="Obtener los avances de una medida específica",
        responses={200: RegistroAvanceSerializer(many=True)}
    )
    @action(detail=True, methods=['get'])
    def avances(self, request, pk=None):
        """
        Obtener los avances de una medida específica.
        """
        medida = self.get_object()
        avances = RegistroAvance.objects.filter(medida=medida)
        serializer = RegistroAvanceSerializer(avances, many=True)
        return Response(serializer.data)

    @extend_schema(
        description="Registrar un nuevo avance para esta medida",
        request=RegistroAvanceSerializer,
        responses={
            201: RegistroAvanceSerializer,
            403: OpenApiResponse(description="El organismo del usuario no está asignado a esta medida"),
            400: OpenApiResponse(description="Datos inválidos")
        }
    )
    @action(detail=True, methods=['post'], permission_classes=[IsOrganismoMember])
    def registrar_avance(self, request, pk=None):
        """
        Registrar un nuevo avance para esta medida.
        """
        medida = self.get_object()

        # Verificar que el organismo del usuario esté asignado a esta medida
        user = request.user
        if not medida.responsables.filter(id=user.organismo.id).exists():
            return Response(
                {"detail": "Tu organismo no está asignado a esta medida"},
                status=status.HTTP_403_FORBIDDEN
            )

        # Crear el registro de avance
        serializer = RegistroAvanceSerializer(
            data=request.data,
            context={'request': request}
        )

        if serializer.is_valid():
            serializer.save(
                medida=medida,
                organismo=user.organismo,
                created_by=user
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    list=extend_schema(description="Listar todos los registros de avance"),
    retrieve=extend_schema(description="Obtener un registro de avance específico"),
    create=extend_schema(description="Crear un nuevo registro de avance"),
    update=extend_schema(description="Actualizar un registro de avance existente"),
    partial_update=extend_schema(description="Actualizar parcialmente un registro de avance"),
    destroy=extend_schema(description="Eliminar un registro de avance")
)
class RegistroAvanceViewSet(viewsets.ModelViewSet):
    """
    API endpoint para consultar y gestionar registros de avance.
    """
    queryset = RegistroAvance.objects.all()
    serializer_class = RegistroAvanceSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['medida', 'organismo', 'fecha_registro']
    filterset_class = RegistroAvanceFilter

    def get_queryset(self):
        user = self.request.user

        # Si es administrador, ve todos los registros
        if user.is_authenticated and (user.is_superadmin or user.is_admin_sma):
            return RegistroAvance.objects.all()

        # Si es usuario de organismo, solo ve sus propios registros
        if user.is_authenticated and user.is_organismo:
            return RegistroAvance.objects.filter(organismo=user.organismo)

        # Para usuarios no autenticados, no ver nada
        return RegistroAvance.objects.none()

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [IsPublicEndpoint]
        elif self.action in ['create']:
            permission_classes = [IsOrganismoMember]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [IsOrganismoOwner | IsAdminSMA | IsSuperAdmin]
        elif self.action in ['destroy']:
            permission_classes = [IsSuperAdmin | IsAdminSMA]
        else:
            permission_classes = [IsPublicEndpoint]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user,
            organismo=self.request.user.organismo
        )