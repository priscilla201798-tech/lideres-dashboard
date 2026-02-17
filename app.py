import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Dashboard IELA", layout="wide")

SPREADSHEET_ID = "1Q4UuncnykLJZrODE_Vwv-_WvCo7LWBNmbhnnPyb1Dt4"

# -----------------------------
# ESTILO
# -----------------------------
st.markdown("""
<style>
body { background-color: #0F172A; color: #F1F5F9; }
.card {
    background-color: #1E293B;
    padding: 20px;
    border-radius: 12px;
}
.metric-title { color: #94A3B8; font-size: 14px; }
.metric-value { font-size: 26px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# CARGAR GOOGLE SHEETS
# -----------------------------
def load_sheet(sheet_name):
    url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    return pd.read_csv(url)

df = load_sheet("BD_ANALISIS_SEMANAL")
df_lideres = load_sheet("BD_LIDERES")
df_obj = load_sheet("OBJETIVOS_DEL_LIDER")

# -----------------------------
# LIMPIEZA EXTREMA DNI
# -----------------------------
def limpiar_columna_dni(df):
    col_dni = None
    for col in df.columns:
        if "dni" in col.lower():
            col_dni = col
            break
    if col_dni is None:
        return None, df

    df[col_dni] = (
        df[col_dni]
        .astype(str)
        .str.replace(".0", "", regex=False)
        .str.strip()
    )
    return col_dni, df

col_dni_df, df = limpiar_columna_dni(df)
col_dni_lideres, df_lideres = limpiar_columna_dni(df_lideres)
col_dni_obj, df_obj = limpiar_columna_dni(df_obj)

if col_dni_lideres is None:
    st.error("No se encontró columna DNI en BD_LIDERES")
    st.stop()

# -----------------------------
# LOGIN
# -----------------------------
st.sidebar.title("Acceso")
rol = st.sidebar.selectbox("Rol", ["Líder", "Supervisor"])

dni = None

if rol == "Líder":
    dni = st.sidebar.text_input("Ingresa tu DNI")
else:
    password = st.sidebar.text_input("Contraseña Supervisor", type="password")
    if password == "INTIMOSIELA2026":
        dni = st.sidebar.selectbox("Selecciona líder", df_lideres[col_dni_lideres].unique())
    else:
        st.stop()

# -----------------------------
# FILTRO FECHA
# -----------------------------
st.sidebar.title("Periodo")
fecha_inicio = st.sidebar.date_input("Desde", datetime(2026,1,1))
fecha_fin = st.sidebar.date_input("Hasta", datetime.now())

# -----------------------------
# CONTENIDO PRINCIPAL
# -----------------------------
if dni:

    dni = str(dni).replace(".0", "").strip()

    fila = df_lideres[df_lideres[col_dni_lideres] == dni]

    if fila.empty:
        st.warning("El DNI existe pero no coincide exactamente. Verifica formato en BD_LIDERES.")
        st.stop()

    info = fila.iloc[0]

    if "Fecha" in df.columns:
        df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")

    df_filtrado = df[
        (df[col_dni_df] == dni) &
        (df["Fecha"] >= pd.to_datetime(fecha_inicio)) &
        (df["Fecha"] <= pd.to_datetime(fecha_fin))
    ]

    st.title("Dashboard de Liderazgo")

    st.markdown(f"""
    <p style='color:#94A3B8'>
    {info.get("NombreCompleto","")} | 
    {info.get("EntidadTipo","")} | 
    {info.get("Proceso","")}
    </p>
    """, unsafe_allow_html=True)

    if df_filtrado.empty:
        st.info("Este líder aún no tiene registros en el periodo seleccionado.")
        st.stop()

    col1, col2, col3, col4 = st.columns(4)

    asistencia = df_filtrado.get("Asistencia_Total", pd.Series([0])).sum()
    eventos = df_filtrado.get("Evento_Realizado", pd.Series([0])).sum()
    reuniones = df_filtrado.get("Reunion_Realizada", pd.Series([0])).sum()
    convertidos = df_filtrado.get("Conversiones", pd.Series([0])).sum()

    with col1:
        st.markdown(f"<div class='card'><div class='metric-title'>Asistencia</div><div class='metric-value'>{int(asistencia)}</div></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='card'><div class='metric-title'>Eventos</div><div class='metric-value'>{int(eventos)}</div></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='card'><div class='metric-title'>Reuniones</div><div class='metric-value'>{int(reuniones)}</div></div>", unsafe_allow_html=True)
    with col4:
        st.markdown(f"<div class='card'><div class='metric-title'>Convertidos</div><div class='metric-value'>{int(convertidos)}</div></div>", unsafe_allow_html=True)

    st.markdown("---")

    st.subheader("Objetivos")

    objetivos = df_obj[df_obj[col_dni_obj] == dni]

    if objetivos.empty:
        st.info("No hay objetivos registrados para este líder.")
    else:
        for _, row in objetivos.iterrows():
            meta = row.get("MetaAnual", 0)
            ejecutado = df_filtrado.get("Avance", pd.Series([0])).sum()

            porcentaje = 0
            if meta > 0:
                porcentaje = min(int((ejecutado/meta)*100), 100)

            st.progress(porcentaje / 100)
            st.write(f"{row.get('NombreObjetivo','Objetivo')} - {porcentaje}%")
