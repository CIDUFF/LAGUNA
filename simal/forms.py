from crispy_forms.helper import FormHelper
from crispy_bootstrap5.bootstrap5 import FloatingField, Switch
from crispy_forms.layout import (
    Layout,
    Fieldset,
    Row,
    Column,
    ButtonHolder,
    Div,
    Submit,
    HTML,
    Field,
)
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone

# from django.forms import ModelChoiceField
from django import forms
from django.utils.html import format_html
from django.urls import reverse
from .models import (
    MetadadosCampo,
    ProgramaColeta,
    TabAnexoAmostra,
    TabSetor,
    Laboratorios,
    Analises,
    TabLocal,
    TabPonto,
    TabParam,
    UnidadesMedida,
    TipoParametro,
    TabFrasco,
    TabEquipe,
    TabLaboratorio,
    TabProduto,
    TabProdxparam,
    TabSerieClassificacao,
    TabCampanha,
    TabColeta,
    TabItemChecklistColeta,
    TabChecklistColeta,
    TabMedida,
    DetalhesUsuario,
    MetadadosPonto,
    EmailTemplate,
)


class ColetaCampo(forms.Form):
    codigo_coleta = forms.CharField(widget=forms.HiddenInput())
    ponto = forms.CharField(widget=forms.HiddenInput())
    hora_inicio = forms.TimeField(
        required=False, widget=forms.TimeInput(attrs={"type": "time"})
    )
    hora_fim = forms.TimeField(widget=forms.HiddenInput())
    temperatura = forms.FloatField(
        required=False,
        label="Temperatura (°C)",
        widget=forms.NumberInput(attrs={"step": "0.001"}),
    )
    ph = forms.FloatField(
        required=False, label="pH", widget=forms.NumberInput(attrs={"step": "0.001"})
    )
    orp = forms.FloatField(
        required=False,
        label="ORP (mV)",
        widget=forms.NumberInput(attrs={"step": "0.001"}),
    )
    condutividade = forms.FloatField(
        required=False,
        label="Condutividade (µS/cm)",
        widget=forms.NumberInput(attrs={"step": "0.001"}),
    )
    turbidez = forms.FloatField(
        required=False,
        label="Turbidez (NTU)",
        widget=forms.NumberInput(attrs={"step": "0.001"}),
    )
    od = forms.FloatField(
        required=False,
        label="OD (mg/L)",
        widget=forms.NumberInput(attrs={"step": "0.001"}),
    )
    od_pct = forms.FloatField(
        required=False,
        label="OD (%)",
        widget=forms.NumberInput(attrs={"step": "0.001"}),
    )
    tds = forms.FloatField(
        required=False,
        label="TDS (mg/L)",
        widget=forms.NumberInput(attrs={"step": "0.001"}),
    )
    salinidade = forms.FloatField(
        required=False,
        label="Salinidade (ppt)",
        widget=forms.NumberInput(attrs={"step": "0.001"}),
    )
    observacoes = forms.CharField(
        label="Observações",
        widget=forms.Textarea(attrs={"rows": 3, "cols": 40}),
        required=False,
    )
    check_amostras = forms.BooleanField(
        label="As amostras de laboratório foram coletadas?",
        required=False,
        widget=forms.CheckboxInput(attrs={"id": "check_amostras"}),
    )
    data_coleta = forms.DateField(
        label="Data de coleta de campo",
        widget=forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
        # initial=timezone.now().date,
        required=False,
    )
    foto = forms.ImageField(
        label="Foto",
        required=False,
        widget=forms.ClearableFileInput(attrs={"capture": "camera"}),
    )

    def __init__(self, *args, **kwargs):
        super(ColetaCampo, self).__init__(*args, **kwargs)

        campos = [
            "temperatura",
            "ph",
            "orp",
            "condutividade",
            "turbidez",
            "od",
            "od_pct",
            "tds",
            "salinidade",
        ]
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                " ",
                *[
                    Row(
                        Column(FloatingField("data_coleta", css_class="col-md-6")),
                        Column(FloatingField("hora_inicio", css_class="col-md-6")),
                    )
                ],
                "codigo_coleta",
                "ponto",
                "hora_fim",
                *[
                    Row(
                        Column(FloatingField(campos[i]), css_class="col-md-6"),
                        Column(FloatingField(campos[i + 1]), css_class="col-md-6")
                        if i + 1 < len(campos)
                        else None,
                    )
                    for i in range(0, len(campos), 2)
                ],
                Switch("check_amostras"),
                "observacoes",  # Adiciona o campo observacoes diretamente no Fieldset
                "foto",  # Adiciona o campo foto diretamente no Fieldset
            ),
            ButtonHolder(Submit("submit", "Salvar e ir para o próximo")),
        )


