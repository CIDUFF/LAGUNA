from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
import pandas as pd
import plotly.express as px
from .models import GrupoPontos, TabMedida, TabParam, TabSetor, TabPonto
import json
import traceback
from django.db.models import F

def load_data():
    # Buscar dados do banco de dados
    medidas = TabMedida.objects.select_related(
        'id_envio__id_amostra__id_coleta',
        'id_envio__id_amostra__id_ponto',
        'id_envio__id_amostra__id_coleta__id_setor',
        'id_pp__id_param'
    ).annotate(
        parametro=F('id_pp__id_param__nome'),
        unidade=F('id_pp__unidade'),
        ponto=F('id_envio__id_amostra__id_ponto__nome'),
        setor=F('id_envio__id_amostra__id_coleta__id_setor__nome'),
        data=F('id_envio__id_amostra__id_coleta__data')
    )
    
    # Converter para DataFrame
    df = pd.DataFrame.from_records(medidas.values(
        'parametro', 'unidade', 'ponto', 'setor', 'data', 'valor'
    ))
    
    # Renomear colunas para manter compatibilidade
    df = df.rename(columns={
        'parametro': 'Parâmetro',
        'unidade': 'Unidade',
        'ponto': 'Ponto',
        'setor': 'Setor',
        'data': 'Data',
        'valor': 'Valor'
    })
    
    return df

def dashboard(request):  # Alterado de index para dashboard
    # Buscar dados direto do banco
    parametros = TabParam.objects.values_list('nome', flat=True).distinct().order_by('nome')
    setores = TabSetor.objects.values_list('nome', flat=True).distinct().order_by('nome')
    pontos = TabPonto.objects.filter(status=True).values_list('nome', flat=True).distinct().order_by('nome')
    grupos = GrupoPontos.objects.all().order_by('nome')
    
    context = {
        'parametros': parametros,
        'setores': setores,
        'pontos': pontos,
        'grupos': grupos,
    }
    # Ajustar o caminho do template
    return render(request, 'dashboard.html', context)

def get_grafico(request):
    try:
        # Verifica se é uma requisição AJAX
        if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return HttpResponse("Requisição inválida", status=400)

        df = load_data()
        parametro = request.GET.get('parametro')
        setor = request.GET.get('setor')
        ponto = request.GET.get('ponto')
        grupo_id = request.GET.get('grupo')
        
        if not parametro:
            return HttpResponse("Parâmetro não selecionado", status=400)
        
        df_filtered = df[df['Parâmetro'] == parametro].copy()
        
        if setor:
            df_filtered = df_filtered[df_filtered['Setor'] == setor]
        
        # Filtrar por grupo se um grupo foi selecionado
        if grupo_id:
            grupo = GrupoPontos.objects.get(pk=grupo_id)
            pontos_grupo = [p for p in grupo.pontos]
            df_filtered = df_filtered[df_filtered['Ponto'].isin(pontos_grupo)]
        elif ponto:
            df_filtered = df_filtered[df_filtered['Ponto'] == ponto]
        
        if df_filtered.empty:
            return HttpResponse("Nenhum dado encontrado para os filtros selecionados", status=404)
            
        # Converter e formatar a data
        df_filtered['Data'] = pd.to_datetime(df_filtered['Data'])
        
        # Garantir que a coluna Valor seja numérica
        df_filtered['Valor'] = pd.to_numeric(df_filtered['Valor'].replace(['ND', 'NULL', 'None', '', 'Não medido'], '0'), errors='coerce')
        
        if df_filtered.empty:
            return HttpResponse('Não há dados disponíveis para este parâmetro')
        
        # Ordenar o DataFrame primeiro por Data para garantir a sequência temporal correta
        df_filtered = df_filtered.sort_values('Data')
        
        # Calcular média e desvio padrão geral
        media_geral = df_filtered['Valor'].mean()
        desvio_padrao = df_filtered['Valor'].std()
        limite_superior = media_geral + desvio_padrao
        limite_inferior = media_geral - desvio_padrao
        
        # Criar gráfico com Plotly com configurações melhoradas e nova configuração de linhas
        fig = px.line(df_filtered, 
                      x='Data', 
                      y='Valor', 
                      color='Ponto',
                      title=f'Evolução de {parametro} ao longo do tempo',
                      markers=True,
                      line_shape='linear')  # Forçar linhas retas entre os pontos
        
        # Adicionar linhas de desvio padrão
        fig.add_hline(y=limite_superior, 
                     line_dash="dash", 
                     line_color="red", 
                     annotation_text=f"Limite Superior (DP): {limite_superior:.2f}",
                     annotation_position="top right")
        
        fig.add_hline(y=limite_inferior, 
                     line_dash="dash", 
                     line_color="red", 
                     annotation_text=f"Limite Inferior (DP): {limite_inferior:.2f}",
                     annotation_position="bottom right")
        
        # Ajustar layout com foco na visualização temporal
        fig.update_layout(
            xaxis_title='Data',
            yaxis_title=f'{parametro} ({df_filtered["Unidade"].iloc[0]})',
            xaxis=dict(
                type='date',
                tickformat='%d/%m/%Y',
                tickangle=45,
                gridcolor='lightgray'
            ),
            yaxis=dict(
                gridcolor='lightgray',
                zeroline=True,
                zerolinecolor='gray',
                zerolinewidth=1
            ),
            hovermode='x unified',
            width=1000,
            height=600,
            margin=dict(l=50, r=50, t=50, b=100),  # Aumentado margem inferior para datas
            showlegend=True,
            template='plotly_white',
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01
            )
        )
        
        # Otimizar o gráfico
        fig.update_traces(
            line=dict(width=2),
            mode='lines+markers',
            marker=dict(size=6)
        )
        
        # Converter para HTML com configurações otimizadas
        grafico_html = fig.to_html(
            full_html=False,
            include_plotlyjs=True,
            config={
                'displayModeBar': True,
                'responsive': True,
                'scrollZoom': True,
                'displaylogo': False,
                'modeBarButtonsToAdd': ['select2d', 'lasso2d']
            }
        )
        
        return HttpResponse(grafico_html)
        
    except Exception as e:
        print(f"Erro ao gerar gráfico: {e}")
        print(traceback.format_exc())
        return HttpResponse(f'Erro ao gerar o gráfico: {str(e)}', status=500)

