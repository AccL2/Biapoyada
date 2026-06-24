# viga_simple_ec5_visual.py
# Calculadora de viga simple apoyada según EC5
# Con visualización paso a paso de fórmulas y sustituciones

import streamlit as st
import numpy as np

# ------------------------------------------------------------
# 1. PROPIEDADES DE LOS MATERIALES (EC5)
# ------------------------------------------------------------
MATERIALES = {
    "C24": {
        "nombre": "C24",
        "f_m_k": 24.0,
        "f_v_k": 4.0,
        "f_c_0_k": 21.0,
        "f_c_90_k": 2.5,
        "f_t_0_k": 14.0,
        "E_0_mean": 11000.0,
        "E_0_05": 7400.0,
        "G_mean": 690.0,
        "rho_k": 350.0,
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
# 2. FUNCIONES DE CÁLCULO
# ------------------------------------------------------------

def esfuerzos_uniforme(q, L):
    M = q * L**2 / 8.0
    V = q * L / 2.0
    return M, V

def esfuerzos_puntual(P, L, a):
    b = L - a
    M = P * a * b / L
    V_izq = P * b / L
    V_der = P * a / L
    return M, V_izq, V_der

def momento_mixto(q, P, L, a):
    R_A = q * L / 2.0 + P * (L - a) / L
    x = R_A / q
    if x > a:
        x = a
    M = R_A * x - q * x**2 / 2.0
    if x > a:
        M += P * (x - a)
    return M, R_A

def propiedades_seccion(b, h):
    A = b * h
    I_y = b * h**3 / 12.0
    I_z = h * b**3 / 12.0
    W_y = b * h**2 / 6.0
    W_z = h * b**2 / 6.0
    i_y = np.sqrt(I_y / A) if A > 0 else 0
    i_z = np.sqrt(I_z / A) if A > 0 else 0
    return A, I_y, I_z, W_y, W_z, i_y, i_z

def flecha_uniforme(q, L, E, I):
    return 5.0 * q * L**4 / (384.0 * E * I)

def flecha_total_con_cortante(w_flex, E, G, h, L):
    factor = 1.0 + (24.0 / 25.0) * (E / G) * (h / L)**2
    return w_flex * factor

# ------------------------------------------------------------
# 3. CÁLCULO PRINCIPAL (con resultados intermedios para mostrar)
# ------------------------------------------------------------

def calcular_viga(L, b, h, G_k, Q_k_uniforme, Q_k_puntual, material_nombre,
                  k_sys=1.10, k_cr=0.67, tiempo_fuego=30):
    
    mat = MATERIALES[material_nombre]
    gamma_M = mat["gamma_M"]
    k_def = mat["k_def"]
    E = mat["E_0_mean"]
    E_05 = mat["E_0_05"]
    G = mat["G_mean"]
    f_m_k = mat["f_m_k"]
    f_v_k = mat["f_v_k"]
    k_mod = 0.80  # media duración
    
    A, I_y, I_z, W_y, W_z, i_y, i_z = propiedades_seccion(b, h)
    
    # --- ESFUERZOS ELU ---
    q_perm = G_k
    q_var = Q_k_uniforme
    P_var = Q_k_puntual
    
    q1 = 1.35 * q_perm
    M1, V1 = esfuerzos_uniforme(q1, L)
    
    q2 = 1.35 * q_perm + 1.50 * q_var
    M2, V2 = esfuerzos_uniforme(q2, L)
    
    q3 = 1.35 * q_perm
    P3 = 1.50 * P_var
    M_puntual, V3_izq, V3_der = esfuerzos_puntual(P3, L, L/2.0)
    M3 = q3 * L**2 / 8.0 + M_puntual
    V3 = q3 * L / 2.0 + P3 / 2.0
    
    a4 = L - h / 1000.0
    q4 = 1.35 * q_perm
    P4 = 1.50 * P_var
    M4, R_A4 = momento_mixto(q4, P4, L, a4)
    V4 = R_A4
    
    # --- RESISTENCIAS ---
    f_m_d = k_mod * f_m_k * k_sys / gamma_M
    f_v_d = k_mod * f_v_k * k_sys / gamma_M
    
    # --- FLEXIÓN ---
    M_flex = M2
    sigma_m = M_flex * 1e6 / W_y
    indice_flexion = sigma_m / f_m_d * 100.0
    
    # --- CORTANTE ---
    V_cort = V2
    tau = 1.5 * V_cort * 1000 / (b * k_cr * h)
    indice_cortante = tau / f_v_d * 100.0
    
    # --- VUELCO ---
    L_ef = L * 1000 + 2 * h
    sigma_crit = 0.78 * b**2 * E_05 / (h * L_ef)
    if sigma_crit > 0:
        lambda_rel_m = np.sqrt(f_m_k / sigma_crit)
    else:
        lambda_rel_m = 10.0
    if lambda_rel_m <= 0.75:
        k_crit = 1.0
    elif lambda_rel_m <= 1.4:
        k_crit = 1.56 - 0.75 * lambda_rel_m
    else:
        k_crit = 1.0 / lambda_rel_m**2
    indice_vuelco = sigma_m / (k_crit * f_m_d) * 100.0
    
    # --- FLECHAS ---
    psi2 = 0.30
    q_conf = Q_k_uniforme
    w_flex_conf = flecha_uniforme(q_conf, L*1000, E, I_y)
    w_conf = flecha_total_con_cortante(w_flex_conf, E, G, h, L*1000)
    limite_conf = L * 1000 / 350.0
    
    q_G = G_k
    q_Q = Q_k_uniforme
    w_flex_G = flecha_uniforme(q_G, L*1000, E, I_y)
    w_flex_Q = flecha_uniforme(q_Q, L*1000, E, I_y)
    w_G_diff = flecha_total_con_cortante(w_flex_G * k_def, E, G, h, L*1000)
    w_Q_inst = flecha_total_con_cortante(w_flex_Q, E, G, h, L*1000)
    w_Q_diff = flecha_total_con_cortante(w_flex_Q * psi2 * k_def, E, G, h, L*1000)
    w_int = w_G_diff + w_Q_inst + w_Q_diff
    limite_int = L * 1000 / 300.0
    
    w_G_apa = flecha_total_con_cortante(w_flex_G * (1 + k_def), E, G, h, L*1000)
    w_Q_apa = flecha_total_con_cortante(w_flex_Q * psi2 * (1 + k_def), E, G, h, L*1000)
    w_apa = w_G_apa + w_Q_apa
    limite_apa = L * 1000 / 300.0
    
    # --- FUEGO ---
    beta_n = 0.80
    d_char = beta_n * tiempo_fuego
    d0 = 7.0
    k0 = 1.0 if tiempo_fuego >= 20 else tiempo_fuego / 20.0
    d_ef = d_char + k0 * d0
    
    b_fi = b - 2 * d_ef
    h_fi = h - d_ef
    if b_fi < 10 or h_fi < 10:
        b_fi = max(b_fi, 10.0)
        h_fi = max(h_fi, 10.0)
    A_fi, I_y_fi, _, W_y_fi, _, _, _ = propiedades_seccion(b_fi, h_fi)
    
    k_fi = 1.25
    f_m_fi_d = 1.0 * k_fi * f_m_k * k_sys / 1.0
    f_v_fi_d = 1.0 * k_fi * f_v_k * k_sys / 1.0
    
    psi1 = 0.50
    q_fi = G_k + psi1 * Q_k_uniforme
    M_fi, V_fi = esfuerzos_uniforme(q_fi, L)
    
    sigma_fi = M_fi * 1e6 / W_y_fi
    indice_flexion_fuego = sigma_fi / f_m_fi_d * 100.0
    
    tau_fi = 1.5 * V_fi * 1000 / (b_fi * k_cr * h_fi)
    indice_cortante_fuego = tau_fi / f_v_fi_d * 100.0
    
    indices = [
        indice_flexion, indice_cortante, indice_vuelco,
        w_conf/limite_conf*100, w_int/limite_int*100, w_apa/limite_apa*100,
        indice_flexion_fuego, indice_cortante_fuego
    ]
    indice_global = max(indices)
    
    return {
        "esfuerzos": {"ELU1": (M1, V1), "ELU2": (M2, V2), "ELU3": (M3, V3), "ELU4": (M4, V4)},
        "seccion": {"A": A, "I_y": I_y, "W_y": W_y, "i_y": i_y},
        "flexion": {"sigma": sigma_m, "f_m_d": f_m_d, "indice": indice_flexion, "M": M2, "W": W_y},
        "cortante": {"tau": tau, "f_v_d": f_v_d, "indice": indice_cortante, "V": V2, "b_ef": b*k_cr},
        "vuelco": {"L_ef": L_ef, "sigma_crit": sigma_crit, "lambda": lambda_rel_m, "k_crit": k_crit, "indice": indice_vuelco},
        "flecha": {
            "confort": {"w": w_conf, "limite": limite_conf, "indice": w_conf/limite_conf*100, "w_flex": w_flex_conf},
            "integridad": {"w": w_int, "limite": limite_int, "indice": w_int/limite_int*100, "w_flex_G": w_flex_G, "w_flex_Q": w_flex_Q},
            "apariencia": {"w": w_apa, "limite": limite_apa, "indice": w_apa/limite_apa*100},
        },
        "fuego": {
            "d_ef": d_ef, "b_fi": b_fi, "h_fi": h_fi, "W_y_fi": W_y_fi,
            "sigma_fi": sigma_fi, "f_m_fi_d": f_m_fi_d, "indice_flexion": indice_flexion_fuego,
            "tau_fi": tau_fi, "f_v_fi_d": f_v_fi_d, "indice_cortante": indice_cortante_fuego,
            "M_fi": M_fi, "V_fi": V_fi
        },
        "indice_global": indice_global,
        "material": {"k_mod": k_mod, "gamma_M": gamma_M, "k_def": k_def, "k_sys": k_sys, "k_cr": k_cr},
    }

# ------------------------------------------------------------
# 4. INTERFAZ STREAMLIT (con visualización paso a paso)
# ------------------------------------------------------------

def main():
    st.set_page_config(page_title="Viga Simple EC5", layout="wide")
    st.title("🪵 Calculadora de Viga Simple Apoyada (EC5)")
    st.markdown("**Procedimiento paso a paso** – Fórmulas, sustituciones y resultados")

    # Sidebar
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

    if st.button("Calcular", type="primary"):
        with st.spinner("Calculando..."):
            res = calcular_viga(L, b, h, G_k, Q_k_uniforme, Q_k_puntual, material, k_sys, k_cr, tiempo_fuego)

        st.success(f"✅ Cálculo completado. Índice global: {res['indice_global']:.1f}%")

        # --- Métricas rápidas ---
        col1, col2, col3 = st.columns(3)
        col1.metric("Flexión ELU", f"{res['flexion']['indice']:.1f}%", 
                    delta="OK" if res['flexion']['indice'] < 100 else "⚠️ NO CUMPLE")
        col2.metric("Cortante ELU", f"{res['cortante']['indice']:.1f}%",
                    delta="OK" if res['cortante']['indice'] < 100 else "⚠️ NO CUMPLE")
        col3.metric("Apariencia ELS", f"{res['flecha']['apariencia']['indice']:.1f}%",
                    delta="OK" if res['flecha']['apariencia']['indice'] < 100 else "⚠️ NO CUMPLE")

        # ------------------------------------------------------------
        # 1. ESFUERZOS ELU
        # ------------------------------------------------------------
        with st.expander("📊 1. ESFUERZOS (ELU)", expanded=True):
            st.markdown("""
            **Combinaciones de carga** según CTE DB-SE-AE:
            - ELU1: solo permanente (γ_G = 1.35)
            - ELU2: permanente + variable uniforme (γ_G = 1.35, γ_Q = 1.50)
            - ELU3: permanente + variable puntual en centro
            - ELU4: permanente + variable puntual cerca del apoyo (a = L - h)
            """)
            datos = {
                "Combinación": ["ELU1", "ELU2", "ELU3", "ELU4"],
                "M (kN·m)": [
                    f"{res['esfuerzos']['ELU1'][0]:.2f}",
                    f"{res['esfuerzos']['ELU2'][0]:.2f}",
                    f"{res['esfuerzos']['ELU3'][0]:.2f}",
                    f"{res['esfuerzos']['ELU4'][0]:.2f}",
                ],
                "V (kN)": [
                    f"{res['esfuerzos']['ELU1'][1]:.2f}",
                    f"{res['esfuerzos']['ELU2'][1]:.2f}",
                    f"{res['esfuerzos']['ELU3'][1]:.2f}",
                    f"{res['esfuerzos']['ELU4'][1]:.2f}",
                ],
            }
            st.dataframe(datos)
            st.caption("La combinación ELU2 (permanente + uniforme) gobierna en momento. ELU4 gobierna en cortante.")

        # ------------------------------------------------------------
        # 2. FLEXIÓN (ELU)
        # ------------------------------------------------------------
        with st.expander("📐 2. FLEXIÓN (ELU)", expanded=True):
            st.subheader("Datos de la sección")
            st.write(f"- Ancho: b = {b} mm")
            st.write(f"- Canto: h = {h} mm")
            st.write(f"- Módulo resistente: W_y = b·h²/6 = {b}·{h}²/6 = {res['seccion']['W_y']:.0f} mm³")
            st.write(f"- Momento de cálculo (ELU2): M_d = {res['flexion']['M']:.2f} kN·m = {res['flexion']['M']*1e6:.0f} N·mm")
            
            st.subheader("Tensión de cálculo")
            st.latex(r"\sigma_{m,d} = \frac{M_d}{W_y}")
            st.write(f"Sustituyendo: σ = {res['flexion']['M']*1e6:.0f} / {res['seccion']['W_y']:.0f} = {res['flexion']['sigma']:.2f} N/mm²")
            
            st.subheader("Resistencia de cálculo")
            st.latex(r"f_{m,d} = k_{mod} \cdot \frac{f_{m,k} \cdot k_{sys}}{\gamma_M}")
            st.write(f"- k_mod = {res['material']['k_mod']:.2f} (media duración, clase 1)")
            st.write(f"- f_m,k = {MATERIALES[material]['f_m_k']:.2f} N/mm²")
            st.write(f"- k_sys = {res['material']['k_sys']:.2f} (carga compartida)")
            st.write(f"- γ_M = {res['material']['gamma_M']:.2f}")
            st.write(f"f_m,d = {res['material']['k_mod']:.2f} · {MATERIALES[material]['f_m_k']:.2f} · {res['material']['k_sys']:.2f} / {res['material']['gamma_M']:.2f} = {res['flexion']['f_m_d']:.2f} N/mm²")
            
            st.subheader("Comprobación")
            st.latex(r"\sigma_{m,d} \leq f_{m,d}")
            st.write(f"{res['flexion']['sigma']:.2f} ≤ {res['flexion']['f_m_d']:.2f} → {'✅ Cumple' if res['flexion']['indice'] < 100 else '❌ No cumple'}")
            st.write(f"**Índice de aprovechamiento:** {res['flexion']['indice']:.1f}%")

        # ------------------------------------------------------------
        # 3. CORTANTE (ELU)
        # ------------------------------------------------------------
        with st.expander("✂️ 3. CORTANTE (ELU)", expanded=True):
            st.subheader("Datos")
            st.write(f"- Cortante de cálculo (ELU2): V_d = {res['cortante']['V']:.2f} kN = {res['cortante']['V']*1000:.0f} N")
            st.write(f"- Ancho efectivo: b·k_cr = {b} · {res['material']['k_cr']:.2f} = {res['cortante']['b_ef']:.0f} mm")
            st.write(f"- Canto: h = {h} mm")
            
            st.subheader("Tensión de cortante")
            st.latex(r"\tau_d = \frac{3}{2} \cdot \frac{V_d}{b \cdot k_{cr} \cdot h}")
            st.write(f"Sustituyendo: τ = 1.5 · {res['cortante']['V']*1000:.0f} / ({res['cortante']['b_ef']:.0f} · {h}) = {res['cortante']['tau']:.3f} N/mm²")
            
            st.subheader("Resistencia de cálculo")
            st.latex(r"f_{v,d} = k_{mod} \cdot \frac{f_{v,k} \cdot k_{sys}}{\gamma_M}")
            st.write(f"- k_mod = {res['material']['k_mod']:.2f}")
            st.write(f"- f_v,k = {MATERIALES[material]['f_v_k']:.2f} N/mm²")
            st.write(f"- k_sys = {res['material']['k_sys']:.2f}")
            st.write(f"- γ_M = {res['material']['gamma_M']:.2f}")
            st.write(f"f_v,d = {res['material']['k_mod']:.2f} · {MATERIALES[material]['f_v_k']:.2f} · {res['material']['k_sys']:.2f} / {res['material']['gamma_M']:.2f} = {res['cortante']['f_v_d']:.2f} N/mm²")
            
            st.subheader("Comprobación")
            st.latex(r"\tau_d \leq f_{v,d}")
            st.write(f"{res['cortante']['tau']:.3f} ≤ {res['cortante']['f_v_d']:.2f} → {'✅ Cumple' if res['cortante']['indice'] < 100 else '❌ No cumple'}")
            st.write(f"**Índice de aprovechamiento:** {res['cortante']['indice']:.1f}%")

        # ------------------------------------------------------------
        # 4. VUELCO LATERAL (LTB)
        # ------------------------------------------------------------
        with st.expander("🔄 4. VUELCO LATERAL (LTB)", expanded=True):
            st.subheader("Longitud eficaz")
            st.latex(r"L_{ef} = L + 2h")
            st.write(f"Sustituyendo: L_ef = {L*1000:.0f} + 2·{h} = {res['vuelco']['L_ef']:.0f} mm")
            
            st.subheader("Tensión crítica")
            st.latex(r"\sigma_{m,crit} = \frac{0{,}78 \cdot b^2 \cdot E_{0,05}}{h \cdot L_{ef}}")
            st.write(f"- b = {b} mm")
            st.write(f"- E_0,05 = {MATERIALES[material]['E_0_05']:.0f} N/mm²")
            st.write(f"- h = {h} mm")
            st.write(f"- L_ef = {res['vuelco']['L_ef']:.0f} mm")
            st.write(f"σ_crit = 0.78·{b}²·{MATERIALES[material]['E_0_05']:.0f} / ({h}·{res['vuelco']['L_ef']:.0f}) = {res['vuelco']['sigma_crit']:.2f} N/mm²")
            
            st.subheader("Esbeltez relativa")
            st.latex(r"\lambda_{rel,m} = \sqrt{\frac{f_{m,k}}{\sigma_{m,crit}}}")
            st.write(f"λ_rel,m = √({MATERIALES[material]['f_m_k']:.2f} / {res['vuelco']['sigma_crit']:.2f}) = {res['vuelco']['lambda']:.3f}")
            
            st.subheader("Coeficiente reductor")
            if res['vuelco']['lambda'] <= 0.75:
                st.write("λ_rel,m ≤ 0.75 → k_crit = 1.00")
            elif res['vuelco']['lambda'] <= 1.4:
                st.write("0.75 < λ_rel,m ≤ 1.4 → k_crit = 1.56 - 0.75·λ_rel,m")
            else:
                st.write("λ_rel,m > 1.4 → k_crit = 1/λ_rel,m²")
            st.write(f"k_crit = {res['vuelco']['k_crit']:.3f}")
            
            st.subheader("Comprobación")
            st.latex(r"\sigma_{m,d} \leq k_{crit} \cdot f_{m,d}")
            st.write(f"{res['flexion']['sigma']:.2f} ≤ {res['vuelco']['k_crit']:.3f} · {res['flexion']['f_m_d']:.2f} = {res['vuelco']['k_crit']*res['flexion']['f_m_d']:.2f}")
            st.write(f"→ {'✅ Cumple' if res['vuelco']['indice'] < 100 else '❌ No cumple'}")
            st.write(f"**Índice de aprovechamiento:** {res['vuelco']['indice']:.1f}%")

        # ------------------------------------------------------------
        # 5. FLECHAS (ELS)
        # ------------------------------------------------------------
        with st.expander("📏 5. FLECHAS (ELS)", expanded=True):
            st.markdown("**Incluye deformación por cortante** (Timoshenko):")
            st.latex(r"w_{total} = w_{flexión} \cdot \left(1 + \frac{24}{25} \cdot \frac{E}{G} \cdot \left(\frac{h}{L}\right)^2\right)")
            st.write(f"- E/G = {MATERIALES[material]['E_0_mean']:.0f} / {MATERIALES[material]['G_mean']:.0f} = {MATERIALES[material]['E_0_mean']/MATERIALES[material]['G_mean']:.2f}")
            st.write(f"- (h/L)² = ({h}/{L*1000:.0f})² = {(h/(L*1000))**2:.5f}")
            factor_cortante = 1 + (24/25)*(MATERIALES[material]['E_0_mean']/MATERIALES[material]['G_mean'])*(h/(L*1000))**2
            st.write(f"- Factor corrector = {factor_cortante:.4f} (añade ~{(factor_cortante-1)*100:.1f}%)")
            
            # Confort
            st.subheader("Confort (sensación al andar)")
            st.latex(r"u_{conf} = u_{inst,Q,1}")
            st.write(f"q = Q_k = {Q_k_uniforme:.2f} N/mm (1 kN/m = 1 N/mm)")
            st.write(f"u_flex = 5·q·L⁴/(384·E·I) = {res['flecha']['confort']['w_flex']:.2f} mm")
            st.write(f"u_conf = {res['flecha']['confort']['w_flex']:.2f} · {factor_cortante:.4f} = {res['flecha']['confort']['w']:.1f} mm")
            st.write(f"Límite: L/350 = {res['flecha']['confort']['limite']:.1f} mm")
            st.write(f"→ {'✅ Cumple' if res['flecha']['confort']['indice'] < 100 else '❌ No cumple'} (índice {res['flecha']['confort']['indice']:.1f}%)")
            
            # Integridad
            st.subheader("Integridad (daño a acabados)")
            st.latex(r"u_{int} = u_{inst,G} \cdot k_{def} + u_{inst,Q,1} \cdot (1 + \psi_2 \cdot k_{def})")
            st.write(f"- u_inst,G = {res['flecha']['integridad']['w_flex_G']:.2f} mm (flecha de G)")
            st.write(f"- u_inst,Q = {res['flecha']['integridad']['w_flex_Q']:.2f} mm (flecha de Q)")
            st.write(f"- k_def = {res['material']['k_def']:.2f}")
            st.write(f"- ψ2 = 0.30")
            w_int_calc = res['flecha']['integridad']['w_flex_G']*res['material']['k_def'] + res['flecha']['integridad']['w_flex_Q']*(1+0.3*res['material']['k_def'])
            w_int_total = res['flecha']['integridad']['w']
            st.write(f"u_int = {res['flecha']['integridad']['w_flex_G']:.2f}·{res['material']['k_def']:.2f} + {res['flecha']['integridad']['w_flex_Q']:.2f}·(1+0.3·{res['material']['k_def']:.2f}) = {w_int_calc:.2f} mm (sin cortante)")
            st.write(f"Con cortante: u_int = {w_int_calc:.2f} · {factor_cortante:.4f} = {w_int_total:.1f} mm")
            st.write(f"Límite: L/300 = {res['flecha']['integridad']['limite']:.1f} mm")
            st.write(f"→ {'✅ Cumple' if res['flecha']['integridad']['indice'] < 100 else '❌ No cumple'} (índice {res['flecha']['integridad']['indice']:.1f}%)")
            
            # Apariencia
            st.subheader("Apariencia (estética a largo plazo)")
            st.latex(r"u_{apa} = u_{inst,G} \cdot (1 + k_{def}) + \psi_2 \cdot u_{inst,Q,1} \cdot (1 + k_{def})")
            w_apa_calc = res['flecha']['integridad']['w_flex_G']*(1+res['material']['k_def']) + 0.3*res['flecha']['integridad']['w_flex_Q']*(1+res['material']['k_def'])
            w_apa_total = res['flecha']['apariencia']['w']
            st.write(f"u_apa = {res['flecha']['integridad']['w_flex_G']:.2f}·(1+{res['material']['k_def']:.2f}) + 0.3·{res['flecha']['integridad']['w_flex_Q']:.2f}·(1+{res['material']['k_def']:.2f}) = {w_apa_calc:.2f} mm (sin cortante)")
            st.write(f"Con cortante: u_apa = {w_apa_calc:.2f} · {factor_cortante:.4f} = {w_apa_total:.1f} mm")
            st.write(f"Límite: L/300 = {res['flecha']['apariencia']['limite']:.1f} mm")
            st.write(f"→ {'✅ Cumple' if res['flecha']['apariencia']['indice'] < 100 else '❌ No cumple'} (índice {res['flecha']['apariencia']['indice']:.1f}%)")

        # ------------------------------------------------------------
        # 6. SITUACIÓN DE INCENDIO
        # ------------------------------------------------------------
        with st.expander("🔥 6. SITUACIÓN DE INCENDIO", expanded=True):
            st.subheader("Sección reducida")
            st.latex(r"d_{ef} = d_{char,n} + k_0 \cdot d_0")
            st.write(f"- β_n = 0.80 mm/min (C24)")
            st.write(f"- t = {tiempo_fuego} min")
            st.write(f"- d_char = 0.80 · {tiempo_fuego} = {res['fuego']['d_ef']-7.0:.1f} mm")
            st.write(f"- d0 = 7.0 mm, k0 = 1.0 (t ≥ 20 min)")
            st.write(f"d_ef = {res['fuego']['d_ef']-7.0:.1f} + 7.0 = {res['fuego']['d_ef']:.1f} mm")
            
            st.write(f"Sección efectiva: {res['fuego']['b_fi']:.0f} × {res['fuego']['h_fi']:.0f} mm (3 caras expuestas)")
            st.write(f"W_y,fi = {res['fuego']['W_y_fi']:.0f} mm³")
            
            st.subheader("Flexión en incendio")
            st.latex(r"f_{m,fi,d} = k_{mod,fi} \cdot k_{fi} \cdot \frac{f_{m,k} \cdot k_{sys}}{\gamma_{M,fi}}")
            st.write(f"- k_mod,fi = 1.00, γ_M,fi = 1.00")
            st.write(f"- k_fi = 1.25 (percentil 20%)")
            st.write(f"f_m,fi,d = 1.00 · 1.25 · {MATERIALES[material]['f_m_k']:.2f} · {k_sys:.2f} / 1.00 = {res['fuego']['f_m_fi_d']:.2f} N/mm²")
            st.write(f"σ_m,fi,d = M_fi / W_y,fi = {res['fuego']['M_fi']*1e6:.0f} / {res['fuego']['W_y_fi']:.0f} = {res['fuego']['sigma_fi']:.2f} N/mm²")
            st.write(f"→ {'✅ Cumple' if res['fuego']['indice_flexion'] < 100 else '❌ No cumple'} (índice {res['fuego']['indice_flexion']:.1f}%)")
            
            st.subheader("Cortante en incendio")
            st.write(f"τ_fi,d = 1.5 · V_fi / (b_fi · k_cr · h_fi)")
            st.write(f"τ_fi,d = 1.5 · {res['fuego']['V_fi']*1000:.0f} / ({res['fuego']['b_fi']:.0f} · {k_cr:.2f} · {res['fuego']['h_fi']:.0f}) = {res['fuego']['tau_fi']:.3f} N/mm²")
            st.write(f"f_v,fi,d = 1.00 · 1.25 · {MATERIALES[material]['f_v_k']:.2f} · {k_sys:.2f} / 1.00 = {res['fuego']['f_v_fi_d']:.2f} N/mm²")
            st.write(f"→ {'✅ Cumple' if res['fuego']['indice_cortante'] < 100 else '❌ No cumple'} (índice {res['fuego']['indice_cortante']:.1f}%)")

        # ------------------------------------------------------------
        # 7. RESUMEN GLOBAL
        # ------------------------------------------------------------
        with st.expander("📋 7. RESUMEN GLOBAL", expanded=True):
            st.dataframe({
                "Comprobación": ["Flexión", "Cortante", "Vuelco lateral", "Flecha Confort", "Flecha Integridad", "Flecha Apariencia", "Fuego Flexión", "Fuego Cortante"],
                "Índice (%)": [
                    f"{res['flexion']['indice']:.1f}",
                    f"{res['cortante']['indice']:.1f}",
                    f"{res['vuelco']['indice']:.1f}",
                    f"{res['flecha']['confort']['indice']:.1f}",
                    f"{res['flecha']['integridad']['indice']:.1f}",
                    f"{res['flecha']['apariencia']['indice']:.1f}",
                    f"{res['fuego']['indice_flexion']:.1f}",
                    f"{res['fuego']['indice_cortante']:.1f}",
                ],
                "Cumple": [
                    "✅" if res['flexion']['indice'] < 100 else "❌",
                    "✅" if res['cortante']['indice'] < 100 else "❌",
                    "✅" if res['vuelco']['indice'] < 100 else "❌",
                    "✅" if res['flecha']['confort']['indice'] < 100 else "❌",
                    "✅" if res['flecha']['integridad']['indice'] < 100 else "❌",
                    "✅" if res['flecha']['apariencia']['indice'] < 100 else "❌",
                    "✅" if res['fuego']['indice_flexion'] < 100 else "❌",
                    "✅" if res['fuego']['indice_cortante'] < 100 else "❌",
                ]
            })
            st.metric("**Índice global**", f"{res['indice_global']:.1f}%",
                      delta="✅ Estructura válida" if res['indice_global'] < 100 else "❌ No cumple")

if __name__ == "__main__":
    main()