class MetadadosCampoForm(forms.ModelForm):
    class Meta:
        model = MetadadosCampo
        exclude = ["codigo_coleta"]  # Exclui o campo codigo_coleta
        labels = {
            "acesso_ponto": "Acesso ao Ponto",
            "dragagem": "Dragagem",
            "gigoga": "Quantidade de Gigoga",
            "odor": "Odor",
            "fezes": "Fezes",
            "oleo": "Óleo",
            "residuos_solidos": "Resíduos Sólidos",
            "lodo": "Lodo",
            "animais_presentes": "Animais Presentes",
            "pescadores": "Pescadores",
            "contato_populacao": "Contato com a População",
        }
        widgets = {
            "acesso_ponto": forms.Select(attrs={"class": "form-select"}),
            "dragagem": forms.NumberInput(
                attrs={
                    "type": "range",
                    "min": -1,
                    "max": 1,
                    "step": 1,
                    "class": "form-range",
                }
            ),
            "gigoga": forms.NumberInput(
                attrs={
                    "type": "range",
                    "min": -1,
                    "max": 1,
                    "step": 1,
                    "class": "form-range",
                }
            ),
            "odor": forms.NumberInput(
                attrs={
                    "type": "range",
                    "min": -1,
                    "max": 1,
                    "step": 1,
                    "class": "form-range",
                }
            ),
            "fezes": forms.NumberInput(
                attrs={
                    "type": "range",
                    "min": -1,
                    "max": 1,
                    "step": 1,
                    "class": "form-range",
                }
            ),
            "oleo": forms.NumberInput(
                attrs={
                    "type": "range",
                    "min": -1,
                    "max": 1,
                    "step": 1,
                    "class": "form-range",
                }
            ),
            "residuos_solidos": forms.NumberInput(
                attrs={
                    "type": "range",
                    "min": -1,
                    "max": 1,
                    "step": 1,
                    "class": "form-range",
                }
            ),
            "lodo": forms.NumberInput(
                attrs={
                    "type": "range",
                    "min": -1,
                    "max": 1,
                    "step": 1,
                    "class": "form-range",
                }
            ),
            "animais_presentes": forms.NumberInput(
                attrs={
                    "type": "range",
                    "min": -1,
                    "max": 1,
                    "step": 1,
                    "class": "form-range",
                }
            ),
            "pescadores": forms.NumberInput(
                attrs={
                    "type": "range",
                    "min": -1,
                    "max": 1,
                    "step": 1,
                    "class": "form-range",
                }
            ),
            "contato_populacao": forms.NumberInput(
                attrs={
                    "type": "range",
                    "min": -1,
                    "max": 1,
                    "step": 1,
                    "class": "form-range",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super(MetadadosCampoForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                "",
                Div(Div("acesso_ponto", css_class="col-md-6"), css_class="row"),
                HTML(
                    '<p class="text-center"><strong>Pouco</strong> | <strong>Neutro</strong> | <strong>Muito</strong></p>'
                ),
                Div(
                    Div("dragagem", css_class="col-md-6"),
                    Div("gigoga", css_class="col-md-6"),
                    Div("odor", css_class="col-md-6"),
                    Div("fezes", css_class="col-md-6"),
                    Div("oleo", css_class="col-md-6"),
                    Div("residuos_solidos", css_class="col-md-6"),
                    Div("lodo", css_class="col-md-6"),
                    Div("animais_presentes", css_class="col-md-6"),
                    Div("pescadores", css_class="col-md-6"),
                    Div("contato_populacao", css_class="col-md-6"),
                    css_class="row",
                ),
            ),
            ButtonHolder(
                Div(
                    Submit(
                        "submit",
                        "Salvar e voltar para o formulário de coleta",
                        css_class="btn btn-primary",
                    ),
                    css_class="d-flex justify-content-center flex-column",
                )
            ),
        )


class ProgramaColetaForm(forms.Form):
    data_coleta_campo = forms.DateField(
        label="Data de coleta de campo",
        widget=forms.DateInput(attrs={"type": "date"}, format="%Y/%m/%d"),
    )
    equipe_coleta = forms.ChoiceField(label="Equipe de coleta")
    # solicitante = forms.ChoiceField(label='Solicitante')
    local_coleta = forms.ChoiceField(label="Local de coleta")
    prazo_previsao = forms.FloatField(
        required=False,
        label="Prazo para verificar a previsão do tempo em dias",
        widget=forms.NumberInput(attrs={"step": "1"}),
        initial=10,
    )
    prazo_lab = forms.FloatField(
        required=False,
        label="Prazo para avisar ao laboratório em dias",
        widget=forms.NumberInput(attrs={"step": "1"}),
        initial=7,
    )
    prazo_car = forms.FloatField(
        required=False,
        label="Prazo para reservar carro em dias",
        widget=forms.NumberInput(attrs={"step": "1"}),
        initial=5,
    )
    prazo_material = forms.FloatField(
        required=False,
        label="Prazo para preparar o material em dias",
        widget=forms.NumberInput(attrs={"step": "1"}),
        initial=3,
    )
    observacoes = forms.CharField(
        label="Observações", widget=forms.Textarea(attrs={"rows": 3, "cols": 40})
    )
    bentos = forms.BooleanField(
        label="Esta campanha possui análise de macrofauna bentônica?", required=False
    )

    def __init__(self, *args, **kwargs):
        super(ProgramaColetaForm, self).__init__(*args, **kwargs)
        campo = [
            "data_coleta_campo",
            "equipe_coleta",
            "local_coleta",
            "prazo_previsao",
            "prazo_lab",
            "prazo_car",
            "prazo_material",
            "observacoes",
        ]
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                " ",
                *[FloatingField(campo) for campo in campo],
                Switch("bentos"),
            ),
            ButtonHolder(Submit("submit", "Salvar")),
        )

        def gerar_opcoes_unicas(modelo, campo):
            valores_unicos = modelo.objects.values_list(campo, flat=True).distinct()
            return [(valor, valor) for valor in valores_unicos]

        self.fields["local_coleta"].choices = gerar_opcoes_unicas(TabSetor, "nome")
        self.fields["equipe_coleta"].choices = [
            (group.id, group.name) for group in Group.objects.all()
        ]


def custom_checkbox_widget(attrs=None):
    """
    Retorna um widget CheckboxInput com a classe CSS 'custom-checkbox' aplicada.
    """
    final_attrs = {"class": "custom-checkbox"}
    if attrs:
        final_attrs.update(attrs)
    return forms.CheckboxInput(attrs=final_attrs)


# Função auxiliar para criar campos booleanos e suas observações
def create_boolean_field(name, label):
    return forms.BooleanField(
        label=label,
        required=False,
        widget=custom_checkbox_widget(attrs={"id": f"{name}_switch"}),
    )


def create_date_field(name, label):
    return forms.DateField(
        label=label,
        required=False,
        widget=forms.DateInput(attrs={"type": "date", "id": f"data_{name}"}),
    )


def create_observation_field(name):
    return forms.CharField(
        label="Observação",
        required=False,
        widget=forms.TextInput(attrs={"id": f"observacao_{name}"}),
    )


class ChecklistCampoForm(forms.Form):
    # Campos básicos do formulário
    data_checklist = forms.DateField(
        widget=forms.HiddenInput(), initial=timezone.now().date
    )
    ordem_servico = forms.CharField(
        label="Ordem de serviço", widget=forms.TextInput(attrs={"readonly": "readonly"})
    )
    observacoes = forms.CharField(
        label="Observações", widget=forms.Textarea, max_length=500, required=False
    )

    # Campos booleanos e suas observações
    boolean_fields = [
        ("previsao_tempo", "Previsão do tempo"),
        ("avisar_labs", "Avisar laboratórios"),
        ("reservar_carro", "Reservar carro"),
        ("reservar_barco", "Reservar barco"),
        ("separar_equipamentos", "Separar equipamentos"),
        ("conferir_equipamentos", "Conferir equipamentos"),
        ("comprar_gelo", "Comprar gelo"),
        ("etiquetar_frascos", "Etiquetar frascos"),
    ]

    def __init__(self, *args, **kwargs):
        ordem_servico_selecionada = kwargs.pop("ordem_servico_selecionada", None)
        checklist_campo_instance = kwargs.pop("instance", None)
        super(ChecklistCampoForm, self).__init__(*args, **kwargs)

        for name, label in self.boolean_fields:
            self.fields[name] = create_boolean_field(name, label)
            self.fields[f"data_{name}"] = create_date_field(
                name, f"Data da {label.lower()}"
            )
            self.fields[f"observacao_{name}"] = create_observation_field(name)

            if checklist_campo_instance:
                self.fields[name].initial = getattr(checklist_campo_instance, name)
                self.fields[f"data_{name}"].initial = getattr(
                    checklist_campo_instance, f"data_{name}"
                )
                self.fields[f"observacao_{name}"].initial = getattr(
                    checklist_campo_instance, f"observacao_{name}"
                )

        if ordem_servico_selecionada:
            self.fields["ordem_servico"].initial = ordem_servico_selecionada

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                "Checklist de Campo",
                "data_checklist",
                "ordem_servico",
                *[
                    Row(
                        Column(Switch(name), css_class="col-md-4"),
                        Column(
                            Div(f"data_{name}", css_class="form-group"),
                            css_class="col-md-4",
                        ),
                        Column(
                            Div(f"observacao_{name}", css_class="form-group"),
                            css_class="col-md-4",
                        ),
                    )
                    for name, _ in self.boolean_fields
                ],
            ),
            ButtonHolder(
                Div(
                    Div(
                        Submit("submit", "Salvar e ir para o formulário de coleta"),
                        HTML(
                            format_html(
                                '<a href="{}" class="btn btn-primary btn-campanha">Voltar</a>',
                                reverse("coletas_agendas"),
                            )
                        ),
                        css_class="d-flex justify-content-between",
                    ),
                    css_class="text-left",
                )
            ),
        )


