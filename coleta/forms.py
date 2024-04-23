from django import forms
from .models import Coleta_lagoa

class Coleta_agua(forms.ModelForm):
    class Meta:
        model = Coleta_lagoa
        fields =['pH', 'temperatura', 'turbidez', 'oxigenio_dissolvido', 'data_coleta',
                 'local_coleta', 'responsavel_coleta', 'observacoes',] 
    
# Compare this snippet from coleta/views.py: