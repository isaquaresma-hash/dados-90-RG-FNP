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

# 2. CSS com a cor exata do fundo da imagem (#00243d) e enquadramento limpo do logótipo
st.markdown("""
<style>
    /* Fundo azul-marinho exato de imagem.pdf.png para fundir o logótipo sem bordas */
    [data-testid="stAppViewContainer"] {
        background-color: #00243d;
    }
    [data-testid="stHeader"] {
        background: rgba(0, 0, 0, 0);
    }
    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 3rem;
        max-width: 1400px;
    }

    /* Enquadramento do logótipo sem excesso de margem azul */
    .fnp-logo-container {
        width: 360px;
        height: 120px;
        overflow: hidden;
        margin-bottom: 0.3rem;
    }
    .fnp-logo-container img {
        width: 1200px;
        max-width: none;
        margin-left: -20px;
        margin-top: -16px;
        display: block;
    }

    /* Título principal branco */
    .fnp-main-title {
        color: #ffffff;
        font-size: 1.8rem;
        font-weight: 700;
        margin-top: 0.2rem;
        margin-bottom: 1.2rem;
    }

    /* Cartão de resumo superior (KPI) */
    .kpi-card {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 18px 24px;
        display: flex;
        align-items: center;
        gap: 18px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
        margin-bottom: 1.5rem;
    }
    .kpi-icon-blue {
        background-color: #1e40af;
        color: #ffffff;
        width: 48px;
        height: 48px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
    }
    .kpi-label {
        font-size: 0.74rem;
        font-weight: 700;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .kpi-number {
        font-size: 1.65rem;
        font-weight: 800;
        color: #0f172a;
        line-height: 1.1;
        margin: 3px 0;
    }
    .kpi-sub {
        font-size: 0.78rem;
        color: #94a3b8;
    }

    /* Badge de seção */
    .section-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background-color: #1a3a54;
        color: #ffffff;
        padding: 8px 16px;
        border-radius: 8px;
        font-weight: 600;
        font-size: 0.95rem;
        margin-bottom: 14px;
        border: 1px solid rgba(255, 255, 255, 0.14);
    }

    /* Cabeçalho escuro acima dos campos/cartões */
    .field-header-box {
        background-color: #1a3a54;
        color: #ffffff;
        padding: 8px 14px;
        border-radius: 6px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-bottom: 8px;
    }

    /* Caixa branca arredondada de resultado */
    .data-value-box {
        background-color: #ffffff;
        color: #0f172a;
        padding: 12px 16px;
        border-radius: 8px;
        font-size: 0.98rem;
        font-weight: 700;
        min-height: 48px;
        display: flex;
        align-items: center;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
        margin-bottom: 14px;
    }

    /* Ajuste de rótulos dos inputs do Streamlit */
    label[data-testid="stWidgetLabel"] p {
        color: #ffffff !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
    }
    .stCaption p {
        color: #cbd5e1 !important;
    }
    h3 {
        color: #ffffff !important;
    }
    hr {
        border-color: rgba(255, 255, 255, 0.15) !important;
    }

    /* Estilização do formulário */
    [data-testid="stForm"] {
        background-color: #09304f;
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 12px;
        padding: 20px;
    }
</style>
""", unsafe_allow_html=True)

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

COL_MUNICIPIO    = df.columns[0]  # Município/UF
COL_TERMO        = df.columns[1]  # Requer assinatura do termo...
COL_RANKING      = df.columns[2]  # Ranking
COL_STATUS       = df.columns[3]  # Status
COL_PARTICIPACAO = df.columns[4]  # Participação

# 4. Cabeçalho com o Logótipo Oficial fundido ao fundo (#00243d)
if os.path.exists("imagem.pdf.png"):
    with open("imagem.pdf.png", "rb") as img_file:
        b64_logo = base64.b64encode(img_file.read()).decode()
    st.markdown(f"""
    <div class="fnp-logo-container">
        <img src="data:image/png;base64,{b64_logo}" alt="FNP - Frente Nacional de Prefeitas e Prefeitos">
    </div>
    """, unsafe_allow_html=True)

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

svg_predio = """
<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M3 21h18"/><path d="M5 21V7l7-4 7 4v14"/><path d="M9 21v-6h6v6"/><path d="M9 9h.01"/><path d="M15 9h.01"/><path d="M9 12h.01"/><path d="M15 12h.01"/>
</svg>
"""

st.markdown(f"""
<div class="kpi-card">
    <div class="kpi-icon-blue">{svg_predio}</div>
    <div>
        <div class="kpi-label">MUNICÍPIOS INSCRITOS</div>
        <div class="kpi-number">{total_inscritos}</div>
        <div class="kpi-sub">Total registrado na 90ª RG (Atualizado em 20/11)</div>
    </div>
</div>
""", unsafe_allow_html=True)

# 6. Seção de Consulta
st.markdown('<div class="section-badge">🔍 Consulta de Município</div>', unsafe_allow_html=True)

st.markdown('<div class="field-header-box">Município/UF</div>', unsafe_allow_html=True)
lista_municipios = sorted(df[COL_MUNICIPIO].astype(str).unique().tolist())

