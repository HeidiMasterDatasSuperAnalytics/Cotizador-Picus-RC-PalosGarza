import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Rutas de archivos
RUTA_RUTAS = "rutas_guardadas.csv"
RUTA_DATOS = "datos_generales.csv"

# ============================
# Funciones auxiliares
# ============================
def safe_number(x):
    return 0 if (x is None or (isinstance(x, float) and pd.isna(x))) else x

def cargar_datos_generales():
    if os.path.exists(RUTA_DATOS):
        return pd.read_csv(RUTA_DATOS).set_index("Parametro").to_dict()["Valor"]
    return {
        "Sueldo por Viaje": 300.0,
        "Bono ISR IMSS por Viaje": 185.06,
        "Bono Rendimiento": 0.0,
        "Rendimiento Camion": 2.5,
        "Costo Diesel": 24.0,
        "Tipo de cambio USD": 17.5,
        "Tipo de cambio MXN": 1.0
    }

def guardar_datos_generales(valores):
    df = pd.DataFrame(valores.items(), columns=["Parametro", "Valor"])
    df.to_csv(RUTA_DATOS, index=False)

valores = cargar_datos_generales()

# Cargar valores dinámicos desde datos generales
SUELDO_POR_VIAJE = float(valores.get("Sueldo por Viaje", 300))
BONO_ISR_POR_VIAJE = float(valores.get("Bono ISR IMSS por Viaje", 185.06))
BONO_RENDIMIENTO = float(valores.get("Bono Rendimiento", 0))

st.title("🚛 Captura de Rutas Cortas - PICUS")

# Configurar Datos Generales
with st.expander("⚙️ Configurar Datos Generales"):
    for key in [
        "Sueldo por Viaje", "Bono ISR IMSS por Viaje", "Bono Rendimiento",
        "Rendimiento Camion", "Costo Diesel", "Tipo de cambio USD", "Tipo de cambio MXN"
    ]:
        valores[key] = st.number_input(key, value=float(valores.get(key, 0)), step=0.1)
    if st.button("Guardar Datos Generales"):
        guardar_datos_generales(valores)
        st.success("✅ Datos Generales guardados correctamente.")

if os.path.exists(RUTA_RUTAS):
    df_rutas = pd.read_csv(RUTA_RUTAS)
else:
    df_rutas = pd.DataFrame()

st.subheader("📥 Nueva Ruta Corta")

with st.form("captura_ruta_corta"):
    col1, col2 = st.columns(2)

    with col1:
        fecha = st.date_input("Fecha", value=datetime.today())
        tipo = st.selectbox("Tipo de Ruta", ["IMPO", "EXPO", "VACIO"])
        cliente = st.text_input("Nombre Cliente")
        origen = st.text_input("Origen")
        destino = st.text_input("Destino")
        km = st.number_input("Kilómetros", min_value=0.0)
        casetas = st.number_input("Casetas", min_value=0.0)

    with col2:
        moneda_ingreso = st.selectbox("Moneda Ingreso Flete", ["MXN", "USD"])
        ingreso_flete = st.number_input("Ingreso Flete", min_value=0.0)
        moneda_cruce = st.selectbox("Moneda Ingreso Cruce", ["MXN", "USD"])
        ingreso_cruce = st.number_input("Ingreso Cruce", min_value=0.0)
        moneda_costo_cruce = st.selectbox("Moneda Costo Cruce", ["MXN", "USD"])
        costo_cruce = st.number_input("Costo Cruce", min_value=0.0)
        movimiento_local = st.number_input("Movimiento Local", min_value=0.0)
        puntualidad = st.number_input("Puntualidad", min_value=0.0)

    st.markdown("---")
    st.subheader("🧾 Costos Extras Adicionales")
    col3, col4 = st.columns(2)
    with col3:
        pistas_extra = st.number_input("Pistas Extra", min_value=0.0)
        stop = st.number_input("Stop", min_value=0.0)
        falso = st.number_input("Falso", min_value=0.0)
        pension = st.number_input("Pensión", min_value=0.0)
    with col4:
        gatas = st.number_input("Gatas", min_value=0.0)
        accesorios = st.number_input("Accesorios", min_value=0.0)
        guias = st.number_input("Guías", min_value=0.0)
        estancia = st.number_input("Estancia", min_value=0.0)

    revisar = st.form_submit_button("🔍 Revisar Ruta")
    if revisar:
        tipo_cambio_flete = valores["Tipo de cambio USD"] if moneda_ingreso == "USD" else valores["Tipo de cambio MXN"]
        tipo_cambio_cruce = valores["Tipo de cambio USD"] if moneda_cruce == "USD" else valores["Tipo de cambio MXN"]
        tipo_cambio_costo_cruce = valores["Tipo de cambio USD"] if moneda_costo_cruce == "USD" else valores["Tipo de cambio MXN"]

        ingreso_flete_convertido = ingreso_flete * tipo_cambio_flete
        ingreso_cruce_convertido = ingreso_cruce * tipo_cambio_cruce
        costo_cruce_convertido = costo_cruce * tipo_cambio_costo_cruce
        ingreso_total = ingreso_flete_convertido + ingreso_cruce_convertido

        costo_diesel_camion = (km / valores["Rendimiento Camion"]) * valores["Costo Diesel"]
        extras = sum(map(safe_number, [
            movimiento_local, puntualidad, pension, estancia,
            pistas_extra, stop, falso, gatas, accesorios, guias
        ]))

        costo_total = costo_diesel_camion + SUELDO_POR_VIAJE + BONO_ISR_POR_VIAJE + BONO_RENDIMIENTO + casetas + extras + costo_cruce_convertido

        nueva_ruta = {
            "Fecha": fecha, "Tipo": tipo, "Cliente": cliente, "Origen": origen, "Destino": destino,
            "KM": km, "Moneda": moneda_ingreso, "Ingreso_Original": ingreso_flete,
            "Tipo de cambio": tipo_cambio_flete, "Ingreso Flete": ingreso_flete_convertido,
            "Moneda_Cruce": moneda_cruce, "Cruce_Original": ingreso_cruce,
            "Tipo cambio Cruce": tipo_cambio_cruce, "Ingreso Cruce": ingreso_cruce_convertido,
            "Moneda Costo Cruce": moneda_costo_cruce, "Costo Cruce": costo_cruce,
            "Costo Cruce Convertido": costo_cruce_convertido, "Ingreso Total": ingreso_total,
            "Sueldo_Operador": SUELDO_POR_VIAJE, "Bono": BONO_ISR_POR_VIAJE,
            "Bono Rendimiento": BONO_RENDIMIENTO, "Casetas": casetas,
            "Movimiento_Local": movimiento_local, "Puntualidad": puntualidad, "Pension": pension,
            "Estancia": estancia, "Pistas Extra": pistas_extra, "Stop": stop, "Falso": falso,
            "Gatas": gatas, "Accesorios": accesorios, "Guías": guias,
            "Costo_Diesel_Camion": costo_diesel_camion, "Costo_Extras": extras,
            "Costo_Total_Ruta": costo_total, "Clasificacion Ruta": "RC"
        }

        df_rutas = pd.concat([df_rutas, pd.DataFrame([nueva_ruta])], ignore_index=True)
        df_rutas.to_csv(RUTA_RUTAS, index=False)
        st.success("✅ Ruta corta guardada exitosamente.")
        st.experimental_rerun()
