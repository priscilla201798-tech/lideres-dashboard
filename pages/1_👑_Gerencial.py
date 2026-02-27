import streamlit as st
import pandas as pd
import json
import plotly.express as px
import re

st.set_page_config(page_title="Vista Gerencial", layout="wide")

# ==============================
# 🔐 CONTRASEÑA GERENCIAL
# ==============================

clave = st.text_input("Contraseña Gerencial", type="password")

if clave != "INTIMOSIELA2026":
    st.warning("Acceso restringido")
    st.stop()

st.success("Acceso concedido")

# ==============================
# CONFIG GOOGLE SHEETS
# ==============================

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
    return default

def aplanar(df):

    resumen = []

    for _, row in df.iterrows():
        try:
            fecha = pd.to_datetime(row["Fecha"])
            dni = str(row["DNI_Lider"]).strip().zfill(8)
        except:
            continue

        raw_json = row.get("RespuestasJSON", "")
        if not isinstance(raw_json, str) or raw_json.strip() == "":
            continue

        try:
            data = json.loads(raw_json)
        except:
            continue

        resumen.append({
            "Fecha": fecha,
            "DNI": dni,
            "Convertidos": int(get_num(data, "¿Cuántas personas aceptaron a Cristo?", default=0)),
            "Reconciliados": int(get_num(data, "¿Cuántas personas se reconciliaron con Cristo?", default=0)),
            "Nuevos": int(get_num(data, "¿Cuántas personas nuevas asistieron?", default=0)),
            "Visitas": int(get_num(data, "Cantidad de visitas realizadas", default=0)),
        })

    return pd.DataFrame(resumen)

# ==============================
# CARGAR DATA
# ==============================

df_raw = cargar_sheet(GID_REGISTROS)
df_plan_eventos = cargar_sheet(GID_EVENTOS)

df_resumen = aplanar(df_raw)

# ==============================
# 🔵 KPIs MACRO
# ==============================

st.title("👑 Dashboard Gerencial")

total_convertidos = df_resumen["Convertidos"].sum()
total_nuevos = df_resumen["Nuevos"].sum()
total_reconciliados = df_resumen["Reconciliados"].sum()
total_visitas = df_resumen["Visitas"].sum()

c1, c2, c3, c4 = st.columns(4)

c1.metric("Convertidos Totales", total_convertidos)
c2.metric("Nuevos Totales", total_nuevos)
c3.metric("Reconciliados Totales", total_reconciliados)
c4.metric("Visitas Totales", total_visitas)

st.divider()

# ==============================
# 🏆 Ranking por Ministerio
# ==============================

df_plan_eventos["DNI_Lider"] = df_plan_eventos["DNI_Lider"].astype(str).str.zfill(8)

df_merge = df_resumen.merge(
    df_plan_eventos[["DNI_Lider", "EntidadNombre", "SupervisorNombre"]],
    left_on="DNI",
    right_on="DNI_Lider",
    how="left"
)

ranking = (
    df_merge.groupby("EntidadNombre")["Convertidos"]
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)

st.subheader("🏆 Ranking por Ministerio")

fig = px.bar(ranking, x="EntidadNombre", y="Convertidos")
st.plotly_chart(fig, use_container_width=True)
