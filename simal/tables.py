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


class ProgramaColetaTable(tables.Table):
    atualizar = tables.LinkColumn('atualizar_programacao', args=[A('pk')], orderable=False, empty_values=[
    ], text='Atualizar dados', attrs={"a": {"class": "btn btn-info btn-sm"}})
    deletar = tables.LinkColumn('deletar_programacao', args=[A('pk')], orderable=False, empty_values=[
    ], text='Remover programação', attrs={"a": {"class": "btn btn-secondary btn-sm"}})
    cancelar = tables.LinkColumn('cancelar_programacao', args=[A('pk')], orderable=False, empty_values=[
    ], text='Cancelar programação', attrs={"a": {"class": "btn btn-danger btn-sm"}})
    iniciar = tables.LinkColumn('checklist_campanha', args=[A('ordem_servico')], orderable=False, empty_values=[
    ], text='Iniciar campanha', attrs={"a": {"class": "btn btn-success btn-sm"}})

    class Meta:
        model = ProgramaColeta
        template_name = 'django_tables2/bootstrap5-responsive.html'
        fields = ['ordem_servico', 'usuario', 'data_coleta_campo',
                  'solicitante', 'local_coleta', 'status_coleta']
        empty_text = 'Não há dados para exibir'
        orderable = True
        exclude = ('id', 'created_at', 'updated_at', 'campo')
        sequence = ('ordem_servico', 'usuario', 'data_coleta_campo', 'solicitante',
                    'local_coleta', 'status_coleta', 'atualizar', 'deletar', 'cancelar', 'iniciar')
        per_page = 10
        paginator_class = tables.LazyPaginator
        table_pagination = True

    def render_status_coleta(self, value):
        status_to_class = {
            "Iniciada": "bg-success",
            "Cancelada": "bg-danger",
            "Coleta realizada": "bg-primary",
            "Programada": "bg-warning text-dark",
        }
        badge_class = status_to_class.get(value, "")
        if badge_class:
            return format_html('<span class="badge {}">{}</span>', badge_class, value)
        return value


class LaboratoriosTable(tables.Table):

    update = tables.LinkColumn('atualizar_laboratorio', args=[A(
        'pk')], orderable=False, empty_values=[], text='EDITAR')

    class Meta:
        model = Laboratorios
        template_name = 'django_tables2/bootstrap5-responsive.html'
        fields = ['nome', 'email', 'telefone', 'endereco', 'tipo']
        attrs = {'class': 'table table-striped table-bordered table-hover'}
        empty_text = 'Não há dados para exibir'
        orderable = False
        exclude = ('id', 'created_at', 'updated_at')
        sequence = ('nome', 'email', 'telefone', 'endereco', 'tipo')
        per_page = 10
        paginator_class = tables.LazyPaginator
        table_pagination = True
# TODO: Criar tabelas para as outras classes