def dashboard_medias(request):
    df = load_data()
    parametros = sorted(df['Parâmetro'].unique())
    setores = sorted(df['Setor'].unique())
    grupos = GrupoPontos.objects.all().order_by('nome')
    
    context = {
        'parametros': parametros,
        'setores': setores,
        'grupos': grupos,
    }
    # Ajustar o caminho do template
    return render(request, 'dashboard_medias.html', context)

def get_grafico_medias(request):
    try:
        df = load_data()
        parametro = request.GET.get('parametro')
        setor = request.GET.get('setor')
        grupo_id = request.GET.get('grupo')
        
        if not parametro:
            return HttpResponse('')
        
        df_filtered = df[df['Parâmetro'] == parametro].copy()
        
        if setor:
            df_filtered = df_filtered[df_filtered['Setor'] == setor]
            
        # Filtrar por grupo se um grupo foi selecionado
        if grupo_id:
            try:
                grupo = GrupoPontos.objects.get(pk=grupo_id)
                pontos_grupo = json.loads(grupo.pontos)
                df_filtered = df_filtered[df_filtered['Ponto'].isin(pontos_grupo)]
            except GrupoPontos.DoesNotExist:
                return HttpResponse('Grupo não encontrado')
        
        # Converter e formatar a data
        df_filtered['Data'] = pd.to_datetime(df_filtered['Data'])
        df_filtered['Valor'] = pd.to_numeric(df_filtered['Valor'].replace(['ND', 'NULL', 'None', '', 'Não medido'], '0'), errors='coerce')
        
        # Calcular a média por data
        df_medias = df_filtered.groupby('Data')['Valor'].mean().reset_index()
        
        if df_medias.empty:
            return HttpResponse('Não há dados disponíveis para este parâmetro')
        
        # Calcular média e desvio padrão geral
        media_geral = df_filtered['Valor'].mean()
        desvio_padrao = df_filtered['Valor'].std()
        limite_superior = media_geral + desvio_padrao
        limite_inferior = media_geral - desvio_padrao
        
        # Criar gráfico com as médias
        fig = px.line(df_medias, 
                     x='Data', 
                     y='Valor',
                     title=f'Média de {parametro} ao longo do tempo',
                     markers=True)
        
        # Adicionar linhas de desvio padrão
        fig.add_hline(y=limite_superior, 
                     line_dash="dash", 
                     line_color="red", 
                     annotation_text=f"Limite Superior (DP): {limite_superior:.2f}",
                     annotation_position="top right")
        
        fig.add_hline(y=limite_inferior, 
                     line_dash="dash", 
                     line_color="red", 
                     annotation_text=f"Limite Inferior (DP): {limite_inferior:.2f}",
                     annotation_position="bottom right")
        
        fig.update_layout(
            xaxis_title='Data',
            yaxis_title=f'Média de {parametro} ({df_filtered["Unidade"].iloc[0]})',
            xaxis=dict(
                type='date',
                tickformat='%d/%m/%Y',
                tickangle=45,
                gridcolor='lightgray'
            ),
            yaxis=dict(
                gridcolor='lightgray',
                zeroline=True
            ),
            hovermode='x unified',
            width=1000,
            height=600,
            template='plotly_white'
        )
        
        fig.update_traces(
            line=dict(width=2, color='#1f77b4'),
            mode='lines+markers',
            marker=dict(size=8)
        )
        
        grafico_html = fig.to_html(
            full_html=False,
            include_plotlyjs=True,
            config={
                'displayModeBar': True,
                'responsive': True,
                'scrollZoom': True,
                'displaylogo': False
            }
        )
        
        return HttpResponse(grafico_html)
        
    except Exception as e:
        return HttpResponse(f'Erro ao gerar o gráfico: {str(e)}')

