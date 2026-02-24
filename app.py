import streamlit as st
import pandas as pd
import json
import plotly.express as px

st.set_page_config(
    layout="wide",
    initial_sidebar_state="collapsed"
)

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

@st.cache_data(ttl=120)
def cargar_sheet(gid):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={gid}"
    return pd.read_csv(url)

def extraer_dni(key):
    return str(key).split("_")[0]

def aplanar(df):

    resumen = []
    eventos = []
    objetivos = []
    asistencia = []

    for _, row in df.iterrows():

        try:
            fecha = pd.to_datetime(row["Fecha"])
            mes = fecha.month
            dni = str(row["DNI_Lider"]).strip().zfill(8)
        except:
            continue

        raw_json = row.get("RespuestasJSON", "")

        if not isinstance(raw_json, str) or raw_json.strip() == "":
            continue

        raw_json = raw_json.strip()

        try:
            data = json.loads(raw_json)
        except:
            try:
                data = json.loads(json.loads(raw_json))
            except:
                continue

        # RESUMEN
        resumen.append({
            "Fecha": fecha,
            "Mes": mes,
            "DNI": dni,
            "Convertidos": int(data.get("¿Cuántas personas aceptaron a Cristo?", 0) or 0),
            "Reconciliados": int(data.get("¿Cuántas personas se reconciliaron con Cristo?", 0) or 0),
            "Ofrenda": float(data.get("Monto total de la ofrenda (S/.)", 0) or 0)
        })

        # EVENTOS
        if data.get("¿Esta semana se realizó algún evento espiritual?") == "Sí":
            eventos.append({
                "Mes": mes,
                "DNI": dni,
                "Tipo": data.get("¿Qué tipo de evento espiritual se realizó?", "").upper(),
                "Participantes": int(data.get("¿Cuántas personas participaron?", 0) or 0)
            })

        # OBJETIVOS
        if data.get("¿Deseas registrar avance en alguno de tus objetivos esta semana?") == "Sí":
            objetivos.append({
                "DNI": dni,
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
df_plan_eventos_f = cargar_sheet(GID_EVENTOS)
df_plan_obj_f = cargar_sheet(GID_OBJETIVOS)

df_resumen_f, df_eventos_f, df_objetivos, df_asistencia_f = aplanar(df_raw)

def pantalla_login():

    st.title("Bienvenido a IELA")

    col1, col2 = st.columns([1.2, 1])

    with col1:
        st.image(
            "https://images.unsplash.com/photo-1507525428034-b723cf961d3e",
            use_container_width=True
        )

    with col2:
        st.subheader("Iglesia Evangélica de Liberación y Avivamiento")

        dni_input = st.text_input("Ingrese su DNI")

        if st.button("Iniciar Sesión"):
            dni_limpio = dni_input.strip().zfill(8)

            if dni_limpio in df_raw["DNI_Lider"].astype(str).str.zfill(8).unique():
                st.session_state.dni = dni_limpio
                st.rerun()
            else:
                st.error("DNI no encontrado")



def pantalla_dashboard():

    dni = st.session_state.dni

    # ==============================
    # FILTRO POR LIDER
    # ==============================
        
    df_resumen_l = df_resumen_f[df_resumen_f["DNI"] == dni]
    df_eventos_l = df_eventos_f[df_eventos_f["DNI"] == dni]
    df_objetivos_l = df_objetivos[df_objetivos["DNI"] == dni]
    df_asistencia_l = df_asistencia_f[df_asistencia_f["DNI"] == dni]

    df_plan_eventos_f["DNI_Lider"] = df_plan_eventos_f["DNI_Lider"].astype(str).str.zfill(8)
    df_plan_obj_f["DNI_Lider"] = df_plan_obj_f["DNI_Lider"].astype(str).str.zfill(8)

    df_plan_eventos_l = df_plan_eventos_f[df_plan_eventos_f["DNI_Lider"] == dni]
    df_plan_obj_l = df_plan_obj_f[df_plan_obj_f["DNI_Lider"] == dni]

    st.title("Dashboard Institucional")

    # ==============================
    # TARJETAS
    # ==============================

    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric("✨ Convertidos", df_resumen_l["Convertidos"].sum())
    c2.metric("🤝 Reconciliados", df_resumen_l["Reconciliados"].sum())
    c3.metric("💰 Ofrendas", round(df_resumen_l["Ofrenda"].sum(),2))
    c4.metric("📅 Reuniones", len(df_resumen_l))
    c5.metric("🔥 Eventos Ejecutados", len(df_eventos_l))

    st.divider()

    # ==============================
    # ASISTENCIA
    # ==============================

    st.subheader("📊 Asistencia Dominical")

    if not df_asistencia_l.empty:

        asistencia_equipo = (
            df_asistencia_l
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
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)"
        )

        fig_asistencia.update_traces(textposition="outside")

        st.plotly_chart(fig_asistencia, use_container_width=True)

    # ==============================
    # EVENTOS
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
                prog = df_plan_eventos_l[df_plan_eventos_l["Mes"] == meses[mes]]["Ayunos_Programados"].sum()
            else:
                prog = df_plan_eventos_l[df_plan_eventos_l["Mes"] == meses[mes]]["Vigilias_Programadas"].sum()

            ejec = df_eventos_l[
                (df_eventos_l["Mes"] == mes) &
                (df_eventos_l["Tipo"] == tipo)
            ].shape[0]

            fila[tipo] = f"{ejec}/{prog}"

        tabla.append(fila)

    df_tabla = pd.DataFrame(tabla)

    st.dataframe(df_tabla)

    # ==============================
    # OBJETIVOS
    # ==============================

    st.subheader("🎯 Objetivos Estratégicos")

    for _, row in df_plan_obj_l.iterrows():

        objetivo = row["ObjetivoID"]
        nombre = row["NombreObjetivo"]
        meta = int(row["MetaAnual"])

        ejecutado = df_objetivos_l[
            df_objetivos_l["Objetivo"].str.contains(objetivo, na=False)
        ]["Avance"].sum()

        progreso = min(ejecutado / meta if meta > 0 else 0, 1)

        st.write(f"**{objetivo} - {nombre} ({ejecutado}/{meta})**")
        st.progress(progreso)
