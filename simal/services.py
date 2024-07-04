from datetime import datetime
import requests
from django.conf import settings
import django
import os


django.setup()



def get_weather_description(cidade, data):
    # Obtém a chave API do OpenWeatherMap a partir de uma variável de ambiente
    chave_api = os.getenv('OPENWEATHERMAP_API_KEY',
                          settings.OPENWEATHERMAP_API_KEY)
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={cidade}&appid={chave_api}&units=metric&lang=pt_br"

    try:
        resposta = requests.get(url)
        resposta.raise_for_status()  # Levanta uma exceção para respostas de erro (4xx ou 5xx)
    except requests.RequestException as e:
        return f"Erro ao acessar a API do OpenWeatherMap: {e}"

    previsoes = resposta.json().get('list', [])
    for previsao in previsoes:
        data_previsao = datetime.fromtimestamp(previsao['dt']).date()
        if data_previsao == datetime.strptime(data, '%Y-%m-%d').date():
            descricao = previsao['weather'][0]['description']
            temperatura = previsao['main']['temp']
            return f"Previsão do tempo para {cidade} em {data}: {descricao}, temperatura de {temperatura}°C"

    return "Previsão do tempo não encontrada para a data especificada."


# Exemplo de uso
cidade = "São Paulo"
data = "2024-07-05"  # Formato AAAA-MM-DD
print(get_weather_description(cidade, data))
