import django_tables2 as tables
from django_tables2.utils import A  # import A
from .models import *

# TODO: Adicionar filtro e opção para exportação de dados


class ColetaCampoTable(tables.Table):

    update = tables.LinkColumn('atualizar_coleta', args=[
                               A('pk')], orderable=False, empty_values=[], text='Preencher dados')

    class Meta:
        model = Campo
        template_name = 'django_tables2/bootstrap.html'
        fields = ['ponto', 'ordem_servico', 'status_form', 'update']
        attrs = {'class': 'table table-striped table-bordered table-hover'}
        empty_text = 'Não há dados para exibir'
        orderable = False
        exclude = ('id', 'created_at', 'updated_at', 'campo')
        sequence = ('ponto', 'ordem_servico', 'status_form', 'update')
        per_page = 10
        paginator_class = tables.LazyPaginator
        table_pagination = True


class ProgramaColetaTable(tables.Table):

    atualizar = tables.LinkColumn('atualizar_programacao', args=[A(
        'pk')], orderable=False, empty_values=[], text='Atualizar dados')
    deletar = tables.LinkColumn('deletar_programacao', args=[A(
        'pk')], orderable=False, empty_values=[], text='Remover programação')
    cancelar = tables.LinkColumn('cancelar_programacao', args=[A(
        'pk')], orderable=False, empty_values=[], text='Cancelar programação')
    iniciar = tables.LinkColumn('checklist_campanha', args=[A(
        'ordem_servico')], orderable=False, empty_values=[], text='Iniciar coleta')

    class Meta:
        model = ProgramaColeta
        template_name = 'django_tables2/bootstrap.html'
        fields = ['ordem_servico', 'usuario', 'data_coleta_campo', 'solicitante',
                  'local_coleta', 'status_coleta']
        attrs = {'class': 'table table-striped table-bordered table-hover'}
        empty_text = 'Não há dados para exibir'
        orderable = False
        exclude = ('id', 'created_at', 'updated_at', 'campo')
        sequence = ('ordem_servico', 'usuario', 'data_coleta_campo', 'solicitante',
                    'local_coleta', 'status_coleta')
        per_page = 10
        paginator_class = tables.LazyPaginator
        table_pagination = True


class LaboratoriosTable(tables.Table):

    update = tables.LinkColumn('atualizar_laboratorio', args=[A(
        'pk')], orderable=False, empty_values=[], text='EDITAR')

    class Meta:
        model = Laboratorios
        template_name = 'django_tables2/bootstrap.html'
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
