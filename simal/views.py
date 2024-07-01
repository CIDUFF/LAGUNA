# pylint: disable=protected-access,no-member

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django_tables2 import RequestConfig
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from datetime import datetime, timedelta
from django.http import JsonResponse
from .forms import *
from .tables import *
from .services import get_weather_description



# from django.views.generic import ListView
# from .models import ColetaCampo

def home(request):
    
    proxima_campanha = ProgramaColeta.objects.filter(data_coleta_campo__gt=timezone.now()).order_by('data_coleta_campo').first()
    # Chama a função get_weather_description para obter a descrição do tempo
    weather_description = get_weather_description("Santa Catarina, BR")

    # Passa a descrição do tempo para o template, junto com outros contextos necessários
    return render(request, 'home.html', {'weather_description': weather_description})
#TODO: Atualizar a view de coleta


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
            # Adicione a linha abaixo para atribuir o valor de data_fim_coleta_campo
            programa_coleta.data_fim_coleta_campo = form.cleaned_data['data_fim_coleta_campo']
            programa_coleta.equipe_coleta = form.cleaned_data['equipe_coleta']
            programa_coleta.laboratorio = form.cleaned_data['laboratorio']
            programa_coleta.solicitante = form.cleaned_data['solicitante']
            programa_coleta.local_coleta = form.cleaned_data['local_coleta']
            programa_coleta.status_coleta = form.cleaned_data['status_coleta']
            programa_coleta.observacoes = form.cleaned_data['observacoes']

            # Salva o modelo no banco de dados
            programa_coleta.save()

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
        form_data = {field.name: getattr(programacao, field.name) for field in ProgramaColeta._meta.fields}
        if 'data_coleta' in form_data:
            form_data['data_coleta'] = form_data['data_coleta'].strftime('%Y-%m-%d %H:%M:%S')
        form = ProgramaColetaForm(initial=form_data)
    return render(request, 'coleta/agendar_coleta.html', {'form': form})

@login_required
def iniciar_campanha(request):
    if request.method == 'POST':
        form = IniciarCampanhaForm(request.POST)
        if form.is_valid():
            ordem_servico = form.cleaned_data['ordem_servico'].id  # Corrigido aqui
            redirect_url = reverse('checklist_campanha') + \
                f'?ordem_servico={ordem_servico}'
            return redirect(redirect_url)
    else:
        form = IniciarCampanhaForm()

    return render(request, 'coleta/iniciar_campanha.html', {'form': form})
            

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

            nova_ajuda = Ajuda() ## Model
            nova_ajuda.nome = form.cleaned_data['nome']
            nova_ajuda.email = form.cleaned_data['email']
            nova_ajuda.pergunta = form.cleaned_data['pergunta']

            nova_ajuda.save()


            return redirect('ajuda')
    else:
        form = AjudaForm()

    return render(request, 'ajuda.html', {'form': form})



## View para pagina de inicio de campanha

@login_required
def iniciar_campanha(request):
    if request.method == 'POST':
        form = IniciarCampanhaForm(request.POST)
        if form.is_valid():
            ordem_servico = form.cleaned_data['ordem_servico'].ordem_servico
            redirect_url = reverse('checklist_campanha') + \
                f'?ordem_servico={ordem_servico}'
            return redirect(redirect_url)
    else:
        form = IniciarCampanhaForm()

    return render(request, 'coleta/iniciar_campanha.html', {'form': form})


@login_required
def checklist_campanha(request):
    ordem_servico_selecionada = request.GET.get('ordem_servico', None)
    if request.method == 'POST':
        form = ChecklistCampoForm(request.POST)
        if form.is_valid():
            checklist_campanha = ChecklistCampo()

            # Busca a instância de ProgramaColeta usando o ID fornecido
            ordem_servico_instance = get_object_or_404(
                ProgramaColeta, ordem_servico=ordem_servico_selecionada)

            checklist_campanha.ordem_servico = ordem_servico_instance
            checklist_campanha.status_checklist = form.cleaned_data['status_checklist']
            checklist_campanha.observacoes = form.cleaned_data['observacoes']
            checklist_campanha.previsao_tempo = form.cleaned_data['previsao_tempo']
            checklist_campanha.avisar_labs = form.cleaned_data['avisar_labs']
            checklist_campanha.reservar_carro = form.cleaned_data['reservar_carro']
            checklist_campanha.reservar_barco = form.cleaned_data['reservar_barco']
            checklist_campanha.separar_equipamentos = form.cleaned_data['separar_equipamentos']
            checklist_campanha.conferir_equipamentos = form.cleaned_data['conferir_equipamentos']
            checklist_campanha.comprar_gelo = form.cleaned_data['comprar_gelo']

            checklist_campanha.save()

            return redirect('home')
    else:
        form = ChecklistCampoForm(
            ordem_servico_selecionada=ordem_servico_selecionada)

    return render(request, 'coleta/checklist_campanha.html', {'form': form})


