import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime
import base64
import os
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(
    page_title="90ª Reunião Geral da FNP",
    page_icon="🏛️",
    layout="wide"
)

CSS_ESTILO = (
    "<style>"
    "[data-testid='stAppViewContainer'] { background-color: #00243d; }"
    "[data-testid='stHeader'] { background: rgba(0, 0, 0, 0); }"
    ".block-container { padding-top: 1.2rem; padding-bottom: 3rem; max-width: 1400px; }"
    ".fnp-logo-container { width: 360px; height: 120px; overflow: hidden; margin-bottom: 0.3rem; }"
    ".fnp-logo-container img { width: 1200px; max-width: none; margin-left: -20px; margin-top: -16px; display: block; }"
    ".fnp-main-title { color: #ffffff; font-size: 1.8rem; font-weight: 700; margin-top: 0.2rem; margin-bottom: 1.2rem; }"
    ".kpi-card { background-color: #ffffff; border-radius: 10px; padding: 18px 24px; display: flex; align-items: center; gap: 18px; box-shadow: 0 4px 12px rgba(0,0,0,0.25); margin-bottom: 1.5rem; }"
    ".kpi-icon-blue { background-color: #1e40af; color: #ffffff; width: 48px; height: 48px; border-radius: 50%; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }"
    ".kpi-label { font-size: 0.74rem; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px; }"
    ".kpi-number { font-size: 1.65rem; font-weight: 800; color: #0f172a; line-height: 1.1; margin: 3px 0; }"
    ".kpi-sub { font-size: 0.78rem; color: #94a3b8; }"
    "div.stButton > button[kind='secondary'] { background-color: #1a3a54; color: #ffffff; border: 1px solid rgba(255,255,255,0.18); border-radius: 8px; padding: 10px 18px; font-weight: 600; font-size: 0.95rem; }"
    "div.stButton > button[kind='secondary']:hover { background-color: #244e70; border-color: rgba(255,255,255,0.4); color: #ffffff; }"
    "div.stButton > button[kind='primary'] { background-color: #2563eb; color: #ffffff; border: 1px solid #60a5fa; border-radius: 8px; padding: 10px 18px; font-weight: 700; font-size: 0.95rem; }"
    "[data-testid='stForm'] button[kind='primary'] { background-color: #ef4444; border: 1px solid #f87171; color: #ffffff; }"
    "[data-testid='stForm'] button[kind='primary']:hover { background-color: #dc2626; border-color: #fca5a5; color: #ffffff; }"
    ".section-badge { display: inline-flex; align-items: center; gap: 8px; background-color: #1a3a54; color: #ffffff; padding: 8px 16px; border-radius: 8px; font-weight: 600; font-size: 0.95rem; margin-bottom: 14px; border: 1px solid rgba(255,255,255,0.14); }"
    ".field-header-box { background-color: #1a3a54; color: #ffffff; padding: 8px 14px; border-radius: 6px; font-size: 0.85rem; font-weight: 600; margin-bottom: 8px; }"
    ".data-value-box { background-color: #ffffff; color: #0f172a; padding: 12px 16px; border-radius: 8px; font-size: 0.98rem; font-weight: 700; min-height: 48px; display: flex; align-items: center; box-shadow: 0 2px 6px rgba(0,0,0,0.15); margin-bottom: 14px; }"
    "label[data-testid='stWidgetLabel'] p { color: #ffffff !important; font-weight: 600 !important; font-size: 0.9rem !important; }"
    "div[data-testid='stCheckbox'] label p { color: #f8fafc !important; font-weight: 400 !important; font-size: 0.88rem !important; }"
    "details[data-testid='stExpander'], div[data-testid='stExpander'] { background-color: #164266 !important; border: 1px solid rgba(255,255,255,0.35) !important; border-radius: 8px !important; margin-bottom: 10px !important; }"
    "details[data-testid='stExpander'] summary, div[data-testid='stExpander'] summary { background-color: #1e527d !important; color: #ffffff !important; border-radius: 7px !important; padding: 10px 14px !important; }"
    "details[data-testid='stExpander'] summary:hover, div[data-testid='stExpander'] summary:hover { background-color: #256396 !important; }"
    "details[data-testid='stExpander'] summary *, div[data-testid='stExpander'] summary * { color: #ffffff !important; fill: #ffffff !important; font-weight: 700 !important; font-size: 0.96rem !important; }"
    "details[data-testid='stExpander'] > div, div[data-testid='stExpander'] > div { background-color: #0e3352 !important; padding: 12px 16px !important; }"
    ".stCaption p { color: #cbd5e1 !important; }"
    "h3 { color: #ffffff !important; }"
    "hr { border-color: rgba(255,255,255,0.15) !important; }"
    "[data-testid='stForm'] { background-color: #09304f; border: 1px solid rgba(255,255,255,0.15); border-radius: 12px; padding: 20px; }"
    "</style>"
)
st.markdown(CSS_ESTILO, unsafe_allow_html=True)

