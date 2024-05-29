import django_tables2 as tables
from django_tables2.utils import A  # import A
from .models import *

#TODO: Adicionar filtro e opção para exportação de dados
class ColetaCampoTable(tables.Table):
    
    update = tables.LinkColumn('atualizar_coleta', args=[A('pk')], orderable=False, empty_values=[])

    class Meta:
        model = Campo
        template_name = 'django_tables2/bootstrap.html'
        fields = ['clima', 'matriz', 'hora_inicio', 'hora_fim', 'temperatura', 'ph', 'orp', 'condutividade', 'turbidez', 'od', 'od_pct', 'tds', 'salinidade','data', 'update']
        attrs = {'class': 'table table-striped table-bordered table-hover'}
        empty_text = 'Não há dados para exibir'
        orderable = False
        exclude = ('id', 'created_at', 'updated_at', 'campo')
        sequence = ('clima', 'matriz', 'hora_inicio', 'hora_fim', 'temperatura', 'ph', 'orp', 'condutividade', 'turbidez', 'od', 'od_pct', 'tds', 'salinidade','data', 'update')
        per_page = 10
        paginator_class = tables.LazyPaginator
        table_pagination = True

class ProgramaColetaTable(tables.Table):
    
    update = tables.LinkColumn('atualizar_programacao', args=[A('pk')], orderable=False, empty_values=[],text='EDITAR')
    start = tables.LinkColumn('atualizar_programacao', args=[A('pk')], orderable=False, empty_values=[],text='Iniciar')
    class Meta:
        model = ProgramaColeta
        template_name = 'django_tables2/bootstrap.html'
        fields = ['data_coleta_campo', 'equipe_coleta', 'laboratorio', 'solicitante', 'local_coleta', 'status_coleta', 'observacoes']
        attrs = {'class': 'table table-striped table-bordered table-hover'}
        empty_text = 'Não há dados para exibir'
        orderable = False
        exclude = ('id', 'created_at', 'updated_at', 'campo')
        sequence = ('data_coleta_campo', 'equipe_coleta', 'laboratorio', 'solicitante', 'local_coleta', 'status_coleta', 'observacoes')
        per_page = 10
        paginator_class = tables.LazyPaginator
        table_pagination = True

#TODO: Criar tabelas para as outras classes