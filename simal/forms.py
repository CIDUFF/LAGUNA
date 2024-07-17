from crispy_forms.helper import FormHelper
from django.forms import TimeInput
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, HTML, Div
from django.utils import timezone
# from django.forms import ModelChoiceField
from django import forms
from django.utils.html import format_html
from django.urls import reverse
from .models import *


class ColetaCampo(forms.Form):

    codigo_coleta = forms.CharField(widget=forms.HiddenInput())
    ponto = forms.CharField(widget=forms.HiddenInput())
    hora_inicio = forms.TimeField(widget=forms.HiddenInput())
    hora_fim = forms.TimeField(widget=forms.HiddenInput())
    temperatura = forms.FloatField()
    ph = forms.FloatField()
    orp = forms.FloatField()
    condutividade = forms.FloatField()
    turbidez = forms.FloatField()
    od = forms.FloatField()
    od_pct = forms.FloatField()
    tds = forms.FloatField()
    salinidade = forms.FloatField()

    def __init__(self, *args, **kwargs):
        super(ColetaCampo, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                ' ',
                'codigo_coleta',
                'ponto',
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
                Submit('submit', 'Salvar e ir para o próximo ponto')
            )
        )


class ProgramaColetaForm(forms.Form):

    data_coleta_campo = forms.DateField(label='Data de coleta de campo',
                                        widget=forms.DateInput(attrs={'type': 'date'},
                                                               format='%Y/%m/%d'))
    data_fim_coleta_campo = forms.DateField(label='Data de fim de coleta',
                                            widget=forms.DateInput(attrs={'type': 'date'},
                                                                   format='%Y/%m/%d'))
    equipe_coleta = forms.ChoiceField(label='Equipe de coleta')
    # laboratorio = forms.ChoiceField()
    solicitante = forms.ChoiceField()
    local_coleta = forms.ChoiceField(label='Local de coleta')

    observacoes = forms.CharField(label='Observações',
                                  widget=forms.Textarea(attrs={'rows': 3, 'cols': 40}))

    def __init__(self, *args, **kwargs):
        super(ProgramaColetaForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Formulário de Programação de Coleta',
                'data_coleta_campo',
                'data_fim_coleta_campo',
                'equipe_coleta',
                # 'laboratorio',
                'solicitante',
                'local_coleta',
                # 'status_coleta',
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
        # self.fields['laboratorio'].choices = gerar_opcoes_unicas(
        #     Laboratorios, 'nome')


def custom_checkbox_widget():
    """
    Retorna um widget CheckboxInput com a classe CSS 'custom-checkbox' aplicada.
    """
    return forms.CheckboxInput(attrs={'class': 'custom-checkbox'})


class ChecklistCampoForm(forms.Form):
    # Campos básicos do formulário
    data_checklist = forms.DateField(
        widget=forms.HiddenInput(), initial=timezone.now().date)
    ordem_servico = forms.CharField(
        label="Ordem de serviço", widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    # status_checklist = forms.ChoiceField(choices=ChecklistCampo.STATUS)  # Esta linha foi removida
    observacoes = forms.CharField(
        label='Observações', widget=forms.Textarea, max_length=500, required=False)

    # Campos booleanos utilizando a função auxiliar para o widget
    previsao_tempo = forms.BooleanField(
        label="Previsão do tempo", required=False, widget=custom_checkbox_widget())
    avisar_labs = forms.BooleanField(
        label="Avisar laboratórios", required=False, widget=custom_checkbox_widget())
    reservar_carro = forms.BooleanField(
        label="Reservar carro", required=False, widget=custom_checkbox_widget())
    reservar_barco = forms.BooleanField(
        label="Reservar barco", required=False, widget=custom_checkbox_widget())
    separar_equipamentos = forms.BooleanField(
        label="Separar equipamentos", required=False, widget=custom_checkbox_widget())
    conferir_equipamentos = forms.BooleanField(
        label="Conferir equipamentos", required=False, widget=custom_checkbox_widget())
    comprar_gelo = forms.BooleanField(
        label="Comprar gelo", required=False, widget=custom_checkbox_widget())

    def __init__(self, *args, **kwargs):
        ordem_servico_selecionada = kwargs.pop(
            'ordem_servico_selecionada', None)
        super(ChecklistCampoForm, self).__init__(*args, **kwargs)
        if ordem_servico_selecionada:
            self.fields['ordem_servico'].initial = ordem_servico_selecionada
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Checklist de Campo',
                'data_checklist',
                'ordem_servico',
                'previsao_tempo',
                'avisar_labs',
                'reservar_carro',
                'reservar_barco',
                'separar_equipamentos',
                'conferir_equipamentos',
                'comprar_gelo',
                # 'status_checklist',  # Esta linha foi removida
                'observacoes',
                css_class='card form-checklist'
            ),
            ButtonHolder(
                Submit('submit', 'Salvar e continuar', css_class='btn-primary')
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

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Iniciar Campanha',
                'ordem_servico',
            ),
            ButtonHolder(
                Submit('submit', 'Prosseguir'),
            )
        )


class LaboratorioForm(forms.Form):
    nome = forms.CharField(label='Nome do laboratório')
    endereco = forms.CharField(label='Endereço')
    telefone = forms.CharField(label='Telefone')
    email = forms.EmailField(label='Email')
    tipo = forms.CharField(label='Tipo')

    def __init__(self, *args, **kwargs):
        super(LaboratorioForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Formulário de Cadastro de Laboratório',
                'nome',
                'endereco',
                'telefone',
                'email',
                'tipo'
            ),
            ButtonHolder(
                Layout(
                    Div(
                        Submit('submit', 'Salvar'),
                        css_class='col-6'
                    ),
                    Div(
                        HTML(format_html('<a href="{}" class="btn btn-primary btn-campanha">Laboratórios Cadastrados</a>',
                             reverse('laboratorios_cadastrados'))),
                        css_class='col-6 text-right'
                    )
                ),
                css_class='row'
            )
        )
