from crispy_forms.helper import FormHelper
from crispy_bootstrap5.bootstrap5 import FloatingField, Switch
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, HTML, Div
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import UserCreationForm
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
    temperatura = forms.FloatField(
        required=False, label='Temperatura (°C)', widget=forms.NumberInput(attrs={'step': '0.1'})
    )
    ph = forms.FloatField(
        required=False, label='pH', widget=forms.NumberInput(attrs={'step': '0.1'})
    )
    orp = forms.FloatField(
        required=False, label='ORP (mV)', widget=forms.NumberInput(attrs={'step': '0.1'})
    )
    condutividade = forms.FloatField(
        required=False, label='Condutividade (µS/cm)', widget=forms.NumberInput(attrs={'step': '0.1'})
    )
    turbidez = forms.FloatField(
        required=False, label='Turbidez (NTU)', widget=forms.NumberInput(attrs={'step': '0.1'})
    )
    od = forms.FloatField(
        required=False, label='OD (mg/L)', widget=forms.NumberInput(attrs={'step': '0.1'})
    )
    od_pct = forms.FloatField(
        required=False, label='OD (%)', widget=forms.NumberInput(attrs={'step': '0.1'})
    )
    tds = forms.FloatField(
        required=False, label='TDS (mg/L)', widget=forms.NumberInput(attrs={'step': '0.1'})
    )
    salinidade = forms.FloatField(
        required=False, label='Salinidade (ppt)', widget=forms.NumberInput(attrs={'step': '0.1'})
        
    )
    observacoes = forms.CharField(
        label='Observações',
        widget=forms.Textarea(attrs={'rows': 3, 'cols': 40}),
        required=False
    )
    foto = forms.ImageField(
        label='Foto',
        required=False,
        widget=forms.ClearableFileInput(attrs={'capture': 'camera'})
    )

    # campos = [
    #     'temperatura', 'ph', 'orp', 'condutividade', 'turbidez', 'od', 'od_pct', 'tds', 'salinidade', 'observacoes'
    # ]


    def __init__(self, *args, **kwargs):
        super(ColetaCampo, self).__init__(*args, **kwargs)
        campos = [
            'temperatura', 'ph', 'orp', 'condutividade', 'turbidez', 'od', 'od_pct', 'tds', 'salinidade', 'observacoes'
        ]
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                ' ',
                'codigo_coleta',
                'ponto',
                'hora_inicio',
                'hora_fim',
                *[FloatingField(campo) for campo in campos],
                'foto'  # Adiciona o campo foto diretamente no Fieldset
            ),
            ButtonHolder(
                Submit('submit', 'Salvar e ir para o próximo')
            )
        )


class ProgramaColetaForm(forms.Form):

    data_coleta_campo = forms.DateField(label='Data de coleta de campo',
                                        widget=forms.DateInput(attrs={'type': 'date'},
                                                               format='%Y/%m/%d'))
    equipe_coleta = forms.ChoiceField(label='Equipe de coleta')
    solicitante = forms.ChoiceField(label='Solicitante')
    local_coleta = forms.ChoiceField(label='Local de coleta')
    observacoes = forms.CharField(label='Observações',
                                  widget=forms.Textarea(attrs={'rows': 3, 'cols': 40}))

    def __init__(self, *args, **kwargs):
        super(ProgramaColetaForm, self).__init__(*args, **kwargs)
        campo = [
            'data_coleta_campo',
            'equipe_coleta', 'solicitante', 'local_coleta', 'observacoes'
        ]
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                ' ',
                *[FloatingField(campo) for campo in campo]
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
            UsuarioSistema, 'equipe')
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
        checklist_campo_instance = kwargs.pop('instance', None)
        super(ChecklistCampoForm, self).__init__(*args, **kwargs)
        if ordem_servico_selecionada:
            self.fields['ordem_servico'].initial = ordem_servico_selecionada
        if checklist_campo_instance:
            self.fields['previsao_tempo'].initial = checklist_campo_instance.previsao_tempo
            self.fields['avisar_labs'].initial = checklist_campo_instance.avisar_labs
            self.fields['reservar_carro'].initial = checklist_campo_instance.reservar_carro
            self.fields['reservar_barco'].initial = checklist_campo_instance.reservar_barco
            self.fields['separar_equipamentos'].initial = checklist_campo_instance.separar_equipamentos
            self.fields['conferir_equipamentos'].initial = checklist_campo_instance.conferir_equipamentos
            self.fields['comprar_gelo'].initial = checklist_campo_instance.comprar_gelo
            self.fields['observacoes'].initial = checklist_campo_instance.observacoes
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Checklist de Campo',
                'data_checklist',
                'ordem_servico',
                Switch('previsao_tempo'),
                Switch('avisar_labs'),
                Switch('reservar_carro'),
                Switch('reservar_barco'),
                Switch('separar_equipamentos'),
                Switch('conferir_equipamentos'),
                Switch('comprar_gelo'),
                'observacoes',
            ),
                        ButtonHolder(
                            Layout(
                                Div(
                                    Submit('submit', 'Salvar e ir para o formulário de coleta'),
                                    css_class='col-6'
                                ),
                                Div(
                                    HTML(format_html('<a href="{}" class="btn btn-primary btn-campanha">Voltar</a>',
                                         reverse('coletas_agendas'))),
                                    css_class='col-6 text-right'
                                )
                            ),
                            css_class='row'
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


# class LaboratorioForm(forms.Form):
#     nome = forms.CharField(label='Nome do laboratório')
#     endereco = forms.CharField(label='Endereço')
#     telefone = forms.CharField(label='Telefone')
#     email = forms.EmailField(label='Email')
#     tipo = forms.CharField(label='Tipo')

#     def __init__(self, *args, **kwargs):
#         super(LaboratorioForm, self).__init__(*args, **kwargs)
#         self.helper = FormHelper()
#         self.helper.layout = Layout(
#             Fieldset(
#                 'Formulário de Cadastro de Laboratório',
#                 'nome',
#                 'endereco',
#                 'telefone',
#                 'email',
#                 'tipo'
#             ),
#             ButtonHolder(
#                 Layout(
#                     Div(
#                         Submit('submit', 'Salvar'),
#                         css_class='col-6'
#                     ),
#                     Div(
#                         HTML(format_html('<a href="{}" class="btn btn-primary btn-campanha">Laboratórios Cadastrados</a>',
#                              reverse('laboratorios_cadastrados'))),
#                         css_class='col-6 text-right'
#                     )
#                 ),
#                 css_class='row'
#             )
#         )


# class AnaliseForm(forms.ModelForm):
#     class Meta:
#         model = Analises
#         fields = ['analise']

class LaboratorioForm(forms.ModelForm):
    class Meta:
        model = Laboratorios
        fields = '__all__'
        labels = {
            'nome': 'Nome do laboratório',
            'endereco': 'Endereço',
            'telefone': 'Telefone',
            'email': 'Email',
            'tipo': 'Tipo'
        }

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
                Submit('submit', 'Salvar'),
            )
        )
        
class AnaliseForm(forms.ModelForm):
    class Meta:
        model = Analises
        fields = '__all__'
        labels = {
            'analise': 'Análise'
        }
        
    def __init__(self, *args, **kwargs):
        super(AnaliseForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Formulário de Cadastro de Análise',
                'analise'
            ),
            ButtonHolder(
                        Submit('submit', 'Salvar'),
            )
        )
        
        
class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Equipe"
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'groups')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            user.groups.set(self.cleaned_data['groups'])
        return user

                
        
