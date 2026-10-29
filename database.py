from sqlalchemy import create_engine, text
from config import AGRAVOS_CONFIG


engine = create_engine("postgresql://postgres:senhabd@localhost:5432/nomebd")

def criar_sql_view(nome_view, config):
    return f"""
    CREATE MATERIALIZED VIEW IF NOT EXISTS {nome_view} AS
    WITH consolidado AS (
        SELECT 
            f.dt_inicial_atendimento::date AS data,
            u.no_unidade_saude AS nome_unidade,
            f.nu_cpf_cidadao AS cpf,
            f.co_dim_sexo,
            f.dt_nascimento,
            f.ds_filtro_cids,
            f.ds_filtro_ciaps,
            f.st_encaminhamento_urgencia AS hospitalizacao,
            f.nu_temperatura AS temperatura
        FROM tb_fat_atendimento_individual f
        LEFT JOIN tb_dim_unidade_saude u ON f.co_dim_unidade_saude_1 = u.co_seq_dim_unidade_saude
        WHERE {config['cids']}
        UNION ALL
        SELECT 
            f_pai.dt_inicial_atendimento::date AS data,
            u.no_unidade_saude AS nome_unidade,
            p.nu_cpf_cidadao AS cpf,
            f_pai.co_dim_sexo,
            f_pai.dt_nascimento,
            f_pai.ds_filtro_cids,
            f_pai.ds_filtro_ciaps,
            0 AS hospitalizacao,
            NULL AS temperatura
        FROM tb_fat_atd_ind_problemas p
        JOIN tb_fat_atendimento_individual f_pai ON p.co_fat_atd_ind = f_pai.co_seq_fat_atd_ind
        LEFT JOIN tb_dim_unidade_saude u ON f_pai.co_dim_unidade_saude_1 = u.co_seq_dim_unidade_saude
        WHERE {config['cids'].replace('f.', 'f_pai.')}
        UNION ALL
        SELECT 
            pr.dt_inicial_atendimento::date AS data,
            u.no_unidade_saude AS nome_unidade,
            pr.nu_cpf_cidadao AS cpf,
            pr.co_dim_sexo,
            pr.dt_nascimento,
            'Suspeita/Exame' AS ds_filtro_cids,
            NULL AS ds_filtro_ciaps,
            0 AS hospitalizacao,
            pr.nu_temperatura AS temperatura
        FROM tb_fat_proced_atend pr
        LEFT JOIN tb_dim_unidade_saude u ON pr.co_dim_unidade_saude = u.co_seq_dim_unidade_saude
        WHERE pr.ds_filtro_procedimento ~* '{config['busca']}'
           OR pr.co_fat_procedimento IN (
               SELECT co_seq_dim_procedimento FROM tb_dim_procedimento 
               WHERE co_proced IN ({config['proced']})
           )
    )
    SELECT 
        *, 
        EXTRACT(YEAR FROM data)::int AS ano,
        CASE WHEN co_dim_sexo = 1 THEN 'Masculino' ELSE 'Feminino' END AS sexo,
        CASE 
            WHEN ds_filtro_cids = 'Suspeita/Exame' THEN 'Suspeita/Exame'
            ELSE ({config['classificacao_sql']})
        END AS classificacao,
        CASE 
            WHEN EXTRACT(YEAR FROM age(data, dt_nascimento)) < 1 THEN '00 a <1'
            WHEN EXTRACT(YEAR FROM age(data, dt_nascimento)) BETWEEN 1 AND 4 THEN '01 a 04'
            WHEN EXTRACT(YEAR FROM age(data, dt_nascimento)) BETWEEN 5 AND 9 THEN '05 a 09'
            WHEN EXTRACT(YEAR FROM age(data, dt_nascimento)) BETWEEN 10 AND 14 THEN '10 a 14'
            WHEN EXTRACT(YEAR FROM age(data, dt_nascimento)) BETWEEN 15 AND 19 THEN '15 a 19'
            WHEN EXTRACT(YEAR FROM age(data, dt_nascimento)) BETWEEN 20 AND 29 THEN '20 a 29'
            WHEN EXTRACT(YEAR FROM age(data, dt_nascimento)) BETWEEN 30 AND 39 THEN '30 a 39'
            WHEN EXTRACT(YEAR FROM age(data, dt_nascimento)) BETWEEN 40 AND 49 THEN '40 a 49'
            WHEN EXTRACT(YEAR FROM age(data, dt_nascimento)) BETWEEN 50 AND 59 THEN '50 a 59'
            ELSE '60 anos ou mais'
        END AS faixa_etaria
    FROM consolidado;
    """

