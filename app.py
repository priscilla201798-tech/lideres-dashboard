from google.oauth2.service_account import Credentials
import streamlit as st
import gspread
import pandas as pd

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

def cargar_data():

    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=SCOPES
    )

    client = gspread.authorize(creds)
    sh = client.open("PLATAFORMA REGISTROS – BASE DE DATOS")

    registros = pd.DataFrame(
        sh.worksheet("REGISTROS_SEMANALES").get_all_records()
    )

    objetivos = pd.DataFrame(
        sh.worksheet("OBJETIVOS_DEL_LIDER").get_all_records()
    )

    eventos = pd.DataFrame(
        sh.worksheet("EVENTOS_ESPIRITUALES").get_all_records()
    )

    objetivos_manual = pd.DataFrame(
        sh.worksheet("BD_OBJETIVOS_ANALISIS").get_all_records()
    )

    return registros, objetivos, eventos, objetivos_manual
