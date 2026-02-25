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
    justify-content: center;
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
# 🎨 ESTILOS CSS PROFESIONALES (CORRECCIÓN DE INTERACCIÓN)
# ==============================
def aplicar_estilos_login():
    st.markdown("""
    <style>
    /* 1. Reset de Streamlit */
    [data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"] {
        display: none !important;
    }
    
    .block-container {
        padding: 0 !important;
        max-width: 100% !important;
    }
    /* Elimina margen superior real de Streamlit */
    .block-container {
        padding-top: 0rem !important;
        margin-top: 0rem !important;
    }
    header {visibility: hidden;}
    /* Fuerza que el contenedor principal no empuje contenido */
    section.main > div {
        padding-top: 0rem !important;
    }
    /* 2. Fondo de Océano */
    .stApp {
        background-image: linear-gradient(to bottom, rgba(0, 31, 63, 0.4), rgba(0, 0, 0, 0.7)), 
                          url("https://images.unsplash.com/photo-1518837695005-2083093ee35b?q=80&w=2070&auto=format&fit=crop");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }

    /* 3. Contenedor de Centrado Absoluto */
    /* IMPORTANTE: pointer-events: none permite que los clics pasen a través de la capa invisible */
    .main-wrapper {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    pointer-events: none;
}

    /* 4. Títulos en BLANCO */
    .header-text {
        text-align: center;
        margin-bottom: 25px;
        pointer-events: none;
    }

    .header-text h1 {
        color: #ffffff !important; 
        font-size: 36px !important;
        font-weight: 800 !important;
        margin: 0 !important;
        text-shadow: 2px 4px 10px rgba(0,0,0,0.6);
    }

    .header-text p.subtitle {
        color: rgba(255, 255, 255, 0.95) !important;
        font-size: 16px !important;
        font-weight: 500;
        margin-top: 5px !important;
        text-shadow: 1px 2px 5px rgba(0,0,0,0.5);
    }

    /* 5. Tarjeta de Login Blanca y Compacta */
    /* pointer-events: all permite volver a interactuar con lo que esté dentro de la caja */
    .login-box {
        background-color: white !important;
        border-radius: 28px;
        padding: 35px;
        width: 360px;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.7);
        text-align: center;
        pointer-events: all; 
    }

    /* Estilo de los Inputs (Barra más pequeña y controlada) */
    div[data-testid="stTextInput"] {
        width: 100% !important;
        margin-bottom: 0px !important;
    }

    div[data-baseweb="input"] {
        background-color: #f8fafc !important;
        border: 2px solid #e2e8f0 !important;
        border-radius: 12px !important;
        height: 45px !important;
    }

    div[data-baseweb="input"] input {
        color: #001f3f !important;
        font-size: 15px !important;
    }

    label p {
        color: #001f3f !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        font-size: 11px !important;
        text-align: left !important;
        margin-bottom: 6px !important;
        letter-spacing: 0.5px;
    }

    /* Botón Marino */
    .stButton > button {
        width: 100%;
        background-color: #001f3f !important;
        color: white !important;
        border-radius: 12px !important;
        padding: 12px !important;
        font-weight: 700 !important;
        font-size: 16px !important;
        border: none !important;
        margin-top: 20px;
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
        background-color: #084d6e !important;
        transform: translateY(-2px);
    }

    /* Ajuste de alertas */
    .stAlert {
        border-radius: 12px !important;
        margin-top: 15px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ==============================
# 🖥️ PANTALLA LOGIN
# ==============================
def pantalla_login():
    aplicar_estilos_login()
    
    # Contenedor de posicionamiento
    st.markdown('<div class="main-wrapper">', unsafe_allow_html=True)
    
    # Títulos fuera de la caja para estilo moderno
    st.markdown("""
        <div class="header-text">
            <div style="font-size: 55px; margin-bottom: 10px;">🕊️</div>
            <h1>Portal de Liderazgo</h1>
            <p class="subtitle">Gestión Ministerial IELA 2026</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Caja blanca de entrada
    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    
    # Input de Streamlit (está dentro del div con pointer-events: all)
    dni_input = st.text_input("Ingresa tu DNI", placeholder="Ej: 45678912")

    if st.button("Acceder al Portal"):
        dni_limpio = dni_input.strip().zfill(8)
        if dni_limpio in df_raw["DNI_Lider"].astype(str).str.zfill(8).unique():
            st.session_state.dni = dni_limpio
            st.rerun()
        else:
            st.error("DNI no registrado")

    st.markdown("""
        <div style="margin-top: 30px; border-top: 1px solid #f1f5f9; padding-top: 20px; width: 100%;">
            <p style="font-size: 11px; color: #94a3b8; font-weight: 700; text-transform: uppercase; letter-spacing: 1px;">
                Avivamiento y Poder
            </p>
        </div>
        </div> <!-- Cierre login-box -->
    </div> <!-- Cierre main-wrapper -->
    """, unsafe_allow_html=True)
# ==============================
# 🖥️ PANTALLA DASHBOARD
# ==============================
def pantalla_dashboard():
    # Recuperamos el DNI del estado de sesión para evitar errores de referencia
    dni_usuario = st.session_state.get("dni")
    
    st.title("Panel de Control")
    st.write(f"Has ingresado como líder DNI: {dni_usuario}")
    
    # Aquí puedes añadir la lógica de filtrado que causaba el error
    # Ejemplo: df_lider = df_plan_eventos_f[df_plan_eventos_f["DNI_Lider"] == dni_usuario]
    
    if st.button("Cerrar Sesión"):
        st.session_state.dni = None
        st.rerun()

    # ==============================
    # DATOS DEL LÍDER + SIDEBAR
    # ==============================
    
    df_plan_eventos_f["DNI_Lider"] = df_plan_eventos_f["DNI_Lider"].astype(str).str.zfill(8)
    
    df_lider = df_plan_eventos_f[df_plan_eventos_f["DNI_Lider"] == dni]
    
    if not df_lider.empty:
        datos_lider = df_lider.iloc[0]
        nombre_lider = datos_lider["NombreCompleto"]
        entidad_lider = datos_lider["EntidadNombre"]
    else:
        nombre_lider = "No registrado"
        entidad_lider = "-"
    
    st.sidebar.title("📊 Panel de Control")
    
    st.sidebar.markdown("""
    <style>
    .sidebar-card {
        background-color: #1D4E89;
        padding: 18px;
        border-radius: 12px;
        color: white;
        margin-bottom: 15px;
        font-size: 14px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.sidebar.markdown(f"""
    <div class="sidebar-card">
    <b>DNI:</b><br>{dni}<br><br>
    <b>Nombre:</b><br>{nombre_lider}<br><br>
    <b>Entidad:</b><br>{entidad_lider}
    </div>
    """, unsafe_allow_html=True)
    
    if st.sidebar.button("Cerrar sesión"):
        st.session_state.dni = None
        st.rerun()
    
    st.sidebar.markdown("---")
    
    st.sidebar.markdown("### 📅 Filtrar por fecha")
    
    fecha_min = df_resumen_f["Fecha"].min()
    fecha_max = df_resumen_f["Fecha"].max()
    
    rango_fechas = st.sidebar.date_input(
        "Seleccionar rango",
        value=(fecha_min, fecha_max),
        min_value=fecha_min,
        max_value=fecha_max
    )
        
    # ==============================
    # FILTRO POR LIDER
    # ==============================
    
    df_resumen_l = df_resumen_f[df_resumen_f["DNI"] == dni]
    df_eventos_l = df_eventos_f[df_eventos_f["DNI"] == dni]
    df_objetivos_l = df_objetivos[df_objetivos["DNI"] == dni]
    df_asistencia_l = df_asistencia_f[df_asistencia_f["DNI"] == dni]
    
    # ==============================
    # FILTRO POR FECHA (AQUÍ VA)
    # ==============================
    
    if isinstance(rango_fechas, tuple) and len(rango_fechas) == 2:
        desde, hasta = rango_fechas
    
        df_resumen_l = df_resumen_l[
            (df_resumen_l["Fecha"] >= pd.to_datetime(desde)) &
            (df_resumen_l["Fecha"] <= pd.to_datetime(hasta))
        ]
    
        df_eventos_l = df_eventos_l[
            df_eventos_l["Mes"].isin(df_resumen_l["Mes"])
        ]
    
        df_asistencia_l = df_asistencia_l[
            df_asistencia_l["Mes"].isin(df_resumen_l["Mes"])
        ]
    

    df_plan_eventos_f["DNI_Lider"] = df_plan_eventos_f["DNI_Lider"].astype(str).str.zfill(8)
    df_plan_obj_f["DNI_Lider"] = df_plan_obj_f["DNI_Lider"].astype(str).str.zfill(8)

    df_plan_eventos_l = df_plan_eventos_f[df_plan_eventos_f["DNI_Lider"] == dni]
    df_plan_eventos_l["Mes"] = df_plan_eventos_l["Mes"].str.strip().str.lower()
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
    
    # Normalizamos texto de meses
    
    tabla = []
    
    for mes in range(1, 13):
    
        mes_nombre = meses[mes].lower()
    
        fila = {"Mes": meses[mes]}
    
        for tipo in ["AYUNO", "VIGILIA"]:
    
            if tipo == "AYUNO":
                prog = df_plan_eventos_l[
                    df_plan_eventos_l["Mes"] == mes_nombre
                ]["Ayunos_Programados"].sum()
            else:
                prog = df_plan_eventos_l[
                    df_plan_eventos_l["Mes"] == mes_nombre
                ]["Vigilias_Programadas"].sum()
    
            ejec = df_eventos_l[
                (df_eventos_l["Mes"] == mes) &
                (df_eventos_l["Tipo"] == tipo)
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


# ==============================
# CONTROLADOR DE PANTALLAS
# ==============================

if "dni" not in st.session_state:
    st.session_state.dni = None

if st.session_state.dni is None:
    pantalla_login()
else:
    pantalla_dashboard()
