import streamlit as st
import requests
import hashlib
import time
from datetime import datetime, timezone, timedelta
import pandas as pd

# Zona horaria Colombia
LOCAL_TZ = timezone(timedelta(hours=-5))

st.title("Consulta API Protrack")
st.write("Ingrese las credenciales para consultar los dispositivos y su último reporte.")

# Inputs
account = st.text_input("Usuario")
password = st.text_input("Contraseña", type="password")

if st.button("Consultar"):

    if not account or not password:
        st.warning("Debe ingresar usuario y contraseña")
        st.stop()

    # =============================
    # GENERAR TIMESTAMP Y FIRMA
    # =============================
    timestamp = str(int(time.time()))
    md5_password = hashlib.md5(password.encode()).hexdigest()
    signature = hashlib.md5((md5_password + timestamp).encode()).hexdigest()

    # =============================
    # AUTENTICACIÓN
    # =============================
    auth_url = "https://api.protrack365.com/api/authorization"

    params = {
        "account": account,
        "time": timestamp,
        "signature": signature
    }

    auth_response = requests.get(auth_url, params=params)
    auth_data = auth_response.json()

    if auth_data.get("code") != 0:
        st.error("Credenciales incorrectas o sin acceso API")
        st.stop()

    token = auth_data["record"]["access_token"]

    st.success("Autenticación exitosa")

    # =============================
    # OBTENER DISPOSITIVOS
    # =============================
    device_url = "https://api.protrack365.com/api/device/list"

    device_params = {
        "access_token": token,
        "account": account
    }

    device_response = requests.get(device_url, params=device_params)
    device_data = device_response.json()

    devices = device_data.get("record", [])

    if not devices:
        st.warning("No se encontraron dispositivos asociados")
        st.stop()

    resultados = []

    # =============================
    # CONSULTAR ÚLTIMO REPORTE
    # =============================
    for device in devices:

        plate = device.get("platenumber")
        imei = device.get("imei")

        track_url = "https://api.protrack365.com/api/track"

        track_params = {
            "access_token": token,
            "imeis": imei
        }

        track_response = requests.get(track_url, params=track_params)
        track_data = track_response.json()

        records = track_data.get("record", [])

        if records:

            timestamp = records[0].get("systemtime") or records[0].get("gpstime")

            if timestamp:

                fecha = datetime.fromtimestamp(
                    timestamp, timezone.utc
                ).astimezone(LOCAL_TZ).strftime("%Y-%m-%d %H:%M:%S")

            else:
                fecha = "Sin fecha"

        else:
            fecha = "Sin datos"

        resultados.append({
            "Placa": plate,
            "Último reporte (UTC-5)": fecha
        })

    df = pd.DataFrame(resultados)

    st.subheader("Resultados")
    st.dataframe(df, use_container_width=True)