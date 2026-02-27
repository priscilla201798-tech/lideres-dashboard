import streamlit as st
import pandas as pd
import json
import plotly.express as px

st.set_page_config(
    page_title="IELA - Portal de Liderazgo",
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
AZUL_PRIMARIO = "#0B3C5D"
AZUL_ACCENTO = "#1D4E89"
VERDE_EXITO = "#1E8449"
ROJO_ERROR = "#C0392B"

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
import re

def norm_txt(s):
    return re.sub(r"\s+", " ", str(s or "").strip().lower())

def es_si(valor):
    v = norm_txt(valor)
    return v in {"si", "sí", "s", "yes", "true", "1", "ok", "x"}

def get_num(data, *keys, default=0):
    """Busca una clave exacta; si no existe, busca por coincidencia 'normalizada'."""
    if not isinstance(data, dict):
        return default

    # 1) exact match
    for k in keys:
        if k in data:
            try:
                return float(data.get(k) or 0)
            except:
                return default

    # 2) fuzzy by normalized text
    wanted = {norm_txt(k) for k in keys}
    for k_data, v in data.items():
        if norm_txt(k_data) in wanted:
            try:
                return float(v or 0)
            except:
                return default
    return default

def get_val(data, *keys, default=""):
    if not isinstance(data, dict):
        return default
    for k in keys:
        if k in data:
            return data.get(k)
    wanted = {norm_txt(k) for k in keys}
    for k_data, v in data.items():
        if norm_txt(k_data) in wanted:
            return v
    return default
    
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

        try:
            data = json.loads(raw_json)
        except:
            try:
                data = json.loads(json.loads(raw_json))
            except:
                continue

        # ==============================
        # PROGRAMACIÓN SEMANAL (SI / NO)
        # ==============================
        cumplio_prog = (
            es_si(get_val(
                data,
                "¿Se realizó la reunión esta semana?",
                "¿Se cumplio con la programación semanal?",   # sin tilde
                "¿Se cumplió con la programación semanal?",   # con tilde (por si acaso)
                default=""
            ))
        )

        # ==============================
        # VARIABLES AUTOMÁTICAS
        # ==============================
        nuevos = get_num(data, "¿Cuántas personas nuevas asistieron?", default=0)
        visitas = get_num(data, "Cantidad de visitas realizadas", default=0)
        esc_bib = get_num(data, "Cantidad de personas derivadas a Escuela Bíblica", default=0)

        # ==============================
        # RESUMEN (UNA SOLA VEZ)
        # ==============================
        resumen.append({
            "Fecha": fecha,
            "Mes": mes,
            "DNI": dni,

            "Convertidos": int(get_num(
                data,
                "¿Cuántas personas aceptaron a Cristo?",
                "4. ¿Cuántas personas aceptaron a Cristo?",
                default=0
            )),
            "Reconciliados": int(get_num(
                data,
                "¿Cuántas personas se reconciliaron con Cristo?",
                default=0
            )),
            "Ofrenda": float(get_num(
                data,
                "Monto total de la ofrenda (S/.)",
                default=0
            )),

            # 👇 CLAVE
            "ProgSemanal": 1 if cumplio_prog else 0,
            "Nuevos": int(nuevos),
            "Visitas": int(visitas),
            "EscuelaBiblica": int(esc_bib),
        })

        # ==============================
        # EVENTOS
        # ==============================
        if es_si(get_val(data, "¿Esta semana se realizó algún evento espiritual?", default="")):
            eventos.append({
                "Mes": mes,
                "DNI": dni,
                "Tipo": str(get_val(
                    data,
                    "¿Qué tipo de evento espiritual se realizó?",
                    default=""
                )).upper(),
                "Participantes": int(get_num(
                    data,
                    "¿Cuántas personas participaron?",
                    default=0
                ))
            })

        # ==============================
        # OBJETIVOS MANUALES
        # ==============================
        if es_si(get_val(data, "¿Deseas registrar avance en alguno de tus objetivos esta semana?", default="")):
            objetivos.append({
                "DNI": dni,
                "Objetivo": get_val(
                    data,
                    "¿En qué objetivo deseas registrar avance?",
                    default=""
                ),
                "Avance": int(get_num(
                    data,
                    "¿Cuánto avanzaste en este objetivo?",
                    default=0
                ))
            })

        # ==============================
        # ASISTENCIA
        # ==============================
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

def calcular_avance_objetivos(df_plan_obj_l, df_res_l, df_ev_l, df_obj_manual_l):
    """
    df_plan_obj_l: hoja OBJETIVOS_DEL_LIDER filtrada por DNI
    df_res_l: resumen filtrado por DNI + rango
    df_ev_l: eventos ejecutados filtrados por DNI + rango
    df_obj_manual_l: avances manuales filtrados por DNI (tu df_objetivos_l)
    """

    # acumulados base (AUTO)
    tot_convertidos = int(df_res_l["Convertidos"].sum()) if "Convertidos" in df_res_l else 0
    tot_nuevos = int(df_res_l["Nuevos"].sum()) if "Nuevos" in df_res_l else 0
    tot_visitas = int(df_res_l["Visitas"].sum()) if "Visitas" in df_res_l else 0
    tot_esc_bib = int(df_res_l["EscuelaBiblica"].sum()) if "EscuelaBiblica" in df_res_l else 0
    tot_prog = int(df_res_l["ProgSemanal"].sum()) if "ProgSemanal" in df_res_l else 0

    # Eventos: conteo y participantes
    ev_count = int(len(df_ev_l)) if df_ev_l is not None else 0
    ev_part = int(df_ev_l["Participantes"].sum()) if (df_ev_l is not None and "Participantes" in df_ev_l) else 0

    filas = []

    for _, row in df_plan_obj_l.iterrows():
        objetivo_id = str(row.get("ObjetivoID", "")).strip()
        nombre = str(row.get("NombreObjetivo", "")).strip()
        meta = int(float(row.get("MetaAnual", 0) or 0))
        fuente = str(row.get("FuenteDato", "")).strip()
        unidad = str(row.get("Unidad", "")).strip()

        fuente_norm = norm_txt(fuente)

        # ---- AUTO según FuenteDato ----
        ejecutado_auto = 0

        if fuente_norm == "registrosemanal":
            ejecutado_auto = tot_convertidos

        elif fuente_norm == "nuevos":
            ejecutado_auto = tot_nuevos

        elif fuente_norm == "visitas":
            ejecutado_auto = tot_visitas

        elif fuente_norm in {"escuelabiblica", "derivaciones"}:
            ejecutado_auto = tot_esc_bib

        elif fuente_norm in {"programacionsemanal", "programacionseman"}:
            ejecutado_auto = tot_prog

        elif fuente_norm == "eventosespirituales":
            # Si la unidad dice Participantes, usamos participantes; si no, conteo de eventos
            if "particip" in norm_txt(unidad):
                ejecutado_auto = ev_part
            else:
                ejecutado_auto = ev_count

        # ---- MANUAL (solo si FuenteDato es Manual) ----
        ejecutado_manual = 0
        if fuente_norm == "manual":
            # Aquí tu df_obj_manual_l debe tener columnas: Objetivo / Avance
            # y Objetivo contiene el ObjetivoID (ej: "OBJ-01")
            if df_obj_manual_l is not None and not df_obj_manual_l.empty:
                ejecutado_manual = int(
                    df_obj_manual_l[df_obj_manual_l["Objetivo"].str.contains(objetivo_id, na=False)]["Avance"].sum()
                )

        ejecutado_total = int(ejecutado_auto + ejecutado_manual)
        progreso = min(ejecutado_total / meta if meta > 0 else 0, 1)

        filas.append({
            "ObjetivoID": objetivo_id,
            "NombreObjetivo": nombre,
            "FuenteDato": fuente,
            "Unidad": unidad,
            "Ejecutado": ejecutado_total,
            "MetaAnual": meta,
            "Progreso": progreso
        })

    return pd.DataFrame(filas)
   
# ==============================
# CARGAR DATA
# ==============================

df_raw = cargar_sheet(GID_REGISTROS)
df_plan_eventos_f = cargar_sheet(GID_EVENTOS)
df_plan_obj_f = cargar_sheet(GID_OBJETIVOS)

df_resumen_f, df_eventos_f, df_objetivos, df_asistencia_f = aplanar(df_raw)


# 1. FUNCIÓN DE ESTILOS ACTUALIZADA (Imagen de paz, centrado y logo de GitHub)
def aplicar_estilos_login():
    st.markdown("""
<style>

/* 1. Eliminar absolutamente TODO el layout nativo */
[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
header,
footer {
    display: none !important;
}

/* 2. Eliminar padding y márgenes reales */
html, body, .stApp {
    margin: 0 !important;
    padding: 0 !important;
    height: 100% !important;
}

section.main > div {
    padding: 0 !important;
}

.block-container {
    padding: 0 !important;
    margin: 0 !important;
    max-width: 100% !important;
}

/* 3. Fondo full screen */
.stApp {
    background-image: linear-gradient(
        rgba(0,0,0,0.55),
        rgba(0,0,0,0.75)
    ), url("https://images.unsplash.com/photo-1518837695005-2083093ee35b?q=80&w=2070&auto=format&fit=crop");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}

/* 4. Wrapper REAL fullscreen */
.main-wrapper {
    position: fixed;
    inset: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: flex-start;
    padding-top: 120px;
    pointer-events: none;
}

/* 5. Activar interacción solo dentro del card */
.login-box {
    background: white;
    border-radius: 28px;
    padding: 35px;
    width: 360px;
    box-shadow: 0 25px 50px rgba(0,0,0,0.6);
    pointer-events: all;
}

</style>
""", unsafe_allow_html=True)


# 2. FUNCIÓN pantalla_login() ACTUALIZADA
# ==============================
# 🎨 ESTILOS CSS (POSICIONAMIENTO FORZADO HACIA ARRIBA)
# ==============================
def aplicar_estilos_login():
    st.markdown("""
    <style>
    /* 1. Fondo de Océano Global */
    .stApp {
        background-image: linear-gradient(to right, rgba(0, 0, 0, 0.2), rgba(0, 31, 63, 0.6)), 
                          url("https://images.unsplash.com/photo-1518837695005-2083093ee35b?q=80&w=2070&auto=format&fit=crop");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }

    /* 2. ELIMINACIÓN TOTAL DE BARRAS */
    header, [data-testid="stHeader"], [data-testid="stDecoration"] {
        display: none !important;
    }
    
        .block-container {
        padding-top: 0 !important;
        margin-top: 0 !important;
    }

        [data-testid="stHeader"] {
        height: 0px !important;
    }
    
    [data-testid="stAppViewContainer"] > .main {
        padding-top: 0rem !important;
    }
    
    /* 3. Estilo de los Inputs */
    div[data-baseweb="input"] {
        background-color: #ffffff !important;
        border: 1px solid #d1d5db !important;
        border-radius: 12px !important;
        height: 45px !important;
    }

    div[data-baseweb="input"] input {
        color: #1e293b !important;
        font-size: 16px !important;
    }

    label p {
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 13px !important;
        margin-bottom: 8px !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
        text-transform: uppercase;
    }

    /* 4. Botón de Acceso */
    .stButton > button {
        width: 100%;
        background-color: #004a99 !important;
        color: white !important;
        border-radius: 12px !important;
        padding: 12px !important;
        font-weight: 800 !important;
        border: none !important;
        box-shadow: 0 10px 20px rgba(0,0,0,0.3);
    }

    /* 5. Contenedor de Bienvenida (Forzado hacia arriba) */
    .welcome-container {
        margin-top: 15vh; /* Empieza al 15% de la altura de la pantalla */
        padding-left: 60px;
    }
    
    .welcome-container h1 {
        color: white !important;
        font-size: 90px !important;
        font-weight: 900 !important;
        text-shadow: 4px 6px 25px rgba(0,0,0,0.9);
        margin: 0 !important;
        line-height: 0.85 !important;
        letter-spacing: -4px !important;
    }

    .welcome-container p {
        color: #f8fafc !important;
        font-size: 26px !important;
        font-weight: 500;
        text-shadow: 2px 3px 10px rgba(0,0,0,0.8);
        margin-top: 25px !important;
    }

    /* 6. Caja de Login (Forzada hacia arriba para coincidir con el título) */
    
    </style>
    """, unsafe_allow_html=True)

# ==============================
# 🖥️ PANTALLA LOGIN
# ==============================
def pantalla_login():
    aplicar_estilos_login()
    
    col_espacio, col_login = st.columns([1.7, 1])
    
    with col_espacio:
        st.markdown("""
            <div class="welcome-container">
                <h1>Portal de<br>Liderazgo</h1>
                <p>Iglesia Evangélica de Liberación y Avivamiento</p>
            </div>
        """, unsafe_allow_html=True)
        
    with col_login:
        st.markdown('<div style="margin-top:15vh; max-width:420px;">', unsafe_allow_html=True)
        st.markdown("<h2 style='color:white; margin-bottom:30px; font-size:30px; font-weight:900; letter-spacing:-1px;'>Iniciar Sesión</h2>", unsafe_allow_html=True)
        
        dni_input = st.text_input("DNI DEL LÍDER", placeholder="Ingresa tu documento")

        if st.button("Ingresar al Portal"):
            dni_limpio = dni_input.strip().zfill(8)
            if dni_limpio in df_raw["DNI_Lider"].astype(str).str.zfill(8).unique():
                st.session_state.dni = dni_limpio
                st.rerun()
            else:
                st.error("Documento no encontrado.")
        
        st.markdown("""
            <div style="margin-top: 50px; border-top: 1px solid rgba(255,255,255,0.15); padding-top: 30px;">
                <p style="font-size: 12px; color: #f1f5f9; font-weight: 800; text-transform: uppercase; letter-spacing: 3px; text-align: center; opacity: 0.7;">
                    IELA 2026 • Gestión Ministerial
                </p>
            </div>
            </div> 
            </div> 
        """, unsafe_allow_html=True)
import streamlit.components.v1 as components

def kpi_card(titulo, valor, icono="📊", color="#1D4E89", descripcion=""):

    html = f"""
    <div style="
        background: linear-gradient(135deg, {color}, #0B3C5D);
        padding:16px 18px;
        border-radius:14px;
        color:white;
        font-family:Arial, sans-serif;
        box-shadow:0 6px 16px rgba(0,0,0,0.25);
    ">

        <div style="font-size:18px;">{icono}</div>

        <div style="
            font-size:12px;
            opacity:0.9;
            text-transform:uppercase;
            letter-spacing:0.5px;
            margin-top:4px;
        ">
            {titulo}
        </div>

        <div style="
            font-size:24px;
            font-weight:800;
            margin-top:4px;
        ">
            {valor}
        </div>

        <div style="
            font-size:11px;
            margin-top:4px;
            opacity:0.75;
        ">
            {descripcion}
        </div>

    </div>
    """

    components.html(html, height=140)
# ==============================
# 🖥️ PANTALLA DASHBOARD
# ==============================
def pantalla_dashboard():
    dni = st.session_state.get("dni", None)
    if not dni:
        st.stop()

    # --- PREPARACIÓN DATOS LÍDER ---
    df_plan_eventos_f["DNI_Lider"] = df_plan_eventos_f["DNI_Lider"].astype(str).str.zfill(8)
    df_lider_info = df_plan_eventos_f[df_plan_eventos_f["DNI_Lider"] == dni]

    if not df_lider_info.empty:
        nombre_lider = df_lider_info.iloc[0]["NombreCompleto"]
        entidad_lider = df_lider_info.iloc[0]["EntidadNombre"]
    else:
        nombre_lider = "Líder IELA"
        entidad_lider = "-"

    # ==============================
    # SIDEBAR
    # ==============================

    st.sidebar.title("I.E.L.A - Panel de Control")

    st.sidebar.markdown(f"""
    <div style="
        background:#1D4E89;
        padding:20px;
        border-radius:14px;
        color:white;
        margin-top:10px;
        margin-bottom:15px;
        font-size:14px;
    ">
    
    <div style="font-size:11px; opacity:0.7; text-transform:uppercase; letter-spacing:1px;">
    Usuario Activo
    </div>
    
    <div style="margin-top:10px;">
    <b>Nombre:</b><br>
    {nombre_lider}
    </div>
    
    <div style="margin-top:10px;">
    <b>Entidad:</b><br>
    {entidad_lider}
    </div>
    
    <div style="margin-top:10px;">
    <b>DNI:</b><br>
    {dni}
    </div>
    
    </div>
    """, unsafe_allow_html=True)

    st.sidebar.markdown("---")

    st.sidebar.markdown("### 📅 Filtrar por fecha")

    fecha_min = df_resumen_f["Fecha"].min()
    fecha_max = df_resumen_f["Fecha"].max()

    rango = st.sidebar.date_input(
        "Seleccionar rango",
        value=(fecha_min, fecha_max),
        min_value=fecha_min,
        max_value=fecha_max
    )

    st.sidebar.markdown("---")

    if st.sidebar.button("🚪 Cerrar sesión", use_container_width=True):
        st.session_state.dni = None
        st.rerun()

    # AQUÍ CONTINÚA EL RESTO DEL DASHBOARD
    # ==============================
    # FILTRADO
    # ==============================

    # ==============================
    # FILTRADO BASE POR DNI
    # ==============================

    df_res_l = df_resumen_f[df_resumen_f["DNI"] == dni]
    df_ev_l = df_eventos_f[df_eventos_f["DNI"] == dni]
    df_as_l = df_asistencia_f[df_asistencia_f["DNI"] == dni]
    df_obj_l = df_objetivos[df_objetivos["DNI"] == dni]

    df_plan_obj_l = df_plan_obj_f[
        df_plan_obj_f["DNI_Lider"].astype(str).str.zfill(8) == dni
    ]

    # ==============================
    # FILTRADO POR FECHA
    # ==============================

    if isinstance(rango, tuple) and len(rango) == 2:
        df_res_l = df_res_l[
            (df_res_l["Fecha"] >= pd.to_datetime(rango[0])) &
            (df_res_l["Fecha"] <= pd.to_datetime(rango[1]))
        ]

        meses_validos = df_res_l["Mes"].unique()

        df_ev_l = df_ev_l[df_ev_l["Mes"].isin(meses_validos)]
        df_as_l = df_as_l[df_as_l["Mes"].isin(meses_validos)]
    # ==============================
    # KPIs BASE
    # ==============================
    
    total_convertidos = int(df_res_l["Convertidos"].sum()) if "Convertidos" in df_res_l else 0
    total_reconciliados = int(df_res_l["Reconciliados"].sum()) if "Reconciliados" in df_res_l else 0
    total_visitas = int(df_res_l["Visitas"].sum()) if "Visitas" in df_res_l else 0
    total_escuela = int(df_res_l["EscuelaBiblica"].sum()) if "EscuelaBiblica" in df_res_l else 0
    total_eventos = len(df_ev_l)

    # Calcular promedio de cumplimiento de objetivos
    df_avance_obj = calcular_avance_objetivos(
        df_plan_obj_l=df_plan_obj_l,
        df_res_l=df_res_l,
        df_ev_l=df_ev_l,
        df_obj_manual_l=df_obj_l
    )

    if not df_avance_obj.empty:
        promedio_cumplimiento = round(df_avance_obj["Progreso"].mean() * 100)
    else:
        promedio_cumplimiento = 0
    
    total_reuniones = int(df_res_l["ProgSemanal"].sum()) if "ProgSemanal" in df_res_l else 0
    total_nuevos = int(df_res_l["Nuevos"].sum()) if "Nuevos" in df_res_l else 0

    # ==============================
    # CONTENIDO PRINCIPAL
    # ==============================

    st.title("Dashboard Institucional")
    # ==============================
    # 📌 RESUMEN GENERAL (KPIs)
    # ==============================
    
    st.subheader("📌 Resumen General")

    # ==============================
    # 🔵 PRIMERA FILA
    # ==============================
    
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        kpi_card(
            "Reuniones",
            total_reuniones,
            "📅",
            "#0f766e",
            "Reuniones realizadas"
        )
    
    with c2:
        kpi_card(
            "Nuevos",
            total_nuevos,
            "🆕",
            "#2563eb",
            "Personas nuevas"
        )
    
    with c3:
        kpi_card(
            "Convertidos",
            total_convertidos,
            "✨",
            "#f59e0b",
            "Aceptaron a Cristo"
        )
    
    with c4:
        kpi_card(
            "Reconciliados",
            total_reconciliados,
            "🤝",
            "#7c3aed",
            "Personas restauradas"
        )
    
    
    # ==============================
    # 🟢 SEGUNDA FILA
    # ==============================
    
    c5, c6, c7, c8 = st.columns(4)
    
    with c5:
        kpi_card(
            "Eventos",
            total_eventos,
            "🔥",
            "#ea580c",
            "Eventos realizados"
        )
    
    with c6:
        kpi_card(
            "Escuela Bíblica",
            total_escuela,
            "📘",
            VERDE_EXITO,
            "Derivados acumulados"
        )
    
    with c7:
        kpi_card(
            "Visitas",
            total_visitas,
            "🏠",
            AZUL_ACCENTO,
            "Visitas registradas"
        )
    
    with c8:
        kpi_card(
            "Cumplimiento Objetivos",
            f"{promedio_cumplimiento}%",
            "🎯",
            "#059669",
            "Promedio general de avance"
        )
    # ==============================
    # 1️⃣ ASISTENCIA DOMINICAL
    # ==============================

    st.subheader("📊 Asistencia Dominical")

    if not df_as_l.empty:
        as_data = (
            df_as_l.groupby("Equipo")
            .size()
            .reset_index(name="Cant")
            .sort_values("Cant", ascending=False)
        )

        fig = px.bar(
            as_data,
            x="Equipo",
            y="Cant",
            color="Cant",
            color_continuous_scale="Blues",
            text_auto=True
        )

        fig.update_layout(height=350, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # ==============================
    # 🎯 OBJETIVOS ESTRATÉGICOS
    # ==============================
    
    st.subheader("🎯 Objetivos Estratégicos")
    
    df_avance_obj = calcular_avance_objetivos(
        df_plan_obj_l=df_plan_obj_l,
        df_res_l=df_res_l,
        df_ev_l=df_ev_l,
        df_obj_manual_l=df_obj_l
    )

    if not df_avance_obj.empty:
        promedio_cumplimiento = round(df_avance_obj["Progreso"].mean() * 100)
    else:
        promedio_cumplimiento = 0

    for _, row in df_avance_obj.iterrows():
    
        objetivo = row["ObjetivoID"]
        nombre = row["NombreObjetivo"]
        meta = row["MetaAnual"]
        ejecutado = row["Ejecutado"]
        progreso = row["Progreso"]
    
        st.markdown(
            f"**{objetivo} – {nombre} ({ejecutado}/{meta})**"
        )
        st.progress(progreso)
           
    # ==============================
    # 3️⃣ EVENTOS
    # ==============================

    st.subheader("📅 Cumplimiento de Eventos (Ayunos y Vigilias)")

    meses_nom = {
        1:"Enero",2:"Febrero",3:"Marzo",4:"Abril",
        5:"Mayo",6:"Junio",7:"Julio",8:"Agosto",
        9:"Septiembre",10:"Octubre",11:"Noviembre",12:"Diciembre"
    }

    tabla = []

    for m_idx in range(1, 13):
        m_name = meses_nom[m_idx]
        fila = {"Mes": m_name}

        for tipo in ["AYUNO", "VIGILIA"]:

            if tipo == "AYUNO":
                prog = df_plan_eventos_f[
                    (df_plan_eventos_f["DNI_Lider"] == dni) &
                    (df_plan_eventos_f["Mes"].str.strip().str.lower() == m_name.lower())
                ]["Ayunos_Programados"].sum()
            else:
                prog = df_plan_eventos_f[
                    (df_plan_eventos_f["DNI_Lider"] == dni) &
                    (df_plan_eventos_f["Mes"].str.strip().str.lower() == m_name.lower())
                ]["Vigilias_Programadas"].sum()

            ejec = df_ev_l[
                (df_ev_l["Mes"] == m_idx) &
                (df_ev_l["Tipo"] == tipo)
            ].shape[0]

            fila[tipo] = f"{ejec}/{prog}"

        tabla.append(fila)

    df_t = pd.DataFrame(tabla)

    def style_ev(val):
        try:
            ejec, prog = map(int, val.split("/"))
            if prog == 0:
                return ""
            if ejec >= prog:
                return "background-color:#1E8449; color:white; font-weight:bold;"
            else:
                return ""   # 👈 sin rojo
        except:
            return ""
    st.table(df_t.style.applymap(style_ev, subset=["AYUNO", "VIGILIA"]))
    st.subheader("📈 Tendencia de Participación en Eventos")

    # Creamos dataset mensual
    data_linea = []

    for m_idx in range(1, 13):
        mes_nombre = meses_nom[m_idx]

        ayuno_total = df_ev_l[
            (df_ev_l["Mes"] == m_idx) &
            (df_ev_l["Tipo"] == "AYUNO")
        ]["Participantes"].sum()

        vigilia_total = df_ev_l[
            (df_ev_l["Mes"] == m_idx) &
            (df_ev_l["Tipo"] == "VIGILIA")
        ]["Participantes"].sum()

        data_linea.append({
            "Mes": mes_nombre,
            "Ayuno": ayuno_total,
            "Vigilia": vigilia_total
        })

    df_linea = pd.DataFrame(data_linea)

    fig_line = px.line(
        df_linea,
        x="Mes",
        y=["Ayuno", "Vigilia"],
        markers=True
    )

    fig_line.update_layout(
        height=400,
        xaxis_title="Mes",
        yaxis_title="Cantidad de asistentes",
        legend_title="Tipo de Evento"
    )

    st.plotly_chart(fig_line, use_container_width=True)
        

# ==============================
# CONTROLADOR DE PANTALLAS
# ==============================

if "dni" not in st.session_state:
    st.session_state.dni = None

if st.session_state.dni is None:
    pantalla_login()
else:
    pantalla_dashboard()

