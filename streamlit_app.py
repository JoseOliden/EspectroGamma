import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# Parámetros de simulación
radionuclidos = {
    '198Au': {'E_kev': 411, 't12_h': 2.7},
    '60Co': {'E_kev': 1173, 't12_h': 1925},
    '24Na': {'E_kev': 1368, 't12_h': 15},
    '82Br': {'E_kev': 554, 't12_h': 35},
}

# Parámetros de tiempo
t_max = st.slider("Tiempo desde la activación (horas)", 0, 5000, 10)

# Crear espectro
canales = np.linspace(0, 2048, 2048)
espectro = np.zeros_like(canales)

for nuc, datos in radionuclidos.items():
    energia = datos['E_kev']
    canal = int(energia * 2)  # Supongamos 0.5 keV por canal
    t12 = datos['t12_h']
    intensidad = np.exp(-np.log(2) * t_max / t12) * 1000  # Escalado arbitrario
    ancho = 10  # ancho del pico
    espectro += intensidad * np.exp(-0.5 * ((canales - canal) / ancho)**2)

# Gráfico del espectro
fig, ax = plt.subplots()
ax.plot(canales, espectro)
ax.set_title(f"Espectro Gamma Simulado - {t_max} horas después de activación")
ax.set_xlabel("Canal (relacionado con energía)")
ax.set_ylabel("Cuentas")
ax.grid(True)
st.pyplot(fig)

# Mostrar tabla de radionúclidos
if st.checkbox("Mostrar radionúclidos simulados"):
    st.write("### Radionúclidos simulados:")
    st.write({k: f"{v['E_kev']} keV, T½={v['t12_h']} h" for k, v in radionuclidos.items()})
