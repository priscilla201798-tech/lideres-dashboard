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
    /* Ocultar elementos de Streamlit en el login */
    [data-testid="stHeader"], [data-testid="stToolbar"] {
        display: none;
    }

    /* Fondo Principal con Imagen de Paz y Tranquilidad */
    .stApp {
        background: #0f172a;
        background-image: linear-gradient(to top, rgba(15, 23, 42, 0.8), rgba(15, 23, 42, 0.3)), 
                          url("https://images.unsplash.com/photo-1499346030926-9a72daac6c63?q=80&w=2070&auto=format&fit=crop");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }

    /* Contenedor Centrado Perfectamente en Pantalla */
    .main-login-container {
        display: flex;
        align-items: center;
        justify-content: center;
        flex-direction: column;
        height: 100vh; /* Ocupa el alto total de la ventana */
        width: 100%;
        position: fixed;
        top: 0;
        left: 0;
        z-index: 1000;
    }

    .login-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 35px;
        padding: 40px;
        width: 90%;
        max-width: 400px;
        box-shadow: 0 25px 50px rgba(0, 0, 0, 0.4);
        color: white;
        text-align: center;
    }

    .login-card h1 {
        font-size: 30px !important;
        font-weight: 800 !important;
        margin-bottom: 5px !important;
        color: white !important;
    }

    .login-card .subtitle {
        color: #e2e8f0 !important;
        font-size: 16px !important;
        font-weight: 500 !important;
        margin-bottom: 30px !important;
    }

    /* Estilo de los Inputs */
    div[data-baseweb="input"] {
        background-color: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 12px !important;
    }
    
    label p {
        color: #93c5fd !important;
        font-weight: 600 !important;
        font-size: 12px !important;
    }

    /* Botón de Iniciar Sesión */
    .stButton > button {
        width: 100%;
        background: #2563eb !important;
        color: white !important;
        border-radius: 12px !important;
        padding: 12px !important;
        font-weight: 700 !important;
        border: none !important;
        margin-top: 20px;
    }

    /* Logo de GitHub ajustado */
    .logo-iglesia {
        width: 80px;
        margin-bottom: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. FUNCIÓN pantalla_login() ACTUALIZADA

def aplicar_estilos_login():
    st.markdown("""
    <style>
    /* Ocultar elementos de Streamlit */
    [data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stSidebar"] {
        display: none;
    }

    /* Fondo de Paz y Tranquilidad (Cielo despejado y suave) */
    .stApp {
        background-image: linear-gradient(to bottom, rgba(255, 255, 255, 0.4), rgba(147, 197, 253, 0.2)), 
                          url("https://images.unsplash.com/photo-1513002749550-c59d786b8e6c?q=80&w=1974&auto=format&fit=crop");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }

    /* Contenedor Flex para centrar sin scroll */
    .main-login-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 100vh; /* Alto exacto de la pantalla */
        width: 100%;
        margin: 0;
        padding: 0;
    }

    /* Tarjeta de Login Glassmorphism Suave */
    .login-card {
        background: rgba(255, 255, 255, 0.25);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.4);
        border-radius: 40px;
        padding: 50px 40px;
        width: 100%;
        max-width: 420px;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.05);
        color: #1e293b;
        text-align: center;
    }

    .login-card h1 {
        font-size: 34px !important;
        font-weight: 800 !important;
        margin-top: 15px !important;
        color: #1e3a8a !important; /* Azul marino profundo */
        letter-spacing: -1px;
    }

    .login-card .subtitle {
        color: #475569 !important;
        font-size: 16px !important;
        font-weight: 500 !important;
        margin-bottom: 35px !important;
    }

    /* Estilo de los Inputs (Más limpios) */
    div[data-baseweb="input"] {
        background-color: rgba(255, 255, 255, 0.6) !important;
        border: 1px solid rgba(255, 255, 255, 0.8) !important;
        border-radius: 16px !important;
    }
    
    input {
        color: #1e293b !important;
    }

    label p {
        color: #1e3a8a !important;
        font-weight: 700 !important;
        font-size: 13px !important;
        text-transform: uppercase;
    }

    /* Botón Profesional */
    .stButton > button {
        width: 100%;
        background: #2563eb !important;
        color: white !important;
        border-radius: 16px !important;
        padding: 14px !important;
        font-weight: 700 !important;
        font-size: 16px !important;
        border: none !important;
        margin-top: 20px;
        box-shadow: 0 10px 20px rgba(37, 99, 235, 0.2) !important;
    }

    .stButton > button:hover {
        background: #1d4ed8 !important;
        transform: translateY(-1px);
    }
    </style>
    """, unsafe_allow_html=True)

# ==============================
# 🖥️ PANTALLA LOGIN
# ==============================
def pantalla_login():
    aplicar_estilos_login()
    
    # Abrimos la tarjeta de login directamente
    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    
    # Logo Institucional
    try:
        if os.path.exists("logotipo.png"):
            st.image("logotipo.png", width=120)
        else:
            st.markdown('<div style="font-size: 60px; color: #3b82f6; margin-bottom: 10px;">🕊️</div>', unsafe_allow_html=True)
    except:
        st.markdown('<div style="font-size: 60px; color: #3b82f6; margin-bottom: 10px;">🕊️</div>', unsafe_allow_html=True)
    
    st.markdown("""
            <h1>Bienvenido</h1>
            <p class="subtitle">Gestión Ministerial IELA</p>
    """, unsafe_allow_html=True)

    # Input de DNI
    dni_input = st.text_input("Ingresa tu DNI", placeholder="Documento de identidad")

    if st.button("Ingresar al Portal"):
        dni_limpio = dni_input.strip().zfill(8)
        if dni_limpio in df_raw["DNI_Lider"].astype(str).str.zfill(8).unique():
            st.session_state.dni = dni_limpio
            st.rerun()
        else:
            st.error("DNI no registrado")

    st.markdown("""
            <div style="margin-top: 35px; border-top: 1px solid rgba(0,0,0,0.1); padding-top: 20px;">
                <p style="font-size: 12px; color: #475569; font-weight: 700; margin-bottom: 0;">IELA 2026</p>
                <p style="font-size: 11px; color: #64748b;">Avivamiento y Poder</p>
            </div>
        </div> <!-- Cierre login-card -->
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
