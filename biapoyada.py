import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

st.title("🔧 Viga Biapoyada Interactiva")

st.sidebar.header("Parámetros de la Viga")

# Parámetros de entrada
L = st.sidebar.slider("Longitud de la viga (m)", 1.0, 20.0, 10.0)
P = st.sidebar.slider("Carga puntual P (kN)", -100.0, 100.0, -10.0)
a = st.sidebar.slider("Posición de la carga (m)", 0.0, L, L/2)

support_A = st.sidebar.selectbox("Tipo de apoyo A", ["Simple", "Empotrado"])
support_B = st.sidebar.selectbox("Tipo de apoyo B", ["Simple", "Empotrado"])

E = st.sidebar.number_input("Módulo de elasticidad E (MPa)", value=210000.0)
I = st.sidebar.number_input("Momento de inercia I (m4)", value=8e-6, format="%e")

st.sidebar.markdown("---")

# Solo resolvemos correctamente simple-simple
if support_A == "Simple" and support_B == "Simple":

    # Reacciones
    RB = -P * a / L
    RA = -P - RB

    st.subheader("🔹 Reacciones")
    st.write(f"Reacción en A: {RA:.2f} kN")
    st.write(f"Reacción en B: {RB:.2f} kN")

    # Discretización
    x = np.linspace(0, L, 500)

    V = np.zeros_like(x)
    M = np.zeros_like(x)
    y = np.zeros_like(x)

    # Cortante y momento
    for i in range(len(x)):
        if x[i] < a:
            V[i] = RA
            M[i] = RA * x[i]
        else:
            V[i] = RA + P
            M[i] = RA * x[i] + P * (x[i] - a)

    # Flecha (fórmula analítica para carga puntual)
    for i in range(len(x)):
        if x[i] < a:
            y[i] = (P * (L - a) * x[i] * (L**2 - (L - a)**2 - x[i]**2)) / (6 * E * I * L)
        else:
            y[i] = (P * a * (L - x[i]) * (L**2 - a**2 - (L - x[i])**2)) / (6 * E * I * L)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Diagrama de Cortante")
        fig1, ax1 = plt.subplots()
        ax1.plot(x, V)
        ax1.axhline(0)
        ax1.set_xlabel("x (m)")
        ax1.set_ylabel("V (kN)")
        st.pyplot(fig1)

        st.subheader("Diagrama de Momento Flector")
        fig2, ax2 = plt.subplots()
        ax2.plot(x, M)
        ax2.axhline(0)
        ax2.set_xlabel("x (m)")
        ax2.set_ylabel("M (kNm)")
        st.pyplot(fig2)

    with col2:
        st.subheader("Deformada (Flecha)")
        fig3, ax3 = plt.subplots()
        ax3.plot(x, y)
        ax3.axhline(0)
        ax3.set_xlabel("x (m)")
        ax3.set_ylabel("Deflexión (m)")
        st.pyplot(fig3)

else:
    st.warning("⚠️ La versión actual solo resuelve correctamente viga Simple-Simple. En la siguiente versión añadiremos empotramientos con método matricial.")