class AjudaForm(forms.Form):
    nome = forms.CharField()
    email = forms.EmailField()
    pergunta = forms.CharField(widget=forms.Textarea, max_length=500, required=False)

    def __init__(self, *args, **kwargs):
        super(AjudaForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset("Formulário de Ajuda", "nome", "email", "pergunta"),
            ButtonHolder(Submit("submit", "Enviar")),
        )


class IniciarCampanhaForm(forms.ModelForm):
    ordem_servico = forms.ModelChoiceField(
        queryset=ProgramaColeta.objects.filter(status_coleta="Programada"),
        label="Selecione a campanha que deseja iniciar",
    )

    class Meta:
        model = ProgramaColeta
        fields = ["ordem_servico"]

    def __init__(self, *args, **kwargs):
        super(IniciarCampanhaForm, self).__init__(*args, **kwargs)
        self.fields["ordem_servico"].empty_label = "Selecione uma campanha"

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                "Iniciar Campanha",
                "ordem_servico",
            ),
            ButtonHolder(
                Submit("submit", "Prosseguir"),
            ),
        )


class LaboratorioForm(forms.ModelForm):
    class Meta:
        model = Laboratorios
        fields = "__all__"
        labels = {
            "nome": "Nome do laboratório",
            "endereco": "Endereço",
            "telefone": "Telefone",
            "email": "Email",
            "tipo": "Tipo",
        }

    def __init__(self, *args, **kwargs):
        super(LaboratorioForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                "Formulário de Cadastro de Laboratório",
                "nome",
                "endereco",
                "telefone",
                "email",
                "tipo",
            ),
            ButtonHolder(
                Submit("submit", "Salvar"),
            ),
        )


