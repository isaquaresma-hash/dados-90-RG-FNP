import streamlit as st
import pandas as pd
from io import BytesIO
import base64
import os

# 1. Configuração da Página
st.set_page_config(
    page_title="90ª Reunião Geral da FNP",
    page_icon="🏛️",
    layout="wide"
)

# 2. CSS sem aspas triplas para evitar erros de colagem no GitHub
css_estilo = (
    "<style>"
    '[data-testid="stAppViewContainer"] { background-color: #00243d; }'
    '[data-testid="stHeader"] { background: rgba(0, 0, 0, 0); }'
    ".block-container { padding-top: 1.2rem; padding-bottom: 3rem; max-width: 1400px; }"
    ".fnp-logo-container { width: 360px; height: 120px; overflow: hidden; margin-bottom: 0.3rem; }"
    ".fnp-logo-container img { width: 1200px; max-width: none; margin-left: -20px; margin-top: -16px; display: block; }"
    ".fnp-main-title { color: #ffffff; font-size: 1.8rem; font-weight: 700; margin-top: 0.2rem; margin-bottom: 1.2rem; }"
    ".kpi-card { background-color: #ffffff; border-radius: 10px; padding: 18px 24px; display: flex; align-items: center; gap: 18px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25); margin-bottom: 1.5rem; }"
    ".kpi-icon-blue { background-color: #1e40af; color: #ffffff; width: 48px; height: 48px; border-radius: 50%; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }"
    ".kpi-label { font-size: 0.74rem; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px; }"
    ".kpi-number { font-size: 1.65rem; font-weight: 800; color: #0f172a; line-height: 1.1; margin: 3px 0; }"
    ".kpi-sub { font-size: 0.78rem; color: #94a3b8; }"
    'div.stButton > button[kind="secondary"] { background-color: #1a3a54; color: #ffffff; border: 1px solid rgba(255, 255, 255, 0.18); border-radius: 8px; padding: 10px 18px; font-weight: 600; font-size: 0.95rem; transition: all 0.2s ease; }'
    'div.stButton > button[kind="secondary"]:hover { background-color: #244e70; border-color: rgba(255, 255, 255, 0.4); color: #ffffff; }'
    'div.stButton > button[kind="primary"] { background-color: #2563eb; color: #ffffff; border: 1px solid #60a5fa; border-radius: 8px; padding: 10px 18px; font-weight: 700; font-size: 0.95rem; }'
    ".section-badge { display: inline-flex; align-items: center; gap: 8px; background-color: #1a3a54; color: #ffffff; padding: 8px 16px; border-radius: 8px; font-weight: 600; font-size: 0.95rem; margin-bottom: 14px; border: 1px solid rgba(255, 255, 255, 0.14); }"
    ".field-header-box { background-color: #1a3a54; color: #ffffff; padding: 8px 14px; border-radius: 6px; font-size: 0.85rem; font-weight: 600; margin-bottom: 8px; }"
    ".data-value-box { background-color: #ffffff; color: #0f172a; padding: 12px 16px; border-radius: 8px; font-size: 0.98rem; font-weight: 700; min-height: 48px; display: flex; align-items: center; box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15); margin-bottom: 14px; }"
    'label[data-testid="stWidgetLabel"] p { color: #ffffff !important; font-weight: 600 !important; font-size: 0.9rem !important; }'
    ".stCaption p { color: #cbd5e1 !important; }"
    "h3 { color: #ffffff !important; }"
    "hr { border-color: rgba(255, 255, 255, 0.15) !important; }"
    '[data-testid="stForm"] { background-color: #09304f; border: 1px solid rgba(255, 255, 255, 0.15); border-radius: 12px; padding: 20px; }'
    "</style>"
)
st.markdown(css_estilo, unsafe_allow_html=True)

# 3. Carregamento da Planilha Excel
@st.cache_data
def carregar_dados():
    df = pd.read_excel("banco de dados.xlsx", skiprows=1)
    df.columns = df.columns.astype(str).str.strip()
    df = df.dropna(how="all")
    df = df.fillna("Não informado")
    return df

try:
    df = carregar_dados()
except FileNotFoundError:
    st.error("Arquivo 'banco de dados.xlsx' não encontrado no repositório.")
    st.stop()

COL_MUNICIPIO    = df.columns[0]
COL_TERMO        = df.columns[1]
COL_RANKING      = df.columns[2]
COL_STATUS       = df.columns[3]
COL_PARTICIPACAO = df.columns[4]

# Inicialização do estado da sessão
if "modo_operacao" not in st.session_state:
    st.session_state.modo_operacao = "consulta"
if "num_contatos" not in st.session_state:
    st.session_state.num_contatos = 1
if "registros_salvos" not in st.session_state:
    st.session_state.registros_salvos = []

# 4. Cabeçalho com o Logótipo Oficial fundido ao fundo (#00243d)
if os.path.exists("imagem.pdf.png"):
    with open("imagem.pdf.png", "rb") as img_file:
        b64_logo = base64.b64encode(img_file.read()).decode()
    st.markdown(f'<div class="fnp-logo-container"><img src="data:image/png;base64,{b64_logo}" alt="FNP"></div>', unsafe_allow_html=True)

# Linha do Título + Botão Superior Direito
col_titulo, col_botoes = st.columns([3, 1])
with col_titulo:
    st.markdown('<div class="fnp-main-title">90ª Reunião Geral da FNP</div>', unsafe_allow_html=True)
with col_botoes:
    st.write("")
    if st.button("🔄 Atualizar Base", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# 5. Cartão Resumo Superior (KPI único: Municípios Inscritos)
total_inscritos = len(df)
svg_predio = '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 21h18"/><path d="M5 21V7l7-4 7 4v14"/><path d="M9 21v-6h6v6"/><path d="M9 9h.01"/><path d="M15 9h.01"/><path d="M9 12h.01"/><path d="M15 12h.01"/></svg>'

kpi_html = f'<div class="kpi-card"><div class="kpi-icon-blue">{svg_predio}</div><div><div class="kpi-label">MUNICÍPIOS INSCRITOS</div><div class="kpi-number">{total_inscritos}</div><div class="kpi-sub">Total registrado na 90ª RG (Atualizado em 20/11)</div></div></div>'
st.markdown(kpi_html, unsafe_allow_html=True)

# 6. Dois Blocos Lado a Lado: "🔍 Consulta de Município" e "➕ Cadastrar novo município (não listado)"
col_btn1, col_btn2, _ = st.columns([1
