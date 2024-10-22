# pylint: disable=protected-access,no-member
# Django imports
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import F
from datetime import timedelta
import csv
import pandas as pd
import plotly.express as px
from plotly.offline import plot
from django.forms import inlineformset_factory
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.cache import cache
from django.http import HttpResponse, FileResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.conf import settings
import json
import os
import logging
from django.db import connection


from django_tables2 import RequestConfig

from .filters import *
from .forms import *
from .services import get_weather_description, gerar_etiquetas
from .tables import *

# Configuração do logger
logger = logging.getLogger(__name__)


def check_admin(user):
    return user.is_superuser


@login_required
@user_passes_test(check_admin)
def cadastro_usuarios(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            # Redirecione para a página de usuários cadastrados
            return redirect('usuarios_cadastrados')
    else:
        form = CustomUserCreationForm()

    return render(request, 'cadastro_usuarios.html', {'form': form})


@login_required
@user_passes_test(check_admin)
def editar_usuario(request, user_id):
    usuario = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuário atualizado com sucesso.')
            return redirect('usuarios_cadastrados')
    else:
        form = CustomUserCreationForm(instance=usuario)

    return render(request, 'editar_usuario.html', {'form': form, 'usuario': usuario})


@login_required
@user_passes_test(check_admin)
def usuarios_cadastrados(request):
    usuarios = User.objects.all()
    return render(request, 'usuarios_cadastrados.html', {'usuarios': usuarios})


def home(request):
    try:
        proxima_coleta = ProgramaColeta.objects.filter(
            status_coleta__in=['Iniciada', 'Programada'],
            data_coleta_campo__gte=timezone.now()
        ).order_by('data_coleta_campo').first()
        table = TopCampanhas(ProgramaColeta.objects.all())
        RequestConfig(request, paginate={"per_page": 3}).configure(table)

        percentual_checklist = None
        if proxima_coleta:
            percentual_checklist = ChecklistCampo.objects.filter(
                ordem_servico=proxima_coleta.id
            ).values_list('progresso', flat=True).first()
            data_coleta_proxima_formatada = proxima_coleta.data_coleta_campo.strftime(
                '%d/%m/%Y')
            weather_description = get_weather_description(
                "Maricá", proxima_coleta.data_coleta_campo.strftime('%Y-%m-%d'))

            checklist = ChecklistCampo.objects.filter(
                ordem_servico=proxima_coleta).first()

            if checklist:
                dados_gantt = [
                    dict(Tarefa="Coleta de Campo", Inicio=proxima_coleta.data_coleta_campo,
                         Termino=proxima_coleta.data_coleta_campo, Cor='#2ca02c' if checklist.previsao_tempo else '#d62728'),  # Verde moderno se verdadeiro, vermelho moderno se falso
                    dict(Tarefa="Verificar previsão do tempo", Inicio=proxima_coleta.data_programacao,
                         Termino=proxima_coleta.data_check_forecast, Cor='#2ca02c' if checklist.previsao_tempo else '#d62728'),
                    dict(Tarefa="Avisar Laboratórios", Inicio=proxima_coleta.data_check_lab,
                         Termino=proxima_coleta.data_check_lab + timedelta(days=2), Cor='#2ca02c' if checklist.avisar_labs else '#d62728'),
                    dict(Tarefa="Reservar Carro e barco", Inicio=proxima_coleta.data_check_car,
                         Termino=proxima_coleta.data_check_car + timedelta(days=2), Cor='#2ca02c' if checklist.reservar_carro else '#d62728'),
                    dict(Tarefa="Checar Equipamentos", Inicio=proxima_coleta.data_check_material,
                         Termino=proxima_coleta.data_check_material + timedelta(days=3), Cor='#2ca02c' if checklist.separar_equipamentos else '#d62728'),
                    dict(Tarefa="Etiquetar frascos", Inicio=proxima_coleta.data_check_material + timedelta(days=3),
                         Termino=proxima_coleta.data_check_material + timedelta(days=3), Cor='#2ca02c' if checklist.conferir_equipamentos else '#d62728'),
                    dict(Tarefa="Comprar gelo", Inicio=proxima_coleta.data_check_material + timedelta(days=3),
                         Termino=proxima_coleta.data_check_material + timedelta(days=3), Cor='#2ca02c' if checklist.conferir_equipamentos else '#d62728'),
                ]
            else:
                dados_gantt = [
                    dict(Tarefa="Coleta de Campo", Inicio=proxima_coleta.data_coleta_campo,
                         Termino=proxima_coleta.data_coleta_campo, Cor='#2ca02c'),  # Verde moderno para tarefas já feitas
                    dict(Tarefa="Verificar previsão do tempo", Inicio=proxima_coleta.data_programacao,
                         Termino=proxima_coleta.data_check_forecast, Cor='#2ca02c'),  # Verde moderno para tarefas já feitas
                    dict(Tarefa="Contatar Laboratórios", Inicio=proxima_coleta.data_check_lab,
                         Termino=proxima_coleta.data_check_lab + timedelta(days=2), Cor='#2ca02c'),  # Verde moderno para tarefas já feitas
                    dict(Tarefa="Reservar Carro", Inicio=proxima_coleta.data_check_car,
                         Termino=proxima_coleta.data_check_car + timedelta(days=2), Cor='#2ca02c'),  # Verde moderno para tarefas já feitas
                    dict(Tarefa="Preparar Equipamentos", Inicio=proxima_coleta.data_check_material,
                         Termino=proxima_coleta.data_check_material + timedelta(days=3), Cor='#2ca02c'),  # Verde moderno para tarefas já feitas
                    dict(Tarefa="Etiquetar frascos", Inicio=proxima_coleta.data_check_material,
                         Termino=proxima_coleta.data_check_material + timedelta(days=3), Cor='#2ca02c'),  # Verde moderno para tarefas já feitas
                    dict(Tarefa="Comprar gelo", Inicio=proxima_coleta.data_coleta_campo,
                         Termino=proxima_coleta.data_coleta_campo, Cor='#2ca02c'),  # Verde moderno para tarefas já feitas
                ]

            # Adiciona a tarefa "Programação" com a cor azul
            dados_gantt.append(dict(Tarefa="Programação", Inicio=proxima_coleta.data_programacao,
                                    Termino=proxima_coleta.data_coleta_campo, Cor='#2ca02c'))

            df = pd.DataFrame(dados_gantt)

            # Converte as colunas para datetime
            df['Inicio'] = pd.to_datetime(df['Inicio'])
            df['Termino'] = pd.to_datetime(df['Termino'])

            # Calcula a duração
            df['Duracao'] = (df['Termino'] - df['Inicio']).dt.total_seconds()

            # Ordena o DataFrame pela duração em ordem decrescente
            df = df.sort_values(by='Duracao', ascending=True)

            fig = px.timeline(df, x_start="Inicio",
                              x_end="Termino", y="Tarefa", color="Cor")

            # Adiciona bolinhas para tarefas com duração zero
            for i, row in df.iterrows():
                if row['Duracao'] == 0:
                    fig.add_scatter(
                        x=[row['Inicio']],
                        y=[row['Tarefa']],
                        mode='markers',
                        marker=dict(size=20, color='#1f77b4'),  # Azul moderno
                        name=row['Tarefa']
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
                        dict(dtickrange=[None, 86400000],
                             value="%d/%m/%Y"),  # daily ticks
                        # larger than daily ticks
                        dict(dtickrange=[86400000, None], value="%d/%m/%Y"),
                    ]
                ),
                height=None,  # Remove a altura fixa
                width=None,   # Remove a largura fixa
                # Ajuste as margens conforme necessário
                margin=dict(l=20, r=20, t=20, b=20),
            )

            # Torna o gráfico responsivo
            fig.update_layout(
                autosize=True
            )

            gantt_div = plot(fig, output_type="div")
        else:
            data_coleta_proxima_formatada = None
            weather_description = None
            gantt_div = None

        campanhas = ProgramaColeta.objects.all()
        eventos = []
        for campanha in campanhas:
            evento = {
                'title': campanha.ordem_servico,
                'start': campanha.data_coleta_campo.isoformat(),
                'end': campanha.data_coleta_campo.isoformat(),
                'url': f'/checklist_campanha/{campanha.ordem_servico}/'
            }
            if campanha.status_coleta == 'Programada':
                evento['className'] = 'evento-programado'
            elif campanha.status_coleta == 'Iniciada':
                evento['className'] = 'evento-iniciado'
            elif campanha.status_coleta == 'Coleta realizada':
                evento['className'] = 'evento-realizado'
            elif campanha.status_coleta == 'Cancelada':
                evento['className'] = 'evento-cancelado'
            eventos.append(evento)

        context = {
            'weather_description': weather_description,
            'data_coleta_proxima_formatada': data_coleta_proxima_formatada,
            'status_coleta': proxima_coleta.status_coleta if proxima_coleta else None,
            'local_coleta': proxima_coleta.local_coleta if proxima_coleta else None,
            'percentual_checklist': percentual_checklist if percentual_checklist else 0,
            'ordem_servico': proxima_coleta.ordem_servico if proxima_coleta else None,
            'table_top3': table,
            'eventos': json.dumps(eventos),
            'gantt_div': gantt_div
        }
        return render(request, 'home.html', context)
    except ProgramaColeta.DoesNotExist:
        return HttpResponse("Nenhum programa de coleta encontrado.", status=404)
    except Exception as e:
        return HttpResponse(f"Erro ao carregar a página: {str(e)}", status=500)


