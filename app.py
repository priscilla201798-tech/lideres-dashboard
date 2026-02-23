import streamlit as st
import pandas as pd
import json

st.set_page_config(layout="wide")

# 🔹 TU GOOGLE SHEET
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

        # RESUMEN
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

        # EVENTOS
        if data.get("¿Esta semana se realizó algún evento espiritual?") == "Sí":
            eventos.append({
                "Fecha": fecha_dt,
                "Año": año,
                "Mes": mes,
                "DNI_Lider": dni,
                "Tipo_Evento": data.get("¿Qué tipo de evento espiritual se realizó?", "").upper(),
                "Participantes": int(data.get("¿Cuántas personas participaron?", 0) or 0)
            })

        # OBJETIVOS
        if data.get("¿Deseas registrar avance en alguno de tus objetivos esta semana?") == "Sí":
            objetivos.append({
                "Fecha": fecha_dt,
                "Año": año,
                "Mes": mes,
                "DNI_Lider": dni,
                "Objetivo": data.get("¿En qué objetivo deseas registrar avance?", ""),
                "Avance": int(data.get("¿Cuánto avanzaste en este objetivo?", 0) or 0)
            })

        # ASISTENCIA
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

# 🔹 EJECUCIÓN
df = cargar_data()
df_resumen, df_eventos, df_objetivos, df_asistencia = aplanar_registros(df)

st.title("📊 Dashboard Ministerial")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Convertidos", df_resumen["Convertidos"].sum())
col2.metric("Reconciliados", df_resumen["Reconciliados"].sum())
col3.metric("Total Asistentes", df_resumen["Asistentes"].sum())
col4.metric("Total Ofrenda", round(df_resumen["Ofrenda"].sum(),2))

st.divider()

st.subheader("Eventos por mes")
if not df_eventos.empty:
    st.bar_chart(df_eventos.groupby("Mes")["Tipo_Evento"].count())

st.subheader("Avance por objetivo")
if not df_objetivos.empty:
    st.bar_chart(df_objetivos.groupby("Objetivo")["Avance"].sum())

st.subheader("Asistencia del equipo")
if not df_asistencia.empty:
    st.bar_chart(df_asistencia.groupby("Persona").size())
