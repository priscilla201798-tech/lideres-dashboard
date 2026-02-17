import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Dashboard IELA", layout="wide")

SPREADSHEET_ID = "1Q4UuncnykLJZrODE_Vwv-_WvCo7LWBNmbhnnPyb1Dt4"

# -----------------------------
# ESTILO MODERNO OSCURO
# -----------------------------
st.markdown("""
<style>
body { background-color: #0F172A; color: #F1F5F9; }
.card {
    background-color: #1E293B;
    padding: 20px;
    border-radius: 12px;
    margin-bottom: 10px;
}
.metric-title { color: #94A3B8; font-size: 14px; }
.metric-value { font-size: 26px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# CARGAR GOOGLE SHEETS
# -----------------------------
def load_sheet(name):
    url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet={name}"
    return pd.read_csv(url)

df = load_sheet("BD_ANALISIS_SEMANAL")
df_lideres = load_sheet("BD_LIDERES")

# Normalizar DNI
df["DNI_Lider"] = df["DNI_Lider"].astype(str).str.replace("'", "").str.strip()
df_lideres["DNI_Lider"] = df_lideres["DNI_Lider"].astype(str).str.replace("'", "").str.strip()

# -----------------------------
# LOGIN
# -----------------------------
st.sidebar.title("Acceso")
rol = st.sidebar.selectbox("Rol", ["Líder", "Supervisor"])

dni = None

if rol == "Líder":
    dni = st.sidebar.text_input("Ingresa tu DNI")
else:
    password = st.sidebar.text_input("Contraseña Supervisor", type="password")
    if password == "INTIMOSIELA2026":
        dni = st.sidebar.selectbox("Selecciona líder", df_lideres["DNI_Lider"].unique())
    else:
        st.stop()

# -----------------------------
# FILTRO FECHA
# -----------------------------
st.sidebar.title("Periodo")
fecha_inicio = st.sidebar.date_input("Desde", datetime(2026,1,1))
fecha_fin = st.sidebar.date_input("Hasta", datetime.now())

# -----------------------------
# CONTENIDO PRINCIPAL
# -----------------------------
if dni:

    dni = str(dni).strip()

    # Buscar líder
    fila = df_lideres[df_lideres["DNI_Lider"] == dni]

    if fila.empty:
        st.warning("DNI no encontrado en BD_LIDERES")
        st.stop()

    info = fila.iloc[0]

    # Filtrar datos
    df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
    df_filtrado = df[
        (df["DNI_Lider"] == dni) &
        (df["Fecha"] >= pd.to_datetime(fecha_inicio)) &
        (df["Fecha"] <= pd.to_datetime(fecha_fin))
    ]

    st.title("Dashboard de Liderazgo")

    st.markdown(f"""
    <p style='color:#94A3B8'>
    <strong>{info.get("NombreCompleto","")}</strong><br>
    {info.get("EntidadTipo","")} | {info.get("Proceso","")} | {info.get("EntidadNombre","")}
    </p>
    """, unsafe_allow_html=True)

    if df_filtrado.empty:
        st.info("No hay registros en el periodo seleccionado.")
        st.stop()

    # KPIs
    col1, col2, col3 = st.columns(3)
    col4, col5, col6 = st.columns(3)

    asistencia = df_filtrado.get("Asistencia_Total", pd.Series([0])).sum()
    reuniones = df_filtrado.get("Reunion_Realizada", pd.Series([0])).sum()
    eventos = df_filtrado.get("Evento_Realizado", pd.Series([0])).sum()
    convertidos = df_filtrado.get("Conversiones", pd.Series([0])).sum()
    visitas = df_filtrado.get("Visitas", pd.Series([0])).sum()
    derivados = df_filtrado.get("Derivados_Escuela", pd.Series([0])).sum()

    with col1:
        st.markdown(f"<div class='card'><div class='metric-title'>Asistencia Total</div><div class='metric-value'>{int(asistencia)}</div></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='card'><div class='metric-title'>Reuniones</div><div class='metric-value'>{int(reuniones)}</div></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='card'><div class='metric-title'>Eventos</div><div class='metric-value'>{int(eventos)}</div></div>", unsafe_allow_html=True)

    with col4:
        st.markdown(f"<div class='card'><div class='metric-title'>Convertidos</div><div class='metric-value'>{int(convertidos)}</div></div>", unsafe_allow_html=True)
    with col5:
        st.markdown(f"<div class='card'><div class='metric-title'>Visitas</div><div class='metric-value'>{int(visitas)}</div></div>", unsafe_allow_html=True)
    with col6:
        st.markdown(f"<div class='card'><div class='metric-title'>Derivados Escuela</div><div class='metric-value'>{int(derivados)}</div></div>", unsafe_allow_html=True)
