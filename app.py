import streamlit as st
import pandas as pd
from io import BytesIO
import base64
import os

# 1. Configuração da Página
st.set_page_config(
    page_title="90ª Reunião Geral da FNP - Consulta e Credenciamento",
    page_icon="🏛️",
    layout="wide"
)

# 2. Estilos HTML / CSS Personalizados alinhados à identidade visual da FNP
st.markdown("""
<style>
    /* Fundo suave da página */
    [data-testid="stAppViewContainer"] {
        background-color: #f4f6f9;
    }
    
    /* Banner Oficial no Topo */
    .fnp-banner-box {
        background-color: #052038;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 12px rgba(5, 32, 56, 0.18);
        margin-bottom: 24px;
    }
    .fnp-banner-box img {
        width: 100%;
        height: auto;
        display: block;
    }
    .fnp-banner-subtitle {
        background-color: #082d4f;
        color: #ffffff;
        padding: 12px 28px;
        font-size: 1.05rem;
        font-weight: 500;
        border-top: 1px solid rgba(255, 255, 255, 0.12);
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
    }

    /* Cartões de Dados do Município */
    .info-card {
        background-color: #ffffff;
        border: 1px solid #dce3ec;
        border-top: 4px solid #052038;
        border-radius: 8px;
        padding: 16px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.05);
        height: 100%;
    }
    .info-label {
        font-size: 0.78rem;
        text-transform: uppercase;
        color: #5c6b7a;
        font-weight: 700;
        margin-bottom: 6px;
    }
    .info-value {
        font-size: 1.05rem;
        font-weight: 600;
        color: #052038;
        line-height: 1.4;
    }
</style>
""", unsafe_allow_html=True)

# 3. Renderização do Banner Oficial ("imagem.pdf.png") no Cabeçalho
def exibir_banner_oficial(caminho_imagem):
    if os.path.exists(caminho_imagem):
        with open(caminho_imagem, "rb") as img_file:
            b64_string = base64.b64encode(img_file.read()).decode()
        
        st.markdown(f"""
        <div class="fnp-banner-box">
            <img src="data:image/png;base64,{b64_string}" alt="FNP - Frente Nacional de Prefeitas e Prefeitos">
            <div class="fnp-banner-subtitle">
                <span><strong>90ª Reunião Geral da FNP</strong> — Consulta de Municípios e Credenciamento</span>
                <span style="font-size: 0.9rem; opacity: 0.85;">Base atualizada em 20/11</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("Imagem 'imagem.pdf.png' não encontrada no repositório.")

exibir_banner_oficial("imagem.pdf.png")

# 4. Carregamento da Planilha Excel pulando a linha 1
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
    st.error("Arquivo 'banco de dados.xlsx' não encontrado. Verifique se ele está na mesma pasta do app.py.")
    st.stop()

# Mapeamento automático das 5 colunas da planilha
COL_MUNICIPIO    = df.columns[0]  # Município/UF
COL_TERMO        = df.columns[1]  # Requer assinatura do termo...
COL_RANKING      = df.columns[2]  # Ranking
COL_STATUS       = df.columns[3]  # Status
COL_PARTICIPACAO = df.columns[4]  # Participação

# 5. Campo de Busca por Município/UF
st.subheader("🔍 Consulta de Município/UF")
lista_municipios = sorted(df[COL_MUNICIPIO].astype(str).unique().tolist())

municipio_selecionado = st.selectbox(
    "Digite ou selecione o nome do município:",
    options=lista_municipios,
    index=None,
    placeholder="Ex: Águas Lindas de Goiás/GO, Alvorada/RS, Amparo/SP..."
)

# 6. Exibição dos Dados e Formulário Dinâmico após a Busca
if municipio_selecionado:
    dados_mun = df[df[COL_MUNICIPIO].astype(str) == municipio_selecionado].iloc[0]

    st.markdown(f"### 📋 Situação Institucional: **{municipio_selecionado}**")

    col1, col2, col3, col4 = st.columns([1.2, 1, 1.3, 2])

    with col1:
        st.markdown(f"""
        <div class="info-card">
            <div class="info-label">{COL_TERMO}</div>
            <div class="info-value">{dados_mun[COL_TERMO]}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="info-card">
            <div class="info-label">{COL_RANKING}</div>
            <div class="info-value">{dados_mun[COL_RANKING]}</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="info-card">
            <div class="info-label">{COL_STATUS}</div>
            <div class="info-value">{dados_mun[COL_STATUS]}</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="info-card">
            <div class="info-label">{COL_PARTICIPACAO}</div>
            <div class="info-value">{dados_mun[COL_PARTICIPACAO]}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # 7. Controle de Múltiplos Contatos na Memória da Sessão
    if "num_contatos" not in st.session_state:
        st.session_state.num_contatos = 1
    if "registros_salvos" not in st.session_state:
        st.session_state.registros_salvos = []

    if st.session_state.get("ultimo_municipio") != municipio_selecionado:
        st.session_state.num_contatos = 1
        st.session_state.ultimo_municipio = municipio_selecionado

    st.subheader("📝 Cadastro de Contatos / Representantes")
    st.caption("Preencha os dados abaixo. Caso deseje cadastrar mais pessoas deste município, clique em '+ Adicionar outro contato'.")

    col_add, col_rem, _ = st.columns([1.5, 1.5, 5])
    with col_add:
        if st.button("➕ Adicionar outro contato"):
            st.session_state.num_contatos += 1
            st.rerun()
    with col_rem:
        if st.session_state.num_contatos > 1:
            if st.button("➖ Remover último"):
                st.session_state.num_contatos -= 1
                st.rerun()

    # Formulário com blocos dinâmicos
    with st.form("form_contatos_fnp", clear_on_submit=False):
        contatos_preenchidos = []

        for i in range(st.session_state.num_contatos):
            st.markdown(f"**Contato {i + 1}**")
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
                st.divider()

        enviado = st.form_submit_button("💾 Salvar Contatos", type="primary")

        if enviado:
            validos = [c for c in contatos_preenchidos if c["Nome"].strip() != ""]
            if not validos:
                st.warning("Preencha pelo menos o Nome do contato antes de salvar.")
            else:
                st.session_state.registros_salvos.extend(validos)
                st.success(f"{len(validos)} contato(s) vinculado(s) a **{municipio_selecionado}** salvo(s) com sucesso!")

    # 8. Visualização e Exportação dos Contatos Cadastrados
    if st.session_state.registros_salvos:
        st.markdown("---")
        st.subheader("📊 Contatos Registrados nesta Sessão")
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
