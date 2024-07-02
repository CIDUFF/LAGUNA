import requests


def get_weather_description(city, date=None):
    api_key = "c7f48ba7775040a6dee7d27670eb2553"
    # Ajuste a URL da API conforme necessário para incluir a data, se disponível
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&lang=pt_br"
    # Se a data for fornecida, ajuste a URL ou a lógica de solicitação conforme necessário

    response = requests.get(url)
    data = response.json()

    weather_description = data['weather'][0]['description']
    return weather_description
