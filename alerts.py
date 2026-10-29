import json
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from sqlalchemy import text
from config import AGRAVOS_CONFIG, resolver_chave_agravo

CONFIG_ALERTAS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config_alertas.json")
CONFIG_ALERTAS_PADRAO = {
    "doencas_monitoradas": ["FEBRE MACULOSA"],
    "email_remetente": "felipeparreiras86@gmail.com",
    "email_destinatarios": ["felipeparreiras86@gmail.com"],
}

def carregar_config_alertas():
    if not os.path.exists(CONFIG_ALERTAS_PATH):
        salvar_config_alertas(CONFIG_ALERTAS_PADRAO)
        return dict(CONFIG_ALERTAS_PADRAO)
    try:
        with open(CONFIG_ALERTAS_PATH, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        for chave, valor_padrao in CONFIG_ALERTAS_PADRAO.items():
            cfg.setdefault(chave, valor_padrao)
        return cfg
    except Exception:
        return dict(CONFIG_ALERTAS_PADRAO)

def salvar_config_alertas(config):
    with open(CONFIG_ALERTAS_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

def contar_casos_confirmados(engine, agravo_nome, anos=None):
    chave = resolver_chave_agravo(agravo_nome)
    if chave not in AGRAVOS_CONFIG: return None
    
    query = f"SELECT COUNT(*) FROM {AGRAVOS_CONFIG[chave]['tabela']} WHERE classificacao != 'Suspeita/Exame'"
    if anos: query += f" AND ano IN ({','.join(map(str, anos))})"
    try:
        with engine.connect() as conn:
            return int(conn.execute(text(query)).scalar() or 0)
    except Exception:
        return None

def enviar_email_alerta(remetente, senha_app, destinatarios, aumentos):
    if not aumentos: return False, "Nenhum aumento detectado; nenhum e-mail foi enviado."
    if not destinatarios: return False, "Nenhum destinatário configurado para o alerta."
    if not remetente or not senha_app: return False, "E-mail remetente ou senha de app não configurados."

    linhas = [f"- {a['doenca']}: {a['antes']} -> {a['depois']} casos confirmados (+{a['depois'] - a['antes']})" for a in aumentos]
    corpo = "Alerta automático do Portal de Vigilância Epidemiológica.\n\nAs seguintes doenças apresentaram AUMENTO:\n\n" + "\n".join(linhas)
    
    msg = MIMEMultipart()
    msg['From'] = remetente
    msg['To'] = ", ".join(destinatarios)
    msg['Subject'] = f"[ALERTA] Aumento de casos: {', '.join(a['doenca'] for a in aumentos)}"
    msg.attach(MIMEText(corpo, 'plain', 'utf-8'))

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as servidor:
            servidor.starttls()
            servidor.login(remetente, senha_app)
            servidor.sendmail(remetente, destinatarios, msg.as_string())
        return True, f"E-mail enviado para: {', '.join(destinatarios)}."
    except Exception as e:
        return False, f"Falha ao enviar e-mail: {e}"