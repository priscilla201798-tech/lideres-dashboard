import streamlit as st
import pandas as pd
import json
import plotly.express as px

st.set_page_config(layout="wide")

# ==============================
# CONFIG GOOGLE SHEETS
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

        if data.get("¿Esta semana se realizó algún evento espiritual?") == "Sí":
            eventos.append({
                "Fecha": fecha_dt,
                "Año": año,
                "Mes": mes,
                "DNI_Lider": dni,
                "Tipo_Evento": data.get("¿Qué tipo de evento espiritual se realizó?", "").upper(),
                "Participantes": int(data.get("¿Cuántas personas participaron?", 0) or 0)
            })

        if data.get("¿Deseas registrar avance en alguno de tus objetivos esta semana?") == "Sí":
            objetivos.append({
                "Fecha": fecha_dt,
                "Año": año,
                "Mes": mes,
                "DNI_Lider": dni,
                "Objetivo": data.get("¿En qué objetivo deseas registrar avance?", ""),
                "Avance": int(data.get("¿Cuánto avanzaste en este objetivo?", 0) or 0)
            })

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
# LOGIN
# ==============================

df_raw = cargar_data()
df_resumen, df_eventos, df_objetivos, df_asistencia = aplanar_registros(df_raw)

if "dni_login" not in st.session_state:
    st.session_state.dni_login = None

if st.session_state.dni_login is None:

    st.title("🔐 Acceso Líder")

    dni_input = st.text_input("Ingrese su DNI")

    if st.button("Ingresar"):

        dni_input = dni_input.strip()

        if dni_input in df_resumen["DNI_Lider"].unique():
            st.session_state.dni_login = dni_input
            st.rerun()
        else:
            st.error("DNI no encontrado.")

    st.stop()

# ==============================
# DASHBOARD FILTRADO
# ==============================

dni = st.session_state.dni_login

st.sidebar.success(f"DNI conectado: {dni}")

if st.sidebar.button("Cerrar sesión"):
    st.session_state.dni_login = None
    st.rerun()

df_resumen = df_resumen[df_resumen["DNI_Lider"] == dni]
df_eventos = df_eventos[df_eventos["DNI_Lider"] == dni]
df_objetivos = df_objetivos[df_objetivos["DNI_Lider"] == dni]
df_asistencia = df_asistencia[df_asistencia["DNI_Lider"] == dni]

st.title("📊 Mi Dashboard Ministerial")

col1, col2, col3, col4 = st.columns(4)

col1.metric("✨ Convertidos", df_resumen["Convertidos"].sum())
col2.metric("🤝 Reconciliados", df_resumen["Reconciliados"].sum())
col3.metric("👥 Asistentes", df_resumen["Asistentes"].sum())
col4.metric("💰 Ofrenda", round(df_resumen["Ofrenda"].sum(),2))

st.divider()

if not df_eventos.empty:
    fig = px.bar(
        df_eventos.groupby("Mes").size().reset_index(name="Eventos"),
        x="Mes",
        y="Eventos",
        title="Eventos por mes"
    )
    st.plotly_chart(fig, use_container_width=True)

if not df_objetivos.empty:
    fig2 = px.bar(
        df_objetivos.groupby("Objetivo")["Avance"].sum().reset_index(),
        x="Objetivo",
        y="Avance",
        title="Avance Objetivos"
    )
    st.plotly_chart(fig2, use_container_width=True)

if not df_asistencia.empty:
    fig3 = px.bar(
        df_asistencia.groupby("Persona").size().reset_index(name="Asistencias"),
        x="Persona",
        y="Asistencias",
        title="Asistencia Equipo"
    )
    st.plotly_chart(fig3, use_container_width=True)
