# viga_simple_ec5.py
# Calculadora de viga simple apoyada según EC5
# Procedimiento paso a paso validado con ejemplo de Trabe

import streamlit as st
import numpy as np

# ------------------------------------------------------------
# 1. PROPIEDADES DE LOS MATERIALES (EC5)
# ------------------------------------------------------------
MATERIALES = {
    "C24": {
        "nombre": "C24",
        "f_m_k": 24.0,      # N/mm²
        "f_v_k": 4.0,       # N/mm²
        "f_c_0_k": 21.0,
        "f_c_90_k": 2.5,
        "f_t_0_k": 14.0,
        "E_0_mean": 11000.0, # N/mm²
        "E_0_05": 7400.0,
        "G_mean": 690.0,
        "rho_k": 350.0,     # kg/m³
        "gamma_M": 1.30,
        "k_def": 0.60,
    },
    "GL24h": {
        "nombre": "GL24h",
        "f_m_k": 24.0,
        "f_v_k": 4.0,
        "f_c_0_k": 21.0,
        "f_c_90_k": 2.5,
        "f_t_0_k": 14.0,
        "E_0_mean": 11600.0,
        "E_0_05": 9400.0,
        "G_mean": 720.0,
        "rho_k": 380.0,
        "gamma_M": 1.25,
        "k_def": 0.60,
    },
}

# ------------------------------------------------------------
# 2. FUNCIONES DE CÁLCULO (PASO A PASO)
# ------------------------------------------------------------

def esfuerzos_uniforme(q, L):
    """
    q en kN/m, L en m
    Devuelve M (kN·m) y V (kN) para viga biapoyada con carga uniforme
    """
    M = q * L**2 / 8.0
    V = q * L / 2.0
    return M, V

def esfuerzos_puntual(P, L, a):
    """
    P en kN, L en m, a = distancia desde apoyo izquierdo (m)
    Devuelve M en kN·m (en el punto de carga), y reacciones V_izq, V_der (kN)
    """
    b = L - a
    M = P * a * b / L
    V_izq = P * b / L
    V_der = P * a / L
    return M, V_izq, V_der

def momento_mixto(q, P, L, a):
    """
    q en kN/m, P en kN, L en m, a = distancia desde apoyo izquierdo (m)
    Devuelve M_máximo (kN·m) y la reacción izquierda R_A (kN)
    Busca el punto de cortante nulo para carga uniforme + puntual descentrada
    """
    R_A = q * L / 2.0 + P * (L - a) / L
    # Punto de cortante nulo en el tramo antes de la carga puntual
    x = R_A / q
    if x > a:
        # Si el punto de cortante nulo está después de la carga, evaluamos en x=a
        x = a
    # Momento debido a la uniforme + reacción
    M = R_A * x - q * x**2 / 2.0
    # Si la carga puntual está antes de x, añadimos su efecto
    if x > a:
        M += P * (x - a)
    return M, R_A

def propiedades_seccion(b, h):
    """
    b, h en mm
    Devuelve: A (mm²), I_y (mm⁴), I_z (mm⁴), W_y (mm³), W_z (mm³), i_y (mm), i_z (mm)
    """
    A = b * h
    I_y = b * h**3 / 12.0
    I_z = h * b**3 / 12.0
    W_y = b * h**2 / 6.0
    W_z = h * b**2 / 6.0
    i_y = np.sqrt(I_y / A) if A > 0 else 0
    i_z = np.sqrt(I_z / A) if A > 0 else 0
    return A, I_y, I_z, W_y, W_z, i_y, i_z

def flecha_uniforme(q, L, E, I):
    """
    q en N/mm (1 kN/m = 1 N/mm), L en mm, E en N/mm², I en mm⁴
    Devuelve flecha instantánea por flexión (mm)
    """
    return 5.0 * q * L**4 / (384.0 * E * I)

def flecha_total_con_cortante(w_flex, E, G, h, L):
    """
    w_flex en mm, E, G en N/mm², h, L en mm
    Devuelve flecha total incluyendo deformación por cortante (Timoshenko)
    """
    factor = 1.0 + (24.0 / 25.0) * (E / G) * (h / L)**2
    return w_flex * factor

# ------------------------------------------------------------
# 3. CÁLCULO PRINCIPAL (PROCEDIMIENTO COMPLETO)
# ------------------------------------------------------------

