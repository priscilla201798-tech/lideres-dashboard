import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(layout="wide")

# =========================
# 🎨 ESTILOS PRO
# =========================
st.markdown("""
<style>

/* FONDO GENERAL */
.stApp {
    background-color: #f4f6f9;
}

/* SIDEBAR */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg,#0f1c2e,#1c2f4a);
}

/* TITULO SIDEBAR */
.sidebar-title {
    font-size: 18px;
    font-weight: 600;
    color: white;
    margin-top: 10px;
}

/* LABELS SIDEBAR */
label, .stSelectbox label, .stDateInput label {
    color: white !important;
    font-weight: 500;
}

/* CARDS */
.card {
    background: linear-gradient(135deg,#1f3b63,#2d4e7a);
    padding: 25px;
    border-radius: 14px;
    box-shadow: 0px 6px 18px rgba(0,0,0,0.15);
    text-align: center;
}

.card-title {
    color: #cfd8e3;
    font-size: 14px;
}

.card-value {
    color: white;
    font-size: 28px;
    font-weight: 700;
}

/* HEADER SUPERIOR */
.header-bar {
    background: #1f3b63;
    padding: 15px 20px;
    border-radius: 12px;
    color: white;
    font-size: 15px;
    margin-bottom: 25px;
}

</style>
""", unsafe_allow_html=True)

# =========================
# 🏛 SIDEBAR
# =========================
with st.sidebar:

    st.image("logo_blanco.png", width=140)

    st.markdown(
        "<div class='sidebar-title'>Iglesia Evangélica de Liberación y Avivamiento</div>",
        unsafe_allow_html=True
    )

    st.markdown("---")

    st.markdown("### 🔐 ACCESO")

    rol = st.selectbox("Rol", ["Líder", "Supervisor"])
    dni = st.text_input("DNI")

    st.markdown("### 📅 PERÍODO")
    desde = st.date_input("Desde", datetime(2026,1,1))
    hasta = st.date_input("Hasta", datetime(2026,12,31))


# =========================
# 🧠 CONTENIDO PRINCIPAL
# =========================

st.title("Dashboard de Líderes")

st.markdown("""
<div class="header-bar">
Líder: PRISCILLA BERENICE ALARCÓN AGUIRRE | Ministerio: MUSICAL | Proceso: Operativo
</div>
""", unsafe_allow_html=True)

# =========================
# 📊 CARDS
# =========================

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class="card">
        <div class="card-title">Asistencia Total</div>
        <div class="card-value">33</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="card">
        <div class="card-title">Eventos Espirituales</div>
        <div class="card-value">4</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="card">
        <div class="card-title">Reuniones Realizadas</div>
        <div class="card-value">5</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="card">
        <div class="card-title">% Cumplimiento</div>
        <div class="card-value">82%</div>
    </div>
    """, unsafe_allow_html=True)


# =========================
# 📈 GRÁFICO EJEMPLO
# =========================

st.subheader("Asistencia Dominical")

data = pd.DataFrame({
    "Equipo": ["Musical", "Adolescentes", "Pre-Adolescentes"],
    "Asistencia": [18, 12, 9]
})

st.bar_chart(data.set_index("Equipo"))

st.subheader("Avance de Objetivos")
st.progress(0.65)

st.subheader("Eventos Espirituales (Ejecutado / Programado)")
st.write("Ayuno: 2 / 5")
st.write("Vigilia: 1 / 3")
