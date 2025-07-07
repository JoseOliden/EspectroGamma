import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import time

st.set_page_config(page_title="Animación de Espectro Gamma", layout="wide")

st.title("📽️ Animación del Espectro Gamma en el Tiempo")
st.markdown("Simula cómo cambia el espectro gamma después de la activación, mostrando el decaimiento de picos en el tiempo.")

# --- Radionúclidos activados ---
radionuclidos = {
    '198Au': {'E_kev': 411, 't12_min': 2.7 * 60},
    '60Co': {'E_kev': 1173, 't12_min': 1925 * 60},
    '24Na': {'E_kev': 1368, 't12_min': 15 * 60},
    '82Br': {'E_kev': 554, 't12_min': 35 * 60},
    '28Al': {'E_kev': 1779, 't12_min': 2.24},
    '56Mn': {'E_kev': 847, 't12_min': 2.58 * 60},
}

# --- Detector y resolución energética ---
keV_por_canal = 0.5
canales = np.arange(0, 4096)
energias = canales * keV_por_canal

detector = st.selectbox("Tipo de detector", ["HPGe", "NaI(Tl)"], index=0)
if detector == "HPGe":
    a = 1.5
    b = 0.001
else:
    a = 4
    b = 0.01

# --- Controles de simulación ---
seleccion = st.multiselect("📡 Radionúclidos activados", list(radionuclidos.keys()), default=['198Au', '56Mn'])
modo = st.radio("Modo:", ["Cuentas por segundo (cps)", "Cuentas acumuladas"], horizontal=True)
tiempo_medicion = st.slider("⏲️ Tiempo de medición por cuadro (segundos)", 1, 60, 1) if modo == "Cuentas acumuladas" else 1
fondo_continuo = st.checkbox("Agregar fondo continuo", value=True)
agregar_ruido = st.checkbox("Agregar ruido Poisson", value=True)

# --- Parámetros de animación ---
col1, col2 = st.columns(2)
with col1:
    t_max = st.slider("⏱️ Tiempo máximo (minutos)", 10, 1000, 1)
with col2:
    paso_tiempo = st.slider("⏩ Paso entre cuadros (minutos)", 1, 50, 10)

iniciar = st.button("▶️ Iniciar animación")

# --- Función para simular espectro en un instante ---
def simular_espectro(t_actual):
    espectro = np.zeros_like(canales, dtype=float)

    for nuc in seleccion:
        datos = radionuclidos[nuc]
        energia = datos['E_kev']
        canal_central = int(energia / keV_por_canal)
        t12 = datos['t12_min']
        
        # Decaimiento y cuentas
        cps = np.exp(-np.log(2) * t_actual / t12) * 100
        cuentas = cps * tiempo_medicion if modo == "Cuentas acumuladas" else cps
        
        # Ensanchamiento (resolución)
        sigma = np.sqrt(a**2 + b * energia)
        pico = cuentas * np.exp(-0.5 * ((canales - canal_central) / sigma) ** 2)
        espectro += pico

        # ✅ Fondo Compton
        if fondo_continuo:
            E = energia
            EC = E / (1 + E / 511)  # borde Compton
            canal_E = int(E / keV_por_canal)
            canal_EC = int(EC / keV_por_canal)
            
            # Simula cola Compton decaída linealmente desde canal_EC a canal_E
            if canal_EC < canal_E:
                base = np.linspace(1, 0, canal_E - canal_EC)
                altura = 0.15 * cuentas  # 15% del pico
                compton = np.zeros_like(canales)
                compton[canal_EC:canal_E] = altura * base
                espectro += compton
    # ✅ Ruido de fondo ambiental (bajo nivel en todo el espectro)
    if fondo_continuo:
        fondo_ambiental = np.random.normal(loc=1.0, scale=0.5, size=len(canales))
        fondo_ambiental = np.clip(fondo_ambiental, 0, None)  # evita valores negativos
        fondo_ambiental *= tiempo_medicion * 0.2  # escala ajustable
        espectro += fondo_ambiental
    # ✅ Ruido electrónico aleatorio bajo en todo el espectro
    if fondo_continuo:
        ruido_electronico = np.random.uniform(0, 2, size=canales.shape)
        ruido_electronico *= tiempo_medicion * 0.05  # Escalado bajo
        espectro += ruido_electronico

    # ✅ Ruido Poisson
    if agregar_ruido:
        espectro = np.random.poisson(espectro)

    return espectro

# --- Animación ---
if iniciar:
    grafico = st.empty()
    espectro1 = simular_espectro(0)
    for t_min in range(0, t_max + 1, paso_tiempo):
        espectro = simular_espectro(t_min)+espectro1
        espectro1 = simular_espectro(t_min)
        
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(energias, espectro, color='navy')
        ax.set_title(f"Espectro Gamma a {t_min} minutos")
        ax.set_xlabel("Energía (keV)")
        ax.set_ylabel("Cuentas" if modo == "Cuentas acumuladas" else "Cuentas por segundo (cps)")
        ax.set_xlim(0, 2000)
        ax.set_ylim(0, max(100, np.max(espectro) * 1.1))
        ax.grid(True)
        grafico.pyplot(fig)
        time.sleep(0.3)  # retardo entre cuadros (ajustable)

st.caption("Desarrollado para simulación educativa de AAN.")
