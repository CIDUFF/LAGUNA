# pylint: disable=protected-access,no-member
from django.shortcuts import render, redirect, get_object_or_404
from django.core.cache import cache
from django.contrib import messages
from django_tables2 import RequestConfig
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from datetime import datetime, timedelta
from django.http import JsonResponse, Http404, HttpResponse, HttpResponseRedirect
from .forms import *
from .tables import *
from .filters import *
from .services import get_weather_description

# from django.views.generic import ListView
# from .models import ColetaCampo


def home(request):
    try:
        data_coleta_proxima = ProgramaColeta.objects.filter(
            data_coleta_campo__gte=timezone.now()
        ).order_by('data_coleta_campo').values_list('data_coleta_campo', flat=True).first()

        status_coleta = ProgramaColeta.objects.filter(
            data_coleta_campo__gte=timezone.now()
        ).order_by('data_coleta_campo').values_list('status_coleta', flat=True).first()

        ordem_servico = ProgramaColeta.objects.filter(
            data_coleta_campo__gte=timezone.now()
        ).order_by('data_coleta_campo').values_list('id', flat=True).first()

        percentual_checklist = ChecklistCampo.objects.filter(
            ordem_servico=ordem_servico).values_list('progresso', flat=True).first()

        if data_coleta_proxima:
            data_coleta_proxima_formatada = data_coleta_proxima.strftime(
                '%Y-%m-%d')
            weather_description = get_weather_description(
                "Maricá", data_coleta_proxima_formatada)
            # Atualiza a formatação da data após confirmar que ela existe
            data_coleta_proxima_formatada = data_coleta_proxima.strftime(
                '%d/%m/%Y')
        else:
            data_coleta_proxima_formatada = None
            weather_description = None

        # Criando a variável context para organizar os dados passados para o template
        context = {
            'weather_description': weather_description,
            'data_coleta_proxima_formatada': data_coleta_proxima_formatada,
            'status_coleta': status_coleta,
            'percentual_checklist': percentual_checklist
        }

        return render(request, 'home.html', context)
    except ProgramaColeta.DoesNotExist:
        # Tratamento para o caso de não encontrar ProgramaColeta
        return HttpResponse("Nenhum programa de coleta encontrado.", status=404)
    except Exception as e:
        # Tratamento genérico de erro
        return HttpResponse(f"Erro ao carregar a página: {str(e)}", status=500)