class AnaliseForm(forms.ModelForm):
    class Meta:
        model = Analises
        fields = "__all__"
        labels = {"analise": "Análise"}

    def __init__(self, *args, **kwargs):
        super(AnaliseForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset("Formulário de Cadastro de Análise", "analise"),
            ButtonHolder(
                Submit("submit", "Salvar"),
            ),
        )


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Equipe",
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2", "groups")

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                "Um usuário com este endereço de e-mail já existe."
            )
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
            user.groups.set(self.cleaned_data["groups"])
        return user


class LocaisForm(forms.ModelForm):
    class Meta:
        model = TabLocal
        fields = ["nome"]
        labels = {
            "nome": "Nome do local",
        }

    def __init__(self, *args, **kwargs):
        super(LocaisForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                "Cadastro de Locais",
                Div(Div("nome", css_class="col-md-6"), css_class="row"),
            ),
            ButtonHolder(Submit("submit", "Salvar", css_class="btn btn-primary")),
        )


class SetorForm(forms.ModelForm):
    class Meta:
        model = TabSetor
        fields = ["nome", "id_local", "lat", "lon", "abreviatura"]
        labels = {
            "nome": "Nome",
            "id_local": "Local",
            "lat": "Latitude",
            "lon": "Longitude",
            "abreviatura": "Abreviatura",
        }

    def __init__(self, *args, **kwargs):
        super(SetorForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                "Cadastro de Setores",
                Div(
                    Div("nome", css_class="col-md-6"),
                    Div("id_local", css_class="col-md-6"),
                    Div("lat", css_class="col-md-6"),
                    Div("lon", css_class="col-md-6"),
                    Div("abreviatura", css_class="col-md-6"),
                    css_class="row",
                ),
            ),
            ButtonHolder(Submit("submit", "Salvar", css_class="btn btn-primary")),
        )


class PontoForm(forms.ModelForm):
    nome = forms.CharField(label="Código", max_length=100)
    modalidade = forms.CharField(label="Modalidade", max_length=100)

    class Meta:
        model = TabPonto
        fields = [
            "id_setor",
            "id_local",
            "nome",
            "modalidade",
            "lat",
            "lon",
            "observacao",
            "status",
        ]
        labels = {
            "nome": "Código",
            "id_setor": "Setor",
            "id_local": "Local",
            "modalidade": "Modalidade",
            "lat": "Latitude",
            "lon": "Longitude",
            "observacao": "Observação",
            "status": "Ponto ativo?",
        }

    def __init__(self, *args, **kwargs):
        super(PontoForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                "Cadastro de Pontos de Coleta",
                Div(
                    Div("nome", css_class="col-md-6"),
                    Div("id_setor", css_class="col-md-6"),
                    Div("id_local", css_class="col-md-6"),
                    Div("modalidade", css_class="col-md-6"),
                    Div("lat", css_class="col-md-6"),
                    Div("lon", css_class="col-md-6"),
                    Div("observacao", css_class="col-md-6"),
                    Div("status", css_class="col-md-6"),
                    css_class="row",
                ),
            ),
            ButtonHolder(Submit("submit", "Salvar", css_class="btn btn-primary")),
        )


class ParametroForm(forms.ModelForm):
    class Meta:
        model = TabParam
        fields = "__all__"


class UnidadeMedidaForm(forms.ModelForm):
    class Meta:
        model = UnidadesMedida
        fields = "__all__"


class TipoParametroForm(forms.ModelForm):
    class Meta:
        model = TipoParametro
        fields = "__all__"


