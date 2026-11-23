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
val_ranking =
