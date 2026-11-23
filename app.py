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
        "Imersão Técnica Internacional em Cidades Inteligentes, Inovação, Governo Digital, Educação
