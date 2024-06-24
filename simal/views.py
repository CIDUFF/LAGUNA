# pylint: disable=protected-access,no-member

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django_tables2 import RequestConfig
from django.contrib.auth.decorators import login_required
from .forms import *
from .tables import *



# from django.views.generic import ListView
# from .models import ColetaCampo

def home(request):
    
    return render(request, 'home.html')

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
            # Cria uma nova instância do modelo ProgramaColeta
            programa_coleta = ProgramaColeta()

            # Atribui os dados do formulário aos campos do modelo
            programa_coleta.data_coleta_campo = form.cleaned_data['data_coleta_campo']

            # Busca a instância correta do modelo Coletores e a atribui ao campo equipe_coleta
            # equipe_coleta = Coletores.objects.filter(equipe=form.cleaned_data['equipe_coleta'])
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
def checklist_campanha(request):
    if request.method == 'POST':
        form = ChecklistCampoForm(request.POST)
        if form.is_valid():
            # Cria uma nova instância do modelo ProgramaColeta
            checklist_campanha = ChecklistCampoForm()

            # programa_coleta.data_coleta_campo = form.cleaned_data['data_coleta_campo']
            checklist_campanha.ordem_servico = form.cleaned_data['ordem_servico']
            checklist_campanha.status_checklist = form.cleaned_data['status_checklist']
            checklist_campanha.observacoes = form.cleaned_data['observacoes']
            

            # Salva o modelo no banco de dados
            checklist_campanha.save()

            return redirect('checklist_campanha')
    else:
        form = ChecklistCampoForm()

    return render(request, 'coleta/checklist_campanha.html', {'form': form})
            
def ajuda(request):
    
    return render(request, 'ajuda.html')

# ----------------------------------------------------------------------------------

# front_end