PAUTAS_FNP = {
    "Fóruns Temáticos e Comissões": [
        "Fórum Nacional de Secretários Municipais de Fazenda e Finanças",
        "Fórum de Cultura das Capitais e Municípios Associados (FNC)",
        "Fórum Inova Cidades (Inovação e Transformação Digital)",
        "Fórum de Proteção de Dados Pessoais dos Municípios (LGPD)",
        "Fórum de Gestores de Limpeza Urbana e Manejo de Resíduos Sólidos",
        "Fórum Unicidades (Planejamento e Desenvolvimento Urbano)",
        "Fórum de Dirigentes Municipais de PPPs e Concessões",
        "Fórum Nacional de Procuradores-Gerais das Capitais e Grandes Cidades (FNPGC)",
        "Fórum Nacional de Gestoras Municipais de Políticas para Mulheres",
        "Fórum Nacional de Secretários e Dirigentes de Mobilidade Urbana",
        "Fórum de Inovação e Tecnologia",
        "Fórum de Cidades Inteligentes",
        "Comissão Permanente de Adaptação, Mitigação e Prevenção de Desastres – CAMP",
        "Comissão de Cidades Amazônicas – CCA",
        "Comissão Permanente de Desenvolvimento Urbano Sustentável – CDUS",
        "Comissão Permanente de Educação",
        "Comissão de Assuntos Sociais",
        "Comissão de Saúde",
        "Coalizão de Municípios pela Redução de Mortes",
        "CASD"
    ],
    "Projetos FNP": [
        "Programa Integrado de Transição Tributária para Municípios",
        "Plataforma de Governança CGIBS - Conecta IBS",
        "Programa Integrado em COSIP, PPPs e Concessões",
        "Plataforma GeoReDus - Dados geoespaciais para todos os municípios brasileiros",
        "Plataforma IFEM - Circuito de Eventos Regionais de Inteligência em Finanças Públicas Municipais",
        "Programa Piloto de Atualização Cadastral Imobiliária e Incremento de Receitas Municipais do IPTU para Regiões Metropolitanas",
        "Projeto ENMU em Ação - Mobilidade Urbana",
        "Programa Integrado de Arborização e Qualidade do Ar em 2 municípios",
        "Programa Mutirão Brasil – Radar Brasil + Cidades Amazônicas",
        "Mobilização El Niño 2026/2027",
        "Adaptação Climática nas Cidades: Planejamento urbano sensível à água (Water Wise)",
        "Estudo Tarifa Zero no Transporte Público",
        "Radar Brasil: Federalismo Climático (RADAR CHAMP)",
        "Rotas para a Autonomia Econômica das Mulheres",
        "Mobilidade Urbana: dados pela construção de políticas municipais e metropolitanas no Brasil",
        "Mais Iguais - FASE 1",
        "Mais Iguais - FASE 2",
        "SIMU: Dados de Mobilidade",
        "ODS",
        "Projeto GTFS",
        "Cidades Inovadoras",
        "Governança Federativa Metropolitana - ANO 1",
        "Embaixadores da Educação (Legado da Educação)",
        "Conexão Urbana",
        "Projeto para Idosos",
        "Projeto com Ancine",
        "Estruturas Críticas de Resposta preparadas para Desastres Climáticos",
        "Transformação Digital em cooperação Trilateral",
        "Governança em Auditorias de Saúde",
        "GeoReDUS Patrimônio Histórico e Artístico Nacional – Integração de dados do patrimônio cultural à gestão territorial, urbana e climática dos municípios"
    ],
    "Participação Ativa, Missões e Eventos": [
        "Coalizão para o Desenvolvimento Urbano Sustentável da Amazônia – DUSA (Participação Ativa)",
        "AdaptaCidades – MMA (Participação Ativa)",
        "Programa Cidades Verdes Resilientes – PCVR (Participação Ativa)",
        "Mitiga+ Brasil (Participação Ativa)",
        "Rede Ruas Completas (Participação Ativa)",
        "Imersão Técnica Internacional em Cidades Inteligentes, Inovação, Governo Digital, Educação e Desenvolvimento Urbano Sustentável – Estônia, Finlândia e Suécia (Missão)",
        "Imersão Internacional em PPPs e Concessões para Infraestrutura e Serviços Públicos – Reino Unido e França (Missão)",
        "Ciclo de Capacitações em Eletromobilidade (Evento)",
        "Elas Governam (Evento)"
    ]
}

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

COL_MUNICIPIO = df.columns[0]
COL_TERMO = df.columns[1]
COL_RANKING = df.columns[2]
COL_STATUS = df.columns[3]
COL_PARTICIPACAO = df.columns[4]

