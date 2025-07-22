## Codigo usado para gerar novas medidas de dbo a partir de abril de 2025, pode ser usado em outras medidas tbm

from simal.models import TabColeta, TabAmostra, TabEnvio, TabMedida, TabProdxparam, TabFrasco, TabPonto
from django.contrib.auth.models import User
from datetime import date
from django.db import transaction

# --- Configurações ---
id_do_prodxparam_a_adicionar = 24
# Sabemos que o TabProdxparam 24 está ligado ao TabFrasco 1
id_do_frasco_do_prodxparam = 1
data_inicio_filtro = date(2024, 4, 1)
# ID do usuário que está realizando a operação (necessário para TabMedida.save())
# Substitua pelo ID de um usuário real ou None se não for registrar o usuário na criação da medida.
id_usuario_operacao = 1 # Exemplo, substitua!

# --- Lógica ---
try:
    usuario_operacao = User.objects.get(id=id_usuario_operacao)
except User.DoesNotExist:
    print(f"ERRO: Usuário com ID {id_usuario_operacao} não encontrado. Abortando.")
    # Decide o que fazer aqui: raise error, or set usuario_operacao = None if your save method allows it
    raise # Ou defina usuario_operacao = None e ajuste o TabMedida.save()

try:
    prodxparam_obj = TabProdxparam.objects.get(id=id_do_prodxparam_a_adicionar)
    if prodxparam_obj.id_frasco_id != id_do_frasco_do_prodxparam:
        print(f"AVISO: O TabProdxparam ID {prodxparam_obj.id} está ligado ao frasco ID {prodxparam_obj.id_frasco_id}, mas estamos esperando o frasco ID {id_do_frasco_do_prodxparam}. Verifique a lógica.")
        # Você pode decidir parar aqui se for uma inconsistência crítica
except TabProdxparam.DoesNotExist:
    print(f"ERRO: TabProdxparam com ID {id_do_prodxparam_a_adicionar} não encontrado. Abortando.")
    raise

try:
    frasco_obj = TabFrasco.objects.get(id=id_do_frasco_do_prodxparam)
except TabFrasco.DoesNotExist:
    print(f"ERRO: TabFrasco com ID {id_do_frasco_do_prodxparam} não encontrado. Abortando.")
    raise

coletas_relevantes = TabColeta.objects.filter(data__gte=data_inicio_filtro)
print(f"Encontradas {coletas_relevantes.count()} coletas desde {data_inicio_filtro}.")

medidas_criadas_count = 0
amostras_criadas_count = 0
envios_criados_count = 0
medidas_ja_existiam_count = 0

with transaction.atomic(): # Garante que todas as operações sejam feitas ou nenhuma
    for coleta in coletas_relevantes:
        print(f"Processando Coleta ID: {coleta.id}, OS: {coleta.ordem_servico}")
        # Para cada coleta, precisamos considerar todos os pontos ativos do setor da coleta
        # para criar/verificar amostras com o frasco do prodxparam.
        pontos_do_setor = TabPonto.objects.filter(id_setor=coleta.id_setor, status=True)

        if not pontos_do_setor.exists():
            print(f"  - Nenhum ponto ativo encontrado para o setor {coleta.id_setor} da coleta {coleta.id}.")
            continue

        for ponto in pontos_do_setor:
            # 1. Garante que a TabAmostra exista para esta coleta, ponto e frasco
            amostra, amostra_created = TabAmostra.objects.get_or_create(
                id_coleta=coleta,
                id_ponto=ponto,
                id_frasco=frasco_obj, # Usando o frasco_obj obtido anteriormente
                defaults={
                    'etiqueta': f"{coleta.ordem_servico}{str(ponto.id).zfill(3)}{str(frasco_obj.id).zfill(2)}"
                }
            )
            if amostra_created:
                amostras_criadas_count += 1
                print(f"    - Amostra criada para Ponto ID {ponto.id}, Frasco ID {frasco_obj.id}")

            # 2. Garante que o TabEnvio exista para esta amostra
            envio, envio_created = TabEnvio.objects.get_or_create(id_amostra=amostra)
            if envio_created:
                envios_criados_count += 1
                print(f"      - Envio criado para Amostra ID {amostra.id}")

            # 3. Cria a TabMedida se não existir
            medida_existente = TabMedida.objects.filter(
                id_envio=envio,
                id_pp=prodxparam_obj
            ).exists()

            if not medida_existente:
                # Seu TabMedida.save() customizado espera um argumento 'usuario'
                nova_medida = TabMedida(id_envio=envio, id_pp=prodxparam_obj)
                nova_medida.save(usuario=usuario_operacao) # Passando o usuário
                medidas_criadas_count += 1
                print(f"        - Medida para DBO5 (ID {prodxparam_obj.id}) criada para Envio ID {envio.id}")
            else:
                medidas_ja_existiam_count += 1
                # print(f"        - Medida para DBO5 (ID {prodxparam_obj.id}) já existe para Envio ID {envio.id}")

print("\n--- Resumo da Operação ---")
print(f"Coletas processadas: {coletas_relevantes.count()}")
print(f"Novas Amostras criadas: {amostras_criadas_count}")
print(f"Novos Envios criados: {envios_criados_count}")
print(f"Novas Medidas (DBO5) criadas: {medidas_criadas_count}")
print(f"Medidas (DBO5) que já existiam: {medidas_ja_existiam_count}")
