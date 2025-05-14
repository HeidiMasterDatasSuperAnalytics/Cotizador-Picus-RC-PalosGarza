import streamlit as st
import pandas as pd
import os

RUTA_RUTAS = "rutas_guardadas.csv"
RUTA_DATOS = "datos_generales.csv"

SUELDO_POR_VIAJE = 1500 / 5  # $300
BONO_ISR_POR_VIAJE = 925.32 / 5  # $185.06
BONO_RENDIMIENTO = 0.0

st.title("🔍 Consulta Individual de Ruta - PICUS RC")

def safe(x):
    return 0 if pd.isna(x) or x is None else x

if os.path.exists(RUTA_RUTAS):
    df = pd.read_csv(RUTA_RUTAS)
    df = df[df["Clasificacion Ruta"] == "RC"]  # Solo rutas cortas

    if df.empty:
        st.warning("⚠️ No hay rutas clasificadas como RC registradas.")
        st.stop()

    st.subheader("📌 Selecciona una Ruta")
    index_sel = st.selectbox(
        "Selecciona índice",
        df.index.tolist(),
        format_func=lambda x: f"{df.loc[x, 'Tipo']} - {df.loc[x, 'Cliente']} - {df.loc[x, 'Origen']} → {df.loc[x, 'Destino']}"
    )

    ruta = df.loc[index_sel]

    ingreso_total = safe(ruta.get("Ingreso Total", 0))
    costo_total = safe(ruta.get("Costo_Total_Ruta", 0))
    utilidad_bruta = ingreso_total - costo_total
    costos_indirectos = ingreso_total * 0.35
    utilidad_neta = utilidad_bruta - costos_indirectos

    porcentaje_bruta = (utilidad_bruta / ingreso_total * 100) if ingreso_total > 0 else 0
    porcentaje_neta = (utilidad_neta / ingreso_total * 100) if ingreso_total > 0 else 0

    def colored_bold(label, value, condition):
        color = "green" if condition else "red"
        return f"<strong>{label}:</strong> <span style='color:{color}; font-weight:bold'>{value}</span>"

    st.markdown("---")
    st.subheader("📊 Ingresos y Utilidades")
    st.write(f"**Ingreso Total:** ${ingreso_total:,.2f}")
    st.write(f"**Costo Total:** ${costo_total:,.2f}")
    st.markdown(colored_bold("Utilidad Bruta", f"${utilidad_bruta:,.2f}", utilidad_bruta >= 0), unsafe_allow_html=True)
    st.markdown(colored_bold("% Utilidad Bruta", f"{porcentaje_bruta:.2f}%", porcentaje_bruta >= 50), unsafe_allow_html=True)
    st.write(f"**Costos Indirectos (35%):** ${costos_indirectos:,.2f}")
    st.markdown(colored_bold("Utilidad Neta", f"${utilidad_neta:,.2f}", utilidad_neta >= 0), unsafe_allow_html=True)
    st.markdown(colored_bold("% Utilidad Neta", f"{porcentaje_neta:.2f}%", porcentaje_neta >= 15), unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("📋 Detalles y Costos de la Ruta")

    costo_diesel = safe(ruta.get("Costo_Diesel_Camion", 0))
    costo_extras = safe(ruta.get("Costo_Extras", 0))
    casetas = safe(ruta.get("Casetas", 0))

    detalles = [
        f"Fecha: {ruta['Fecha']}",
        f"Tipo: {ruta['Tipo']}",
        f"Cliente: {ruta['Cliente']}",
        f"Origen → Destino: {ruta['Origen']} → {ruta['Destino']}",
        f"KM: {safe(ruta['KM']):,.2f}",
        f"Moneda Flete: {ruta['Moneda']}",
        f"Ingreso Flete Original: ${safe(ruta['Ingreso_Original']):,.2f}",
        f"Tipo de cambio: {safe(ruta['Tipo de cambio']):,.2f}",
        f"Ingreso Flete Convertido: ${safe(ruta['Ingreso Flete']):,.2f}",
        f"Moneda Cruce: {ruta['Moneda_Cruce']}",
        f"Ingreso Cruce Original: ${safe(ruta['Cruce_Original']):,.2f}",
        f"Tipo cambio Cruce: {safe(ruta['Tipo cambio Cruce']):,.2f}",
        f"Ingreso Cruce Convertido: ${safe(ruta['Ingreso Cruce']):,.2f}",
        f"Moneda Costo Cruce: {ruta['Moneda Costo Cruce']}",
        f"Costo Cruce Original: ${safe(ruta['Costo Cruce']):,.2f}",
        f"Costo Cruce Convertido: ${safe(ruta['Costo Cruce Convertido']):,.2f}",
        f"Diesel Camion: ${costo_diesel:,.2f}",
        f"Sueldo Operador (fijo): ${SUELDO_POR_VIAJE:,.2f}",
        f"Bono ISR IMSS (fijo): ${BONO_ISR_POR_VIAJE:,.2f}",
        f"Bono Rendimiento: ${BONO_RENDIMIENTO:,.2f}",
        f"Casetas: ${casetas:,.2f}",
        "---",
        "**🧾 Desglose Extras:**",
        f"- Movimiento Local: ${safe(ruta['Movimiento_Local']):,.2f}",
        f"- Puntualidad: ${safe(ruta['Puntualidad']):,.2f}",
        f"- Pensión: ${safe(ruta['Pension']):,.2f}",
        f"- Estancia: ${safe(ruta['Estancia']):,.2f}",
        f"- Pistas Extra: ${safe(ruta['Pistas Extra']):,.2f}",
        f"- Stop: ${safe(ruta['Stop']):,.2f}",
        f"- Falso: ${safe(ruta['Falso']):,.2f}",
        f"- Gatas: ${safe(ruta['Gatas']):,.2f}",
        f"- Accesorios: ${safe(ruta['Accesorios']):,.2f}",
        f"- Guías: ${safe(ruta['Guías']):,.2f}"
    ]

    for line in detalles:
        st.write(line)

else:
    st.warning("⚠️ No hay rutas guardadas todavía.")
