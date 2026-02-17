import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# ---------------------------
# CONFIGURACIÓN INICIAL
# ---------------------------
st.set_page_config(page_title="Dashboard IELA", layout="wide")

SPREADSHEET_ID = "1Q4UuncnykLJZrODE_Vwv-_WvCo7LWBNmbhnnPyb1Dt4"

def load_sheet(sheet_name):
    url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    return pd.read_csv(url)

df_analisis = load_sheet("BD_ANALISIS_SEMANAL")
df_obj = load_sheet("BD_OBJETIVOS_ANALISIS")
df_eventos_prog = load_sheet("EVENTOS_ESPIRITUALES")
df_obj_prog = load_sheet("OBJETIVOS_DEL_LIDER")
df_lideres = load_sheet("BD_LIDERES")

# ---------------------------
# LIMPIEZA DNI
# ---------------------------
df_lideres["DNI_Lider"] = df_lideres["DNI_Lider"].astype(str).str.zfill(8)
df_analisis["DNI_Lider"] = df_analisis["DNI_Lider"].astype(str).str.zfill(8)
df_obj["DNI_Lider"] = df_obj["DNI_Lider"].astype(str).str.zfill(8)

# ---------------------------
# ESTILO GENERAL
# ---------------------------
st.markdown("""
<style>
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0b1e3d, #07142a);
}

.sidebar-title {
    color: #f4c430;
    font-weight: 700;
    font-size: 18px;
}

.sidebar-text {
    color: white;
    font-weight: 600;
}

.main-title {
    font-size: 32px;
    font-weight: 700;
    color: #0b1e3d;
}

.tarjeta {
    background: #142850;
    padding: 25px;
    border-radius: 15px;
    text-align: center;
    color: white;
    box-shadow: 0px 6px 18px rgba(0,0,0,0.4);
    height: 140px;
    display: flex;
    flex-direction: column;
    justify-content: center;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------
# SIDEBAR
# ---------------------------
st.sidebar.image("logo.png")

st.sidebar.markdown("""
<div class='sidebar-title'>
Iglesia Evangélica de Liberación y Avivamiento
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("<br>", unsafe_allow_html=True)

rol = st.sidebar.selectbox("Rol", ["Líder", "Supervisor"])
dni = st.sidebar.text_input("DNI")

fecha_inicio = st.sidebar.date_input("Desde")
fecha_fin = st.sidebar.date_input("Hasta")

# ---------------------------
# VALIDACIÓN DNI
# ---------------------------
if dni:
    dni = dni.zfill(8)
    lider = df_lideres[df_lideres["DNI_Lider"] == dni]

    if lider.empty:
        st.error("DNI no encontrado")
        st.stop()
else:
    st.stop()

# ---------------------------
# DATOS DEL LÍDER
# ---------------------------
nombre = lider.iloc[0]["NombreCompleto"]
ministerio = lider.iloc[0]["EntidadTipo"]
proceso = lider.iloc[0]["Proceso"]
equipo = lider.iloc[0]["EntidadNombre"]

# ---------------------------
# FILTROS
# ---------------------------
df_filtrado = df_analisis[df_analisis["DNI_Lider"] == dni]

if not df_filtrado.empty:
    df_filtrado["Fecha"] = pd.to_datetime(df_filtrado["Fecha"])
    df_filtrado = df_filtrado[
        (df_filtrado["Fecha"] >= pd.to_datetime(fecha_inicio)) &
        (df_filtrado["Fecha"] <= pd.to_datetime(fecha_fin))
    ]

# ---------------------------
# MÉTRICAS
# ---------------------------
asistencia_total = df_filtrado["Asistencia_Dominical_Equipo"].sum()
reuniones = df_filtrado["Reunion_Realizada"].sum()
eventos_realizados = df_filtrado["Evento_Realizado"].sum()

# Cumplimiento objetivos
obj_prog = df_obj_prog[df_obj_prog["DNI_Lider"] == dni]
obj_ejec = df_obj[df_obj["DNI_Lider"] == dni]

meta_total = obj_prog["Meta_Anual"].sum() if not obj_prog.empty else 0
ejecutado_total = obj_ejec["Avance"].sum() if not obj_ejec.empty else 0

cumplimiento = int((ejecutado_total / meta_total) * 100) if meta_total > 0 else 0

# ---------------------------
# TÍTULO
# ---------------------------
st.markdown("<div class='main-title'>Dashboard de Líderes</div>", unsafe_allow_html=True)

st.markdown(f"""
<div style="
background:#0f2550;
padding:20px;
border-radius:12px;
color:white;
margin-top:20px;
margin-bottom:30px;
">
<b>Líder:</b> {nombre} |
<b>Ministerio:</b> {ministerio} |
<b>Proceso:</b> {proceso} |
<b>Equipo:</b> {equipo}
</div>
""", unsafe_allow_html=True)

# ---------------------------
# TARJETAS
# ---------------------------
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"<div class='tarjeta'>Asistencia Total<br><span style='font-size:32px'>{asistencia_total}</span></div>", unsafe_allow_html=True)

with col2:
    st.markdown(f"<div class='tarjeta'>Eventos Espirituales<br><span style='font-size:32px'>{eventos_realizados}</span></div>", unsafe_allow_html=True)

with col3:
    st.markdown(f"<div class='tarjeta'>Reuniones Realizadas<br><span style='font-size:32px'>{reuniones}</span></div>", unsafe_allow_html=True)

with col4:
    st.markdown(f"<div class='tarjeta'>% Cumplimiento<br><span style='font-size:32px'>{cumplimiento}%</span></div>", unsafe_allow_html=True)

# ---------------------------
# GRÁFICO ASISTENCIA
# ---------------------------
st.subheader("Asistencia Dominical")

fig = px.bar(
    df_filtrado,
    x="EntidadNombre",
    y="Asistencia_Dominical_Equipo",
    color_discrete_sequence=["#142850"]
)

st.plotly_chart(fig, use_container_width=True)

# ---------------------------
# OBJETIVOS
# ---------------------------
st.subheader("Avance de Objetivos")

for _, row in obj_prog.iterrows():
    obj_id = row["ObjetivoID"]
    meta = row["Meta_Anual"]

    ejec = obj_ejec[obj_ejec["ObjetivoID"] == obj_id]["Avance"].sum()
    porcentaje = int((ejec / meta) * 100) if meta > 0 else 0

    st.markdown(f"""
    <div style="margin-bottom:20px;">
        <b>{obj_id}</b>
        <div style="background:#ddd; border-radius:10px; height:20px;">
            <div style="width:{porcentaje}%; background:#f4c430; height:20px; border-radius:10px;"></div>
        </div>
        <div>{porcentaje}%</div>
    </div>
    """, unsafe_allow_html=True)

# ---------------------------
# EVENTOS PROGRAMADOS VS EJECUTADOS
# ---------------------------
st.subheader("Eventos Espirituales")

eventos_prog = df_eventos_prog[df_eventos_prog["DNI_Lider"] == dni]["Meta_Anual"].sum()
eventos_ejec = eventos_realizados

fig2 = px.bar(
    x=["Programados", "Ejecutados"],
    y=[eventos_prog, eventos_ejec],
    color_discrete_sequence=["#0b1e3d"]
)

st.plotly_chart(fig2, use_container_width=True)
