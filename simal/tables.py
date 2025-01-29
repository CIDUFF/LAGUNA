import django_tables2 as tables
from django_tables2.utils import A  # import A
from .models import (
    Campo,
    ProgramaColeta,
    Laboratorios,
    TabColeta,
    TabSetor,
    TabPonto,
    TabLocal,
    TipoParametro,
    TabParam,
    TabFrasco,
    TabEquipe,
    TabLaboratorio,
    TabProduto,
    TabProdxparam,
    TabSerieClassificacao,
    TabItemChecklistColeta,
    TabMedida,
    TabAmostra,
    EmailTemplate,
)
from django.utils.html import format_html

# TODO: Adicionar filtro e opção para exportação de dados


class ColetaCampoTable(tables.Table):
    update = tables.LinkColumn(
        "atualizar_coleta",
        args=[A("pk")],
        orderable=False,
        empty_values=[],
        text="Preencher dados",
        attrs={"a": {"class": "btn btn-success btn-sm"}},
    )

    class Meta:
        model = Campo
        template_name = "tables/bootstrap5.html"
        fields = ["ponto", "codigo_coleta", "status_form", "update"]
        # attrs = {'class': 'table table-striped table-bordered table-hover'}
        empty_text = "Não há dados para exibir"
        orderable = True
        exclude = ("id", "created_at", "updated_at", "campo")
        sequence = ("ponto", "codigo_coleta", "status_form", "update")
        per_page = 10
        paginator_class = tables.LazyPaginator
        table_pagination = True

    def render_status_form(self, value):
        status_to_class = {
            "Não preenchido": "bg-warning text-dark",
            "Preenchido": "bg-success",
        }
        badge_class = status_to_class.get(value, "")
        if badge_class:
            return format_html('<span class="badge {}">{}</span>', badge_class, value)
        return value


class ResultadosColetaTable(tables.Table):
    class Meta:
        model = Campo
        template_name = "tables/bootstrap5.html"
        fields = [
            "codigo_coleta",
            "hora_inicio",
            "hora_fim",
            "ponto",
            "temperatura",
            "ph",
            "orp",
            "condutividade",
            "turbidez",
            "od",
            "od_pct",
            "tds",
            "salinidade",
            "status_form",
            "check_amostras",
            "observacoes",
            "foto",
        ]
        empty_text = "Não há dados para exibir"
        orderable = True
        exclude = ("id", "created_at", "updated_at", "campo")
        sequence = (
            "codigo_coleta",
            "hora_inicio",
            "hora_fim",
            "ponto",
            "temperatura",
            "ph",
            "orp",
            "condutividade",
            "turbidez",
            "od",
            "od_pct",
            "tds",
            "salinidade",
            "status_form",
            "check_amostras",
            "observacoes",
            "foto",
        )
        per_page = 25
        paginator_class = tables.LazyPaginator
        table_pagination = True


class ProgramaColetaTable(tables.Table):
    # Define os atributos comuns
    common_attrs = {
        "a": {
            "class": "btn btn-primary btn-sm active",
            "style": "font-weight: normal; font-size: 0.7em; background-color: #5783b6",
        }
    }
    delete_attrs = {
        "a": {
            "class": "btn btn-primary btn-sm active delete-campaign-btn",
            "style": "font-weight: normal; font-size: 0.7em; background-color: #5783b6",
        }
    }
    cancel_attrs = {
        "a": {
            "class": "btn btn-primary btn-sm active cancel-campaign-btn",
            "style": "font-weight: normal; font-size: 0.7em; background-color: #5783b6",
        }
    }

    atualizar = tables.LinkColumn(
        "atualizar_programacao",
        args=[A("pk")],
        orderable=False,
        empty_values=[],
        text="",
        attrs=common_attrs,
    )
    deletar = tables.LinkColumn(
        "deletar_programacao",
        args=[A("pk")],
        orderable=False,
        empty_values=[],
        text="",
        attrs=delete_attrs,
    )
    cancelar = tables.LinkColumn(
        "cancelar_programacao",
        args=[A("pk")],
        orderable=False,
        empty_values=[],
        text="",
        attrs=cancel_attrs,
    )
    iniciar = tables.LinkColumn(
        "checklist_campanha",
        args=[A("ordem_servico")],
        orderable=False,
        empty_values=[],
        text="",
        attrs=common_attrs,
    )

    class Meta:
        model = ProgramaColeta
        template_name = "tables/bootstrap5.html"
        fields = [
            "ordem_servico",
            "usuario",
            "data_coleta_campo",
            "local_coleta",
            "status_coleta",
        ]
        empty_text = "Não há dados para exibir"
        orderable = True
        exclude = ("id", "created_at", "updated_at", "campo")
        sequence = (
            "ordem_servico",
            "usuario",
            "data_coleta_campo",
            "local_coleta",
            "status_coleta",
            "iniciar",
            "atualizar",
            "cancelar",
            "deletar",
        )
        per_page = 10
        paginator_class = tables.LazyPaginator
        table_pagination = True

    def render_status_coleta(self, value):
        status_to_class = {
            "Iniciada": "bg-primary",
            "Cancelada": "bg-danger",
            "Coleta realizada": "bg-success",
            "Programada": "bg-warning text-dark",
        }
        badge_class = status_to_class.get(value, "")
        if badge_class:
            return format_html('<span class="badge {}">{}</span>', badge_class, value)
        return value


