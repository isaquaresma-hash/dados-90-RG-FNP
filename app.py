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
    "div.stButton > button[kind='primary'] { background-color: #2563eb; color: #ffffff; border: 1px solid #60a5fa; border-radius: 8px; padding: 10px 18px; font-weight:
