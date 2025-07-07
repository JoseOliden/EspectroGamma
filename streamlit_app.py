import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Espectro Gamma Realista", layout="wide")

st.title("📟 Simulación Realista de Espectro Gamma Medido")
st.markdown("Simula cómo un detector gamma ve el espectro después de una activación: picos, decaimiento, ruido y fondo continuo.")

# --- Datos de radionúclidos (energía y vida media en minutos) ---
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
canales = np.arange(0, 4096)
energias = canales * keV_por_canal

# --- Resolución dependiente de la energía: sigma(E) = sqrt(a² + b·E) ---
detector = st.selectbox("Tipo de detector", ["HPGe", "NaI(Tl)"], index=0)
if detector == "HPGe":
    a = 1.5  # canales
    b = 0.001  # proporcional a energía (keV)
else:  # NaI
    a = 4
    b = 0.01

# --- Parámetros de simulación ---
t_actual = st.slider("⏱️ Tiempo desde la activación (minutos)", 0, 5000, 60)
modo = st.radio("Modo:", ["Cuentas por segundo (cps)", "Cuentas acumuladas"], horizontal=True)
tiempo_medicion = st.slider("⏲️ Tiempo de medición (segundos)", 1, 3600, 60) if modo == "Cuentas acumuladas" else 1
seleccion = st.multiselect("📡 Radionúclidos activados", list(radionuclidos.keys()), default=['198Au', '56Mn'])
agregar_ruido = st.checkbox("Agregar ruido Poisson", value=True)
fondo_continuo = st.checkbox("Agregar fondo continuo simulado", value=True)

# --- Simulación del espectro ---
espectro = np.zeros_like(canales, dtype=float)

for nuc in seleccion:
    datos = radionuclidos[nuc]
    energia = datos['E_kev']
    canal_central = int(energia / keV_por_canal)
    t12 = datos['t12_min']
    
    # Decaimiento exponencial
    cps = np.exp(-np.log(2) * t_actual / t12) * 100
    cuentas = cps * tiempo_medicion if modo == "Cuentas acumuladas" else cps

    # --- Ensanchamiento del pico según energía ---
    sigma = np.sqrt(a**2 + b * energia)  # en canales

    # --- Pico Gaussiano centrado en canal ---
    pico = cuentas * np.exp(-0.5 * ((canales - canal_central) / sigma) ** 2)
    espectro += pico

# --- Fondo continuo (Compton simulado o radiación ambiental) ---
if fondo_continuo:
    fondo = 5 + 30 * np.exp(-energias / 500)  # fondo decreciente con energía
    fondo *= tiempo_medicion
    espectro += fondo

# --- Ruido Poisson (simulación realista) ---
if agregar_ruido:
    espectro = np.random.poisson(espectro)

# --- Gráfico del espectro ---
fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(energias, espectro, color='darkgreen')
ax.set_title(f"Espectro Gamma Simulado ({modo}) - {t_actual} min post activación")
ax.set_xlabel("Energía (keV)")
ax.set_ylabel("Cuentas" if modo == "Cuentas acumuladas" else "Cuentas por segundo (cps)")
ax.set_xlim(0, 2000)
ax.grid(True)
st.pyplot(fig)

# --- Parámetros visualizados ---
with st.expander("📋 Parámetros de los radionúclidos activados"):
    for nuc in seleccion:
        datos = radionuclidos[nuc]
        st.write(f"**{nuc}** → {datos['E_kev']} keV, T½ = {datos['t12_min']/60:.2f} h")

st.caption("Simulación educativa de espectros gamma con resolución energética realista.")
