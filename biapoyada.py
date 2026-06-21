import streamlit as st
import pandas as pd
import numpy as np
import math

# ============================================
# CONFIGURACIÓN DE LA PÁGINA
# ============================================
st.set_page_config(
    page_title="Calculadora de Viguetas de Forjado",
    page_icon="🏗️",
    layout="wide"
)

st.title("🏗️ Calculadora de Viguetas de Forjado")
st.markdown("---")

# ============================================
# PROPIEDADES DE MATERIALES (Madera)
# ============================================
WOOD_PROPERTIES = {
    'D27': {'fmk': 27.0, 'fvk': 3.8, 'E0med': 10500, 'E0k': 8800, 'Gmed': 660, 'rhom': 610, 'rhok': 510},
    'D30': {'fmk': 30.0, 'fvk': 4.0, 'E0med': 11000, 'E0k': 9200, 'Gmed': 690, 'rhom': 640, 'rhok': 540},
    'D35': {'fmk': 35.0, 'fvk': 4.2, 'E0med': 12000, 'E0k': 10000, 'Gmed': 750, 'rhom': 670, 'rhok': 570},
    'C24': {'fmk': 24.0, 'fvk': 4.0, 'E0med': 11000, 'E0k': 7400, 'Gmed': 690, 'rhom': 420, 'rhok': 350},
    'C30': {'fmk': 30.0, 'fvk': 4.0, 'E0med': 12000, 'E0k': 8000, 'Gmed': 750, 'rhom': 460, 'rhok': 380}
}

# ============================================
# FUNCIONES AUXILIARES
# ============================================
def get_kmod(service_class, duration):
    """Obtiene k_mod según clase de servicio y duración"""
    table = {
        1: {'permanente': 0.60, 'media': 0.80, 'corta': 0.90},
        2: {'permanente': 0.60, 'media': 0.80, 'corta': 0.90},
        3: {'permanente': 0.50, 'media': 0.65, 'corta': 0.70}
    }
    return table.get(service_class, {}).get(duration, 0.80)

def get_kdef(service_class):
    """Obtiene k_def según clase de servicio"""
    table = {1: 0.60, 2: 0.80, 3: 2.00}
    return table.get(service_class, 0.60)

def calculate_flecha(q, L, E, I):
    """Calcula flecha máxima para viga biapoyada con carga uniforme"""
    return (5 * q * (L * 1000)**4) / (384 * E * I)

def progress_bar(value, max_value=100, label=""):
    """Genera una barra de progreso HTML"""
    if value > 100:
        color = "danger"
    elif value > 80:
        color = "warning"
    else:
        color = "success"
    
    pct = min(value, 100)
    return f"""
    <div style="margin: 5px 0;">
        <div style="background: #ecf0f1; border-radius: 10px; height: 20px; overflow: hidden;">
            <div style="height: 100%; width: {pct}%; 
                        background: {'#e74c3c' if color == 'danger' else '#f39c12' if color == 'warning' else '#2ecc71'};
                        border-radius: 10px; transition: width 0.5s;">
            </div>
        </div>
        <div style="font-size: 0.8em; color: #666; text-align: right;">{value:.1f}%</div>
    </div>
    """

def badge(text, is_pass):
    """Genera una badge HTML"""
    color = "#28a745" if is_pass else "#dc3545"
    bg = "#d4edda" if is_pass else "#f8d7da"
    return f'<span style="background:{bg}; color:{color}; padding:3px 12px; border-radius:20px; font-weight:600; font-size:0.85em;">{text}</span>'

