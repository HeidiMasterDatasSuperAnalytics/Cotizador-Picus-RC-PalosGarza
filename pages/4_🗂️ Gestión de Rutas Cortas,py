import streamlit as st
import pandas as pd
import os
from datetime import datetime

RUTA_RUTAS = "rutas_guardadas.csv"

SUELDO_POR_VIAJE = 1500 / 5  # $300
BONO_ISR_POR_VIAJE = 925.32 / 5  # $185.06
BONO_RENDIMIENTO = 0.0

st.title("🗂️ Gestión de Rutas Cortas - PICUS RC")

def safe_number(x):
    return 0 if (x is None or (isinstance(x, float) and pd.isna(x))) else x

if os.path.exists(RUTA_RUTAS):
    df = pd.read_csv(RUTA_RUTAS)
    df = df[df["Clasificacion Ruta"] == "RC"]

    if df.empty:
        st.warning("⚠️ No hay rutas cortas registradas todavía.")
        st.stop()

    st.subheader("📋 Rutas Registradas")
    st.dataframe(df, use_container_width=True)
    st.markdown(f"**Total de rutas registradas:** {len(df)}")
    st.markdown("---")

    st.subheader("🗑️ Eliminar rutas")
    indices = st.multiselect("Selecciona los índices a eliminar", df.index.tolist())
    if st.button("Eliminar rutas seleccionadas") and indices:
        df.drop(index=indices, inplace=True)
        df.reset_index(drop=True, inplace=True)
        df.to_csv(RUTA_RUTAS, index=False)
        st.success("✅ Rutas eliminadas correctamente.")
        st.experimental_rerun()

    st.markdown("---")
    st.subheader("✏️ Editar Ruta Existente")
    indice_editar = st.selectbox("Selecciona el índice a editar", df.index.tolist())
    if indice_editar is not None:
        ruta = df.loc[indice_editar]
        st.markdown("### Modifica los valores de la ruta:")
        with st.form("editar_ruta"):
            col1, col2 = st.columns(2)
            with col1:
                fecha = st.date_input("Fecha", pd.to_datetime(ruta.get("Fecha", pd.Timestamp.now())))
                tipo = st.selectbox("Tipo", ["IMPO", "EXPO", "VACIO"], index=["IMPO", "EXPO", "VACIO"].index(ruta.get("Tipo", "IMPO")))
                cliente = st.text_input("Cliente", value=ruta.get("Cliente", ""))
                origen = st.text_input("Origen", value=ruta.get("Origen", ""))
                destino = st.text_input("Destino", value=ruta.get("Destino", ""))
                km = st.number_input("Kilómetros", min_value=0.0, value=float(ruta.get("KM", 0.0)))
                casetas = st.number_input("Casetas", min_value=0.0, value=float(ruta.get("Casetas", 0.0)))

            with col2:
                moneda_ingreso = st.selectbox("Moneda Flete", ["MXN", "USD"], index=["MXN", "USD"].index(ruta.get("Moneda", "MXN")))
                ingreso_original = st.number_input("Ingreso Flete Original", min_value=0.0, value=float(ruta.get("Ingreso_Original", 0.0)))
                moneda_cruce = st.selectbox("Moneda Cruce", ["MXN", "USD"], index=["MXN", "USD"].index(ruta.get("Moneda_Cruce", "MXN")))
                ingreso_cruce = st.number_input("Ingreso Cruce Original", min_value=0.0, value=float(ruta.get("Cruce_Original", 0.0)))
                moneda_costo_cruce = st.selectbox("Moneda Costo Cruce", ["MXN", "USD"], index=["MXN", "USD"].index(ruta.get("Moneda Costo Cruce", "MXN")))
                costo_cruce = st.number_input("Costo Cruce", min_value=0.0, value=float(ruta.get("Costo Cruce", 0.0)))
                movimiento_local = st.number_input("Movimiento Local", min_value=0.0, value=float(ruta.get("Movimiento_Local", 0.0)))
                puntualidad = st.number_input("Puntualidad", min_value=0.0, value=float(ruta.get("Puntualidad", 0.0)))

            st.markdown("### 🧾 Costos Extras")
            col3, col4 = st.columns(2)
            with col3:
                pistas_extra = st.number_input("Pistas Extra", min_value=0.0, value=float(ruta.get("Pistas Extra", 0.0)))
                stop = st.number_input("Stop", min_value=0.0, value=float(ruta.get("Stop", 0.0)))
                falso = st.number_input("Falso", min_value=0.0, value=float(ruta.get("Falso", 0.0)))
                pension = st.number_input("Pensión", min_value=0.0, value=float(ruta.get("Pension", 0.0)))
            with col4:
                gatas = st.number_input("Gatas", min_value=0.0, value=float(ruta.get("Gatas", 0.0)))
                accesorios = st.number_input("Accesorios", min_value=0.0, value=float(ruta.get("Accesorios", 0.0)))
                guias = st.number_input("Guías", min_value=0.0, value=float(ruta.get("Guías", 0.0)))
                estancia = st.number_input("Estancia", min_value=0.0, value=float(ruta.get("Estancia", 0.0)))

            guardar = st.form_submit_button("📅 Guardar cambios")

            if guardar:
                tc_usd = 17.5
                tc_mxn = 1.0
                tipo_cambio_flete = tc_usd if moneda_ingreso == "USD" else tc_mxn
                tipo_cambio_cruce = tc_usd if moneda_cruce == "USD" else tc_mxn
                tipo_cambio_costo_cruce = tc_usd if moneda_costo_cruce == "USD" else tc_mxn

                ingreso_flete_convertido = ingreso_original * tipo_cambio_flete
                ingreso_cruce_convertido = ingreso_cruce * tipo_cambio_cruce
                ingreso_total = ingreso_flete_convertido + ingreso_cruce_convertido
                costo_cruce_convertido = costo_cruce * tipo_cambio_costo_cruce

                costo_diesel_camion = (km / 2.5) * 24.0
                extras = sum(map(safe_number, [
                    movimiento_local, puntualidad, pension, estancia,
                    pistas_extra, stop, falso, gatas, accesorios, guias
                ]))

                costo_total = costo_diesel_camion + SUELDO_POR_VIAJE + BONO_ISR_POR_VIAJE + BONO_RENDIMIENTO + casetas + extras + costo_cruce_convertido

                # Guardar cambios
                df.at[indice_editar, "Fecha"] = fecha
                df.at[indice_editar, "Tipo"] = tipo
                df.at[indice_editar, "Cliente"] = cliente
                df.at[indice_editar, "Origen"] = origen
                df.at[indice_editar, "Destino"] = destino
                df.at[indice_editar, "KM"] = km
                df.at[indice_editar, "Moneda"] = moneda_ingreso
                df.at[indice_editar, "Ingreso_Original"] = ingreso_original
                df.at[indice_editar, "Tipo de cambio"] = tipo_cambio_flete
                df.at[indice_editar, "Ingreso Flete"] = ingreso_flete_convertido
                df.at[indice_editar, "Moneda_Cruce"] = moneda_cruce
                df.at[indice_editar, "Cruce_Original"] = ingreso_cruce
                df.at[indice_editar, "Tipo cambio Cruce"] = tipo_cambio_cruce
                df.at[indice_editar, "Ingreso Cruce"] = ingreso_cruce_convertido
                df.at[indice_editar, "Ingreso Total"] = ingreso_total
                df.at[indice_editar, "Moneda Costo Cruce"] = moneda_costo_cruce
                df.at[indice_editar, "Costo Cruce"] = costo_cruce
                df.at[indice_editar, "Costo Cruce Convertido"] = costo_cruce_convertido
                df.at[indice_editar, "Sueldo_Operador"] = SUELDO_POR_VIAJE
                df.at[indice_editar, "Bono"] = BONO_ISR_POR_VIAJE
                df.at[indice_editar, "Bono Rendimiento"] = BONO_RENDIMIENTO
                df.at[indice_editar, "Casetas"] = casetas
                df.at[indice_editar, "Movimiento_Local"] = movimiento_local
                df.at[indice_editar, "Puntualidad"] = puntualidad
                df.at[indice_editar, "Pension"] = pension
                df.at[indice_editar, "Estancia"] = estancia
                df.at[indice_editar, "Pistas Extra"] = pistas_extra
                df.at[indice_editar, "Stop"] = stop
                df.at[indice_editar, "Falso"] = falso
                df.at[indice_editar, "Gatas"] = gatas
                df.at[indice_editar, "Accesorios"] = accesorios
                df.at[indice_editar, "Guías"] = guias
                df.at[indice_editar, "Costo_Diesel_Camion"] = costo_diesel_camion
                df.at[indice_editar, "Costo_Extras"] = extras
                df.at[indice_editar, "Costo_Total_Ruta"] = costo_total

                df.to_csv(RUTA_RUTAS, index=False)
                st.success("✅ Ruta actualizada exitosamente.")
                st.stop()
else:
    st.warning("⚠️ No hay rutas guardadas todavía.")
