from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit
from django import forms
from .models import *

class ColetaCampo(forms.ModelForm):
    
    def __init__(self,*args,**kwargs):

        super(ColetaCampo, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Dados da Coleta',
                'clima',
                'matriz',
                'hora_inicio',
                'hora_fim',
                'temperatura',
                'ph',
                'orp',
                'condutividade',
                'turbidez',
                'od',
                'od_pct',
                'tds',
                'salinidade'
            ),
            ButtonHolder(
                Submit('submit', 'Salvar')
            )
        )

    class Meta:

        model = Campo
        fields = [
            'clima',
            'matriz',
            'hora_inicio',
            'hora_fim',
            'temperatura',
            'ph',
            'orp',
            'condutividade',
            'turbidez',
            'od',
            'od_pct',
            'tds',
            'salinidade'
        ]
        widgets = {
            'hora_inicio': forms.TimeInput(attrs={'type': 'time'}),
            'hora_fim': forms.TimeInput(attrs={'type': 'time'}),
        }