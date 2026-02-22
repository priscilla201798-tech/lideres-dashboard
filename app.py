import streamlit as st

st.title("Prueba Secrets")

if "gcp_service_account" in st.secrets:
    st.success("Secret cargado correctamente")
else:
    st.error("Secret NO cargado")
