import streamlit as st
import pandas as pd

def aplicar_estilo_css():
    st.markdown("""
        <style>
        .main { background-color: #fdf5e6; }
        [data-testid="stMetric"] { background-color: #ffffff; border: 2px solid #800000; border-radius: 8px; }
        div.stButton > button { background-color: #ff4b11; color: white; border: none; }
        </style>
    """, unsafe_allow_html=True)

@st.dialog("Detalhes da Ocorrência")
def modal_detalhes_ocorrencia(registro):
    st.markdown("### 📋 Informações Clínicas e Demográficas")
    c1, c2 = st.columns(2)
    with c1:
        st.write(f"**📅 Data:** {registro.get('data', 'N/A')}")
        st.write(f"**🏥 Unidade:** {registro.get('nome_unidade', 'N/A')}")
        st.write(f"**🩺 Classificação:** {registro.get('classificacao', 'N/A')}")
    with c2:
        st.write(f"**👤 Sexo:** {registro.get('sexo', 'N/A')}")
        st.write(f"**🎂 Idade:** {registro.get('faixa_etaria', 'N/A')}")
        if 'cpf' in registro and pd.notna(registro['cpf']):
            cpf_str = str(registro['cpf']).replace(".0", "").zfill(11)
            st.write(f"**🔑 CPF:** ***.{cpf_str[3:6]}.{cpf_str[6:9]}-**")
            
    st.divider()
    if 'hospitalizacao' in registro and registro['hospitalizacao'] == 1:
        st.error("🚨 Indicação de internação/encaminhamento de urgência.")
    if 'temperatura' in registro and pd.notna(registro['temperatura']):
        temp = float(registro['temperatura'])
        if temp > 37.8: st.warning(f"🌡️ **Atenção:** Febril ({temp} °C)")
        else: st.info(f"🌡️ Temperatura: {temp} °C")