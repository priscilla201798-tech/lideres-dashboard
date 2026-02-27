import streamlit as st
import pandas as pd
import json
import re

SHEET_ID = "1Q4UuncnykLJZrODE_Vwv-_WvCo7LWBNmbhnnPyb1Dt4"
GID_REGISTROS = "632350714"
GID_EVENTOS = "1679434742"
GID_OBJETIVOS = "236814605"

@st.cache_data(ttl=120)
def cargar_sheet(gid):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={gid}"
    return pd.read_csv(url)

def norm_txt(s):
    return re.sub(r"\s+", " ", str(s or "").strip().lower())

def es_si(valor):
    v = norm_txt(valor)
    return v in {"si", "sí", "s", "yes", "true", "1", "ok", "x"}

def get_num(data, *keys, default=0):
    if not isinstance(data, dict):
        return default

    for k in keys:
        if k in data:
            try:
                return float(data.get(k) or 0)
            except:
                return default

    wanted = {norm_txt(k) for k in keys}
    for k_data, v in data.items():
        if norm_txt(k_data) in wanted:
            try:
                return float(v or 0)
            except:
                return default
    return default

def get_val(data, *keys, default=""):
    if not isinstance(data, dict):
        return default
    for k in keys:
        if k in data:
            return data.get(k)
    wanted = {norm_txt(k) for k in keys}
    for k_data, v in data.items():
        if norm_txt(k_data) in wanted:
            return v
    return default
