import streamlit as st
import pandas as pd
import json
import plotly.express as px
from datetime import datetime

st.set_page_config(layout="wide")

# ==============================
# 🎨 ESTILO INSTITUCIONAL
# ==============================

st.markdown("""
<style>
.metric-container {
    background-color: #0F2D52;
    padding: 15px;
    border-radius: 10px;
    color: white;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# ==============================
# CONFIG GOOGLE SHEETS
# ==============================

SHEET_ID = "1Q4UuncnykLJZrODE_Vwv-_WvCo7LWBNmbhnnPyb1Dt4"
GID_REGISTROS = "632350714"
GID_EVENTOS = "1679434742"
GID_OBJETIVOS = "236814605"

@st.cache_data
def cargar_sheet(gid):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={gid}"
    return pd.read_csv(url)

def extraer_dni_desde_key(key):
    return str(key).split("_")[0]

def aplanar_registros(df):

    resumen, eventos, objetivos, asistencia = [], [], [], []

    for _, row in df.iterrows():

        fecha = pd.to_datetime(row["Fecha"])
        key = row["Key"]
        dni = extraer_dni_desde_key(key)

        try:
            data = json.loads(row["RespuestasJSON"])
        except:
            continue

        año = fecha.year
        mes = fecha.month

        resumen.append({
            "Fecha": fecha,
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
                "Fecha": fecha,
                "Año": año,
                "Mes": mes,
                "DNI_Lider": dni,
                "Tipo_Evento": data.get("¿Qué tipo de evento espiritual se realizó?", "").upper(),
                "Participantes": int(data.get("¿Cuántas personas participaron?", 0) or 0)
            })

        if data.get("¿Deseas registrar avance en alguno de tus objetivos esta semana?") == "Sí":
            objetivos.append({
                "Fecha": fecha,
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
                "Fecha": fecha,
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

df_raw = cargar_sheet(GID_REGISTROS)
df_plan_eventos = cargar_sheet(GID_EVENTOS)
df_plan_obj = cargar_sheet(GID_OBJETIVOS)

df_resumen, df_eventos, df_objetivos, df_asistencia = aplanar_registros(df_raw)

if "dni_login" not in st.session_state:
    st.session_state.dni_login = None

if st.session_state.dni_login is None:

    st.title("🔐 Acceso Líder")
    dni_input = st.text_input("Ingrese su DNI")

    if st.button("Ingresar"):
        if dni_input in df_resumen["DNI_Lider"].unique():
            st.session_state.dni_login = dni_input
            st.rerun()
        else:
            st.error("DNI no encontrado")

    st.stop()

dni = st.session_state.dni_login

# ==============================
# FILTROS DE / HASTA
# ==============================

st.sidebar.success(f"DNI: {dni}")

fecha_min = df_resumen["Fecha"].min()
fecha_max = df_resumen["Fecha"].max()

desde = st.sidebar.date_input("Desde", fecha_min)
hasta = st.sidebar.date_input("Hasta", fecha_max)

df_resumen = df_resumen[(df_resumen["DNI_Lider"] == dni) &
                        (df_resumen["Fecha"] >= pd.to_datetime(desde)) &
                        (df_resumen["Fecha"] <= pd.to_datetime(hasta))]

df_eventos = df_eventos[(df_eventos["DNI_Lider"] == dni) &
                        (df_eventos["Fecha"] >= pd.to_datetime(desde)) &
                        (df_eventos["Fecha"] <= pd.to_datetime(hasta))]

df_objetivos = df_objetivos[df_objetivos["DNI_Lider"] == dni]
df_plan_eventos = df_plan_eventos[df_plan_eventos["DNI_Lider"] == int(dni)]
df_plan_obj = df_plan_obj[df_plan_obj["DNI_Lider"] == int(dni)]

# ==============================
# TARJETAS
# ==============================

st.title("📊 Dashboard Institucional")

col1, col2, col3, col4 = st.columns(4)

col1.metric("✨ Convertidos", df_resumen["Convertidos"].sum())
col2.metric("🤝 Reconciliados", df_resumen["Reconciliados"].sum())
col3.metric("💰 Ofrendas", round(df_resumen["Ofrenda"].sum(),2))
col4.metric("📅 Reuniones", len(df_resumen))

st.divider()

# ==============================
# MATRIZ EVENTOS
# ==============================

meses = range(1,13)
tabla = []

for mes in meses:
    fila = {"Mes": mes}

    for tipo in ["AYUNO","VIGILIA"]:

        if tipo == "AYUNO":
            prog = df_plan_eventos[df_plan_eventos["Mes"] == mes]["Ayunos_Programados"].sum()
        else:
            prog = df_plan_eventos[df_plan_eventos["Mes"] == mes]["Vigilias_Programadas"].sum()

        ejec = df_eventos[(df_eventos["Mes"] == mes) &
                          (df_eventos["Tipo_Evento"] == tipo)].shape[0]

        fila[tipo] = f"{ejec}/{prog}"

    tabla.append(fila)

df_tabla = pd.DataFrame(tabla)

def color(val):
    ejec, prog = val.split("/")
    if int(prog) == 0:
        return ""
    return "background-color: #1B8A5A; color: white;" if int(ejec) >= int(prog) \
        else "background-color: #C0392B; color: white;"

st.subheader("📅 Cumplimiento Eventos")
st.dataframe(df_tabla.style.applymap(color, subset=["AYUNO","VIGILIA"]),
             height=350)

# ==============================
# LINEA PARTICIPANTES
# ==============================

if not df_eventos.empty:
    fig = px.line(
        df_eventos.groupby(["Mes","Tipo_Evento"])["Participantes"].sum().reset_index(),
        x="Mes",
        y="Participantes",
        color="Tipo_Evento",
        markers=True,
        color_discrete_sequence=["#0F2D52","#1B8A5A"]
    )
    st.plotly_chart(fig, use_container_width=True)

# ==============================
# ASISTENCIA DOMINICAL
# ==============================

if not df_asistencia.empty:
    asistencia_persona = df_asistencia.groupby("Persona").size().reset_index(name="Asistencias")

    fig2 = px.bar(
        asistencia_persona,
        x="Persona",
        y="Asistencias",
        color_discrete_sequence=["#0F2D52"]
    )

    st.plotly_chart(fig2, use_container_width=True)

# ==============================
# OBJETIVOS
# ==============================

st.subheader("🎯 Objetivos Estratégicos")

for _, row in df_plan_obj.iterrows():

    objetivo_id = row["ObjetivoID"]
    nombre = row["NombreObjetivo"]
    meta = row["MetaAnual"]

    ejecutado = df_objetivos[df_objetivos["Objetivo"].str.contains(objetivo_id, na=False)]["Avance"].sum()

    progreso = min(ejecutado / meta if meta > 0 else 0, 1)

    st.write(f"**{objetivo_id} - {nombre}**  ({ejecutado}/{meta})")
    st.progress(progreso)
