import unicodedata

AGRAVOS_CONFIG = {
    "DENGUE": {
        "tabela": "mv_dengue",
        "cids": "f.ds_filtro_cids ~ '(^|\\|)A90($|\\|)' OR f.ds_filtro_cids ~ '(^|\\|)A91($|\\|)'",
        "cids_transacional": "c.nu_cid10 LIKE 'A90%%' OR c.nu_cid10 LIKE 'A91%%'",
        "proced": "'0202030764', '0202030772'",
        "busca": "dengue",
        "classificacao_sql": "CASE WHEN ds_filtro_cids LIKE '%%A91%%' THEN 'Dengue Grave' ELSE 'Dengue Clássica' END"
    },
    "COVID": {
        "tabela": "mv_covid",
        "cids": "(f.ds_filtro_cids ~ '(^|\\|)(U071|U072|B342|J11|J111|J069|U09|U099|U10|U109)($|\\|)' OR f.ds_filtro_ciaps ~ '(^|\\|)(R99|A77|R83)($|\\|)')",
        "cids_transacional": "(c.nu_cid10 LIKE 'U071%%' OR c.nu_cid10 LIKE 'U072%%' OR c.nu_cid10 LIKE 'B342%%' OR c.nu_cid10 LIKE 'J11%%' OR c.nu_cid10 LIKE 'J069%%' OR c.nu_cid10 LIKE 'U09%%' OR c.nu_cid10 LIKE 'U10%%')",
        "proced": "'0202031442', '0202031469'",
        "busca": "covid|sars-cov",
        "classificacao_sql": """
            CASE 
                WHEN ds_filtro_cids LIKE '%%U071%%' THEN 'COVID-19 Confirmado Lab (U07.1)' 
                WHEN ds_filtro_cids LIKE '%%U072%%' THEN 'COVID-19 Clínico/Epidemiol. (U07.2)' 
                WHEN ds_filtro_cids LIKE '%%U09%%' OR ds_filtro_cids LIKE '%%U10%%' THEN 'Pós-COVID / SIM (U09/U10)' 
                WHEN ds_filtro_cids LIKE '%%B342%%' THEN 'Coronavírus NE (B34.2)' 
                WHEN ds_filtro_cids LIKE '%%J11%%' OR ds_filtro_cids LIKE '%%J069%%' THEN 'Síndrome Gripal / IVAS' 
                WHEN ds_filtro_ciaps LIKE '%%R99%%' OR ds_filtro_ciaps LIKE '%%A77%%' OR ds_filtro_ciaps LIKE '%%R83%%' THEN 'Suspeita CIAP-2 (Viral/Resp.)' 
                ELSE 'COVID-19 (Outros)' 
            END
        """
    },
    "FEBRE_MACULOSA": {
        "tabela": "mv_febre",
        "cids": "f.ds_filtro_cids ~ '(^|\\|)A770($|\\|)'",
        "proced": "'0202030918'",
        "busca": "maculosa|rickettsia",
        "classificacao_sql": "'Febre Maculosa'"
    },
    "HEPATITES": {
        "tabela": "mv_hepatites",
        "cids": "f.ds_filtro_cids ~ '(^|\\|)B1[5-9]($|\\|)'",
        "proced": "'0202030632', '0202030373', '0202030640'",
        "busca": "hepatite",
        "classificacao_sql": "CASE WHEN ds_filtro_cids LIKE '%%B15%%' THEN 'Hepatite A' WHEN ds_filtro_cids LIKE '%%B16%%' OR ds_filtro_cids LIKE '%%B180%%' THEN 'Hepatite B' WHEN ds_filtro_cids LIKE '%%B171%%' OR ds_filtro_cids LIKE '%%B182%%' THEN 'Hepatite C' ELSE 'Hepatite (Outras)' END"
    },
    "HIV_AIDS": {
        "tabela": "mv_hiv",
        "cids": "f.ds_filtro_cids ~ '(^|\\|)B2[0-4]($|\\|)' OR f.ds_filtro_cids ~ '(^|\\|)Z21($|\\|)'",
        "proced": "'0202030306', '0214010040'",
        "busca": "hiv|aids",
        "classificacao_sql": "CASE WHEN ds_filtro_cids LIKE '%%Z21%%' THEN 'HIV Positivo (Assintomático)' ELSE 'AIDS (Doença pelo HIV)' END"
    },
    "INTOXICACAO_EXOGENA": {
        "tabela": "mv_intox",
        "cids": "f.ds_filtro_cids ~ '(^|\\|)T[3-6][0-9]($|\\|)' OR f.ds_filtro_cids ~ '(^|\\|)X4[0-9]($|\\|)'",
        "proced": "''",
        "busca": "intoxicacao|envenenamento",
        "classificacao_sql": "'Intoxicação Exógena'"
    },
    "MONKEYPOX": {
        "tabela": "mv_monkeypox",
        "cids": "f.ds_filtro_cids ~ '(^|\\|)B04($|\\|)'",
        "proced": "''",
        "busca": "monkeypox|mpox",
        "classificacao_sql": "'Monkeypox - Mpox'"
    },
    "SIFILIS": {
        "tabela": "mv_sifilis",
        "cids": "f.ds_filtro_cids ~ '(^|\\|)A5[0-3]($|\\|)'",
        "proced": "'0202031175', '0202030586'",
        "busca": "sifilis|vdrl",
        "classificacao_sql": "CASE WHEN ds_filtro_cids LIKE '%%A50%%' THEN 'Sífilis Congênita' ELSE 'Sífilis Adquirida' END"
    },
    "TUBERCULOSE": {
        "tabela": "mv_tuberculose",
        "cids": "f.ds_filtro_cids ~ '(^|\\|)(A16|A160|A161|A162|A163|A165|A167|A168|A169|A178|A179|A18|A180|A182|A183|A184|A185|A188|A19|A192|A198|A199)($|\\|)'",
        "cids_transacional": "c.nu_cid10 LIKE 'A16%%' OR c.nu_cid10 LIKE 'A17%%' OR c.nu_cid10 LIKE 'A18%%' OR c.nu_cid10 LIKE 'A19%%'",
        "proced": "'0202030047', '0202080060'",
        "busca": "tuberculose|baaf",
        "classificacao_sql": "CASE WHEN ds_filtro_cids LIKE '%%A16%%' THEN 'Tuberculose Respiratória (A16)' WHEN ds_filtro_cids LIKE '%%A18%%' THEN 'Tuberculose de Outros Órgãos (A18)' WHEN ds_filtro_cids LIKE '%%A19%%' THEN 'Tuberculose Miliar (A19)' ELSE 'Tuberculose (Outras)' END"
    },
    "VIOLENCIA": {
        "tabela": "mv_violencia",
        "cids": "f.ds_filtro_cids ~ '(^|\\|)X8[5-9]($|\\|)' OR f.ds_filtro_cids ~ '(^|\\|)X9[0-9]($|\\|)' OR f.ds_filtro_cids ~ '(^|\\|)Y0[0-9]($|\\|)'",
        "proced": "''",
        "busca": "violencia|agressao",
        "classificacao_sql": "'Violência/Agressão'"
    },
    "ANIMAIS_PECONHENTOS": {
        "tabela": "mv_peconhentos",
        "cids": "f.ds_filtro_cids ~ '(^|\\|)X2[0-9]($|\\|)'",
        "proced": "''",
        "busca": "escorpiao|cobra|aranha|peconhento",
        "classificacao_sql": "'Acidente c/ Animal Peçonhento'"
    },
    "TRANSITO": {
        "tabela": "mv_transito",
        "cids": "f.ds_filtro_cids ~ '(^|\\|)V[0-9]($|\\|)'",
        "proced": "''",
        "busca": "acidente de transito|atropelamento|colisao",
        "classificacao_sql": "'Acidente de Trânsito'"
    }
}

AGRAVO_DISPLAY_TO_KEY = {
    "DENGUE": "DENGUE",
    "COVID": "COVID",
    "FEBRE MACULOSA": "FEBRE_MACULOSA",
    "HEPATITES": "HEPATITES",
    "HIV/AIDS": "HIV_AIDS",
    "INTOXICAÇÃO EXÓGENA": "INTOXICACAO_EXOGENA",
    "MONKEYPOX - MPOX": "MONKEYPOX",
    "SÍFILIS": "SIFILIS",
    "TUBERCULOSE": "TUBERCULOSE",
    "VIOLÊNCIA": "VIOLENCIA",
    "ANIMAIS PEÇONHENTOS": "ANIMAIS_PECONHENTOS",
    "ACIDENTES DE TRÂNSITO": "TRANSITO",
}

def resolver_chave_agravo(agravo_nome):
    if agravo_nome in AGRAVO_DISPLAY_TO_KEY:
        return AGRAVO_DISPLAY_TO_KEY[agravo_nome]
    texto = unicodedata.normalize('NFKD', agravo_nome).encode('ASCII', 'ignore').decode('ASCII')
    texto = texto.replace("-", " ").replace("/", " ")
    return "_".join(texto.upper().split())