import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Simulación de Espectro Gamma en AAN", layout="wide")

st.title("🔬 Simulación del Espectro Gamma en el Tiempo - AAN")
st.markdown("Este simulador muestra cómo evoluciona el espectro gamma en función del tiempo (en minutos) tras una irradiación nuclear.")

# --- Parámetros de radionúclidos activados ---
radionuclidos = {
    '198Au': {'E_kev': 411, 't12_min': 2.7 * 60},    # 2.7 h
    '60Co': {'E_kev': 1173, 't12_min': 1925 * 60},   # 1925 h
    '24Na': {'E_kev': 1368, 't12_min': 15 * 60},     # 15 h
    '82Br': {'E_kev': 554, 't12_min': 35 * 60},      # 35 h
}

# --- Control de tiempo ---
t_actual = st.slider("⏱️ Tiempo desde la activación (minutos)", 0, 200000, 60)

# --- Generación del espectro ---
canales = np.linspace(0, 2048, 2048)
espectro = np.zeros_like(canales)

for nuc, datos in radionuclidos.items():
    energia = datos['E_kev']
    canal = int(energia * 2)  # 0.5 keV por canal (asumido)
    t12 = datos['t12_min']
    intensidad = np.exp(-np.log(2) * t_actual / t12) * 1000  # decaimiento exponencial
    ancho = 10
    espectro += intensidad * np.exp(-0.5 * ((canales - canal) / ancho)**2)

# --- Mostrar gráfico ---
fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(canales, espectro, color='royalblue')
ax.set_title(f"Espectro Gamma Simulado - {t_actual} minutos después de la activación")
ax.set_xlabel("Canal (relacionado con energía)")
ax.set_ylabel("Cuentas")
ax.grid(True)
st.pyplot(fig)

# --- Mostrar información de radionúclidos ---
with st.expander("📋 Ver radionúclidos simulados"):
    for k, v in radionuclidos.items():
        st.write(f"**{k}**: {v['E_kev']} keV, T½ = {v['t12_min']/60:.2f} horas")

# --- Créditos ---
st.caption("Desarrollado para fines educativos en análisis por activación neutrónica.")
