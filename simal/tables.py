import django_tables2 as tables
from django_tables2.utils import A  # import A
from .models import *
from django.utils.html import format_html

# TODO: Adicionar filtro e opção para exportação de dados


class ColetaCampoTable(tables.Table):

    update = tables.LinkColumn('atualizar_coleta', args=[
                               A('pk')], orderable=False, empty_values=[], text='Preencher dados',
                               attrs={"a": {"class": "btn btn-success btn-sm"}})

    class Meta:
        model = Campo
        template_name = 'django_tables2/bootstrap5-responsive.html'
        fields = ['ponto', 'codigo_coleta', 'status_form', 'update']
        # attrs = {'class': 'table table-striped table-bordered table-hover'}
        empty_text = 'Não há dados para exibir'
        orderable = True
        exclude = ('id', 'created_at', 'updated_at', 'campo')
        sequence = ('ponto', 'codigo_coleta', 'status_form', 'update')
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
        template_name = 'django_tables2/bootstrap5-responsive.html'
        fields = ['codigo_coleta',
                  'hora_inicio',
                  'hora_fim', 'ponto', 'temperatura', 'ph',
                  'orp', 'condutividade', 'turbidez', 'od',
                  'tds', 'salinidade']
        empty_text = 'Não há dados para exibir'
        orderable = True
        exclude = ('id', 'created_at', 'updated_at', 'campo')
        sequence = ('codigo_coleta',
                    'hora_inicio',
                    'hora_fim', 'ponto', 'temperatura', 'ph',
                    'orp', 'condutividade', 'turbidez', 'od',
                    'tds', 'salinidade')
        per_page = 25
        paginator_class = tables.LazyPaginator
        table_pagination = True


class ProgramaColetaTable(tables.Table):
    # Define os atributos comuns
    common_attrs = {
        "a": {
            "class": "btn btn-primary btn-sm active",
            "style": "font-weight: normal; font-size: 0.7em; background-color: #5783b6"
        }
    }
    delete_attrs = {
        "a": {
            "class": "btn btn-primary btn-sm active delete-campaign-btn",
            "style": "font-weight: normal; font-size: 0.7em; background-color: #5783b6"
        }
    }
    cancel_attrs = {
        "a": {
            "class": "btn btn-primary btn-sm active cancel-campaign-btn",
            "style": "font-weight: normal; font-size: 0.7em; background-color: #5783b6"
        }
    }
    
    atualizar = tables.LinkColumn('atualizar_programacao', args=[A('pk')], orderable=False, empty_values=[],
                                  text='', attrs=common_attrs)
    deletar = tables.LinkColumn('deletar_programacao', args=[A('pk')], orderable=False, empty_values=[],
                                text='', attrs=delete_attrs)
    cancelar = tables.LinkColumn('cancelar_programacao', args=[A('pk')], orderable=False, empty_values=[],
                                 text='', attrs=cancel_attrs)
    iniciar = tables.LinkColumn('checklist_campanha', args=[A('ordem_servico')], orderable=False, empty_values=[],
                                text='', attrs=common_attrs)
    
    class Meta:
        model = ProgramaColeta
        template_name = 'django_tables2/bootstrap5-responsive.html'
        fields = ['ordem_servico', 'usuario', 'data_coleta_campo',
                  'local_coleta', 'status_coleta']
        empty_text = 'Não há dados para exibir'
        orderable = True
        exclude = ('id', 'created_at', 'updated_at', 'campo')
        sequence = ('ordem_servico', 'usuario', 'data_coleta_campo',
                    'local_coleta', 'status_coleta', 'iniciar', 'atualizar', 'cancelar', 'deletar')
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
    update = tables.LinkColumn('atualizar_laboratorio', args=[A(
        'pk')], orderable=False, empty_values=[], text='EDITAR')
    analises = tables.Column(
        empty_values=(), orderable=False, verbose_name='Análises')

    def render_analises(self, record):
        return ', '.join([analise.analise for analise in record.analises.all()])

    class Meta:
        model = Laboratorios
        template_name = 'django_tables2/bootstrap5-responsive.html'
        fields = ['nome', 'email', 'telefone', 'endereco', 'tipo']
        empty_text = 'Não há dados para exibir'
        orderable = False
        exclude = ('id', 'created_at', 'updated_at')
        sequence = ('nome', 'email', 'telefone',
                    'endereco', 'tipo', 'analises')
        per_page = 10
        paginator_class = tables.LazyPaginator
        table_pagination = True


class TopCampanhas(tables.Table):
    class Meta:
        model = ProgramaColeta
        template_name = 'django_tables2/bootstrap5-responsive.html'
        fields = ['ordem_servico', 'data_coleta_campo', 'local_coleta', 'status_coleta']
        empty_text = 'Não há dados para exibir'
        orderable = True
        exclude = ('id', 'created_at', 'updated_at', 'campo')
        sequence = ('ordem_servico', 'data_coleta_campo',
                    'local_coleta', 'status_coleta')
        per_page = 3
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

class SetorTable(tables.Table):
    update = tables.LinkColumn('atualizar_setor', args=[A(
        'pk')], orderable=False, empty_values=[], text='EDITAR')

    class Meta:
        model = Setor
        template_name = 'django_tables2/bootstrap5-responsive.html'
        fields = ['nome', 'local', 'lat', 'lon','abreviatura']
        empty_text = 'Não há dados para exibir'
        orderable = False
        exclude = ('id', 'created_at', 'updated_at')
        sequence = ('nome', 'local', 'lat', 'lon','abreviatura')
        per_page = 2
        paginator_class = tables.LazyPaginator
        table_pagination = True
        
class PontoTable(tables.Table):
    update = tables.LinkColumn('atualizar_ponto', args=[A('pk')], orderable=False, empty_values=[], text='EDITAR')

    class Meta:
        model = PontosColeta
        template_name = 'django_tables2/bootstrap5-responsive.html'
        fields = ['nome', 'setor', 'local', 'tipo', 'lat', 'lon','status']
        empty_text = 'Não há dados para exibir'
        orderable = True
        exclude = ('id', 'created_at', 'updated_at')
        sequence = ('nome', 'setor', 'local', 'tipo', 'lat', 'lon','status')
        per_page = 10
        paginator_class = tables.LazyPaginator
        table_pagination = True
        
class LocalTable(tables.Table):
    update = tables.LinkColumn('atualizar_local', args=[A('pk')], orderable=False, empty_values=[], text='EDITAR')

    class Meta:
        model = TabLocal
        template_name = 'django_tables2/bootstrap5-responsive.html'
        fields = ['nome', 'desc']
        empty_text = 'Não há dados para exibir'
        orderable = False
        exclude = ('id', 'created_at', 'updated_at')
        sequence = ('nome', 'desc')
        per_page = 1
        paginator_class = tables.LazyPaginator
        table_pagination = True
        
class TipoParametroTable(tables.Table):
#    update = tables.LinkColumn('atualizar_tipo_parametro', args=[A('pk')], orderable=False, empty_values=[], text='EDITAR')

    class Meta:
        model = TipoParametro
        template_name = 'django_tables2/bootstrap5-responsive.html'
        fields = ['nome', 'descricao']
        empty_text = 'Não há dados para exibir'
        orderable = False
        exclude = ('id', 'created_at', 'updated_at')
        sequence = ('nome', 'descricao')
        per_page = 1
        paginator_class = tables.LazyPaginator
        table_pagination = True