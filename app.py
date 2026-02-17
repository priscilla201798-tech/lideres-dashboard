import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------
# CONFIGURACIÓN GENERAL
# -----------------------------

st.set_page_config(
    page_title="Dashboard de Líderes",
    page_icon="📊",
    layout="wide"
)

# -----------------------------
# ESTILO PROFESIONAL DARK
# -----------------------------

st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background-color: #0F172A;
}
[data-testid="stSidebar"] {
    background-color: #111827;
}
h1, h2, h3, h4, h5 {
    color: #F1F5F9;
}
.metric-card {
    background-color: #1E293B;
    padding: 20px;
    border-radius: 15px;
    box-shadow: 0 0 20px rgba(99,102,241,0.3);
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# CARGA DE DATOS
# -----------------------------

SHEET_ID = "1Q4UuncnykLJZrODE_Vwv-_WvCo7LWBNmbhnnPyb1Dt4"
SHEET_NAME = "BD_ANALISIS_SEMANAL"

url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}"

df = pd.read_csv(url)

df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")

# -----------------------------
# SIDEBAR – LOGIN
# -----------------------------

st.sidebar.title("🔐 Acceso")

rol = st.sidebar.selectbox("Selecciona tu rol", ["Líder", "Supervisor"])

dni_input = st.sidebar.text_input("Ingresa tu DNI")

st.sidebar.markdown("---")

fecha_inicio = st.sidebar.date_input("Desde", df["Fecha"].min())
fecha_fin = st.sidebar.date_input("Hasta", df["Fecha"].max())

# -----------------------------
# FILTROS
# -----------------------------

df = df[(df["Fecha"] >= pd.to_datetime(fecha_inicio)) &
        (df["Fecha"] <= pd.to_datetime(fecha_fin))]

if rol == "Líder":
    df = df[df["DNI_Lider"].astype(str) == dni_input]

# -----------------------------
# VALIDACIÓN LOGIN
# -----------------------------

if rol == "Líder" and dni_input == "":
    st.warning("Ingresa tu DNI para continuar.")
    st.stop()

if rol == "Líder" and df.empty:
    st.error("No se encontraron registros para este DNI.")
    st.stop()

# -----------------------------
# TÍTULO
# -----------------------------

st.title("📊 Dashboard Ejecutivo de Líderes")

# -----------------------------
# KPIs
# -----------------------------

total_asistencia = df["Asistencia_Dominical_Equipo"].sum()

total_eventos = df["Evento_Realizado"].sum()

total_reuniones = df["Reunion_Realizada"].sum()

total_programacion = df["Cumplio_Programacion"].sum()
total_registros = len(df)

if total_registros > 0:
    cumplimiento = round((total_programacion / total_registros) * 100, 1)
else:
    cumplimiento = 0

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <h4>👥 Asistencia Total</h4>
        <h2>{int(total_asistencia)}</h2>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <h4>🔥 Eventos Espirituales</h4>
        <h2>{int(total_eventos)}</h2>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <h4>📅 Reuniones</h4>
        <h2>{int(total_reuniones)}</h2>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <h4>🎯 Cumplimiento</h4>
        <h2>{cumplimiento}%</h2>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# -----------------------------
# GRÁFICOS
# -----------------------------

colA, colB = st.columns(2)

with colA:
    st.subheader("📈 Tendencia de Asistencia")
    asistencia_por_fecha = df.groupby("Fecha")["Asistencia_Dominical_Equipo"].sum().reset_index()
    fig1 = px.line(asistencia_por_fecha,
                   x="Fecha",
                   y="Asistencia_Dominical_Equipo",
                   markers=True)
    fig1.update_layout(template="plotly_dark")
    st.plotly_chart(fig1, use_container_width=True)

with colB:
    st.subheader("🏆 Ranking Líderes")
    ranking = df.groupby("NombreCompleto")["Cumplio_Programacion"].sum().reset_index()
    fig2 = px.bar(ranking,
                  x="NombreCompleto",
                  y="Cumplio_Programacion")
    fig2.update_layout(template="plotly_dark")
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# -----------------------------
# TABLA DETALLE
# -----------------------------

st.subheader("📋 Detalle de Registros")
st.dataframe(df.sort_values("Fecha", ascending=False), use_container_width=True)
