from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
import os
from datetime import datetime
from decouple import config
import requests
import qrcode
# import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

def get_weather_description(city, date):
    """
    Obtém a descrição do clima e a temperatura para uma cidade e data específicas usando a API do OpenWeatherMap.

    Parâmetros:
    city (str): Nome da cidade para a qual a previsão do tempo é solicitada.
    date (str): Data para a qual a previsão do tempo é solicitada, no formato 'YYYY-MM-DD'.

    Retorna:
    str: Descrição do clima e temperatura em graus Celsius para a data especificada, ou uma mensagem de erro se a previsão não for encontrada ou se ocorrer um erro ao acessar a API.

    Exceções:
    requests.RequestException: Lançada se ocorrer um erro ao acessar a API do OpenWeatherMap.

    Exemplo:
    >>> get_weather_description("São Paulo", "2023-10-01")
    'céu limpo, 25°C'
    """


    api_key = config('OPENWEATHERMAP_API_KEY')

    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric&lang=pt_br"

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

# -----------------------------------------------------------------------------------------------------------------


# import random
# import string


# def gerar_codigos_unicos(prefixo, quantidade):
#     codigos = set()
#     while len(codigos) < quantidade:
#         sufixo = ''.join(random.choices(string.digits, k=16))
#         codigo = f"{prefixo}{sufixo}"
#         codigos.add(codigo)
#     return list(codigos)

def gerar_qr_code(codigo, data, responsavel, codigo_servico):
    try:
        qr_data = f"Responsável: {responsavel}\nData da coleta: {data}\nCódigo de Serviço: {codigo_servico}"
        qr = qrcode.make(qr_data)
        qr_path = os.path.join(
            '/home/marcus/projects/LAGUNA/media/tmp/', f"qr_{codigo}.png")
        try:
            qr.save(qr_path)
        except Exception as e:
            print(f"Erro ao salvar QR Code: {e}")
            return None
        return qr_path
    except Exception as e:
        print(f"Erro ao gerar QR Code: {e}")
        return None


def adicionar_etiqueta(c, qr_path, codigo, data, responsavel, x, y):
    try:
        c.drawImage(qr_path, x, y, width=20*mm, height=20*mm)
        c.drawString(x + 25*mm, y + 15*mm, f"Código: {codigo}")
        c.drawString(x + 25*mm, y + 7*mm, f"Data da coleta: {data}")
        c.drawString(x + 25*mm, y + -1*mm, f"Responsável: {responsavel}")
    except Exception as e:
        print(f"Erro ao adicionar etiqueta: {e}")


def desenhar_linhas_tracejadas(c, largura_pagina, altura_pagina, largura_etiqueta, altura_etiqueta, espacamento_x, espacamento_y):
    try:
        c.setDash(1, 2)  # Define o estilo da linha tracejada

        # Linhas verticais
        x = 30 * mm + largura_etiqueta + espacamento_x / 2
        for _ in range(1):
            c.line(x, 0, x, altura_pagina)
            x += largura_etiqueta + espacamento_x

        # Linhas horizontais
        y = altura_pagina + 5 * mm - altura_etiqueta - espacamento_y / 2
        for _ in range(8):
            c.line(0, y, largura_pagina, y)
            y -= altura_etiqueta + espacamento_y

        c.setDash()  # Reseta o estilo da linha para o padrão
    except Exception as e:
        print(f"Erro ao desenhar linhas tracejadas: {e}")


def gerar_etiquetas(codigos, data, responsavel, codigo_servico):
    try:
        largura_pagina, altura_pagina = A4
        pdf_path = os.path.join(
            '/home/marcus/projects/LAGUNA/media/pdf/', f"etiquetas_da_OS_{codigo_servico}.pdf")
        try:
            c = canvas.Canvas(pdf_path, pagesize=A4)
        except Exception as e:
            print(f"Erro ao criar canvas do PDF: {e}")
            return None

        x_inicial = 10 * mm
        y_inicial = altura_pagina - 20 * mm
        largura_etiqueta = 50 * mm
        altura_etiqueta = 30 * mm
        espacamento_x = 50 * mm
        espacamento_y = 3 * mm
        x = x_inicial
        y = y_inicial
        etiquetas_por_pagina = 18
        contador_etiquetas = 0
        qr_paths = []

        try:
            desenhar_linhas_tracejadas(c, largura_pagina, altura_pagina,
                                       largura_etiqueta, altura_etiqueta, espacamento_x, espacamento_y)
        except Exception as e:
            print(f"Erro ao desenhar linhas tracejadas: {e}")

        for codigo in codigos:
            for i in range(1, 4):
                codigo_modificado = f"{codigo}{i}"
                try:
                    qr_path = gerar_qr_code(
                        codigo_modificado, data, responsavel, codigo_servico)
                    if qr_path:
                        qr_paths.append(qr_path)
                        try:
                            adicionar_etiqueta(
                                c, qr_path, codigo_modificado, data, responsavel, x, y)
                        except Exception as e:
                            print(f"Erro ao adicionar etiqueta: {e}")
                        y -= altura_etiqueta + espacamento_y
                        contador_etiquetas += 1

                        if contador_etiquetas == 9:
                            x += largura_etiqueta + espacamento_x
                            y = y_inicial

                        if contador_etiquetas >= etiquetas_por_pagina:
                            c.showPage()
                            try:
                                desenhar_linhas_tracejadas(c, largura_pagina, altura_pagina,
                                                           largura_etiqueta, altura_etiqueta, espacamento_x, espacamento_y)
                            except Exception as e:
                                print(
                                    f"Erro ao desenhar linhas tracejadas em nova página: {e}")
                            x = x_inicial
                            y = y_inicial
                            contador_etiquetas = 0
                except Exception as e:
                    print(f"Erro ao gerar QR Code ou adicionar etiqueta: {e}")

        try:
            c.save()
        except Exception as e:
            print(f"Erro ao salvar o PDF: {e}")

        for path in qr_paths:
            try:
                os.remove(path)
            except OSError as e:
                print(f"Erro ao remover o arquivo {path}: {e}")
        return pdf_path
    except Exception as e:
        print(f"Erro ao gerar etiquetas: {e}")
        return None
# from simal.models import *

# codigos = Campo.objects.get(id="BIO20240802125946")

# Exemplo de uso
# codigos = gerar_codigos_unicos("BIO", 35)
# data = "08/08/2024"
# responsavel = "Samuel"
# codigo_servico = "BIO20240803142052"
# gerar_etiquetas(codigos, data, responsavel, codigo_servico)
