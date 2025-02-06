from django.http import JsonResponse
from django.db.models import Q
from .models import TabColeta, TabSetor, TabPonto, TabCampanha

def get_filtered_options(request):
    # Pegar todos os filtros ativos
    campanha = request.GET.get('campanha')
    coleta = request.GET.get('coleta')
    setor = request.GET.get('setor')
    ponto = request.GET.get('ponto')
    
    # Queries iniciais
    campanhas_qs = TabCampanha.objects.all()
    coletas_qs = TabColeta.objects.all()
    setores_qs = TabSetor.objects.all()
    pontos_qs = TabPonto.objects.filter(status=True)

    # Filtrar por campanha
    if campanha:
        campanhas_qs = campanhas_qs.filter(nome=campanha)
        coletas_qs = coletas_qs.filter(id_campanha__nome=campanha)
        # Pegar setores relacionados às coletas desta campanha
        setores_ids = coletas_qs.values_list('id_setor_id', flat=True).distinct()
        setores_qs = setores_qs.filter(id__in=setores_ids)
        # Filtrar pontos dos setores relacionados
        pontos_qs = pontos_qs.filter(id_setor__in=setores_ids)

    # Filtrar por coleta
    if coleta:
        coleta_obj = coletas_qs.filter(nome=coleta).first()
        if coleta_obj:
            coletas_qs = coletas_qs.filter(Q(id=coleta_obj.id))
            # Pegar apenas o setor desta coleta
            setores_qs = setores_qs.filter(id=coleta_obj.id_setor.id)
            # Pegar pontos apenas deste setor
            pontos_qs = pontos_qs.filter(id_setor=coleta_obj.id_setor)

    # Filtrar por setor
    if setor:
        setor_obj = setores_qs.filter(nome=setor).first()
        if setor_obj:
            setores_qs = setores_qs.filter(id=setor_obj.id)
            # Filtrar coletas deste setor
            coletas_qs = coletas_qs.filter(id_setor=setor_obj)
            # Filtrar apenas pontos deste setor
            pontos_qs = pontos_qs.filter(id_setor=setor_obj)

    # Filtrar por ponto
    if ponto:
        ponto_obj = pontos_qs.filter(nome=ponto).first()
        if ponto_obj:
            pontos_qs = pontos_qs.filter(id=ponto_obj.id)
            # Filtrar setor deste ponto
            setores_qs = setores_qs.filter(id=ponto_obj.id_setor.id)
            # Filtrar coletas do setor deste ponto
            coletas_qs = coletas_qs.filter(id_setor=ponto_obj.id_setor)

    # Preparar dados garantindo valores únicos e ordenados
    data = {
        'campanhas': list(campanhas_qs.order_by('nome').values_list('nome', flat=True).distinct()),
        'coletas': list(coletas_qs.order_by('nome').values_list('nome', flat=True).distinct()),
        'setores': list(setores_qs.order_by('nome').values_list('nome', flat=True).distinct()),
        'pontos': list(pontos_qs.order_by('nome').values_list('nome', flat=True).distinct())
    }
    
    return JsonResponse(data)