# ============================================
# SIDEBAR - ENTRADA DE DATOS
# ============================================
with st.sidebar:
    st.header("📐 Geometría")
    col1, col2 = st.columns(2)
    with col1:
        b = st.number_input("Ancho (b) mm", value=120, min_value=40, step=1)
    with col2:
        h = st.number_input("Canto (h) mm", value=240, min_value=40, step=1)
    
    L = st.number_input("Luz (L) m", value=4.5, min_value=1.0, max_value=12.0, step=0.1)
    spacing = st.number_input("Separación entre vigas (m)", value=0.80, min_value=0.30, max_value=1.20, step=0.05)
    
    st.header("📋 Material")
    wood_class = st.selectbox("Clase de madera", options=list(WOOD_PROPERTIES.keys()))
    service_class = st.selectbox("Clase de servicio", options=[1, 2, 3], format_func=lambda x: f"Clase {x}")
    fire_time = st.number_input("Resistencia al fuego (min)", value=30, min_value=15, max_value=120, step=5)
    
    st.header("⚖️ Cargas")
    gk = st.number_input("Peso propio (CC1) kN/m", value=1.78, step=0.01, format="%.2f")
    qk = st.number_input("Sobrecarga de uso (CC2) kN/m", value=1.60, step=0.01, format="%.2f")
    Pk = st.number_input("Carga puntual (kN)", value=2.00, step=0.10, format="%.2f")
    
    st.markdown("---")
    if st.button("🔢 Calcular", use_container_width=True):
        st.session_state.calculate = True
    
    if st.button("↺ Ejemplo del PDF", use_container_width=True):
        st.session_state.b = 120
        st.session_state.h = 240
        st.session_state.L = 4.5
        st.session_state.spacing = 0.80
        st.session_state.wood_class = 'D27'
        st.session_state.service_class = 1
        st.session_state.fire_time = 30
        st.session_state.gk = 1.78
        st.session_state.qk = 1.60
        st.session_state.Pk = 2.00
        st.session_state.calculate = True
        st.rerun()

# ============================================
# INICIALIZACIÓN
# ============================================
if 'calculate' not in st.session_state:
    st.session_state.calculate = True

