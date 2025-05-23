from ninja import NinjaAPI
from typing import List
from simal.ninja_schemas import (
    ColetaSchema,
)
from simal.models import (
    TabColeta,
)

api = NinjaAPI()


@api.get("/coletas", response=List[ColetaSchema])
def coletas(request):
    return TabColeta.objects.all()


# # @api.get("/ola")
# # def ola_mundo(request):
# #     return {"message": "Olá Mundo!"}


# # @api.get("/hello")
# # def hello(request):
# #     return "Hello world"
