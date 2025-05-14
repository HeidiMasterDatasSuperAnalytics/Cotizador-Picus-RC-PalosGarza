import streamlit as st
from PIL import Image
import base64
import os

# Ruta al logo personalizado
LOGO_PATH = "Picus BG.png"

@st.cache_data
def image_to_base64(img_path):
    with open(img_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

if os.path.exists(LOGO_PATH):
    logo_b64 = image_to_base64(LOGO_PATH)
    st.markdown(f"""
        <div style='text-align: center;'>
            <img src="data:image/png;base64,{logo_b64}" style="height: 120px; margin-bottom: 20px;">
        </div>
    """, unsafe_allow_html=True)

st.markdown("""
    <h1 style='text-align: center; color: #003366;'>Sistema Cotizador PICUS RC</h1>
    <p style='text-align: center;'>Rutas Cortas | Control de costos, simulación y rentabilidad</p>
    <hr style='margin-top: 20px; margin-bottom: 30px;'>
""", unsafe_allow_html=True)

st.subheader("📂 Módulos disponibles")
st.markdown("""
- **🛣️ Captura de Rutas:** Registrar nueva ruta corta
- **🔍 Consulta Individual de Ruta:** Ver utilidad y desglose por ruta
- **🔁 Simulador Vuelta Redonda:** Armar combinaciones de ida-vuelta
- **🚚 Programación de Viajes:** Registrar tráficos por fecha
- **🗂️ Gestión de Rutas:** Editar o eliminar rutas
- **📂 Archivos:** Respaldar o restaurar información
""")

st.info("Selecciona una opción desde el menú lateral para comenzar")
