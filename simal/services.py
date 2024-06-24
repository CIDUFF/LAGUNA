import requests


def get_weather_description(city):
    api_key = "c7f48ba7775040a6dee7d27670eb2553"
    # Construa a URL da API
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&lang=pt_br"

    # Faça a solicitação à API
    response = requests.get(url)
    data = response.json()

    # Obtenha a descrição do tempo
    weather_description = data['weather'][0]['description']

    return weather_description
