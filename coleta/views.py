from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import Coleta_agua
from django.contrib.auth.decorators import login_required
from .models import Coleta_lagoa


@login_required
def coleta(request):
    if request.method == 'POST':
        form = Coleta_agua(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_coleta')
    else:
        form = Coleta_agua()
    return render(request, 'coleta/coleta.html', {'form': form})


@login_required
def lista_coleta(request):
    coletas = Coleta_lagoa.objects.all()
    return render(request, 'coleta/lista_coleta.html', {'coletas': coletas})

@login_required
def atualizar_coleta(request, id):
    coleta = Coleta_lagoa.objects.get(id=id)
    form = Coleta_agua(instance=coleta)
    if request.method == 'POST':
        form = Coleta_agua(request.POST, instance=coleta)
        if form.is_valid():
            form.save()
            messages.success(request, 'Dados atualizados com sucesso!')
    return render(request, 'coleta/coleta.html', {'form': form})



def home(request):
    return render(request, 'home.html')


