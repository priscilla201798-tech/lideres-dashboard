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
# 🎨 CONFIGURACIÓN E IMAGEN VISUAL
# ==============================
st.set_page_config(
    page_title="IELA - Portal de Liderazgo",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Colores de Marca
COLOR_PRIMARY = "#3b82f6"
COLOR_DARK = "#020617"
COLOR_CARD = "rgba(255, 255, 255, 0.03)"

# ==============================
# 🛠️ ESTILOS CSS AGRESIVOS (FUERZA EL REDISEÑO)
# ==============================
def aplicar_estilos_radiales():
    st.markdown(f"""
    <style>
    /* Importación de fuente moderna */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800&display=swap');

    /* Reset global */
    html, body, [data-testid="stAppViewContainer"] {{
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        background: radial-gradient(circle at 50% 0%, #1e293b 0%, #020617 100%) !important;
        color: #f8fafc !important;
    }}

    /* Eliminar el padding superior de Streamlit */
    .block-container {{
        padding-top: 2rem !important;
    }}

    /* Sidebar con efecto Glassmorphism real */
    [data-testid="stSidebar"] {{
        background: rgba(2, 6, 23, 0.5) !important;
        backdrop-filter: blur(20px) !important;
        border-right: 1px solid rgba(255,255,255,0.1) !important;
    }}

    /* Tarjetas de Métricas Custom (No usamos st.metric) */
    .custom-card {{
        background: linear-gradient(145deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.01) 100%);
        padding: 1.5rem;
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        text-align: center;
        transition: all 0.3s ease;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    }}
    
    .custom-card:hover {{
        transform: translateY(-8px);
        border-color: {COLOR_PRIMARY};
        box-shadow: 0 12px 30px rgba(59, 130, 246, 0.2);
    }}

    .card-icon {{
        font-size: 2rem;
        margin-bottom: 0.5rem;
        display: block;
    }}

    .card-value {{
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(to bottom, #fff, #94a3b8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1;
    }}

    .card-label {{
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.1rem;
        color: #64748b;
        margin-top: 0.5rem;
        font-weight: 600;
    }}

    /* Contenedores de Bloques */
    .glass-panel {{
        background: rgba(255, 255, 255, 0.02);
        padding: 2rem;
        border-radius: 24px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        margin-bottom: 1rem;
    }}

    /* Títulos con estilo */
    .main-title {{
        font-size: 3.5rem !important;
        font-weight: 800 !important;
        letter-spacing: -3px !important;
        margin-bottom: 0 !important;
        background: linear-gradient(to right, #ffffff, #3b82f6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }}

    /* Tabla elegante */
    .modern-table {{
        width: 100%;
        border-collapse: collapse;
        margin-top: 1rem;
    }}
    .modern-table th {{
        background: rgba(255, 255, 255, 0.05);
        color: #94a3b8;
        text-align: left;
        padding: 1rem;
        font-size: 0.8rem;
        text-transform: uppercase;
    }}
    .modern-table td {{
        padding: 1rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.03);
    }}
    
    /* Progress bar custom */
    .stProgress > div > div > div > div {{
        background-color: {COLOR_PRIMARY} !important;
        height: 8px !important;
    }}

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
        st.markdown('<div class="login-sidebar-wrapper">', unsafe_allow_html=True)
        st.markdown('<div class="login-sidebar">', unsafe_allow_html=True)
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


# ==============================
# 🖥️ PANTALLA DASHBOARD
# ==============================
def pantalla_dashboard(nombre, entidad):
    # Paso 1: Aplicar los estilos al inicio de la función
    aplicar_estilos_radiales()
    
    # Header con HTML puro para evitar el estilo estándar
    st.markdown(f"""
        <div style='margin-bottom: 2rem;'>
            <p style='color: {COLOR_PRIMARY}; font-weight: 600; margin: 0; letter-spacing: 2px;'>DASHBOARD OPERATIVO</p>
            <h1 class='main-title'>Hola, {nombre}</h1>
            <p style='color: #64748b;'>Supervisando la entidad: <b>{entidad}</b></p>
        </div>
    """, unsafe_allow_html=True)

    # Grid de Métricas (6 columnas)
    m1, m2, m3, m4, m5, m6 = st.columns(6)
    
    # Datos de ejemplo (sustituir por tus variables reales de los DataFrames)
    metrics_data = [
        ("Reuniones", "24", "📅"),
        ("Convertidos", "156", "✨"),
        ("Ofrendas", "S/ 4.2k", "💰"),
        ("Eventos", "8", "🔥"),
        ("Escuela B.", "92%", "📘"),
        ("Visitas", "42", "👣")
    ]
    
    cols = [m1, m2, m3, m4, m5, m6]
    for i, (label, val, icon) in enumerate(metrics_data):
        with cols[i]:
            st.markdown(f"""
                <div class="custom-card">
                    <span class="card-icon">{icon}</span>
                    <div class="card-value">{val}</div>
                    <div class="card-label">{label}</div>
                </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Bloques de Contenido (Izquierda: Objetivos, Derecha: Gráfico)
    c1, c2 = st.columns([1.2, 0.8])

    with c1:
        st.markdown("<div class='glass-panel'>", unsafe_allow_html=True)
        st.markdown("<h3 style='margin-top:0;'>🎯 Objetivos Estratégicos</h3>", unsafe_allow_html=True)
        
        for label, val in [("Crecimiento Anual", 85), ("Liderazgo", 60), ("Misiones", 40)]:
            st.markdown(f"<p style='margin-bottom:0.2rem; font-weight:600;'>{label}</p>", unsafe_allow_html=True)
            st.progress(val/100)
            st.markdown("<div style='margin-bottom:1rem;'></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown("<div class='glass-panel'>", unsafe_allow_html=True)
        st.markdown("<h3 style='margin-top:0;'>📊 Distribución</h3>", unsafe_allow_html=True)
        
        # Gráfico con transparencia total para integrarse al fondo radial
        fig = px.pie(values=[45, 25, 30], names=['Adultos', 'Jóvenes', 'Niños'], hole=0.8)
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color="white",
            margin=dict(t=0, b=0, l=0, r=0),
            height=220,
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Tabla final estilizada como una Web App moderna
    st.markdown("<div class='glass-panel'>", unsafe_allow_html=True)
    st.markdown("<h3 style='margin-top:0;'>📅 Próximas Actividades</h3>", unsafe_allow_html=True)
    st.markdown("""
        <table class="modern-table">
            <thead>
                <tr>
                    <th>Actividad</th>
                    <th>Fecha</th>
                    <th>Estado</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td><b>Vigilia de Intercesión</b></td>
                    <td>24 de Noviembre</td>
                    <td><span style='color:#10b981; background:rgba(16,185,129,0.1); padding:4px 12px; border-radius:10px;'>Confirmado</span></td>
                </tr>
                <tr>
                    <td><b>Seminario de Liderazgo</b></td>
                    <td>02 de Diciembre</td>
                    <td><span style='color:#f59e0b; background:rgba(245,158,11,0.1); padding:4px 12px; border-radius:10px;'>Pendiente</span></td>
                </tr>
            </tbody>
        </table>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ==============================
# 🚀 PUNTO DE ENTRADA
# ==============================
if __name__ == "__main__":
    # Aquí puedes simular los datos para ver el cambio
    pantalla_dashboard("Admin IELA", "Sede Central Lima")
# ==============================
# CONTROLADOR DE PANTALLAS
# ==============================

if "dni" not in st.session_state:
    st.session_state.dni = None

if st.session_state.dni is None:
    pantalla_login()
else:
    pantalla_dashboard()
