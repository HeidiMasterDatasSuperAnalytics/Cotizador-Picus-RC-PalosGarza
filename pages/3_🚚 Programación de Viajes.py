import streamlit as st
import pandas as pd
import os
from datetime import datetime

RUTA_RUTAS = "rutas_guardadas.csv"
RUTA_PROG = "viajes_programados.csv"

SUELDO_POR_VIAJE = 1500 / 5  # $300
BONO_ISR_POR_VIAJE = 925.32 / 5  # $185.06
BONO_RENDIMIENTO = 0.0

st.title("🚚 Programación de Viajes - PICUS RC")

def safe(x): return 0 if pd.isna(x) or x is None else x

def cargar_rutas():
    if not os.path.exists(RUTA_RUTAS):
        st.error("❌ No se encontró rutas_guardadas.csv")
        st.stop()
    df = pd.read_csv(RUTA_RUTAS)
    df = df[df["Clasificacion Ruta"] == "RC"]
    df["Utilidad"] = df["Ingreso Total"] - df["Costo_Total_Ruta"]
    df["% Utilidad"] = (df["Utilidad"] / df["Ingreso Total"] * 100).round(2)
    df["Ruta"] = df["Origen"] + " → " + df["Destino"]
    return df

def guardar_programacion(df_nueva):
    if os.path.exists(RUTA_PROG):
        df_prog = pd.read_csv(RUTA_PROG)
        df_total = pd.concat([df_prog, df_nueva], ignore_index=True)
    else:
        df_total = df_nueva
    df_total.to_csv(RUTA_PROG, index=False)

# ==============================
# Registro de tráfico
# ==============================
st.header("🚛 Registro de Tráfico")
rutas_df = cargar_rutas()
tipo = st.selectbox("Tipo de ruta (ida)", ["IMPO", "EXPO"])
rutas_tipo = rutas_df[rutas_df["Tipo"] == tipo].copy()

if rutas_tipo.empty:
    st.info("No hay rutas registradas de este tipo.")
    st.stop()

ruta_sel = st.selectbox("Selecciona una ruta", rutas_tipo["Ruta"].unique())
rutas_filtradas = rutas_tipo[rutas_tipo["Ruta"] == ruta_sel].sort_values(by="% Utilidad", ascending=False)

cliente_idx = st.selectbox("Cliente", rutas_filtradas.index,
    format_func=lambda x: f"{rutas_filtradas.loc[x, 'Cliente']} ({rutas_filtradas.loc[x, '% Utilidad']:.2f}%)")
ruta_ida = rutas_filtradas.loc[cliente_idx]

with st.form("registro_trafico"):
    fecha = st.date_input("Fecha de tráfico", value=datetime.today())
    trafico = st.text_input("Número de Tráfico")
    unidad = st.text_input("Unidad")
    operador = st.text_input("Operador")
    submit = st.form_submit_button("📅 Registrar Tráfico")

    if submit:
        if not trafico or not unidad or not operador:
            st.error("❌ Todos los campos son obligatorios para registrar un tráfico.")
        else:
            fecha_str = fecha.strftime("%Y-%m-%d")
            datos = ruta_ida.copy()
            datos["Fecha"] = fecha_str
            datos["Número_Trafico"] = trafico
            datos["Unidad"] = unidad
            datos["Operador"] = operador
            datos["Tramo"] = "IDA"
            datos["ID_Programacion"] = f"{trafico}_{fecha_str}"
            guardar_programacion(pd.DataFrame([datos]))
            st.success("✅ Tráfico registrado exitosamente.")

# ==============================
# Gestión y cierre de tráfico
# ==============================
st.markdown("---")
st.header("🛠️ Gestión de Tráficos Programados")