def calcular_viga(L, b, h, G_k, Q_k_uniforme, Q_k_puntual, material_nombre,
                  clase_servicio=1, k_sys=1.10, k_cr=0.67, tiempo_fuego=30):
    """
    Realiza todas las comprobaciones de una viga simple apoyada según EC5.
    Devuelve un diccionario con todos los resultados.
    """
    
    # --- Material ---
    mat = MATERIALES[material_nombre]
    gamma_M = mat["gamma_M"]
    k_def = mat["k_def"]
    E = mat["E_0_mean"]
    E_05 = mat["E_0_05"]
    G = mat["G_mean"]
    f_m_k = mat["f_m_k"]
    f_v_k = mat["f_v_k"]
    f_c_90_k = mat["f_c_90_k"]
    
    # k_mod para media duración (uso residencial)
    k_mod = 0.80
    
    # --- Sección ---
    A, I_y, I_z, W_y, W_z, i_y, i_z = propiedades_seccion(b, h)
    
    # --- ESFUERZOS ELU (4 combinaciones) ---
    q_perm = G_k
    q_var = Q_k_uniforme
    P_var = Q_k_puntual
    
    # ELU1: solo permanente
    q1 = 1.35 * q_perm
    M1, V1 = esfuerzos_uniforme(q1, L)
    
    # ELU2: permanente + variable uniforme
    q2 = 1.35 * q_perm + 1.50 * q_var
    M2, V2 = esfuerzos_uniforme(q2, L)
    
    # ELU3: permanente + variable puntual en centro (a = L/2)
    q3 = 1.35 * q_perm
    P3 = 1.50 * P_var
    M_puntual, V3_izq, V3_der = esfuerzos_puntual(P3, L, L/2.0)
    M3 = q3 * L**2 / 8.0 + M_puntual   # sumamos el momento de la uniforme en el centro
    V3 = q3 * L / 2.0 + P3 / 2.0        # cortante en apoyo
    
    # ELU4: permanente + variable puntual cerca del apoyo (a = L - h/1000)
    a4 = L - h / 1000.0   # h en mm -> m
    q4 = 1.35 * q_perm
    P4 = 1.50 * P_var
    M4, R_A4 = momento_mixto(q4, P4, L, a4)
    V4 = R_A4   # cortante máximo = reacción izquierda (porque la carga está cerca)
    
    # --- RESISTENCIAS DE CÁLCULO (ELU) ---
    f_m_d = k_mod * f_m_k * k_sys / gamma_M   # N/mm²
    f_v_d = k_mod * f_v_k * k_sys / gamma_M   # N/mm²
    
    # --- FLEXIÓN (ELU) - usando ELU2 (la más desfavorable) ---
    M_flex = M2  # kN·m
    sigma_m = M_flex * 1e6 / W_y   # N/mm²
    indice_flexion = sigma_m / f_m_d * 100.0
    
    # --- CORTANTE (ELU) - usando ELU2 (la que da más V en este caso) ---
    V_cort = V2  # kN
    tau = 1.5 * V_cort * 1000 / (b * k_cr * h)   # N/mm²
    indice_cortante = tau / f_v_d * 100.0
    
    # --- VUELCO LATERAL (LTB) ---
    # Longitud eficaz (carga en borde superior comprimido)
    L_ef = L * 1000 + 2 * h   # mm
    # Tensión crítica (Euler para vuelco lateral)
    sigma_crit = 0.78 * b**2 * E_05 / (h * L_ef)   # N/mm²
    if sigma_crit > 0:
        lambda_rel_m = np.sqrt(f_m_k / sigma_crit)
    else:
        lambda_rel_m = 10.0  # valor alto para que no cumpla
    # k_crit según EC5
    if lambda_rel_m <= 0.75:
        k_crit = 1.0
    elif lambda_rel_m <= 1.4:
        k_crit = 1.56 - 0.75 * lambda_rel_m
    else:
        k_crit = 1.0 / lambda_rel_m**2
    # Comprobación de vuelco: σ_m ≤ k_crit · f_m_d
    indice_vuelco = sigma_m / (k_crit * f_m_d) * 100.0
    
    # --- ELS: FLECHA (siguiendo el procedimiento de Trabe) ---
    # Nota: 1 kN/m = 1 N/mm, por lo que q en kN/m se usa directamente como N/mm
    # Confort: solo Q instantánea
    q_conf = Q_k_uniforme  # N/mm
    w_flex_conf = flecha_uniforme(q_conf, L*1000, E, I_y)
    w_conf = flecha_total_con_cortante(w_flex_conf, E, G, h, L*1000)
    limite_conf = L * 1000 / 350.0
    
    # Integridad: G diferida + Q (inst + ψ2·fluencia)
    psi2 = 0.30
    q_G = G_k
    q_Q = Q_k_uniforme
    w_flex_G = flecha_uniforme(q_G, L*1000, E, I_y)
    w_flex_Q = flecha_uniforme(q_Q, L*1000, E, I_y)
    # Parte diferida de G
    w_G_diff = flecha_total_con_cortante(w_flex_G * k_def, E, G, h, L*1000)
    # Parte instantánea de Q
    w_Q_inst = flecha_total_con_cortante(w_flex_Q, E, G, h, L*1000)
    # Parte diferida de Q (solo ψ2)
    w_Q_diff = flecha_total_con_cortante(w_flex_Q * psi2 * k_def, E, G, h, L*1000)
    w_int = w_G_diff + w_Q_inst + w_Q_diff
    limite_int = L * 1000 / 300.0
    
    # Apariencia: G total (inst+fluencia) + ψ2·Q total (inst+fluencia)
    w_G_apa = flecha_total_con_cortante(w_flex_G * (1 + k_def), E, G, h, L*1000)
    w_Q_apa = flecha_total_con_cortante(w_flex_Q * psi2 * (1 + k_def), E, G, h, L*1000)
    w_apa = w_G_apa + w_Q_apa
    limite_apa = L * 1000 / 300.0
    
    # --- SITUACIÓN DE INCENDIO (sección reducida) ---
    beta_n = 0.80  # mm/min
    d_char = beta_n * tiempo_fuego
    d0 = 7.0  # mm
    k0 = 1.0 if tiempo_fuego >= 20 else tiempo_fuego / 20.0
    d_ef = d_char + k0 * d0
    
    # Sección reducida (3 caras expuestas: inferior, izquierda, derecha)
    b_fi = b - 2 * d_ef
    h_fi = h - d_ef
    if b_fi < 10 or h_fi < 10:
        b_fi = max(b_fi, 10.0)
        h_fi = max(h_fi, 10.0)
    A_fi, I_y_fi, _, W_y_fi, _, _, _ = propiedades_seccion(b_fi, h_fi)
    
    # Resistencia en incendio
    k_fi = 1.25  # percentil 20%
    f_m_fi_d = 1.0 * k_fi * f_m_k * k_sys / 1.0   # γM=1, kmod=1
    f_v_fi_d = 1.0 * k_fi * f_v_k * k_sys / 1.0
    
    # Combinación de incendio: G + ψ1·Q (ψ1=0.50)
    psi1 = 0.50
    q_fi = G_k + psi1 * Q_k_uniforme
    M_fi, V_fi = esfuerzos_uniforme(q_fi, L)
    
    # Flexión fuego
    sigma_fi = M_fi * 1e6 / W_y_fi
    indice_flexion_fuego = sigma_fi / f_m_fi_d * 100.0
    
    # Cortante fuego
    tau_fi = 1.5 * V_fi * 1000 / (b_fi * k_cr * h_fi)
    indice_cortante_fuego = tau_fi / f_v_fi_d * 100.0
    
    # --- ÍNDICE GLOBAL ---
    indices = [
        indice_flexion,
        indice_cortante,
        indice_vuelco,
        w_conf / limite_conf * 100,
        w_int / limite_int * 100,
        w_apa / limite_apa * 100,
        indice_flexion_fuego,
        indice_cortante_fuego
    ]
    indice_global = max(indices)
    
    # --- RESULTADOS ---
    return {
        "esfuerzos": {
            "ELU1": {"M": M1, "V": V1},
            "ELU2": {"M": M2, "V": V2},
            "ELU3": {"M": M3, "V": V3},
            "ELU4": {"M": M4, "V": V4},
        },
        "flexion": {
            "sigma": sigma_m,
            "f_m_d": f_m_d,
            "indice": indice_flexion,
        },
        "cortante": {
            "tau": tau,
            "f_v_d": f_v_d,
            "indice": indice_cortante,
        },
        "vuelco": {
            "L_ef": L_ef,
            "sigma_crit": sigma_crit,
            "lambda_rel_m": lambda_rel_m,
            "k_crit": k_crit,
            "indice": indice_vuelco,
        },
        "flecha": {
            "confort": {"w": w_conf, "limite": limite_conf, "indice": w_conf/limite_conf*100},
            "integridad": {"w": w_int, "limite": limite_int, "indice": w_int/limite_int*100},
            "apariencia": {"w": w_apa, "limite": limite_apa, "indice": w_apa/limite_apa*100},
        },
        "fuego": {
            "d_ef": d_ef,
            "b_fi": b_fi,
            "h_fi": h_fi,
            "W_y_fi": W_y_fi,
            "sigma_fi": sigma_fi,
            "f_m_fi_d": f_m_fi_d,
            "indice_flexion": indice_flexion_fuego,
            "tau_fi": tau_fi,
            "f_v_fi_d": f_v_fi_d,
            "indice_cortante": indice_cortante_fuego,
        },
        "indice_global": indice_global,
        "seccion": {"A": A, "I_y": I_y, "W_y": W_y, "i_y": i_y},
    }

