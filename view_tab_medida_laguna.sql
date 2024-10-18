-- Passo 1: Criação da view intermediária sem a conversão para texto
CREATE OR REPLACE VIEW view_intermediaria AS
SELECT 
    tab_campanha.nome AS Campanha, 
    tab_coleta.data AS Data, 
    tab_setor.nome AS Setor,
    tab_ponto.nome AS Ponto, 
    tab_ponto.lat AS Lat, 
    tab_ponto.lon AS Lon, 
    tab_prodxparam.unidade AS Unidade, 
    tab_param.nome AS Parametro, 
    tab_produto.nome AS Produto, 
    tab_serie_classificacao.nome AS Serie, 
    tab_frasco.nome AS Frasco, 
    tab_medida.input_valor AS Valor, -- Mantém a coluna original como double precision
    tab_ponto.observacao AS Observacao, 
    CONCAT(tab_param.nome, '_', tab_produto.nome, '_', tab_serie_classificacao.nome) AS param_prod_serie
FROM 
    tab_campanha
JOIN 
    tab_coleta ON tab_campanha.id = tab_coleta.id_campanha
JOIN 
    tab_amostra ON tab_coleta.id = tab_amostra.id_coleta
JOIN 
    tab_ponto ON tab_amostra.id_ponto = tab_ponto.id
JOIN 
    tab_setor ON tab_ponto.id_setor = tab_setor.id
JOIN 
    tab_envio ON tab_amostra.id = tab_envio.id_amostra
JOIN 
    tab_medida ON tab_envio.id = tab_medida.id_envio
JOIN 
    tab_prodxparam ON tab_medida.id_pp = tab_prodxparam.id
JOIN 
    tab_param ON tab_prodxparam.id_param = tab_param.id
JOIN 
    tab_produto ON tab_prodxparam.id_produto = tab_produto.id
JOIN 
    tab_serie_classificacao ON tab_prodxparam.id_serie = tab_serie_classificacao.id
JOIN 
    tab_frasco ON tab_prodxparam.id_frasco = tab_frasco.id;

-- Passo 2: Criação da view com a nova coluna concatenada e a observação usando a view intermediária
CREATE OR REPLACE VIEW view_com_nova_coluna AS
SELECT 
    Campanha, 
    Setor,
    Data, 
    Ponto, 
    Lat, 
    Lon, 
    Unidade, 
    Parametro, 
    Produto, 
    Serie, 
    Frasco, 
    Valor, 
    Observacao, 
    param_prod_serie
FROM 
    view_intermediaria;

-- Passo 3: Construção da consulta dinâmica para a view pivotada
DO $$
DECLARE
    sql TEXT;
    cols TEXT;
BEGIN
    -- Obter os valores únicos de param_prod_serie e construir a lista de colunas
    SELECT STRING_AGG('MAX(CASE WHEN param_prod_serie = ''' || param_prod_serie || ''' THEN Valor END) AS "' || param_prod_serie || '"', ', ')
    INTO cols
    FROM (SELECT DISTINCT param_prod_serie FROM view_com_nova_coluna) AS param_prod_serie_list;

    -- Construir a consulta final
    sql := 'CREATE OR REPLACE VIEW tab_medida_pivotada AS
            SELECT 
                Campanha, 
                Setor,
                Ponto, 
                ' || cols || '
            FROM view_com_nova_coluna
            GROUP BY Campanha, Setor, Ponto
            ORDER BY Campanha, Setor, Ponto'; 

    -- Executar a consulta
    EXECUTE sql;
END $$;


-- nao usar: 

-- DROP VIEW tab_medida_pivotada; 

-- DROP VIEW view_com_nova_coluna;

-- DROP VIEW view_intermediaria;