COLUNAS_PLANILHA = [
    "Data/Hora", "Tipo de Registro", "Origem", "Município/UF",
    str(COL_TERMO), str(COL_RANKING), str(COL_STATUS), str(COL_PARTICIPACAO),
    "Observação Município", "Nome", "Cargo", "Interesse / Pauta",
    "E-mail", "Telefone", "Observação Contatos"
]

@st.cache_resource
def conectar_google_sheets():
    escopos = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    credenciais = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=escopos
    )
    cliente = gspread.authorize(credenciais)
    planilha = cliente.open_by_url(st.secrets["sheet_url"])
    try:
        aba = planilha.worksheet("Cadastros_FNP")
    except gspread.WorksheetNotFound:
        aba = planilha.sheet1
    if not aba.row_values(1):
        aba.append_row(COLUNAS_PLANILHA)
    return aba

def carregar_registros_nuvem():
    try:
        aba = conectar_google_sheets()
        return aba.get_all_records()
    except Exception as e:
        st.warning(f"Não foi possível conectar ao Google Sheets no momento: {e}")
        return []

def salvar_registro_persistente(novo_registro):
    aba = conectar_google_sheets()
    linha = [str(novo_registro.get(col, "")) for col in COLUNAS_PLANILHA]
    aba.append_row(linha, value_input_option="USER_ENTERED")
    if "registros_salvos" not in st.session_state:
        st.session_state.registros_salvos = []
    st.session_state.registros_salvos.append(novo_registro)

if "registros_salvos" not in st.session_state:
    st.session_state.registros_salvos = carregar_registros_nuvem()

if os.path.exists("imagem.pdf.png"):
    with open("imagem.pdf.png", "rb") as img_file:
        b64_logo = base64.b64encode(img_file.read()).decode()
    st.markdown(f'<div class="fnp-logo-container"><img src="data:image/png;base64,{b64_logo}" alt="FNP"></div>', unsafe_allow_html=True)

col_titulo, col_botoes = st.columns([3, 1])
with col_titulo:
    st.markdown('<div class="fnp-main-title">90ª Reunião Geral da FNP</div>', unsafe_allow_html=True)
with col_botoes:
    st.write("")
    if st.button("🔄 Atualizar Base", use_container_width=True):
        st.cache_data.clear()
        st.session_state.registros_salvos = carregar_registros_nuvem()
        st.rerun()

total_inscritos = len(df)
svg_predio = '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 21h18"/><path d="M5 21V7l7-4 7 4v14"/><path d="M9 21v-6h6v6"/><path d="M9 9h.01"/><path d="M15 9h.01"/><path d="M9 12h.01"/><path d="M15 12h.01"/></svg>'

st.markdown(
    f'<div class="kpi-card"><div class="kpi-icon-blue">{svg_predio}</div><div>'
    f'<div class="kpi-label">MUNICÍPIOS INSCRITOS</div>'
    f'<div class="kpi-number">{total_inscritos}</div>'
    f'<div class="kpi-sub">Total registrado na 90ª RG (Atualizado em 20/11)</div>'
    f'</div></div>',
    unsafe_allow_html=True
)

if "modo_operacao" not in st.session_state:
    st.session_state.modo_operacao = "consulta"

col_btn1, col_btn2, _ = st.columns([1.8, 2.5, 4])

with col_btn1:
    tipo_consulta = "primary" if st.session_state.modo_operacao == "consulta" else "secondary"
    if st.button("🔍 Consulta de Município", type=tipo_consulta, use_container_width=True):
        st.session_state.modo_operacao = "consulta"
        st.rerun()

with col_btn2:
    tipo_novo = "primary" if st.session_state.modo_operacao == "novo" else "secondary"
    if st.button("➕ Cadastrar novo município (não listado)", type=tipo_novo, use_container_width=True):
        st.session_state.modo_operacao = "novo"
        st.rerun()

st.write("")

municipio_final = None
val_termo = "Não informado"
val_ranking = ""
val_status = ""
val_participacao = ""
obs_novo_municipio = ""

if st.session_state.modo_operacao == "consulta":
    st.markdown('<div class="field-header-box">Município/UF</div>', unsafe_allow_html=True)
    lista_municipios = sorted(df[COL_MUNICIPIO].astype(str).unique().tolist())

    selecao = st.selectbox(
        "Selecione o município",
        options=lista_municipios,
        index=None,
        placeholder="- Digite ou selecione o nome do município na base -",
        label_visibility="collapsed"
    )

    if selecao:
        municipio_final = selecao
        dados_mun = df[df[COL_MUNICIPIO].astype(str) == selecao].iloc[0]
        val_termo = dados_mun[COL_TERMO]
        val_ranking = dados_mun[COL_RANKING]
        val_status = dados_mun[COL_STATUS]
        val_participacao = dados_mun[COL_PARTICIPACAO]

        st.write("")
        c_termo, c_rank, c_status, c_part = st.columns([1.2, 1, 1.3, 2])

        with c_termo
