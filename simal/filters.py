from django import forms
import django_filters
from .models import *
from .forms import *


class CampoFilter(django_filters.FilterSet):
    class Meta:
        model = Campo
        fields = {
            'codigo_coleta': ['icontains'],
            'clima': ['exact'],
            # Adicione mais campos conforme necessário
        }


class ProgramaColetaFilter(django_filters.FilterSet):
    class Meta:
        model = ProgramaColeta
        fields = {
            'local_coleta': ['icontains'],
           'data_coleta_campo': ['exact'],
            'equipe_coleta': ['exact'],
           'status_coleta': ['exact'],
         # Adicione mais campos conforme necessário
        }