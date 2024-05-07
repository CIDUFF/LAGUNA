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
                'Formulário de campo - coleta de dados',
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

class ProgramaColetaForm(forms.ModelForm):
        
    def __init__(self,*args,**kwargs):

        super(ProgramaColetaForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Formulário de Programação de Coleta',
                'data_coleta_campo',
                'equipe_coleta',
                'laboratorio',
                'solicitante',
                'local_coleta',
                'status_coleta',
                'observacoes'
            ),
            ButtonHolder(
                Submit('submit', 'Salvar')
            )
        )

        # Cria uma lista de opções únicas para o campo local_coleta
        locais_unicos = LocaisColeta.objects.values_list('local', flat=True).distinct()
        opcoes_unicas = [(local, local) for local in locais_unicos]
        self.fields['local_coleta'].choices = opcoes_unicas

    class Meta:

        model = ProgramaColeta
        fields = [
            'data_coleta_campo',
            'equipe_coleta',
            'laboratorio',
            'solicitante',
            'local_coleta',
            'status_coleta',
            'observacoes'
        ]
        widgets = {
        'data_coleta_campo': forms.DateInput(attrs={'type': 'date'}),
    }