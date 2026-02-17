import streamlit as st
import pandas as pd
from datetime import datetime

# --------------------------------------------------
# CONFIGURACIÓN GENERAL
# --------------------------------------------------

st.set_page_config(page_title="Dashboard IELA", layout="wide")

SPREADSHEET_ID = "1Q4UuncnykLJZrODE_Vwv-_WvCo7LWBNmbhnnPyb1Dt4"

# --------------------------------------------------
# ESTILO DARK PROFESIONAL
# --------------------------------------------------

st.markdown("""
<style>
body {
    background-color: #0F172A;
    color: #F1F5F9;
}
.main {
    background-color: #0F172A;
}
.card {
    background-color: #1E293B;
    padding: 20px;
    border-radius: 15px;
    box-shadow: 0px 4px 15px rgba(0,0,0,0.4);
}
.metric-title {
    font-size: 14px;
    color: #94A3B8;
}
.metric-value {
    font-size: 28px;
    font-weight: bold;
}
.progress-container {
    background-color: #334155;
    border-radius: 10px;
    height: 12px;
}
.progress-bar {
    height: 12px;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# FUNCION PARA LEER GOOGLE SHEETS PUBLICO
# --------------------------------------------------

def load_sheet(sheet_name):
    url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    return pd.read_csv(url)

# --------------------------------------------------
# CARGAR DATA
# --------------------------------------------------

df = load_sheet("BD_ANALISIS_SEMANAL")
df_obj = load_sheet("OBJETIVOS_DEL_LIDER")
df_event = load_sheet("EVENTOS_ESPIRITUALES")
df_lideres = load_sheet("BD_LIDERES")

# NORMALIZAR DNIs COMO TEXTO
df["DNI_Lider"] = df["DNI_Lider"].astype(str).str.strip()
df_lideres["DNI_Lider"] = df_lideres["DNI_Lider"].astype(str).str.strip()
df_obj["DNI_Lider"] = df_obj["DNI_Lider"].astype(str).str.strip()

# --------------------------------------------------
# LOGIN
# --------------------------------------------------

st.sidebar.title("Acceso")
rol = st.sidebar.selectbox("Selecciona tu rol", ["Líder", "Supervisor"])

dni = None

if rol == "Líder":
    dni = st.sidebar.text_input("Ingresa tu DNI")
else:
    password = st.sidebar.text_input("Contraseña Supervisor", type="password")
    if password == "INTIMOSIELA2026":
        dni = st.sidebar.selectbox("Selecciona líder", df_lideres["DNI_Lider"])
    else:
        st.stop()

# --------------------------------------------------
# FILTRO FECHA
# --------------------------------------------------

st.sidebar.title("Filtros")
fecha_inicio = st.sidebar.date_input("Desde", datetime(2026,1,1))
fecha_fin = st.sidebar.date_input("Hasta", datetime.now())

# --------------------------------------------------
# PROCESAMIENTO PRINCIPAL
# --------------------------------------------------

if dni:

    dni = str(dni).strip()

    # Buscar información del líder
    fila = df_lideres[df_lideres["DNI_Lider"] == dni]

    if fila.empty:
        st.error("DNI no encontrado en BD_LIDERES")
        st.stop()

    info = fila.iloc[0]

    # Filtrar registros
    df["Fecha"] = pd.to_datetime(df["Fecha"])
    df_filtrado = df[
        (df["DNI_Lider"] == dni) &
        (df["Fecha"] >= pd.to_datetime(fecha_inicio)) &
        (df["Fecha"] <= pd.to_datetime(fecha_fin))
    ]

    # --------------------------------------------------
    # HEADER
    # --------------------------------------------------

    st.markdown(f"""
    <h1 style='color:#F1F5F9;'>Dashboard de Liderazgo</h1>
    <p style='color:#94A3B8;'>
    {info["NombreCompleto"]} | {info["EntidadTipo"]} | {info["Proceso"]}
    </p>
    """, unsafe_allow_html=True)

    # --------------------------------------------------
    # KPIS PRINCIPALES
    # --------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    asistencia = df_filtrado["Asistencia_Total"].sum() if "Asistencia_Total" in df_filtrado else 0
    eventos = df_filtrado["Evento_Realizado"].sum() if "Evento_Realizado" in df_filtrado else 0
    reuniones = df_filtrado["Reunion_Realizada"].sum() if "Reunion_Realizada" in df_filtrado else 0
    convertidos = df_filtrado["Conversiones"].sum() if "Conversiones" in df_filtrado else 0

    with col1:
        st.markdown(f"<div class='card'><div class='metric-title'>Asistencia Total</div><div class='metric-value'>{int(asistencia)}</div></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='card'><div class='metric-title'>Eventos Realizados</div><div class='metric-value'>{int(eventos)}</div></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='card'><div class='metric-title'>Reuniones</div><div class='metric-value'>{int(reuniones)}</div></div>", unsafe_allow_html=True)
    with col4:
        st.markdown(f"<div class='card'><div class='metric-title'>Convertidos</div><div class='metric-value'>{int(convertidos)}</div></div>", unsafe_allow_html=True)

    st.markdown("---")

    # --------------------------------------------------
    # OBJETIVOS
    # --------------------------------------------------

    st.subheader("Avance de Objetivos")

    objetivos = df_obj[df_obj["DNI_Lider"] == dni]

    for _, row in objetivos.iterrows():

        meta = row["MetaAnual"] if "MetaAnual" in row else 0
        ejecutado = df_filtrado["Avance"].sum() if "Avance" in df_filtrado else 0

        porcentaje = 0
        if meta > 0:
            porcentaje = min(int((ejecutado/meta)*100), 100)

        if porcentaje >= 80:
            color = "#10B981"
        elif porcentaje >= 50:
            color = "#F59E0B"
        else:
            color = "#EF4444"

        st.markdown(f"""
        <div class='card'>
            <div class='metric-title'>{row.get("NombreObjetivo","Objetivo")}</div>
            <div class='progress-container'>
                <div class='progress-bar' style='width:{porcentaje}%; background:{color};'></div>
            </div>
            <div style='margin-top:8px'>{porcentaje}%</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # --------------------------------------------------
    # TENDENCIA ASISTENCIA
    # --------------------------------------------------

    st.subheader("Tendencia Asistencia")

    if "Asistencia_Total" in df_filtrado:
        grafico = df_filtrado.set_index("Fecha")["Asistencia_Total"]
        st.line_chart(grafico)
