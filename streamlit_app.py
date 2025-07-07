import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Espectro Gamma en el Tiempo", layout="wide")

st.title("📊 Simulación de Espectro Gamma en el Tiempo")
st.markdown("Simula cómo se mide el espectro gamma en un detector después de una activación nuclear, en función del tiempo.")

# --- Radionúclidos simulados (energía y vida media en minutos) ---
radionuclidos = {
    '198Au': {'E_kev': 411, 't12_min': 2.7 * 60},
    '60Co': {'E_kev': 1173, 't12_min': 1925 * 60},
    '24Na': {'E_kev': 1368, 't12_min': 15 * 60},
    '82Br': {'E_kev': 554, 't12_min': 35 * 60},
}

# --- Parámetros de detector ---
resolucion = 10  # ancho de pico (en canales)
keV_por_canal = 0.5
canales = np.arange(0, 2048)
energias = canales * keV_por_canal

# --- Parámetros de simulación ---
t_actual = st.slider("⏱️ Tiempo después de activación (minutos)", 0, 200000, 60)
seleccion = st.multiselect("Selecciona los radionúclidos activados", list(radionuclidos.keys()), default=['198Au', '24Na'])
agregar_ruido = st.checkbox("Agregar ruido Poisson", value=True)

# --- Simulación del espectro en ese tiempo ---
espectro = np.zeros_like(canales, dtype=float)

for nuc in seleccion:
    datos = radionuclidos[nuc]
    energia = datos['E_kev']
    canal_central = int(energia / keV_por_canal)
    t12 = datos['t12_min']
    intensidad = np.exp(-np.log(2) * t_actual / t12) * 1000  # decaimiento

    # Generar pico gaussiano
    pico = intensidad * np.exp(-0.5 * ((canales - canal_central) / resolucion) ** 2)
    espectro += pico

# --- Ruido Poisson ---
if agregar_ruido:
    espectro = np.random.poisson(espectro)

# --- Graficar espectro ---
fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(energias, espectro, color='royalblue')
ax.set_title(f"Espectro Gamma Simulado - {t_actual} minutos después de la activación")
ax.set_xlabel("Energía (keV)")
ax.set_ylabel("Cuentas")
ax.set_xlim(0, 1600)
ax.grid(True)
st.pyplot(fig)

# --- Tabla de información ---
with st.expander("📋 Parámetros de los radionúclidos simulados"):
    for nuc in seleccion:
        st.write(f"**{nuc}**: Energía pico = {radionuclidos[nuc]['E_kev']} keV, T½ = {radionuclidos[nuc]['t12_min']/60:.2f} h")

st.caption("Simulación educativa de espectros gamma para análisis por activación neutrónica.")
