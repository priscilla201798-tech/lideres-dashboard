import streamlit as st
import pandas as pd
import json
import plotly.express as px

st.set_page_config(layout="wide")

# ==============================
# 🎨 COLORES PROFESIONALES
# ==============================

AZUL = "#0B3C5D"
AZUL2 = "#1D4E89"
VERDE = "#1E8449"
ROJO = "#C0392B"
GRIS = "#6B7280"

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
        dni = extraer_dni(row["Key"]).zfill(8)
        mes = fecha.month

        try:
            data = json.loads(row["RespuestasJSON"])
        except:
            continue

        resumen.append({
            "Fecha": fecha,
            "Mes": mes,
            "DNI": dni,
            "Convertidos": int(data.get("¿Cuántas personas aceptaron a Cristo?", 0) or 0),
            "Reconciliados": int(data.get("¿Cuántas personas se reconciliaron con Cristo?", 0) or 0),
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
# CARGAR DATA
# ==============================

df_raw = cargar_sheet(GID_REGISTROS)
df_plan_eventos = cargar_sheet(GID_EVENTOS)
df_plan_obj = cargar_sheet(GID_OBJETIVOS)

df_resumen, df_eventos, df_objetivos, df_asistencia = aplanar(df_raw)

# ==============================
# SIDEBAR + LOGIN
# ==============================

st.sidebar.markdown("""
<div style="font-size:18px; font-weight:600; line-height:1.4;">
IGLESIA EVANGÉLICA<br>
DE LIBERACIÓN Y AVIVAMIENTO
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")

if "dni" not in st.session_state:
    st.session_state.dni = None

dni_disponibles = df_resumen["DNI"].unique()

if st.session_state.dni is None:

    dni_input = st.sidebar.text_input("Ingrese su DNI")

    if st.sidebar.button("Ingresar"):
        if dni_input.strip().zfill(8) in dni_disponibles:
            st.session_state.dni = dni_input.strip().zfill(8)
            st.rerun()
        else:
            st.sidebar.error("DNI no encontrado")

    st.stop()

dni = st.session_state.dni

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
df_plan_eventos["DNI_Lider"] = df_plan_eventos["DNI_Lider"].astype(str).str.zfill(8)
df_plan_obj["DNI_Lider"] = df_plan_obj["DNI_Lider"].astype(str).str.zfill(8)

df_plan_eventos = df_plan_eventos[df_plan_eventos["DNI_Lider"] == dni]
df_plan_obj = df_plan_obj[df_plan_obj["DNI_Lider"] == dni]

st.title("📊 Dashboard Institucional")

# ==============================
# 🔝 TARJETAS SUPERIORES
# ==============================

c1, c2, c3, c4, c5 = st.columns(5)

c1.metric("✨ Convertidos", df_resumen["Convertidos"].sum())
c2.metric("🤝 Reconciliados", df_resumen["Reconciliados"].sum())
c3.metric("💰 Ofrendas", round(df_resumen["Ofrenda"].sum(),2))
c4.metric("📅 Reuniones", len(df_resumen))
c5.metric("🔥 Eventos Ejecutados", len(df_eventos))

st.divider()

# ==============================
# PARTE 1 – ASISTENCIA DOMINICAL
# ==============================

st.subheader("📊 Asistencia Dominical")

if not df_asistencia.empty:

    asistencia_equipo = (
        df_asistencia
        .groupby("Equipo")
        .size()
        .reset_index(name="Domingos_Asistidos")
        .sort_values("Domingos_Asistidos", ascending=False)
    )

    fig_asistencia = px.bar(
        asistencia_equipo,
        x="Equipo",
        y="Domingos_Asistidos",
        text="Domingos_Asistidos",
        color="Domingos_Asistidos",
        color_continuous_scale="Blues"
    )

    fig_asistencia.update_layout(
        xaxis_title="Equipos",
        yaxis_title="Cantidad de Domingos Asistidos",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white")
    )

    fig_asistencia.update_traces(textposition="outside")

    st.plotly_chart(fig_asistencia, use_container_width=True)
    
# ==============================
# PARTE 2 – EVENTOS ESPIRITUALES
# ==============================

st.subheader("📅 Cumplimiento Anual de Eventos")

meses = {
1:"Enero",2:"Febrero",3:"Marzo",4:"Abril",
5:"Mayo",6:"Junio",7:"Julio",8:"Agosto",
9:"Septiembre",10:"Octubre",11:"Noviembre",12:"Diciembre"
}

tabla = []

for mes in range(1,13):

    fila = {"Mes": meses[mes]}

    for tipo in ["AYUNO", "VIGILIA"]:

        if tipo == "AYUNO":
            prog = df_plan_eventos[df_plan_eventos["Mes"] == meses[mes]]["Ayunos_Programados"].sum()
        else:
            prog = df_plan_eventos[df_plan_eventos["Mes"] == meses[mes]]["Vigilias_Programadas"].sum()

        ejec = df_eventos[
            (df_eventos["Mes"] == mes) &
            (df_eventos["Tipo"] == tipo)
        ].shape[0]

        fila[tipo] = f"{ejec}/{prog}"

    tabla.append(fila)

df_tabla = pd.DataFrame(tabla)

def color(val):
    ejec, prog = val.split("/")
    if int(prog) == 0:
        return ""
    return "background-color:#1E8449; color:white;" if int(ejec) >= int(prog) \
        else "background-color:#C0392B; color:white;"

styled = df_tabla.style.applymap(color, subset=["AYUNO","VIGILIA"])

st.write(styled)
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