municipio_selecionado = st.selectbox(
    "Selecione o município",
    options=lista_municipios,
    index=None,
    placeholder="- Digite ou selecione o nome do município -",
    label_visibility="collapsed"
)

# 7. Exibição dos 4 Dados do Banco e Formulário após a Seleção
if municipio_selecionado:
    dados_mun = df[df[COL_MUNICIPIO].astype(str) == municipio_selecionado].iloc[0]

    st.write("")
    c_termo, c_rank, c_status, c_part = st.columns([1.2, 1, 1.3, 2])

    with c_termo:
        st.markdown(f'<div class="field-header-box">{COL_TERMO}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="data-value-box">{dados_mun[COL_TERMO]}</div>', unsafe_allow_html=True)

    with c_rank:
        st.markdown(f'<div class="field-header-box">{COL_RANKING}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="data-value-box">{dados_mun[COL_RANKING]}</div>', unsafe_allow_html=True)

    with c_status:
        st.markdown(f'<div class="field-header-box">{COL_STATUS}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="data-value-box">{dados_mun[COL_STATUS]}</div>', unsafe_allow_html=True)

    with c_part:
        st.markdown(f'<div class="field-header-box">{COL_PARTICIPACAO}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="data-value-box">{dados_mun[COL_PARTICIPACAO]}</div>', unsafe_allow_html=True)

    st.markdown("---")

    # 8. Controle de Múltiplos Contatos
    if "num_contatos" not in st.session_state:
        st.session_state.num_contatos = 1
    if "registros_salvos" not in st.session_state:
        st.session_state.registros_salvos = []

    if st.session_state.get("ultimo_municipio") != municipio_selecionado:
        st.session_state.num_contatos = 1
        st.session_state.ultimo_municipio = municipio_selecionado

    st.markdown('<div class="section-badge">📝 Cadastro de Contatos / Representantes</div>', unsafe_allow_html=True)
    st.caption("Preencha os dados abaixo. Clique em '+ Adicionar outro contato' para incluir mais representantes deste município.")

    col_add, col_rem, _ = st.columns([1.6, 1.6, 5])
    with col_add:
        if st.button("➕ Adicionar outro contato", use_container_width=True):
            st.session_state.num_contatos += 1
            st.rerun()
    with col_rem:
        if st.session_state.num_contatos > 1:
            if st.button("➖ Remover último", use_container_width=True):
                st.session_state.num_contatos -= 1
                st.rerun()

    with st.form("form_contatos_fnp", clear_on_submit=False):
        contatos_preenchidos = []

        for i in range(st.session_state.num_contatos):
            st.markdown(f'<div class="field-header-box">Contato {i + 1}</div>', unsafe_allow_html=True)
            c1, c2, c3 = st.columns([2, 2, 2])
            c4, c5 = st.columns([2, 2])

            nome = c1.text_input("Nome completo *", key=f"nome_{municipio_selecionado}_{i}")
            cargo = c2.text_input("Cargo *", key=f"cargo_{municipio_selecionado}_{i}")
            interesse = c3.text_input("Interesse / Pauta", key=f"interesse_{municipio_selecionado}_{i}")
            email = c4.text_input("E-mail *", key=f"email_{municipio_selecionado}_{i}")
            telefone = c5.text_input("Telefone / WhatsApp *", key=f"tel_{municipio_selecionado}_{i}")

            contatos_preenchidos.append({
                "Município/UF": municipio_selecionado,
                str(COL_TERMO): dados_mun[COL_TERMO],
                str(COL_RANKING): dados_mun[COL_RANKING],
                str(COL_STATUS): dados_mun[COL_STATUS],
                str(COL_PARTICIPACAO): dados_mun[COL_PARTICIPACAO],
                "Nome": nome,
                "Cargo": cargo,
                "Interesse": interesse,
                "E-mail": email,
                "Telefone": telefone
            })

            if i < st.session_state.num_contatos - 1:
                st.write("")

        enviado = st.form_submit_button("💾 Salvar Contatos", type="primary")

        if enviado:
            validos = [c for c in contatos_preenchidos if c["Nome"].strip() != ""]
            if not validos:
                st.warning("Preencha pelo menos o Nome do contato antes de salvar.")
            else:
                st.session_state.registros_salvos.extend(validos)
                st.success(f"{len(validos)} contato(s) vinculado(s) a **{municipio_selecionado}** salvo(s) com sucesso!")

    # 9. Tabela de Registros Salvos e Botão de Download Excel
    if st.session_state.registros_salvos:
        st.markdown("---")
        st.markdown('<div class="section-badge">📊 Contatos Registrados nesta Sessão</div>', unsafe_allow_html=True)
        df_salvos = pd.DataFrame(st.session_state.registros_salvos)
        st.dataframe(df_salvos, use_container_width=True)

        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df_salvos.to_excel(writer, index=False, sheet_name="Contatos_FNP")

        st.download_button(
            label="📥 Baixar Planilha com Contatos Cadastrados (.xlsx)",
            data=buffer.getvalue(),
            file_name="contatos_90_reuniao_fnp.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
