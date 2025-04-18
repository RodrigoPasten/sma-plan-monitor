from django.shortcuts import render, redirect, get_object_or_404
from rest_framework import viewsets, status
from rest_framework.response import Response

from .models import Medida, LogMedida, Componente, RegistroAvance
#Serializer
from .serializers import MedidaSerializer

from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count

from django.contrib import messages

from .forms import RegistroAvanceForm



from django.views.generic import TemplateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Avg, Count, Sum, Q, F, Case, When, Value, IntegerField
from django.utils import timezone

from apps.medidas.models import Medida, Componente, RegistroAvance
from apps.organismos.models import Organismo


class MedidaViewSet(viewsets.ModelViewSet):

    queryset = Medida.objects.filter(activo=True)
    serializer_class = MedidaSerializer
    #permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        medida = serializer.save(usuario=self.request.user)
        LogMedida.objects.create(usuario=self.request.user, medida=medida, accion="crear")
        
    def perform_update(self, serializer):
        medida = serializer.save()
        LogMedida.objects.create(usuario=self.request.user, medida=medida, accion="actualizar")
        
    def destroy(self, instance, *args, **kwargs):
        """Soft delete: instead of deleting, set activo=False"""
        instance = self.get_object()
        instance.activo = False
        instance.save()
        
        # Log the delete action
        LogMedida.objects.create(usuario=self.request.user, medida=instance, accion="eliminar")
        return Response({"message": "Medida archived instead of deleted"}, status=status.HTTP_204_NO_CONTENT)



class DashboardSMAView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'dashboard/dashboard_sma.html'

    def test_func(self):
        """Verificar que solo los superadmin y admin_sma pueden acceder"""
        return self.request.user.is_superadmin or self.request.user.is_admin_sma

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Fecha actual para cálculos
        hoy = timezone.now().date()

        # 1. Estadísticas generales
        total_medidas = Medida.objects.count()
        medidas_completadas = Medida.objects.filter(estado='completada').count()
        medidas_en_proceso = Medida.objects.filter(estado='en_proceso').count()
        medidas_retrasadas = Medida.objects.filter(
            Q(estado__in=['pendiente', 'en_proceso', 'retrasada']) &
            Q(fecha_termino__lt=hoy)
        ).count()

        avance_promedio = Medida.objects.aggregate(
            promedio=Avg('porcentaje_avance')
        )['promedio'] or 0

        # 2. Avance por componente
        componentes = Componente.objects.annotate(
            total_medidas=Count('medidas'),
            medidas_completadas=Count('medidas', filter=Q(medidas__estado='completada')),
            avance_promedio=Avg('medidas__porcentaje_avance')
        ).values('id', 'nombre', 'color', 'total_medidas', 'medidas_completadas', 'avance_promedio')

        # 3. Medidas próximas a vencer (en los próximos 30 días)
        proximo_mes = hoy + timezone.timedelta(days=30)
        medidas_proximas_vencer = Medida.objects.filter(
            estado__in=['pendiente', 'en_proceso'],
            fecha_termino__gte=hoy,
            fecha_termino__lte=proximo_mes
        ).order_by('fecha_termino').select_related('componente')[:10]

        # 4. Medidas más retrasadas
        medidas_retrasadas_list = Medida.objects.filter(
            estado__in=['pendiente', 'en_proceso', 'retrasada'],
            fecha_termino__lt=hoy
        ).annotate(
            dias_retraso=timezone.now().date() - F('fecha_termino')
        ).order_by('-dias_retraso').select_related('componente')[:10]

        # 5. Organismos con mejor y peor desempeño
        organismos = Organismo.objects.annotate(
            total_medidas=Count('medidas_asignadas'),
            medidas_completadas=Count('medidas_asignadas', filter=Q(medidas_asignadas__estado='completada')),
            porcentaje_completado=Case(
                When(total_medidas=0, then=Value(0)),
                default=100 * F('medidas_completadas') / F('total_medidas'),
                output_field=IntegerField(),
            ),
            avance_promedio=Avg('medidas_asignadas__porcentaje_avance')
        ).filter(total_medidas__gt=0).values(
            'id', 'nombre', 'total_medidas', 'medidas_completadas',
            'porcentaje_completado', 'avance_promedio'
        )

        mejores_organismos = list(organismos.order_by('-avance_promedio')[:5])
        peores_organismos = list(organismos.order_by('avance_promedio')[:5])

        # 6. Últimos avances registrados
        ultimos_avances = RegistroAvance.objects.select_related(
            'medida', 'organismo', 'created_by'
        ).order_by('-fecha_registro')[:10]

        # Añadir todo al contexto
        context.update({
            'total_medidas': total_medidas,
            'medidas_completadas': medidas_completadas,
            'medidas_en_proceso': medidas_en_proceso,
            'medidas_retrasadas': medidas_retrasadas,
            'avance_promedio': avance_promedio,
            'componentes': componentes,
            'medidas_proximas_vencer': medidas_proximas_vencer,
            'medidas_retrasadas_list': medidas_retrasadas_list,
            'mejores_organismos': mejores_organismos,
            'peores_organismos': peores_organismos,
            'ultimos_avances': ultimos_avances
        })

        return context
