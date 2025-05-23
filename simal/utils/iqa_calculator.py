import math
import numpy as np

def qi_ecoli(ecoli):
    try:
        if not isinstance(ecoli, (int, float)) or ecoli < 0:
            return None
        if ecoli >= 100000:
            return 3
        elif ecoli <= 0:
            return None	
        elif ecoli <= 10:
            return max(0, 100 - 33 * math.log10(max(0.000001, ecoli)))
        elif ecoli >= 5:
            log_value = math.log10(max(0.000001, ecoli))
            return max(0, 100 - 37.2 * log_value + 3.60743 * (log_value ** 2))
        else:
            return 3
    except Exception as e:
        return None

def qi_dbo(dbo):
    if dbo == 0:
        return 100
    qi_calculado = -30.1 * math.log(dbo) + 103.45
    if qi_calculado > 100:
        return 100
    elif dbo >= 30:
        return 2
    return qi_calculado

def qi_fosfato(fosfato):
    if fosfato >= 9.6:
        return 1
    elif fosfato < 0.5:
        return 20
    return 46 - 19.8 * math.log(fosfato)

def qi_nitrogenio(nitrogenio):
    if nitrogenio < 0.79:
        return 100
    elif nitrogenio >= 100:
        return 1
    return -20.8 * math.log(nitrogenio) + 93.092

def qi_od(od):
    if od > 140:
        return 42
    elif od < 103:
        return 100 * math.exp(-((od - 100) ** 2) / (2 * (0.025**2)))
    return 134 - 0.142 * od - 0.00181 * (od**2)

def qi_ph(ph):
    return 93 * math.exp(-(((ph - 7.5) ** 2) / (2 * (0.652**2))))

def qi_tds(tds):
    if tds > 500:
        return 32
    elif tds <= 60:
        return 80.4 + 0.336 * tds - 0.00322 * (tds**2)
    return 94.7 - 0.078 * tds - 0.0000954 * (tds**2)

def qi_turbidez(turbidez):
    if turbidez < 10:
        return 99.8 - 3.61 * turbidez + 0.0901 * (turbidez**2)
    elif turbidez < 20:
        return 107 - 15.2 * np.log(turbidez) - (-10 + turbidez) * 0.1
    elif turbidez < 100:
        return -26.45 * np.log(turbidez) + 140
    return 5

def calculate_iqa(dados_ponto):
    pesos = {
        "OD": 0.17,
        "Escherichia coli": 0.15,
        "pH": 0.12, 
        "DBOs": 0.10,
        "Temperatura": 0.10,
        "Nitrogênio Total": 0.10,
        "Fosfato": 0.10,
        "Turbidez": 0.08,
        "TDS": 0.08
    }

    parametros_qi = {
        "OD": (qi_od, pesos["OD"]),
        "Escherichia coli": (qi_ecoli, pesos["Escherichia coli"]),
        "DBOs": (qi_dbo, pesos["DBOs"]), 
        "Nitrogênio Total": (qi_nitrogenio, pesos["Nitrogênio Total"]),
        "Fosfato": (qi_fosfato, pesos["Fosfato"]),
        "pH": (qi_ph, pesos["pH"]),
        "Turbidez": (qi_turbidez, pesos["Turbidez"]),
        "TDS": (qi_tds, pesos["TDS"])
    }

    iqa_total = 0
    soma_pesos = 0
    qi_temperatura = 93

    for param, (func_qi, peso) in parametros_qi.items():
        valor = dados_ponto.get(param)
        if valor is not None and valor != "" and not np.isnan(valor):
            try:
                # Ensure valor is converted to float before calculations
                numeric_valor = float(valor)
                qi_value = func_qi(numeric_valor)
                if qi_value is not None:
                    iqa_total += float(qi_value) * peso
                    soma_pesos += peso
            except (ValueError, TypeError):
                # Skip this parameter if conversion fails
                continue

    # Adicionar temperatura
    iqa_total += qi_temperatura * pesos["Temperatura"]
    soma_pesos += pesos["Temperatura"]

    return iqa_total / soma_pesos if soma_pesos > 0 else None