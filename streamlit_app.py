import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Simulación de Espectro en Detector", layout="wide")

st.title("📟 Espectro Gamma Medido en el Detector")
st.markdown("Este simulador muestra cómo un detector gamma mediría el espectro después de una activación, en términos de **cuentas por segundo** o **cuentas acumuladas**.")

# --- Parámetros de radionúclidos activados ---
radionuclidos = {
    '198Au': {'E_kev': 411, 't12_min': 2.7 * 60},
    '60Co': {'E_kev': 1173, 't12_min': 1925 * 60},
    '24Na': {'E_kev': 1368, 't12_min': 15 * 60},
    '82Br': {'E_kev': 554, 't12_min': 35 * 60},
    '28Al': {'E_kev': 1779, 't12_min': 2.24},
    '56Mn': {'E_kev': 847, 't12_min': 2.58 * 60},
}

# --- Parámetros del detector ---
keV_por_canal = 0.5
resolucion = 10
canales = np.arange(0, 2048)
energias = canales * keV_por_canal

# --- Parámetros de tiempo y medición ---
t_actual = st.slider("⏱️ Tiempo desde la activación (minutos)", 0, 5000, 60)
modo = st.radio("Modo de visualización:", ["Cuentas por segundo (cps)", "Cuentas acumuladas"], horizontal=True)
tiempo_medicion = 60  # segundos
if modo == "Cuentas acumuladas":
    tiempo_medicion = st.slider("⏲️ Tiempo de medición (segundos)", 1, 3600, 60)

seleccion = st.multiselect("📡 Radionúclidos activados", list(radionuclidos.keys()), default=['198Au', '56Mn'])
agregar_ruido = st.checkbox("Agregar ruido Poisson", value=True)

# --- Simulación del espectro ---
espectro = np.zeros_like(canales, dtype=float)

for nuc in seleccion:
    datos = radionuclidos[nuc]
    energia = datos['E_kev']
    canal_central = int(energia / keV_por_canal)
    t12 = datos['t12_min']
    
    # Tasa de cuentas por segundo (decaimiento desde el tiempo 0)
    cps = np.exp(-np.log(2) * t_actual / t12) * 100  # cps arbitraria
    
    # Cuentas en el intervalo de medición
    cuentas = cps * tiempo_medicion if modo == "Cuentas acumuladas" else cps
    
    # Pico Gaussiano
    pico = cuentas * np.exp(-0.5 * ((canales - canal_central) / resolucion) ** 2)
    espectro += pico

# --- Agregar ruido ---
if agregar_ruido:
    espectro = np.random.poisson(espectro)

# --- Graficar espectro ---
fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(energias, espectro, color='teal')
ax.set_title(f"Espectro Gamma Simulado - {modo} a {t_actual} minutos")
ax.set_xlabel("Energía (keV)")
ax.set_ylabel("Cuentas" if modo == "Cuentas acumuladas" else "Cuentas por segundo (cps)")
ax.set_xlim(0, 2000)
ax.grid(True)
st.pyplot(fig)

# --- Mostrar tabla de radionúclidos seleccionados ---
with st.expander("📋 Parámetros de radionúclidos"):
    for nuc in seleccion:
        datos = radionuclidos[nuc]
        st.write(f"**{nuc}** → {datos['E_kev']} keV, T½ = {datos['t12_min']/60:.2f} h")

st.caption("Simulación educativa del espectro gamma medido por un detector tras activación neutrónica.")