class TabFrascoForm(forms.ModelForm):
    class Meta:
        model = TabFrasco
        fields = "__all__"


class TabEquipeForm(forms.ModelForm):
    class Meta:
        model = TabEquipe
        fields = "__all__"


class TabLaboratorioForm(forms.ModelForm):
    class Meta:
        model = TabLaboratorio
        fields = "__all__"


class TabProdutoForm(forms.ModelForm):
    class Meta:
        model = TabProduto
        fields = "__all__"


class TabProdxParamForm(forms.ModelForm):
    class Meta:
        model = TabProdxparam
        fields = "__all__"


class TabSerieClassificacaoForm(forms.ModelForm):
    class Meta:
        model = TabSerieClassificacao
        fields = "__all__"


class CadastroCampanhaForm(forms.ModelForm):
    # data_criacao = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))

    class Meta:
        model = TabCampanha
        exclude = ["id", "data_criacao"]
        labels = {
            "id_local": "Local",
        }

    def __init__(self, *args, **kwargs):
        super(CadastroCampanhaForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit("submit", "Salvar"))


# TODO: #176 Refatorar o código para que a campanha já venha preenchida automaticamente


class CadastroColetaForm(forms.ModelForm):
    data = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"}),
        required=False,
        label="Data programada",
    )

    class Meta:
        model = TabColeta
        exclude = ["id", "ordem_servico", "criado_por", "atualizado_por", "status"]
        labels = {
            "id_campanha": "Campanha",
            "id_setor": "Setor",
        }

    def __init__(self, *args, **kwargs):
        super(CadastroColetaForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit("submit", "Salvar"))


class CadastroItemChecklistColetaForm(forms.ModelForm):
    class Meta:
        model = TabItemChecklistColeta
        exclude = ["id", "data_cadastro", "user"]

    def __init__(self, *args, **kwargs):
        super(CadastroItemChecklistColetaForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit("submit", "Salvar"))

    def save(self, user=None, *args, **kwargs):
        instance = super(CadastroItemChecklistColetaForm, self).save(commit=False)
        if user:
            instance.user = user
        instance.save()
        return instance


