import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import time

st.set_page_config(page_title="Animación de Espectro Gamma", layout="wide")

st.title("📽️ Animación del Espectro Gamma en el Tiempo")
st.markdown("Simula cómo cambia el espectro gamma después de la activación, mostrando el decaimiento de picos en el tiempo.")

# --- Radionúclidos activados ---
radionuclidos = {
    '198Au': {
        't12_min': 2.7 * 60,
        'gammas': [(411.8, 1.0)],
    },
    '60Co': {
        't12_min': 1925 * 60,
        'gammas': [(1173.2, 1.0), (1332.5, 1.0)],
    },
    '24Na': {
        't12_min': 15 * 60,
        'gammas': [(1368.6, 1.0), (2754.0, 0.99)],
    },
    '82Br': {
        't12_min': 35 * 60,
        'gammas': [(554.3, 1.0), (776.5, 0.75)],
    },
    '28Al': {
        't12_min': 2.24,
        'gammas': [(1778.9, 1.0)],
    },
    '56Mn': {
        't12_min': 2.58 * 60,
        'gammas': [(846.8, 1.0), (1810.7, 0.27), (2113.1, 0.14)],
    },
}

# --- Detector y resolución energética ---


detector = st.selectbox("Tipo de detector", ["HPGe", "NaI(Tl)"], index=0)
if detector == "HPGe":
    a = 1.5
    b = 0.001
    keV_por_canal = 0.5
    canales = np.arange(0, 4096)
else:
    a = 4
    b = 0.01
    keV_por_canal = 1.0
    canales = np.arange(0, 2048)

energias = canales * keV_por_canal

# --- Controles de simulación ---
seleccion = st.multiselect("📡 Radionúclidos activados", list(radionuclidos.keys()), default=['56Mn'])
seleccion1 = st.multiselect("📡 Radionúclidos activados", list(radionuclidos.keys()), default=['28Al'])
tiempo_medicion = 1
fondo_continuo = st.checkbox("Agregar fondo continuo", value=True)
agregar_ruido = st.checkbox("Agregar ruido Poisson", value=True)
paso_tiempo = 1

# --- Parámetros de animación ---
t_max = st.slider("⏱️ Tiempo máximo (minutos)", 10, 60, 1)

#with col1:
#    t_max = st.slider("⏱️ Tiempo máximo (minutos)", 10, 50, 1)
#with col2:
    #paso_tiempo = st.slider("⏩ Paso entre cuadros (minutos)", 1, 5, 1)

iniciar = st.button("▶️ Iniciar animación")

# --- Función para simular espectro en un instante ---
def simular_espectro(t_actual, sel):
    espectro = np.zeros_like(canales, dtype=float)

    for nuc in sel:
        datos = radionuclidos[nuc]
        t12 = datos['t12_min']
        gammas = datos['gammas']
        if nuc == "56Mn":
            f_a = 0.05
        if nuc == "28Al":
            f_a = 100
        
            
        # Decaimiento del radionúclido
        actividad = np.exp(-np.log(2) * t_actual / t12) * 100

        for energia, intensidad_relativa in gammas:
            cuentas = actividad * intensidad_relativa
            cuentas = cuentas * tiempo_medicion

            canal_central = int(energia / keV_por_canal)
            sigma = np.sqrt(a**2 + b * energia)

            pico = cuentas * np.exp(-0.5 * ((canales - canal_central) / sigma) ** 2) 
            espectro += pico * f_a # ajuste 

            # Fondo Compton (opcional por línea)
            if fondo_continuo:
                EC = energia / (1 + energia / 511)
                canal_E = int(energia / keV_por_canal)
                canal_EC = int(EC / keV_por_canal)
                if 0 <= canal_EC < canal_E <= len(canales):
                    n = canal_E - canal_EC
                    if n > 1:
                        base = np.linspace(1, 0, n)
                        altura = 0.01 * cuentas
                        compton = np.zeros_like(canales)
                        compton[canal_EC:canal_E] = altura * base
                        espectro += compton
    # ✅ Ruido de fondo ambiental (bajo nivel en todo el espectro)
    if fondo_continuo:
        fondo_ambiental = np.random.normal(loc=1.0, scale=0.1, size=len(canales))*0
        fondo_ambiental = np.clip(fondo_ambiental, 0, None)  # evita valores negativos
        fondo_ambiental *= tiempo_medicion * 0.1  # escala ajustable
        espectro += fondo_ambiental
    # ✅ Ruido electrónico aleatorio bajo en todo el espectro
    if fondo_continuo:
        ruido_electronico = np.random.uniform(0, 2, size=canales.shape)
        ruido_electronico *= tiempo_medicion * 0.1  # Escalado bajo
        espectro += ruido_electronico

    # ✅ Ruido Poisson
    if agregar_ruido:
        espectro = np.random.poisson(espectro)

    return espectro, fondo_ambiental

# --- Animación ---
if iniciar:
    grafico = st.empty()
    espectro1, fondo = simular_espectro(0, seleccion)
    for t_min in range(0, 5*t_max + 1, paso_tiempo):
        espectro, fondo = simular_espectro(t_min, seleccion)
        espectro += espectro1
        espectro1 = espectro
        
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.set_yscale("log")
        ax.plot(energias, espectro, color='navy')
        ax.set_title(f"Espectro Gamma a {t_min} minutos")
        ax.set_xlabel("Energía (keV)")
        ax.set_ylabel("Cuentas")
        ax.set_xlim(800, 900)
        ax.set_ylim(0, max(100, np.max(espectro) * 1.1))
        #ax.set_ylim(0, 400)
        ax.grid(True)
        grafico.pyplot(fig)
        time.sleep(0.300)  # retardo entre cuadros (ajustable)
    energias2 = energias
    espectro2 = espectro
    ax.plot(energias2, espectro2, color='r')
    grafico.pyplot(fig)
    time.sleep(0.5)  # retardo entre cuadros (ajustable)
    
    for t_min in range(0, 5*t_max + 1, paso_tiempo):
        espectro56Mn, fondo = simular_espectro(t_min + 5*t_max, seleccion)
        espectro28Al, fondo_ambiental = simular_espectro(t_min, seleccion1)
        espectro = espectro56Mn + espectro28Al - fondo_ambiental +espectro1
        #espectro = simular_espectro(t_min, seleccion1)

        espectro1 = espectro
        
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.set_yscale("log")
        ax.plot(energias, espectro, color='navy')
        ax.plot(energias2, espectro2, color='r')
        ax.set_title(f"Espectro Gamma a {t_min} minutos")
        ax.set_xlabel("Energía (keV)")
        ax.set_ylabel("Cuentas")
        ax.set_xlim(800, 900)
        ax.set_ylim(0, max(100, np.max(espectro) * 1.1))
        #ax.set_ylim(0, 400)
        ax.grid(True)
        grafico.pyplot(fig)
        time.sleep(0.5)  # retardo entre cuadros (ajustable)

st.caption("Desarrollado para simulación educativa de AAN.")
