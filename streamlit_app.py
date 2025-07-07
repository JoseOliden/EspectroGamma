import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Espectro Gamma Realista", layout="wide")

st.title("📟 Simulación Realista de Espectro Gamma Medido")
st.markdown("Este simulador muestra un espectro gamma con picos de radionúclidos activados, ruido estadístico (Poisson) y fondo continuo simulado.")

# --- Radionúclidos simulados ---
radionuclidos = {
    '198Au': {'E_kev': 411, 't12_min': 2.7 * 60},
    '60Co': {'E_kev': 1173, 't12_min': 1925 * 60},
    '24Na': {'E_kev': 1368, 't12_min': 15 * 60},
    '82Br': {'E_kev': 554, 't12_min': 35 * 60},
    '28Al': {'E_kev': 1779, 't12_min': 2.24},
    '56Mn': {'E_kev': 847, 't12_min': 2.58 * 60},
}

# --- Detector y energía ---
keV_por_canal = 0.5
resolucion = 10
canales = np.arange(0, 2048)
energias = canales * keV_por_canal

# --- Parámetros usuario ---
t_actual = st.slider("⏱️ Tiempo desde la activación (minutos)", 0, 5000, 60)
modo = st.radio("Modo:", ["Cuentas por segundo (cps)", "Cuentas acumuladas"], horizontal=True)
tiempo_medicion = st.slider("⏲️ Tiempo de medición (segundos)", 1, 3600, 60) if modo == "Cuentas acumuladas" else 1
seleccion = st.multiselect("📡 Radionúclidos activados", list(radionuclidos.keys()), default=['198Au', '56Mn'])
agregar_ruido = st.checkbox("Agregar ruido Poisson", value=True)
fondo_continuo = st.checkbox("Agregar fondo continuo simulado", value=True)

# --- Simular espectro ---
espectro = np.zeros_like(canales, dtype=float)

for nuc in seleccion:
    datos = radionuclidos[nuc]
    energia = datos['E_kev']
    canal_central = int(energia / keV_por_canal)
    t12 = datos['t12_min']

    cps = np.exp(-np.log(2) * t_actual / t12) * 100  # intensidad base
    cuentas = cps * tiempo_medicion if modo == "Cuentas acumuladas" else cps
    pico = cuentas * np.exp(-0.5 * ((canales - canal_central) / resolucion) ** 2)
    espectro += pico

# --- Agregar fondo continuo (simple, tipo Compton o ambiental) ---
if fondo_continuo:
    fondo = 5 + 30 * np.exp(-energias / 500)  # fondo decreciente con energía
    fondo *= tiempo_medicion  # escalar con tiempo
    espectro += fondo

# --- Ruido Poisson ---
if agregar_ruido:
    espectro = np.random.poisson(espectro)

# --- Graficar ---
fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(energias, espectro, color='darkgreen')
ax.set_title(f"Espectro Gamma Simulado ({modo}) - {t_actual} min post activación")
ax.set_xlabel("Energía (keV)")
ax.set_ylabel("Cuentas" if modo == "Cuentas acumuladas" else "Cuentas por segundo (cps)")
ax.set_xlim(0, 2000)
ax.grid(True)
st.pyplot(fig)

# --- Detalles ---
with st.expander("📋 Información de radionúclidos activados"):
    for nuc in seleccion:
        datos = radionuclidos[nuc]
        st.write(f"**{nuc}** → {datos['E_kev']} keV, T½ = {datos['t12_min']/60:.2f} h")

st.caption("Simulación educativa con decaimiento, picos gamma, ruido y fondo continuo.")