class ChecklistColetaForm(forms.ModelForm):
    item_nome = forms.CharField(
        label="item",
        required=False,
        widget=forms.TextInput(attrs={"readonly": "readonly"}),
    )

    class Meta:
        model = TabChecklistColeta
        fields = ["item_nome", "status", "observacao"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields["item_nome"].initial = self.instance.item.item
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.template = "table_inline_formset.html"
        self.helper.form_show_labels = False


class InputFisicoQuimicoForm(forms.ModelForm):
    id_pp_hidden = forms.ModelChoiceField(
        queryset=TabProdxparam.objects.all(), widget=forms.HiddenInput(), required=False
    )

    id_pp_display = forms.CharField(
        label="Parâmetro - unidade",
        required=False,
        widget=forms.TextInput(attrs={"readonly": True, "disabled": True}),
    )

    input_valor = forms.DecimalField(
        label="Valor",
        required=False,
        min_value=0,
        max_digits=10,
        decimal_places=5,
        widget=forms.NumberInput(
            attrs={
                "step": "0.00001",
                "min": "0",
                "class": "form-control",
                'pattern': '^-?\d*\.?\d{0,5}$',
                'placeholder': 'Digite o valor...'
            }
        ),
    )

    class Meta:
        model = TabMedida
        exclude = ["valor", "id_pp"]  # Excluir 'id_pp' para mantê-lo oculto
        fields = [
            "id_pp_hidden",
            "id_pp_display",
            "input_valor",
        ]  # Exibir 'id_pp_hidden' e 'id_envio'

    def __init__(self, *args, **kwargs):
        super(InputFisicoQuimicoForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.id_pp:
            self.fields["id_pp_hidden"].initial = self.instance.id_pp
            self.fields["id_pp_display"].initial = self.instance.id_pp
        else:
            self.fields["id_pp_display"].initial = "N/A"

        self.fields["id_envio"].widget.attrs.update(
            {"readonly": True, "disabled": True}
        )
        self.fields["id_envio"].widget = forms.HiddenInput()

        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.form_show_labels = True
        self.order_fields(["id_pp_hidden", "id_pp_display", "input_valor"])
        self.helper.template = "table_inline_formset.html"
        self.helper.layout = Layout(
            Div(
                Field("input_valor"),  # Exibe a coluna "Valor" em seguida
                Field("id_pp_display"),  # Exibe a coluna "Parâmetro" primeiro
                Field("id_pp_hidden"),  # Campo oculto para o ID real
                css_class="form-row",
            )
        )


class AnexoAmostraForm(forms.ModelForm):
    class Meta:
        model = TabAnexoAmostra
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(AnexoAmostraForm, self).__init__(*args, **kwargs)


class MetadadosPontoForm(forms.ModelForm):
    class Meta:
        model = MetadadosPonto
        exclude = ["codigo_coleta"]  # Exclui o campo codigo_coleta
        labels = {
            "acesso_ponto": "Acesso ao Ponto",
            "dragagem": "Dragagem",
            "gigoga": "Quantidade de Gigoga",
            "odor": "Odor",
            "fezes": "Fezes",
            "oleo": "Óleo",
            "residuos_solidos": "Resíduos Sólidos",
            "lodo": "Lodo",
            "animais_presentes": "Animais Presentes",
            "pescadores": "Pescadores",
            "contato_populacao": "Contato com a População",
        }
        widgets = {
            "acesso_ponto": forms.Select(attrs={"class": "form-select"}),
            "dragagem": forms.NumberInput(
                attrs={
                    "type": "range",
                    "min": -1,
                    "max": 1,
                    "step": 1,
                    "class": "form-range",
                }
            ),
            "gigoga": forms.NumberInput(
                attrs={
                    "type": "range",
                    "min": -1,
                    "max": 1,
                    "step": 1,
                    "class": "form-range",
                }
            ),
            "odor": forms.NumberInput(
                attrs={
                    "type": "range",
                    "min": -1,
                    "max": 1,
                    "step": 1,
                    "class": "form-range",
                }
            ),
            "fezes": forms.NumberInput(
                attrs={
                    "type": "range",
                    "min": -1,
                    "max": 1,
                    "step": 1,
                    "class": "form-range",
                }
            ),
            "oleo": forms.NumberInput(
                attrs={
                    "type": "range",
                    "min": -1,
                    "max": 1,
                    "step": 1,
                    "class": "form-range",
                }
            ),
            "residuos_solidos": forms.NumberInput(
                attrs={
                    "type": "range",
                    "min": -1,
                    "max": 1,
                    "step": 1,
                    "class": "form-range",
                }
            ),
            "lodo": forms.NumberInput(
                attrs={
                    "type": "range",
                    "min": -1,
                    "max": 1,
                    "step": 1,
                    "class": "form-range",
                }
            ),
            "animais_presentes": forms.NumberInput(
                attrs={
                    "type": "range",
                    "min": -1,
                    "max": 1,
                    "step": 1,
                    "class": "form-range",
                }
            ),
            "pescadores": forms.NumberInput(
                attrs={
                    "type": "range",
                    "min": -1,
                    "max": 1,
                    "step": 1,
                    "class": "form-range",
                }
            ),
            "contato_populacao": forms.NumberInput(
                attrs={
                    "type": "range",
                    "min": -1,
                    "max": 1,
                    "step": 1,
                    "class": "form-range",
                }
            ),
        }


class DetalhesUsuarioForm(forms.ModelForm):
    class Meta:
        model = DetalhesUsuario
        fields = ["telefone", "endereco", "cpf"]  # Remova 'usuario' daqui

    def __init__(self, *args, **kwargs):
        super(DetalhesUsuarioForm, self).__init__(*args, **kwargs)
        # Remova a linha que desabilita o campo 'usuario'


class EmailForm(forms.ModelForm):
    class Meta:
        model = EmailTemplate
        fields = "__all__"
