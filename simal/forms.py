from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit
from django import forms
from .models import *

class ColetaCampo(forms.Form):
    clima = forms.CharField()
    matriz = forms.CharField()
    hora_inicio = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}))
    hora_fim = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}))
    temperatura = forms.DecimalField()
    ph = forms.DecimalField()
    orp = forms.DecimalField()
    condutividade = forms.DecimalField()
    turbidez = forms.DecimalField()
    od = forms.DecimalField()
    od_pct = forms.DecimalField()
    tds = forms.DecimalField()
    salinidade = forms.DecimalField()

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

class ProgramaColetaForm(forms.Form):
    
    data_coleta_campo = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    
    equipe_coleta = forms.ChoiceField()
    
    TIPO_CHOICES = [
    ('interno', 'Interno'),
    ('externo', 'Externo'),
    ]
        
    laboratorio = forms.ChoiceField(choices=TIPO_CHOICES)
    
    solicitante = forms.ChoiceField()
    
    local_coleta = forms.ChoiceField()
    
    STATUS = [
        ('programada', 'Programada'),
        ('reprogramada', 'Reprogramada'), 
        ('realizada', 'Realizada'),
        ('cancelada', 'Cancelada'),
        ]
    
    status_coleta = forms.ChoiceField(choices=STATUS)
    
    observacoes = forms.CharField(widget=forms.Textarea(attrs={'rows': 3, 'cols': 40}))

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
        self.fields['local_coleta'].choices = [(local, local) for local in locais_unicos]

        # Faz o mesmo para equipe_coleta, laboratorio, solicitante e status_coleta
        equipes_unicas = Coletores.objects.values_list('equipe', flat=True).distinct()
        self.fields['equipe_coleta'].choices = [(equipe, equipe) for equipe in equipes_unicas]

        solicitantes_unicos = Solicitantes.objects.values_list('nome', flat=True).distinct()
        self.fields['solicitante'].choices = [(solicitante, solicitante) for solicitante in solicitantes_unicos]

