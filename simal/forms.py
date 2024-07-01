from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit
from django.forms import ModelChoiceField
from django import forms
from .models import *


class ColetaCampo(forms.Form):
    """
    Representa um formulário para coletar dados de campo.

    Atributos:
        clima (CharField): Campo para capturar informações sobre o clima.
        matriz (CharField): Campo para capturar informações sobre a matriz.
        hora_inicio (TimeField): Campo para capturar a hora de início.
        hora_fim (TimeField): Campo para capturar a hora de término.
        temperatura (DecimalField): Campo para capturar a temperatura.
        ph (DecimalField): Campo para capturar o valor de pH.
        orp (DecimalField): Campo para capturar o potencial de oxidação-redução.
        condutividade (DecimalField): Campo para capturar a condutividade.
        turbidez (DecimalField): Campo para capturar a turbidez.
        od (DecimalField): Campo para capturar a demanda de oxigênio.
        od_pct (DecimalField): Campo para capturar a porcentagem de demanda de oxigênio.
        tds (DecimalField): Campo para capturar os sólidos dissolvidos totais.
        salinidade (DecimalField): Campo para capturar a salinidade.

    Métodos:
        __init__: Inicializa o formulário e define o layout.
    """

    clima = forms.CharField()
    matriz = forms.CharField()
    hora_inicio = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time'}))
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

    def __init__(self, *args, **kwargs):
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
    """
    Classe que define o formulário de programação de coleta.

    Este formulário é usado para capturar informações sobre a programação de coleta de amostras.
    Ele contém campos para a data de coleta, equipe de coleta, laboratório, solicitante, local de coleta,
    status da coleta e observações.

    Atributos:
        data_coleta_campo (DateField): Campo para inserir a data de coleta.
        equipe_coleta (ChoiceField): Campo para selecionar a equipe de coleta.
        laboratorio (ChoiceField): Campo para selecionar o laboratório.
        solicitante (ChoiceField): Campo para selecionar o solicitante.
        local_coleta (ChoiceField): Campo para selecionar o local de coleta.
        status_coleta (ChoiceField): Campo para selecionar o status da coleta.
        observacoes (CharField): Campo para inserir observações sobre a coleta.

    Métodos:
        __init__: Inicializa o formulário e define o layout.
    """

    data_coleta_campo = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}))

    equipe_coleta = forms.ChoiceField()

    laboratorio = forms.ChoiceField()

    solicitante = forms.ChoiceField()

    local_coleta = forms.ChoiceField()

    STATUS = [
        ('programada', 'Programada'),
        ('reprogramada', 'Reprogramada'),
        ('realizada', 'Realizada'),
        ('cancelada', 'Cancelada'),
    ]

    status_coleta = forms.ChoiceField(choices=STATUS)

    observacoes = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'cols': 40}))

    data_fim_coleta_campo = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}))

    def __init__(self, *args, **kwargs):
        super(ProgramaColetaForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Formulário de Programação de Coleta',
                'data_coleta_campo',
                'data_fim_coleta_campo',
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

        def gerar_opcoes_unicas(modelo, campo):
            valores_unicos = modelo.objects.values_list(
                campo, flat=True).distinct()
            return [(valor, valor) for valor in valores_unicos]

        # Agora você pode usar essa função para gerar as opções únicas para cada campo
        self.fields['local_coleta'].choices = gerar_opcoes_unicas(
            LocaisColeta, 'local')
        self.fields['equipe_coleta'].choices = gerar_opcoes_unicas(
            Coletores, 'equipe')
        self.fields['solicitante'].choices = gerar_opcoes_unicas(
            Solicitantes, 'nome')
        self.fields['laboratorio'].choices = gerar_opcoes_unicas(
            Laboratorios, 'nome')


class ChecklistCampoForm(forms.Form):
    # Mantém os campos existentes
    data_checklist = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'})) 
    ordem_servico = forms.CharField(
        widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    status_checklist = forms.ChoiceField(choices=ChecklistCampo.STATUS)
    observacoes = forms.CharField(
        widget=forms.Textarea, max_length=500, required=False)

    # Adiciona os novos campos booleanos
    previsao_tempo = forms.BooleanField(
        label="Previsão do tempo", required=False)
    avisar_labs = forms.BooleanField(
        label="Avisar laboratórios", required=False)
    reservar_carro = forms.BooleanField(label="Reservar carro", required=False)
    reservar_barco = forms.BooleanField(label="Reservar barco", required=False)
    separar_equipamentos = forms.BooleanField(
        label="Separar equipamentos", required=False)
    conferir_equipamentos = forms.BooleanField(
        label="Conferir equipamentos", required=False)
    comprar_gelo = forms.BooleanField(label="Comprar gelo", required=False)

    def __init__(self, *args, **kwargs):
        ordem_servico_selecionada = kwargs.pop(
            'ordem_servico_selecionada', None)
        super(ChecklistCampoForm, self).__init__(*args, **kwargs)
        if ordem_servico_selecionada:
            self.fields['ordem_servico'].initial = ordem_servico_selecionada
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Formulário de Checklist de Campo',
                'data_checklist',
                'ordem_servico',
                'status_checklist',
                'observacoes',
                'previsao_tempo',
                'avisar_labs',
                'reservar_carro',
                'reservar_barco',
                'separar_equipamentos',
                'conferir_equipamentos',
                'comprar_gelo'
            ),
            ButtonHolder(
                Submit('submit', 'Salvar')
            )
        )

class AjudaForm(forms.Form):
    nome = forms.CharField()
    email = forms.EmailField()
    pergunta = forms.CharField(
        widget=forms.Textarea, max_length=500, required=False)

    def __init__(self, *args, **kwargs):
        super(AjudaForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Formulário de Ajuda',
                'nome',
                'email',
                'pergunta'
            ),
            ButtonHolder(
                Submit('submit', 'Enviar')
            )
        )


class IniciarCampanhaForm(forms.Form):
    ordem_servico = forms.ModelChoiceField(queryset=ProgramaColeta.objects.all(
    ), label="Selecione a campanha que deseja iniciar")

    def __init__(self, *args, **kwargs):
        super(IniciarCampanhaForm, self).__init__(*args, **kwargs)
        self.fields['ordem_servico'].empty_label = "Selecione uma campanha"
