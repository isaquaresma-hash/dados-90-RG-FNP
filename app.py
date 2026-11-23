import streamlit as st
import pandas as pd
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

TEMATICAS_FNP = [
    "Finanças",
    "Inovação e transformação digital",
    "Limpeza urbana e manejo de resíduos sólidos",
    "PPPs e concessões",
    "Políticas para mulheres",
    "Adaptação, mitigação e prevenção de desastres",
    "Desenvolvimento urbano sustentável",
    "Assuntos sociais",
    "Cultura",
    "Proteção de dados",
    "Planejamento e desenvolvimento urbano",
    "Mobilidade urbana",
    "Cidades inteligentes",
    "Educação",
    "Saúde",
    "Procuradores-gerais das capitais e grandes cidades",
    "CGIBS",
    "Missões internacionais",
    "Municípios subfinanciados"
]

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

COLUNAS_PADRAO = [
    "Data/Hora", "Município/UF", "Nome", "Cargo", "Setor",
    "Interesse / Pauta", "E-mail", "Telefone", "Observação"
]

@st.cache_resource
def conectar_planilha():
    escopos = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    credenciais = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=escopos
    )
    cliente = gspread.authorize(credenciais)
    return cliente.open_by_url(st.secrets["sheet_url"])

def obter_aba(nome_aba):
    planilha = conectar_planilha()
    try:
        aba = planilha.worksheet(nome_aba)
    except gspread.WorksheetNotFound:
        aba = planilha.add_worksheet(title=nome_aba, rows=1000, cols=len(COLUNAS_PADRAO))
    if not aba.row_values(1):
        aba.append_row(COLUNAS_PADRAO)
    return aba

