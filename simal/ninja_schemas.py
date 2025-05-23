from ninja import ModelSchema
from simal.models import TabColeta


class ColetaSchema(ModelSchema):
    class Config:
        model = TabColeta
        # Se quiser incluir todos os campos:
        model_fields = "__all__"