# ------------------------------------------------------------
# 4. INTERFAZ STREAMLIT (SIN COMPARACIÓN CON TRABE)
# ------------------------------------------------------------

def main():
    st.set_page_config(page_title="Viga Simple EC5", layout="wide")
    st.title("🪵 Calculadora de Viga Simple Apoyada (EC5)")
    st.markdown("**Procedimiento paso a paso según EC5** – Válido para madera maciza y laminada.")
    
    # --- Sidebar: Datos de entrada ---
    with st.sidebar:
        st.header("📐 Datos de entrada")
        L = st.number_input("Luz (m)", value=5.0, step=0.5, min_value=1.0)
        b = st.number_input("Ancho (mm)", value=120, step=10, min_value=50)
        h = st.number_input("Canto (mm)", value=260, step=10, min_value=50)
        
        st.divider()
        st.subheader("Cargas")
        G_k = st.number_input("Carga permanente (kN/m)", value=2.13, step=0.1, min_value=0.0)
        Q_k_uniforme = st.number_input("Sobrecarga uniforme (kN/m)", value=2.00, step=0.1, min_value=0.0)
        Q_k_puntual = st.number_input("Sobrecarga puntual (kN)", value=2.00, step=0.5, min_value=0.0)
        
        st.divider()
        st.subheader("Material")
        material = st.selectbox("Material", list(MATERIALES.keys()), index=0)
        
        st.divider()
        st.subheader("Coeficientes")
        k_sys = st.number_input("k_sys (carga compartida)", value=1.10, step=0.05, min_value=1.0, max_value=1.2)
        k_cr = st.number_input("k_cr (fendas)", value=0.67, step=0.01, min_value=0.5, max_value=1.0)
        tiempo_fuego = st.number_input("Resistencia al fuego (min)", value=30, step=10, min_value=0)
    
    # --- Botón de cálculo ---
    if st.button("Calcular", type="primary"):
        with st.spinner("Calculando..."):
            res = calcular_viga(
                L, b, h, G_k, Q_k_uniforme, Q_k_puntual,
                material, k_sys=k_sys, k_cr=k_cr, tiempo_fuego=tiempo_fuego
            )
        
        # --- Mostrar resultados ---
        st.success(f"✅ Cálculo completado. Índice global: {res['indice_global']:.1f}%")
        
        # Métricas principales
        col1, col2, col3 = st.columns(3)
        col1.metric("Flexión ELU", f"{res['flexion']['indice']:.1f}%",
                    delta="OK" if res['flexion']['indice'] < 100 else "⚠️ NO CUMPLE")
        col2.metric("Cortante ELU", f"{res['cortante']['indice']:.1f}%",
                    delta="OK" if res['cortante']['indice'] < 100 else "⚠️ NO CUMPLE")
        col3.metric("Apariencia ELS", f"{res['flecha']['apariencia']['indice']:.1f}%",
                    delta="OK" if res['flecha']['apariencia']['indice'] < 100 else "⚠️ NO CUMPLE")
        
        # --- Sección: Esfuerzos ELU ---
        with st.expander("📊 Esfuerzos (ELU)", expanded=True):
            st.dataframe({
                "Combinación": ["ELU1", "ELU2", "ELU3", "ELU4"],
                "M (kN·m)": [
                    f"{res['esfuerzos']['ELU1']['M']:.2f}",
                    f"{res['esfuerzos']['ELU2']['M']:.2f}",
                    f"{res['esfuerzos']['ELU3']['M']:.2f}",
                    f"{res['esfuerzos']['ELU4']['M']:.2f}",
                ],
                "V (kN)": [
                    f"{res['esfuerzos']['ELU1']['V']:.2f}",
                    f"{res['esfuerzos']['ELU2']['V']:.2f}",
                    f"{res['esfuerzos']['ELU3']['V']:.2f}",
                    f"{res['esfuerzos']['ELU4']['V']:.2f}",
                ],
            })
        
        # --- ELU: Flexión y Cortante ---
        with st.expander("🔧 Comprobaciones ELU"):
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("📌 Flexión (ELU2)")
                st.write(f"Momento de cálculo: M_d = {res['esfuerzos']['ELU2']['M']:.2f} kN·m")
                st.write(f"W_y = {res['seccion']['W_y']:.0f} mm³")
                st.write(f"σ_m,d = {res['flexion']['sigma']:.2f} N/mm²")
                st.write(f"f_m,d = {res['flexion']['f_m_d']:.2f} N/mm²")
                st.write(f"Índice: {res['flexion']['indice']:.1f}%")
                if res['flexion']['indice'] < 100:
                    st.success("✅ Cumple")
                else:
                    st.error("❌ No cumple")
                
                st.subheader("📌 Vuelco lateral")
                st.write(f"L_ef = {res['vuelco']['L_ef']:.0f} mm")
                st.write(f"σ_m,crit = {res['vuelco']['sigma_crit']:.2f} N/mm²")
                st.write(f"λ_rel,m = {res['vuelco']['lambda_rel_m']:.3f}")
                st.write(f"k_crit = {res['vuelco']['k_crit']:.3f}")
                st.write(f"Índice: {res['vuelco']['indice']:.1f}%")
            
            with col2:
                st.subheader("📌 Cortante (ELU2)")
                st.write(f"Cortante de cálculo: V_d = {res['esfuerzos']['ELU2']['V']:.2f} kN")
                st.write(f"b·k_cr·h = {b * k_cr * h:.0f} mm²")
                st.write(f"τ_d = {res['cortante']['tau']:.3f} N/mm²")
                st.write(f"f_v,d = {res['cortante']['f_v_d']:.2f} N/mm²")
                st.write(f"Índice: {res['cortante']['indice']:.1f}%")
                if res['cortante']['indice'] < 100:
                    st.success("✅ Cumple")
                else:
                    st.error("❌ No cumple")
        
        # --- ELS: Flecha ---
        with st.expander("📏 Flechas (ELS)"):
            st.dataframe({
                "Concepto": ["Confort", "Integridad", "Apariencia"],
                "Flecha (mm)": [
                    f"{res['flecha']['confort']['w']:.1f}",
                    f"{res['flecha']['integridad']['w']:.1f}",
                    f"{res['flecha']['apariencia']['w']:.1f}",
                ],
                "Límite (mm)": [
                    f"{res['flecha']['confort']['limite']:.1f}",
                    f"{res['flecha']['integridad']['limite']:.1f}",
                    f"{res['flecha']['apariencia']['limite']:.1f}",
                ],
                "Índice (%)": [
                    f"{res['flecha']['confort']['indice']:.1f}",
                    f"{res['flecha']['integridad']['indice']:.1f}",
                    f"{res['flecha']['apariencia']['indice']:.1f}",
                ],
                "Cumple": [
                    "✅" if res['flecha']['confort']['indice'] < 100 else "❌",
                    "✅" if res['flecha']['integridad']['indice'] < 100 else "❌",
                    "✅" if res['flecha']['apariencia']['indice'] < 100 else "❌",
                ]
            })
            st.caption("La flecha incluye deformación por cortante según Timoshenko.")
        
        # --- Incendio ---
        with st.expander("🔥 Situación de incendio"):
            st.write(f"d_ef = {res['fuego']['d_ef']:.1f} mm")
            st.write(f"Sección efectiva: {res['fuego']['b_fi']:.0f} × {res['fuego']['h_fi']:.0f} mm")
            st.write(f"W_y,fi = {res['fuego']['W_y_fi']:.0f} mm³")
            
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Flexión en incendio")
                st.write(f"σ_m,fi,d = {res['fuego']['sigma_fi']:.2f} N/mm²")
                st.write(f"f_m,fi,d = {res['fuego']['f_m_fi_d']:.2f} N/mm²")
                st.write(f"Índice: {res['fuego']['indice_flexion']:.1f}%")
                if res['fuego']['indice_flexion'] < 100:
                    st.success("✅ Cumple")
                else:
                    st.error("❌ No cumple")
            with col2:
                st.subheader("Cortante en incendio")
                st.write(f"τ_fi,d = {res['fuego']['tau_fi']:.3f} N/mm²")
                st.write(f"f_v,fi,d = {res['fuego']['f_v_fi_d']:.2f} N/mm²")
                st.write(f"Índice: {res['fuego']['indice_cortante']:.1f}%")
                if res['fuego']['indice_cortante'] < 100:
                    st.success("✅ Cumple")
                else:
                    st.error("❌ No cumple")

if __name__ == "__main__":
    main()
