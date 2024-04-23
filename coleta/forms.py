from django import forms
from .models import Coleta_lagoa

class Coleta_agua(forms.ModelForm):
    class Meta:
        model = Coleta_lagoa
        fields = ['data_coleta', 'local_coleta', 'responsavel_coleta', 'pH',
                  'temperatura', 'turbidez', 'oxigenio_dissolvido',
                  'observacoes']
    
# Compare this snippet from coleta/views.py: