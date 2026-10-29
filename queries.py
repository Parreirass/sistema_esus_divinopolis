import pandas as pd
import time
from sqlalchemy import text
from config import AGRAVOS_CONFIG, resolver_chave_agravo

def query_com_timer(query_name, sql_query, engine):
    inicio = time.time()
    df = pd.read_sql(text(sql_query), engine)
    return df, round(time.time() - inicio, 2)

def get_dados_agravo(engine, agravo_nome, anos=None):
    chave = resolver_chave_agravo(agravo_nome)
    colunas_esperadas = ['data', 'ano', 'nome_unidade', 'cpf', 'sexo', 'faixa_etaria', 'classificacao', 'hospitalizacao', 'temperatura', 'ds_filtro_ciaps']
    
    if chave not in AGRAVOS_CONFIG:
        return pd.DataFrame(columns=colunas_esperadas), 0
    
    tabela = AGRAVOS_CONFIG[chave]['tabela']
    query = f"SELECT * FROM {tabela}"
    if anos: query += f" WHERE ano IN ({','.join(map(str, anos))})"
    
    try:
        df, tempo = query_com_timer("Agravo", query, engine)
        return df if not df.empty else pd.DataFrame(columns=colunas_esperadas), tempo
    except Exception:
        return pd.DataFrame(columns=colunas_esperadas), 0

def get_resumo_unidades_completo(engine, tabela_nome, anos=None):
    filtro_ano = f"WHERE ano IN ({','.join(map(str, anos))})" if anos else ""
    sql = f"""
    SELECT u.no_unidade_saude AS "Unidade", u.no_bairro AS "Bairro", COUNT(m.cpf) AS "Casos"
    FROM tb_dim_unidade_saude u
    LEFT JOIN (SELECT nome_unidade, cpf FROM {tabela_nome} {filtro_ano}) m ON u.no_unidade_saude = m.nome_unidade
    WHERE u.st_registro_valido = 1
    GROUP BY u.no_unidade_saude, u.no_bairro ORDER BY "Casos" DESC;
    """
    return query_com_timer("Resumo Unidades", sql, engine)

def get_resumo_bairros(engine, tabela_nome, anos=None):
    filtro_ano = f"AND ano IN ({','.join(map(str, anos))})" if anos else ""
    sql = f"""
    SELECT u.no_bairro AS "Bairro", COUNT(m.cpf) AS "Confirmados"
    FROM tb_dim_unidade_saude u
    JOIN {tabela_nome} m ON u.no_unidade_saude = m.nome_unidade
    WHERE u.st_registro_valido = 1 AND u.no_bairro IS NOT NULL {filtro_ano}
    GROUP BY u.no_bairro ORDER BY "Confirmados" DESC;
    """
    return query_com_timer("Resumo Bairros", sql, engine)

def get_sintomas_reais(engine, agravo_nome, anos=None):
    colunas_esperadas = ['id_atendimento', 'data', 'ano', 'codigo_ciap', 'nome_sintoma']
    chave = resolver_chave_agravo(agravo_nome)
    if chave not in AGRAVOS_CONFIG: return pd.DataFrame(columns=colunas_esperadas)
    
    query = f"SELECT * FROM {AGRAVOS_CONFIG[chave]['tabela']}_sintomas"
    if anos: query += f" WHERE ano IN ({','.join(map(str, anos))})"
    try: return pd.read_sql(text(query), engine)
    except Exception: return pd.DataFrame(columns=colunas_esperadas)

def get_exames_reais(engine, agravo_nome, anos=None):
    colunas_esperadas = ['data_solicitacao', 'ano', 'cid_motivo', 'co_proced', 'resultado_exame', 'data_resultado']
    chave = resolver_chave_agravo(agravo_nome)
    if chave not in AGRAVOS_CONFIG: return pd.DataFrame(columns=colunas_esperadas)
    
    query = f"SELECT * FROM {AGRAVOS_CONFIG[chave]['tabela']}_exames"
    if anos: query += f" WHERE ano IN ({','.join(map(str, anos))})"
    try: return pd.read_sql(text(query), engine)
    except Exception: return pd.DataFrame(columns=colunas_esperadas)