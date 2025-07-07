import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Simulación de Lectura Gamma", layout="wide")

st.title("📈 Simulación de Lectura en el Tiempo - Detector Gamma")
st.markdown("Simula cómo varía la lectura (cuentas) en un canal característico a lo largo del tiempo para diferentes radionúclidos activados.")

# --- Parámetros de radionúclidos activados ---
radionuclidos = {
    '198Au': {'E_kev': 411, 't12_min': 2.7 * 60},
    '60Co': {'E_kev': 1173, 't12_min': 1925 * 60},
    '24Na': {'E_kev': 1368, 't12_min': 15 * 60},
    '82Br': {'E_kev': 554, 't12_min': 35 * 60},
}

# --- Selección de radionúclidos ---
seleccion = st.multiselect("Selecciona los radionúclidos simulados", list(radionuclidos.keys()), default=['198Au'])

# --- Parámetros de tiempo ---
tiempo_max = st.slider("Duración de la medición (minutos)", 10, 200000, 2000)
tiempo = np.linspace(0, tiempo_max, 300)

# --- Simular lectura en el tiempo ---
cuentas_totales = np.zeros_like(tiempo)

for nuc in seleccion:
    t12 = radionuclidos[nuc]['t12_min']
    lambda_ = np.log(2) / t12
    cuentas = 1000 * np.exp(-lambda_ * tiempo)
    cuentas_totales += cuentas

# --- Agregar ruido Poisson (simula medición real) ---
if st.checkbox("Agregar ruido Poisson (lectura realista)"):
    cuentas_totales = np.random.poisson(cuentas_totales)

# --- Mostrar gráfico ---
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(tiempo, cuentas_totales, label="Cuentas simuladas", color='darkred')
ax.set_title("Simulación de Lectura en el Tiempo")
ax.set_xlabel("Tiempo (minutos)")
ax.set_ylabel("Cuentas detectadas")
ax.grid(True)
ax.legend()
st.pyplot(fig)

# --- Mostrar tabla de parámetros ---
with st.expander("📋 Parámetros de radionúclidos seleccionados"):
    for nuc in seleccion:
        datos = radionuclidos[nuc]
        st.write(f"**{nuc}** → Energía: {datos['E_kev']} keV, T½ = {datos['t12_min']/60:.2f} h")

st.caption("Simulación educativa de lectura de decaimiento gamma en el tiempo.")