def grupos_list(request):
    grupos = GrupoPontos.objects.all().order_by('nome')
    df = load_data()
    pontos = sorted(df['Ponto'].unique())
    
    context = {
        'grupos': grupos,
        'pontos': pontos
    }
    # Ajustar o caminho do template
    return render(request, 'grupos_list.html', context)

def grupo_create(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        descricao = request.POST.get('descricao')
        pontos_selecionados = request.POST.getlist('pontos')
        
        GrupoPontos.objects.create(
            nome=nome,
            descricao=descricao,
            pontos=json.dumps(pontos_selecionados)
        )
        return redirect('resultados:dashboard_grupos')
    
    return redirect('resultados:dashboard_grupos')

def grupo_delete(request, pk):
    grupo = get_object_or_404(GrupoPontos, pk=pk)
    grupo.delete()
    return redirect('resultados:dashboard_grupos')

def dados_ausentes(request):
    df = load_data()
    
    # Criar uma máscara para identificar valores problemáticos
    mascara_valores_ausentes = (
        (df['Valor'].isna()) |  # Valores NaN
        (df['Valor'] == 'ND') |  # Valores "ND"
        (df['Valor'] == 'NULL') |  # Valores "NULL"
        (df['Valor'] == 'None') |  # Valores "None"
        (df['Valor'] == '') |  # Valores vazios
        (df['Valor'] == 'Não medido') |  # Valores "Não medido"
        (df['Valor'].astype(str).str.contains('^0*\.?0*$', na=False))  # Valores zero ou 0.0
    )
    
    # Filtrar o DataFrame usando a máscara
    df_problematicos = df[mascara_valores_ausentes].copy()
    
    # Ordenar por data, parâmetro e ponto
    df_problematicos = df_problematicos.sort_values(['Data', 'Parâmetro', 'Ponto'])
    
    # Preparar dados para o template
    dados = df_problematicos.to_dict('records')
    
    context = {
        'dados': dados,
        'total_registros': len(dados),
        'parametros': sorted(df_problematicos['Parâmetro'].unique()),
        'setores': sorted(df_problematicos['Setor'].unique()),
        'pontos': sorted(df_problematicos['Ponto'].unique())
    }
    # Ajustar o caminho do template
    return render(request, 'dados_ausentes.html', context)

def atualizar_valor(request):
    if request.method == 'POST':
        try:
            parametro = request.POST.get('parametro')
            ponto = request.POST.get('ponto')
            data = request.POST.get('data')
            novo_valor = request.POST.get('valor')
            setor = request.POST.get('setor')
            
            # Carregar o DataFrame
            df = load_data()
            
            # Converter a data para o mesmo formato do DataFrame
            data = datetime.strptime(data, '%Y-%m-%d')
            
            # Localizar e atualizar o valor
            mask = (
                (df['Parâmetro'] == parametro) & 
                (df['Ponto'] == ponto) & 
                (df['Data'] == data) &
                (df['Setor'] == setor)
            )
            
            if not df[mask].empty:
                # Atualizar o valor no DataFrame
                df.loc[mask, 'Valor'] = novo_valor
                
                # Salvar o DataFrame atualizado
                arquivo_csv = 'dados/resultados_medidas_20250218_104500.csv'
                df.to_csv(arquivo_csv, sep=';', index=False)
                
                return JsonResponse({'status': 'success'})
            
            return JsonResponse({'status': 'error', 'message': 'Registro não encontrado'})
            
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Método não permitido'})