def criar_view_sintomas_reais(nome_view_base, config):
    nome_view_sintomas = f"{nome_view_base}_sintomas"
    filtro_cid = config.get('cids_transacional', "1=2")
    return f"""
    CREATE MATERIALIZED VIEW IF NOT EXISTS {nome_view_sintomas} AS
    WITH AtendimentosAlvo AS (
        SELECT DISTINCT rel.co_atend_prof
        FROM rl_evolucao_avaliacao_ciap_cid rel
        JOIN tb_cid10 c ON rel.co_cid10 = c.co_cid10
        WHERE {filtro_cid}
    )
    SELECT 
        a.co_seq_atend_prof AS id_atendimento,
        a.dt_inicio::date AS data,
        EXTRACT(YEAR FROM a.dt_inicio)::int AS ano,
        ciap.co_ciap AS codigo_ciap,
        ciap.ds_ciap AS nome_sintoma
    FROM tb_atend_prof a
    JOIN AtendimentosAlvo alvo ON a.co_seq_atend_prof = alvo.co_atend_prof
    JOIN rl_evolucao_avaliacao_ciap_cid rel ON a.co_seq_atend_prof = rel.co_atend_prof
    JOIN tb_ciap ciap ON rel.co_ciap = ciap.co_seq_ciap;
    """

def criar_view_exames_reais(nome_view_base, config):
    nome_view_exames = f"{nome_view_base}_exames"
    filtro_cid = config['cids']  
    filtro_proced = config.get('proced') or "''"
    return f"""
    CREATE MATERIALIZED VIEW IF NOT EXISTS {nome_view_exames} AS
    SELECT 
        e.co_fat_atd_ind AS id_atendimento,
        e.dt_solicitacao::date AS data_solicitacao,
        e.dt_realizacao::date AS data_realizacao,
        e.dt_resultado::date AS data_resultado,
        EXTRACT(YEAR FROM e.dt_solicitacao)::int AS ano,
        p.co_proced AS codigo_sigtap,
        p.ds_proced AS nome_exame,
        e.nu_resultado_valor AS resultado_exame
    FROM tb_fat_atd_ind_exames e
    JOIN tb_fat_atendimento_individual f ON e.co_fat_atd_ind = f.co_seq_fat_atd_ind
    LEFT JOIN tb_dim_procedimento p ON e.co_dim_procedimento = p.co_seq_dim_procedimento
    WHERE ({filtro_cid} OR p.co_proced IN ({filtro_proced}));
    """

def inicializar_todas_as_views(engine_conn):
    with engine_conn.connect() as conn:
        for agravo, cfg in AGRAVOS_CONFIG.items():
            nome_view = cfg['tabela']
            conn.execute(text(f"DROP MATERIALIZED VIEW IF EXISTS {nome_view} CASCADE;"))
            conn.execute(text(criar_sql_view(nome_view, cfg)))
            conn.execute(text(f"CREATE INDEX IF NOT EXISTS idx_{nome_view}_ano ON {nome_view} (ano);"))
            
            conn.execute(text(f"DROP MATERIALIZED VIEW IF EXISTS {nome_view}_exames CASCADE;"))
            conn.execute(text(criar_view_exames_reais(nome_view, cfg)))
            conn.execute(text(f"CREATE INDEX IF NOT EXISTS idx_{nome_view}_exam_ano ON {nome_view}_exames (ano);"))

            if 'cids_transacional' in cfg:
                conn.execute(text(f"DROP MATERIALIZED VIEW IF EXISTS {nome_view}_sintomas CASCADE;"))
                conn.execute(text(criar_view_sintomas_reais(nome_view, cfg)))
                conn.execute(text(f"CREATE INDEX IF NOT EXISTS idx_{nome_view}_sint_ano ON {nome_view}_sintomas (ano);"))
        conn.commit()

def views_existem(engine_conn):
    query = "SELECT count(*) FROM pg_matviews WHERE matviewname IN ('mv_dengue', 'mv_covid', 'mv_febre', 'mv_transito')"
    with engine_conn.connect() as conn:
        return conn.execute(text(query)).scalar() == 4