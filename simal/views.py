from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import *
from django.contrib.auth.decorators import login_required
from .tables import *
from django_tables2 import RequestConfig

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
            equipe_coleta = Coletores.objects.filter(equipe=form.cleaned_data['equipe_coleta']).first()
            programa_coleta.equipe_coleta = equipe_coleta
            programa_coleta.Laboratorio = form.cleaned_data['laboratorio']
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


    