# ============================================
# CÁLCULO PRINCIPAL
# ============================================
if st.session_state.calculate:
    # --- Propiedades del material ---
    props = WOOD_PROPERTIES[wood_class]
    
    # --- Propiedades de la sección ---
    A = b * h  # mm²
    Iy = (b * h**3) / 12  # mm⁴
    Iz = (h * b**3) / 12
    Wy = Iy / (h / 2)  # mm³
    Wz = Iz / (b / 2)
    iy = math.sqrt(Iy / A)
    iz = math.sqrt(Iz / A)
    weight = (A / 1e6) * props['rhom']  # kg/m
    
    # --- Coeficientes ---
    psi0, psi1, psi2 = 0.70, 0.50, 0.30
    gammaG, gammaQ = 1.35, 1.50
    gammaM = 1.30
    ksys = 1.0
    kh = 1.0
    kcr = 0.67
    kmod = get_kmod(service_class, 'media')
    kdef = get_kdef(service_class)
    
    # --- Cargas y esfuerzos ---
    # Momento flector máximo (viga biapoyada)
    M_G = gk * L**2 / 8  # kN·m
    M_Q = qk * L**2 / 8 + Pk * L / 4
    M_ELU = gammaG * M_G + gammaQ * M_Q
    
    # Cortante máximo
    V_G = gk * L / 2
    V_Q = qk * L / 2 + Pk / 2
    V_ELU = gammaG * V_G + gammaQ * V_Q
    
    # --- ELU: Flexión ---
    sigma_m = M_ELU * 1e6 / Wy  # N/mm²
    fmd = kmod * (props['fmk'] * kh * ksys) / gammaM
    flex_index = (sigma_m / fmd) * 100
    
    # --- ELU: Cortante ---
    tau = 1.5 * (V_ELU * 1000) / (b * kcr * h)  # N/mm²
    fvd = kmod * (props['fvk'] * ksys) / gammaM
    shear_index = (tau / fvd) * 100
    
    # --- ELS: Flechas ---
    E = props['E0med']  # N/mm²
    
    # Flecha instantánea por carga total
    q_total = gk + qk
    u_inst = (5 * q_total * (L * 1000)**4) / (384 * E * Iy)  # mm
    
    # Flecha diferida
    u_fin = u_inst * (1 + kdef)
    
    # Límites
    limit_integridad = (L * 1000) / 300
    limit_confort = (L * 1000) / 350
    limit_apariencia = (L * 1000) / 300
    
    # Flechas para cada estado (aproximado)
    u_int = u_inst * kdef
    u_conf = u_inst
    u_apa = u_inst * (1 + kdef)
    
    int_index = (u_int / limit_integridad) * 100 if limit_integridad > 0 else 0
    conf_index = (u_conf / limit_confort) * 100 if limit_confort > 0 else 0
    apa_index = (u_apa / limit_apariencia) * 100 if limit_apariencia > 0 else 0
    
    # --- Incendio (sección reducida) ---
    beta_n = 0.55  # mm/min
    d0 = 7.0
    dchar = beta_n * fire_time
    def_fire = dchar + d0
    
    b_ef = max(b - 2 * def_fire, 10)
    h_ef = max(h - def_fire, 10)
    A_ef = b_ef * h_ef
    Iy_ef = (b_ef * h_ef**3) / 12
    Wy_ef = Iy_ef / (h_ef / 2) if h_ef > 0 else 1
    
    kmod_fi = 1.0
    gammaM_fi = 1.0
    k_fi = 1.25  # Factor por incendio (20percentil)
    fmd_fi = kmod_fi * (props['fmk'] * k_fi * ksys) / gammaM_fi
    
    # Combinación de incendio: G + ψ1·Q
    M_fi = M_G + psi1 * M_Q
    V_fi = V_G + psi1 * V_Q
    
    sigma_fi = (M_fi * 1e6) / Wy_ef if Wy_ef > 0 else 0
    flex_fi_index = (sigma_fi / fmd_fi) * 100 if fmd_fi > 0 else 0
    
    tau_fi = 1.5 * (V_fi * 1000) / (b_ef * kcr * h_ef) if b_ef > 0 and h_ef > 0 else 0
    fvd_fi = kmod_fi * (props['fvk'] * k_fi * ksys) / gammaM_fi
    shear_fi_index = (tau_fi / fvd_fi) * 100 if fvd_fi > 0 else 0
    
    # ============================================
    # MOSTRAR RESULTADOS
    # ============================================
    
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Resumen")
        st.metric("Sección", f"{b}×{h} mm")
        st.metric("Luz", f"{L} m")
        st.metric("Material", wood_class)
        st.metric("Peso propio", f"{weight:.1f} kg/m")
    
    with col2:
        st.subheader("📈 Índices globales")
        max_elu = max(flex_index, shear_index)
        max_els = max(int_index, conf_index, apa_index)
        max_fi = max(flex_fi_index, shear_fi_index)
        
        st.markdown(f"**ELU:** {badge(f'{max_elu:.0f}%', max_elu < 100)}")
        st.markdown(f"**ELS:** {badge(f'{max_els:.0f}%', max_els < 100)}")
        st.markdown(f"**Incendio:** {badge(f'{max_fi:.0f}%', max_fi < 100)}")
    
    # ============================================
    # TABLA DE COMBINACIONES
    # ============================================
    st.markdown("---")
    st.subheader("📋 Combinaciones de carga y esfuerzos máximos")
    
    combos = {
        "ELU1": {"combo": "1.35·CC1", "M": gammaG * M_G, "V": gammaG * V_G},
        "ELU2": {"combo": "1.35·CC1 + 1.50·CC2", "M": gammaG * M_G + gammaQ * (qk * L**2 / 8), "V": gammaG * V_G + gammaQ * (qk * L / 2)},
        "ELU3": {"combo": "1.35·CC1 + 1.50·CC2.1", "M": gammaG * M_G + gammaQ * (Pk * L / 4), "V": gammaG * V_G + gammaQ * (Pk / 2)}
    }
    
    df_combos = pd.DataFrame([
        {"Combinación": k, "Expresión": v["combo"], "M_y (kN·m)": f"{v['M']:.2f}", "V_z (kN)": f"{v['V']:.2f}"}
        for k, v in combos.items()
    ])
    st.dataframe(df_combos, use_container_width=True, hide_index=True)
    
    # ============================================
    # ELU
    # ============================================
    st.markdown("---")
    st.subheader("🔴 Estado Límite Último (ELU)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Flexión")
        st.metric("M_y,d", f"{M_ELU:.2f} kN·m")
        st.metric("σ_m,y,d", f"{sigma_m:.2f} N/mm²")
        st.metric("f_m,y,d", f"{fmd:.2f} N/mm²")
        st.markdown(progress_bar(flex_index))
        st.caption(f"{'✅ Cumple' if flex_index < 100 else '❌ No cumple'}")
    
    with col2:
        st.markdown("#### Cortante")
        st.metric("V_z,d", f"{V_ELU:.2f} kN")
        st.metric("τ_z,d", f"{tau:.2f} N/mm²")
        st.metric("f_v,d", f"{fvd:.2f} N/mm²")
        st.markdown(progress_bar(shear_index))
        st.caption(f"{'✅ Cumple' if shear_index < 100 else '❌ No cumple'}")
    
    # ============================================
    # ELS
    # ============================================
    st.markdown("---")
    st.subheader("🟡 Estado Límite de Servicio (ELS)")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### Integridad")
        st.metric("u_int", f"{u_int:.1f} mm")
        st.metric("Límite", f"{limit_integridad:.1f} mm (L/300)")
        st.markdown(progress_bar(int_index))
        st.caption(f"{'✅ Cumple' if int_index < 100 else '❌ No cumple'}")
    
    with col2:
        st.markdown("#### Confort")
        st.metric("u_conf", f"{u_conf:.1f} mm")
        st.metric("Límite", f"{limit_confort:.1f} mm (L/350)")
        st.markdown(progress_bar(conf_index))
        st.caption(f"{'✅ Cumple' if conf_index < 100 else '❌ No cumple'}")
    
    with col3:
        st.markdown("#### Apariencia")
        st.metric("u_apa", f"{u_apa:.1f} mm")
        st.metric("Límite", f"{limit_apariencia:.1f} mm (L/300)")
        st.markdown(progress_bar(apa_index))
        st.caption(f"{'✅ Cumple' if apa_index < 100 else '❌ No cumple'}")
    
    # ============================================
    # INCENDIO
    # ============================================
    st.markdown("---")
    st.subheader("🔥 Situación de Incendio")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        st.markdown("#### Sección reducida")
        st.metric("b_ef", f"{b_ef:.0f} mm")
        st.metric("h_ef", f"{h_ef:.0f} mm")
        st.metric("A_ef", f"{A_ef:.0f} mm²")
    
    with col2:
        st.markdown("#### Flexión")
        st.metric("M_fi", f"{M_fi:.2f} kN·m")
        st.metric("σ_fi", f"{sigma_fi:.2f} N/mm²")
        st.metric("f_m,fi,d", f"{fmd_fi:.2f} N/mm²")
        st.markdown(progress_bar(flex_fi_index))
        st.caption(f"{'✅ Cumple' if flex_fi_index < 100 else '❌ No cumple'}")
    
    with col3:
        st.markdown("#### Cortante")
        st.metric("V_fi", f"{V_fi:.2f} kN")
        st.metric("τ_fi", f"{tau_fi:.2f} N/mm²")
        st.metric("f_v,fi,d", f"{fvd_fi:.2f} N/mm²")
        st.markdown(progress_bar(shear_fi_index))
        st.caption(f"{'✅ Cumple' if shear_fi_index < 100 else '❌ No cumple'}")
    
    # ============================================
    # PIE DE PÁGINA
    # ============================================
    st.markdown("---")
    st.caption("🔧 Calculadora basada en CTE DB SE-M y UNE-EN 338:2016")

else:
    st.info("👈 Ajusta los parámetros en la barra lateral y presiona 'Calcular'")
