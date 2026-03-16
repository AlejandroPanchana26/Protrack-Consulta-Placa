import streamlit as st
import requests
import hashlib
import time
import pandas as pd

st.title("Consulta de Vehículos - Protrack")

# ==========================
# FUNCION LOGIN
# ==========================

def login(account, password):

    timestamp = str(int(time.time()))

    md5_password = hashlib.md5(password.encode()).hexdigest()
    signature = hashlib.md5((md5_password + timestamp).encode()).hexdigest()

    url = "https://api.protrack365.com/api/authorization"

    params = {
        "account": account,
        "time": timestamp,
        "signature": signature
    }

    try:

        response = requests.get(url, params=params)
        data = response.json()

        return data

    except Exception as e:

        return {
            "error": str(e)
        }


# ==========================
# INTERFAZ
# ==========================

account = st.text_input("Usuario Protrack")
password = st.text_input("Password", type="password")

if st.button("Probar conexión API"):

    if not account or not password:
        st.warning("Debes ingresar usuario y contraseña")
        st.stop()

    st.info("Conectando con API...")

    auth_data = login(account, password)

    # ==========================
    # ERROR DE CONEXION
    # ==========================

    if "error" in auth_data:

        st.error("Error de conexión")
        st.write(auth_data["error"])
        st.stop()

    # ==========================
    # RESPUESTA COMPLETA API
    # ==========================

    st.subheader("Respuesta completa del servidor")

    st.json(auth_data)

    # ==========================
    # VALIDAR LOGIN
    # ==========================

    if auth_data.get("code") != 0:

        st.error("Error de autenticación")

        st.write("Código:", auth_data.get("code"))
        st.write("Mensaje:", auth_data.get("message"))

        st.stop()

    st.success("Login exitoso")

    token = auth_data["record"]["access_token"]

    st.write("Access Token:")
    st.code(token)