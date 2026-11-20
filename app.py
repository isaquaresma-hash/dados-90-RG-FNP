import streamlit as st
import pandas as pd
from io import BytesIO

# 1. Configuração da Página
st.set_page_config(
    page_title="90ª Reunião Geral da FNP - Consulta e Credenciamento",
    page_icon="🏛️",
    layout="wide"
)

# 2. Estilos HTML / CSS Personalizados
st.markdown("""
<style>
    .fnp-header {
        background: linear-gradient(135deg, #0b2e59 0%, #16539c 100%);
        padding: 25px 30px;
        border-radius: 12px;
        color: white;
        margin-bottom: 25px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.12);
    }
    .fnp-header h1 {
        margin: 0;
        font-size: 1.9rem;
    }
    .fnp-header p {
        margin: 6px 0 0 0;
        opacity: 0.9;
        font-size: 1rem;
    }
    .info-card {
        background-color: #ffffff;
        border: 1px solid #e0e6ed;
        border-top: 4px solid #16539c;
        border-radius: 8px;
        padding: 16px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.04);
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
        font-size: 1.15rem;
        font-weight: 600;
        color: #1a2530;
    }
</style>

<div class="fnp-header">
    <h1>🏛️ 90ª Reunião Geral da FNP</h1>
    <p>Base de Consulta de Municípios e Cadastro de Representantes</p>
</div>
""", unsafe_allow_html=True)

# 3. Carregamento da Planilha Excel
@st.cache_data
def carregar_dados():
    # Certifique-se de que o nome do arquivo seja exatamente o mesmo enviado ao GitHub
    df = pd.read_excel("dados_fnp.xlsx")
    df.columns = df.columns.str.strip()  # Remove espaços extras nos nomes das colunas
    return df

try:
    df = carregar_dados()
except FileNotFoundError:
    st.error("Arquivo 'dados_fnp.xlsx' não encontrado. Verifique se ele está na mesma pasta do app.py.")
    st.stop()

# ⚠️ AJUSTE AQUI OS NOMES EXATOS DAS COLUNAS DA SUA PLANILHA EXCEL:
COL_MUNICIPIO    = "Município"
COL_TERMO        = "Requer assinatura do termo de filiação"
COL_RANKING      = "Ranking"
COL_STATUS       = "Status"
COL_PARTICIPACAO = "Participação"

# Verifica se as colunas existem na planilha
colunas_necessarias = [COL_MUNICIPIO, COL_TERMO, COL_RANKING, COL_STATUS, COL_PARTICIPACAO]
faltantes = [c for c in colunas_necessarias if c not in df.columns]

if faltantes:
    st.warning(f"Atenção: As colunas abaixo não foram encontradas na planilha: {faltantes}")
    st.info(f"Colunas disponíveis no seu Excel: {list(df.columns)}")
    st.stop()

# 4. Campo de Busca por Município
st.subheader("🔍 Consulta de Município")
lista_municipios = sorted(df[COL_MUNICIPIO].dropna().astype(str).unique().tolist())

municipio_selecionado = st.selectbox(
    "Digite ou selecione o nome do município:",
    options=lista_municipios,
    index=None,
    placeholder="Ex: Brasília, São Paulo, Recife..."
)

# 5. Exibição dos Dados e Formulário Dinâmico após a Busca
if municipio_selecionado:
    # Filtra a linha correspondente ao município escolhido
    dados_mun = df[df[COL_MUNICIPIO].astype(str) == municipio_selecionado].iloc[0]

    st.markdown(f"### 📋 Situação Institucional: **{municipio_selecionado}**")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="info-card">
            <div class="info-label">Termo de Filiação</div>
            <div class="info-value">{dados_mun[COL_TERMO]}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="info-card">
            <div class="info-label">Ranking</div>
            <div class="info-value">{dados_mun[COL_RANKING]}</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="info-card">
            <div class="info-label">Status</div>
            <div class="info-value">{dados_mun[COL_STATUS]}</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="info-card">
            <div class="info-label">Participação</div>
            <div class="info-value">{dados_mun[COL_PARTICIPACAO]}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # 6. Controle de Múltiplos Contatos na Memória da Sessão
    if "num_contatos" not in st.session_state:
        st.session_state.num_contatos = 1
    if "registros_salvos" not in st.session_state:
        st.session_state.registros_salvos = []

    # Reseta a quantidade de blocos para 1 se trocar de município
    if st.session_state.get("ultimo_municipio") != municipio_selecionado:
        st.session_state.num_contatos = 1
        st.session_state.ultimo_municipio = municipio_selecionado

    st.subheader("📝 Cadastro de Contatos / Representantes")
    st.caption("Preencha os dados abaixo. Caso deseje cadastrar mais pessoas deste município, clique em '+ Adicionar outro contato'.")

    # Botões para adicionar ou remover blocos de contato
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
                "Município": municipio_selecionado,
                "Termo de Filiação": dados_mun[COL_TERMO],
                "Ranking": dados_mun[COL_RANKING],
                "Status": dados_mun[COL_STATUS],
                "Participação": dados_mun[COL_PARTICIPACAO],
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

    # 7. Visualização e Exportação dos Contatos Cadastrados
    if st.session_state.registros_salvos:
        st.markdown("---")
        st.subheader("📊 Contatos Registrados nesta Sessão")
        df_salvos = pd.DataFrame(st.session_state.registros_salvos)
        st.dataframe(df_salvos, use_container_width=True)

        # Gera arquivo Excel para download imediato
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df_salvos.to_excel(writer, index=False, sheet_name="Contatos_FNP")

        st.download_button(
            label="📥 Baixar Planilha com Contatos Cadastrados (.xlsx)",
            data=buffer.getvalue(),
            file_name="contatos_90_reuniao_fnp.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
