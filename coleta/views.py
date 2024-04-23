from django.shortcuts import render
from django.contrib import messages
from .forms import Coleta_agua


def coleta(request):
    if request.method == 'POST':
        form = Coleta_agua(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Dados salvos com sucesso!')
    else:
        form = Coleta_agua()
    return render(request, 'coleta/coleta.html', {'form': form})
