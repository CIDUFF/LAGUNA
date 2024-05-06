from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ColetaCampo
from django.contrib.auth.decorators import login_required
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


@login_required
def lista_coleta(request):
    coletas = ColetaCampo.objects.all()
    return render(request, 'coleta/lista_coleta.html', {'coletas': coletas})

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



def home(request):
    return render(request, 'home.html')