@login_required
def registrar_avance(request, medida_id=None):
    # Verificar que el usuario pertenezca a un organismo
    if not hasattr(request.user, 'organismo') or not request.user.organismo:
        messages.error(request, "No tienes un organismo asignado para registrar avances.")
        return redirect('dashboard_organismo')

    organismo = request.user.organismo

    # Si se proporciona un ID de medida, pre-seleccionarla
    initial = {}
    if medida_id:
        medida = get_object_or_404(
            Medida,
            id=medida_id,
            responsables=organismo
        )
        initial['medida'] = medida

    if request.method == 'POST':
        form = RegistroAvanceForm(request.POST, request.FILES, organismo=organismo)
        if form.is_valid():
            avance = form.save(commit=False)
            avance.organismo = organismo
            avance.created_by = request.user
            avance.save()

            # Actualizar el porcentaje de avance de la medida
            medida = avance.medida
            medida.porcentaje_avance = avance.porcentaje_avance
            medida.save()

            messages.success(request, "Avance registrado correctamente.")
            return redirect('medidas:detalle', pk=medida.id)
    else:
        form = RegistroAvanceForm(initial=initial, organismo=organismo)

    return render(request, 'medidas/registrar_avance.html', {
        'form': form,
        'medida_id': medida_id
    })


class MedidaDetailView(LoginRequiredMixin, DetailView):
    model = Medida
    template_name = 'medidas/detalle_medida.html'
    context_object_name = 'medida'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        medida = self.object

        # Añadir información adicional al contexto
        context['registros_avance'] = medida.registros_avance.all().order_by('-fecha_registro')
        context['asignaciones'] = medida.asignaciones.all().select_related('organismo')

        return context


class DashboardOrganismoView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'dashboard/dashboard_organismo.html'

    def test_func(self):
        """Verificar que el usuario pertenece a un organismo"""
        return self.request.user.is_organismo

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        organismo = self.request.user.organismo

        # Obtener medidas asignadas al organismo del usuario
        medidas_asignadas = Medida.objects.filter(
            responsables=organismo
        ).select_related('componente')

        # Otras estadísticas relevantes
        total_medidas = medidas_asignadas.count()
        medidas_completadas = medidas_asignadas.filter(estado='completada').count()
        medidas_en_proceso = medidas_asignadas.filter(estado='en_proceso').count()
        medidas_retrasadas = medidas_asignadas.filter(
            estado__in=['pendiente', 'en_proceso'],
            fecha_termino__lt=timezone.now().date()
        ).count()

        avance_promedio = medidas_asignadas.aggregate(
            promedio=Avg('porcentaje_avance')
        )['promedio'] or 0

        # Últimos avances registrados por este organismo
        ultimos_avances = RegistroAvance.objects.filter(
            organismo=organismo
        ).select_related('medida').order_by('-fecha_registro')[:10]

        context.update({
            'organismo': organismo,
            'medidas_asignadas': medidas_asignadas,
            'total_medidas': total_medidas,
            'medidas_completadas': medidas_completadas,
            'medidas_en_proceso': medidas_en_proceso,
            'medidas_retrasadas': medidas_retrasadas,
            'avance_promedio': avance_promedio,
            'ultimos_avances': ultimos_avances
        })

        return context