if os.path.exists(RUTA_PROG):
    df_prog = pd.read_csv(RUTA_PROG)
    df_prog = df_prog[df_prog["Clasificacion Ruta"] == "RC"] if "Clasificacion Ruta" in df_prog.columns else df_prog

    # Mostrar solo tráficos con un tramo (IDA)
    incompletos = df_prog.groupby("ID_Programacion").size().reset_index(name="Tramos")
    incompletos = incompletos[incompletos["Tramos"] == 1]["ID_Programacion"]
    ids = incompletos.tolist()

    if ids:
        id_edit = st.selectbox("Selecciona un tráfico para editar", ids)
        df_filtrado = df_prog[df_prog["ID_Programacion"] == id_edit].reset_index()
        st.write("**Vista previa del tráfico seleccionado:**")
        st.dataframe(df_filtrado)

        if not df_filtrado[df_filtrado["Tramo"] == "IDA"].empty:
            tramo_ida = df_filtrado[df_filtrado["Tramo"] == "IDA"].iloc[0]
            with st.form("editar_trafico"):
                nueva_unidad = st.text_input("Unidad", value=tramo_ida["Unidad"])
                nuevo_operador = st.text_input("Operador", value=tramo_ida["Operador"])

                col1, col2 = st.columns(2)
                with col1:
                    movimiento_local = st.number_input("Movimiento Local", min_value=0.0, value=safe(tramo_ida.get("Movimiento_Local", 0)))
                    puntualidad = st.number_input("Puntualidad", min_value=0.0, value=safe(tramo_ida.get("Puntualidad", 0)))
                    pension = st.number_input("Pensión", min_value=0.0, value=safe(tramo_ida.get("Pension", 0)))
                    estancia = st.number_input("Estancia", min_value=0.0, value=safe(tramo_ida.get("Estancia", 0)))
                    pistas_extra = st.number_input("Pistas Extra", min_value=0.0, value=safe(tramo_ida.get("Pistas Extra", 0)))
                with col2:
                    stop = st.number_input("Stop", min_value=0.0, value=safe(tramo_ida.get("Stop", 0)))
                    falso = st.number_input("Falso", min_value=0.0, value=safe(tramo_ida.get("Falso", 0)))
                    gatas = st.number_input("Gatas", min_value=0.0, value=safe(tramo_ida.get("Gatas", 0)))
                    accesorios = st.number_input("Accesorios", min_value=0.0, value=safe(tramo_ida.get("Accesorios", 0)))
                    guias = st.number_input("Guías", min_value=0.0, value=safe(tramo_ida.get("Guías", 0)))
                actualizar = st.form_submit_button("💾 Guardar cambios")
                if actualizar:
                    columnas = {
                        "Unidad": nueva_unidad,
                        "Operador": nuevo_operador,
                        "Movimiento_Local": movimiento_local,
                        "Puntualidad": puntualidad,
                        "Pension": pension,
                        "Estancia": estancia,
                        "Pistas Extra": pistas_extra,
                        "Stop": stop,
                        "Falso": falso,
                        "Gatas": gatas,
                        "Accesorios": accesorios,
                        "Guías": guias
                    }
                    for col, val in columnas.items():
                        df_prog.loc[(df_prog["ID_Programacion"] == id_edit) & (df_prog["Tramo"] == "IDA"), col] = val

                    # Recalcular costo total
                    extras = sum([safe(x) for x in columnas.values() if isinstance(x, (int, float))])
                    base = tramo_ida.get("Costo_Total_Ruta", 0) - tramo_ida.get("Costo_Extras", 0)
                    total = base + extras
                    df_prog.loc[(df_prog["ID_Programacion"] == id_edit) & (df_prog["Tramo"] == "IDA"), "Costo_Extras"] = extras
                    df_prog.loc[(df_prog["ID_Programacion"] == id_edit) & (df_prog["Tramo"] == "IDA"), "Costo_Total_Ruta"] = total

                    df_prog.to_csv(RUTA_PROG, index=False)
                    st.success("✅ Cambios guardados correctamente.")

# ==============================
# Sugerencia de regreso y conclusión
# ==============================
st.markdown("---")
st.header("🔁 Sugerencia de Vuelta y Conclusión")

if os.path.exists(RUTA_PROG):
    df_prog = pd.read_csv(RUTA_PROG)
    pendientes = df_prog.groupby("ID_Programacion").size().reset_index(name="count")
    pendientes = pendientes[pendientes["count"] == 1]["ID_Programacion"]

    if not pendientes.empty:
        id_sel = st.selectbox("Selecciona tráfico pendiente", pendientes)
        ida = df_prog[df_prog["ID_Programacion"] == id_sel].iloc[0]
        destino = ida["Destino"]
        tipo_ida = ida["Tipo"]
        tipo_regreso = "EXPO" if tipo_ida == "IMPO" else "IMPO"

        df_rutas = cargar_rutas()
        directas = df_rutas[(df_rutas["Tipo"] == tipo_regreso) & (df_rutas["Origen"] == destino)].copy()
        if not directas.empty:
            directas = directas.sort_values(by="% Utilidad", ascending=False)
            idx = st.selectbox("Ruta sugerida", directas.index,
                format_func=lambda x: f"{directas.loc[x, 'Cliente']} - {directas.loc[x, 'Ruta']} ({directas.loc[x, '% Utilidad']:.2f}%)")
            tramo = directas.loc[idx]

            tramo["Fecha"] = ida["Fecha"]
            tramo["Número_Trafico"] = ida["Número_Trafico"]
            tramo["Unidad"] = ida["Unidad"]
            tramo["Operador"] = ida["Operador"]
            tramo["ID_Programacion"] = ida["ID_Programacion"]
            tramo["Tramo"] = "VUELTA"

            if st.button("💾 Cerrar tráfico"):
                guardar_programacion(pd.DataFrame([tramo]))
                st.success("✅ Tráfico cerrado exitosamente.")

# ==============================
# Tráficos concluidos
# ==============================
st.markdown("---")
st.subheader("✅ Tráficos Concluidos")

if os.path.exists(RUTA_PROG):
    df_prog = pd.read_csv(RUTA_PROG)
    concluidos = df_prog.groupby("ID_Programacion").size().reset_index(name="Tramos")
    concluidos = concluidos[concluidos["Tramos"] >= 2]["ID_Programacion"]

    df_concluidos = df_prog[df_prog["ID_Programacion"].isin(concluidos)].copy()
    if not df_concluidos.empty:
        df_concluidos["Fecha"] = pd.to_datetime(df_concluidos["Fecha"])
        st.markdown("### 📅 Filtro por Fecha")
        col1, col2 = st.columns(2)
        with col1:
            fecha_inicio = st.date_input("Fecha inicio", value=df_concluidos["Fecha"].min().date())
        with col2:
            fecha_fin = st.date_input("Fecha fin", value=df_concluidos["Fecha"].max().date())

        filtro = (df_concluidos["Fecha"] >= pd.to_datetime(fecha_inicio)) & (df_concluidos["Fecha"] <= pd.to_datetime(fecha_fin))
        df_filtrado = df_concluidos[filtro]

        if not df_filtrado.empty:
            st.dataframe(df_filtrado)
        else:
            st.warning("No hay tráficos concluidos en ese rango de fechas.")
    else:
        st.info("No hay tráficos concluidos todavía.")
