from django.shortcuts import render
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
            messages.success(request, 'Dados salvos com sucesso!')
    else:
        form = Coleta_agua()
    return render(request, 'coleta/coleta.html', {'form': form})


@login_required
def lista_coleta(request):
    coletas = Coleta_lagoa.objects.all()
    return render(request, 'coleta/lista_coleta.html', {'coletas': coletas})


def home(request):
    return render(request, 'home.html')


