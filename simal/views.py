# pylint: disable=protected-access,no-member

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django_tables2 import RequestConfig
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from datetime import datetime, timedelta
from django.http import JsonResponse, Http404, HttpResponse, HttpResponseRedirect
from .forms import *
from .tables import *
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
            'status_coleta': status_coleta
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
    coleta = ColetaCampo.objects.get(id=id)
    form = ColetaCampo(instance=coleta)
    if request.method == 'POST':
        form = ColetaCampo(request.POST, instance=coleta)
        if form.is_valid():
            form.save()
            messages.success(request, 'Dados atualizados com sucesso!')
    return render(request, 'coleta/coleta.html', {'form': form})




@login_required
def deletar_coleta(request, id):
    coleta = ColetaCampo.objects.get(id=id)
    coleta.delete()
    return redirect('lista_coleta')


@login_required
def lista_coleta(request):
    table = ColetaCampoTable(Campo.objects.all())
    RequestConfig(request, paginate={"per_page": 25}).configure(table)
    return render(request, 'coleta/lista_coleta.html', {
        'table_campo': table
        })


@login_required
def coletas_agendas(request):
    table = ProgramaColetaTable(ProgramaColeta.objects.all())
    RequestConfig(request, paginate={"per_page": 25}).configure(table)
    return render(request, 'coleta/coletas_agendas.html', {
        'table_agenda_coleta': table
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
            programa_coleta.laboratorio = form.cleaned_data['laboratorio']
            programa_coleta.solicitante = form.cleaned_data['solicitante']
            programa_coleta.local_coleta = form.cleaned_data['local_coleta']
            programa_coleta.status_coleta = form.cleaned_data['status_coleta']
            programa_coleta.observacoes = form.cleaned_data['observacoes']

            # Salva o modelo no banco de dados
            programa_coleta.save(usuario=request.user)

            return redirect('coletas_agendas')
    else:
        form = ProgramaColetaForm()

    return render(request, 'coleta/agendar_coleta.html', {'form': form})


@login_required
def atualizar_programacao(request, id):
    """
    Atualiza a programação de coleta com base nos dados fornecidos pelo formulário.

    Args:
        request (HttpRequest): O objeto HttpRequest que contém os dados da requisição.
        id (int): O ID da programação de coleta a ser atualizada.

    Returns:
        HttpResponse: O objeto HttpResponse que renderiza o template 'coleta/agendar_coleta.html'
                      com o formulário atualizado ou redireciona para a página 'coletas_agendas'
                      em caso de sucesso na atualização dos dados.

    Raises:
        Http404: Se a programação de coleta com o ID fornecido não existir.

    """
    programacao = get_object_or_404(ProgramaColeta, id=id)
    if request.method == 'POST':
        form = ProgramaColetaForm(request.POST)
        if form.is_valid():
            for field, value in form.cleaned_data.items():
                setattr(programacao, field, value)
            programacao.save()
            messages.success(request, 'Dados atualizados com sucesso!')
            return redirect('coletas_agendas')
        else:
            print(form.errors)  # Imprime os erros de validação
    else:
        form_data = {field.name: getattr(
            programacao, field.name) for field in ProgramaColeta._meta.fields}
        if 'data_coleta' in form_data:
            form_data['data_coleta'] = form_data['data_coleta'].strftime(
                '%Y-%m-%d %H:%M:%S')
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
def checklist_campanha(request):
    ordem_servico_selecionada = request.GET.get('ordem_servico')
    form = ChecklistCampoForm(
        request.POST or None, ordem_servico_selecionada=ordem_servico_selecionada)

    if request.method == 'POST' and form.is_valid():
        checklist_campanha = ChecklistCampo()
        ordem_servico_instance = get_object_or_404(
            ProgramaColeta, ordem_servico=ordem_servico_selecionada)
        redirect_url = reverse('gerar_rota_campanha') + \
            f'?ordem_servico={ordem_servico_instance.ordem_servico}'

        # Atribui os campos do formulário e outros valores diretamente
        for campo in ('observacoes', 'previsao_tempo', 'avisar_labs',
                      'reservar_carro', 'reservar_barco', 'separar_equipamentos',
                      'conferir_equipamentos', 'comprar_gelo'):
            setattr(checklist_campanha, campo, form.cleaned_data[campo])

        checklist_campanha.ordem_servico = ordem_servico_instance
        checklist_campanha.save()

        return redirect (redirect_url)

    return render(request, 'coleta/checklist_campanha.html', {'form': form})


@login_required
def gerar_rota_campanha(request):
    ordem_servico = request.GET.get('ordem_servico')
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
        # Supondo que ponto tenha um atributo id
        campo.codigo_coleta = str(ponto.ponto) + ordem_servico
        campo.clima = previsao_tempo
        campo.save()

    # Atenção: O redirecionamento não deve estar dentro do loop
    if request.method == 'POST' and campanha:
        return HttpResponseRedirect(reverse('home'))

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
        form_data = {field.name: getattr(laboratorio, field.name) for field in Laboratorios._meta.fields}
        form = LaboratorioForm(initial=form_data)
    return render(request, 'cadastro_laboratorio.html', {'form': form})
