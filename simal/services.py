from datetime import datetime
import requests
# import os
# from dotenv import load_dotenv


def get_weather_description(city, date):
    
    # load_dotenv()
    
    # Obtém a chave API do OpenWeatherMap a partir das configurações do Django ou variável de ambiente
    # api_key = os.getenv('OPENWEATHERMAP_API_KEY')
    
    # @TODO: remover a chave de api
    
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid=c7f48ba7775040a6dee7d27670eb2553&units=metric&lang=pt_br"

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises an exception for 4xx/5xx responses
    except requests.RequestException as e:
        return f"Erro ao acessar a API do OpenWeatherMap: {e}"

    forecasts = response.json().get('list', [])
    target_date = datetime.strptime(date, '%Y-%m-%d').date()
    for forecast in forecasts:
        forecast_date = datetime.fromtimestamp(forecast['dt']).date()
        if forecast_date == target_date:
            description = forecast['weather'][0]['description']
            temperature = forecast['main']['temp']
            return f"{description}, {temperature}°C"

    return "Previsão do tempo não encontrada para a data especificada."



# Exemplo de uso
# city = "Maricá"
# date = "2024-07-07"  # Formato AAAA-MM-DD
# print(get_weather_description(city, date))
