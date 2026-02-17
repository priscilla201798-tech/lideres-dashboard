import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --------------------------------------------------
# CONFIGURACIÓN
# --------------------------------------------------

st.set_page_config(
    page_title="Panel Ejecutivo",
    layout="wide"
)

# --------------------------------------------------
# CSS PROFESIONAL IGLESIA
# --------------------------------------------------

st.markdown("""
<style>

html, body, [data-testid="stAppViewContainer"] {
    background-color: #0b1120;
    color: #f8fafc;
    font-family: 'Segoe UI', sans-serif;
}

[data-testid="stSidebar"] {
    background-color: #111827;
}

h1 {
    font-size: 42px !important;
    font-weight: 600 !important;
    letter-spacing: 1px;
}

h2, h3 {
    font-weight: 500 !important;
}

.card {
    background: linear-gradient(145deg, #111827, #1f2937);
    padding: 25px;
    border-radius: 18px;
    box-shadow: 0 0 25px rgba(99,102,241,0.25);
    text-align: center;
}

.card h3 {
    font-size: 16px;
    opacity: 0.7;
}

.card h1 {
    font-size: 32px;
    margin-top: 10px;
}

.stDataFrame {
    background-color: #111827;
}

</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# DATOS
# --------------------------------------------------

SHEET_ID = "1Q4UuncnykLJZrODE_Vwv-_WvCo7LWBNmbhnnPyb1Dt4"
SHEET_NAME = "BD_ANALISIS_SEMANAL"

url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}"

df = pd.read_csv(url)
df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

st.sidebar.title("ACCESO")

rol = st.sidebar.selectbox("Rol", ["Líder", "Supervisor"])
dni = st.sidebar.text_input("DNI")

st.sidebar.markdown("---")

fecha_inicio = st.sidebar.date_input("Desde", df["Fecha"].min())
fecha_fin = st.sidebar.date_input("Hasta", df["Fecha"].max())

df = df[(df["Fecha"] >= pd.to_datetime(fecha_inicio)) &
        (df["Fecha"] <= pd.to_datetime(fecha_fin))]

if rol == "Líder":
    df = df[df["DNI_Lider"].astype(str) == dni]

if rol == "Líder" and dni == "":
    st.warning("Ingresa tu DNI")
    st.stop()

# --------------------------------------------------
# TITULO
# --------------------------------------------------

st.title("Panel Ejecutivo de Liderazgo")

# --------------------------------------------------
# KPIs
# --------------------------------------------------

total_asistencia = df["Asistencia_Dominical_Equipo"].sum()
total_eventos = df["Evento_Realizado"].sum()
total_reuniones = df["Reunion_Realizada"].sum()

total_registros = len(df)
cumplimiento = 0

if total_registros > 0:
    cumplimiento = round((df["Cumplio_Programacion"].sum() / total_registros) * 100, 1)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="card">
        <h3>Asistencia Total</h3>
        <h1>{int(total_asistencia)}</h1>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="card">
        <h3>Eventos Espirituales</h3>
        <h1>{int(total_eventos)}</h1>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="card">
        <h3>Reuniones Realizadas</h3>
        <h1>{int(total_reuniones)}</h1>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="card">
        <h3>Cumplimiento</h3>
        <h1>{cumplimiento}%</h1>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# --------------------------------------------------
# GRAFICO TENDENCIA
# --------------------------------------------------

st.subheader("Tendencia de Asistencia")

asistencia = df.groupby("Fecha")["Asistencia_Dominical_Equipo"].sum().reset_index()

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=asistencia["Fecha"],
    y=asistencia["Asistencia_Dominical_Equipo"],
    mode='lines+markers',
    line=dict(color="#6366F1", width=4),
    marker=dict(size=8)
))

fig.update_layout(
    plot_bgcolor="#0b1120",
    paper_bgcolor="#0b1120",
    font=dict(color="#f8fafc"),
    xaxis=dict(showgrid=False),
    yaxis=dict(showgrid=True, gridcolor="#1f2937")
)

st.plotly_chart(fig, use_container_width=True)

# --------------------------------------------------
# TABLA
# --------------------------------------------------

st.subheader("Detalle de Registros")

st.dataframe(
    df.sort_values("Fecha", ascending=False),
    use_container_width=True
)