class LaboratoriosTable(tables.Table):
    update = tables.LinkColumn(
        "atualizar_laboratorio",
        args=[A("pk")],
        orderable=False,
        empty_values=[],
        text="EDITAR",
    )
    analises = tables.Column(empty_values=(), orderable=False, verbose_name="Análises")

    def render_analises(self, record):
        return ", ".join([analise.analise for analise in record.analises.all()])

    class Meta:
        model = Laboratorios
        template_name = "tables/bootstrap5.html"
        fields = ["nome", "email", "telefone", "endereco", "tipo"]
        empty_text = "Não há dados para exibir"
        orderable = False
        exclude = ("id", "created_at", "updated_at")
        sequence = ("nome", "email", "telefone", "endereco", "tipo", "analises")
        per_page = 10
        paginator_class = tables.LazyPaginator
        table_pagination = True


# class TopCampanhas(tables.Table):
#     class Meta:
#         model = ProgramaColeta
#         template_name = "django_tables2/bootstrap5-responsive.html"
#         fields = ["ordem_servico", "data_coleta_campo",
#                   "local_coleta", "status_coleta"]
#         empty_text = "Não há dados para exibir"
#         orderable = True
#         exclude = ("id", "created_at", "updated_at", "campo")
#         sequence = (
#             "ordem_servico",
#             "data_coleta_campo",
#             "local_coleta",
#             "status_coleta",
#         )
#         per_page = 3
#         paginator_class = tables.LazyPaginator
#         table_pagination = True

#     def render_status_coleta(self, value):
#         status_to_class = {
#             "Iniciada": "bg-primary",
#             "Cancelada": "bg-danger",
#             "Coleta realizada": "bg-success",
#             "Programada": "bg-warning text-dark",
#         }
#         badge_class = status_to_class.get(value, "")
#         if badge_class:
#             return format_html('<span class="badge {}">{}</span>', badge_class, value)
#         return value


class TopCampanhas(tables.Table):
    ordem_servico = tables.Column(
        attrs={
            "th": {"class": "d-none d-md-table-cell"},
            "td": {"class": "d-none d-md-table-cell"},
        }
    )
    data_coleta_campo = tables.DateColumn(
        format="d/m/Y",
        attrs={
            "th": {"class": "d-none d-md-table-cell"},
            "td": {"class": "d-none d-md-table-cell"},
        },
    )
    local_coleta = tables.Column()
    status_coleta = tables.Column()

    class Meta:
        model = ProgramaColeta
        template_name = "tables/bootstrap5.html"
        fields = ["ordem_servico", "data_coleta_campo", "local_coleta", "status_coleta"]
        empty_text = "Não há dados para exibir"
        orderable = True
        exclude = ("id", "created_at", "updated_at", "campo")
        sequence = (
            "ordem_servico",
            "data_coleta_campo",
            "local_coleta",
            "status_coleta",
        )
        per_page = 3
        paginator_class = tables.LazyPaginator
        table_pagination = True
        attrs = {
            "class": "table table-bordered table-hover",
            "thead": {"class": "thead-light"},
        }

    def render_status_coleta(self, value):
        status_to_class = {
            "Iniciada": "bg-primary",
            "Cancelada": "bg-danger",
            "Coleta realizada": "bg-success",
            "Programada": "bg-warning text-dark",
        }
        badge_class = status_to_class.get(value, "")
        if badge_class:
            return format_html('<span class="badge {}">{}</span>', badge_class, value)
        return value

    def render_local_coleta(self, value):
        return format_html(
            '<span class="d-inline d-md-none font-weight-bold">Local:</span> {}', value
        )


