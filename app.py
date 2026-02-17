import streamlit as st
import pandas as pd

# --------------------------------------------------
# CONFIGURACIÓN GENERAL
# --------------------------------------------------

st.set_page_config(
    page_title="Dashboard IELA",
    page_icon="📊",
    layout="wide"
)

# --------------------------------------------------
# ESTILOS PERSONALIZADOS
# --------------------------------------------------

st.markdown("""
<style>

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
    color: white;
}

.sidebar-title {
    font-size: 18px;
    font-weight: 600;
    color: white;
    text-align: center;
    margin-bottom: 20px;
}

.card {
    background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
    padding: 25px;
    border-radius: 15px;
    box-shadow: 0px 4px 15px rgba(0,0,0,0.4);
    text-align: center;
}

.card-title {
    font-size: 16px;
    color: #cbd5e1;
}

.card-value {
    font-size: 38px;
    font-weight: bold;
    color: white;
}

.main-title {
    font-size: 34px;
    font-weight: bold;
    color: #0f172a;
}

</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

st.sidebar.image("logo.png", use_container_width=True)

st.sidebar.markdown(
    "<div class='sidebar-title'>Iglesia Evangélica de Liberación y Avivamiento</div>",
    unsafe_allow_html=True
)

st.sidebar.markdown("### 🔐 ACCESO")

rol = st.sidebar.selectbox("Rol", ["Líder", "Supervisor"])
dni = st.sidebar.text_input("DNI")

st.sidebar.markdown("### 📅 Periodo")
desde = st.sidebar.date_input("Desde")
hasta = st.sidebar.date_input("Hasta")

# --------------------------------------------------
# DASHBOARD PRINCIPAL
# --------------------------------------------------

st.markdown("<div class='main-title'>Dashboard de Líderes</div>", unsafe_allow_html=True)
st.markdown("---")

# Datos simulados (solo visual)
asistencia_total = 24
eventos = 3
reuniones = 5
cumplimiento = "82%"

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="card">
        <div class="card-title">Asistencia Total</div>
        <div class="card-value">{asistencia_total}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="card">
        <div class="card-title">Eventos Espirituales</div>
        <div class="card-value">{eventos}</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="card">
        <div class="card-title">Reuniones Realizadas</div>
        <div class="card-value">{reuniones}</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="card">
        <div class="card-title">% Cumplimiento</div>
        <div class="card-value">{cumplimiento}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("")

# --------------------------------------------------
# GRÁFICOS
# --------------------------------------------------

st.subheader("📈 Tendencia de Asistencia")

df = pd.DataFrame({
    "Mes": ["Ene", "Feb", "Mar", "Abr", "May"],
    "Asistencia": [10, 15, 18, 12, 20]
})

st.line_chart(df.set_index("Mes"))

st.subheader("🏆 Ranking de Líderes")

df2 = pd.DataFrame({
    "Lider": ["Priscilla", "Gladys", "Susy", "Gerson"],
    "Cumplimiento": [90, 85, 80, 70]
})

st.bar_chart(df2.set_index("Lider"))
