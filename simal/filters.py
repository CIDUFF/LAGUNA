import django_filters
from .models import *


class CampoFilter(django_filters.FilterSet):
    class Meta:
        model = Campo
        fields = {
            'ponto': ['exact'],

            # Adicione mais campos conforme necessário
        }

class ProgramaColetaFilter(django_filters.FilterSet):
    class Meta:
        model = ProgramaColeta
        fields = {
            'local_coleta': ['icontains'],
            'data_coleta_campo': ['exact'],
            'status_coleta': ['exact'],
            'equipe_coleta': ['exact'],
            # Adicione mais campos conforme necessário
        }



