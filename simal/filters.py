from django_filters import FilterSet, CharFilter, ChoiceFilter
from functools import wraps
from .models import Campo, ProgramaColeta, TabPonto, TabSetor, TabLocal


# def lazy_filter(cls):
#     """Decorator para garantir inicialização lazy e singleton das classes de filtro"""
#     _instances = {}

#     @wraps(cls)
#     def get_instance(*args, **kwargs):
#         if cls not in _instances:
#             _instances[cls] = cls(*args, **kwargs)
#         return _instances[cls]

#     return get_instance


# @lazy_filter
class CampoFilter(FilterSet):
    class Meta:
        model = Campo
        fields = {
            "ponto": ["icontains"],
        }


# @lazy_filter
class ProgramaColetaFilter(FilterSet):
    class Meta:
        model = ProgramaColeta
        fields = {
            "local_coleta": ["icontains"],
            "data_coleta_campo": ["exact"],
            "status_coleta": ["exact"],
        }


# @lazy_filter
class ResultadosColetaFilter(FilterSet):
    ponto = CharFilter(lookup_expr="icontains", label="Ponto")
    codigo_coleta = CharFilter(lookup_expr="icontains", label="Código da Coleta")

    class Meta:
        fields = ["ponto", "codigo_coleta"]


# @lazy_filter
class PontoFilter(FilterSet):
    codigo = ChoiceFilter(field_name="nome", lookup_expr="exact", label="Ponto")
    setor = ChoiceFilter(field_name="id_setor", lookup_expr="exact", label="Setor")
    status = ChoiceFilter(field_name="status", lookup_expr="exact", label="Status")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters["codigo"].extra["choices"] = [
            (ponto.nome, ponto.nome) for ponto in TabPonto.objects.all().distinct()
        ]
        self.filters["setor"].extra["choices"] = [
            (setor.id, setor.nome) for setor in TabSetor.objects.all().distinct()
        ]
        self.filters["status"].extra["choices"] = [(True, "Ativo"), (False, "Inativo")]

    class Meta:
        model = TabPonto
        fields = ["nome", "status"]


# @lazy_filter
class SetorFilter(FilterSet):
    abreviatura = ChoiceFilter(
        field_name="abreviatura", lookup_expr="exact", label="Setor"
    )
    local = ChoiceFilter(field_name="id_local", lookup_expr="exact", label="Local")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters["abreviatura"].extra["choices"] = [
            (setor.nome, setor.nome) for setor in TabSetor.objects.all().distinct()
        ]
        self.filters["local"].extra["choices"] = [
            (local.id, local.nome) for local in TabLocal.objects.all().distinct()
        ]

    class Meta:
        model = TabSetor
        fields = ["abreviatura", "local"]


# @lazy_filter
class LocalFilter(FilterSet):
    codigo = ChoiceFilter(field_name="nome", lookup_expr="exact", label="Local")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters["codigo"].extra["choices"] = [
            (local.nome, local.nome) for local in TabLocal.objects.all().distinct()
        ]

    class Meta:
        model = TabLocal
        fields = ["codigo"]