@login_required
def coleta(request):
    if request.method == 'POST':
        form = ColetaCampo(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_coleta')

    else:
        form = ColetaCampo()
    return render(request, 'coleta/coleta.html', {'form': form})

# TODO: Atualizar a view de coleta


@login_required
def atualizar_coleta(request, id):
    coleta = get_object_or_404(Campo, id=id)
    form_data = {field: getattr(coleta, field)
                 for field in ColetaCampo.base_fields}
    form_data['hora_inicio'] = timezone.now().strftime('%H:%M')
    form = ColetaCampo(initial=form_data)

    if request.method == 'POST':
        post_data = request.POST.copy()
        post_data['hora_fim'] = timezone.now().strftime('%H:%M')
        form = ColetaCampo(post_data)

        if form.is_valid():
            for field, value in form.cleaned_data.items():
                setattr(coleta, field, value)
            coleta.save()
            messages.success(request, 'Dados atualizados com sucesso!')

            # Obtenha todos os pontos de coleta da mesma ordem de serviço,
            # ordenados por algum critério que defina a sequência
            pontos_coleta = Campo.objects.filter(
                ordem_servico=coleta.ordem_servico).order_by('ponto')
            # Encontre o índice do ponto de coleta atual
            index_atual = list(pontos_coleta).index(coleta)
            # Verifique se existe um próximo ponto de coleta
            if index_atual + 1 < len(pontos_coleta):
                proximo_ponto = pontos_coleta[index_atual + 1]
                return redirect(reverse('atualizar_coleta', args=[proximo_ponto.id]))
            else:
                # Se não houver próximo ponto, redirecione para a lista de coletas ou página de conclusão
                return redirect('lista_coleta')
        else:
            pass  # Mantenha o formulário com erros para exibição

    context = {'form': form, 'codigo_coleta': coleta.codigo_coleta,
               'ponto': coleta.ponto}
    return render(request, 'coleta/coleta.html', context)


@login_required
def deletar_coleta(request, id):
    coleta = ColetaCampo.objects.get(id=id)
    coleta.delete()
    return redirect('lista_coleta')


@login_required
def lista_coleta(request, ordem_servico=None):
    # filtro = CampoFilter(request.GET, queryset=Campo.objects.all())
    filtro = CampoFilter(request.GET, queryset=Campo.objects.filter(ordem_servico_id=ordem_servico))
    table = ColetaCampoTable(filtro.qs)
    RequestConfig(request, paginate={"per_page": 25}).configure(table)
    return render(request, 'coleta/lista_coleta.html', {
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
            programa_coleta.data_fim_coleta_campo = form.cleaned_data['data_fim_coleta_campo']
            programa_coleta.equipe_coleta = form.cleaned_data['equipe_coleta']
            # programa_coleta.laboratorio = form.cleaned_data['laboratorio']
            programa_coleta.solicitante = form.cleaned_data['solicitante']
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

    if programacao is None:
        programacao = get_object_or_404(ProgramaColeta, id=id)
        cache.set(cache_key, programacao, timeout=3600)  # Cache por 1 hora

    if request.method == 'POST':
        form = ProgramaColetaForm(request.POST, instance=programacao)
        if form.is_valid():
            form.save()
            cache.set(cache_key, programacao, timeout=3600)  # Atualiza o cache
            messages.success(request, 'Dados atualizados com sucesso!')
            return redirect('coletas_agendas')
        else:
            print(form.errors)  # Imprime os erros de validação
    else:
        form_data = {field.name: getattr(
            programacao, field.name) for field in ProgramaColeta._meta.fields}
        for date_field in ['data_coleta_campo', 'data_fim_coleta_campo']:
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
    Cancela a programação de coleta com base no ID fornecido.

    Args:
        request (HttpRequest): O objeto HttpRequest que contém os dados da requisição.
        id (int): O ID da programação de coleta a ser cancelada.

    Returns:
        HttpResponse: O objeto HttpResponse que redireciona para a página 'coletas_agendas'
                      em caso de sucesso no cancelamento dos dados.

    Raises:
        Http404: Se a programação de coleta com o ID fornecido não existir.

    """
    programacao = get_object_or_404(ProgramaColeta, id=id)
    programacao.status_coleta = 'Cancelada'
    programacao.save()
    messages.success(request, 'Programação de coleta cancelada com sucesso!')
    return redirect('coletas_agendas')

# ----------------------------------------------------------------------------------

# front_end


# @login_required
# def weather(request):
#     weather_description = get_weather_description("Niterói, BR")
#     return render(request, 'home.html', {'weather_description': weather_description})


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
    # Busca a instância da ordem de serviço antes de qualquer processamento
    ordem_servico_instance = get_object_or_404(
        ProgramaColeta, ordem_servico=ordem_servico_selecionada)

    # Verifica se a ordem de serviço está cancelada antes de prosseguir
    if ordem_servico_instance.status_coleta == 'Cancelada':
        messages.warning(
            request, 'Não é possível iniciar uma campanha cancelada')
        # Redireciona ou renderiza uma página específica para o erro
        return redirect('coletas_agendas')
    try:
        checklist_campanha = ChecklistCampo.objects.get(
            ordem_servico=ordem_servico_instance)
        if checklist_campanha.progresso == 100:
            # Substitua 'lista_coletas' pelo nome correto da sua URL
            return redirect('lista_coleta')
    except ChecklistCampo.DoesNotExist:
        # Se não existir, você pode prosseguir com a criação ou outra lógica
        checklist_campanha = None
        # Continue com a lógica para criar um novo ChecklistCampo ou outra ação
    # Continua com a lógica original se a ordem de serviço não estiver cancelada
    checklist_campanha = None
    form = ChecklistCampoForm(
        request.POST or None, ordem_servico_selecionada=ordem_servico_selecionada)
    if request.method == 'POST' and form.is_valid():
        # A verificação de status foi movida, então esta parte permanece inalterada
        checklist_campanha, created = ChecklistCampo.objects.get_or_create(
            ordem_servico=ordem_servico_instance,
            defaults={campo: form.cleaned_data[campo] for campo in (
                'observacoes', 'previsao_tempo', 'avisar_labs',
                'reservar_carro', 'reservar_barco', 'separar_equipamentos',
                'conferir_equipamentos', 'comprar_gelo')}
        )
        if not created:
            for campo in ('observacoes', 'previsao_tempo', 'avisar_labs',
                          'reservar_carro', 'reservar_barco', 'separar_equipamentos',
                          'conferir_equipamentos', 'comprar_gelo'):
                setattr(checklist_campanha, campo, form.cleaned_data[campo])
            checklist_campanha.save()

        # Verifica se o progresso é igual a 100

        # ordem_servico_instance.status_coleta = 'Iniciada'
        ordem_servico_instance.save()
        return redirect('gerar_rota_campanha', ordem_servico=ordem_servico_instance.ordem_servico)

    context = {
        'form': form,
        'checklist_campanha': checklist_campanha
    }
    return render(request, 'coleta/checklist_campanha.html', context)


@login_required
def gerar_rota_campanha(request, ordem_servico=None):
    ordem_servico = request.GET.get('ordem_servico', ordem_servico)
    campanha = None
    previsao_tempo = None
    pontos_coleta = []

    if ordem_servico:
        campanha = get_object_or_404(
            ProgramaColeta, ordem_servico=ordem_servico)
        data = campanha.data_coleta_campo
        previsao_tempo = get_weather_description(
            "Maricá", data.strftime('%Y-%m-%d'))

    if request.method == 'POST' and campanha:
        local_campanha = ProgramaColeta.objects.filter(
            ordem_servico=ordem_servico).values_list('local_coleta', flat=True).first()
        pontos_coleta = LocaisColeta.objects.filter(
            local=local_campanha)

    # Antes do loop for, obtenha a instância de ProgramaColeta
        programa_coleta_instance = get_object_or_404(
            ProgramaColeta, ordem_servico=ordem_servico)

    for ponto in pontos_coleta:
        campo = Campo()
        # Agora, atribua a instância de ProgramaColeta ao campo ordem_servico
        campo.ordem_servico = programa_coleta_instance
        campo.ponto = str(ponto.ponto)
        campo.codigo_coleta = ordem_servico + str(ponto.ponto)
        campo.clima = previsao_tempo
        campo.save()

    campanha.status_coleta = 'Iniciada'

    # Atenção: O redirecionamento não deve estar dentro do loop
    if request.method == 'POST' and campanha:
        return redirect('lista_coleta', ordem_servico=ordem_servico)

    context = {
        'campanha': campanha,
        'previsao_tempo': previsao_tempo
    }
    return render(request, 'coleta/gerar_rota_campanha.html', context)


@login_required
def cadastro_laboratorio(request):
    if request.method == 'POST':
        form = LaboratorioForm(request.POST)
        if form.is_valid():
            laboratorio = Laboratorios()
            laboratorio.nome = form.cleaned_data['nome']
            laboratorio.email = form.cleaned_data['email']
            laboratorio.telefone = form.cleaned_data['telefone']
            laboratorio.endereco = form.cleaned_data['endereco']
            laboratorio.tipo = form.cleaned_data['tipo']
            laboratorio.save()
            return redirect('laboratorios_cadastrados')

    else:
        form = LaboratorioForm()

    return render(request, 'cadastro_laboratorio.html', {'form': form})


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
    if request.method == 'POST':
        form = LaboratorioForm(request.POST)
        if form.is_valid():
            for field, value in form.cleaned_data.items():
                setattr(laboratorio, field, value)
            laboratorio.save()
            messages.success(request, 'Dados atualizados com sucesso!')
            return redirect('laboratorios_cadastrados')
        else:
            print(form.errors)  # Imprime os erros de validação
    else:
        form_data = {field.name: getattr(
            laboratorio, field.name) for field in Laboratorios._meta.fields}
        form = LaboratorioForm(initial=form_data)
    return render(request, 'cadastro_laboratorio.html', {'form': form})