class SetorTable(tables.Table):
    update = tables.LinkColumn(
        'atualizar_setor',
        args=[A('pk')],
        orderable=False,
        empty_values=[],
        text=lambda record: format_html('<i class="bi bi-pencil-square me-1"></i>Editar'),
        attrs={'a': {'class': 'btn btn-sm btn-outline-primary rounded-pill'}}
    )

    class Meta:
        model = TabSetor
        template_name = "tables/bootstrap5.html"
        fields = ["nome", "local", "lat", "lon", "abreviatura"]
        empty_text = "Não há dados para exibir"
        orderable = False
        exclude = ("id", "created_at", "updated_at")
        sequence = ("nome", "local", "lat", "lon", "abreviatura")
        per_page = 2
        paginator_class = tables.LazyPaginator
        table_pagination = True


class PontoTable(tables.Table):
    update = tables.LinkColumn(
        'atualizar_ponto',
        args=[A('pk')],
        orderable=False,
        empty_values=[],
        text=lambda record: format_html('<i class="bi bi-pencil-square me-1"></i>Editar'),
        attrs={'a': {'class': 'btn btn-sm btn-outline-primary rounded-pill'}}
    )

    class Meta:
        model = TabPonto
        template_name = "tables/bootstrap5.html"
        fields = ["nome", "id_setor", "id_local", "modalidade", "lat", "lon", "status"]
        empty_text = "Não há dados para exibir"
        orderable = True
        exclude = ("id", "created_at", "updated_at")
        sequence = (
            "nome",
            "id_setor",
            "id_local",
            "modalidade",
            "lat",
            "lon",
            "status",
        )
        per_page = 10
        paginator_class = tables.LazyPaginator
        table_pagination = True


class LocalTable(tables.Table):
    update = tables.LinkColumn(
        'atualizar_local',
        args=[A('pk')],
        orderable=False,
        empty_values=[],
        text=lambda record: format_html('<i class="bi bi-pencil-square me-1"></i>Editar'),
        attrs={'a': {'class': 'btn btn-sm btn-outline-primary rounded-pill'}}
    )

    class Meta:
        model = TabLocal
        template_name = "tables/bootstrap5.html"
        fields = ["nome", "desc"]
        empty_text = "Não há dados para exibir"
        orderable = False
        exclude = ("id", "created_at", "updated_at")
        sequence = ("nome", "desc")
        per_page = 1
        paginator_class = tables.LazyPaginator
        table_pagination = True


class TipoParametroTable(tables.Table):
    #    update = tables.LinkColumn('atualizar_tipo_parametro', args=[A('pk')], orderable=False, empty_values=[], text='EDITAR')

    class Meta:
        model = TipoParametro
        template_name = "tables/bootstrap5.html"
        fields = ["nome", "descricao"]
        empty_text = "Não há dados para exibir"
        orderable = False
        exclude = ("id", "created_at", "updated_at")
        sequence = ("nome", "descricao")
        per_page = 1
        paginator_class = tables.LazyPaginator
        table_pagination = True


class ParametroTable(tables.Table):
    update = tables.LinkColumn(
        "editar_registro",
        args=["param", A("pk")],
        orderable=False,
        empty_values=[],
        text="EDITAR",
    )

    class Meta:
        model = TabParam
        template_name = "django_tables2/bootstrap.html"
        fields = ("nome", "param_meta_dado")


class EmailTable(tables.Table):
    update = tables.LinkColumn(
        "editar_registro",
        args=["email", A("pk")],
        orderable=False,
        empty_values=[],
        text="EDITAR",
    )

    class Meta:
        model = EmailTemplate
        template_name = "django_tables2/bootstrap.html"
        fields = ("nome", "assunto", "corpo")


# class ParametroTable(tables.Table):
#     update = tables.LinkColumn('atualizar_parametro', args=[A('pk')], orderable=False, empty_values=[], text='EDITAR')

#     class Meta:
#         model = TabParam
#         template_name = "django_tables2/bootstrap.html"
#         fields = ('nome', 'param_meta_dado')


class FrascoTable(tables.Table):
    update = tables.LinkColumn(
        "editar_registro",
        args=["frasco", A("pk")],
        orderable=False,
        empty_values=[],
        text="EDITAR",
    )

    class Meta:
        model = TabFrasco
        template_name = "django_tables2/bootstrap.html"
        fields = ("nome",)
        empty_text = "Não há dados para exibir"
        orderable = False
        exclude = ("id",)
        sequence = ("nome",)
        per_page = 1
        paginator_class = tables.LazyPaginator
        table_pagination = True


class EquipeTable(tables.Table):
    update = tables.LinkColumn(
        "editar_registro",
        args=["equipe", A("pk")],
        orderable=False,
        empty_values=[],
        text="EDITAR",
    )

    class Meta:
        model = TabEquipe
        template_name = "django_tables2/bootstrap.html"
        fields = ("nome",)


class LaboratorioTable(tables.Table):
    update = tables.LinkColumn(
        "editar_registro",
        args=["laboratorio", A("pk")],
        orderable=False,
        empty_values=[],
        text="EDITAR",
    )

    class Meta:
        model = TabLaboratorio
        template_name = "django_tables2/bootstrap.html"
        fields = ("nome",)


class ProdutoTable(tables.Table):
    update = tables.LinkColumn(
        "editar_registro",
        args=["produto", A("pk")],
        orderable=False,
        empty_values=[],
        text="EDITAR",
    )

    class Meta:
        model = TabProduto
        template_name = "django_tables2/bootstrap.html"
        fields = ("nome",)


class ProdxparamTable(tables.Table):
    update = tables.LinkColumn(
        "editar_registro",
        args=["prodxparam", A("pk")],
        orderable=False,
        empty_values=[],
        text="EDITAR",
    )

    class Meta:
        model = TabProdxparam
        template_name = "django_tables2/bootstrap.html"
        fields = ("nome",)


class SerieClassificacaoTable(tables.Table):
    update = tables.LinkColumn(
        "editar_registro",
        args=["serie_classificacao", A("pk")],
        orderable=False,
        empty_values=[],
        text="EDITAR",
    )

    class Meta:
        model = TabSerieClassificacao
        template_name = "django_tables2/bootstrap.html"
        fields = ("nome",)


class TipoItemChecklistColetaTable(tables.Table):
    update = tables.LinkColumn(
        "editar_registro",
        args=["item_checklist", A("pk")],
        orderable=False,
        empty_values=[],
        text="EDITAR",
    )

    class Meta:
        model = TabItemChecklistColeta
        template_name = "tables/bootstrap5.html"
        fields = ("item",)
        # exclude = ['id', 'data_cadastro']
        # empty_text = 'Não há dados para exibir'
        # orderable = True
        # per_page = 10
        # paginator_class = tables.LazyPaginator
        # table_pagination = True


class ListaCampoTable(tables.Table):
    acoes = tables.TemplateColumn(
        template_code='''
        <button type="button" class="btn btn-primary btn-sm btn-preencher" data-ponto-id="{{ record.id_ponto.id }}">
            <i class="bi bi-pencil-square"></i> Preencher dados
        </button>
        ''',
        verbose_name="Ações"
    )
    
    class Meta:
        model = TabAmostra
        fields = ["id_ponto", "etiqueta"]
        attrs = {"class": "table table-hover"}


class TabColetaTable(tables.Table):
    selecionar = tables.TemplateColumn(
        '<input type="radio" name="selecionar" value="{{ record.pk }}" class="single-select">',
        orderable=False,
        attrs={
            "input": {"class": "single-select"},
            "th__input": {"style": "display:none;"},
        },
    )

    class Meta:
        model = TabColeta
        template_name = "django_tables2/bootstrap5-responsive.html"
        fields = [
            "selecionar",
            "data",
            "nome",
            "id_campanha",
            "id_setor",
            "ordem_servico",
            "status",
        ]
        empty_text = "Não há dados para exibir"
        orderable = True
        exclude = ("id",)
        sequence = (
            "selecionar",
            "data",
            "nome",
            "id_campanha",
            "id_setor",
            "ordem_servico",
            "status",
        )
        per_page = 5
        paginator_class = tables.LazyPaginator
        table_pagination = True
        order_by = "-data"  # Adiciona ordenação decrescente por data
        labels = {
            "data": "Data",
            "nome": "Nome",
            "id_campanha": "Campanha",
            "id_setor": "Setor",
            "ordem_servico": "Ordem de Serviço",
            "status": "Status",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.base_columns["id_campanha"].verbose_name = "Campanha"
        self.base_columns["id_setor"].verbose_name = "Setor"
