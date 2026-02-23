import streamlit as st
import pandas as pd
import json
import plotly.express as px

st.set_page_config(layout="wide")

# ==============================
# 🎨 COLORES INSTITUCIONALES
# ==============================

AZUL = "#0F2D52"
VERDE = "#1B8A5A"
ROJO = "#C0392B"

st.markdown(f"""
<style>
section[data-testid="stSidebar"] {{
    background-color: {AZUL};
    color: white;
}}
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

def extraer_dni(key):
    return str(key).split("_")[0]

def aplanar(df):

    resumen, eventos, objetivos, asistencia = [], [], [], []

    for _, row in df.iterrows():

        fecha = pd.to_datetime(row["Fecha"])
        dni = extraer_dni(row["Key"])

        try:
            data = json.loads(row["RespuestasJSON"])
        except:
            continue

        mes = fecha.month

        resumen.append({
            "Fecha": fecha,
            "Mes": mes,
            "DNI": dni,
            "Convertidos": int(data.get("¿Cuántas personas aceptaron a Cristo?", 0) or 0),
            "Reconciliados": int(data.get("¿Cuántas personas se reconciliaron con Cristo?", 0) or 0),
            "Asistentes": int(data.get("¿Cuántas personas asistieron en total?", 0) or 0),
            "Ofrenda": float(data.get("Monto total de la ofrenda (S/.)", 0) or 0)
        })

        if data.get("¿Esta semana se realizó algún evento espiritual?") == "Sí":
            eventos.append({
                "Mes": mes,
                "DNI": dni,
                "Tipo": data.get("¿Qué tipo de evento espiritual se realizó?", "").upper(),
                "Participantes": int(data.get("¿Cuántas personas participaron?", 0) or 0)
            })

        if data.get("¿Deseas registrar avance en alguno de tus objetivos esta semana?") == "Sí":
            objetivos.append({
                "DNI": dni,
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
                "Mes": mes,
                "DNI": dni,
                "Equipo": persona
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

df_resumen, df_eventos, df_objetivos, df_asistencia = aplanar(df_raw)

if "dni" not in st.session_state:
    st.session_state.dni = None

if st.session_state.dni is None:
    st.title("🔐 Acceso Líder")
    dni_input = st.text_input("Ingrese su DNI")

    if st.button("Ingresar"):
        if dni_input in df_resumen["DNI"].unique():
            st.session_state.dni = dni_input
            st.rerun()
        else:
            st.error("DNI no encontrado")

    st.stop()

dni = st.session_state.dni

# ==============================
# SIDEBAR
# ==============================

st.sidebar.title("IGLESIA EVANGÉLICA")
st.sidebar.write("DE LIBERACIÓN Y AVIVAMIENTO")
st.sidebar.markdown("---")
st.sidebar.success(f"DNI: {dni}")

if st.sidebar.button("Cerrar sesión"):
    st.session_state.dni = None
    st.rerun()

# ==============================
# FILTRAR
# ==============================

df_resumen = df_resumen[df_resumen["DNI"] == dni]
df_eventos = df_eventos[df_eventos["DNI"] == dni]
df_objetivos = df_objetivos[df_objetivos["DNI"] == dni]
df_asistencia = df_asistencia[df_asistencia["DNI"] == dni]
df_plan_eventos = df_plan_eventos[df_plan_eventos["DNI_Lider"] == int(dni)]
df_plan_obj = df_plan_obj[df_plan_obj["DNI_Lider"] == int(dni)]

# ==============================
# TARJETAS SUPERIORES
# ==============================

st.title("📊 Dashboard Institucional")

c1, c2, c3, c4, c5 = st.columns(5)

c1.metric("✨ Convertidos", df_resumen["Convertidos"].sum())
c2.metric("🤝 Reconciliados", df_resumen["Reconciliados"].sum())
c3.metric("💰 Ofrendas", round(df_resumen["Ofrenda"].sum(),2))
c4.metric("📅 Reuniones", len(df_resumen))
c5.metric("👥 Asistentes", df_resumen["Asistentes"].sum())

st.divider()

# ==============================
# PARTE 1 – ASISTENCIA DOMINICAL
# ==============================

st.subheader("📊 Asistencias Dominicales")

if not df_asistencia.empty:
    asistencia_equipo = df_asistencia.groupby("Equipo").size().reset_index(name="Domingos")

    fig1 = px.bar(
        asistencia_equipo,
        x="Equipo",
        y="Domingos",
        color_discrete_sequence=[AZUL]
    )
    st.plotly_chart(fig1, use_container_width=True)

# ==============================
# PARTE 2 – EVENTOS ESPIRITUALES
# ==============================

st.subheader("📅 Cumplimiento Eventos (Ene-Mar)")

tabla = []

for tipo in ["AYUNO", "VIGILIA"]:

    fila = {"Tipo": tipo}

    for mes in [1,2,3]:

        if tipo == "AYUNO":
            prog = df_plan_eventos[df_plan_eventos["Mes"] == mes]["Ayunos_Programados"].sum()
        else:
            prog = df_plan_eventos[df_plan_eventos["Mes"] == mes]["Vigilias_Programadas"].sum()

        ejec = df_eventos[(df_eventos["Mes"] == mes) &
                          (df_eventos["Tipo"] == tipo)].shape[0]

        fila[f"Mes {mes}"] = f"{ejec}/{prog}"

    tabla.append(fila)

df_tabla = pd.DataFrame(tabla)

def color(val):
    ejec, prog = val.split("/")
    if int(prog) == 0:
        return ""
    return f"background-color: {VERDE}; color: white;" if int(ejec) >= int(prog) \
        else f"background-color: {ROJO}; color: white;"

st.dataframe(df_tabla.style.applymap(color, subset=df_tabla.columns[1:]),
             height=200)

# Línea asistencia eventos
if not df_eventos.empty:
    fig2 = px.line(
        df_eventos.groupby(["Mes","Tipo"])["Participantes"].sum().reset_index(),
        x="Mes",
        y="Participantes",
        color="Tipo",
        markers=True,
        color_discrete_sequence=[AZUL, VERDE]
    )
    st.plotly_chart(fig2, use_container_width=True)

# ==============================
# PARTE 3 – OBJETIVOS
# ==============================

st.subheader("🎯 Objetivos Estratégicos")

for _, row in df_plan_obj.iterrows():

    objetivo = row["ObjetivoID"]
    nombre = row["NombreObjetivo"]
    meta = int(row["MetaAnual"])

    ejecutado = df_objetivos[
        df_objetivos["Objetivo"].str.contains(objetivo, na=False)
    ]["Avance"].sum()

    progreso = min(ejecutado / meta if meta > 0 else 0, 1)

    st.write(f"**{objetivo} - {nombre} ({ejecutado}/{meta})**")
    st.progress(progreso)
