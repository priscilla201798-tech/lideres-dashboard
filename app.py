import streamlit as st
import pandas as pd
import plotly.express as px

# ----------------------------
# CONFIGURACIÓN GENERAL
# ----------------------------

st.set_page_config(
    page_title="Líderes Dashboard",
    layout="wide",
)

SHEET_ID = "1Q4UuncnykLJZrODE_Vwv-_WvCo7LWBNmbhnnPyb1Dt4"

URL_ANALISIS = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=BD_ANALISIS_SEMANAL"
URL_OBJETIVOS = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=BD_OBJETIVOS_ANALISIS"

# ----------------------------
# CARGA DE DATOS
# ----------------------------

@st.cache_data
def load_data():
    df_analisis = pd.read_csv(URL_ANALISIS)
    df_obj = pd.read_csv(URL_OBJETIVOS)

    df_analisis["Fecha"] = pd.to_datetime(df_analisis["Fecha"])
    df_obj["Fecha"] = pd.to_datetime(df_obj["Fecha"])

    return df_analisis, df_obj

df, df_obj = load_data()

# ----------------------------
# LOGIN SIMPLE
# ----------------------------

st.sidebar.title("🔐 Acceso")

rol = st.sidebar.selectbox("Selecciona tu rol", ["Líder", "Supervisor"])

if rol == "Líder":
    dni_input = st.sidebar.text_input("Ingresa tu DNI")
    acceso = dni_input in df["DNI_Lider"].astype(str).unique()
else:
    clave = st.sidebar.text_input("Clave supervisor", type="password")
    acceso = clave == "super123"

if not acceso:
    st.warning("Ingresa credenciales válidas.")
    st.stop()

# ----------------------------
# FILTROS
# ----------------------------

st.sidebar.title("🎯 Filtros")

fecha_min = df["Fecha"].min()
fecha_max = df["Fecha"].max()

rango_fechas = st.sidebar.date_input(
    "Rango de fechas",
    [fecha_min, fecha_max]
)

df = df[(df["Fecha"] >= pd.to_datetime(rango_fechas[0])) &
        (df["Fecha"] <= pd.to_datetime(rango_fechas[1]))]

if rol == "Líder":
    df = df[df["DNI_Lider"].astype(str) == dni_input]

# ----------------------------
# KPIs
# ----------------------------

st.title("📊 Dashboard de Líderes")

col1, col2, col3, col4 = st.columns(4)

with col1:
    asistencia_total = df["Asistencia_Dominical_Equipo"].sum()
    st.metric("👥 Asistencia Total", int(asistencia_total))

with col2:
    eventos_total = df["Evento_Realizado"].sum()
    st.metric("🔥 Eventos Espirituales", int(eventos_total))

with col3:
    reuniones = df["Reunion_Realizada"].sum()
    st.metric("📅 Reuniones Realizadas", int(reuniones))

with col4:
    cumplimiento = df["Cumplio_Programacion"].mean() * 100
    st.metric("🎯 % Cumplimiento", f"{cumplimiento:.1f}%")

st.markdown("---")

# ----------------------------
# GRÁFICOS
# ----------------------------

colA, colB = st.columns(2)

with colA:
    st.subheader("📈 Tendencia Asistencia")
    fig = px.line(
        df.groupby("Fecha")["Asistencia_Dominical_Equipo"].sum().reset_index(),
        x="Fecha",
        y="Asistencia_Dominical_Equipo",
        markers=True
    )
    st.plotly_chart(fig, use_container_width=True)

with colB:
    st.subheader("🏆 Ranking Líderes")
    ranking = df.groupby("NombreCompleto")["Cumplio_Programacion"].mean().reset_index()
    ranking = ranking.sort_values("Cumplio_Programacion", ascending=False)

    fig2 = px.bar(
        ranking,
        x="NombreCompleto",
        y="Cumplio_Programacion",
    )
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# ----------------------------
# AVANCE OBJETIVOS
# ----------------------------

st.subheader("🚀 Avance de Objetivos")

if rol == "Líder":
    df_obj = df_obj[df_obj["DNI_Lider"].astype(str) == dni_input]

avance_obj = df_obj.groupby("ObjetivoID")["Avance"].sum().reset_index()

fig3 = px.bar(
    avance_obj,
    x="ObjetivoID",
    y="Avance",
)

st.plotly_chart(fig3, use_container_width=True)

st.markdown("---")

st.dataframe(df)
