from simal.models import *


# Lista de parâmetros
parametros = ['OD', 'Escherichia coli', 'DBOs',
              'Nitrogênio Total', 'Fosfato', 'pH', 'Turbidez', 'TDS']

# Função para obter os IDs dos parâmetros


def get_parametros_ids(parametros):
    return TabParam.objects.filter(nome__in=parametros).values_list('id', flat=True)


# Supondo que parametros_ids já esteja definido
parametros_ids = TabParam.objects.filter(
    nome__in=parametros).values_list('id', flat=True)

# Executa a consulta
queryset = TabMedida.objects.filter(id_pp__id_param__in=parametros_ids).values(
    'id',  # ID da medida
    'input_valor',  # Valor da medição
    'id_envio__id_amostra__id_coleta',  # ID da coleta
    'id_envio__id_amostra__id_coleta__id_campanha',  # ID da campanha
    'id_envio__id_amostra__id_ponto',  # ID do ponto
    'id_pp__id_param__nome'  # Nome do parâmetro
)

# Converte o queryset em uma lista de dicionários
data = list(queryset)

# Cria o DataFrame
df = pd.DataFrame(data)

# Exibe o DataFrame
print(df)
     
    
    
    
