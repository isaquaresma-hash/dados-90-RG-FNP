import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime
import base64
import os
import gspread
from google.oauth2.service_account import Credentials

# 1. Configuração da Página
st.set_page_config(
    page_title="90ª Reunião Geral da FNP",
    page_icon="🏛️",
    layout="wide"
)

# 2. CSS com a cor exata do fundo (#00243d) e alto contraste nos blocos
st.markdown("""
<style>
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
    .fnp-main-title {
        color: #ffffff;
        font-size: 1.8rem;
        font-weight: 700;
        margin-top: 0.2rem;
        margin-bottom: 1.2rem;
    }
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
    div.stButton > button[kind="secondary"] {
        background-color: #1a3a54;
        color: #ffffff;
        border: 1px solid rgba(255, 255, 255, 0.18);
        border-radius: 8px;
        padding: 10px 18px;
        font-weight: 600;
        font-size: 0.95rem;
        transition: all 0.2s ease;
    }
    div.stButton > button[kind="secondary"]:hover {
        background-color: #244e70;
        border-color: rgba(255, 255, 255, 0.4);
        color: #ffffff;
    }
    div.stButton > button[kind="primary"] {
        background-color: #2563eb;
        color: #ffffff;
        border: 1px solid #60a5fa;
        border-radius: 8px;
        padding: 10px 18px;
        font-weight: 700;
        font-size: 0.95rem;
    }
    [data-testid="stForm"] button[kind="primary"] {
        background-color: #ef4444;
        border: 1px solid #f87171;
        color: #ffffff;
    }
    [data-testid="stForm"] button[kind="primary"]:hover {
        background-color: #dc2626;
        border-color: #fca5a5;
        color: #ffffff;
    }
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
    .field-header-box {
        background-color: #1a3a54;
        color: #ffffff;
        padding: 8px 14px;
        border-radius: 6px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-bottom: 8px;
    }
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
    label[data-testid="stWidgetLabel"] p {
        color: #ffffff !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
    }
    div[data-testid="stCheckbox"] label p {
        color: #f8fafc !important;
        font-weight: 400 !important;
        font-size: 0.88rem !important;
    }
    details[data-testid="stExpander"],
    div[data-testid="stExpander"] {
        background-color: #164266 !important;
        border: 1px solid rgba(255, 255, 255, 0.35) !important;
        border-radius: 8px !important;
        margin-bottom: 10px !important;
    }
    details[data-testid="stExpander"] summary,
    div[data-testid="stExpander"] summary {
        background-color: #1e527d !important;
        color: #ffffff !important;
        border-radius: 7px !important;
        padding: 10px 14px !important;
    }
    details[data-testid="stExpander"] summary:hover,
    div[data-testid="stExpander"] summary:hover {
        background-color: #256396 !important;
    }
    details[data-testid="stExpander"] summary *,
    div[data-testid="stExpander"] summary * {
        color: #ffffff !important;
        fill: #ffffff !important;
        font-weight: 700 !important;
        font-size: 0.96rem !important;
    }
    details[data-testid
