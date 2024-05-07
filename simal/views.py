from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import *
from django.contrib.auth.decorators import login_required
from .tables import *
from django_tables2 import RequestConfig
# from django.views.generic import ListView
# from .models import ColetaCampo

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


# @login_required
# def lista_coleta(request):
#     coletas = ColetaCampo.objects.all()
#     return render(request, 'coleta/lista_coleta.html', {'coletas': coletas})

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
            form.save()
            return redirect('coletas_agendas')
    else:
        form = ProgramaColetaForm()
    return render(request, 'coleta/agendar_coleta.html', {'form': form})
    


def home(request):
    return render(request, 'home.html')