@login_required
def coleta(request):
    if request.method == 'POST':
        form = ColetaCampo(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('lista_coleta')

    else:
        form = ColetaCampo()
    return render(request, 'coleta/coleta.html', {'form': form})


@login_required
def atualizar_coleta(request, id):
    coleta = get_object_or_404(Campo, id=id)
    pontos_coleta = Campo.objects.filter(
        ordem_servico=coleta.ordem_servico).order_by('ponto')

    form_data = {field: getattr(coleta, field)
                 for field in ColetaCampo.base_fields}
    form_data['hora_inicio'] = timezone.now().strftime('%H:%M')
    form = ColetaCampo(initial=form_data)

    if request.method == 'POST':
        post_data = request.POST.copy()
        post_data['hora_fim'] = timezone.now().strftime('%H:%M')
        form = ColetaCampo(post_data, request.FILES)

        if form.is_valid():
            for field, value in form.cleaned_data.items():
                setattr(coleta, field, value)
            coleta.save()
            messages.success(request, 'Dados atualizados com sucesso!')

            # Verifica se todos os pontos foram coletados
            todos_pontos_preenchidos = not Campo.objects.filter(
                ordem_servico=coleta.ordem_servico).exclude(status_form='Preenchido').exists()

            if todos_pontos_preenchidos:
                campanha = ProgramaColeta.objects.get(
                    id=coleta.ordem_servico.id)
                campanha.status_coleta = 'Coleta realizada'
                campanha.save()

            pontos_coleta_list = list(pontos_coleta)
            index_atual = pontos_coleta_list.index(coleta)

            while not todos_pontos_preenchidos:
                index_atual = (index_atual + 1) % len(pontos_coleta_list)
                proximo_ponto = pontos_coleta_list[index_atual]
                if proximo_ponto.status_form != 'Preenchido':
                    return redirect(reverse('atualizar_coleta', args=[proximo_ponto.id]))

            return redirect('lista_coleta', ordem_servico=coleta.ordem_servico.id)
        else:
            pass  # Mantenha o formulário com erros para exibição

    context = {'form': form, 'codigo_coleta': coleta.codigo_coleta,
               'coleta_id': coleta.id,
               'ponto': coleta.ponto, 'pontos_coleta': pontos_coleta,
               'ordem_servico_id': coleta.ordem_servico.id, }
    return render(request, 'coleta/coleta.html', context)


@login_required
def meta_coleta(request, id):
    coleta = get_object_or_404(Campo, id=id)

    # Verifica se já existe um registro de metadados para o código de coleta
    metadados, created = MetadadosCampo.objects.get_or_create(
        codigo_coleta=coleta)

    if created:
        messages.info(
            request, 'Novo registro de metadados criado para o código de coleta fornecido.')

    if request.method == 'POST':
        form = MetadadosCampoForm(request.POST, instance=metadados)
        if form.is_valid():
            form.save()
            # Redireciona para a página anterior
            return redirect(reverse('atualizar_coleta', args=[coleta.id]))
    else:
        form = MetadadosCampoForm(instance=metadados)

    context = {
        'form': form,
        'codigo_coleta': coleta.codigo_coleta,
        'coleta_id': coleta.id,
        'ponto': coleta.ponto,
        'ordem_servico_id': coleta.ordem_servico.id,
        'ordem_servico': coleta.ordem_servico
    }

    return render(request, 'coleta/meta_coleta.html', context)


@login_required
@user_passes_test(check_admin)
def deletar_coleta(request, id):
    coleta = ColetaCampo.objects.get(id=id)
    coleta.delete()
    return redirect('lista_coleta')


@login_required
def lista_coleta(request, ordem_servico=None):
    # filtro = CampoFilter(request.GET, queryset=Campo.objects.all())
    ordem_servico = ProgramaColeta.objects.get(id=ordem_servico)
    responsavel = ProgramaColeta.objects.get(id=ordem_servico.id).usuario
    filtro = CampoFilter(request.GET, queryset=Campo.objects.filter(
        ordem_servico_id=ordem_servico))
    table = ColetaCampoTable(filtro.qs)
    RequestConfig(request, paginate={"per_page": 25}).configure(table)
    return render(request, 'coleta/lista_coleta.html', {
        'table_campo': table,
        'filtro': filtro,
        'ordem_servico': ordem_servico,
        'responsavel': responsavel
    })


@login_required
def resultados(request):
    filtro = ResultadosColetaFilter(request.GET, queryset=Campo.objects.all())
    table = ResultadosColetaTable(filtro.qs)
    RequestConfig(request, paginate={"per_page": 25}).configure(table)
    return render(request, 'coleta/resultados_coleta.html', {
        'table_campo': table,
        'filtro': filtro,
    })


@login_required
def coletas_agendas(request):
    filtro = ProgramaColetaFilter(
        request.GET, queryset=ProgramaColeta.objects.all())
    table = ProgramaColetaTable(filtro.qs)
    RequestConfig(request, paginate={"per_page": 25}).configure(table)
    return render(request, 'coleta/coletas_agendas.html', {
        'table_agenda_coleta': table,
        'filtro': filtro,
    })


@login_required
def agenda_coleta(request):
    if request.method == 'POST':
        form = ProgramaColetaForm(request.POST)
        if form.is_valid():
            programa_coleta = ProgramaColeta()

            # Atribui os dados do formulário aos campos do modelo
            programa_coleta.data_coleta_campo = form.cleaned_data['data_coleta_campo']
            # programa_coleta.data_fim_coleta_campo = form.cleaned_data['data_fim_coleta_campo']
            programa_coleta.equipe_coleta = form.cleaned_data['equipe_coleta']
            # programa_coleta.laboratorio = form.cleaned_data['laboratorio']
            # programa_coleta.solicitante = form.cleaned_data['solicitante']
            programa_coleta.local_coleta = form.cleaned_data['local_coleta']
            programa_coleta.observacoes = form.cleaned_data['observacoes']
            programa_coleta.status_coleta = 'Programada'
            # Salva o modelo no banco de dados
            programa_coleta.save(usuario=request.user)

            messages.success(
                request, 'Programação realizada com sucesso!')
            return redirect('coletas_agendas')
    else:
        form = ProgramaColetaForm()

    return render(request, 'coleta/agendar_coleta.html', {'form': form})


@login_required
def atualizar_programacao(request, id):
    cache_key = f'programacao_{id}'
    programacao = cache.get(cache_key)

    if not programacao:
        programacao = get_object_or_404(ProgramaColeta, id=id)
        cache.set(cache_key, programacao, timeout=3600)

    # Verifica se o status da programação é 'Cancelada' ou se a rota é True
    if programacao.status_coleta == 'Cancelada' or programacao.rota:
        messages.warning(
            request, 'Não é possível alterar campanhas canceladas ou com rota definida.')
        return redirect('coletas_agendas')

    if request.method == 'POST':
        form = ProgramaColetaForm(request.POST)
        if form.is_valid():
            for field, value in form.cleaned_data.items():
                setattr(programacao, field, value)
            programacao.save()
            cache.set(cache_key, programacao, timeout=3600)
            messages.success(request, 'Dados atualizados com sucesso!')
            return redirect('coletas_agendas')
        else:
            print(form.errors)
    else:
        form_data = {field.name: getattr(
            programacao, field.name) for field in ProgramaColeta._meta.fields}
        for date_field in ['data_coleta_campo']:
            if date_field in form_data and form_data[date_field]:
                form_data[date_field] = form_data[date_field].strftime(
                    '%Y-%m-%d')
        form = ProgramaColetaForm(initial=form_data)
    return render(request, 'coleta/agendar_coleta.html', {'form': form})


@login_required
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

    """
    programacao = get_object_or_404(ProgramaColeta, id=id)
    programacao.delete()
    messages.success(request, 'Programação de coleta deletada com sucesso!')
    return redirect('coletas_agendas')


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
    if programacao.status_coleta in ['Coleta realizada', 'Iniciada']:
        messages.warning(
            request, 'Não é possível cancelar uma coleta que já foi iniciada ou realizada.')
        return redirect('coletas_agendas')
    else:
        programacao.status_coleta = 'Cancelada'
        programacao.save()
        messages.success(
            request, 'Programação de coleta cancelada com sucesso!')
        return redirect('coletas_agendas')


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
    if request.method == 'POST':
        form = AjudaForm(request.POST)
        if form.is_valid():
            nova_ajuda = Ajuda()  # Model
            nova_ajuda.nome = form.cleaned_data['nome']
            nova_ajuda.email = form.cleaned_data['email']
            nova_ajuda.pergunta = form.cleaned_data['pergunta']
            nova_ajuda.save()

            # Enviar e-mail para o administrador
            subject_admin = 'Nova solicitação de ajuda'
            message_admin = f"Nome: {nova_ajuda.nome}\nEmail: {nova_ajuda.email}\nPergunta: {nova_ajuda.pergunta}"
            recipient_list_admin = [settings.EMAIL_HOST_USER]
            send_mail(subject_admin, message_admin,
                      settings.EMAIL_HOST_USER, recipient_list_admin)

            # Enviar e-mail para o usuário
            subject_user = 'Confirmação de solicitação de ajuda'
            message_user = f"Olá {nova_ajuda.nome},\n\nVocê está recebendo este e-mail porque fez uma solicitação de ajuda no sistema LAGUNA.\n\nPergunta: {nova_ajuda.pergunta}\n\nAtenciosamente,\nEquipe LAGUNA"
            recipient_list_user = [nova_ajuda.email]
            send_mail(subject_user, message_user,
                      settings.EMAIL_HOST_USER, recipient_list_user)

            messages.success(
                request, 'Sua solicitação de ajuda foi enviada com sucesso!')

            return redirect('ajuda')
    else:
        form = AjudaForm()

    return render(request, 'ajuda.html', {'form': form})


# View para pagina de inicio de campanha


@login_required
def iniciar_campanha(request, ordem_servico=None):
    # Obtém o valor de ordem_servico da URL, se houver
    ordem_servico = request.GET.get('ordem_servico', None)
    filtro = {}
    if ordem_servico:
        filtro['ordem_servico_inicial'] = ordem_servico

    if request.method == 'POST':
        form = IniciarCampanhaForm(request.POST, **filtro)
        if form.is_valid():
            ordem_servico = form.cleaned_data['ordem_servico']
            redirect_url = reverse('checklist_campanha') + \
                f'?ordem_servico={ordem_servico.ordem_servico}'
            return redirect(redirect_url)
    else:
        form = IniciarCampanhaForm(**filtro)

    return render(request, 'coleta/iniciar_campanha.html', {'form': form})


@login_required
def checklist_campanha(request, ordem_servico=None):
    ordem_servico_selecionada = request.GET.get('ordem_servico', ordem_servico)
    campanha = get_object_or_404(
        ProgramaColeta, ordem_servico=ordem_servico_selecionada)
    if campanha.status_coleta == 'Cancelada':
        messages.warning(
            request, 'Não é possível iniciar uma campanha cancelada')
        return redirect('coletas_agendas')
    try:
        checklist_campanha = ChecklistCampo.objects.get(
            ordem_servico=campanha)
    except ChecklistCampo.DoesNotExist:
        checklist_campanha = None

    form = ChecklistCampoForm(
        request.POST or None, instance=checklist_campanha, ordem_servico_selecionada=ordem_servico_selecionada)
    if request.method == 'POST' and form.is_valid():
        checklist_campanha, created = ChecklistCampo.objects.get_or_create(
            ordem_servico=campanha,
            defaults={campo: form.cleaned_data[campo] for campo in (
                ('previsao_tempo', 'data_previsao_tempo', 'observacao_previsao_tempo', 'avisar_labs', 'data_avisar_labs', 'observacao_avisar_labs',
                 'reservar_carro', 'observacao_reservar_carro', 'data_reservar_carro', 'reservar_barco', 'observacao_reservar_barco', 'data_reservar_barco', 'separar_equipamentos',
                 'data_separar_equipamentos', 'observacao_separar_equipamentos', 'conferir_equipamentos', 'data_conferir_equipamentos',
                 'observacao_conferir_equipamentos', 'comprar_gelo', 'data_comprar_gelo', 'observacao_comprar_gelo', 'etiquetar_frascos', 'data_etiquetar_frascos', 'observacao_etiquetar_frascos', )
            )}
        )
        if not created:
            for campo in ('previsao_tempo', 'data_previsao_tempo', 'observacao_previsao_tempo', 'avisar_labs', 'data_avisar_labs', 'observacao_avisar_labs',
                          'reservar_carro', 'observacao_reservar_carro', 'data_reservar_carro', 'reservar_barco', 'observacao_reservar_barco', 'data_reservar_barco', 'separar_equipamentos',
                          'data_separar_equipamentos', 'observacao_separar_equipamentos', 'conferir_equipamentos', 'data_conferir_equipamentos',
                          'observacao_conferir_equipamentos', 'comprar_gelo', 'data_comprar_gelo', 'observacao_comprar_gelo', 'etiquetar_frascos', 'data_etiquetar_frascos', 'observacao_etiquetar_frascos',):
                setattr(checklist_campanha, campo, form.cleaned_data[campo])
            checklist_campanha.save(usuario=request.user)
        if campanha.rota:
            return redirect('lista_coleta', ordem_servico=campanha.id)
        else:
            return redirect('checklist_campanha', ordem_servico=campanha.ordem_servico)

    if campanha.status_coleta == 'Programada':
        campanha.status_coleta = 'Iniciada'

    campanha.save()

    data = campanha.data_coleta_campo
    previsao_tempo = get_weather_description(
        "Maricá", data.strftime('%Y-%m-%d'))

    context = {
        'form': form,
        'checklist_campanha': checklist_campanha,
        'ordem_servico': campanha.ordem_servico,
        'previsao_tempo': previsao_tempo,
        'campanha': campanha
    }
    return render(request, 'coleta/checklist_campanha.html', context)


@login_required
def gerar_rota_campanha(request, ordem_servico=None):
    """
Gera rota para uma campanha com base na ordem de serviço fornecida.

Ordem de serviço é: Local + Data da coleta

Esta função de view recupera a ordem de serviço da requisição, busca a campanha correspondente
e gera pontos de coleta e previsões meteorológicas para a campanha. Em seguida, salva os dados
gerados e redireciona para a checklist da campanha.

Args:
    request (HttpRequest): O objeto de requisição HTTP.
    ordem_servico (str, opcional): O identificador da ordem de serviço. Padrão é None.

Returns:
    HttpResponseRedirect: Redireciona para a view da checklist da campanha.

Raises:
    Http404: Se a campanha ou os pontos de coleta não forem encontrados.
"""
    ordem_servico = request.GET.get('ordem_servico', ordem_servico)
    campanha = None
    if ordem_servico:
        campanha = get_object_or_404(
            ProgramaColeta, ordem_servico=ordem_servico)

    previsao_tempo = None
    pontos_coleta = []
    if campanha:
        data = campanha.data_coleta_campo
        previsao_tempo = get_weather_description(
            "Maricá", data.strftime('%Y-%m-%d'))

        local_campanha = campanha.local_coleta
        setor_local = TabSetor.objects.get(nome=local_campanha)
        pontos_coleta = TabPonto.objects.filter(id_setor=setor_local)
        programa_coleta_instance = get_object_or_404(
            ProgramaColeta, ordem_servico=ordem_servico)
        for ponto in pontos_coleta:
            campo = Campo()
            campo.ordem_servico = programa_coleta_instance
            campo.ponto = str(ponto.nome)
            campo.codigo_coleta = ordem_servico + str(ponto.nome)
            campo.clima = previsao_tempo
            campo.save()

        campanha.rota = True
        campanha.save()

    return redirect('checklist_campanha', ordem_servico=ordem_servico)


def etiquetagem(request, ordem_servico=None):
    try:
        ordem_servico = request.GET.get('ordem_servico', ordem_servico)
        campanha = None
        if ordem_servico:
            campanha = get_object_or_404(
                ProgramaColeta, ordem_servico=ordem_servico)
    try:
        ordem_servico = request.GET.get('ordem_servico', ordem_servico)
        campanha = None
        if ordem_servico:
            campanha = get_object_or_404(
                ProgramaColeta, ordem_servico=ordem_servico)

            data = campanha.data_coleta_campo.strftime('%d/%m/%Y')
            responsavel = campanha.usuario
            codigo_servico = campanha.ordem_servico
            codigos = Campo.objects.filter(
                ordem_servico=campanha).values_list('codigo_coleta', flat=True)
            data = campanha.data_coleta_campo.strftime('%d/%m/%Y')
            responsavel = campanha.usuario
            codigo_servico = campanha.ordem_servico
            codigos = Campo.objects.filter(
                ordem_servico=campanha).values_list('codigo_coleta', flat=True)

            if not codigos:
                messages.warning(
                    request, 'Nenhum código de coleta encontrado para a ordem de serviço fornecida.')
                return redirect('checklist_campanha', ordem_servico=ordem_servico)
            if not codigos:
                messages.warning(
                    request, 'Nenhum código de coleta encontrado para a ordem de serviço fornecida.')
                return redirect('checklist_campanha', ordem_servico=ordem_servico)

            pdf_path = gerar_etiquetas(
                codigos, data, responsavel, codigo_servico)
            pdf_path = gerar_etiquetas(
                codigos, data, responsavel, codigo_servico)

            # Retorna o PDF como uma resposta HTTP
            response = FileResponse(
                open(pdf_path, 'rb'), as_attachment=True, filename=os.path.basename(pdf_path))
            # Retorna o PDF como uma resposta HTTP
            response = FileResponse(
                open(pdf_path, 'rb'), as_attachment=True, filename=os.path.basename(pdf_path))

            # Apaga o arquivo PDF após o download
            os.remove(pdf_path)
            # Apaga o arquivo PDF após o download
            os.remove(pdf_path)

            return response
            return response

        return redirect('checklist_campanha', ordem_servico=ordem_servico)
    except Exception as e:
        messages.error(request, f'Ocorreu um erro: {str(e)}')
        return redirect('checklist_campanha', ordem_servico=ordem_servico)
        return redirect('checklist_campanha', ordem_servico=ordem_servico)
    except Exception as e:
        messages.error(request, f'Ocorreu um erro: {str(e)}')
        return redirect('checklist_campanha', ordem_servico=ordem_servico)


@login_required
def cadastro_laboratorio(request):
    AnaliseFormSet = inlineformset_factory(
        Laboratorios, Analises, form=AnaliseForm, extra=1, fields='__all__'
    )
    if request.method == 'POST':
        form = LaboratorioForm(request.POST)
        formset = AnaliseFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            laboratorio = form.save()
            formset.instance = laboratorio
            formset.save()
            return redirect('laboratorios_cadastrados')
    else:
        form = LaboratorioForm()
        formset = AnaliseFormSet()

    return render(request, 'cadastro_laboratorio.html', {'form': form, 'formset': formset})


@login_required
def laboratorios_cadastrados(request):
    table = LaboratoriosTable(Laboratorios.objects.all())
    RequestConfig(request, paginate={"per_page": 25}).configure(table)
    return render(request, 'laboratorios_cadastrados.html', {
        'table_laboratorios': table
    })


@login_required
def atualizar_laboratorio(request, id):
    laboratorio = get_object_or_404(Laboratorios, id=id)
    AnaliseFormSet = inlineformset_factory(
        Laboratorios, Analises, form=AnaliseForm, extra=0, fields='__all__'
    )

    if request.method == 'POST':
        form = LaboratorioForm(request.POST, instance=laboratorio)
        formset = AnaliseFormSet(request.POST, instance=laboratorio)

        if form.is_valid() and formset.is_valid():
            laboratorio = form.save()
            formset.instance = laboratorio
            formset.save()
            messages.success(request, 'Dados atualizados com sucesso!')
            return redirect('laboratorios_cadastrados')
        else:
            print(form.errors)  # Imprime os erros de validação
            print(formset.errors)  # Imprime os erros de validação do formset
    else:
        form = LaboratorioForm(instance=laboratorio)
        formset = AnaliseFormSet(instance=laboratorio)

    return render(request, 'cadastro_laboratorio.html', {'form': form, 'formset': formset})


def calendario_campanhas(request):
    campanhas = ProgramaColeta.objects.all()
    eventos = []

    for campanha in campanhas:
        eventos.append({
            # Substitua 'id' por um campo existente apropriado
            'title': campanha.ordem_servico,
            'start': campanha.data_coleta_campo.isoformat(),
            'end': campanha.data_coleta_campo.isoformat(),
            # URL corrigida para detalhes da campanha
            'url': f'/checklist_campanha/{campanha.ordem_servico}/'
        })

    context = {
        'eventos': json.dumps(eventos)
    }
    return render(request, 'calendario.html', context)


def exportar_resultados_csv(request):
    try:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="resultados_coleta.csv"'

        writer = csv.writer(response)
        writer.writerow(['Código Coleta', 'Hora Início', 'Hora Fim', 'Ponto', 'Temperatura',
                        'pH', 'ORP', 'Condutividade', 'Turbidez', 'OD', 'OD %', 'TDS', 'Salinidade'])

        try:
            resultados = Campo.objects.all().values_list('codigo_coleta', 'hora_inicio', 'hora_fim', 'ponto',
                                                         'temperatura', 'ph', 'orp', 'condutividade', 'turbidez', 'od', 'tds', 'salinidade')
        except ObjectDoesNotExist:
            logger.error("Nenhum resultado encontrado.")
            return HttpResponse("Nenhum resultado encontrado.", content_type='text/plain')
        except Exception as e:
            logger.error(f"Erro ao consultar o banco de dados: {e}")
            return HttpResponse(f"Erro ao consultar o banco de dados: {e}", content_type='text/plain')

        for resultado in resultados:
            try:
                writer.writerow(resultado)
            except Exception as e:
                logger.error(f"Erro ao escrever linha CSV: {e}")
                return HttpResponse(f"Erro ao escrever linha CSV: {e}", content_type='text/plain')

        return response

    except Exception as e:
        logger.error(f"Erro ao gerar CSV: {e}")
        return HttpResponse(f"Erro ao gerar CSV: {e}", content_type='text/plain')


@login_required
def cadastro_local(request):
    if request.method == 'POST':
        form = LocaisForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Local cadastrado com sucesso.')
            return redirect('cadastro_local')
    else:
        form = LocaisForm()
    return render(request, 'cadastro_local.html', {'form': form})


@login_required
def atualizar_local(request, id):
    local = get_object_or_404(TabLocal, id=id)
    if request.method == 'POST':
        form = LocaisForm(request.POST, instance=local)
        if form.is_valid():
            form.save()
            messages.success(request, 'Local atualizado com sucesso.')
            return redirect('cadastro_local')
    else:
        form = LocaisForm(instance=local)
    return render(request, 'cadastro_local.html', {'form': form})


@login_required
def cadastro_setor(request):
    if request.method == 'POST':
        form = SetorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Setor cadastrado com sucesso.')
            return redirect('cadastro_setor')
    else:
        form = SetorForm()
    return render(request, 'cadastro_setor.html', {'form': form})


@login_required
def atualizar_setor(request, id):
    setor = get_object_or_404(TabSetor, id=id)
    if request.method == 'POST':
        form = SetorForm(request.POST, instance=setor)
        if form.is_valid():
            form.save()
            messages.success(request, 'Setor atualizado com sucesso.')
            return redirect('cadastro_setor')
    else:
        form = SetorForm(instance=setor)
    return render(request, 'cadastro_setor.html', {'form': form})


@login_required
def cadastro_ponto(request):
    if request.method == 'POST':
        form = PontoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ponto cadastrado com sucesso.')
            return redirect('cadastro_ponto')
    else:
        form = PontoForm()
    return render(request, 'cadastro_ponto.html', {'form': form})


@login_required
def atualizar_ponto(request, id):
    ponto = get_object_or_404(TabPonto, id=id)
    if request.method == 'POST':
        form = PontoForm(request.POST, instance=ponto)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ponto atualizado com sucesso.')
            return redirect('cadastro_ponto')
    else:
        form = PontoForm(instance=ponto)
    return render(request, 'cadastro_ponto.html', {'form': form})


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

    return render(request, 'locais_cadastrados.html', {
        'table_setores': table_setores,
        'table_pontos': table_pontos,
        'table_locais': table_locais,
        'setor_filter': setor_filter,
        'ponto_filter': ponto_filter,
        'local_filter': local_filter
    })


def export_pontos_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="pontos_coleta.csv"'

    writer = csv.writer(response, delimiter=';',
                        quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(['Nome', 'Setor', 'Local', 'Descrição',
                    'Status', 'Latitude', 'Longitude'])

    pontos = TabPonto.objects.select_related('setor', 'local').all()
    for ponto in pontos:
        writer.writerow([
            ponto.nome,
            ponto.setor,  # Acessa o nome do setor
            ponto.local,  # Acessa o nome do local
            ponto.nome,
            'Ativo' if ponto.status else 'Inativo',
            ponto.lat,
            ponto.lon,
            ponto.tipo
        ])

    return response


@login_required
def cadastro_parametro(request):
    if request.method == 'POST':
        form = ParametroForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Parâmetro cadastrado com sucesso.')
            return redirect('cadastro_parametro')
    else:
        form = ParametroForm()
    return render(request, 'cadastro_parametro.html', {'form': form})


@login_required
def cadastro_unidade_medida(request):
    if request.method == 'POST':
        form = UnidadeMedidaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request, 'Unidade de Medida cadastrada com sucesso.')
            return redirect('cadastro_unidade_medida')
    else:
        form = UnidadeMedidaForm()
    return render(request, 'cadastro_unidade_medida.html', {'form': form})


@login_required
def cadastro_tipo_parametro(request):
    if request.method == 'POST':
        form = TipoParametroForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request, 'Tipo de Parâmetro cadastrado com sucesso.')
            return redirect('cadastro_tipo_parametro')
    else:
        form = TipoParametroForm()

    table_tipo_parametro = TipoParametroTable(TipoParametro.objects.all())
    RequestConfig(request, paginate={"per_page": 25}).configure(
        table_tipo_parametro)

    return render(request, 'cadastro_tipo_parametro.html', {'form': form, 'table_tipo_parametro': table_tipo_parametro})


@login_required
def configuracoes_view(request):
    if request.method == 'POST':
        if 'param_submit' in request.POST:
            param_form = ParametroForm(request.POST, label_suffix='param')
            if param_form.is_valid():
                param_form.save()
                messages.success(request, 'Parâmetro salvo com sucesso.')
        elif 'frasco_submit' in request.POST:
            frasco_form = TabFrascoForm(request.POST, label_suffix='frasco')
            if frasco_form.is_valid():
                frasco_form.save()
                messages.success(request, 'Frasco salvo com sucesso.')
        elif 'equipe_submit' in request.POST:
            equipe_form = TabEquipeForm(request.POST, label_suffix='equipe')
            if equipe_form.is_valid():
                equipe = equipe_form.save(commit=False)
                equipe.responsavel = request.user  # Define o campo responsavel
                equipe.save()
                messages.success(request, 'Equipe salva com sucesso.')
        elif 'laboratorio_submit' in request.POST:
            laboratorio_form = TabLaboratorioForm(request.POST, label_suffix='laboratorio')
            if laboratorio_form.is_valid():
                laboratorio_form.save()
                messages.success(request, 'Laboratório salvo com sucesso.')
        elif 'produto_submit' in request.POST:
            produto_form = TabProdutoForm(request.POST, label_suffix='produto')
            if produto_form.is_valid():
                produto_form.save()
                messages.success(request, 'Produto salvo com sucesso.')
        elif 'prodxparam_submit' in request.POST:
            prodxparam_form = TabProdxParamForm(request.POST, label_suffix='prodxparam')
            if prodxparam_form.is_valid():
                prodxparam_form.save()
                messages.success(request, 'Produto x Parâmetro salvo com sucesso.')
        elif 'serie_classificacao_submit' in request.POST:
            serie_classificacao_form = TabSerieClassificacaoForm(request.POST, label_suffix='serie_classificacao')
            if serie_classificacao_form.is_valid():
                serie_classificacao_form.save()
                messages.success(request, 'Série de Classificação salva com sucesso.')

        return redirect('configuracoes')
    else:
        param_form = ParametroForm()
        frasco_form = TabFrascoForm()
        equipe_form = TabEquipeForm()
        laboratorio_form = TabLaboratorioForm()
        produto_form = TabProdutoForm()
        prodxparam_form = TabProdxParamForm()
        serie_classificacao_form = TabSerieClassificacaoForm()

    # Instanciar as tabelas
    table_parametro = ParametroTable(TabParam.objects.all())
    table_frasco = FrascoTable(TabFrasco.objects.all())
    table_equipe = EquipeTable(TabEquipe.objects.all())
    table_laboratorio = LaboratorioTable(TabLaboratorio.objects.all())
    table_produto = ProdutoTable(TabProduto.objects.all())
    table_prodxparam = ProdxparamTable(TabProdxparam.objects.all())
    table_serie_classificacao = SerieClassificacaoTable(TabSerieClassificacao.objects.all())

    # Configurar a paginação das tabelas
    RequestConfig(request, paginate={"per_page": 25}).configure(table_parametro)
    RequestConfig(request, paginate={"per_page": 25}).configure(table_frasco)
    RequestConfig(request, paginate={"per_page": 25}).configure(table_equipe)
    RequestConfig(request, paginate={"per_page": 25}).configure(table_laboratorio)
    RequestConfig(request, paginate={"per_page": 25}).configure(table_produto)
    RequestConfig(request, paginate={"per_page": 25}).configure(table_prodxparam)
    RequestConfig(request, paginate={"per_page": 25}).configure(table_serie_classificacao)

    # Renderizar o template com os formulários e tabelas
    return render(request, 'configuracoes.html', {
        'param_form': param_form,
        'frasco_form': frasco_form,
        'equipe_form': equipe_form,
        'laboratorio_form': laboratorio_form,
        'produto_form': produto_form,
        'prodxparam_form': prodxparam_form,
        'serie_classificacao_form': serie_classificacao_form,
        'table_parametro': table_parametro,
        'table_frasco': table_frasco,
        'table_equipe': table_equipe,
        'table_laboratorio': table_laboratorio,
        'table_produto': table_produto,
        'table_prodxparam': table_prodxparam,
        'table_serie_classificacao': table_serie_classificacao
    })

@login_required
def editar_registro(request, tabela, pk):
    model_map = {
        'param': (TabParam, ParametroForm),
        'frasco': (TabFrasco, TabFrascoForm),
        'equipe': (TabEquipe, TabEquipeForm),
        'laboratorio': (TabLaboratorio, TabLaboratorioForm),
        'produto': (TabProduto, TabProdutoForm),
        'prodxparam': (TabProdxparam, TabProdxParamForm),
        'serie_classificacao': (TabSerieClassificacao, TabSerieClassificacaoForm),
    }

    if tabela not in model_map:
        messages.error(request, 'Tabela inválida.')
        return redirect('configuracoes')

    model, form_class = model_map[tabela]
    instance = get_object_or_404(model, pk=pk)

    if request.method == 'POST':
        form = form_class(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registro atualizado com sucesso!')
            return redirect('configuracoes')
    else:
        form = form_class(instance=instance)

    return render(request, 'configuracoes_editar.html', {'form': form, 'tabela': tabela})

def direcionamento_campanha(request):
    return render(request, 'direcionamento_campanha.html')


def cadastro_campanha(request):
    if request.method == 'POST':
        form = CadastroCampanhaForm(request.POST)
        if form.is_valid():
            form.save()
            # Substitua 'success_url' pela URL de sucesso desejada
            return redirect('cadastro_coleta')
    else:
        form = CadastroCampanhaForm()

    return render(request, 'cadastro_campanha.html', {'form': form})




def cadastro_coleta_view(request):
    if request.method == 'POST':
        form = CadastroColetaForm(request.POST)
        if form.is_valid():
            form.save()
            # Substitua 'success_url' pela URL de sucesso desejada
            return redirect('checklist_coleta')
    else:
        form = CadastroColetaForm()

    return render(request, 'cadastro_coleta.html', {'form': form})


def cadastro_item_checklist_coleta(request):
    if request.method == 'POST':
        form = CadastroItemChecklistColetaForm(request.POST)
        if form.is_valid():
            form.save(user=request.user)
            messages.success(
                request, 'Item de checklist cadastrado com sucesso.')
            return redirect('cadastro_item_checklist_coleta')
    else:
        form = CadastroItemChecklistColetaForm()

    # Crie a tabela com os itens existentes
    table = TipoItemChecklistColetaTable(TabItemChecklistColeta.objects.all())
    RequestConfig(request).configure(table)

    return render(request, 'cadastro_item_checklist_coleta.html', {'form': form, 'table': table})

def checklist_coleta(request):

    return render(request, 'checklist_coleta.html')


def export_csv(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM tab_medida_pivotada")
        rows = cursor.fetchall()
        columns = [col[0] for col in cursor.description]

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="tab_medida_pivotada.csv"'

    writer = csv.writer(response)
    writer.writerow(columns)
    for row in rows:
        writer.writerow(row)

    return response


def view_tab_medida_pivotada(request):
    # Campo padrão para ordenar
    order_by = request.GET.get('order_by', 'campanha')
    # Direção padrão para ordenar
    direction = request.GET.get('direction', 'asc')

    # Filtros de campanha e ponto
    campanha_filter = request.GET.get('campanha', '')
    ponto_filter = request.GET.get('ponto', '')

    # Construir a cláusula WHERE corretamente
    where_clauses = []
    if campanha_filter:
        where_clauses.append(f"campanha = '{campanha_filter}'")
    if ponto_filter:
        where_clauses.append(f"ponto = '{ponto_filter}'")
    where_clause = ' AND '.join(where_clauses) if where_clauses else '1=1'

    # Construir a cláusula ORDER BY corretamente
    order_clause = f'"{order_by}" {direction.upper()}'

    with connection.cursor() as cursor:
        cursor.execute(
            f'SELECT * FROM tab_medida_pivotada WHERE {where_clause} ORDER BY {order_clause}')
        rows = cursor.fetchall()
        columns = [col[0] for col in cursor.description]

    paginator = Paginator(rows, 20)  # Limitar a 20 resultados por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'columns': columns,
        'page_obj': page_obj,
        'order_by': order_by,
        'direction': direction,
        'campanha_filter': campanha_filter,
        'ponto_filter': ponto_filter
    }
    return render(request, 'view_tab_medida_pivotada.html', context)
