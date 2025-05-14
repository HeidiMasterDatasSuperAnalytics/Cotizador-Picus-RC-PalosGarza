import streamlit as st
import pandas as pd
import os

RUTA_RUTAS = "rutas_guardadas.csv"
SUELDO_POR_VIAJE = 1500 / 5  # $300
BONO_ISR_POR_VIAJE = 925.32 / 5  # $185.06
BONO_RENDIMIENTO = 0.0

st.title("🔁 Simulador Vuelta Redonda - PICUS RC")

def safe(x):
    return 0 if pd.isna(x) or x is None else x

def cargar_rutas():
    if os.path.exists(RUTA_RUTAS):
        df = pd.read_csv(RUTA_RUTAS)
        df = df[df["Clasificacion Ruta"] == "RC"]
        if df.empty:
            st.warning("No hay rutas clasificadas como RC registradas.")
            st.stop()
        df["Ruta"] = df["Origen"] + " → " + df["Destino"]
        df["Utilidad"] = df["Ingreso Total"] - df["Costo_Total_Ruta"]
        df["% Utilidad"] = (df["Utilidad"] / df["Ingreso Total"] * 100).round(2)
        return df
    st.error("❌ No se encontró rutas_guardadas.csv")
    st.stop()

df_rutas = cargar_rutas()

st.subheader("📌 Paso 1: Selecciona tipo de ruta principal")
tipo_principal = st.selectbox("Tipo de ruta inicial", ["IMPO", "EXPO", "VACIO"])
rutas_principales = df_rutas[df_rutas["Tipo"] == tipo_principal].copy()

if rutas_principales.empty:
    st.warning(f"No hay rutas tipo {tipo_principal} registradas.")
    st.stop()

ruta_sel = st.selectbox("Selecciona una ruta", rutas_principales["Ruta"].unique())
rutas_filtradas = rutas_principales[rutas_principales["Ruta"] == ruta_sel].copy()
rutas_filtradas = rutas_filtradas.sort_values(by="% Utilidad", ascending=False)

cliente_idx = st.selectbox("Cliente (ordenado por % utilidad)", rutas_filtradas.index,
    format_func=lambda x: f"{rutas_filtradas.loc[x, 'Cliente']} ({rutas_filtradas.loc[x, '% Utilidad']:.2f}%)")
ruta1 = rutas_filtradas.loc[cliente_idx]

st.subheader("📌 Paso 2: Ruta intermedia sugerida (opcional)")
destino1 = ruta1["Destino"]
vacios = df_rutas[(df_rutas["Tipo"] == "VACIO") & (df_rutas["Origen"] == destino1)].copy()

opcion_intermedia = None
if not vacios.empty:
    vacios = vacios.sort_values(by="% Utilidad", ascending=False)
    idx = st.selectbox("Ruta vacía sugerida", vacios.index,
        format_func=lambda x: f"{vacios.loc[x, 'Ruta']} ({vacios.loc[x, 'Cliente']})")
    opcion_intermedia = vacios.loc[idx]

st.subheader("📌 Paso 3: Ruta final sugerida")
origen_final = opcion_intermedia["Destino"] if opcion_intermedia is not None else ruta1["Destino"]

if tipo_principal == "IMPO":
    tipo_final = "EXPO"
elif tipo_principal == "EXPO":
    tipo_final = "IMPO"
else:
    tipo_final = "EXPO"

rutas_finales = df_rutas[(df_rutas["Tipo"] == tipo_final) & (df_rutas["Origen"] == origen_final)].copy()
ruta3 = None
if not rutas_finales.empty:
    rutas_finales = rutas_finales.sort_values(by="% Utilidad", ascending=False)
    idx = st.selectbox("Ruta final sugerida", rutas_finales.index,
        format_func=lambda x: f"{rutas_finales.loc[x, 'Cliente']} - {rutas_finales.loc[x, 'Ruta']}")
    ruta3 = rutas_finales.loc[idx]

rutas_seleccionadas = [ruta1]
if opcion_intermedia is not None:
    rutas_seleccionadas.append(opcion_intermedia)
if ruta3 is not None:
    rutas_seleccionadas.append(ruta3)

st.header("🛤️ Rutas Seleccionadas")
for r in rutas_seleccionadas:
    st.markdown(f"**{r['Tipo']}** | {r['Origen']} → {r['Destino']} | Cliente: {r['Cliente']}")

# =====================
# Cálculos por ruta
# =====================
detalle = []
ingreso_total = 0
costo_total = 0

for r in rutas_seleccionadas:
    ingreso = safe(r["Ingreso Total"])
    costo = safe(r["Costo_Total_Ruta"])
    extras = safe(r.get("Costo_Extras", 0))
    tipo = r["Tipo"]

    total_costos = costo + SUELDO_POR_VIAJE + BONO_ISR_POR_VIAJE + BONO_RENDIMIENTO

    ingreso_total += ingreso
    costo_total += total_costos

    detalle.append({
        "Tipo": tipo,
        "Cliente": r["Cliente"],
        "Ruta": r["Origen"] + " → " + r["Destino"],
        "Ingreso": ingreso,
        "Costo Base": costo,
        "Sueldo": SUELDO_POR_VIAJE,
        "Bono": BONO_ISR_POR_VIAJE,
        "Extras": extras,
        "Rendimiento": BONO_RENDIMIENTO,
        "Total Ruta": total_costos
    })

utilidad_bruta = ingreso_total - costo_total
costos_indirectos = ingreso_total * 0.35
utilidad_neta = utilidad_bruta - costos_indirectos

st.header("📊 Resultados Generales")
st.metric("Ingreso Total", f"${ingreso_total:,.2f}")
st.metric("Costo Total", f"${costo_total:,.2f}")
st.metric("Utilidad Bruta", f"${utilidad_bruta:,.2f} ({(utilidad_bruta/ingreso_total*100):.2f}%)")
st.metric("Costos Indirectos (35%)", f"${costos_indirectos:,.2f}")
st.metric("Utilidad Neta", f"${utilidad_neta:,.2f} ({(utilidad_neta/ingreso_total*100):.2f}%)")

st.subheader("📋 Detalle por Ruta")
st.dataframe(pd.DataFrame(detalle), use_container_width=True)
