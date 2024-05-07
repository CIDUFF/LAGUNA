import django_tables2 as tables
from .models import *


class ColetaCampoTable(tables.Table):
    class Meta:
        model = Campo
        template_name = 'django_tables2/bootstrap.html'
        fields = ['clima', 'matriz', 'hora_inicio', 'hora_fim', 'temperatura', 'ph', 'orp', 'condutividade', 'turbidez', 'od', 'od_pct', 'tds', 'salinidade','data']
        attrs = {'class': 'table table-striped table-bordered table-hover'}
        empty_text = 'Não há dados para exibir'
        orderable = False
        exclude = ('id', 'created_at', 'updated_at', 'campo')
        sequence = ('clima', 'matriz', 'hora_inicio', 'hora_fim', 'temperatura', 'ph', 'orp', 'condutividade', 'turbidez', 'od', 'od_pct', 'tds', 'salinidade','data')
        per_page = 10
        paginator_class = tables.LazyPaginator
        table_pagination = False