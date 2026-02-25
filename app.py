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
# 🎨 ESTILOS CSS (DISEÑO ALINEADO Y SIN BARRAS)
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

    /* 2. ELIMINACIÓN RADICAL DE BARRAS SUPERIORES */
    header, [data-testid="stHeader"], [data-testid="stDecoration"] {
        display: none !important;
        height: 0 !important;
    }
    
    /* Reset de márgenes de Streamlit para subir el contenido */
    .main .block-container {
        padding-top: 0 !important;
        padding-bottom: 0 !important;
        margin-top: -30px !important; 
    }

    /* 3. Estilo de los Inputs */
    div[data-baseweb="input"] {
        background-color: #ffffff !important;
        border: 1px solid #d1d5db !important;
        border-radius: 8px !important;
        height: 40px !important;
    }

    div[data-baseweb="input"] input {
        color: #1e293b !important;
        font-size: 14px !important;
    }

    label p {
        color: #ffffff !important;
        font-weight: 600 !important;
        font-size: 12px !important;
        margin-bottom: 8px !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
    }

    /* 4. Botón de Acceso */
    .stButton > button {
        width: 100%;
        background-color: #004a99 !important;
        color: white !important;
        border-radius: 8px !important;
        padding: 10px !important;
        font-weight: 700 !important;
        border: none !important;
        transition: all 0.2s ease;
    }

    /* 5. Contenedor de Bienvenida (Alineado hacia arriba) */
    .welcome-container {
        display: flex;
        flex-direction: column;
        justify-content: center;
        height: 85vh;
        padding-left: 50px;
    }
    
    .welcome-container h1 {
        color: white !important;
        font-size: 85px !important;
        font-weight: 900 !important;
        text-shadow: 4px 6px 20px rgba(0,0,0,0.9);
        margin: 0 !important;
        line-height: 0.95 !important;
        letter-spacing: -3px !important;
    }

    .welcome-container p {
        color: #f8fafc !important;
        font-size: 24px !important;
        font-weight: 500;
        text-shadow: 2px 3px 10px rgba(0,0,0,0.8);
        margin-top: 15px !important;
    }

    /* 6. Caja de Login - Ajuste de altura para que no baje tanto */
    .login-sidebar-wrapper {
        display: flex;
        align-items: center;
        justify-content: center;
        height: 85vh;
    }

    .login-sidebar {
        background-color: rgba(0, 31, 63, 0.45);
        backdrop-filter: blur(25px);
        padding: 40px;
        border-radius: 32px;
        border: 1px solid rgba(255,255,255,0.25);
        width: 100%;
        max-width: 380px;
        box-shadow: 0 30px 60px rgba(0,0,0,0.6);
        margin-top: -20px; /* Ajuste manual para subir el bloque */
    }
    </style>
    """, unsafe_allow_html=True)

# ==============================
# 🖥️ PANTALLA LOGIN
# ==============================
def pantalla_login():
    aplicar_estilos_login()
    
    col_espacio, col_login = st.columns([1.6, 1])
    
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
        st.markdown("<h2 style='color:white; margin-bottom:25px; font-size:26px; font-weight:800; letter-spacing:-0.5px;'>Iniciar Sesión</h2>", unsafe_allow_html=True)
        
        dni_input = st.text_input("DNI DEL LÍDER", placeholder="Ingresa tu documento")

        if st.button("Ingresar al Portal"):
            dni_limpio = dni_input.strip().zfill(8)
            if dni_limpio in df_raw["DNI_Lider"].astype(str).str.zfill(8).unique():
                st.session_state.dni = dni_limpio
                st.rerun()
            else:
                st.error("Documento no encontrado.")
        
        st.markdown("""
            <div style="margin-top: 40px; border-top: 1px solid rgba(255,255,255,0.2); padding-top: 25px;">
                <p style="font-size: 11px; color: #f1f5f9; font-weight: 800; text-transform: uppercase; letter-spacing: 2px; text-align: center; opacity: 0.8;">
                    IELA 2026 • Gestión Ministerial
                </p>
            </div>
            </div> 
            </div> 
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
