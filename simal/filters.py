from django import forms
import django_filters
from .models import *
from .forms import *


class CampoFilter(django_filters.FilterSet):
    class Meta:
        model = Campo
        fields = {
            'ponto': ['icontains'],

            # Adicione mais campos conforme necessário
        }


class ProgramaColetaFilter(django_filters.FilterSet):

    class Meta:
        model = ProgramaColeta
        fields = {
            'local_coleta': ['icontains'],
           'data_coleta_campo': ['exact'],
           'status_coleta': ['exact'],
         # Adicione mais campos conforme necessário
        }

class ResultadosColetaFilter(django_filters.FilterSet):
    ponto = django_filters.CharFilter(
        lookup_expr='icontains', label='Ponto')
    codigo_coleta = django_filters.CharFilter(
        lookup_expr='icontains', label='Código da Coleta')

class PontoFilter(django_filters.FilterSet):
    codigo = django_filters.ChoiceFilter(
        field_name='nome',
        lookup_expr='exact',
        label='Ponto'
    )
    setor = django_filters.ChoiceFilter(
        field_name='setor',
        lookup_expr='exact',
        label='Setor'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters['codigo'].extra['choices'] = [(ponto.nome, ponto.nome) for ponto in PontosColeta.objects.all().distinct()]
        self.filters['setor'].extra['choices'] = [(setor.id, setor.nome) for setor in Setor.objects.all().distinct()]

    class Meta:
        model = PontosColeta
        fields = ['nome', 'setor']

class SetorFilter(django_filters.FilterSet):
    desc = django_filters.ChoiceFilter(
        field_name='desc',
        lookup_expr='exact',
        label='Setor'
    )
    local = django_filters.ChoiceFilter(
        field_name='local',
        lookup_expr='exact',
        label='Local'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters['desc'].extra['choices'] = [(setor.nome, setor.nome) for setor in Setor.objects.all().distinct()]
        self.filters['local'].extra['choices'] = [(local.id, local.nome) for local in Locais.objects.all().distinct()]

    class Meta:
        model = Setor
        fields = ['desc', 'local']

class LocalFilter(django_filters.FilterSet):
    codigo = django_filters.ChoiceFilter(
        field_name='nome',
        lookup_expr='exact',
        label='Local'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters['codigo'].extra['choices'] = [(local.nome, local.nome) for local in Locais.objects.all().distinct()]

    class Meta:
        model = Locais
        fields = ['codigo']