def salvar_registro_aba(nome_aba, novo_registro):
    aba = obter_aba(nome_aba)
    linha = [str(novo_registro.get(col, "")) for col in COLUNAS_PADRAO]
    aba.append_row(linha, value_input_option="USER_ENTERED")

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
        dados_mun = df[df[COL_MUNICIPIO].astype(str) == selecao].iloc[0]
        val_termo = dados_mun[COL_TERMO]
        val_ranking = dados_mun[COL_RANKING]
        val_status = dados_mun[COL_STATUS]
        val_participacao = dados_mun[COL_PARTICIPACAO]

        st.write("")
        c_termo, c_rank, c_status, c_part = st.columns([1.2, 1, 1.3, 2])

        with c_termo:
            st.markdown(f'<div class="field-header-box">{COL_TERMO}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="data-value-box">{val_termo}</div>', unsafe_allow_html=True)

        with c_rank:
            st.markdown(f'<div class="field-header-box">{COL_RANKING}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="data-value-box">{val_ranking}</div>', unsafe_allow_html=True)

        with c_status:
            st.markdown(f'<div class="field-header-box">{COL_STATUS}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="data-value-box">{val_status}</div>', unsafe_allow_html=True)

        with c_part:
            st.markdown(f'<div class="field-header-box">{COL_PARTICIPACAO}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="data-value-box">{val_participacao}</div>', unsafe_allow_html=True)

        st.markdown("---")

        if "num_contatos" not in st.session_state:
            st.session_state.num_contatos = 1

        if st.session_state.get("ultimo_municipio") != selecao:
            st.session_state.num_contatos = 1
            st.session_state.ultimo_municipio = selecao

        st.markdown(f'<div class="section-badge">📝 Cadastro de Contatos / Representantes — {selecao}</div>', unsafe_allow_html=True)
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
            contatos_temp = []

            for i in range(st.session_state.num_contatos):
                st.markdown(f'<div class="field-header-box">Contato {i + 1}</div>', unsafe_allow_html=True)
                c1, c2, c3 = st.columns([2, 1.5, 1.5])
                c4, c5 = st.columns([2, 2])

                nome = c1.text_input("Nome completo *", key=f"nome_{selecao}_{i}")
                cargo = c2.text_input("Cargo *", key=f"cargo_{selecao}_{i}")
                setor = c3.text_input("Setor", key=f"setor_{selecao}_{i}")
                email = c4.text_input("E-mail *", key=f"email_{selecao}_{i}")
                telefone = c5.text_input("Telefone / WhatsApp *", key=f"tel_{selecao}_{i}")

                st.markdown('<div class="field-header-box" style="margin-top:8px;">Interesse / Pauta — Temáticas (Marque as opções desejadas)</div>', unsafe_allow_html=True)
                nenhum_marcado = st.checkbox("Nenhum interesse específico / Apenas acompanhamento geral", key=f"pauta_nenhum_{selecao}_{i}")

                itens_marcados = []
                with st.expander(f"📌 Temáticas ({len(TEMATICAS_FNP)} opções)", expanded=True):
                    col_chk1, col_chk2 = st.columns(2)
                    for idx_item, item_nome in enumerate(TEMATICAS_FNP):
                        coluna_atual = col_chk1 if idx_item % 2 == 0 else col_chk2
                        marcado = coluna_atual.checkbox(
                            item_nome,
                            key=f"chk_{selecao}_{i}_{idx_item}"
                        )
                        if marcado:
                            itens_marcados.append(item_nome)

                if nenhum_marcado and not itens_marcados:
                    interesse_str = "Nenhum"
                else:
                    interesse_str = "; ".join(itens_marcados)

                contatos_temp.append({
                    "nome": nome,
                    "cargo": cargo,
                    "setor": setor,
                    "interesse": interesse_str,
                    "email": email,
                    "telefone": telefone
                })

                if i < st.session_state.num_contatos - 1:
                    st.markdown("---")

            st.write("")
            st.markdown('<div class="field-header-box">Observação dos Contatos / Atendimento</div>', unsafe_allow_html=True)
            observacao_contatos = st.text_area(
                "Observação",
                placeholder="Digite aqui observações livres sobre os contatos ou o atendimento...",
                height=90,
                key=f"obs_contatos_{selecao}",
                label_visibility="collapsed"
            )

            enviado = st.form_submit_button("💾 Salvar Cadastro", type="primary")

            if enviado:
                validos = [c for c in contatos_temp if c["nome"].strip() != ""]
                if not validos:
                    st.warning("Preencha pelo menos o Nome do contato antes de salvar.")
                else:
                    for c in validos:
                        salvar_registro_aba("Cadastros_FNP", {
                            "Data/Hora": datetime.now().strftime("%d/%m/%Y %H:%M"),
                            "Município/UF": selecao,
                            "Nome": c["nome"],
                            "Cargo": c["cargo"],
                            "Setor": c["setor"],
                            "Interesse / Pauta": c["interesse"],
                            "E-mail": c["email"],
                            "Telefone": c["telefone"],
                            "Observação": observacao_contatos.strip()
                        })
                    st.success(f"{len(validos)} registro(s) vinculado(s) a **{selecao}** salvo(s) na aba **Cadastros_FNP** com sucesso!")

