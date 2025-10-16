import io
import csv
import json
import logging
import os
from datetime import datetime, timedelta
from threading import Thread
import pandas as pd
import plotly.express as px
from plotly.offline import plot
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import PasswordChangeForm
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.core.mail import send_mail, EmailMessage
from django.core.paginator import Paginator
from django.db import connection, transaction
from django.db.models import Q
from django.forms import inlineformset_factory, modelformset_factory
from django.http import FileResponse, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from openpyxl import Workbook
from openpyxl.utils import get_column_letter
from django.core.serializers.json import DjangoJSONEncoder
from django_tables2 import RequestConfig
from openpyxl.styles import Font, PatternFill
from django.contrib.auth.models import Group
from django.http import JsonResponse
import json
import folium
from datetime import datetime

import qrcode
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from io import BytesIO
from PIL import Image

from django_tables2 import RequestConfig
import urllib.parse
from .services import gerar_etiquetas, get_weather_description
from .tables import (
    EmailTable,
    StatusColetaTable,
    TabColetaTable,
    TopCampanhas,
    ColetaCampoTable,
    ResultadosColetaTable,
    ProgramaColetaTable,
    LaboratoriosTable,
    SetorTable,
    PontoTable,
    LocalTable,
    TipoParametroTable,
    ParametroTable,
    FrascoTable,
    EquipeTable,
    LaboratorioTable,
    ProdutoTable,
    ProdxparamTable,
    SerieClassificacaoTable,
    TipoItemChecklistColetaTable,
    ListaCampoTable,
)
from .models import (
    EmailTemplate,
    MetadadosPonto,
    TabAnexoAmostra,
    TabLogColeta,
    TabStatusColeta,
    TipoParametro,
    TabAmostra,
    TabEnvio,
    TabMedida,
    TabProdxparam,
)

from .forms import (
    CustomUserCreationForm,
    ColetaCampo,
    MetadadosCampoForm,
    ProgramaColetaForm,
    AjudaForm,
    IniciarCampanhaForm,
    ChecklistCampoForm,
    LaboratorioForm,
    AnaliseForm,
    LocaisForm,
    SetorForm,
    PontoForm,
    ParametroForm,
    UnidadeMedidaForm,
    TipoParametroForm,
    TabFrascoForm,
    TabEquipeForm,
    TabLaboratorioForm,
    TabProdutoForm,
    TabProdxParamForm,
    TabSerieClassificacaoForm,
    CadastroItemChecklistColetaForm,
    EmailForm,
    StatusColetaForm,
    DetalhesUsuarioForm,
    CadastroCampanhaForm,
    CadastroColetaForm,
    ChecklistColetaForm,
    InputFisicoQuimicoForm,
)
from .filters import *


from .models import (
    User,
    ProgramaColeta,
    ChecklistCampo,
    Campo,
    MetadadosCampo,
    Ajuda,
    Laboratorios,
    Analises,
    TabSetor,
    TabPonto,
    TabLocal,
    TabParam,
    TabFrasco,
    TabEquipe,
    TabLaboratorio,
    TabProduto,
    TabSerieClassificacao,
    TabItemChecklistColeta,
    TabChecklistColeta,
    TabColeta,
    DetalhesUsuario,
)
from django.db.models import Count
from .utils.iqa_calculator import calculate_iqa
import requests
from django.views.decorators.csrf import csrf_exempt
from openpyxl.styles import Alignment
from django.conf import settings


# ================= FUNÇÃO AUXILIAR DE ENVIO DE EMAIL =================
def enviar_email_relatorio_coleta(coleta, arquivo_excel, usuario):
    """
    Envia o relatório Excel da coleta por e-mail para o usuário logado.
    """

    if not usuario.email:
        logger.warning(
            "Usuário sem e-mail cadastrado. Não foi possível enviar o relatório.")
        return

    subject = f"Relatório Pós-Coleta - {coleta}"
    # Monta o link para a página de informações da coleta
    link_sistema = f"{settings.SITE_URL}/info_coleta/{coleta.id}"
    codigo_coleta = getattr(coleta, 'codigo_coleta', coleta.id)
    body = (
        f"Olá,\n\nSegue em anexo o relatório pós-coleta.\n\n"
        f"Código da Coleta: {codigo_coleta}\n"
        f"Acesse as informações completas da coleta neste link: {link_sistema}\n\n"
        f"Este é um e-mail automático, favor não responder."
    )
    email = EmailMessage(
        subject=subject,
        body=body,
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
        to=[usuario.email,],
    )
    email.attach(
        f"relatorio_coleta_{coleta.id}.xlsx",
        arquivo_excel.getvalue(),
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    try:
        email.send(fail_silently=False)
        logger.info(f"Relatório pós-coleta enviado para {usuario.email}.")
    except Exception as e:
        logger.error(f"Erro ao enviar relatório pós-coleta: {e}")


# ================= FUNÇÕES AUXILIARES =================
# Alteração para o card 359
def gerar_relatorio_excel_por_coleta(coleta, id_frasco=1):
    """
    Alteração para o card 359
    Função agora parametrizável: exporta dados do frasco informado (padrão: 1 - Sonda)
    Gera um arquivo Excel com todos os dados em uma única aba, incluindo o nome do ponto como coluna.
    Exporta apenas dados do frasco especificado (padrão: 1 - Sonda).
    Usa openpyxl como engine, não requer xlsxwriter.
    """
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='openpyxl')

    amostras = TabAmostra.objects.filter(id_coleta=coleta, id_frasco=id_frasco)
    dados = []
    # Alteração para o card 359: inclusão da coluna 'Série de Classificação' na exportação
    for amostra in amostras:
        ponto_nome = amostra.id_ponto.nome if amostra.id_ponto else ''
        envios = TabEnvio.objects.filter(id_amostra=amostra)
        for envio in envios:
            medidas = TabMedida.objects.filter(id_envio=envio)
            for medida in medidas:
                dados.append({
                    'Ponto': ponto_nome,
                    'Parâmetro': medida.id_pp.id_param.nome if medida.id_pp and medida.id_pp.id_param else '',
                    'Valor': medida.input_valor,
                    'Unidade': medida.id_pp.unidade if medida.id_pp else '',
                    'Série de Classificação': medida.id_pp.id_serie.nome if medida.id_pp and medida.id_pp.id_serie else '',
                    'Observação': getattr(medida, 'observacao', ''),
                    'Código Oceanus': getattr(medida, 'codigo_oceanus', ''),
                    'Data': getattr(medida, 'data_medida', ''),
                })
    df = pd.DataFrame(dados)
    df.to_excel(writer, sheet_name="Resultados", index=False)
    writer.close()
    output.seek(0)
    return output


# Configuração do logger
logger = logging.getLogger(__name__)


def check_admin(user):
    return user.is_superuser


def is_superuser(user):
    return user.is_superuser


@login_required
@user_passes_test(check_admin)
def cadastro_usuarios(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            # Redirecione para a página de usuários cadastrados
            return redirect("usuarios_cadastrados")
    else:
        form = CustomUserCreationForm()

    return render(request, "cadastro_usuarios.html", {"form": form})


@login_required
@user_passes_test(check_admin)
def editar_usuario(request, user_id):
    usuario = get_object_or_404(User, id=user_id)
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, "Usuário atualizado com sucesso.")
            return redirect("usuarios_cadastrados")
    else:
        form = CustomUserCreationForm(instance=usuario)

    return render(request, "editar_usuario.html", {"form": form, "usuario": usuario})


@login_required
@user_passes_test(check_admin)
def usuarios_cadastrados(request):
    usuarios = User.objects.all()
    return render(request, "usuarios_cadastrados.html", {"usuarios": usuarios})


def home(request):
    try:
        proxima_coleta = (
            ProgramaColeta.objects.filter(
                status_coleta__in=["Iniciada", "Programada"],
                data_coleta_campo__gte=timezone.now(),
            )
            .order_by("data_coleta_campo")
            .first()
        )
        table = TopCampanhas(ProgramaColeta.objects.all())
        RequestConfig(request, paginate={"per_page": 3}).configure(table)
        hoje = timezone.now().strftime("%d/%m/%Y")
        percentual_checklist = None
        data_coleta_proxima_formatada = None
        data_coleta_menos_um = None
        data_coleta_menos_dois = None
        weather_description = None
        weather_description_day_before = None
        weather_description_two_days_before = None
        gantt_div = None

        if (proxima_coleta):
            percentual_checklist = (
                ChecklistCampo.objects.filter(ordem_servico=proxima_coleta.id)
                .values_list("progresso", flat=True)
                .first()
            )
            data_coleta_proxima_formatada = proxima_coleta.data_coleta_campo.strftime(
                "%d/%m/%Y"
            )

            data_coleta_menos_um = (
                proxima_coleta.data_coleta_campo - timedelta(days=1)
            ).strftime("%d/%m/%Y")

            data_coleta_menos_dois = (
                proxima_coleta.data_coleta_campo - timedelta(days=2)
            ).strftime("%d/%m/%Y")

            weather_description = get_weather_description(
                "Maricá", proxima_coleta.data_coleta_campo.strftime("%Y-%m-%d")
            )
            weather_description_day_before = get_weather_description(
                "Maricá",
                (proxima_coleta.data_coleta_campo - timedelta(days=1)).strftime(
                    "%Y-%m-%d"
                ),
            )
            weather_description_two_days_before = get_weather_description(
                "Maricá",
                (proxima_coleta.data_coleta_campo - timedelta(days=2)).strftime(
                    "%Y-%m-%d"
                ),
            )

            checklist = ChecklistCampo.objects.filter(
                ordem_servico=proxima_coleta
            ).first()

            if checklist:
                dados_gantt = [
                    dict(
                        Tarefa="Coleta de Campo",
                        Inicio=proxima_coleta.data_coleta_campo,
                        Termino=proxima_coleta.data_coleta_campo,
                        Cor="#2ca02c" if checklist.previsao_tempo else "#d62728",
                    ),  # Verde moderno se verdadeiro, vermelho moderno se falso
                    dict(
                        Tarefa="Verificar previsão do tempo",
                        Inicio=proxima_coleta.data_programacao,
                        Termino=proxima_coleta.data_check_forecast,
                        Cor="#2ca02c" if checklist.previsao_tempo else "#d62728",
                    ),
                    dict(
                        Tarefa="Avisar Laboratórios",
                        Inicio=proxima_coleta.data_check_lab,
                        Termino=proxima_coleta.data_check_lab +
                        timedelta(days=2),
                        Cor="#2ca02c" if checklist.avisar_labs else "#d62728",
                    ),
                    dict(
                        Tarefa="Reservar Carro e barco",
                        Inicio=proxima_coleta.data_check_car,
                        Termino=proxima_coleta.data_check_car +
                        timedelta(days=2),
                        Cor="#2ca02c" if checklist.reservar_carro else "#d62728",
                    ),
                    dict(
                        Tarefa="Checar Equipamentos",
                        Inicio=proxima_coleta.data_check_material,
                        Termino=proxima_coleta.data_check_material +
                        timedelta(days=3),
                        Cor="#2ca02c" if checklist.separar_equipamentos else "#d62728",
                    ),
                    dict(
                        Tarefa="Etiquetar frascos",
                        Inicio=proxima_coleta.data_check_material +
                        timedelta(days=3),
                        Termino=proxima_coleta.data_check_material +
                        timedelta(days=3),
                        Cor="#2ca02c" if checklist.conferir_equipamentos else "#d62728",
                    ),
                    dict(
                        Tarefa="Comprar gelo",
                        Inicio=proxima_coleta.data_check_material +
                        timedelta(days=3),
                        Termino=proxima_coleta.data_check_material +
                        timedelta(days=3),
                        Cor="#2ca02c" if checklist.conferir_equipamentos else "#d62728",
                    ),
                ]
            else:
                dados_gantt = [
                    dict(
                        Tarefa="Coleta de Campo",
                        Inicio=proxima_coleta.data_coleta_campo,
                        Termino=proxima_coleta.data_coleta_campo,
                        Cor="#2ca02c",
                    ),  # Verde moderno para tarefas já feitas
                    dict(
                        Tarefa="Verificar previsão do tempo",
                        Inicio=proxima_coleta.data_programacao,
                        Termino=proxima_coleta.data_check_forecast,
                        Cor="#2ca02c",
                    ),  # Verde moderno para tarefas já feitas
                    dict(
                        Tarefa="Contatar Laboratórios",
                        Inicio=proxima_coleta.data_check_lab,
                        Termino=proxima_coleta.data_check_lab +
                        timedelta(days=2),
                        Cor="#2ca02c",
                    ),  # Verde moderno para tarefas já feitas
                    dict(
                        Tarefa="Reservar Carro",
                        Inicio=proxima_coleta.data_check_car,
                        Termino=proxima_coleta.data_check_car +
                        timedelta(days=2),
                        Cor="#2ca02c",
                    ),  # Verde moderno para tarefas já feitas
                    dict(
                        Tarefa="Preparar Equipamentos",
                        Inicio=proxima_coleta.data_check_material,
                        Termino=proxima_coleta.data_check_material +
                        timedelta(days=3),
                        Cor="#2ca02c",
                    ),  # Verde moderno para tarefas já feitas
                    dict(
                        Tarefa="Etiquetar frascos",
                        Inicio=proxima_coleta.data_check_material,
                        Termino=proxima_coleta.data_check_material +
                        timedelta(days=3),
                        Cor="#2ca02c",
                    ),  # Verde moderno para tarefas já feitas
                    dict(
                        Tarefa="Comprar gelo",
                        Inicio=proxima_coleta.data_coleta_campo,
                        Termino=proxima_coleta.data_coleta_campo,
                        Cor="#2ca02c",
                    ),  # Verde moderno para tarefas já feitas
                ]

            # Adiciona a tarefa "Programação" com a cor azul
            dados_gantt.append(
                dict(
                    Tarefa="Programação",
                    Inicio=proxima_coleta.data_programacao,
                    Termino=proxima_coleta.data_coleta_campo,
                    Cor="#2ca02c",
                )
            )

            df = pd.DataFrame(dados_gantt)

            # Converte as colunas para datetime
            df["Inicio"] = pd.to_datetime(df["Inicio"])
            df["Termino"] = pd.to_datetime(df["Termino"])

            # Calcula a duração
            df["Duracao"] = (df["Termino"] - df["Inicio"]).dt.total_seconds()

            # Ordena o DataFrame pela duração em ordem decrescente
            df = df.sort_values(by="Duracao", ascending=True)

            fig = px.timeline(
                df, x_start="Inicio", x_end="Termino", y="Tarefa", color="Cor"
            )

            # Adiciona bolinhas para tarefas com duração zero
            for i, row in df.iterrows():
                if row["Duracao"] == 0:
                    fig.add_scatter(
                        x=[row["Inicio"]],
                        y=[row["Tarefa"]],
                        mode="markers",
                        marker=dict(size=20, color="#1f77b4"),  # Azul moderno
                        name=row["Tarefa"],
                    )

            # fig.update_yaxes(autorange="reversed")

            # Remove a legenda
            fig.update_layout(showlegend=False, template="simple_white")

            # Configura o locale para português e coloca as datas na parte inferior
            fig.update_layout(
                xaxis=dict(
                    side="top",
                    tickformat="%d/%m/%Y",
                    tickformatstops=[
                        dict(
                            dtickrange=[None, 86400000], value="%d/%m/%Y"
                        ),  # daily ticks
                        # larger than daily ticks
                        dict(dtickrange=[86400000, None], value="%d/%m/%Y"),
                    ],
                ),
                height=None,  # Remove a altura fixa
                width=None,  # Remove a largura fixa
                # Ajuste as margens conforme necessário
                margin=dict(l=20, r=20, t=20, b=20),
            )

            # Torna o gráfico responsivo
            fig.update_layout(autosize=True)

            gantt_div = plot(fig, output_type="div")

        campanhas = ProgramaColeta.objects.all()
        eventos = []
        for campanha in campanhas:
            evento = {
                "title": campanha.ordem_servico,
                "start": campanha.data_coleta_campo.isoformat(),
                "end": campanha.data_coleta_campo.isoformat(),
                "url": f"/checklist_campanha/{campanha.ordem_servico}/",
            }
            if campanha.status_coleta == "Programada":
                evento["className"] = "evento-programado"
            elif campanha.status_coleta == "Iniciada":
                evento["className"] = "evento-iniciado"
            elif campanha.status_coleta == "Coleta realizada":
                evento["className"] = "evento-realizado"
            elif campanha.status_coleta == "Cancelada":
                evento["className"] = "evento-cancelado"
            eventos.append(evento)

        context = {
            "data_coleta_proxima_formatada": data_coleta_proxima_formatada,
            "data_coleta_formatada_menos_um": data_coleta_menos_um,
            "data_coleta_formatada_menos_dois": data_coleta_menos_dois,
            "hoje": hoje,
            "weather_description": weather_description,
            "weather_description_day_before": weather_description_day_before,
            "weather_description_two_days_before": weather_description_two_days_before,
            "status_coleta": proxima_coleta.status_coleta if proxima_coleta else None,
            "local_coleta": proxima_coleta.local_coleta if proxima_coleta else None,
            "percentual_checklist": percentual_checklist if percentual_checklist else 0,
            "ordem_servico": proxima_coleta.ordem_servico if proxima_coleta else None,
            "table_top3": table,
            "eventos": json.dumps(eventos),
            "gantt_div": gantt_div,
        }
        return render(request, "home.html", context)
    except ProgramaColeta.DoesNotExist:
        return HttpResponse("Nenhum programa de coleta encontrado.", status=404)
    except Exception as e:
        return HttpResponse(f"Erro ao carregar a página: {str(e)}", status=500)


@login_required
def coleta(request):
    if request.method == "POST":
        form = ColetaCampo(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("lista_coleta")

    else:
        form = ColetaCampo()
    return render(request, "coleta/coleta.html", {"form": form})


@login_required
def atualizar_coleta(request, id):
    coleta = get_object_or_404(Campo, id=id)
    pontos_coleta = Campo.objects.filter(ordem_servico=coleta.ordem_servico).order_by(
        "ponto"
    )

    form_data = {field: getattr(coleta, field)
                 for field in ColetaCampo.base_fields}
    form_data["hora_inicio"] = timezone.now().strftime("%H:%M")
    form = ColetaCampo(initial=form_data)

    if request.method == "POST":
        post_data = request.POST.copy()
        post_data["hora_fim"] = timezone.now().strftime("%H:%M")
        form = ColetaCampo(post_data, request.FILES)

        if form.is_valid():
            for field, value in form.cleaned_data.items():
                setattr(coleta, field, value)
            coleta.save()
            messages.success(request, "Dados atualizados com sucesso!")

            # Verifica se todos os pontos foram coletados
            todos_pontos_preenchidos = (
                not Campo.objects.filter(ordem_servico=coleta.ordem_servico)
                .exclude(status_form="Preenchido")
                .exists()
            )

            if todos_pontos_preenchidos:
                campanha = ProgramaColeta.objects.get(
                    id=coleta.ordem_servico.id)
                campanha.status_coleta = "Coleta realizada"
                campanha.save()

            pontos_coleta_list = list(pontos_coleta)
            index_atual = pontos_coleta_list.index(coleta)

            while not todos_pontos_preenchidos:
                index_atual = (index_atual + 1) % len(pontos_coleta_list)
                proximo_ponto = pontos_coleta_list[index_atual]
                if proximo_ponto.status_form != "Preenchido":
                    return redirect(
                        reverse("atualizar_coleta", args=[proximo_ponto.id])
                    )

            return redirect("lista_coleta", ordem_servico=coleta.ordem_servico.id)
        else:
            pass  # Mantenha o formulário com erros para exibição

    context = {
        "form": form,
        "codigo_coleta": coleta.codigo_coleta,
        "coleta_id": coleta.id,
        "ponto": coleta.ponto,
        "pontos_coleta": pontos_coleta,
        "ordem_servico_id": coleta.ordem_servico.id,
    }
    return render(request, "coleta/coleta.html", context)


@login_required
def meta_coleta(request, id):
    coleta = get_object_or_404(Campo, id=id)

    # Verifica se já existe um registro de metadados para o código de coleta
    metadados, created = MetadadosCampo.objects.get_or_create(
        codigo_coleta=coleta)

    if created:
        messages.info(
            request,
            "Novo registro de metadados criado para o código de coleta fornecido.",
        )

    if request.method == "POST":
        form = MetadadosCampoForm(request.POST, instance=metadados)
        if form.is_valid():
            form.save()
            # Redireciona para a página anterior
            return redirect(reverse("atualizar_coleta", args=[coleta.id]))
    else:
        form = MetadadosCampoForm(instance=metadados)

    context = {
        "form": form,
        "codigo_coleta": coleta.codigo_coleta,
        "coleta_id": coleta.id,
        "ponto": coleta.ponto,
        "ordem_servico_id": coleta.ordem_servico.id,
        "ordem_servico": coleta.ordem_servico,
    }

    return render(request, "coleta/meta_coleta.html", context)


@login_required
@user_passes_test(check_admin)
def deletar_coleta(request, id):
    coleta = ColetaCampo.objects.get(id=id)
    coleta.delete()
    return redirect("lista_coleta")


@login_required
def lista_coleta(request, ordem_servico=None):
    # filtro = CampoFilter(request.GET, queryset=Campo.objects.all())
    ordem_servico = ProgramaColeta.objects.get(id=ordem_servico)
    responsavel = ProgramaColeta.objects.get(id=ordem_servico.id).usuario
    filtro = CampoFilter(
        request.GET, queryset=Campo.objects.filter(
            ordem_servico_id=ordem_servico)
    )
    table = ColetaCampoTable(filtro.qs)
    RequestConfig(request, paginate={"per_page": 25}).configure(table)
    return render(
        request,
        "coleta/lista_coleta.html",
        {
            "table_campo": table,
            "filtro": filtro,
            "ordem_servico": ordem_servico,
            "responsavel": responsavel,
        },
    )


@login_required
def resultados(request):
    filtro = ResultadosColetaFilter(request.GET, queryset=Campo.objects.all())
    table = ResultadosColetaTable(filtro.qs)
    RequestConfig(request, paginate={"per_page": 25}).configure(table)
    return render(
        request,
        "coleta/resultados_coleta.html",
        {
            "table_campo": table,
            "filtro": filtro,
        },
    )


@login_required
def coletas_agendas(request):
    filtro = ProgramaColetaFilter(
        request.GET, queryset=ProgramaColeta.objects.all())
    table = ProgramaColetaTable(filtro.qs)
    RequestConfig(request, paginate={"per_page": 25}).configure(table)
    return render(
        request,
        "coleta/coletas_agendas.html",
        {
            "table_agenda_coleta": table,
            "filtro": filtro,
        },
    )


@login_required
def agenda_coleta(request):
    if request.method == "POST":
        form = ProgramaColetaForm(request.POST)
        if form.is_valid():
            programa_coleta = ProgramaColeta()

            # Atribui os dados do formulário aos campos do modelo
            programa_coleta.data_coleta_campo = form.cleaned_data["data_coleta_campo"]
            # programa_coleta.data_fim_coleta_campo = form.cleaned_data['data_fim_coleta_campo']
            programa_coleta.equipe_coleta = form.cleaned_data["equipe_coleta"]
            # programa_coleta.laboratorio = form.cleaned_data['laboratorio']
            # programa_coleta.solicitante = form.cleaned_data['solicitante']
            programa_coleta.local_coleta = form.cleaned_data["local_coleta"]
            programa_coleta.observacoes = form.cleaned_data["observacoes"]
            programa_coleta.status_coleta = "Programada"
            # Salva o modelo no banco de dados
            programa_coleta.save(usuario=request.user)

            messages.success(request, "Programação realizada com sucesso!")
            return redirect("coletas_agendas")
    else:
        form = ProgramaColetaForm()

    return render(request, "coleta/agendar_coleta.html", {"form": form})


@login_required
def atualizar_programacao(request, id):
    cache_key = f"programacao_{id}"
    programacao = cache.get(cache_key)

    if not programacao:
        programacao = get_object_or_404(ProgramaColeta, id=id)
        cache.set(cache_key, programacao, timeout=3600)

    # Verifica se o status da programação é 'Cancelada' ou se a rota é True
    if programacao.status_coleta == "Cancelada" or programacao.rota:
        messages.warning(
            request, "Não é possível alterar campanhas canceladas ou com rota definida."
        )
        return redirect("coletas_agendas")

    if request.method == "POST":
        form = ProgramaColetaForm(request.POST)
        if form.is_valid():
            for field, value in form.cleaned_data.items():
                setattr(programacao, field, value)
            programacao.save()
            cache.set(cache_key, programacao, timeout=3600)
            messages.success(request, "Dados atualizados com sucesso!")
            return redirect("coletas_agendas")
        else:
            print(form.errors)
    else:
        form_data = {
            field.name: getattr(programacao, field.name)
            for field in ProgramaColeta._meta.fields
        }
        for date_field in ["data_coleta_campo"]:
            if date_field in form_data and form_data[date_field]:
                form_data[date_field] = form_data[date_field].strftime(
                    "%Y-%m-%d")
        form = ProgramaColetaForm(initial=form_data)
    return render(request, "coleta/agendar_coleta.html", {"form": form})


@login_required
@user_passes_test(is_superuser, login_url="coletas_agendas")
def deletar_programacao(request, id):
    """
    Deleta a programação de coleta com base no ID fornecido.

    Args:
        request (HttpRequest): O objeto HttpRequest que contém os dados da requisição.
        id (int): O ID da programação de coleta a ser deletada.

    Returns:
        HttpResponse: O objeto HttpResponse que redireciona para a página 'coletas_agendas'
                      em caso de sucesso na deleção dos dados.

    Raises:
        Http404: Se a programação de coleta com o ID fornecido não existir.
        PermissionDenied: Se o usuário não for um superusuário.

    """
    if not request.user.is_superuser:
        messages.warning(
            request, "Você não tem permissão para executar esta ação.")
        raise PermissionDenied

    programacao = get_object_or_404(ProgramaColeta, id=id)
    programacao.delete()
    messages.success(request, "Programação de coleta deletada com sucesso!")
    return redirect("coletas_agendas")


def cancelar_programacao(request, id):
    """
    Cancela a programação de coleta com base no ID fornecido, a menos que a coleta já tenha sido realizada ou iniciada.

    Args:
        request (HttpRequest): O objeto HttpRequest que contém os dados da requisição.
        id (int): O ID da programação de coleta a ser cancelada.

    Returns:
        HttpResponse: O objeto HttpResponse que redireciona para a página 'coletas_agendas'
                      em caso de sucesso no cancelamento dos dados, ou permanece na mesma página
                      com uma mensagem de aviso se a coleta já foi realizada ou iniciada.

    Raises:
        Http404: Se a programação de coleta com o ID fornecido não existir.

    """
    programacao = get_object_or_404(ProgramaColeta, id=id)
    if programacao.status_coleta in ["Coleta realizada", "Iniciada"]:
        messages.warning(
            request,
            "Não é possível cancelar uma coleta que já foi iniciada ou realizada.",
        )
        return redirect("coletas_agendas")
    else:
        programacao.status_coleta = "Cancelada"
        programacao.save()
        messages.success(
            request, "Programação de coleta cancelada com sucesso!")
        return redirect("coletas_agendas")


# pagina de ajuda
@login_required
def ajuda(request):
    """
    Função de visualização para a página de ajuda.

    Esta função é decorada com @login_required para garantir que apenas usuários autenticados possam acessar a página de ajuda.

    Args:
        request (HttpRequest): O objeto HttpRequest que contém os detalhes da solicitação HTTP.

    Returns:
        HttpResponse: O objeto HttpResponse que representa a resposta HTTP para a solicitação.

    Raises:
        None
    """
    if request.method == "POST":
        form = AjudaForm(request.POST, request.FILES)
        if form.is_valid():
            nova_ajuda = Ajuda()  # Model
            nova_ajuda.nome = form.cleaned_data["nome"]
            nova_ajuda.email = form.cleaned_data["email"]
            nova_ajuda.pergunta = form.cleaned_data["pergunta"]

            # Salvar o anexo se estiver presente
            if form.cleaned_data.get("anexo"):
                nova_ajuda.anexo = form.cleaned_data["anexo"]

            nova_ajuda.save()

            # Enviar e-mail para o administrador
            subject_admin = "Nova solicitação de ajuda"
            message_admin = f"Nome: {nova_ajuda.nome}\nEmail: {nova_ajuda.email}\nPergunta: {nova_ajuda.pergunta}"
            recipient_list_admin = [settings.EMAIL_HOST_USER]
            send_mail(
                subject_admin,
                message_admin,
                settings.EMAIL_HOST_USER,
                recipient_list_admin,
            )

            # Enviar e-mail para o usuário
            subject_user = "Confirmação de solicitação de ajuda"
            message_user = f"Olá {nova_ajuda.nome},\n\nVocê está recebendo este e-mail porque fez uma solicitação de ajuda no sistema LAGUNA.\n\nPergunta: {nova_ajuda.pergunta}\n\nAtenciosamente,\nEquipe LAGUNA"
            recipient_list_user = [nova_ajuda.email]
            send_mail(
                subject_user,
                message_user,
                settings.EMAIL_HOST_USER,
                recipient_list_user,
            )

            messages.success(
                request, "Sua solicitação de ajuda foi enviada com sucesso!"
            )

            return redirect("ajuda")
    else:
        form = AjudaForm()

    return render(request, "ajuda.html", {"form": form})


# View para pagina de inicio de campanha


@login_required
def iniciar_campanha(request, ordem_servico=None):
    # Obtém o valor de ordem_servico da URL, se houver
    ordem_servico = request.GET.get("ordem_servico", None)
    filtro = {}
    if ordem_servico:
        filtro["ordem_servico_inicial"] = ordem_servico

    if request.method == "POST":
        form = IniciarCampanhaForm(request.POST, **filtro)
        if form.is_valid():
            ordem_servico = form.cleaned_data["ordem_servico"]
            redirect_url = (
                reverse("checklist_campanha")
                + f"?ordem_servico={ordem_servico.ordem_servico}"
            )
            return redirect(redirect_url)
    else:
        form = IniciarCampanhaForm(**filtro)

    return render(request, "coleta/iniciar_campanha.html", {"form": form})


@login_required
def checklist_campanha(request, ordem_servico=None):
    ordem_servico_selecionada = request.GET.get("ordem_servico", ordem_servico)
    campanha = get_object_or_404(
        ProgramaColeta, ordem_servico=ordem_servico_selecionada
    )
    if campanha.status_coleta == "Cancelada":
        messages.warning(
            request, "Não é possível iniciar uma campanha cancelada")
        return redirect("coletas_agendas")
    try:
        checklist_campanha = ChecklistCampo.objects.get(ordem_servico=campanha)
    except ChecklistCampo.DoesNotExist:
        checklist_campanha = None

    form = ChecklistCampoForm(
        request.POST or None,
        instance=checklist_campanha,
        ordem_servico_selecionada=ordem_servico_selecionada,
    )
    if request.method == "POST" and form.is_valid():
        checklist_campanha, created = ChecklistCampo.objects.get_or_create(
            ordem_servico=campanha,
            defaults={
                campo: form.cleaned_data[campo]
                for campo in (
                    (
                        "previsao_tempo",
                        "data_previsao_tempo",
                        "observacao_previsao_tempo",
                        "avisar_labs",
                        "data_avisar_labs",
                        "observacao_avisar_labs",
                        "reservar_carro",
                        "observacao_reservar_carro",
                        "data_reservar_carro",
                        "reservar_barco",
                        "observacao_reservar_barco",
                        "data_reservar_barco",
                        "separar_equipamentos",
                        "data_separar_equipamentos",
                        "observacao_separar_equipamentos",
                        "conferir_equipamentos",
                        "data_conferir_equipamentos",
                        "observacao_conferir_equipamentos",
                        "comprar_gelo",
                        "data_comprar_gelo",
                        "observacao_comprar_gelo",
                        "etiquetar_frascos",
                        "data_etiquetar_frascos",
                        "observacao_etiquetar_frascos",
                    )
                )
            },
        )
        if not created:
            for campo in (
                "previsao_tempo",
                "data_previsao_tempo",
                "observacao_previsao_tempo",
                "avisar_labs",
                "data_avisar_labs",
                "observacao_avisar_labs",
                "reservar_carro",
                "observacao_reservar_carro",
                "data_reservar_carro",
                "reservar_barco",
                "observacao_reservar_barco",
                "data_reservar_barco",
                "separar_equipamentos",
                "data_separar_equipamentos",
                "observacao_separar_equipamentos",
                "conferir_equipamentos",
                "data_conferir_equipamentos",
                "observacao_conferir_equipamentos",
                "comprar_gelo",
                "data_comprar_gelo",
                "observacao_comprar_gelo",
                "etiquetar_frascos",
                "data_etiquetar_frascos",
                "observacao_etiquetar_frascos",
            ):
                setattr(checklist_campanha, campo, form.cleaned_data[campo])
            checklist_campanha.save(usuario=request.user)
        if campanha.rota:
            return redirect("lista_coleta", ordem_servico=campanha.id)
        else:
            return redirect("checklist_campanha", ordem_servico=campanha.ordem_servico)

    if campanha.status_coleta == "Programada":
        campanha.status_coleta = "Iniciada"

    campanha.save()

    data = campanha.data_coleta_campo
    previsao_tempo = get_weather_description(
        "Maricá", data.strftime("%Y-%m-%d"))

    context = {
        "form": form,
        "checklist_campanha": checklist_campanha,
        "ordem_servico": campanha.ordem_servico,
        "previsao_tempo": previsao_tempo,
        "campanha": campanha,
    }
    return render(request, "coleta/checklist_campanha.html", context)


@login_required
def gerar_rota_campanha(request, ordem_servico=None):
    ordem_servico = request.GET.get("ordem_servico", ordem_servico)
    campanha = None
    if ordem_servico:
        campanha = get_object_or_404(
            ProgramaColeta, ordem_servico=ordem_servico)

    previsao_tempo = None
    pontos_coleta = []
    if campanha:
        data = campanha.data_coleta_campo
        previsao_tempo = get_weather_description(
            "Maricá", data.strftime("%Y-%m-%d"))

        local_campanha = campanha.local_coleta
        setor_local = TabSetor.objects.get(nome=local_campanha)
        # Modificação aqui - adiciona filtro status=True
        pontos_coleta = TabPonto.objects.filter(
            id_setor=setor_local,
            status=True,  # Apenas pontos ativos
        )

        programa_coleta_instance = get_object_or_404(
            ProgramaColeta, ordem_servico=ordem_servico
        )

        for ponto in pontos_coleta:
            campo = Campo()
            campo.ordem_servico = programa_coleta_instance
            campo.ponto = str(ponto.nome)
            campo.codigo_coleta = ordem_servico + str(ponto.nome)
            campo.clima = previsao_tempo
            campo.save()

        campanha.rota = True
        campanha.save()

    return redirect("checklist_campanha", ordem_servico=ordem_servico)


def etiquetagem(request, ordem_servico=None):
    ordem_servico = request.GET.get("ordem_servico", ordem_servico)
    campanha = None
    if ordem_servico:
        campanha = get_object_or_404(
            ProgramaColeta, ordem_servico=ordem_servico)

        data = campanha.data_coleta_campo.strftime("%d/%m/%Y")
        responsavel = campanha.usuario
        codigo_servico = campanha.ordem_servico
        codigos = Campo.objects.filter(ordem_servico=campanha).values_list(
            "codigo_coleta", flat=True
        )

        if not codigos:
            messages.warning(
                request,
                "Nenhum código de coleta encontrado para a ordem de serviço fornecida.",
            )
            return redirect("checklist_campanha", ordem_servico=ordem_servico)

        pdf_path = gerar_etiquetas(codigos, data, responsavel, codigo_servico)

        # Retorna o PDF como uma resposta HTTP
        response = FileResponse(
            open(pdf_path, "rb"),
            as_attachment=True,
            filename=os.path.basename(pdf_path),
        )

        # Apaga o arquivo PDF após o download
        os.remove(pdf_path)

        return response

    return redirect("checklist_campanha", ordem_servico=ordem_servico)


@login_required
def cadastro_laboratorio(request):
    AnaliseFormSet = inlineformset_factory(
        Laboratorios, Analises, form=AnaliseForm, extra=1, fields="__all__"
    )
    if request.method == "POST":
        form = LaboratorioForm(request.POST)
        formset = AnaliseFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            laboratorio = form.save()
            formset.instance = laboratorio
            formset.save()
            return redirect("laboratorios_cadastrados")
    else:
        form = LaboratorioForm()
        formset = AnaliseFormSet()

    return render(
        request, "cadastro_laboratorio.html", {
            "form": form, "formset": formset}
    )


@login_required
def laboratorios_cadastrados(request):
    table = LaboratoriosTable(Laboratorios.objects.all())
    RequestConfig(request, paginate={"per_page": 25}).configure(table)
    return render(
        request, "laboratorios_cadastrados.html", {"table_laboratorios": table}
    )


@login_required
def atualizar_laboratorio(request, id):
    laboratorio = get_object_or_404(Laboratorios, id=id)
    AnaliseFormSet = inlineformset_factory(
        Laboratorios, Analises, form=AnaliseForm, extra=0, fields="__all__"
    )

    if request.method == "POST":
        form = LaboratorioForm(request.POST, instance=laboratorio)
        formset = AnaliseFormSet(request.POST, instance=laboratorio)

        if form.is_valid() and formset.is_valid():
            laboratorio = form.save()
            formset.instance = laboratorio
            formset.save()
            messages.success(request, "Dados atualizados com sucesso!")
            return redirect("laboratorios_cadastrados")
        else:
            print(form.errors)  # Imprime os erros de validação
            print(formset.errors)  # Imprime os erros de validação do formset
    else:
        form = LaboratorioForm(instance=laboratorio)
        formset = AnaliseFormSet(instance=laboratorio)

    return render(
        request, "cadastro_laboratorio.html", {
            "form": form, "formset": formset}
    )


def calendario_campanhas(request):
    campanhas = ProgramaColeta.objects.all()
    eventos = []

    for campanha in campanhas:
        eventos.append(
            {
                "title": campanha.ordem_servico,
                "start": campanha.data_coleta_campo.isoformat(),
                "end": campanha.data_coleta_campo.isoformat(),
                "url": f"/checklist_campanha/{campanha.ordem_servico}/",
            }
        )

    context = {"eventos": json.dumps(eventos)}
    return render(request, "calendario.html", context)


def exportar_resultados_csv(request):
    try:
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="resultados_coleta.csv"'

        writer = csv.writer(response)
        writer.writerow(
            [
                "Código Coleta",
                "Hora Início",
                "Hora Fim",
                "Ponto",
                "Temperatura",
                "pH",
                "ORP",
                "Condutividade",
                "Turbidez",
                "OD",
                "OD %",
                "TDS",
                "Salinidade",
                "Status",
                "Check Amostras",
                "Observações",
            ]
        )

        try:
            resultados = Campo.objects.all().values_list(
                "codigo_coleta",
                "hora_inicio",
                "hora_fim",
                "ponto",
                "temperatura",
                "ph",
                "orp",
                "condutividade",
                "turbidez",
                "od",
                "od_pct",
                "tds",
                "salinidade",
                "status_form",
                "check_amostras",
                "observacoes",
            )
        except ObjectDoesNotExist:
            logger.error("Nenhum resultado encontrado.")
            return HttpResponse(
                "Nenhum resultado encontrado.", content_type="text/plain"
            )
        except Exception as e:
            logger.error(f"Erro ao consultar o banco de dados: {e}")
            return HttpResponse(
                f"Erro ao consultar o banco de dados: {e}", content_type="text/plain"
            )

        for resultado in resultados:
            try:
                writer.writerow(resultado)
            except Exception as e:
                logger.error(f"Erro ao escrever linha CSV: {e}")
                return HttpResponse(
                    f"Erro ao escrever linha CSV: {e}", content_type="text/plain"
                )

        return response

    except Exception as e:
        logger.error(f"Erro ao gerar CSV: {e}")
        return HttpResponse(f"Erro ao gerar CSV: {e}", content_type="text/plain")


def exportar_resultados_xlsx(request):
    try:
        wb = Workbook()
        ws = wb.active
        ws.title = "Resultados Coleta"

        headers = [
            "Código Coleta",
            "Hora Início",
            "Hora Fim",
            "Ponto",
            "Temperatura",
            "pH",
            "ORP",
            "Condutividade",
            "Turbidez",
            "OD",
            "OD %",
            "TDS",
            "Salinidade",
            "Status",
            "Check Amostras",
            "Observações",
        ]

        for col, header in enumerate(headers, 1):
            ws.cell(row=1, column=col, value=header)

        try:
            resultados = Campo.objects.all().values_list(
                "codigo_coleta",
                "hora_inicio",
                "hora_fim",
                "ponto",
                "temperatura",
                "ph",
                "orp",
                "condutividade",
                "turbidez",
                "od",
                "od_pct",
                "tds",
                "salinidade",
                "status_form",
                "check_amostras",
                "observacoes",
            )
        except ObjectDoesNotExist:
            logger.error("Nenhum resultado encontrado.")
            return HttpResponse(
                "Nenhum resultado encontrado.", content_type="text/plain"
            )
        except Exception as e:
            logger.error(f"Erro ao consultar o banco de dados: {e}")
            return HttpResponse(
                f"Erro ao consultar o banco de dados: {e}", content_type="text/plain"
            )

        for row_num, resultado in enumerate(resultados, 2):
            try:
                for col_num, value in enumerate(resultado, 1):
                    ws.cell(row=row_num, column=col_num, value=value)
            except Exception as e:
                logger.error(f"Erro ao escrever linha XLSX: {e}")
                return HttpResponse(
                    f"Erro ao escrever linha XLSX: {e}", content_type="text/plain"
                )

        for col in range(1, len(headers) + 1):
            ws.column_dimensions[get_column_letter(col)].auto_size = True

        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = (
            'attachment; filename="resultados_coleta.xlsx"'
        )

        wb.save(response)
        return response

    except Exception as e:
        logger.error(f"Erro ao gerar XLSX: {e}")
        return HttpResponse(f"Erro ao gerar XLSX: {e}", content_type="text/plain")


@login_required
def cadastro_local(request):
    if request.method == "POST":
        form = LocaisForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Local cadastrado com sucesso.")
            return redirect("cadastro_local")
    else:
        form = LocaisForm()
    return render(request, "cadastro_local.html", {"form": form})


@login_required
def atualizar_local(request, id):
    local = get_object_or_404(TabLocal, id=id)
    if request.method == "POST":
        form = LocaisForm(request.POST, instance=local)
        if form.is_valid():
            form.save()
            messages.success(request, "Local atualizado com sucesso.")
            return redirect("cadastro_local")
    else:
        form = LocaisForm(instance=local)
    return render(request, "cadastro_local.html", {"form": form})


@login_required
def cadastro_setor(request):
    if request.method == "POST":
        form = SetorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Setor cadastrado com sucesso.")
            return redirect("cadastro_setor")
    else:
        form = SetorForm()
    return render(request, "cadastro_setor.html", {"form": form})


@login_required
def atualizar_setor(request, id):
    setor = get_object_or_404(TabSetor, id=id)
    if request.method == "POST":
        form = SetorForm(request.POST, instance=setor)
        if form.is_valid():
            form.save()
            messages.success(request, "Setor atualizado com sucesso.")
            return redirect("cadastro_setor")
    else:
        form = SetorForm(instance=setor)
    return render(request, "cadastro_setor.html", {"form": form})


@login_required
def cadastro_ponto(request):
    if request.method == "POST":
        form = PontoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Ponto cadastrado com sucesso.")
            return redirect("cadastro_ponto")
    else:
        form = PontoForm()
    return render(request, "cadastro_ponto.html", {"form": form})


@login_required
def atualizar_ponto(request, id):
    ponto = get_object_or_404(TabPonto, id=id)
    if request.method == "POST":
        form = PontoForm(request.POST, instance=ponto)
        if form.is_valid():
            form.save()
            messages.success(request, "Ponto atualizado com sucesso.")
            return redirect("cadastro_ponto")
    else:
        form = PontoForm(instance=ponto)
    return render(request, "cadastro_ponto.html", {"form": form})


@login_required
def locais_cadastrados(request):
    setor_filter = SetorFilter(request.GET, queryset=TabSetor.objects.all())
    table_setores = SetorTable(setor_filter.qs)

    ponto_filter = PontoFilter(request.GET, queryset=TabPonto.objects.all())
    table_pontos = PontoTable(ponto_filter.qs)

    local_filter = LocalFilter(request.GET, queryset=TabLocal.objects.all())
    table_locais = LocalTable(local_filter.qs)

    RequestConfig(request, paginate={"per_page": 25}).configure(table_setores)
    RequestConfig(request, paginate={"per_page": 25}).configure(table_pontos)
    RequestConfig(request, paginate={"per_page": 25}).configure(table_locais)

    return render(
        request,
        "locais_cadastrados.html",
        {
            "table_setores": table_setores,
            "table_pontos": table_pontos,
            "table_locais": table_locais,
            "setor_filter": setor_filter,
            "ponto_filter": ponto_filter,
            "local_filter": local_filter,
        },
    )


def export_pontos_csv(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="pontos_coleta.csv"'

    # Adiciona BOM UTF-8 para o Excel reconhecer os caracteres especiais
    response.write("\ufeff".encode("utf-8"))

    writer = csv.writer(
        response,
        delimiter=";",
        quotechar='"',
        quoting=csv.QUOTE_MINIMAL,
    )

    writer.writerow(
        [
            "Nome",
            "Setor",
            "Local",
            "Descrição",
            "Status",
            "Latitude",
            "Longitude",
            "Modalidade",
        ]
    )

    pontos = TabPonto.objects.select_related("id_setor", "id_local").all()
    for ponto in pontos:
        writer.writerow(
            [
                ponto.nome,
                ponto.id_setor.nome if ponto.id_setor else "",
                ponto.id_local.nome if ponto.id_local else "",
                ponto.observacao or "",
                "Ativo" if ponto.status else "Inativo",
                ponto.lat or "",
                ponto.lon or "",
                ponto.modalidade or "",
            ]
        )

    return response


@login_required
def cadastro_parametro(request):
    if request.method == "POST":
        form = ParametroForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Parâmetro cadastrado com sucesso.")
            return redirect("cadastro_parametro")
    else:
        form = ParametroForm()
    return render(request, "cadastro_parametro.html", {"form": form})


@login_required
def cadastro_unidade_medida(request):
    if request.method == "POST":
        form = UnidadeMedidaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request, "Unidade de Medida cadastrada com sucesso.")
            return redirect("cadastro_unidade_medida")
    else:
        form = UnidadeMedidaForm()
    return render(request, "cadastro_unidade_medida.html", {"form": form})


@login_required
def cadastro_tipo_parametro(request):
    if request.method == "POST":
        form = TipoParametroForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request, "Tipo de Parâmetro cadastrado com sucesso.")
            return redirect("cadastro_tipo_parametro")
    else:
        form = TipoParametroForm()

    table_tipo_parametro = TipoParametroTable(TipoParametro.objects.all())
    RequestConfig(request, paginate={"per_page": 25}).configure(
        table_tipo_parametro)

    return render(
        request,
        "cadastro_tipo_parametro.html",
        {"form": form, "table_tipo_parametro": table_tipo_parametro},
    )


@login_required
def configuracoes_view(request):
    if request.method == "POST":
        form_type = None
        for key in request.POST:
            if key.endswith("_submit"):
                form_type = key.replace("_submit", "")
                break

        form_map = {
            "tab_param": (ParametroForm, TabParam),
            "tab_frasco": (TabFrascoForm, TabFrasco),
            "tab_equipe": (TabEquipeForm, TabEquipe),
            "tab_laboratorio": (TabLaboratorioForm, TabLaboratorio),
            "tab_produto": (TabProdutoForm, TabProduto),
            "tab_prodxparam": (TabProdxParamForm, TabProdxparam),
            "tab_serie_classificacao": (
                TabSerieClassificacaoForm,
                TabSerieClassificacao,
            ),
            "tab_item_checklist": (
                CadastroItemChecklistColetaForm,
                TabItemChecklistColeta,
            ),
            "tab_email": (EmailForm, EmailTemplate),
            "tab_status_coleta": (StatusColetaForm, TabStatusColeta),
        }
        if form_type in form_map:
            FormClass, ModelClass = form_map[form_type]
            form = FormClass(request.POST)
            if form.is_valid():
                try:
                    form.save()
                    messages.success(
                        request, "Novo registro criado com sucesso.")
                except Exception as e:
                    messages.error(request, f"Erro ao salvar: {str(e)}")
            else:
                messages.error(
                    request, "Por favor, corrija os erros no formulário.")
        return redirect("configuracoes")

    # Filtros de busca
    nome_parametro = request.GET.get('nome_parametro', '')
    nome_prodxparam = request.GET.get('nome_prodxparam', '')

    param_form = ParametroForm()
    frasco_form = TabFrascoForm()
    equipe_form = TabEquipeForm()
    laboratorio_form = TabLaboratorioForm()
    produto_form = TabProdutoForm()
    prodxparam_form = TabProdxParamForm()
    serie_classificacao_form = TabSerieClassificacaoForm()
    item_checklist_form = CadastroItemChecklistColetaForm()
    email_form = EmailForm()
    status_coleta_form = StatusColetaForm()

    # Obter dados para as tabelas
    param_data = TabParam.objects.all()
    prodxparam_data = TabProdxparam.objects.all()

    # Aplicar filtros
    if nome_parametro:
        param_data = param_data.filter(nome__icontains=nome_parametro)

    if nome_prodxparam:
        prodxparam_data = prodxparam_data.filter(
            Q(id_produto__nome__icontains=nome_prodxparam) |
            Q(id_param__nome__icontains=nome_prodxparam) |
            Q(unidade__icontains=nome_prodxparam)
        )

    # Instanciar as tabelas
    table_parametro = ParametroTable(param_data)
    table_frasco = FrascoTable(TabFrasco.objects.all())
    table_equipe = EquipeTable(TabEquipe.objects.all())
    table_laboratorio = LaboratorioTable(TabLaboratorio.objects.all())
    table_produto = ProdutoTable(TabProduto.objects.all())
    table_prodxparam = ProdxparamTable(prodxparam_data)
    table_serie_classificacao = SerieClassificacaoTable(
        TabSerieClassificacao.objects.all()
    )
    table_item_checklist = TipoItemChecklistColetaTable(
        TabItemChecklistColeta.objects.all()
    )
    table_email = EmailTable(EmailTemplate.objects.all())
    table_status_coleta = StatusColetaTable(TabStatusColeta.objects.all())

    # Configurar a paginação das tabelas
    RequestConfig(request, paginate={"per_page": 25}).configure(
        table_parametro)
    RequestConfig(request, paginate={"per_page": 25}).configure(table_frasco)
    RequestConfig(request, paginate={"per_page": 25}).configure(table_equipe)
    RequestConfig(request, paginate={"per_page": 25}).configure(
        table_laboratorio)
    RequestConfig(request, paginate={"per_page": 25}).configure(table_produto)
    RequestConfig(request, paginate={"per_page": 25}).configure(
        table_prodxparam)
    RequestConfig(request, paginate={"per_page": 25}).configure(
        table_serie_classificacao
    )
    RequestConfig(request).configure(table_item_checklist)
    RequestConfig(request).configure(table_email)
    RequestConfig(request).configure(table_status_coleta)

    # Configurar os dados das abas
    tabs = [
        ("tab_param", param_form, table_parametro, "Parâmetros"),
        ("tab_frasco", frasco_form, table_frasco, "Frascos"),
        ("tab_equipe", equipe_form, table_equipe, "Equipes"),
        ("tab_laboratorio", laboratorio_form, table_laboratorio, "Laboratórios"),
        ("tab_produto", produto_form, table_produto, "Produtos"),
        ("tab_prodxparam", prodxparam_form,
         table_prodxparam, "Produto x Parâmetro"),
        (
            "tab_serie_classificacao",
            serie_classificacao_form,
            table_serie_classificacao,
            "Série Classificação",
        ),
        (
            "tab_item_checklist",
            item_checklist_form,
            table_item_checklist,
            "Itens de Checklist",
        ),
        ("tab_email", email_form, table_email, "Templates de E-mail"),
        (
            "tab_status_coleta",
            status_coleta_form,
            table_status_coleta,
            "Status de Coleta",
        ),
    ]

    context = {
        "tabs": tabs,
        "nome_parametro": nome_parametro,
        "nome_prodxparam": nome_prodxparam,
    }

    # Renderizar o template com os formulários e tabelas
    return render(
        request,
        "configuracoes.html",
        context,
    )


@login_required
def editar_registro(request, tabela, pk):
    model_map = {
        "param": (TabParam, ParametroForm),
        "frasco": (TabFrasco, TabFrascoForm),
        "equipe": (TabEquipe, TabEquipeForm),
        "laboratorio": (TabLaboratorio, TabLaboratorioForm),
        "produto": (TabProduto, TabProdutoForm),
        "prodxparam": (TabProdxparam, TabProdxParamForm),
        "serie_classificacao": (TabSerieClassificacao, TabSerieClassificacaoForm),
        "item_checklist": (TabItemChecklistColeta, CadastroItemChecklistColetaForm),
        "email": (EmailTemplate, EmailForm),
        # Adicionar esta linha
        "status_coleta": (TabStatusColeta, StatusColetaForm),
    }

    if tabela not in model_map:
        messages.error(request, "Tabela inválida.")
        return redirect("configuracoes")

    model, form_class = model_map[tabela]
    instance = get_object_or_404(model, pk=pk)

    if request.method == "POST":
        form = form_class(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, "Registro atualizado com sucesso!")
            return redirect("configuracoes")
    else:
        form = form_class(instance=instance)

    return render(
        request, "configuracoes_editar.html", {"form": form, "tabela": tabela}
    )


def direcionamento_campanha(request):
    return render(request, "direcionamento_campanha.html")


@login_required
def perfil_usuario(request):
    usuario = request.user
    try:
        detalhes_usuario = DetalhesUsuario.objects.get(usuario=usuario)
    except DetalhesUsuario.DoesNotExist:
        detalhes_usuario = DetalhesUsuario(usuario=usuario)

    if request.method == "POST":
        detalhes_form = DetalhesUsuarioForm(
            request.POST, instance=detalhes_usuario)
        senha_form = PasswordChangeForm(user=usuario, data=request.POST)

        if detalhes_form.is_valid():
            detalhes_form.save()
            messages.success(
                request, "Detalhes do perfil atualizados com sucesso.")

        if senha_form.is_valid():
            user = senha_form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Senha alterada com sucesso.")
            return redirect("perfil_usuario")
    else:
        detalhes_form = DetalhesUsuarioForm(instance=detalhes_usuario)
        senha_form = PasswordChangeForm(user=usuario)

    return render(
        request,
        "perfil_usuario.html",
        {"detalhes_form": detalhes_form, "senha_form": senha_form},
    )


@login_required
@user_passes_test(is_superuser)
def cadastro_usuarios_adm(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # Define uma senha não utilizável até que o usuário a redefina
            user.set_unusable_password()
            user.save()

            # Enviar e-mail de boas-vindas
            subject = "Bem-vindo ao sistema LAGUNA"
            message = f"Olá {user.username},\n\nVocê foi cadastrado no sistema LAGUNA. Por favor, clique no link abaixo para definir sua senha e completar seu cadastro:\n\n{settings.SITE_URL}/accounts/password/reset/"
            recipient_list = [user.email]
            send_mail(subject, message,
                      settings.EMAIL_HOST_USER, recipient_list)

            messages.success(
                request,
                "Usuário cadastrado com sucesso e e-mail de boas-vindas enviado.",
            )
            return redirect("usuarios_cadastrados")
    else:
        form = CustomUserCreationForm()

    return render(request, "cadastro_usuarios_adm.html", {"form": form})


@login_required
def cadastro_campanha(request):
    if request.method == "POST":
        form = CadastroCampanhaForm(request.POST)
        if form.is_valid():
            form.save()
            # Substitua 'success_url' pela URL de sucesso desejada
            return redirect("cadastro_coleta")
    else:
        form = CadastroCampanhaForm()

    return render(request, "cadastro_campanha.html", {"form": form})


def enviar_email_async(subject, message, from_email, recipient_list):
    """Função auxiliar para enviar email de forma assíncrona"""
    try:
        send_mail(subject, message, from_email, recipient_list)
    except Exception as e:
        logger.error(f"Erro ao enviar email: {e}")


def get_group_emails(group_name):
    """Helper function to retrieve emails of users in a specific group."""

    try:
        group = Group.objects.filter(name__iexact=group_name).first()
        if not group:
            raise Group.DoesNotExist
        return [user.email for user in group.user_set.all() if user.email]
    except Group.DoesNotExist:
        logger.warning(f"Group '{group_name}' not found.")
        return []


def get_all_group_names():
    """Helper function to retrieve all group names."""

    return [group.name for group in Group.objects.all()]


@login_required
def cadastro_coleta_view(request):
    data_inicial = request.GET.get("date")
    if request.method == "POST":
        form = CadastroColetaForm(request.POST)
        if form.is_valid():
            coleta = form.save(commit=False)
            coleta.criado_por = request.user

            # Converter a data da string para datetime
            data_str = request.POST.get("data")
            if data_str:
                coleta.data = datetime.strptime(data_str, "%Y-%m-%d")

            coleta.save(usuario=request.user)

            # Criar entradas na tabela TabChecklistColeta para cada item de checklist
            itens_checklist = TabItemChecklistColeta.objects.all()
            checklist_entries = [
                TabChecklistColeta(id_coleta=coleta, item=item)
                for item in itens_checklist
            ]
            TabChecklistColeta.objects.bulk_create(checklist_entries)

            # Enviar e-mail para todos os usuários do grupo "Coleta"
            subject = "Não responda - Coleta programada com sucesso"
            message = f"Olá,\n\nA coleta com a ordem de serviço {coleta.ordem_servico} foi criada com sucesso por {request.user.username}. \n\nAcesse o sistema em {settings.SITE_URL}/info_coleta/{coleta.id} para mais informações. \n\n Este é um e-mail automático, favor não responder."

            try:
                # Usar iexact para busca insensível a maiúsculas/minúsculas
                grupo_coleta = Group.objects.filter(
                    name__iexact="coleta").first()
                if not grupo_coleta:
                    raise Group.DoesNotExist

                usuarios_coleta = grupo_coleta.user_set.all()
                recipient_list = [
                    usuario.email for usuario in usuarios_coleta if usuario.email
                ]

                if recipient_list:
                    # Iniciar thread para envio de email
                    Thread(
                        target=enviar_email_async,
                        args=(
                            subject,
                            message,
                            settings.EMAIL_HOST_USER,
                            recipient_list,
                        ),
                    ).start()
                    messages.success(
                        request,
                        f"Coleta agendada com sucesso e notificações enviadas para {len(recipient_list)} membros da equipe de coleta.",
                    )
                else:
                    messages.warning(
                        request,
                        "Coleta agendada com sucesso, mas os usuários do grupo de coleta não possuem e-mails cadastrados.",
                    )
            except Group.DoesNotExist:
                messages.warning(
                    request,
                    f"Coleta agendada com sucesso, mas o grupo de coleta não foi encontrado. Grupos disponíveis: {', '.join(get_all_group_names())}",
                )

            return redirect("checklist_coleta", coleta_id=coleta.id)
    else:
        initial_data = {}
        if data_inicial:
            initial_data["data"] = data_inicial
        form = CadastroColetaForm(initial=initial_data)
    return render(request, "cadastro_coleta.html", {"form": form})


@login_required
def cadastro_item_checklist_coleta(request):
    if request.method == "POST":
        form = CadastroItemChecklistColetaForm(request.POST)
        if form.is_valid():
            form.save(user=request.user)
            messages.success(
                request, "Item de checklist cadastrado com sucesso.")
            return redirect("cadastro_item_checklist_coleta")
    else:
        form = CadastroItemChecklistColetaForm()

    # Crie a tabela com os itens existentes
    table = TipoItemChecklistColetaTable(TabItemChecklistColeta.objects.all())
    RequestConfig(request).configure(table)

    return render(
        request, "cadastro_item_checklist_coleta.html", {
            "form": form, "table": table}
    )


@login_required
def export_csv(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM tab_medida_pivotada")
        rows = cursor.fetchall()
        columns = [col[0] for col in cursor.description]

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="tab_medida_pivotada.csv"'

    writer = csv.writer(response)
    writer.writerow(columns)
    for row in rows:
        writer.writerow(row)

    return response


@login_required
def view_tab_medida_pivotada(request):
    # Campo padrão para ordenar
    order_by = request.GET.get("order_by", "campanha")
    # Direção padrão para ordenar
    direction = request.GET.get("direction", "asc")

    # Filtros de campanha, ponto e setor
    campanha_filter = request.GET.get("campanha", "")
    ponto_filter = request.GET.get("ponto", "")
    setor_filter = request.GET.get("setor", "")

    # Construir a cláusula WHERE corretamente
    where_clauses = []
    if campanha_filter:
        where_clauses.append(f"campanha = '{campanha_filter}'")
    if setor_filter:
        where_clauses.append(f"setor = '{setor_filter}'")
    if ponto_filter:
        where_clauses.append(f"ponto = '{ponto_filter}'")

    where_clause = " AND ".join(where_clauses) if where_clauses else "1=1"

    # Construir a cláusula ORDER BY corretamente
    order_clause = f'"{order_by}" {direction.upper()}'

    with connection.cursor() as cursor:
        cursor.execute(
            f"SELECT * FROM tab_medida_pivotada WHERE {where_clause} ORDER BY {order_clause}"
        )
        rows = cursor.fetchall()
        columns = [col[0] for col in cursor.description]

    paginator = Paginator(rows, 20)  # Limitar a 20 resultados por página
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "columns": columns,
        "page_obj": page_obj,
        "order_by": order_by,
        "direction": direction,
        "campanha_filter": campanha_filter,
        "ponto_filter": ponto_filter,
        "setor_filter": setor_filter,
    }
    return render(request, "view_tab_medida_pivotada.html", context)


@login_required
def checklist_coleta(request, coleta_id):
    """
    Gera e processa um formulário de checklist para uma coleta específica.

    Esta função cria um conjunto de formulários (formset) para o modelo TabChecklistColeta,
    filtrando os itens pelo ID da coleta fornecido. Se a solicitação for um POST, o formset
    é preenchido com os dados enviados e, se válido, salva os dados no banco de dados.
    Caso contrário, um formset vazio é gerado para exibição.

    Parâmetros:
    request (HttpRequest): O objeto de solicitação HTTP.
    coleta_id (int): O ID da coleta para a qual o checklist será gerado.

    Retorna:
    HttpResponse: Renderiza a página 'checklist_coleta.html' com o formset, coleta e campanha.
    """
    ChecklistColetaFormSet = modelformset_factory(
        TabChecklistColeta, form=ChecklistColetaForm, extra=0
    )
    coleta = get_object_or_404(TabColeta, id=coleta_id)
    campanha = coleta.id_campanha
    if request.method == "POST":
        formset = ChecklistColetaFormSet(
            request.POST, queryset=TabChecklistColeta.objects.filter(
                id_coleta=coleta)
        )
        if formset.is_valid():
            formset.save()
            # Substitua pela URL de sucesso desejada
            return redirect("info_coleta", coleta_id=coleta_id)
    else:
        formset = ChecklistColetaFormSet(
            queryset=TabChecklistColeta.objects.filter(id_coleta=coleta)
        )

    return render(
        request,
        "checklist_coleta.html",
        {"formset": formset, "coleta": coleta, "campanha": campanha},
    )


@login_required
def fill_amostra(request, coleta_id):
    """
    Preenche as amostras e envios para uma coleta específica.
    """
    try:
        with transaction.atomic():
            coleta = get_object_or_404(TabColeta, id=coleta_id)
            frascos = TabFrasco.objects.all()
            pontos_coleta = TabPonto.objects.filter(
                id_setor=coleta.id_setor,
                status=True,  # Apenas pontos ativos
            )

            # Obter amostras existentes para esta coleta
            amostras_existentes = set(
                TabAmostra.objects.filter(id_coleta=coleta).values_list(
                    "id_ponto_id", "id_coleta_id", "id_frasco_id"
                )
            )

            amostras = []
            for frasco in frascos:
                if not coleta.analise_bentos and frasco.id in [5, 6, 7]:
                    continue
                for ponto in pontos_coleta:
                    # Verifica se a combinação já existe
                    if (ponto.id, coleta.id, frasco.id) not in amostras_existentes:
                        amostra = TabAmostra(
                            id_coleta=coleta,
                            id_frasco=frasco,
                            id_ponto=ponto,
                            etiqueta=f"{coleta.ordem_servico}{str(ponto.id).zfill(3)}{str(frasco.id).zfill(2)}",
                        )
                        amostras.append(amostra)

            # Só cria amostras se houver novas
            if amostras:
                TabAmostra.objects.bulk_create(amostras)

                # Criar envios para as novas amostras
                envios = [
                    TabEnvio(id_amostra=amostra)
                    for amostra in TabAmostra.objects.filter(id_coleta=coleta)
                    if not TabEnvio.objects.filter(id_amostra=amostra).exists()
                ]

                if envios:
                    TabEnvio.objects.bulk_create(envios)

                # Atualiza o status da coleta para
                TabColeta.objects.filter(id=coleta_id).update(status_id=6)

                messages.success(request, "Amostras criadas com sucesso!")
            else:
                messages.info(
                    request, "Todas as amostras já foram criadas anteriormente."
                )

            # Após criar as amostras e envios, gerar medidas para todos os frascos
            for frasco in frascos:
                if not coleta.analise_bentos and frasco.id in [5, 6, 7]:
                    continue
                return redirect(
                    "fill_frasco_medida", coleta_id=coleta_id, frasco_id=frasco.id
                )

            return redirect("info_coleta", coleta_id=coleta_id)

    except Exception as e:
        messages.error(request, f"Erro ao criar amostras: {str(e)}")
        return redirect("info_coleta", coleta_id=coleta_id)


@login_required
def fill_frasco_medida(request, coleta_id, frasco_id):
    """
    Preenche os campos de medida para um frasco específico da coleta.
    """
    coleta = get_object_or_404(TabColeta, id=coleta_id)
    frasco = get_object_or_404(TabFrasco, id=frasco_id)

    # Verifica se já existem medidas para este frasco nesta coleta
    medidas_existentes = TabMedida.objects.filter(
        id_envio__id_amostra__id_coleta=coleta_id,
        id_envio__id_amostra__id_frasco=frasco_id,
    ).exists()

    if not medidas_existentes:
        try:
            # Obtém todas as amostras para este frasco
            amostras = TabAmostra.objects.filter(
                id_coleta=coleta, id_frasco=frasco)

            # Para cada amostra, verifica/cria o envio e as medidas
            for amostra in amostras:
                # Cria ou obtém o envio
                envio, created = TabEnvio.objects.get_or_create(
                    id_amostra=amostra)

                # Obtém os parâmetros ativos para este frasco
                parametros = TabProdxparam.objects.filter(
                    id_frasco=frasco, status=True)

                # Cria as medidas para cada parâmetro
                medidas = []
                for parametro in parametros:
                    medida = TabMedida(id_envio=envio, id_pp=parametro)
                    medidas.append(medida)

                # Cria todas as medidas de uma vez
                if medidas:
                    TabMedida.objects.bulk_create(medidas)

            # Procura próximo frasco que precise de medidas
            proximo_frasco = TabFrasco.objects.filter(
                id__gt=frasco_id, tabamostra__id_coleta=coleta
            ).first()

            if proximo_frasco:
                return redirect(
                    "fill_frasco_medida",
                    coleta_id=coleta_id,
                    frasco_id=proximo_frasco.id,
                )
            else:
                # Só mostra a mensagem de sucesso quando terminar todos os frascos
                messages.success(
                    request, "Formulários gerados com sucesso para todos os frascos"
                )

        except Exception as e:
            messages.error(request, f"Erro ao gerar formulários: {str(e)}")
            return redirect("info_coleta", coleta_id=coleta_id)

    return redirect("info_coleta", coleta_id=coleta_id)


@login_required
def lista_campo_frasco(request, coleta_id, frasco_id):
    """
    Lista os campos de medida para um frasco específico.
    """
    coleta = get_object_or_404(TabColeta, id=coleta_id)
    frasco = get_object_or_404(TabFrasco, id=frasco_id)

    # Filtra as amostras da coleta atual para o frasco específico
    amostras = TabAmostra.objects.filter(id_coleta=coleta, id_frasco=frasco).order_by(
        "id_ponto"
    )

    table = ListaCampoTable(amostras)
    RequestConfig(request, paginate={"per_page": 40}).configure(table)

    return render(
        request,
        "lista_campo.html",
        {"coleta": coleta, "frasco": frasco, "table": table, "amostras": amostras},
    )


@login_required
def selecionar_frasco(request, coleta_id):
    coleta = get_object_or_404(TabColeta, id=coleta_id)

    # Obtém os frascos disponíveis para esta coleta
    frascos_disponiveis = TabFrasco.objects.filter(
        id__in=TabAmostra.objects.filter(id_coleta=coleta)
        .values_list("id_frasco", flat=True)
        .distinct()
    )

    # Para cada frasco, verifica se tem envios E medidas
    frascos_info = []
    for frasco in frascos_disponiveis:
        envios_existentes = TabEnvio.objects.filter(
            id_amostra__id_coleta=coleta_id, id_amostra__id_frasco=frasco.id
        ).exists()

        medidas_existentes = TabMedida.objects.filter(
            id_envio__id_amostra__id_coleta=coleta_id,
            id_envio__id_amostra__id_frasco=frasco.id,
        ).exists()

        tem_formularios = envios_existentes and medidas_existentes

        frascos_info.append(
            {
                "id": frasco.id,
                "nome": frasco.nome,
                "tem_formularios": tem_formularios,
                "status": "success" if tem_formularios else "warning",
            }
        )

    return render(
        request,
        "modal_selecao_frasco.html",
        {"coleta": coleta, "frascos": frascos_info},
    )


@login_required
def info_coleta(request, coleta_id):
    coleta = get_object_or_404(TabColeta, id=coleta_id)
    usuario_responsavel = coleta.criado_por
    data_coleta = coleta.data
    data_criacao = coleta.criado_em
    fill_amostra_gerado = TabMedida.objects.filter(
        id_envio__id_amostra__id_coleta=coleta.id, id_envio__id_amostra__id_frasco=1
    ).exists()
    previsao_tempo = get_weather_description(
        "Maricá", data_coleta.strftime("%Y-%m-%d")
    )
    total_items = TabChecklistColeta.objects.filter(id_coleta=coleta).count()
    items_preenchidos = TabChecklistColeta.objects.filter(
        id_coleta=coleta, status=True
    ).count()
    percentual_checklist = (
        float((items_preenchidos / total_items)
              * 100) if total_items > 0 else 0.0
    )
    pontos_coleta = []
    pontos = TabPonto.objects.filter(id_setor=coleta.id_setor)
    for ponto in pontos:
        amostra = TabAmostra.objects.filter(
            id_coleta=coleta,
            id_ponto=ponto,
            id_frasco=1,
        ).first()
        formulario_preenchido = False
        parcialmente_preenchido = False
        if amostra:
            medidas = TabMedida.objects.filter(id_envio__id_amostra=amostra)
            total_medidas = medidas.count()
            medidas_preenchidas = (
                medidas.exclude(input_valor__isnull=True)
                .exclude(input_valor__exact="")
                .count()
            )
            if total_medidas > 0:
                if medidas_preenchidas == total_medidas:
                    formulario_preenchido = True
                elif medidas_preenchidas > 0:
                    parcialmente_preenchido = True
        pontos_coleta.append(
            {
                "id": ponto.id,
                "nome": ponto.nome,
                "lat": ponto.lat,
                "lon": ponto.lon,
                "status": ponto.status,
                "formulario_preenchido": formulario_preenchido,
                "parcialmente_preenchido": parcialmente_preenchido,
            }
        )
    pontos_coleta_json = json.dumps(pontos_coleta, cls=DjangoJSONEncoder)
    context = {
        "coleta": coleta.id,
        "setor": coleta.id_setor,
        "coleta_os": coleta.ordem_servico,
        "usuario_responsavel": usuario_responsavel,
        "data_coleta": data_coleta,
        "data_criacao": data_criacao,
        "fill_amostra_gerado": fill_amostra_gerado,
        "previsao_tempo": previsao_tempo,
        "percentual_checklist": percentual_checklist,
        "link": f"{settings.SITE_URL}/info_coleta/{coleta_id}",
        "pontos_coleta": pontos_coleta_json,
        "atualizado": coleta.atualizado_em,
        "status_coleta": coleta.status_id,
        "status_disponiveis": TabStatusColeta.objects.all().order_by("status"),
        "mostrar_diagnostico": request.user.is_superuser,
    }
    return render(request, "info_coleta.html", context)


@login_required
@user_passes_test(lambda u: u.is_superuser)
def diagnostico_coleta(request, coleta_id):
    coleta = get_object_or_404(TabColeta, id=coleta_id)
    frascos_ativos = TabFrasco.objects.all()
    medidas_faltantes_por_frasco = {}      # Medidas existem, mas não preenchidas
    medidas_nao_geradas_por_frasco = {}    # Medidas não existem na tabela

    for frasco in frascos_ativos:
        amostras = TabAmostra.objects.filter(id_coleta=coleta, id_frasco=frasco)
        parametros = TabProdxparam.objects.filter(id_frasco=frasco, status=True)
        faltantes = []
        nao_geradas = []
        for parametro in parametros:
            for amostra in amostras:
                envio = TabEnvio.objects.filter(id_amostra=amostra).first()
                medida = TabMedida.objects.filter(id_envio=envio, id_pp=parametro).first() if envio else None
                if medida:
                    if not medida.input_valor:
                        faltantes.append((amostra, parametro))
                else:
                    nao_geradas.append((amostra, parametro))
        if faltantes:
            medidas_faltantes_por_frasco[frasco] = faltantes
        if nao_geradas:
            medidas_nao_geradas_por_frasco[frasco] = nao_geradas

    context = {
        "coleta": coleta,
        "medidas_faltantes_por_frasco": medidas_faltantes_por_frasco,
        "medidas_nao_geradas_por_frasco": medidas_nao_geradas_por_frasco,
    }
    return render(request, "diagnostico_coleta.html", context)

@login_required
def adicionar_frasco_coleta(request, coleta_id):
    if request.method == "POST":
        frasco_id = request.POST.get("frasco_id")
        coleta = get_object_or_404(TabColeta, id=coleta_id)
        frasco = get_object_or_404(TabFrasco, id=frasco_id)
        pontos_coleta = TabPonto.objects.filter(
            id_setor=coleta.id_setor, status=True)
        novas_amostras = []
        for ponto in pontos_coleta:
            if not TabAmostra.objects.filter(id_coleta=coleta, id_frasco=frasco, id_ponto=ponto).exists():
                amostra = TabAmostra(
                    id_coleta=coleta,
                    id_frasco=frasco,
                    id_ponto=ponto,
                    etiqueta=f"{coleta.ordem_servico}{str(ponto.id).zfill(3)}{str(frasco.id).zfill(2)}",
                )
                novas_amostras.append(amostra)
        if novas_amostras:
            TabAmostra.objects.bulk_create(novas_amostras)
            for amostra in TabAmostra.objects.filter(id_coleta=coleta, id_frasco=frasco):
                TabEnvio.objects.get_or_create(id_amostra=amostra)
            messages.success(
                request, "Frasco adicionado e amostras criadas com sucesso!")
        else:
            messages.info(
                request, "O frasco já estava presente em todos os pontos.")
        return redirect("info_coleta", coleta_id=coleta_id)
    return redirect("info_coleta", coleta_id=coleta_id)


@login_required
def corrigir_medidas_frasco(request, coleta_id, frasco_id):
    coleta = get_object_or_404(TabColeta, id=coleta_id)
    frasco = get_object_or_404(TabFrasco, id=frasco_id)
    usuario = request.user

    amostras = TabAmostra.objects.filter(id_coleta=coleta, id_frasco=frasco)
    parametros = TabProdxparam.objects.filter(id_frasco=frasco, status=True)
    medidas_criadas = 0

    with transaction.atomic():
        for amostra in amostras:
            envio, _ = TabEnvio.objects.get_or_create(id_amostra=amostra)
            for parametro in parametros:
                if not TabMedida.objects.filter(id_envio=envio, id_pp=parametro).exists():
                    medida = TabMedida(id_envio=envio, id_pp=parametro)
                    medida.save(usuario=usuario)
                    medidas_criadas += 1

    messages.success(
        request, f"{medidas_criadas} medidas criadas/corrigidas para o frasco selecionado.")
    return redirect("info_coleta", coleta_id=coleta_id)


@login_required
def input_fisico_quimico(request, coleta_id, ponto_id):
    MedidaFormSet = modelformset_factory(
        TabMedida, form=InputFisicoQuimicoForm, extra=0, fields="__all__"
    )

    coleta = get_object_or_404(TabColeta, id=coleta_id)
    ponto = get_object_or_404(TabPonto, id=ponto_id, status=True)

    # Busca parametro_id do GET (ou defina um valor padrão se necessário)
    parametro_id = request.GET.get('parametro')

    # Busca anexo existente
    anexo_existente = None
    anexo_query = TabAnexoAmostra.objects.filter(
        id_envio__id_amostra__id_coleta=coleta_id,
        id_envio__id_amostra__id_ponto=ponto_id,
        id_envio__id_amostra__id_frasco=1,
    ).first()

    # Se encontrou um anexo, verifica se tem arquivo ou observação
    if anexo_query:
        anexo_existente = anexo_query
        # Se não tem arquivo nem observação, deleta o registro
        if not anexo_existente.anexo and not anexo_existente.observacao:
            anexo_existente.delete()
            anexo_existente = None

    if request.method == "POST":
        formset = MedidaFormSet(
            request.POST,
            request.FILES,
            queryset=TabMedida.objects.filter(
                id_pp_id=parametro_id, id_envio__id_amostra__id_ponto_id=ponto_id
            )
            .select_related("id_envio__id_amostra__id_coleta")
            .order_by("id_envio__id_amostra__id_coleta__data"),
        )

        if formset.is_valid():
            instances = formset.save()

            # Processa o anexo se houver arquivo ou observação
            primeiro_envio = instances[0].id_envio if instances else None
            if primeiro_envio:
                handle_anexo(request, primeiro_envio)

            proximo_ponto = TabPonto.objects.filter(
                id_setor=coleta.id_setor, status=True, id__gt=ponto.id
            ).first()

            if proximo_ponto:
                return redirect(
                    "input_fisico_quimico",
                    coleta_id=coleta_id,
                    ponto_id=proximo_ponto.id,
                )
            else:
                return redirect("info_coleta", coleta_id=coleta_id)
    else:
        formset = MedidaFormSet(
            queryset=TabMedida.objects.filter(
                id_envio__id_amostra__id_coleta=coleta_id,
                id_envio__id_amostra__id_ponto=ponto_id,
                id_envio__id_amostra__id_frasco=1,
            )
        )

    return render(
        request,
        "input_fisico_quimico.html",
        {
            "formset": formset,
            "coleta": coleta,
            "ponto": ponto,
            "anexo_existente": anexo_existente,
        },
    )


@login_required
def lista_campo(request, coleta_id):
    coleta = get_object_or_404(TabColeta, id=coleta_id)

    # Filtra as amostras da coleta atual
    amostras = TabAmostra.objects.filter(
        id_coleta=coleta,
        id_frasco=1,  # Assumindo que queremos apenas amostras do frasco 1
    ).order_by("id_ponto")

    # Cria a tabela com as amostras
    table = ListaCampoTable(amostras)

    # Configura a paginação

    RequestConfig(request, paginate={"per_page": 40}).configure(table)

    return render(
        request,
        "lista_campo.html",
        {"coleta": coleta, "table": table, "amostras": amostras},
    )


@login_required
def meta_ponto(request, id):
    coleta = get_object_or_404(TabColeta, id=id)

    # Verifica se já existe um registro de metadados para o código de coleta
    metadados, created = MetadadosPonto.objects.get_or_create(
        codigo_coleta=coleta)

    if created:
        messages.info(
            request,
            "Novo registro de metadados criado para o código de coleta fornecido.",
        )

    if request.method == "POST":
        form = MetadadosCampoForm(request.POST, instance=metadados)
        if form.is_valid():
            form.save()
            # Redireciona para a página anterior
            return redirect(reverse("atualizar_coleta", args=[coleta.id]))
    else:
        form = MetadadosCampoForm(instance=metadados)

    context = {
        "form": form,
        "codigo_coleta": coleta.codigo_coleta,
        "coleta_id": coleta.id,
        "ponto": coleta.ponto,
        "ordem_servico_id": coleta.ordem_servico.id,
        "ordem_servico": coleta.ordem_servico,
    }

    return render(request, "coleta/meta_coleta.html", context)


@login_required
def lista_de_coletas(request):
    # Obter os filtros da query string
    status_id = request.GET.get("status_id")
    id_setor = request.GET.get("id_setor")

    # Query base
    queryset = TabColeta.objects.all().order_by("-data")

    # Aplicar filtros se fornecidos
    if status_id:
        queryset = queryset.filter(status_id=status_id)
    if id_setor:
        queryset = queryset.filter(id_setor=id_setor)

    # Obter listas únicas para os dropdowns
    setores = TabSetor.objects.all()
    status = TabStatusColeta.objects.all()

    # Criar a tabela
    table = TabColetaTable(queryset)
    RequestConfig(request, paginate={"per_page": 10}).configure(table)

    context = {
        "table": table,
        "setores": setores,
        "status": status,
        "filtros": {
            "status_id": status_id,
            "id_setor": id_setor,
        },
    }

    # Se for uma requisição AJAX, retornar apenas os dados filtrados
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse(
            {
                "setores": list(setores.values("id", "nome")),
                "status": list(status.values("id", "status")),
            }
        )

    return render(request, "lista_de_coletas.html", context)


@login_required
def update_coleta(request, id):
    coleta = get_object_or_404(TabColeta, id=id)
    coleta_original = TabColeta.objects.get(
        pk=coleta.pk)  # Cópia do estado original

    if request.method == "POST":
        form = CadastroColetaForm(request.POST, instance=coleta)
        if form.is_valid():
            # Não salva ainda para poder comparar os campos
            coleta_atualizada = form.save(commit=False)
            coleta_atualizada.atualizado_por = request.user

            # Lista de campos a serem monitorados para registro de logs
            campos_monitorados = [
                ("nome", "Nome"),
                ("data", "Data"),
                ("id_campanha_id", "Campanha"),
                ("id_setor_id", "Setor"),
                ("analise_bentos", "Análise Bentos"),
                ("ordem_servico", "Ordem de Serviço"),
                ("status_id_id", "Status"),
                ("observacao", "Observação"),
            ]

            mudancas = []
            for campo_id, campo_nome in campos_monitorados:
                valor_antigo = getattr(coleta_original, campo_id)
                valor_novo = getattr(coleta_atualizada, campo_id)

                # Tratamento especial para FKs
                if campo_id.endswith("_id"):
                    # Usar .get_FOO_display() para obter nome legível de objetos relacionados
                    campo_base = campo_id[:-3]  # Remove o sufixo '_id'
                    objeto_relacionado_antigo = getattr(
                        coleta_original, campo_base, None
                    )
                    objeto_relacionado_novo = getattr(
                        coleta_atualizada, campo_base, None
                    )

                    if objeto_relacionado_antigo:
                        valor_antigo = str(objeto_relacionado_antigo)
                    if objeto_relacionado_novo:
                        valor_novo = str(objeto_relacionado_novo)

                # Tratamento especial para campos date/datetime
                if isinstance(valor_antigo, datetime):
                    valor_antigo = valor_antigo.strftime("%d/%m/%Y %H:%M")
                if isinstance(valor_novo, datetime):
                    valor_novo = valor_novo.strftime("%d/%m/%Y %H:%M")

                # Se houve mudança, registra
                if valor_antigo != valor_novo:
                    mudancas.append(
                        f"{campo_nome}: '{valor_antigo}' → '{valor_novo}'")

            # Salva as alterações na coleta
            coleta_atualizada.save()

            # Gerar log detalhado se houver mudanças
            if mudancas:
                motivo = f"Alterações realizadas: {', '.join(mudancas)}"

                # Cria o log da atualização
                TabLogColeta.objects.create(
                    id_coleta=coleta,
                    acao="Coleta atualizada",
                    usuario=request.user,
                    motivo=motivo,
                )

                # Notificar por e-mail se houver mudanças
                subject = f"Coleta {coleta.ordem_servico} foi atualizada"
                message = f"Olá,\n\nA coleta com ordem de serviço {coleta.ordem_servico} foi atualizada por {request.user.username}.\n\n"
                message += f"Alterações realizadas:\n{', '.join(mudancas)}.\n\n"
                message += f"Acesse o sistema em {settings.SITE_URL}/info_coleta/{coleta.id} para mais informações.\n\n"
                message += "Este é um e-mail automático, favor não responder."

                try:
                    grupo_coleta = Group.objects.filter(
                        name__iexact="coleta").first()
                    if grupo_coleta:
                        usuarios_coleta = grupo_coleta.user_set.all()
                        recipient_list = [
                            usuario.email
                            for usuario in usuarios_coleta
                            if usuario.email
                        ]

                        if recipient_list:
                            # Iniciar thread para envio de email
                            Thread(
                                target=enviar_email_async,
                                args=(
                                    subject,
                                    message,
                                    settings.EMAIL_HOST_USER,
                                    recipient_list,
                                ),
                            ).start()
                            messages.success(
                                request,
                                f"Coleta atualizada com sucesso! {motivo} Notificações enviadas para {len(recipient_list)} membros da equipe de coleta.",
                            )
                        else:
                            messages.success(
                                request,
                                f"Coleta atualizada com sucesso! {motivo} Nenhuma notificação enviada pois os membros do grupo não possuem e-mails cadastrados.",
                            )
                    else:
                        messages.success(
                            request,
                            f"Coleta atualizada com sucesso! {motivo} Grupo 'Coleta' não encontrado, notificações não foram enviadas.",
                        )
                except Exception as e:
                    logger.error(
                        f"Erro ao enviar email de notificação de atualização: {e}"
                    )
                    messages.success(
                        request,
                        f"Coleta atualizada com sucesso! {motivo} Erro ao enviar notificações por e-mail.",
                    )
            else:
                messages.info(
                    request, "Nenhuma alteração detectada na coleta.")

            return redirect("lista_de_coletas")
    else:
        # Inicializa o formulário com os dados atuais
        form = CadastroColetaForm(instance=coleta)

    context = {
        "form": form,
        "titulo": "Atualizar Coleta",
        "coleta_id": id,
    }
    return render(request, "cadastro_coleta.html", context)


@login_required
def aplicar_acao(request):
    if request.method == "POST":
        acao = request.POST.get("acao")
        selecionados = request.POST.getlist("selecionar")

        if acao and selecionados:
            # Obter a primeira coleta selecionada
            coleta = get_object_or_404(TabColeta, id=selecionados[0])

            # Verificar se a coleta está cancelada antes de qualquer ação
            if coleta.status_id.id == 2:  # status 2 = cancelada
                messages.error(
                    request, "Não é possível editar uma coleta que já está cancelada."
                )
                return redirect("lista_de_coletas")

            if acao == "editar":
                return redirect("update_coleta", id=selecionados[0])
            elif acao == "detalhes":
                return redirect("info_coleta", coleta_id=selecionados[0])
            elif acao == "cancelar":
                coletas = TabColeta.objects.filter(id__in=selecionados)
                if coletas.filter(status_id=2).exists():
                    messages.error(
                        request,
                        "Não é possível cancelar coletas que já estão canceladas.",
                    )
                else:
                    coletas.update(status_id=2)
                    messages.success(
                        request, "Coletas canceladas com sucesso.")

    return redirect("lista_de_coletas")


@login_required
def detalhes_coleta_popup(request, coleta_id):
    coleta = get_object_or_404(TabColeta, id=coleta_id)
    return render(request, "detalhes_coleta_popup.html", {"coleta": coleta})


# @login_required
# def resultados_coleta(request):

#     return render(request, "resultados_campo.html")


@login_required
def cadastro_email(request):
    if request.method == "POST":
        form = EmailForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request, "Template de email cadastrado com sucesso.")
            return redirect("cadastro_email")
    else:
        form = EmailForm()

    return render(request, "cadastro_email.html", {"form": form})


@login_required
def input_laboratorio(request, coleta_id, ponto_id, frasco_id):
    """
    View para entrada de dados laboratoriais
    """

    MedidaFormSet = modelformset_factory(
        TabMedida, form=InputFisicoQuimicoForm, extra=0, fields="__all__"
    )

    coleta = get_object_or_404(TabColeta, id=coleta_id)
    ponto = get_object_or_404(TabPonto, id=ponto_id)
    frasco = get_object_or_404(TabFrasco, id=frasco_id)

    # Get amostra and envio for this specific combination
    amostra = TabAmostra.objects.filter(
        id_coleta=coleta, id_ponto=ponto, id_frasco=frasco
    ).first()

    envio = TabEnvio.objects.filter(
        id_amostra=amostra).first() if amostra else None

    # Get medidas for this envio with proper ordering using ordem_visualizacao
    medidas = (
        TabMedida.objects.filter(id_envio=envio)
        .select_related("id_envio", "id_pp", "id_pp__id_param")
        # Adicionar esta ordenação
        .order_by("id_pp__ordem_visualizacao", "id_pp__id_param__nome")
        if envio
        else TabMedida.objects.none()
    )

    # Busca anexo existente
    anexo_existente = None
    anexo_query = TabAnexoAmostra.objects.filter(
        id_envio__id_amostra__id_coleta=coleta_id,
        id_envio__id_amostra__id_ponto=ponto_id,
        id_envio__id_amostra__id_frasco=frasco_id,
    ).first()

    # Se encontrou um anexo, verifica se tem arquivo ou observação
    if anexo_query:
        anexo_existente = anexo_query
        # Se não tem arquivo nem observação, deleta o registro
        if not anexo_existente.anexo and not anexo_existente.observacao and not anexo_existente.codigo_oceanus:
            anexo_existente.delete()
            anexo_existente = None

    if request.method == "POST":
        formset = MedidaFormSet(request.POST, request.FILES, queryset=medidas)
        if formset.is_valid():
            instances = formset.save(commit=False)
            for instance in instances:
                instance.save(usuario=request.user)  # Passa o usuário atual
            formset.save_m2m()

            # Processa o anexo se houver arquivo ou observação
            primeiro_envio = instances[0].id_envio if instances else None
            if primeiro_envio:
                handle_anexo(request, primeiro_envio)

            messages.success(request, "Dados salvos com sucesso!")

            # Sempre verifica se o frasco está completo após salvar os dados
            coleta_obj = envio.id_amostra.id_coleta if envio and envio.id_amostra else None
            frasco_atual = frasco
            # Debug
            print(
                f"Verificando se o frasco {frasco_atual.id} da coleta está completo...")
            # Recupera todos os pontos esperados para a coleta
            pontos_esperados = set(TabPonto.objects.filter(
                id_setor=coleta_obj.id_setor, status=True).values_list('id', flat=True)) if coleta_obj else set()
            amostras_frasco = TabAmostra.objects.filter(
                id_coleta=coleta_obj, id_frasco=frasco_atual)
            pontos_amostrados = set(
                amostras_frasco.values_list('id_ponto', flat=True))
            frasco_completo = True
            # Verifica se todos os pontos esperados têm amostra para este frasco
            if pontos_esperados != pontos_amostrados:
                frasco_completo = False
                print(
                    f"Faltam amostras para alguns pontos do frasco {frasco_atual.id}. Esperados: {pontos_esperados}, encontrados: {pontos_amostrados}")
            else:
                # Só verifica medidas se todas as amostras existem
                for amostra in amostras_frasco:
                    envios = TabEnvio.objects.filter(id_amostra=amostra)
                    for envio_f in envios:
                        id_frasco_f = envio_f.id_amostra.id_frasco
                        id_produto_f = getattr(
                            envio_f.id_amostra, 'id_produto', None)
                        if not id_frasco_f or not id_produto_f:
                            continue
                        parametros = TabProdxparam.objects.filter(
                            id_frasco=id_frasco_f,
                            id_produto=id_produto_f,
                            status=True
                        )
                        for parametro in parametros:
                            medida_qs = TabMedida.objects.filter(
                                id_envio=envio_f, id_pp=parametro
                            ).exclude(input_valor__isnull=True).exclude(input_valor__exact="")
                            if not medida_qs.exists():
                                frasco_completo = False
                                print(
                                    f"Faltando medida para amostra {amostra.id}, envio {envio_f.id}, frasco {id_frasco_f.id}, produto {id_produto_f.id}, parâmetro {parametro.id} ({parametro.id_param.nome})")
                                break
                        if not frasco_completo:
                            break
                    if not frasco_completo:
                        break
            # Só envia e-mail se o botão Salvar foi clicado E o frasco atual estiver completo para todos os pontos
            if coleta_obj and "salvar" in request.POST:
                if coleta_obj.is_completa_frasco(frasco_atual.id):
                    # Debug
                    print(
                        f"Frasco {frasco_atual.id} da coleta {coleta_obj.id} completo! Gerando relatório e enviando e-mail...")
                    arquivo_excel = gerar_relatorio_excel_por_coleta(
                        coleta_obj, id_frasco=frasco_atual.id)
                    enviar_email_relatorio_coleta(
                        coleta_obj, arquivo_excel, request.user)
                else:
                    # Debug
                    print(
                        f"Frasco {frasco_atual.id} da coleta {coleta_obj.id} ainda não está completo. Não será gerado relatório.")

            # Find next point
            proximo_ponto = TabPonto.objects.filter(
                id_setor=coleta.id_setor, status=True, id__gt=ponto.id
            ).first()

            if proximo_ponto:
                return redirect(
                    "input_laboratorio",
                    coleta_id=coleta_id,
                    ponto_id=proximo_ponto.id,
                    frasco_id=frasco_id,
                )
            return redirect(
                "lista_campo_frasco", coleta_id=coleta_id, frasco_id=frasco_id
            )
    else:
        formset = MedidaFormSet(queryset=medidas)

    # Add parameter info to each form
    for form in formset:
        medida = form.instance
        if medida.id_pp:
            form.parametro = medida.id_pp.id_param.nome
            form.unidade = medida.id_pp.unidade
            # Adicionar informação da série classificação
            form.serie_classificacao = medida.id_pp.id_serie.nome if medida.id_pp.id_serie else "Sem série"

            # Atualizar o campo de exibição com série classificação
            parametro = medida.id_pp
            serie_classificacao = parametro.id_serie.nome if parametro.id_serie else "Sem série"
            unidade = parametro.unidade if parametro.unidade else "Sem unidade"
            display_text = f"{parametro.nome} ({unidade} - {serie_classificacao})"
            form.fields["id_pp_display"].initial = display_text

    # Get existing attachments with proper ordering
    anexos_existentes = (
        TabAnexoAmostra.objects.filter(id_envio=envio).order_by("ordem")
        if envio
        else []
    )

    # Obter todos os pontos desta coleta para navegação
    todos_pontos = list(
        TabPonto.objects.filter(id_setor=coleta.id_setor,
                                status=True).order_by("id")
    )

    # Para cada ponto, verificar se já tem dados preenchidos
    for p in todos_pontos:
        amostra = TabAmostra.objects.filter(
            id_coleta=coleta, id_ponto=p, id_frasco=frasco
        ).first()

        if amostra:
            envio = TabEnvio.objects.filter(id_amostra=amostra).first()
            if envio:
                medidas = TabMedida.objects.filter(id_envio=envio)
                p.tem_dados = any(m.input_valor for m in medidas)
            else:
                p.tem_dados = False
        else:
            p.tem_dados = False

    # A geração do relatório e envio de e-mail agora só ocorre no POST quando o botão 'Salvar' é clicado

    # Encontrar índice do ponto atual e pontos anterior/próximo
    try:
        ponto_atual_index = [p.id for p in todos_pontos].index(ponto.id)
        ponto_anterior = (
            todos_pontos[ponto_atual_index -
                         1] if ponto_atual_index > 0 else None
        )
        ponto_proximo = (
            todos_pontos[ponto_atual_index + 1]
            if ponto_atual_index < len(todos_pontos) - 1
            else None
        )
    except (ValueError, IndexError):
        ponto_anterior = None
        ponto_proximo = None

    return render(
        request,
        "input_laboratorio.html",
        {
            "formset": formset,
            "coleta": coleta,
            "ponto": ponto,
            "frasco": frasco,
            "anexo_existente": anexo_existente,
            "envio": envio,
            "has_anexos": bool(anexos_existentes),
            # Novos contextos para navegação
            "todos_pontos": todos_pontos,
        },
    )


def handle_anexo(request, envio):
    """
    Função auxiliar para processar anexos de amostras.

    Args:
        request: O objeto HttpRequest
        envio: O objeto TabEnvio associado ao anexo

    Returns:
        TabAnexoAmostra: O objeto de anexo criado/atualizado ou None
    """

    anexo_existente = TabAnexoAmostra.objects.filter(id_envio=envio).first()

    # Verifica se há novo anexo ou observação
    tem_novo_anexo = bool(request.FILES.get("anexo"))
    tem_nova_observacao = bool(request.POST.get("observacao_anexo"))
    tem_novo_codigo_oceanus = bool(request.POST.get("codigo_oceanus_anexo"))
    # Se tem novo conteúdo
    if tem_novo_anexo or tem_nova_observacao or tem_novo_codigo_oceanus:
        if anexo_existente:
            # Atualiza anexo existente
            if tem_novo_anexo:
                anexo_existente.anexo = request.FILES["anexo"]
            anexo_existente.observacao = request.POST.get(
                "observacao_anexo", "")
            anexo_existente.codigo_oceanus = request.POST.get(
                "codigo_oceanus_anexo", "")
            anexo_existente.save()

        else:
            # Cria novo anexo
            anexo_existente = TabAnexoAmostra.objects.create(
                id_envio=envio,
                anexo=request.FILES.get("anexo"),
                observacao=request.POST.get("observacao_anexo", ""),
                codigo_oceanus=request.POST.get("codigo_oceanus_anexo", ""),
            )

    # Se não tem novo conteúdo e existe um anexo vazio
    elif anexo_existente and not (anexo_existente.anexo or anexo_existente.observacao or anexo_existente.codigo_oceanus):
        anexo_existente.delete()
        anexo_existente = None

    return anexo_existente


@login_required
def resultados_todas_medidas(request):
    try:
        # Sanitiza os parâmetros
        def sanitize_param(param):
            if param:
                return param.strip()
            return ""

        campanha = sanitize_param(request.GET.get("campanha", ""))
        setor = sanitize_param(request.GET.get("setor", ""))
        ponto = sanitize_param(request.GET.get("ponto", ""))
        coleta = sanitize_param(request.GET.get("coleta", ""))

        # Adicionar filtros de data junto com os outros
        data_inicio = request.GET.get("data_inicio", "")
        data_fim = request.GET.get("data_fim", "")

        # Query base otimizada
        query = TabMedida.objects.select_related(
            "id_envio__id_amostra__id_coleta",
            "id_envio__id_amostra__id_ponto",
            "id_envio__id_amostra__id_coleta__id_setor",
            "id_envio__id_amostra__id_coleta__id_campanha",
            "id_pp__id_param",
        )

        # Aplicar filtros de data
        if data_inicio:
            query = query.filter(
                id_envio__id_amostra__id_coleta__data__gte=data_inicio)
        if data_fim:
            query = query.filter(
                id_envio__id_amostra__id_coleta__data__lte=data_fim)

        # Aplicar os mesmos filtros
        if campanha:
            query = query.filter(
                id_envio__id_amostra__id_coleta__id_campanha__nome__icontains=campanha
            )
        if setor:
            query = query.filter(
                id_envio__id_amostra__id_coleta__id_setor__nome__icontains=setor
            )
        if ponto:
            query = query.filter(
                id_envio__id_amostra__id_ponto__nome__icontains=ponto)

        # Modificar a busca de coletas para incluir nulos
        coletas = list(
            TabColeta.objects.values_list(
                "nome", flat=True).distinct().order_by("nome")
        )

        # Adiciona um valor para representar coletas sem nome
        if None in coletas:
            coletas.remove(None)
            coletas.append("Não definido")

        # Se o filtro de coleta for 'Não definido', ajustar a query
        if coleta == "Não definido":
            query = query.filter(
                id_envio__id_amostra__id_coleta__nome__isnull=True)
        elif coleta:  # Mantém o filtro original para outros casos
            query = query.filter(
                id_envio__id_amostra__id_coleta__nome__icontains=coleta
            )

        # Buscar valores únicos para filtros de forma mais eficiente
        campanhas = (
            TabMedida.objects.values_list(
                "id_envio__id_amostra__id_coleta__id_campanha__nome", flat=True
            )
            .distinct()
            .order_by("id_envio__id_amostra__id_coleta__id_campanha__nome")
        )

        setores = (
            TabMedida.objects.values_list(
                "id_envio__id_amostra__id_coleta__id_setor__nome", flat=True
            )
            .distinct()
            .order_by("id_envio__id_amostra__id_coleta__id_setor__nome")
        )

        pontos = (
            TabMedida.objects.values_list(
                "id_envio__id_amostra__id_ponto__nome", flat=True
            )
            .distinct()
            .order_by("id_envio__id_amostra__id_ponto__nome")
        )

        coletas = (
            TabColeta.objects.values_list(
                "nome", flat=True).distinct().order_by("nome")
        )

        # Paginação com validação melhorada
        PER_PAGE_CHOICES = [10, 20, 40, 80, 100]
        per_page = request.GET.get("per_page")

        try:
            per_page = int(per_page) if per_page else 10
            if per_page not in PER_PAGE_CHOICES:
                per_page = 10
        except ValueError:
            per_page = 10

        paginator = Paginator(query, per_page)
        page = request.GET.get("page", 1)
        try:
            medidas = paginator.page(page)
        except Exception:
            medidas = paginator.page(1)

        # Processar resultados de forma mais eficiente
        resultados = []
        for medida in medidas:
            try:
                amostra = medida.id_envio.id_amostra
                coleta = amostra.id_coleta
                resultado = {
                    "campanha_nome": coleta.id_campanha.nome
                    if coleta.id_campanha
                    else "N/A",
                    "coleta_nome": coleta.nome if coleta.nome else "N/A",
                    "ordem_servico": coleta.ordem_servico,
                    # Corrigido aqui
                    "etiqueta": amostra.etiqueta,
                    "parametro": medida.id_pp.id_param.nome
                    if medida.id_pp and medida.id_pp.id_param
                    else "N/A",
                    "valor": medida.input_valor if medida.input_valor else "Não medido",
                    "unidade": medida.id_pp.unidade if medida.id_pp else "",
                }
                resultados.append(resultado)
            except Exception as e:
                logger.error(f"Erro ao processar medida {medida.id}: {str(e)}")
                continue

        context = {
            "page_obj": {
                "object_list": resultados,
                "number": medidas.number,
                "paginator": medidas.paginator,
                "has_previous": medidas.has_previous(),
                "has_next": medidas.has_next(),
                "previous_page_number": medidas.previous_page_number
                if medidas.has_previous()
                else None,
                "next_page_number": medidas.next_page_number
                if medidas.has_next()
                else None,
                "start_index": medidas.start_index(),
                "end_index": medidas.end_index(),
            },
            "total_resultados": paginator.count,
            "campanhas": campanhas,
            "setores": setores,
            "pontos": pontos,
            "coletas": coletas,
            "filtros": {
                "campanha": campanha,
                "setor": setor,
                "ponto": ponto,
                "coleta": coleta,
                "data_inicio": data_inicio,  # Adicionar data_inicio ao contexto
                "data_fim": data_fim,  # Adicionar data_fim ao contexto
            },
            "per_page_choices": PER_PAGE_CHOICES,  # Adiciona as opções ao contexto
            "current_per_page": per_page,  # Adiciona o valor atual
        }

        return render(request, "resultados_todas_medidas.html", context)

    except Exception as e:
        logger.error(f"Erro ao carregar resultados: {str(e)}")
        messages.error(
            request, "Erro ao carregar os resultados. Por favor, tente novamente."
        )
        return redirect("home")


@login_required
def export_resultados_medidas_csv(request):
    try:
        # Reutilizar a mesma lógica de filtros da view principal
        def sanitize_param(param):
            if param:
                return param.strip()
            return ""

        campanha = sanitize_param(request.GET.get("campanha", ""))
        setor = sanitize_param(request.GET.get("setor", ""))
        ponto = sanitize_param(request.GET.get("ponto", ""))
        coleta = sanitize_param(request.GET.get(
            "coleta", ""))  # Adicionar esta linha

        # Query base otimizada
        query = TabMedida.objects.select_related(
            "id_envio__id_amostra__id_coleta",
            "id_envio__id_amostra__id_ponto",
            "id_envio__id_amostra__id_coleta__id_setor",
            "id_envio__id_amostra__id_coleta__id_campanha",
            "id_pp__id_param",
        )

        # Aplicar os mesmos filtros
        if campanha:
            query = query.filter(
                id_envio__id_amostra__id_coleta__id_campanha__nome__icontains=campanha
            )
        if setor:
            query = query.filter(
                id_envio__id_amostra__id_coleta__id_setor__nome__icontains=setor
            )
        if ponto:
            query = query.filter(
                id_envio__id_amostra__id_ponto__nome__icontains=ponto)
        if coleta:
            # Adicionar esta linha
            query = query.filter(
                id_envio__id_amostra__id_coleta__nome__icontains=coleta
            )

        # Adicionar filtros de data
        data_inicio = request.GET.get("data_inicio")
        data_fim = request.GET.get("data_fim")

        if data_inicio:
            query = query.filter(
                id_envio__id_amostra__id_coleta__data__gte=data_inicio)
        if data_fim:
            query = query.filter(
                id_envio__id_amostra__id_coleta__data__lte=data_fim)

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="resultados_coleta.csv"'

        writer = csv.writer(response)
        writer.writerow(
            [
                "Código Coleta",
                "Hora Início",
                "Hora Fim",
                "Ponto",
                "Temperatura",
                "pH",
                "ORP",
                "Condutividade",
                "Turbidez",
                "OD",
                "OD %",
                "TDS",
                "Salinidade",
                "Status",
                "Check Amostras",
                "Observações",
            ]
        )

        # Processar resultados de forma otimizada
        batch_size = 1000
        for medida in query.iterator(chunk_size=batch_size):
            try:
                amostra = medida.id_envio.id_amostra
                coleta = amostra.id_coleta
                row = [
                    str(coleta.id_campanha.nome if coleta.id_campanha else "N/A"),
                    str(coleta.nome if coleta.nome else "N/A"),
                    str(coleta.ordem_servico),
                    coleta.data.strftime("%d/%m/%Y") if coleta.data else "N/A",
                    str(coleta.id_setor.nome if coleta.id_setor else "N/A"),
                    str(amostra.id_ponto.nome if amostra.id_ponto else "N/A"),
                    str(amostra.etiqueta),
                    str(
                        medida.id_pp.id_param.nome
                        if medida.id_pp and medida.id_pp.id_param
                        else "N/A"
                    ),
                    str(medida.input_valor if medida.input_valor else "Não medido"),
                    str(medida.id_pp.unidade if medida.id_pp else ""),
                ]
                writer.writerow(row)
            except Exception as e:
                logger.error(f"Erro ao processar medida {medida.id}: {str(e)}")
                continue

        return response

    except Exception as e:
        logger.error(f"Erro ao exportar resultados: {str(e)}")
        messages.error(
            request, "Erro ao exportar os resultados. Por favor, tente novamente."
        )
        return redirect("resultados_todas_medidas")


@login_required
def export_resultados_medidas_xlsx(request):
    try:

        def sanitize_param(param):
            return param.strip() if param else ""

        campanha = sanitize_param(request.GET.get("campanha", ""))
        setor = sanitize_param(request.GET.get("setor", ""))
        ponto = sanitize_param(request.GET.get("ponto", ""))
        coleta = sanitize_param(request.GET.get("coleta", ""))

        # Query base otimizada
        query = TabMedida.objects.select_related(
            "id_envio__id_amostra__id_coleta",
            "id_envio__id_amostra__id_ponto",
            "id_envio__id_amostra__id_coleta__id_setor",
            "id_envio__id_amostra__id_coleta__id_campanha",
            "id_pp__id_param",
        )

        # Aplicar filtros
        if campanha:
            query = query.filter(
                id_envio__id_amostra__id_coleta__id_campanha__nome__icontains=campanha
            )
        if setor:
            query = query.filter(
                id_envio__id_amostra__id_coleta__id_setor__nome__icontains=setor
            )
        if ponto:
            query = query.filter(
                id_envio__id_amostra__id_ponto__nome__icontains=ponto)
        if coleta:
            query = query.filter(
                id_envio__id_amostra__id_coleta__nome__icontains=coleta
            )

        # Adicionar filtros de data
        data_inicio = request.GET.get("data_inicio")
        data_fim = request.GET.get("data_fim")

        if data_inicio:
            query = query.filter(
                id_envio__id_amostra__id_coleta__data__gte=data_inicio)
        if data_fim:
            query = query.filter(
                id_envio__id_amostra__id_coleta__data__lte=data_fim)

        wb = Workbook()
        ws = wb.active
        ws.title = "Resultados Medidas"

        # Definir cabeçalhos
        headers = [
            "Campanha",
            "Coleta",
            "Ordem Serviço",
            "Data",
            "Setor",
            "Ponto",
            "Etiqueta",
            "Parâmetro",
            "Valor",
            "Unidade",
        ]

        # Estilo para cabeçalho
        header_font = Font(bold=True)
        header_fill = PatternFill(
            start_color="CCCCCC", end_color="CCCCCC", fill_type="solid"
        )

        # Aplicar cabeçalhos
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.font = header_font
            cell.fill = header_fill

        # Preencher dados
        row = 2
        batch_size = 1000
        for medida in query.iterator(chunk_size=batch_size):
            try:
                amostra = medida.id_envio.id_amostra
                coleta = amostra.id_coleta

                ws.cell(
                    row=row,
                    column=1,
                    value=str(
                        coleta.id_campanha.nome if coleta.id_campanha else "N/A"),
                )
                ws.cell(
                    row=row, column=2, value=str(coleta.nome if coleta.nome else "N/A")
                )
                ws.cell(row=row, column=3, value=str(coleta.ordem_servico))
                ws.cell(
                    row=row,
                    column=4,
                    value=coleta.data.strftime(
                        "%d/%m/%Y") if coleta.data else "N/A",
                )
                ws.cell(
                    row=row,
                    column=5,
                    value=str(
                        coleta.id_setor.nome if coleta.id_setor else "N/A"),
                )
                ws.cell(
                    row=row,
                    column=6,
                    value=str(
                        amostra.id_ponto.nome if amostra.id_ponto else "N/A"),
                )
                ws.cell(row=row, column=7, value=str(amostra.etiqueta))
                ws.cell(
                    row=row,
                    column=8,
                    value=str(
                        medida.id_pp.id_param.nome
                        if medida.id_pp and medida.id_pp.id_param
                        else "N/A"
                    ),
                )
                ws.cell(
                    row=row,
                    column=9,
                    value=str(
                        medida.input_valor if medida.input_valor else "Não medido"
                    ),
                )
                ws.cell(
                    row=row,
                    column=10,
                    value=str(medida.id_pp.unidade if medida.id_pp else ""),
                )

                row += 1
            except Exception as e:
                logger.error(f"Erro ao processar medida {medida.id}: {str(e)}")
                continue

        # Ajustar largura das colunas
        for column in ws.columns:
            max_length = 0
            column_letter = get_column_letter(column[0].column)
            for cell in column:
                if len(str(cell.value)) > max_length:
                    adjusted_width = max_length + 2
                    ws.column_dimensions[column_letter].width = adjusted_width

        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = (
            f'attachment; filename="resultados_medidas_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx"'
        )

        wb.save(response)
        return response

    except Exception as e:
        logger.error(f"Erro ao exportar resultados: {str(e)}")
        messages.error(
            request, "Erro ao exportar os resultados. Por favor, tente novamente."
        )
        return redirect("resultados_todas_medidas")


@login_required
def atualizar_status_coleta(request, coleta_id):
    """
    Updates the status of a specific coleta (collection) and logs the change.

    Args:
        request (HttpRequest): The HTTP request object containing POST data with the new status and reason.
        coleta_id (int): The ID of the coleta to update.

    Returns:
        JsonResponse: A JSON response indicating success or failure of the operation.
    """
    if request.method == "POST":
        try:
            coleta = TabColeta.objects.select_related(
                "status_id").get(id=coleta_id)
            status_antigo = (
                coleta.status_id.status if coleta.status_id else "Não definido"
            )
            novo_status = TabStatusColeta.objects.get(
                id=request.POST.get("status"))
            motivo = request.POST.get("motivo")

            # Debug
            print(f"Status atual: {coleta.status_id}")
            logger.debug(f"Novo status ID: {novo_status.id}")
            logger.debug(f"Motivo: {motivo}")

            # Só faz alterações se realmente houver mudança
            if coleta.status_id is None or novo_status.id != coleta.status_id.id:
                coleta.status_id = novo_status
                coleta.atualizado_por = request.user
                coleta.atualizado_em = timezone.now()
                coleta.save()

                # Registra o log com o motivo
                TabLogColeta.objects.create(
                    id_coleta=coleta,
                    acao=f"Status alterado para {novo_status.status}",
                    motivo=motivo,
                    usuario=request.user,
                )

                # Notificar por e-mail
                subject = f"Status da coleta {coleta.ordem_servico} foi alterado"
                message = f"Olá,\n\nO status da coleta com ordem de serviço {coleta.ordem_servico} foi alterado de '{status_antigo}' para '{novo_status.status}' por {request.user.username}.\n\n"
                message += f"Motivo da alteração: {motivo}\n\n"
                message += f"Acesse o sistema em {settings.SITE_URL}/info_coleta/{coleta.id} para mais informações.\n\n"
                message += "Este é um e-mail automático, favor não responder."

                try:
                    grupo_coleta = Group.objects.filter(
                        name__iexact="coleta").first()
                    if grupo_coleta:
                        usuarios_coleta = grupo_coleta.user_set.all()
                        recipient_list = [
                            usuario.email
                            for usuario in usuarios_coleta
                            if usuario.email
                        ]

                        if recipient_list:
                            # Iniciar thread para envio de email
                            Thread(
                                target=enviar_email_async,
                                args=(
                                    subject,
                                    message,
                                    settings.EMAIL_HOST_USER,
                                    recipient_list,
                                ),
                            ).start()
                except Exception as e:
                    logger.error(
                        f"Erro ao enviar email de notificação de alteração de status: {e}"
                    )

            return JsonResponse({"success": True})

        except Exception as e:
            print(f"Erro ao atualizar status: {str(e)}")  # Debug
            return JsonResponse({"success": False, "error": str(e)}, status=400)

    return JsonResponse({"success": False, "error": "Método não permitido"}, status=405)


@login_required
def generate_sample_labels(request, coleta_id):
    coleta = TabColeta.objects.get(id=coleta_id)
    amostras = TabAmostra.objects.filter(
        id_coleta=coleta).exclude(id_frasco__id=1)

    # Parâmetros fixos
    margin = 1 * mm
    label_spacing = 5 * mm
    label_width = 47 * mm
    label_height = 25 * mm
    labels_per_row = 2
    labels_per_page = 2

    PAGE_WIDTH = (
        (label_width * labels_per_row)
        + (label_spacing * (labels_per_row - 1))
        + (2 * margin)
    )
    PAGE_HEIGHT = label_height + (2 * margin)
    PAGE_SIZE = (PAGE_WIDTH, PAGE_HEIGHT)

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=PAGE_SIZE)

    # Carregar e preparar a marca d'água
    watermark_path = os.path.join(
        settings.STATIC_ROOT,
        "/home/marcus/desenvolvimento/LAGUNA/simal/static/images/logo_projeto_lagoa_viva.png",
    )
    try:
        # Abrir e converter a imagem
        watermark_img = Image.open(watermark_path)
        if (watermark_img.mode != "RGBA"):
            watermark_img = watermark_img.convert("RGBA")

        # Ajustar o tamanho da marca d'água para ser menor e proporcional
        watermark_width = label_width * 0.35  # Reduzido para 35% da largura da etiqueta
        aspect_ratio = watermark_img.height / watermark_img.width
        watermark_height = watermark_width * aspect_ratio

        # Ajustar a transparência da imagem
        alpha = Image.new("RGBA", watermark_img.size, (255, 255, 255, 128))
        watermark_img = Image.blend(watermark_img, alpha, 0.2)

        # Salvar em buffer temporário
        temp_watermark = BytesIO()
        watermark_img.save(temp_watermark, format="PNG")
        temp_watermark.seek(0)
    except Exception as e:
        print(f"Erro ao carregar marca d'água: {str(e)}")
        watermark_path = None

    # Processar amostras
    total_amostras = len(amostras)
    for i in range(0, total_amostras, labels_per_page):
        page_amostras = amostras[i: i + labels_per_page]
        is_last_page = i + labels_per_page >= total_amostras
        is_odd_last_page = is_last_page and (
            total_amostras % labels_per_page == 1)

        if is_odd_last_page:
            # Se for a última página com uma única etiqueta, alinhar à esquerda
            start_x = margin
        else:
            # Caso contrário, centralizar as etiquetas na página
            total_width = (label_width * len(page_amostras)) + (
                label_spacing * (len(page_amostras) - 1)
            )
            start_x = (PAGE_WIDTH - total_width) / 2

        for idx, amostra in enumerate(page_amostras):
            x = start_x + (idx * (label_width + label_spacing))
            y = margin

            # Adicionar código da etiqueta
            c.setFont("Helvetica-Bold", 8)
            c.drawString(x + 2 * mm, y + label_height -
                         4 * mm, f"{amostra.etiqueta}")

            # Gerar e desenhar QR code
            qr = qrcode.QRCode(version=1, box_size=10, border=0)
            url = request.build_absolute_uri(
                reverse(
                    "input_laboratorio",
                    args=[coleta.id, amostra.id_ponto.id, amostra.id_frasco.id],
                )
            )
            qr.add_data(url)
            qr.make(fit=True)
            qr_img = qr.make_image(fill_color="black", back_color="white")

            # Salvar QR code em buffer
            qr_buffer = BytesIO()
            qr_img.save(qr_buffer, format="PNG")
            qr_buffer.seek(0)

            # Desenhar QR code
            qr_size = 18 * mm
            c.drawImage(
                ImageReader(qr_buffer),
                x + 2 * mm,
                y + 2 * mm,
                width=qr_size,
                height=qr_size,
            )

            # Configurar posição do texto à direita do QR code
            text_x = x + (qr_size + 4 * mm)

            # Desenhar informações
            c.setFont("Helvetica-Bold", 16)
            c.drawString(text_x, y + 15 * mm, f"{amostra.id_ponto.nome}")
            c.setFont("Helvetica-Bold", 9)
            c.drawString(text_x, y + 11 * mm, f"{coleta.id_setor.nome}")
            c.drawString(text_x, y + 7 * mm,
                         f"{coleta.data.strftime('%d/%m/%Y')}")
            c.drawString(text_x, y + 3 * mm, f"{amostra.id_frasco.nome}")

            # Desenhar marca d'água à direita do QR code
            if watermark_path:
                try:
                    watermark_x = text_x + 2 * mm  # Posiciona após o texto
                    watermark_y = (
                        y + (label_height - watermark_height) / 2
                    )  # Centraliza verticalmente

                    c.saveState()
                    c.setFillAlpha(0.3)  # Reduz a opacidade para 30%
                    c.drawImage(
                        ImageReader(temp_watermark),
                        watermark_x,
                        watermark_y,
                        width=watermark_width,
                        height=watermark_height,
                        mask="auto",
                    )
                    c.restoreState()
                except Exception as e:
                    print(f"Erro ao desenhar marca d'água: {str(e)}")

        if i + labels_per_page < total_amostras:
            c.showPage()

    c.save()
    buffer.seek(0)

    response = HttpResponse(buffer, content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="etiquetas_coleta_{coleta_id}.pdf"'
    )

    return response


@login_required
def new_home(request):
    try:
        # Buscar status e contagens em uma única query
        status_counts = (
            TabColeta.objects.values("status_id__status", "status_id__cor")
            .annotate(count=Count("id"))
            .order_by("status_id__status")
        )

        # Criar dicionário de status e garantir que todos os status tenham uma contagem
        all_status = {
            status.status: {"cor": status.cor, "count": 0}
            for status in TabStatusColeta.objects.all()
        }

        # Buscar totais para os cards
        total_coletas = TabColeta.objects.count()
        coletas_pendentes = TabColeta.objects.filter(
            Q(
                status_id__status__in=[
                    "Adiada",
                    "Prorrogada",
                    "Programada",
                    "Em andamento",
                ]
            )
            | Q(status_id__isnull=True)
        ).count()
        coletas_finalizadas = TabColeta.objects.filter(
            status_id__status="Concluída"
        ).count()
        coletas_esperando_resultados = TabColeta.objects.filter(
            status_id__status="Aguardando resultados"
        ).count()

        # Atualizar contagens para o gráfico
        for item in status_counts:
            status = item["status_id__status"]
            if status in all_status:
                all_status[status]["count"] = item["count"]

        # Dados para o novo gráfico de coletas por setor
        coletas_por_setor = (
            TabColeta.objects.values("id_setor__nome", "data")
            .annotate(total=Count("id"))
            .order_by("id_setor__nome", "data")
        )

        # Organizar dados para o gráfico de linha
        setores_dados = {}
        datas = set()

        for coleta in coletas_por_setor:
            setor = coleta["id_setor__nome"] or "Não definido"
            data = (
                coleta["data"].strftime("%Y-%m-%d")
                if coleta["data"]
                else "Não definido"
            )
            total = coleta["total"]

            if setor not in setores_dados:
                setores_dados[setor] = {}

            setores_dados[setor][data] = total
            datas.add(data)

        # Converte para formato do gráfico
        datas_ordenadas = sorted(list(datas))
        series_data = []

        for setor, dados in setores_dados.items():
            series_data.append(
                {
                    "name": setor,
                    "data": [dados.get(data, 0) for data in datas_ordenadas],
                }
            )

        # Preparar eventos do calendário
        coletas = (
            TabColeta.objects.select_related("status_id", "id_setor")
            .filter(
                data__isnull=False  # Garantir que só pegaremos coletas com data
            )
            .order_by("data")
        )

        calendar_events = []

        print("Total de coletas encontradas:", coletas.count())  # Debug

        for coleta in coletas:
            print(f"Processando coleta {coleta.id}:")  # Debug
            print(f"- Data: {coleta.data}")
            print(f"- Ordem de serviço: {coleta.ordem_servico}")
            print(
                f"- Setor: {coleta.id_setor.nome if coleta.id_setor else 'N/A'}")

            if coleta.data:
                event = {
                    "id": coleta.id,
                    "title": f"{coleta.id_setor.nome if coleta.id_setor else 'N/A'}",
                    "start": coleta.data.strftime("%Y-%m-%d"),
                    "backgroundColor": coleta.status_id.cor
                    if coleta.status_id
                    else "#6c757d",
                    "borderColor": coleta.status_id.cor
                    if coleta.status_id
                    else "#6c757d",
                    "textColor": "#ffffff",
                    "allDay": True,
                }
                calendar_events.append(event)
                print(f"- Evento criado: {event}")  # Debug
            else:
                print("- Coleta sem data definida")  # Debug

        # Debug do JSON final
        # calendar_events_json = json.dumps(calendar_events, default=str)
        # print("JSON final dos eventos:", calendar_events_json)

        context = {
            "total_coletas": total_coletas,
            "coletas_pendentes": coletas_pendentes,
            "coletas_finalizadas": coletas_finalizadas,
            "coletas_esperando_resultados": coletas_esperando_resultados,
            "chart_data": {
                "labels": list(all_status.keys()),
                "counts": [data["count"] for data in all_status.values()],
                "colors": [data["cor"] for data in all_status.values()],
            },
            "timeline_data": {"labels": datas_ordenadas, "series": series_data},
            "calendar_events": json.dumps(calendar_events, cls=DjangoJSONEncoder),
        }

        return render(request, "new_home.html", context)

    except Exception as e:
        print(f"Erro na view new_home: {str(e)}")
        import traceback

        traceback.print_exc()  # Imprime o traceback completo
        messages.error(request, "Erro ao carregar o dashboard.")
        return redirect("home")


def convert_to_float(value):
    """Helper function to convert values to float, handling 'ND' and other non-numeric values"""
    try:
        if value is None:
            return None

        # Se já for um float, retorna diretamente
        if isinstance(value, (float, int)):
            return float(value)

        # Se for uma string, verifica se não é 'ND'
        if isinstance(value, str) and value.upper() != 'ND':
            return float(value)
    except (ValueError, TypeError):
        pass
    return None


@login_required
def dashboard_parametros(request):
    # Initialize ALL variables at the very beginning to ensure they're in function scope
    tipo_visualizacao = request.GET.get('tipo', 'ponto')
    parametro_id = request.GET.get('parametro')
    ponto_id = request.GET.get('ponto')
    setor_id = request.GET.get('setor')

    # Usar nomes diferentes para as variáveis IQA para evitar conflito
    setor_iqa_param = request.GET.get('setor_iqa')
    mes_ano_param = request.GET.get('mes_ano')

    # Initialize other variables that might be used in context
    dados_grafico = None
    dados_grafico_setor = None
    dados_grafico_tempo = None
    dados_grafico_tratamento = None
    dados_grafico_estacoes = None
    dados_grafico_iqa = None
    mapa_iqa = None
    parametro_nome_display = None

    # Add campaign selection
    campanhas = TabColeta.objects.all().order_by('-data')
    campanha_id = request.GET.get('campanha')

    if campanha_id:
        campanha_selecionada = TabColeta.objects.get(id=campanha_id)
    else:
        campanha_selecionada = campanhas.first()

    # Mantém apenas os parâmetros regulares, excluindo os frascos de bentos
    parametros = (TabProdxparam.objects
                  .filter(status=True)
                  .exclude(id_frasco_id__in=[5, 6, 7])
                  .select_related('id_param')
                  .order_by('id_param__nome'))

    # Obtém todos os pontos ordenados pelo id
    pontos = TabPonto.objects.all().order_by('id')

    # Obtém todos os setores ordenados pelo nome
    setores = TabSetor.objects.all().order_by('nome')

    # Verifica se há parâmetros na consulta
    tem_parametros = 'parametro' in request.GET or 'ponto' in request.GET or 'setor' in request.GET

    # Se não há parâmetros na consulta, redirecionar com valores padrão
    if not tem_parametros:
        redirect_params = {}

        # Adicionar tipo de visualização à URL
        redirect_params['tipo'] = tipo_visualizacao

        # Valores padrão para cada tipo de visualização
        if tipo_visualizacao == 'ponto':
            # Encontrar o parâmetro pH
            ph_param = parametros.filter(
                id_param__nome__icontains='ph').first()
            pt01 = pontos.filter(nome__iexact='Pt01').first() or pontos.first()

            if ph_param and pt01:
                redirect_params['parametro'] = ph_param.id
                redirect_params['ponto'] = pt01.id

        elif tipo_visualizacao == 'setor':
            # Encontrar o parâmetro pH
            ph_param = parametros.filter(
                id_param__nome__icontains='ph').first()
            # Buscar especificamente o setor "Lagoa de Araçatiba"
            setor_aracatiba = setores.filter(nome__icontains='araçatiba').first(
            ) or setores.filter(nome__icontains='aracatiba').first()

            if ph_param and setor_aracatiba:
                redirect_params['parametro'] = ph_param.id
                redirect_params['setor'] = setor_aracatiba.id
            elif ph_param and setores.exists():
                # Fallback para o primeiro setor se "Lagoa de Araçatiba" não for encontrado
                redirect_params['parametro'] = ph_param.id
                redirect_params['setor'] = setores.first().id

                # Nova lógica para o tipo 'tempo'
        elif tipo_visualizacao == 'tempo':
            # Encontrar o parâmetro pH
            ph_param = parametros.filter(
                id_param__nome__icontains='ph').first()
            # Buscar especificamente o setor "Lagoa de Araçatiba"
            setor_aracatiba = setores.filter(nome__icontains='araçatiba').first(
            ) or setores.filter(nome__icontains='aracatiba').first()

            if ph_param and setor_aracatiba:
                redirect_params['parametro'] = ph_param.id
                redirect_params['setor'] = setor_aracatiba.id
            elif ph_param and setores.exists():
                redirect_params['parametro'] = ph_param.id
                redirect_params['setor'] = setores.first().id

        # Redirecionar apenas se tiver parâmetros para adicionar
        if len(redirect_params) > 1:  # > 1 porque sempre terá pelo menos o 'tipo'
            base_url = reverse('dashboard_parametros')
            query_string = urllib.parse.urlencode(redirect_params)
            return redirect(f"{base_url}?{query_string}")

    # Processa seleção do usuário
    parametro_id = request.GET.get('parametro')
    ponto_id = request.GET.get('ponto')
    setor_id = request.GET.get('setor')
    dados_grafico = None
    dados_grafico_setor = None
    dados_grafico_tempo = None

    if parametro_id:
        if tipo_visualizacao == 'ponto' and ponto_id:
            # Lógica para visualização por ponto
            medidas = TabMedida.objects.filter(
                id_pp_id=parametro_id,
                id_envio__id_amostra__id_ponto_id=ponto_id
            ).select_related(
                'id_envio__id_amostra__id_coleta'
            ).order_by('id_envio__id_amostra__id_coleta__data')
            # Prepara dados para o gráfico
            dados_grafico = {"datas": [], "valores": []}

            for medida in medidas:
                if medida.valor and medida.id_envio.id_amostra.id_coleta.data:
                    dados_grafico['datas'].append(
                        medida.id_envio.id_amostra.id_coleta.data.strftime(
                            '%Y-%m-%d')
                    )
                    dados_grafico['valores'].append(float(medida.valor))

        elif tipo_visualizacao == 'setor' and setor_id:
            # Lógica para visualização por setor
            medidas = TabMedida.objects.filter(
                id_pp_id=parametro_id,
                id_envio__id_amostra__id_ponto__id_setor=setor_id
            ).select_related(
                'id_envio__id_amostra__id_coleta',
                'id_envio__id_amostra__id_ponto'
            ).order_by('id_envio__id_amostra__id_coleta__data')

            # Agrupa medidas por data e calcula média
            valores_por_data = {}

            # Coletar dados dos pontos individuais
            pontos_data = {}  # Dicionário de dados por data
            todos_pontos = set()  # Conjunto de todos os pontos

            for medida in medidas:
                data = medida.id_envio.id_amostra.id_coleta.data
                ponto_nome = medida.id_envio.id_amostra.id_ponto.nome
                if data and medida.valor:
                    data_str = data.strftime('%Y-%m-%d')

                    # Adicionar ponto ao conjunto de todos os pontos
                    todos_pontos.add(ponto_nome)

                    # Inicializar dicionário para esta data se não existir
                    if data_str not in pontos_data:
                        pontos_data[data_str] = {}

                    # Adicionar valor para este ponto nesta data
                    try:
                        valor = float(medida.valor)
                        pontos_data[data_str][ponto_nome] = valor
                    except (ValueError, TypeError):
                        continue

                    if data_str not in valores_por_data:
                        valores_por_data[data_str] = {"soma": 0, "count": 0}
                    try:
                        valor = float(medida.valor)
                        valores_por_data[data_str]['soma'] += valor
                        valores_por_data[data_str]['count'] += 1
                    except (ValueError, TypeError):
                        continue

         # Calcula as médias e prepara dados para o gráfico
            dados_grafico_setor = {
                "datas": [],
                "valores": [],
                "todos_pontos": list(todos_pontos),
                "pontos_data": []
            }

            for data in sorted(valores_por_data.keys()):
                dados = valores_por_data[data]
                if dados['count'] > 0:
                    media = dados['soma'] / dados['count']
                    dados_grafico_setor['datas'].append(data)
                    dados_grafico_setor['valores'].append(round(media, 2))
                    # Adicionar dados de pontos individuais para esta data
                    dados_grafico_setor['pontos_data'].append(
                        pontos_data.get(data, {}))

                # Nova lógica para visualização "Por Tempo"
        # Dentro da função dashboard_parametros, modifique a lógica para tipo_visualizacao == 'tempo'
        elif tipo_visualizacao == 'tempo' and setor_id and parametro_id:
            # Buscar medidas para este setor e parâmetro
            medidas = TabMedida.objects.filter(
                id_pp_id=parametro_id,
                id_envio__id_amostra__id_ponto__id_setor=setor_id
            ).select_related(
                'id_envio__id_amostra__id_coleta',
                'id_envio__id_amostra__id_ponto'
            ).order_by('id_envio__id_amostra__id_coleta__data')

            # Definir data de corte para "pré-tratamento"
            setor = TabSetor.objects.get(id=setor_id)
            pre_tratamento_cutoff = None

            # Define cutoff date based on sector ID
            if setor.id == 9:  # Araçatiba
                pre_tratamento_cutoff = datetime(2021, 11, 1)
            elif setor.id == 3:  # Jacaroá
                pre_tratamento_cutoff = datetime(2024, 4, 1)
            elif setor.id == 10:  # Spar
                # Ajuste esta data conforme necessário
                pre_tratamento_cutoff = datetime(2024, 4, 1)
            elif setor.id == 4:  # Maricá
                # Ajuste esta data conforme necessário
                pre_tratamento_cutoff = datetime(2024, 4, 1)
            else:
                # Para outros setores, usar uma data padrão
                pre_tratamento_cutoff = datetime(2022, 1, 1)

            # Obter todos os pontos do setor
            pontos_do_setor = TabPonto.objects.filter(
                id_setor=setor).order_by('nome')

            # Estrutura para armazenar os dados agrupados
            dados_tempo_por_ponto = {
                'pontos': [],
                'pre_tratamento': [],
                'pos_tratamento': []
            }

            # Atualizar a verificação de períodos com dados
            periodos_com_dados = {
                'pre_tratamento': False,
                'pos_tratamento': False
            }

            # Para cada ponto, calcular as médias por período
            for ponto in pontos_do_setor:
                # Filtrar medidas para este ponto específico
                medidas_ponto = TabMedida.objects.filter(
                    id_pp_id=parametro_id,
                    id_envio__id_amostra__id_ponto=ponto
                ).select_related('id_envio__id_amostra__id_coleta')

                if medidas_ponto.exists():
                    # Adicionar o ponto à lista
                    dados_tempo_por_ponto['pontos'].append(ponto.nome)

                    # Calcular média para pré-tratamento
                    medidas_pre = medidas_ponto.filter(
                        id_envio__id_amostra__id_coleta__data__lt=pre_tratamento_cutoff)
                    valores_pre = [convert_to_float(
                        m.valor) for m in medidas_pre if m.valor]
                    valores_pre = [v for v in valores_pre if v is not None]
                    media_pre = sum(valores_pre) / \
                        len(valores_pre) if valores_pre else None
                    dados_tempo_por_ponto['pre_tratamento'].append(
                        round(media_pre, 2) if media_pre is not None else None)
                    if media_pre is not None:
                        periodos_com_dados['pre_tratamento'] = True

                    # Calcular média para pós-tratamento
                    medidas_pos = medidas_ponto.filter(
                        id_envio__id_amostra__id_coleta__data__gte=pre_tratamento_cutoff)
                    valores_pos = [convert_to_float(
                        m.valor) for m in medidas_pos if m.valor]
                    valores_pos = [v for v in valores_pos if v is not None]
                    media_pos = sum(valores_pos) / \
                        len(valores_pos) if valores_pos else None
                    dados_tempo_por_ponto['pos_tratamento'].append(
                        round(media_pos, 2) if media_pos is not None else None)
                    if media_pos is not None:
                        periodos_com_dados['pos_tratamento'] = True

            # Verificar se há algum dado disponível
            tem_dados = any(periodos_com_dados.values())

            # Formatar mensagens sobre dados ausentes
            periodos_ausentes = [
                periodo for periodo, tem_dados in periodos_com_dados.items() if not tem_dados]
            mensagem_periodos_ausentes = None

            if periodos_ausentes:
                mensagem_periodos_ausentes = f"Não há dados disponíveis para os seguintes períodos: {', '.join(periodos_ausentes)}"

            # Atualizar a variável dados_grafico_tempo com os novos períodos
            dados_grafico_tempo = {
                'pontos': dados_tempo_por_ponto['pontos'],
                'periodos': {
                    'pre_tratamento': {
                        'nome': 'Pré-tratamento',
                        'valores': dados_tempo_por_ponto['pre_tratamento'],
                        'tem_dados': periodos_com_dados['pre_tratamento']
                    },
                    'pos_tratamento': {
                        'nome': 'Pós-tratamento',
                        'valores': dados_tempo_por_ponto['pos_tratamento'],
                        'tem_dados': periodos_com_dados['pos_tratamento']
                    }
                },
                'tem_dados': tem_dados,
                'mensagem_periodos_ausentes': mensagem_periodos_ausentes
            }

    # Para exibir o nome correto do parâmetro no título
    parametro_nome_display = None
    if parametro_id:
        try:
            param = TabProdxparam.objects.get(id=parametro_id)
            parametro_nome_display = param.id_param.nome
        except:
            parametro_nome_display = "Parâmetro desconhecido"

    # Add logic for pre/post treatment comparison
    dados_grafico_tratamento = None
    if tipo_visualizacao == 'tratamento' and parametro_id and setor_id:
        setor = TabSetor.objects.get(id=setor_id)

        # Define cutoff date based on sector ID
        cutoff_date = None
        if setor.id == 9:  # Araçatiba
            cutoff_date = datetime(2021, 11, 1)
        elif setor.id == 3:  # Jacaroá
            cutoff_date = datetime(2024, 4, 1)
        elif setor.id == 10:  # Spar
            # Ajuste esta data conforme necessário
            cutoff_date = datetime(2024, 4, 1)
        elif setor.id == 4:  # Maricá
            # Ajuste esta data conforme necessário
            cutoff_date = datetime(2024, 4, 1)
            # Para outros setores, usar uma data padrão
        else:
            cutoff_date = datetime(2022, 1, 1)

        # Get all points in the sector
        pontos_setor = TabPonto.objects.filter(id_setor=setor).order_by('nome')

        dados_grafico_tratamento = {
            'pontos': [],
            'pre_tratamento': [],
            'pos_tratamento': []
        }

        for ponto in pontos_setor:
            # Get measurements for this point
            medidas_ponto = TabMedida.objects.filter(
                id_pp_id=parametro_id,
                id_envio__id_amostra__id_ponto=ponto
            ).select_related('id_envio__id_amostra__id_coleta')

            # Calculate pre-treatment average
            medidas_pre = medidas_ponto.filter(
                id_envio__id_amostra__id_coleta__data__lt=cutoff_date
            )
            valores_pre = [convert_to_float(m.valor)
                           for m in medidas_pre if m.valor]
            # Filter out None values
            valores_pre = [v for v in valores_pre if v is not None]
            media_pre = sum(valores_pre) / \
                len(valores_pre) if valores_pre else None

            # Calculate post-treatment average
            medidas_pos = medidas_ponto.filter(
                id_envio__id_amostra__id_coleta__data__gte=cutoff_date)
            valores_pos = [convert_to_float(m.valor)
                           for m in medidas_pos if m.valor]
            # Filter out None values
            valores_pos = [v for v in valores_pos if v is not None]
            media_pos = sum(valores_pos) / \
                len(valores_pos) if valores_pos else None

            if media_pre is not None or media_pos is not None:
                dados_grafico_tratamento['pontos'].append(ponto.nome)
                dados_grafico_tratamento['pre_tratamento'].append(
                    round(media_pre, 2) if media_pre is not None else None
                )
                dados_grafico_tratamento['pos_tratamento'].append(
                    round(media_pos, 2) if media_pos is not None else None
                )

    # Add logic for seasonal comparison
    dados_grafico_estacoes = None
    if tipo_visualizacao == 'estacoes' and parametro_id and setor_id:
        setor = TabSetor.objects.get(id=setor_id)
        pontos_setor = TabPonto.objects.filter(id_setor=setor).order_by('nome')

        dados_grafico_estacoes = {
            'pontos': [],
            'estacao_chuvosa': [],
            'estacao_seca': []
        }

        for ponto in pontos_setor:
            medidas = TabMedida.objects.filter(
                id_pp_id=parametro_id,
                id_envio__id_amostra__id_ponto__id_setor=setor_id
            ).select_related(
                'id_envio__id_amostra__id_coleta',
                'id_envio__id_amostra__id_ponto'
            ).order_by('id_envio__id_amostra__id_coleta__data')

            # Estação chuvosa (abril a outubro)
            medidas_chuvosa = medidas.filter(
                id_envio__id_amostra__id_coleta__data__month__range=(4, 10)
            )
            valores_chuvosa = [convert_to_float(
                m.valor) for m in medidas_chuvosa if m.valor]
            valores_chuvosa = [v for v in valores_chuvosa if v is not None]
            media_chuvosa = sum(valores_chuvosa) / \
                len(valores_chuvosa) if valores_chuvosa else None

            # Estação seca (novembro a março)
            medidas_seca = medidas.filter(
                id_envio__id_amostra__id_coleta__data__month__in=[
                    11, 12, 1, 2, 3]
            )
            valores_seca = [convert_to_float(m.valor)
                            for m in medidas_seca if m.valor]
            valores_seca = [v for v in valores_seca if v is not None]
            media_seca = sum(valores_seca) / \
                len(valores_seca) if valores_seca else None

            if media_chuvosa is not None or media_seca is not None:
                dados_grafico_estacoes['pontos'].append(ponto.nome)
                dados_grafico_estacoes['estacao_chuvosa'].append(
                    round(media_chuvosa, 2) if media_chuvosa is not None else None
                )
                dados_grafico_estacoes['estacao_seca'].append(
                    round(media_seca, 2) if media_seca is not None else None
                )

    # Add logic for IQA
    dados_grafico_iqa = None
    mapa_iqa = None
    if tipo_visualizacao == 'iqa':
        parametros_iqa = [
            "OD", "Escherichia coli", "DBOs", "Nitrogênio Total",
            "Fosfato", "pH", "Turbidez", "TDS",
            "Nitrito", "Nitrato", "Nitrogênio Amoniacal", "Amônia", "Amônio" 
        ]

        # Find the specific OD parameter from TabProdxparam that measures % (percentage)
        od_percentage_param = TabProdxparam.objects.filter(
            id_param__nome="OD",
            unidade__icontains="%"  # Filter for the percentage unit
        ).first()


        # MUDANÇA: Buscar TODOS os parâmetros IQA sem filtro especial para OD
        query_base = TabMedida.objects.filter(
            id_pp__id_param__nome__in=parametros_iqa
        ).select_related(
            'id_envio__id_amostra__id_coleta',
            'id_envio__id_amostra__id_ponto'
        )

        # MUDANÇA: Aplicar filtros de setor e mês
        if setor_iqa_param:
            query_base = query_base.filter(
                id_envio__id_amostra__id_ponto__id_setor_id=setor_iqa_param
            )
        
        if mes_ano_param:
            try:
                ano, mes = map(int, mes_ano_param.split('-'))
                query_base = query_base.filter(
                    id_envio__id_amostra__id_coleta__data__year=ano,
                    id_envio__id_amostra__id_coleta__data__month=mes
                )
            except (ValueError, AttributeError):
                pass

        dados_iqa = query_base

        # Verificar se existem dados antes de criar o DataFrame
        if dados_iqa.exists():
            df = pd.DataFrame(list(dados_iqa.values(
                'id_envio__id_amostra__id_coleta__data',
                'id_envio__id_amostra__id_ponto__nome',
                'id_envio__id_amostra__id_ponto__lat',
                'id_envio__id_amostra__id_ponto__lon',
                'id_envio__id_amostra__id_coleta__id_setor__nome',
                'id_pp__id_param__nome',
                'valor'
            )))

            # Verificar se há dados válidos
            if not df.empty:
                # Convertendo valor para numérico
                df['valor'] = pd.to_numeric(df['valor'], errors='coerce')

                df.columns = ['data', 'ponto', 'lat',
                              'lon', 'setor', 'parametro', 'valor']

                # MUDANÇA: Pivot table incluindo os novos parâmetros
                df_pivot = df.pivot_table(
                    index=['data', 'ponto', 'lat', 'lon', 'setor'],
                    columns='parametro',
                    values='valor',
                    aggfunc='mean'  # Calcula a média se houver múltiplas medições no mesmo mês
                ).reset_index()

                # Preencher valores ausentes com 0
                df_pivot = df_pivot.fillna(0)

                # Calcular IQA
                df_pivot['IQA'] = df_pivot.apply(calculate_iqa, axis=1)

                # Criar mapa centralizado na média das coordenadas
                if not df_pivot.empty and df_pivot['lat'].notna().any() and df_pivot['lon'].notna().any():
                    lat_medio = df_pivot['lat'].mean()
                    lon_medio = df_pivot['lon'].mean()
                else:
                    lat_medio = -22.9292  # Coordenada padrão (Maricá)
                    lon_medio = -42.8719  # Coordenada padrão (Maricá)

                mapa = folium.Map(
                    location=[lat_medio, lon_medio],
                    zoom_start=12,
                    tiles='CartoDB positron'
                )

                # Verificar se existem pontos com IQA calculado
                pontos_com_iqa = df_pivot[df_pivot['IQA'].notna()]

                # Função para determinar a cor com base no IQA

                def get_color(iqa):
                    if 90 < iqa <= 100:
                        return '#4169E1'  # Azul royal
                    if 70 < iqa <= 90:
                        return '#008000'    # Verde
                    if 50 < iqa <= 70:
                        return '#FFFF00'    # Amarelo
                    if 25 < iqa <= 50:
                        return '#FFA500'    # Laranja
                    return '#FF0000'                       # Vermelho
            if not pontos_com_iqa.empty:
                # Adicionar marcadores ao mapa
                for idx, row in df_pivot.iterrows():
                    if not pd.isna(row['IQA']) and not pd.isna(row['lat']) and not pd.isna(row['lon']):
                        data_str = row['data'].strftime(
                            '%d/%m/%Y') if pd.notna(row['data']) else 'Data não disponível'

                    # MUDANÇA: Criar listas de parâmetros presentes e ausentes
                        parametros_presentes = []
                        parametros_ausentes = []

                        # Parâmetros principais do IQA
                        parametros_principais = [
                            "OD", "Escherichia coli", "DBOs", "pH", 
                            "Fosfato", "Turbidez", "TDS"
                        ]
                        
                        # Verificar parâmetros principais
                        for param in parametros_principais:
                            if param in df_pivot.columns and row[param] > 0:
                                parametros_presentes.append(
                                    f"{param}: {row[param]:.2f}")
                            else:
                                parametros_ausentes.append(param)

                        # MUDANÇA: Verificar Nitrogênio (pode ser direto ou calculado)
                        nt_status = "Não disponível"
                        if "Nitrogênio Total" in df_pivot.columns and row.get("Nitrogênio Total", 0) > 0:
                            nt_status = f"Nitrogênio Total: {row['Nitrogênio Total']:.2f}"
                        elif any(param in df_pivot.columns and row.get(param, 0) > 0 
                                for param in ["Nitrito", "Nitrato", "Nitrogênio Amoniacal", "Amônia", "Amônio"]):
                            componentes = []
                            for param in ["Nitrito", "Nitrato", "Nitrogênio Amoniacal", "Amônia", "Amônio"]:
                                if param in df_pivot.columns and row.get(param, 0) > 0:
                                    componentes.append(f"{param}: {row[param]:.2f}")
                            if componentes:
                                nt_status = f"Nitrogênio (calculado): {' + '.join(componentes)}"


                        # Montar HTML para o popup com informações dos parâmetros
                        popup_html = f"""
                            <div style="font-family: Arial, sans-serif; min-width: 250px;">
                                <h4 style="margin-bottom: 10px; color: #333;">Informações do Ponto</h4>
                                <b>Ponto:</b> {row['ponto']}<br>
                                <b>Setor:</b> {row['setor']}<br>
                                <b>Data:</b> {data_str}<br>
                                <b>IQA:</b> <span style="color: {get_color(row['IQA'])}; font-weight: bold;">{row['IQA']:.2f}</span><br>
                                <hr style="margin: 10px 0;">
                                <b>Parâmetros utilizados:</b><br>
                                <ul style="margin: 5px 0; padding-left: 20px;">
                                    {"".join([f"<li>{p}</li>" for p in parametros_presentes]) if parametros_presentes else "<li>Nenhum</li>"}
                                    <li>{nt_status}</li>
                                </ul>
                                <hr style="margin: 10px 0;">
                                <b>Parâmetros ausentes:</b><br>
                                <ul style="margin: 5px 0; padding-left: 20px;">
                                    {"".join([f"<li>{p}</li>" for p in parametros_ausentes]) if parametros_ausentes else "<li>Nenhum</li>"}
                                </ul>
                            </div>
                        """

                        folium.CircleMarker(
                            location=[row['lat'], row['lon']],
                            radius=10,
                            popup=folium.Popup(popup_html, max_width=300),
                            color=get_color(row['IQA']),
                            fill=True,
                            fill_color=get_color(row['IQA'])
                        ).add_to(mapa)

                # Adicionar legenda
                legend_html = '''
                    <div style="position: fixed; bottom: 50px; left: 50px; z-index: 1000; background-color: white; padding: 10px; border:   2px solid grey; border-radius: 5px">
                    <p><strong>Índice de Qualidade da Água (IQA)</strong></p>
                    <p><span style="color: #4169E1;">●</span> Excelente (91-100)</p>
                    <p><span style="color: #008000;">●</span> Bom (71-90)</p>
                    <p><span style="color: #FFFF00;">●</span> Médio (51-70)</p>
                    <p><span style="color: #FFA500;">●</span> Ruim (26-50)</p>
                    <p><span style="color: #FF0000;">●</span> Muito Ruim (0-25)</p>
                    </div>
                '''
                mapa.get_root().html.add_child(folium.Element(legend_html))

            else:
                # Criar mapa vazio com mensagem
                mapa = folium.Map(
                    location=[-22.9292, -42.8719],
                    zoom_start=12,
                    tiles='CartoDB positron'
                )
                folium.LayerControl().add_to(mapa)

                # Adicionar mensagem ao mapa
                title_html = '''
                    <h4 style="position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); 
                              background-color: white; padding: 10px; border-radius: 5px; z-index: 1000;">
                        Não foram encontrados dados suficientes para calcular o IQA nesta campanha
                    </h4>
                '''
                mapa.get_root().html.add_child(folium.Element(title_html))
        else:
            # Criar mapa vazio com mensagem
            mapa = folium.Map(
                location=[-22.9292, -42.8719],
                zoom_start=12,
                tiles='CartoDB positron'
            )
            folium.LayerControl().add_to(mapa)

            # Adicionar mensagem ao mapa
            title_html = '''
                <h4 style="position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); 
                          background-color: white; padding: 10px; border-radius: 5px; z-index: 1000;">
                    Não foram encontradas medições para esta campanha
                </h4>
            '''
            mapa.get_root().html.add_child(folium.Element(title_html))

        # Salvar o mapa em HTML
        mapa_iqa = mapa._repr_html_()

        dados_grafico_iqa = {
            'datas': df_pivot['data'].tolist() if 'df_pivot' in locals() else [],
            'pontos': df_pivot['ponto'].tolist() if 'df_pivot' in locals() else [],
            'valores': df_pivot['IQA'].tolist() if 'df_pivot' in locals() else [],
            'lat': df_pivot['lat'].tolist() if 'df_pivot' in locals() else [],
            'lon': df_pivot['lon'].tolist() if 'df_pivot' in locals() else [],
            'setores': df_pivot['setor'].tolist() if 'df_pivot' in locals() else []
        }

    context = {
        'parametros': parametros,
        'pontos': pontos,
        'setores': setores,
        'dados_grafico': dados_grafico,
        'dados_grafico_setor': dados_grafico_setor,
        'dados_grafico_tratamento': dados_grafico_tratamento,
        'dados_grafico_estacoes': dados_grafico_estacoes,  # Add to context
        'dados_grafico_iqa': dados_grafico_iqa,  # Add IQA data to context
        'mapa_iqa': mapa_iqa,  # Add the map to context
        'dados_grafico_tempo': dados_grafico_tempo,
        'parametro_selecionado': parametro_id,
        'parametro_nome_display': parametro_nome_display,
        'ponto_selecionado': ponto_id,
        'setor_selecionado': setor_id,
        'tipo_visualizacao': tipo_visualizacao,
        'campanhas': campanhas,
        'campanha_selecionada': campanha_selecionada,
        'setor_iqa_selecionado': setor_iqa_param,  
        'mes_ano_selecionado': mes_ano_param,
    }

    # Preparar dados do gráfico para serialização segura no template
    if dados_grafico_tempo:
        dados_grafico_tempo['pontos_json'] = json.dumps(
            dados_grafico_tempo['pontos'])

        # Serializa periodos para JSON
        periodos_json = {}
        for periodo_key, periodo_data in dados_grafico_tempo['periodos'].items():
            periodos_json[periodo_key] = {
                'nome': periodo_data['nome'],
                'valores': periodo_data['valores'],
                'tem_dados': periodo_data['tem_dados']
            }
        dados_grafico_tempo['periodos_json'] = json.dumps(periodos_json)

        dados_grafico_tempo['tem_dados_json'] = json.dumps(
            dados_grafico_tempo['tem_dados'])

    return render(request, "dashboard.html", context)


@login_required
@csrf_exempt
def process_dbo_pdfs(request, coleta_id, ponto_id, frasco_id):
    """
    Endpoint para processar múltiplos PDFs de laudos DBO, DQO e E. coli para o Frasco 9.
    Extrai os valores e retorna para preenchimento automático do formulário.
    """
    # Adicionar importação do módulo re
    import re
    import json

    if request.method != 'POST' or frasco_id != 9:  # Apenas para Frasco 9
        return JsonResponse({'error': 'Método não permitido ou frasco inválido'}, status=400)

    if not request.FILES:
        return JsonResponse({'error': 'Nenhum arquivo enviado'}, status=400)

    # Obter informações do ponto atual
    try:
        ponto_atual = TabPonto.objects.get(id=ponto_id)
        ponto_atual_nome = ponto_atual.nome
    except TabPonto.DoesNotExist:
        return JsonResponse({'error': 'Ponto não encontrado'}, status=400)

    results = []
    errors = []

    # Log detalhado para debug
    print(f"Ponto atual da página: {ponto_atual_nome} (ID: {ponto_id})")
    print(f"Recebidos {len(request.FILES)} arquivos para processamento")

    # URL do serviço de extração de PDF - usando configuração do settings.py se disponível
    extraction_service_url = getattr(
        settings, 'PDF_EXTRACTION_SERVICE_URL', 'http://localhost:8041/extract/')

    for file_name, file in request.FILES.items():
        try:
            print(f"Processando arquivo: {file.name}")

            # Verificar se o arquivo é um PDF válido
            if not file.name.lower().endswith('.pdf'):
                error_msg = f"O arquivo '{file.name}' não é um PDF válido"
                errors.append(error_msg)
                print(error_msg)
                continue

            # Enviar arquivo para o serviço de extração
            files = {'file': (file.name, file, 'application/pdf')}

            # Usar try/except para capturar falhas na requisição HTTP
            try:
                response = requests.post(
                    extraction_service_url, files=files, timeout=30)
            except requests.exceptions.RequestException as e:
                error_msg = "Este PDF não é referente ao laudo Oceanus"
                errors.append(error_msg)
                print(f"Erro na requisição ao serviço de extração: {str(e)}")
                continue

            print(f"Resposta do serviço de extração: {response.status_code}")

            if response.status_code != 200:
                error_msg = "Este PDF não é referente ao laudo Oceanus"
                errors.append(error_msg)
                print(
                    f"Erro ao processar o arquivo '{file.name}': Serviço retornou código {response.status_code}")
                continue

            # Tentar parsear o JSON da resposta
            try:
                data = response.json()
            except json.JSONDecodeError:
                error_msg = "Este PDF não é referente ao laudo Oceanus"
                errors.append(error_msg)
                print(
                    f"Resposta inválida do serviço de extração para '{file.name}'")
                continue

            print(f"Dados extraídos: {data}")

            # Verificar se a resposta contém dados
            if not data:
                error_msg = "Este PDF não é referente ao laudo Oceanus"
                errors.append(error_msg)
                print(
                    f"O serviço de extração não retornou dados para '{file.name}'")
                continue

            # Validar dados básicos - mais flexível na busca do ponto
            ponto_info = None
            for key in data.keys():
                if 'ponto' in str(key).lower() or 'identifica' in str(key).lower():
                    ponto_info = data[key]
                    break

            if not ponto_info:
                error_msg = "Este PDF não é referente ao laudo Oceanus"
                errors.append(error_msg)
                print(
                    f"Não foi possível identificar o ponto no arquivo '{file.name}'")
                continue

            # Verificar se o ponto do PDF corresponde ao ponto atual
            ponto_pdf = str(ponto_info).strip().upper()
            ponto_atual_upper = ponto_atual_nome.upper()

            print(
                f"Comparando pontos - PDF: '{ponto_pdf}' vs Atual: '{ponto_atual_upper}'")

            # Verificação mais rigorosa de equivalência de pontos
            # Apenas processar se o ponto do PDF corresponder ao ponto atual
            if ponto_pdf != ponto_atual_upper and not (
                ponto_pdf in ponto_atual_upper or ponto_atual_upper in ponto_pdf
            ):
                error_msg = f"O ponto no arquivo '{file.name}' ({ponto_pdf}) não corresponde ao ponto selecionado ({ponto_atual_upper})"
                errors.append(error_msg)
                print(error_msg)
                continue

            # Função para extrair valores numéricos de diferentes formatos
            def extrair_valor_numerico(valor_bruto):
                if valor_bruto is None:
                    return None

                # Se já for um número, apenas converte para string
                if isinstance(valor_bruto, (int, float)):
                    return str(valor_bruto)

                # Converte para string se não for
                valor_str = str(valor_bruto)

                # Remove tudo que não for dígito, vírgula ou ponto
                valor_limpo = re.sub(r'[^\d.,]', '', valor_str)

                # Substituir vírgula por ponto para padrão numérico
                valor_limpo = valor_limpo.replace(',', '.')

                # Se ficou vazio após a limpeza
                if not valor_limpo:
                    return None

                return valor_limpo

            # Função genérica para encontrar valores de parâmetros em qualquer formato do JSON
            def buscar_parametro(data, nomes_param, chave_resultado='Resultados'):
                # Verificar se data é um dicionário
                if not isinstance(data, dict):
                    return None

                # Busca direta nas chaves de primeiro nível
                for nome in nomes_param:
                    if nome in data:
                        if isinstance(data[nome], dict) and chave_resultado in data[nome]:
                            return data[nome][chave_resultado]
                        elif not isinstance(data[nome], dict):
                            return data[nome]

                # Busca em qualquer chave que contenha o nome do parâmetro
                for key, value in data.items():
                    key_lower = str(key).lower()

                    # Verifica se a chave contém algum dos nomes do parâmetro
                    if any(nome.lower() in key_lower for nome in nomes_param):
                        # Se for um dict e tiver a chave de resultado
                        if isinstance(value, dict) and chave_resultado in value:
                            return value[chave_resultado]
                        # Se for um valor direto
                        elif not isinstance(value, dict):
                            return value

                # Busca recursiva em dicionários aninhados
                for key, value in data.items():
                    if isinstance(value, dict):
                        resultado = buscar_parametro(
                            value, nomes_param, chave_resultado)
                        if resultado is not None:
                            return resultado

                return None

            # Extrair parâmetros com a função genérica

            # 1. DBO
            nomes_dbo = ['dbo', 'DBO', 'dbo5', 'DBO5',
                         'demanda bioquímica', 'DBOS', 'dbos']
            dbo_valor = buscar_parametro(data, nomes_dbo)

            if dbo_valor:
                dbo_valor_limpo = extrair_valor_numerico(dbo_valor)
                if dbo_valor_limpo:
                    results.append({
                        'ponto': ponto_atual_nome,
                        'parametro': 'DBO',
                        'valor': dbo_valor_limpo,
                        'arquivo': file.name
                    })
                    print(f"Dados DBO adicionados: valor={dbo_valor_limpo}")

            # 2. DQO
            nomes_dqo = ['dqo', 'DQO', 'demanda química']
            dqo_valor = buscar_parametro(data, nomes_dqo)

            if dqo_valor:
                dqo_valor_limpo = extrair_valor_numerico(dqo_valor)
                if dqo_valor_limpo:
                    results.append({
                        'ponto': ponto_atual_nome,
                        'parametro': 'DQO',
                        'valor': dqo_valor_limpo,
                        'arquivo': file.name
                    })
                    print(f"Dados DQO adicionados: valor={dqo_valor_limpo}")

            # 3. Escherichia coli
            nomes_ecoli = ['escherichia_coli', 'Escherichia_coli', 'e_coli', 'E_coli',
                           'escherichia coli', 'e. coli', 'coli', 'Escherichia', 'ecoli']
            ecoli_valor = buscar_parametro(data, nomes_ecoli)

            if ecoli_valor:
                ecoli_valor_limpo = extrair_valor_numerico(ecoli_valor)
                if ecoli_valor_limpo:
                    results.append({
                        'ponto': ponto_atual_nome,
                        'parametro': 'Escherichia coli',
                        'valor': ecoli_valor_limpo,
                        'arquivo': file.name
                    })
                    print(
                        f"Dados E. coli adicionados: valor={ecoli_valor_limpo}")

            # Se nenhum dos parâmetros foi encontrado, adicionar ao log de erros
            if not any([dbo_valor, dqo_valor, ecoli_valor]):
                # Imprimir todas as chaves para debug
                print(f"Chaves disponíveis no PDF: {list(data.keys())}")

                # Tentar método alternativo de pesquisa - buscar por chaves que contenham "resultado"
                resultados_encontrados = False
                for key, value in data.items():
                    key_lower = str(key).lower()
                    if 'resultado' in key_lower or 'valor' in key_lower:
                        valor_limpo = extrair_valor_numerico(value)
                        if valor_limpo:
                            # Tentar deduzir o parâmetro pelo contexto
                            param_deduzido = None
                            if 'dbo' in key_lower or 'bioquimica' in key_lower:
                                param_deduzido = 'DBO'
                            elif 'dqo' in key_lower or 'quimica' in key_lower:
                                param_deduzido = 'DQO'
                            elif 'coli' in key_lower or 'escherichia' in key_lower:
                                param_deduzido = 'Escherichia coli'

                            if param_deduzido:
                                results.append({
                                    'ponto': ponto_atual_nome,
                                    'parametro': param_deduzido,
                                    'valor': valor_limpo,
                                    'arquivo': file.name
                                })
                                print(
                                    f"Dados {param_deduzido} adicionados pelo método alternativo: valor={valor_limpo}")
                                resultados_encontrados = True

                if not resultados_encontrados:
                    error_msg = "Este PDF não é referente ao laudo Oceanus"
                    errors.append(error_msg)
                    print(
                        f"Nenhum parâmetro relevante (DBO, DQO, E. coli) encontrado no arquivo '{file.name}'")

        except Exception as e:
            error_msg = "Este PDF não é referente ao laudo Oceanus"
            errors.append(error_msg)
            print(f"Erro ao processar o arquivo '{file.name}': {str(e)}")
            import traceback
            print(traceback.format_exc())

    response_data = {
        'success': len(results) > 0,
        'results': results,
        'errors': errors,
        'ponto_atual': ponto_atual_nome
    }
    print(f"Resposta final: {response_data}")
    return JsonResponse(response_data)

# Alteração para o card 359


def gerar_relatorio_excel_por_coleta(coleta, id_frasco=1):
    """
    Alteração para o card 359
    Função agora parametrizável: exporta dados do frasco informado (padrão: 1 - Sonda)
    Gera um arquivo Excel com todos os dados em uma única aba, incluindo o nome do ponto como coluna.
    Exporta apenas dados do frasco especificado (padrão: 1 - Sonda).
    Usa openpyxl como engine, não requer xlsxwriter.
    """

    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='openpyxl')

    amostras = TabAmostra.objects.filter(id_coleta=coleta, id_frasco=id_frasco)
    dados = []
    # Alteração para o card 359: inclusão da coluna 'Série de Classificação' na exportação
    for amostra in amostras:
        ponto_nome = amostra.id_ponto.nome if amostra.id_ponto else ''
        envios = TabEnvio.objects.filter(id_amostra=amostra)
        for envio in envios:
            medidas = TabMedida.objects.filter(id_envio=envio)
            for medida in medidas:
                anexo = TabAnexoAmostra.objects.filter(
                    id_envio=medida.id_envio).first()

                dados.append({
                    'Ponto': ponto_nome,
                    'Parâmetro': medida.id_pp.id_param.nome if medida.id_pp and medida.id_pp.id_param else '',
                    'Valor': medida.input_valor,
                    'Unidade': medida.id_pp.unidade if medida.id_pp else '',
                    'Série de Classificação': medida.id_pp.id_serie.nome if medida.id_pp and medida.id_pp.id_serie else '',
                    'Observação': getattr(anexo, 'observacao', '') if anexo else '',
                    'Código Oceanus': getattr(anexo, 'codigo_oceanus', '') if anexo else '',
                    'Data de Preenchimento': datetime.now().strftime('%d/%m/%Y'),
                })
    df = pd.DataFrame(dados)
    df.to_excel(writer, sheet_name="Resultados", index=False)
    writer.close()
    output.seek(0)
    return output


@login_required
def export_frasco_resultados_xlsx(request, coleta_id, frasco_id):
    """
    Exporta os resultados de um frasco específico para Excel com formato tabular horizontal
    """
    try:
        # Obter os dados da coleta e frasco
        coleta = get_object_or_404(TabColeta, id=coleta_id)
        frasco = get_object_or_404(TabFrasco, id=frasco_id)

        # Criar um novo workbook e worksheet
        wb = Workbook()
        ws = wb.active
        ws.title = f"Resultados {frasco.nome}"

        # Adicionar título principal
        ws.merge_cells('A1:N1')
        ws['A1'] = f"Resultados da Coleta - {frasco.nome}"
        ws['A1'].font = Font(bold=True, size=14)
        ws['A1'].alignment = Alignment(horizontal='center')

        # Adicionar informações da coleta
        row = 3
        ws['A3'] = "Ordem de Serviço:"
        ws['B3'] = coleta.ordem_servico
        ws['A4'] = "Data da Coleta:"
        ws['B4'] = coleta.data.strftime('%d/%m/%Y') if coleta.data else "N/A"
        ws['A5'] = "Setor:"
        ws['B5'] = str(coleta.id_setor)
        ws['A6'] = "Frasco:"
        ws['B6'] = frasco.nome

        # Aplicar estilo às células de informação
        for cell in [ws['A3'], ws['A4'], ws['A5'], ws['A6']]:
            cell.font = Font(bold=True)

        # Pular linhas para começar a tabela
        row = 9

        # Obter todos os pontos da coleta
        pontos = TabAmostra.objects.filter(
            id_coleta=coleta,
            id_frasco=frasco
        ).values_list('id_ponto', flat=True).distinct()

        pontos = TabPonto.objects.filter(id__in=pontos).order_by('nome')

        # Obter todos os parâmetros para este frasco
        params = []

        # Buscar as primeiras medidas para identificar quais parâmetros existem
        primeira_amostra = TabAmostra.objects.filter(
            id_coleta=coleta,
            id_frasco=frasco
        ).first()

        if primeira_amostra:
            envio = TabEnvio.objects.filter(
                id_amostra=primeira_amostra).first()
            if envio:
                medidas = TabMedida.objects.filter(
                    id_envio=envio
                ).select_related('id_pp', 'id_pp__id_param').order_by('id_pp__ordem_visualizacao')

                for medida in medidas:
                    if medida.id_pp and medida.id_pp.id_param:
                        params.append({
                            'id': medida.id_pp.id_param.id,
                            'nome': medida.id_pp.id_param.nome,
                            'ordem': medida.id_pp.ordem_visualizacao,
                            'unidade': medida.id_pp.unidade
                        })

        # Cabeçalho com pontos
        col = 2
        ws.cell(row=row, column=1, value="Parâmetro")

        # Adicionar cada ponto como cabeçalho de coluna
        for ponto in pontos:
            ws.cell(row=row, column=col, value=f"PT {ponto.id}")
            ws.cell(row=row, column=col).font = Font(bold=True)
            ws.cell(row=row, column=col).alignment = Alignment(
                horizontal='center')
            ws.cell(row=row, column=col).fill = PatternFill(
                start_color="CCCCCC", end_color="CCCCCC", fill_type="solid")
            col += 1

        # Estilizar a célula "Parâmetro"
        ws.cell(row=row, column=1).font = Font(bold=True)
        ws.cell(row=row, column=1).fill = PatternFill(
            start_color="CCCCCC", end_color="CCCCCC", fill_type="solid")

        # Para cada parâmetro, adicionar uma linha
        for param in params:
            row += 1
            ws.cell(row=row, column=1, value=param['nome'])
            ws.cell(row=row, column=1).font = Font(bold=True)

            # Para cada ponto, buscar o valor do parâmetro
            col = 2
            for ponto in pontos:
                # Buscar a amostra para este ponto e frasco
                amostra = TabAmostra.objects.filter(
                    id_coleta=coleta,
                    id_frasco=frasco,
                    id_ponto=ponto.id
                ).first()

                valor = "ND"  # Valor padrão se não encontrado

                if amostra:
                    envio = TabEnvio.objects.filter(id_amostra=amostra).first()
                    if envio:
                        medida = TabMedida.objects.filter(
                            id_envio=envio,
                            id_pp__id_param__id=param['id']
                        ).first()

                        if medida and medida.input_valor:
                            valor = medida.input_valor

                ws.cell(row=row, column=col, value=valor)
                ws.cell(row=row, column=col).alignment = Alignment(
                    horizontal='center')
                col += 1

        # Adicionar legenda de unidades
        row += 2
        ws.cell(row=row, column=1, value="Unidades:")
        ws.cell(row=row, column=1).font = Font(bold=True)

        for param in params:
            row += 1
            if 'unidade' in param and param['unidade']:
                ws.cell(row=row, column=1,
                        value=f"{param['nome']}: {param['unidade']}")

        # Ajustar largura das colunas
        for col in ws.columns:
            max_length = 0
            column_letter = get_column_letter(col[0].column)

            for cell in col:
                if cell.value:
                    cell_length = len(str(cell.value))
                    if cell_length > max_length:
                        max_length = cell_length

            adjusted_width = max_length + 2
            ws.column_dimensions[column_letter].width = adjusted_width

        # Preparar a resposta HTTP
        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = f'attachment; filename="resultados_{coleta.ordem_servico}_{frasco.nome}.xlsx"'

        # Salvar o arquivo
        wb.save(response)
        return response

    except Exception as e:
        logger.error(f"Erro ao exportar resultados do frasco: {str(e)}")
        messages.error(
            request, "Erro ao exportar os resultados. Por favor, tente novamente.")
        return redirect("lista_campo_frasco", coleta_id=coleta_id, frasco_id=frasco_id)




@login_required
def get_meses_disponiveis_setor(request):
    """Retorna os meses/anos disponíveis para um setor específico"""
    setor_id = request.GET.get('setor_id')
    
    if not setor_id:
        return JsonResponse({'meses': []})
    
    # Buscar todas as datas de coletas deste setor
    datas = TabMedida.objects.filter(
        id_envio__id_amostra__id_ponto__id_setor_id=setor_id
    ).select_related(
        'id_envio__id_amostra__id_coleta'
    ).values_list(
        'id_envio__id_amostra__id_coleta__data', 
        flat=True
    ).distinct()
    
    # Extrair mês/ano únicos
    meses_anos = set()
    for data in datas:
        if data:
            meses_anos.add(data.strftime('%Y-%m'))
    
    # Ordenar em ordem decrescente (mais recente primeiro)
    meses_ordenados = sorted(list(meses_anos), reverse=True)
    
    return JsonResponse({
        'meses': [{'value': mes, 'label': mes} for mes in meses_ordenados]
    })
