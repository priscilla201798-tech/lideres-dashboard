import streamlit as st
import pandas as pd
import json
import plotly.express as px

st.set_page_config(layout="wide")

# ==============================
# 🔹 CONFIG GOOGLE SHEETS
# ==============================

SHEET_ID = "1Q4UuncnykLJZrODE_Vwv-_WvCo7LWBNmbhnnPyb1Dt4"
GID = "632350714"

@st.cache_data
def cargar_data():
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}"
    df = pd.read_csv(url)
    return df

def extraer_dni_desde_key(key):
    return str(key).split("_")[0]

def aplanar_registros(df):

    resumen = []
    eventos = []
    objetivos = []
    asistencia = []

    for _, row in df.iterrows():

        fecha = row["Fecha"]
        key = row["Key"]
        dni = extraer_dni_desde_key(key)

        try:
            data = json.loads(row["RespuestasJSON"])
        except:
            continue

        fecha_dt = pd.to_datetime(fecha)
        año = fecha_dt.year
        mes = fecha_dt.month

        # RESUMEN
        resumen.append({
            "Fecha": fecha_dt,
            "Año": año,
            "Mes": mes,
            "DNI_Lider": dni,
            "Convertidos": int(data.get("¿Cuántas personas aceptaron a Cristo?", 0) or 0),
            "Reconciliados": int(data.get("¿Cuántas personas se reconciliaron con Cristo?", 0) or 0),
            "Asistentes": int(data.get("¿Cuántas personas asistieron en total?", 0) or 0),
            "Ofrenda": float(data.get("Monto total de la ofrenda (S/.)", 0) or 0)
        })

        # EVENTOS
        if data.get("¿Esta semana se realizó algún evento espiritual?") == "Sí":
            eventos.append({
                "Fecha": fecha_dt,
                "Año": año,
                "Mes": mes,
                "DNI_Lider": dni,
                "Tipo_Evento": data.get("¿Qué tipo de evento espiritual se realizó?", "").upper(),
                "Participantes": int(data.get("¿Cuántas personas participaron?", 0) or 0)
            })

        # OBJETIVOS
        if data.get("¿Deseas registrar avance en alguno de tus objetivos esta semana?") == "Sí":
            objetivos.append({
                "Fecha": fecha_dt,
                "Año": año,
                "Mes": mes,
                "DNI_Lider": dni,
                "Objetivo": data.get("¿En qué objetivo deseas registrar avance?", ""),
                "Avance": int(data.get("¿Cuánto avanzaste en este objetivo?", 0) or 0)
            })

        # ASISTENCIA
        asistentes = (
            data.get("Marca a los integrantes del equipo ALMAH que asistieron al culto dominical")
            or data.get("Marca a los integrantes del equipo que asistieron al culto dominical")
            or []
        )

        for persona in asistentes:
            asistencia.append({
                "Fecha": fecha_dt,
                "Año": año,
                "Mes": mes,
                "DNI_Lider": dni,
                "Persona": persona
            })

    return (
        pd.DataFrame(resumen),
        pd.DataFrame(eventos),
        pd.DataFrame(objetivos),
        pd.DataFrame(asistencia)
    )

# ==============================
# 🔹 CARGAR Y APLANAR
# ==============================

df = cargar_data()
df_resumen, df_eventos, df_objetivos, df_asistencia = aplanar_registros(df)

# ==============================
# 🔹 DISEÑO DASHBOARD
# ==============================

st.title("📊 Dashboard Ministerial")

# Filtros
colf1, colf2 = st.columns(2)

with colf1:
    año_seleccionado = st.selectbox("Selecciona Año", sorted(df_resumen["Año"].unique()))

with colf2:
    mes_seleccionado = st.selectbox("Selecciona Mes", sorted(df_resumen["Mes"].unique()))

df_resumen_f = df_resumen[(df_resumen["Año"] == año_seleccionado) & 
                          (df_resumen["Mes"] == mes_seleccionado)]

df_eventos_f = df_eventos[(df_eventos["Año"] == año_seleccionado) & 
                          (df_eventos["Mes"] == mes_seleccionado)]

df_objetivos_f = df_objetivos[(df_objetivos["Año"] == año_seleccionado) & 
                              (df_objetivos["Mes"] == mes_seleccionado)]

df_asistencia_f = df_asistencia[(df_asistencia["Año"] == año_seleccionado) & 
                                (df_asistencia["Mes"] == mes_seleccionado)]

st.markdown("## 📌 Indicadores Clave")

k1, k2, k3, k4 = st.columns(4)

k1.metric("✨ Convertidos", df_resumen_f["Convertidos"].sum())
k2.metric("🤝 Reconciliados", df_resumen_f["Reconciliados"].sum())
k3.metric("👥 Asistentes", df_resumen_f["Asistentes"].sum())
k4.metric("💰 Ofrenda (S/)", round(df_resumen_f["Ofrenda"].sum(),2))

st.divider()

# EVENTOS
if not df_eventos_f.empty:
    st.subheader("🔥 Eventos del Mes")
    fig = px.bar(
        df_eventos_f.groupby("Tipo_Evento").size().reset_index(name="Cantidad"),
        x="Tipo_Evento",
        y="Cantidad",
        color="Tipo_Evento"
    )
    st.plotly_chart(fig, use_container_width=True)

# OBJETIVOS
if not df_objetivos_f.empty:
    st.subheader("🎯 Avance de Objetivos")
    fig2 = px.bar(
        df_objetivos_f.groupby("Objetivo")["Avance"].sum().reset_index(),
        x="Objetivo",
        y="Avance",
        color="Objetivo"
    )
    st.plotly_chart(fig2, use_container_width=True)

# ASISTENCIA
if not df_asistencia_f.empty:
    st.subheader("👥 Asistencia del Equipo")
    fig3 = px.bar(
        df_asistencia_f.groupby("Persona").size().reset_index(name="Asistencias"),
        x="Persona",
        y="Asistencias",
        color="Persona"
    )
    st.plotly_chart(fig3, use_container_width=True)