elif st.session_state.modo_operacao == "novo":
    if "num_contatos_novo" not in st.session_state:
        st.session_state.num_contatos_novo = 1

    st.markdown('<div class="section-badge">📝 Cadastro de Contatos / Representantes — Novo Município</div>', unsafe_allow_html=True)
    st.caption("Preencha os dados abaixo. Clique em '+ Adicionar outro contato' para incluir mais representantes deste município.")

    col_n_add, col_n_rem, _ = st.columns([1.6, 1.6, 5])
    with col_n_add:
        if st.button("➕ Adicionar outro contato", key="btn_add_novo_contato", use_container_width=True):
            st.session_state.num_contatos_novo += 1
            st.rerun()
    with col_n_rem:
        if st.session_state.num_contatos_novo > 1:
            if st.button("➖ Remover último", key="btn_rem_novo_contato", use_container_width=True):
                st.session_state.num_contatos_novo -= 1
                st.rerun()

    with st.form("form_novo_municipio_fnp", clear_on_submit=False):
        st.markdown('<div class="field-header-box">📍 Município/UF (não listado na base)</div>', unsafe_allow_html=True)
        novo_nome = st.text_input(
            "Nome do Município/UF *",
            placeholder="Digite o nome do município e UF (Ex: Palmas/TO)",
            label_visibility="collapsed",
            key="input_novo_municipio_nome"
        )

        st.write("")
        contatos_novos_temp = []

        for i in range(st.session_state.num_contatos_novo):
            st.markdown(f'<div class="field-header-box">Contato {i + 1}</div>', unsafe_allow_html=True)
            c1, c2, c3 = st.columns([2, 1.5, 1.5])
            c4, c5 = st.columns([2, 2])

            nome = c1.text_input("Nome completo *", key=f"novo_nome_{i}")
            cargo = c2.text_input("Cargo *", key=f"novo_cargo_{i}")
            setor = c3.text_input("Setor", key=f"novo_setor_{i}")
            email = c4.text_input("E-mail *", key=f"novo_email_{i}")
            telefone = c5.text_input("Telefone / WhatsApp *", key=f"novo_tel_{i}")

            st.markdown('<div class="field-header-box" style="margin-top:8px;">Interesse / Pauta — Temáticas (Marque as opções desejadas)</div>', unsafe_allow_html=True)
            nenhum_marcado = st.checkbox("Nenhum interesse específico / Apenas acompanhamento geral", key=f"novo_pauta_nenhum_{i}")

            itens_marcados = []
            with st.expander(f"📌 Temáticas ({len(TEMATICAS_FNP)} opções)", expanded=True):
                col_n_chk1, col_n_chk2 = st.columns(2)
                for idx_item, item_nome in enumerate(TEMATICAS_FNP):
                    coluna_atual = col_n_chk1 if idx_item % 2 == 0 else col_n_chk2
                    marcado = coluna_atual.checkbox(
                        item_nome,
                        key=f"novo_chk_{i}_{idx_item}"
                    )
                    if marcado:
                        itens_marcados.append(item_nome)

            if nenhum_marcado and not itens_marcados:
                interesse_str = "Nenhum"
            else:
                interesse_str = "; ".join(itens_marcados)

            contatos_novos_temp.append({
                "nome": nome,
                "cargo": cargo,
                "setor": setor,
                "interesse": interesse_str,
                "email": email,
                "telefone": telefone
            })

            if i < st.session_state.num_contatos_novo - 1:
                st.markdown("---")

        st.write("")
        st.markdown('<div class="field-header-box">Observação dos Contatos / Município</div>', unsafe_allow_html=True)
        obs_novo_municipio = st.text_area(
            "Observação",
            placeholder="Digite aqui observações livres sobre este novo município ou os contatos...",
            height=90,
            key="obs_novo_mun_input",
            label_visibility="collapsed"
        )

        salvou_municipio = st.form_submit_button("💾 Salvar Cadastro", type="primary")

        if salvou_municipio:
            if not novo_nome.strip():
                st.warning("Preencha o **Município/UF** antes de salvar.")
            else:
                validos = [c for c in contatos_novos_temp if c["nome"].strip() != ""]
                if not validos:
                    st.warning("Preencha pelo menos o Nome de um contato antes de salvar.")
                else:
                    for c in validos:
                        salvar_registro_aba("Novos_Municipios", {
                            "Data/Hora": datetime.now().strftime("%d/%m/%Y %H:%M"),
                            "Município/UF": novo_nome.strip(),
                            "Nome": c["nome"].strip(),
                            "Cargo": c["cargo"].strip(),
                            "Setor": c["setor"].strip(),
                            "Interesse / Pauta": c["interesse"],
                            "E-mail": c["email"].strip(),
                            "Telefone": c["telefone"].strip(),
                            "Observação": obs_novo_municipio.strip()
                        })
                    st.success(f"{len(validos)} registro(s) vinculado(s) a **{novo_nome.strip()}** salvo(s) na aba **Novos_Municipios** com sucesso!")
