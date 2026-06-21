import math
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# =========================================================
# CONFIGURACIÓN Y ESTILO GLOBAL
# =========================================================

st.set_page_config(page_title="Holzbau Pro", layout="wide", page_icon="🌲")

st.markdown("""
<style>
.block-container { padding-top: 2rem; padding-bottom: 2rem; }
.envelope-card {
    background: linear-gradient(135deg, #f8fafc 0%, #eff6ff 100%);
    border: 1px solid #bfdbfe;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 1rem;
    box-shadow: 0 4px 6px rgba(0,0,0,0.02);
}
.envelope-title {
    font-size: 1.1rem;
    font-weight: 700;
    color: #1e3a8a;
    margin-bottom: 8px;
    border-bottom: 2px solid #dbeafe;
    padding-bottom: 4px;
}
.val-highlight { font-size: 1.8rem; font-weight: 800; color: #111827; }
.val-sub { font-size: 0.95rem; color: #4b5563; font-weight: 500; margin-top: 4px; }
.math-box {
    background: #1e293b;
    color: #f8fafc;
    font-family: monospace;
    padding: 12px 16px;
    border-radius: 8px;
    margin: 10px 0;
    font-size: 1.05rem;
}
.math-res { color: #10b981; font-weight: bold; }
.badge-winner {
    background: #fef08a;
    color: #854d0e;
    padding: 4px 10px;
    border-radius: 99px;
    font-size: 0.85rem;
    font-weight: bold;
    display: inline-block;
    margin-bottom: 10px;
    border: 1px solid #fde047;
}
.expl-box {
    background: #f0fdf4;
    border-left: 4px solid #22c55e;
    padding: 12px 16px;
    border-radius: 4px;
    color: #166534;
    font-size: 0.95rem;
    margin-top: 10px;
}
.blue-box {
    background: #eff6ff;
    border: 1px solid #bfdbfe;
    color: #1e3a8a;
    padding: 12px 14px;
    border-radius: 8px;
    margin-bottom: 1rem;
    font-size: 0.95rem;
}
.orange-box {
    background: #fff7ed;
    border: 1px solid #fdba74;
    color: #9a3412;
    padding: 12px 14px;
    border-radius: 8px;
    margin-bottom: 1rem;
    font-size: 0.95rem;
}
.link-box {
    background: #faf5ff;
    border: 1px dashed #fde047;
    color: #854d0e;
    padding: 10px 14px;
    border-radius: 8px;
    margin-bottom: 1rem;
    font-size: 0.95rem;
    font-weight: 500;
}
.small-gray { color: #6b7280; font-size: 0.92rem; }

.result-box {
    padding: 1rem 1.2rem;
    border-radius: 14px;
    margin-bottom: 1rem;
    border: 1px solid #e5e7eb;
    background: #f9fafb;
}
.result-ok {
    background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
    border: 1px solid #10b981;
    color: #065f46;
}
.result-bad {
    background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
    border: 1px solid #ef4444;
    color: #991b1b;
}

.title-day1 {
    color: #2563eb;
    font-size: 1.2rem;
    font-weight: 700;
    border-bottom: 2px solid #bfdbfe;
    padding-bottom: 5px;
}
.title-activa {
    color: #d97706;
    font-size: 1.2rem;
    font-weight: 700;
    border-bottom: 2px solid #fde047;
    padding-bottom: 5px;
}
.title-day10k {
    color: #dc2626;
    font-size: 1.2rem;
    font-weight: 700;
    border-bottom: 2px solid #fca5a5;
    padding-bottom: 5px;
}
.val-big { font-size: 2.2rem; font-weight: 800; color: #111827; }
.val-unit { font-size: 1.1rem; font-weight: 500; color: #6b7280; }
.badge-ok {
    background: #dcfce7;
    color: #166534;
    padding: 4px 12px;
    border-radius: 99px;
    font-weight: bold;
    border: 1px solid #bbf7d0;
}
.badge-bad {
    background: #fee2e2;
    color: #991b1b;
    padding: 4px 12px;
    border-radius: 99px;
    font-weight: bold;
    border: 1px solid #fecaca;
}
.title-main {
    color: #1e293b;
    font-size: 1.3rem;
    font-weight: 700;
    border-bottom: 2px solid #cbd5e1;
    padding-bottom: 5px;
    margin-bottom: 15px;
}
.story-box {
    padding: 15px;
    border-radius: 8px;
    margin-bottom: 15px;
    height: 100%;
}
.story-title {
    font-size: 1.1rem;
    font-weight: bold;
    margin-bottom: 8px;
    margin-top: 0;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# BASES DE DATOS GLOBALES
# =========================================================

MATERIALES = {
    "C14": {"f_m_k": 14.0, "f_t_0_k": 8.0,  "f_c_0_k": 16.0, "f_v_k": 3.0, "E_0_mean": 7000,  "rho_k": 290, "rho_mean": 350},
    "C16": {"f_m_k": 16.0, "f_t_0_k": 10.0, "f_c_0_k": 17.0, "f_v_k": 3.2, "E_0_mean": 8000,  "rho_k": 310, "rho_mean": 370},
    "C18": {"f_m_k": 18.0, "f_t_0_k": 11.0, "f_c_0_k": 18.0, "f_v_k": 3.4, "E_0_mean": 9000,  "rho_k": 320, "rho_mean": 380},
    "C24": {"f_m_k": 24.0, "f_t_0_k": 14.5, "f_c_0_k": 21.0, "f_v_k": 4.0, "E_0_mean": 11000, "rho_k": 350, "rho_mean": 420},
    "C30": {"f_m_k": 30.0, "f_t_0_k": 18.0, "f_c_0_k": 26.0, "f_v_k": 4.0, "E_0_mean": 12000, "rho_k": 380, "rho_mean": 460},
    "GL24h": {"f_m_k": 24.0, "f_t_0_k": 16.5, "f_c_0_k": 24.0, "f_v_k": 3.5, "E_0_mean": 11600, "rho_k": 385, "rho_mean": 430},
    "GL28h": {"f_m_k": 28.0, "f_t_0_k": 19.5, "f_c_0_k": 26.5, "f_v_k": 3.5, "E_0_mean": 12600, "rho_k": 425, "rho_mean": 460},
    "GL32h": {"f_m_k": 32.0, "f_t_0_k": 22.5, "f_c_0_k": 29.0, "f_v_k": 3.8, "E_0_mean": 13700, "rho_k": 440, "rho_mean": 490},
}

KMOD_TABLA = {
    "1": {"Permanente": 0.60, "Larga": 0.70, "Media": 0.80, "Corta": 0.90, "Instantánea": 1.10},
    "2": {"Permanente": 0.60, "Larga": 0.70, "Media": 0.80, "Corta": 0.90, "Instantánea": 1.10},
    "3": {"Permanente": 0.50, "Larga": 0.55, "Media": 0.65, "Corta": 0.70, "Instantánea": 0.90},
}

KDEF_DICT = {"1": 0.60, "2": 0.80, "3": 2.00}

GAMMA_G = 1.35
GAMMA_Q = 1.50
PSI2_VIV = 0.30
K_CR = 0.67

# =========================================================
# FUNCIONES AUXILIARES GLOBALES
# =========================================================

def obtener_propiedades_material(material):
    return MATERIALES[material]

def obtener_k_mod(clase_servicio, duracion):
    return KMOD_TABLA[clase_servicio][duracion]

def calcular_propiedades_geometricas_rectangulo(b_mm, h_mm):
    A = b_mm * h_mm
    I_y = b_mm * h_mm**3 / 12
    I_z = h_mm * b_mm**3 / 12
    W_y = I_y / (h_mm / 2) if h_mm > 0 else 0
    W_z = I_z / (b_mm / 2) if b_mm > 0 else 0
    return {"A": A, "I_y": I_y, "I_z": I_z, "W_y": W_y, "W_z": W_z}

def convertir_a_lineal(Gk_m2, Quk_m2, s_m, b_mm, h_mm, densidad_mean):
    area_m2 = (b_mm / 1000) * (h_mm / 1000)
    peso_viga_kN_m = area_m2 * (densidad_mean * 9.81 / 1000)
    gk_total = (Gk_m2 * s_m) + peso_viga_kN_m
    quk = Quk_m2 * s_m
    return gk_total, quk, peso_viga_kN_m, area_m2

def calcular_esfuerzos(q_kNm, P_kN, L_m):
    M_q = q_kNm * L_m**2 / 8.0
    M_P = P_kN * L_m / 4.0
    V_q = q_kNm * L_m / 2.0
    V_P = P_kN / 2.0
    return {"M": M_q + M_P, "V": V_q + V_P, "Mq": M_q, "Mp": M_P, "Vq": V_q, "Vp": V_P}

def generar_todas_las_combinaciones(gk, quk, Qpk, L):
    combos = []

    # ELU
    q1 = GAMMA_G * gk
    P1 = 0.0
    combos.append({
        "id": "ELU-1", "tipo": "ELU", "nombre": "Solo permanente",
        "form_q": f"{GAMMA_G}·Gk", "num_q": f"{GAMMA_G} · {gk:.3f}",
        "form_P": "0", "num_P": "0",
        "q": q1, "P": P1, **calcular_esfuerzos(q1, P1, L),
        "explicacion": "A veces la carga de uso es nula. Comprobamos la viga solo con su peso mayorado."
    })

    q2 = GAMMA_G * gk + GAMMA_Q * quk
    P2 = 0.0
    combos.append({
        "id": "ELU-2", "tipo": "ELU", "nombre": "Uniforme dominante",
        "form_q": f"{GAMMA_G}·Gk + {GAMMA_Q}·Qu,k", "num_q": f"{GAMMA_G} · {gk:.3f} + {GAMMA_Q} · {quk:.3f}",
        "form_P": "0", "num_P": "0",
        "q": q2, "P": P2, **calcular_esfuerzos(q2, P2, L),
        "explicacion": "Carga de uso uniforme. Según el EN 1991-1-1, no actúa simultáneamente con la carga puntual local."
    })

    q3 = GAMMA_G * gk
    P3 = GAMMA_Q * Qpk
    combos.append({
        "id": "ELU-3", "tipo": "ELU", "nombre": "Puntual dominante",
        "form_q": f"{GAMMA_G}·Gk", "num_q": f"{GAMMA_G} · {gk:.3f}",
        "form_P": f"{GAMMA_Q}·Qp,k", "num_P": f"{GAMMA_Q} · {Qpk:.3f}",
        "q": q3, "P": P3, **calcular_esfuerzos(q3, P3, L),
        "explicacion": "Carga puntual local. Alternativa a la carga uniforme."
    })

    # ELS
    q4 = gk + quk
    P4 = 0.0
    combos.append({
        "id": "ELS-1", "tipo": "ELS_INST", "nombre": "Inst. Uniforme dom.",
        "form_q": "Gk + Qu,k", "num_q": f"{gk:.3f} + {quk:.3f}",
        "form_P": "0", "num_P": "0",
        "q": q4, "P": P4, **calcular_esfuerzos(q4, P4, L),
        "explicacion": "Flecha instantánea asumiendo el forjado con la carga uniforme."
    })

    q5 = gk
    P5 = Qpk
    combos.append({
        "id": "ELS-2", "tipo": "ELS_INST", "nombre": "Inst. Puntual dom.",
        "form_q": "Gk", "num_q": f"{gk:.3f}",
        "form_P": "Qp,k", "num_P": f"{Qpk:.3f}",
        "q": q5, "P": P5, **calcular_esfuerzos(q5, P5, L),
        "explicacion": "Flecha instantánea local producida por el objeto pesado en el centro."
    })

    q6 = gk + PSI2_VIV * quk
    P6 = 0.0
    combos.append({
        "id": "ELS-QP", "tipo": "ELS_QP", "nombre": "Cuasi-permanente",
        "form_q": "Gk + ψ2·Qu,k", "num_q": f"{gk:.3f} + {PSI2_VIV} · {quk:.3f}",
        "form_P": "0", "num_P": "0",
        "q": q6, "P": P6, **calcular_esfuerzos(q6, P6, L),
        "explicacion": "Cargas que se quedan a vivir. Generan fluencia a lo largo de los años."
    })

    return combos

def render_tabla_propiedades(titulo, filas, height=430, color="#2563eb"):
    filas_html = ""
    for prop, valor in filas:
        filas_html += f"""
        <tr>
            <td style="padding:10px 14px;border-bottom:1px solid #f1f5f9;color:#4b5563;">{prop}</td>
            <td style="padding:10px 14px;border-bottom:1px solid #f1f5f9;text-align:right;color:#111827;font-weight:600;">{valor}</td>
        </tr>
        """
    html = f"""
    <html>
    <head>
        <meta charset='utf-8'>
        <style>
            body{{margin:0;font-family:Arial;background:transparent;}}
            .card{{background:linear-gradient(180deg,#ffffff 0%,#f8fafc 100%);border:1px solid #e5e7eb;border-radius:18px;padding:18px;box-sizing:border-box;box-shadow:0 8px 24px rgba(15,23,42,0.06);}}
            .title{{font-size:20px;font-weight:700;margin-bottom:14px;color:#111827;padding-bottom:10px;border-bottom:3px solid {color};}}
            table{{width:100%;border-collapse:separate;border-spacing:0;font-size:14px;background:white;border:1px solid #e5e7eb;border-radius:12px;overflow:hidden;}}
            thead tr{{background:#f3f4f6;}}
            th{{text-align:left;padding:12px 14px;font-weight:700;color:#374151;border-bottom:1px solid #e5e7eb;}}
            th:last-child{{text-align:right;}}
            tbody tr:nth-child(even){{background:#fafafa;}}
        </style>
    </head>
    <body>
        <div class='card'>
            <div class='title'>{titulo}</div>
            <table>
                <thead><tr><th>Propiedad</th><th>Valor</th></tr></thead>
                <tbody>{filas_html}</tbody>
            </table>
        </div>
    </body>
    </html>
    """
    components.html(html, height=height, scrolling=False)

def mostrar_tarjeta_resultado(ratio, sigma_d, f_d, simbolo="σ"):
    cumple = ratio <= 1.0
    if cumple:
        color, estado, clase = "#10b981", "✅ Cumple", "result-ok"
    else:
        color, estado, clase = "#ef4444", "❌ No cumple", "result-bad"

    st.markdown(f"""
    <div class="result-box {clase}">
        <div style="display:flex; justify-content:space-between; align-items:center; gap:12px; flex-wrap:wrap;">
            <div>
                <div style="font-size:1.4rem; font-weight:800;">{estado}</div>
                <div style="margin-top:0.35rem; font-size:1rem;">η = {ratio:.2f}</div>
            </div>
            <div style="min-width:140px;text-align:center;background:white;border:2px solid {color};border-radius:16px;padding:0.8rem 1rem;box-shadow:0 4px 12px rgba(0,0,0,0.04);">
                <div style="font-size:0.9rem; color:#6b7280;">Aprovechamiento</div>
                <div style="font-size:2rem; font-weight:800; color:{color};">η = {ratio:.2f}</div>
            </div>
        </div>
        <div style="margin-top:0.8rem; font-size:0.95rem;">
            <b>{simbolo}<sub>d</sub></b> = {sigma_d:.2f} N/mm² &nbsp;&nbsp;|&nbsp;&nbsp;
            <b>f<sub>d</sub></b> = {f_d:.2f} N/mm²
        </div>
    </div>
    """, unsafe_allow_html=True)

def mostrar_datos_globales(mat, clase_servicio, b_mm, h_mm, L_m, gk, quk, Qpk_kN):
    st.markdown(f"""
    <div class="blue-box">
    <b>Datos globales adoptados</b><br>
    Material: <b>{mat}</b> &nbsp;&nbsp;|&nbsp;&nbsp;
    Clase de servicio: <b>{clase_servicio}</b> &nbsp;&nbsp;|&nbsp;&nbsp;
    Sección: <b>{b_mm:.0f} × {h_mm:.0f} mm</b> &nbsp;&nbsp;|&nbsp;&nbsp;
    Luz: <b>{L_m:.2f} m</b><br>
    gk total: <b>{gk:.3f} kN/m</b> &nbsp;&nbsp;|&nbsp;&nbsp;
    quk: <b>{quk:.3f} kN/m</b> &nbsp;&nbsp;|&nbsp;&nbsp;
    Qpk: <b>{Qpk_kN:.2f} kN</b>
    </div>
    """, unsafe_allow_html=True)

# =========================================================
# ENTRADAS GLOBALES
# =========================================================

st.sidebar.markdown("## 🧭 Navegación")
page = st.sidebar.radio(
    "Ir a...",
    [
        "🏠 1. Combinaciones",
        "📐 2. Flexión y Axil",
        "✂️ 3. Cortante ($k_{cr}$)",
        "📏 4. Flecha y $k_{def}$",
        "📳 5. Vibraciones"
    ],
    label_visibility="collapsed"
)

st.sidebar.divider()

st.sidebar.markdown("### 📐 Geometría y Sección")
L_m = st.sidebar.number_input("Luz de la viga L [m]", value=5.00, step=0.10, min_value=0.50)
s_m = st.sidebar.number_input("Ancho tributario s [m]", value=1.00, step=0.05, min_value=0.10)
b_mm = st.sidebar.number_input("Base viga b [mm]", value=120, step=10)
h_mm = st.sidebar.number_input("Canto viga h [mm]", value=280, step=10)

st.sidebar.markdown("### ⚖️ Cargas (Valores Base)")
Gk_m2 = st.sidebar.number_input("Permanente Gk [kN/m²]", value=1.00, step=0.10)
Quk_m2 = st.sidebar.number_input("Uso Uniforme Qu,k [kN/m²]", value=2.00, step=0.10)
Qpk_kN = st.sidebar.number_input("Uso Puntual local Qp,k [kN] (alternativa a la uniforme)", value=2.00, step=0.10)

st.sidebar.markdown("### 🌲 Material y Entorno")
mat = st.sidebar.selectbox("Clase de Madera", list(MATERIALES.keys()), index=5)
clase_servicio = st.sidebar.selectbox("Clase de Servicio", ["1", "2", "3"], index=0)

# =========================================================
# CÁLCULOS GLOBALES
# =========================================================

props_geo = calcular_propiedades_geometricas_rectangulo(b_mm, h_mm)
props_mat = obtener_propiedades_material(mat)

gk, quk, peso_viga, area_m2 = convertir_a_lineal(
    Gk_m2, Quk_m2, s_m, b_mm, h_mm, props_mat["rho_mean"]
)

combos = generar_todas_las_combinaciones(gk, quk, Qpk_kN, L_m)

combos_elu = [c for c in combos if c["tipo"] == "ELU"]
combos_els_inst = [c for c in combos if c["tipo"] == "ELS_INST"]
combo_qp = [c for c in combos if c["tipo"] == "ELS_QP"][0]

elu_max_M = max(combos_elu, key=lambda x: x["M"])
elu_max_V = max(combos_elu, key=lambda x: x["V"])
els_inst_max_M = max(combos_els_inst, key=lambda x: x["M"])

duracion_M = "Permanente" if elu_max_M["id"] == "ELU-1" else "Media"
duracion_V = "Permanente" if elu_max_V["id"] == "ELU-1" else "Media"

# =========================================================
# PÁGINA 1: COMBINACIONES
# =========================================================

if page == "🏠 1. Combinaciones":
    st.title("Forjado: Acciones y Combinaciones (Eurocódigo EN 1991-1-1)")

    st.markdown("""
    <div class="blue-box">
    <b>Actualizado a Eurocódigo 1:</b> La carga uniforme de uso y la puntual son situaciones <b>alternativas</b>, no actúan simultáneamente.
    Además, el programa calcula automáticamente el <b>peso propio de la viga</b>.
    </div>
    """, unsafe_allow_html=True)

    mostrar_datos_globales(mat, clase_servicio, b_mm, h_mm, L_m, gk, quk, Qpk_kN)

    st.subheader("Peso propio calculado automáticamente")
    c1, c2, c3 = st.columns(3)
    c1.metric("Densidad usada ρmean [kg/m³]", f"{props_mat['rho_mean']:.0f}")
    c2.metric("Área sección [m²]", f"{area_m2:.4f}")
    c3.metric("Peso propio viga [kN/m]", f"{peso_viga:.3f}")

    st.subheader("Cargas sobre la viga (Base sin mayorar)")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Luz (L)", f"{L_m:.2f} m")
    c2.metric("Permanente lineal (gk)", f"{gk:.3f} kN/m")
    c3.metric("Uso lineal (qu,k)", f"{quk:.3f} kN/m")
    c4.metric("Uso puntual (Qp,k)", f"{Qpk_kN:.2f} kN")
    st.markdown(
        f'<div class="small-gray">gk = (Gk · s) + peso propio viga = ({Gk_m2:.2f} · {s_m:.2f}) + {peso_viga:.3f}</div>',
        unsafe_allow_html=True
    )
    st.divider()

    st.subheader("Envolventes de Cálculo (Valores Críticos)")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div class="envelope-card">
            <div class="envelope-title">🔥 ELU (Resistencia / Rotura)</div>
            <div class="val-highlight">{elu_max_M['M']:.2f} <span style="font-size:1rem;font-weight:500;">kN·m</span></div>
            <div class="val-sub">M<sub>d</sub> máximo • <span style="color:#2563eb;">{elu_max_M['id']}</span></div>
            <div style="margin-top:12px;"></div>
            <div class="val-highlight">{elu_max_V['V']:.2f} <span style="font-size:1rem;font-weight:500;">kN</span></div>
            <div class="val-sub">V<sub>d</sub> máximo • <span style="color:#2563eb;">{elu_max_V['id']}</span></div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="envelope-card" style="background: linear-gradient(135deg, #f8fafc 0%, #f0fdf4 100%); border-color: #bbf7d0;">
            <div class="envelope-title" style="color: #166534; border-bottom-color: #dcfce7;">📏 ELS Instantáneo (Flecha)</div>
            <div class="val-highlight">{els_inst_max_M['M']:.2f} <span style="font-size:1rem;font-weight:500;">kN·m</span></div>
            <div class="val-sub">M<sub>inst</sub> máximo • <span style="color:#059669;">{els_inst_max_M['id']}</span></div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="envelope-card" style="background: linear-gradient(135deg, #fdf8f6 0%, #fef3c7 100%); border-color: #fde047;">
            <div class="envelope-title" style="color: #854d0e; border-bottom-color: #fef08a;">⏳ ELS Cuasi-permanente (Fluencia)</div>
            <div class="val-highlight">{combo_qp['q']:.3f} <span style="font-size:1rem;font-weight:500;">kN/m</span></div>
            <div class="val-sub">Carga lineal base (q<sub>qp</sub>)</div>
            <div style="margin-top:12px;"></div>
            <div class="val-highlight">{combo_qp['P']:.2f} <span style="font-size:1rem;font-weight:500;">kN</span></div>
            <div class="val-sub">Carga puntual base (P<sub>qp</sub>)</div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    st.header("🔍 Explorador de Combinaciones")
    opciones_combos = {f"[{c['id']}] {c['nombre']}": c for c in combos}
    seleccion = st.selectbox("Elige combinación:", list(opciones_combos.keys()), label_visibility="collapsed")
    c_sel = opciones_combos[seleccion]

    es_max_M = c_sel["id"] == elu_max_M["id"]
    es_max_V = c_sel["id"] == elu_max_V["id"]
    if es_max_M or es_max_V:
        mensaje = []
        if es_max_M:
            mensaje.append("Momento (ELU)")
        if es_max_V:
            mensaje.append("Cortante (ELU)")
        st.markdown(f"<div class='badge-winner'>🏆 Gobernante para: {' y '.join(mensaje)}</div>", unsafe_allow_html=True)

    colA, colB = st.columns([1.1, 1.3])
    with colA:
        st.markdown("**1. Cargas de la combinación**")
        st.markdown(f"""
        <div class="math-box">
        q = {c_sel['form_q']}<br>
        q = {c_sel['num_q']} = <span class="math-res">{c_sel['q']:.3f} kN/m</span>
        <hr style="border-color:#334155; margin:10px 0;">
        P = {c_sel['form_P']}<br>
        P = {c_sel['num_P']} = <span class="math-res">{c_sel['P']:.2f} kN</span>
        </div>
        """, unsafe_allow_html=True)

    with colB:
        st.markdown("**2. Esfuerzos resultantes (Desglose Lineal + Puntual)**")
        st.markdown(f"""
        <div class="math-box" style="background:#f8fafc; color:#0f172a; border:1px solid #cbd5e1;">
        M<sub>max</sub> = M<sub>q</sub> + M<sub>P</sub> = (q·L²/8) + (P·L/4)<br>
        M<sub>max</sub> = {c_sel['Mq']:.2f} + {c_sel['Mp']:.2f} = <span style="color:#2563eb; font-weight:bold;">{c_sel['M']:.2f} kN·m</span>
        <hr style="border-color:#e2e8f0; margin:10px 0;">
        V<sub>max</sub> = V<sub>q</sub> + V<sub>P</sub> = (q·L/2) + (P/2)<br>
        V<sub>max</sub> = {c_sel['Vq']:.2f} + {c_sel['Vp']:.2f} = <span style="color:#2563eb; font-weight:bold;">{c_sel['V']:.2f} kN</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("**3. Justificación Eurocódigo 1:**")
    st.markdown(f"<div class='expl-box'>{c_sel['explicacion']}</div>", unsafe_allow_html=True)

    st.divider()
    st.header("Tablas Resumen y Desarrollo Numérico")

    tab1, tab2 = st.tabs(["📊 Tablas de Combinaciones", "🧮 Fórmulas de Cálculo y el misterio del k_mod"])

    with tab1:
        def mostrar_df(combos_list):
            df = pd.DataFrame(combos_list)
            df_show = df[["id", "nombre", "q", "P", "M", "V"]].copy()
            df_show.columns = ["ID", "Combinación", "q [kN/m]", "P [kN]", "Momento [kN·m]", "Cortante [kN]"]
            for col in ["q [kN/m]", "P [kN]", "Momento [kN·m]", "Cortante [kN]"]:
                df_show[col] = df_show[col].apply(lambda x: f"{x:.3f}")
            st.dataframe(df_show, use_container_width=True, hide_index=True)

        st.subheader("ELU (Estado Límite Último)")
        mostrar_df(combos_elu)
        st.subheader("ELS (Estado Límite de Servicio)")
        mostrar_df(combos_els_inst + [combo_qp])

    with tab2:
        st.write("**1. Conversión de cargas superficiales a lineales (con Peso Propio de la viga)**")
        st.latex(rf"g_{{k,total}} = (G_k \cdot s) + Peso_{{viga}} = ({Gk_m2:.2f} \cdot {s_m:.2f}) + {peso_viga:.3f} = {gk:.3f}\ \mathrm{{kN/m}}")
        st.latex(rf"q_{{u,k}} = Q_{{u,k}} \cdot s = {Quk_m2:.2f} \cdot {s_m:.2f} = {quk:.3f}\ \mathrm{{kN/m}}")

        st.write("**2. Esfuerzos máximos en viga biapoyada**")
        st.latex(r"M_{max} = q\frac{L^2}{8} + P\frac{L}{4}")
        st.latex(r"V_{max} = q\frac{L}{2} + \frac{P}{2}")

        st.write("**3. Coeficientes Normativos (Seguridad y Alternancia)**")
        st.latex(rf"\gamma_G = {GAMMA_G:.2f} \quad \gamma_Q = {GAMMA_Q:.2f} \quad \psi_2 = {PSI2_VIV:.2f}")

        st.write("**4. La Regla del $k_{{mod}}$ (Clase de Duración de la Carga)**")
        st.info("El $k_{mod}$ no se usa para calcular los kilos o los esfuerzos, sino para calcular la **resistencia** de la madera en las siguientes pestañas. La norma dice: *se toma el kmod de la acción de menor duración de la combinación ganadora*.")

        kmod_perm = obtener_k_mod(clase_servicio, "Permanente")
        kmod_med = obtener_k_mod(clase_servicio, "Media")

        st.write(f"- Si gana **ELU-1**: duración = Permanente → $k_{{mod}} = {kmod_perm}$")
        st.write(f"- Si gana **ELU-2** o **ELU-3**: duración = Media → $k_{{mod}} = {kmod_med}$")
        st.markdown(f"**En el caso actual, para Momento ha ganado {elu_max_M['id']}, por lo que se usará $k_{{mod}} = {obtener_k_mod(clase_servicio, duracion_M)}$.**")

# =========================================================
# PÁGINA 2: FLEXIÓN Y AXIL
# =========================================================

elif page == "📐 2. Flexión y Axil":
    st.title("Cálculo de secciones de madera")
    mostrar_datos_globales(mat, clase_servicio, b_mm, h_mm, L_m, gk, quk, Qpk_kN)

    tipo = st.radio("Selecciona el caso a comprobar:", ["Flexión", "Tracción paralela a la fibra", "Compresión paralela a la fibra"], horizontal=True)

    gamma_M = 1.25 if "GL" in mat else 1.30

    if tipo == "Flexión":
        k_mod = obtener_k_mod(clase_servicio, duracion_M)
        st.markdown(f"""
        <div class='link-box'>
        🔗 <b>Vinculado Automáticamente:</b><br>
        - Momento gobernante: <b>{elu_max_M['nombre']}</b> ({elu_max_M['id']}) → $M_d = {elu_max_M['M']:.2f} \ kN\cdot m$<br>
        - Duración deducida: <b>{duracion_M}</b> → $k_{{mod}} = {k_mod}$<br>
        - Material detectado: <b>{'Laminado' if 'GL' in mat else 'Macizo'}</b> → $\\gamma_M = {gamma_M}$
        </div>
        """, unsafe_allow_html=True)
        M_kNm = elu_max_M["M"]
    else:
        st.markdown("<div class='link-box'>✏️ <b>Modo Manual:</b> El axil no proviene del modelo de forjado simple. Introdúcelo manualmente.</div>", unsafe_allow_html=True)
        F_kN = st.number_input("Esfuerzo axial Fd [kN]", min_value=0.0, value=114.0, step=1.0)
        duracion_manual = st.selectbox("Duración de carga", ["Permanente", "Larga", "Media", "Corta", "Instantánea"], index=2)
        k_mod = obtener_k_mod(clase_servicio, duracion_manual)

    k_h = 1.0
    if tipo in ["Flexión", "Tracción paralela a la fibra"]:
        if "GL" in mat:
            k_h = min((600 / h_mm)**0.1, 1.1) if h_mm < 600 else 1.0
        else:
            k_h = min((150 / h_mm)**0.2, 1.3) if h_mm < 150 else 1.0

    st.markdown("""
    <div class="small-gray">
    Nota: <b>k<sub>h</sub></b> es el efecto tamaño. En flexión y tracción puede aumentar la resistencia en piezas de canto moderado.
    </div>
    """, unsafe_allow_html=True)

    if tipo == "Tracción paralela a la fibra":
        f_k = props_mat["f_t_0_k"]
        notacion = {"sigma": r"\sigma_{t,0,d}", "f_k": r"f_{t,0,k}", "f_d": r"f_{t,0,d}"}
    elif tipo == "Compresión paralela a la fibra":
        f_k = props_mat["f_c_0_k"]
        k_h = 1.0
        notacion = {"sigma": r"\sigma_{c,0,d}", "f_k": r"f_{c,0,k}", "f_d": r"f_{c,0,d}"}
    else:
        f_k = props_mat["f_m_k"]
        notacion = {"sigma": r"\sigma_{m,d}", "f_k": r"f_{m,k}", "f_d": r"f_{m,d}"}

    col1, col2 = st.columns(2)
    with col1:
        filas_mat = [
            ("Material", mat),
            ("<i>f</i><sub>m,k</sub>", f"{props_mat['f_m_k']:.1f} N/mm²"),
            ("<i>k</i><sub>h</sub>", f"{k_h:.3f}"),
            ("Clase de servicio", clase_servicio),
            ("<i>k</i><sub>mod</sub>", f"{k_mod:.2f}"),
            ("γ<sub>M</sub>", f"{gamma_M:.2f}")
        ]
        render_tabla_propiedades("Material automático", filas_mat, height=400, color="#2563eb")

    with col2:
        filas_sec = [
            ("<i>b</i>", f"{b_mm:.1f} mm"),
            ("<i>h</i>", f"{h_mm:.1f} mm"),
            ("<i>A</i>", f"{props_geo['A']:.2f} mm²"),
            ("<i>W</i><sub>y</sub>", f"{props_geo['W_y']:.2f} mm³")
        ]
        render_tabla_propiedades("Sección automática", filas_sec, height=400, color="#7c3aed")

    if tipo == "Flexión":
        W_mm3 = props_geo["W_y"]
        M_Nmm = M_kNm * 1_000_000.0
        sigma_d = M_Nmm / W_mm3
        f_d = (k_mod * k_h * f_k) / gamma_M
        ratio = sigma_d / f_d

        st.subheader("Desarrollo del cálculo")
        st.latex(rf"{notacion['f_d']} = \frac{{k_{{mod}} \cdot k_h \cdot f_{{m,k}}}}{{\gamma_M}} = \frac{{{k_mod:.2f} \cdot {k_h:.3f} \cdot {f_k:.2f}}}{{{gamma_M:.2f}}} = {f_d:.2f}\ \mathrm{{N/mm}}^2")
        st.latex(rf"{notacion['sigma']} = \frac{{M_d}}{{W}} = \frac{{{M_kNm:.2f}\cdot 10^6}}{{{W_mm3:.2f}}} = {sigma_d:.2f}\ \mathrm{{N/mm}}^2")

        st.header("Resultado")
        mostrar_tarjeta_resultado(ratio, sigma_d, f_d, simbolo="σ")

    else:
        A_mm2 = props_geo["A"]
        F_N = F_kN * 1000.0
        sigma_d = F_N / A_mm2
        f_d = (k_mod * k_h * f_k) / gamma_M
        ratio = sigma_d / f_d

        st.subheader("Desarrollo del cálculo")
        st.latex(rf"{notacion['f_d']} = \frac{{k_{{mod}} \cdot k_h \cdot f_k}}{{\gamma_M}} = \frac{{{k_mod:.2f} \cdot {k_h:.3f} \cdot {f_k:.2f}}}{{{gamma_M:.2f}}} = {f_d:.2f}\ \mathrm{{N/mm}}^2")
        st.latex(rf"{notacion['sigma']} = \frac{{{F_kN:.2f} \cdot 1000}}{{{A_mm2:.2f}}} = {sigma_d:.2f}\ \mathrm{{N/mm}}^2")

        st.header("Resultado")
        mostrar_tarjeta_resultado(ratio, sigma_d, f_d, simbolo="σ")

# =========================================================
# PÁGINA 3: CORTANTE
# =========================================================

elif page == "✂️ 3. Cortante ($k_{cr}$)":
    st.title("Módulo de Cortante (ELU)")
    mostrar_datos_globales(mat, clase_servicio, b_mm, h_mm, L_m, gk, quk, Qpk_kN)

    kmod = obtener_k_mod(clase_servicio, duracion_V)
    gamma_m = 1.25 if "GL" in mat else 1.30

    st.markdown(f"""
    <div class='link-box'>
    🔗 <b>Vinculado Automáticamente:</b><br>
    - Cortante máximo: <b>{elu_max_V['V']:.2f} kN</b><br>
    - Carga lineal de la combinación: <b>{elu_max_V['q']:.2f} kN/m</b><br>
    - Combinación gobernante: <b>{elu_max_V['nombre']}</b> ({elu_max_V['id']})<br>
    - Duración deducida: <b>{duracion_V}</b> → $k_{{mod}} = {kmod}$<br>
    - $\\gamma_M = {gamma_m}$
    </div>
    """, unsafe_allow_html=True)

    Vd = elu_max_V["V"]
    qd = elu_max_V["q"]
    fvk = props_mat["f_v_k"]

    h_m = h_mm / 1000.0
    Vd_red = max(Vd - (qd * h_m), 0)
    b_eff = b_mm * K_CR
    tau_d = (1.5 * Vd_red * 1000) / (b_eff * h_mm)
    fvd = (fvk * kmod) / gamma_m
    ratio = tau_d / fvd

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<div class='envelope-card'>", unsafe_allow_html=True)
        st.markdown("<div class='title-main'>1. Tensión Actuante (Lo que sufre la viga)</div>", unsafe_allow_html=True)
        st.markdown(f"<span class='val-big'>{tau_d:.2f}</span> <span class='val-unit'>N/mm²  (τ<sub>d</sub>)</span>", unsafe_allow_html=True)
        st.write(f"• Cortante inicial: **{Vd:.2f} kN**")
        st.write(f"• Reducción en apoyo: **-{Vd - Vd_red:.2f} kN**")
        st.write(f"• Cortante reducido: **{Vd_red:.2f} kN**")
        st.write(f"• Base efectiva: **{b_eff:.1f} mm**")
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='envelope-card'>", unsafe_allow_html=True)
        st.markdown("<div class='title-main'>2. Tensión Resistente (Lo que aguanta el material)</div>", unsafe_allow_html=True)
        st.markdown(f"<span class='val-big'>{fvd:.2f}</span> <span class='val-unit'>N/mm²  (f<sub>v,d</sub>)</span>", unsafe_allow_html=True)
        st.write(f"• Resistencia característica: **{fvk:.2f} N/mm²**")
        st.write(f"• kmod = **{kmod:.2f}**")
        st.write(f"• γM = **{gamma_m:.2f}**")
        st.markdown("</div>", unsafe_allow_html=True)

    st.subheader("Veredicto Estructural")
    mostrar_tarjeta_resultado(ratio, tau_d, fvd, simbolo="τ")

    st.markdown("### 🧮 Cómo se calculó paso a paso")
    with st.expander("Ver fórmulas completas"):
        st.latex(rf"V_{{d,red}} = V_d - q_d \cdot h = {Vd:.2f} - ({qd:.2f} \cdot {h_m:.2f}) = {Vd_red:.2f}\ \mathrm{{kN}}")
        st.latex(rf"\tau_d = \frac{{3 \cdot V_{{d,red}}}}{{2 \cdot b_{{eff}} \cdot h}} = \frac{{3 \cdot {Vd_red:.2f} \cdot 10^3}}{{2 \cdot ({b_mm} \cdot {K_CR}) \cdot {h_mm}}} = {tau_d:.2f}\ \mathrm{{N/mm^2}}")
        st.latex(rf"f_{{v,d}} = k_{{mod}} \cdot \frac{{f_{{v,k}}}}{{\gamma_M}} = {kmod:.2f} \cdot \frac{{{fvk:.2f}}}{{{gamma_m:.2f}}} = {fvd:.2f}\ \mathrm{{N/mm^2}}")

# =========================================================
# PÁGINA 4: FLECHA Y KDEF
# =========================================================

elif page == "📏 4. Flecha y $k_{def}$":
    st.title("Módulo de Flecha (Deformaciones y kdef)")
    mostrar_datos_globales(mat, clase_servicio, b_mm, h_mm, L_m, gk, quk, Qpk_kN)

    kdef = KDEF_DICT[clase_servicio]
    E_mean = props_mat["E_0_mean"]

    st.markdown(f"""
    <div class='link-box'>
    🔗 <b>Vinculado Automáticamente:</b><br>
    - Módulo de elasticidad: <b>{E_mean} N/mm²</b><br>
    - Clase de servicio {clase_servicio} → <b>kdef = {kdef}</b>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="blue-box">
    Hipótesis adoptada en esta pestaña:<br>
    - Para <b>flecha instantánea</b>, se toma el caso más desfavorable entre la sobrecarga uniforme y la carga puntual local, consideradas <b>alternativas</b>.<br>
    - La <b>flecha activa</b> se estima de forma simplificada como: <b>w<sub>activa</sub> = w<sub>fin</sub> - w<sub>inst,G</sub></b>, suponiendo que cerramientos y acabados se ejecutan tras la deformación inicial por peso propio.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Selecciona tus límites normativos")
    colA, colB, colC = st.columns(3)
    limite_inst = colA.selectbox("Límite Instantánea", [300, 400, 500], format_func=lambda x: f"L/{x}")
    limite_activa = colB.selectbox("Límite Activa (Tabiques)", [400, 500], format_func=lambda x: f"L/{x}")
    limite_fin = colC.selectbox("Límite Final Neto", [250, 300, 400], format_func=lambda x: f"L/{x}")

    def flecha_uniforme(q_kNm, L_m, E_mean, I_mm4):
        return (5.0 / 384.0) * ((q_kNm * (L_m * 1000)**4) / (E_mean * I_mm4))

    def flecha_puntual(P_kN, L_m, E_mean, I_mm4):
        return (1.0 / 48.0) * (((P_kN * 1000) * (L_m * 1000)**3) / (E_mean * I_mm4))

    I_y = props_geo["I_y"]

    w_inst_G = flecha_uniforme(gk, L_m, E_mean, I_y)
    w_inst_Q_uni = flecha_uniforme(quk, L_m, E_mean, I_y)
    w_inst_Q_pun = flecha_puntual(Qpk_kN, L_m, E_mean, I_y)

    # Hipótesis simplificada: acciones alternativas en ELS instantáneo
    w_inst_Q = max(w_inst_Q_uni, w_inst_Q_pun)
    w_inst_total = w_inst_G + w_inst_Q

    w_creep_G = w_inst_G * kdef
    w_creep_Q = w_inst_Q * (PSI2_VIV * kdef)
    w_creep_total = w_creep_G + w_creep_Q

    w_fin_G = w_inst_G + w_creep_G
    w_fin_Q = w_inst_Q + w_creep_Q
    w_fin_total = w_inst_total + w_creep_total

    w_activa = w_fin_total - w_inst_G

    w_lim_inst = (L_m * 1000) / limite_inst
    w_lim_activa = (L_m * 1000) / limite_activa
    w_lim_fin = (L_m * 1000) / limite_fin

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("<div class='envelope-card'>", unsafe_allow_html=True)
        st.markdown("<div class='title-day1'>📅 Día 1: Instantánea (w_inst)</div>", unsafe_allow_html=True)
        st.markdown(f"<span class='val-big'>{w_inst_total:.1f}</span> <span class='val-unit'>mm</span>", unsafe_allow_html=True)
        st.write(f"• Por peso (G): **{w_inst_G:.1f} mm**")
        st.write(f"• Por uso (Q): **{w_inst_Q:.1f} mm**")
        st.markdown("<hr style='margin:10px 0;'>", unsafe_allow_html=True)
        if (w_inst_total / w_lim_inst) <= 1.0:
            st.markdown(f"<span class='badge-ok'>✅ Cumple: ≤ {w_lim_inst:.1f} mm</span>", unsafe_allow_html=True)
        else:
            st.markdown(f"<span class='badge-bad'>❌ No cumple: > {w_lim_inst:.1f} mm</span>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='envelope-card' style='background: linear-gradient(135deg, #fefce8 0%, #fffbeb 100%); border-color: #fde047;'>", unsafe_allow_html=True)
        st.markdown("<div class='title-activa'>🧱 Flecha Activa (w_activa)</div>", unsafe_allow_html=True)
        st.markdown(f"<span class='val-big'>{w_activa:.1f}</span> <span class='val-unit'>mm</span>", unsafe_allow_html=True)
        st.write(f"• Flecha final: **{w_fin_total:.1f} mm**")
        st.write(f"• Menos flecha inicial por G: **-{w_inst_G:.1f} mm**")
        st.markdown("<hr style='margin:10px 0;'>", unsafe_allow_html=True)
        if (w_activa / w_lim_activa) <= 1.0:
            st.markdown(f"<span class='badge-ok' style='color:#854d0e; border-color:#fde047; background:#fef08a;'>✅ Cumple: ≤ {w_lim_activa:.1f} mm</span>", unsafe_allow_html=True)
        else:
            st.markdown(f"<span class='badge-bad'>❌ No cumple: > {w_lim_activa:.1f} mm</span>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col3:
        st.markdown("<div class='envelope-card' style='background: linear-gradient(135deg, #fef2f2 0%, #fff1f2 100%); border-color: #fecaca;'>", unsafe_allow_html=True)
        st.markdown("<div class='title-day10k'>⏳ 30 Años: Flecha Final (w_fin)</div>", unsafe_allow_html=True)
        st.markdown(f"<span class='val-big'>{w_fin_total:.1f}</span> <span class='val-unit'>mm</span>", unsafe_allow_html=True)
        st.write(f"• Día 1: **{w_inst_total:.1f} mm**")
        st.write(f"• Fluencia (Creep): **+{w_creep_total:.1f} mm**")
        st.markdown("<hr style='margin:10px 0;'>", unsafe_allow_html=True)
        if (w_fin_total / w_lim_fin) <= 1.0:
            st.markdown(f"<span class='badge-ok' style='color:#991b1b; border-color:#fca5a5; background:#fecaca;'>✅ Cumple: ≤ {w_lim_fin:.1f} mm</span>", unsafe_allow_html=True)
        else:
            st.markdown(f"<span class='badge-bad'>❌ No cumple: > {w_lim_fin:.1f} mm</span>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.divider()

    st.header("🔍 ¿Cómo ha afectado exactamente el $k_{def}$?")
    st.markdown(f"""
    <div class='expl-box'>
    Has elegido <b>Clase {clase_servicio}</b>, por lo que el coeficiente de deformación en el tiempo es <b>kdef = {kdef:.2f}</b>.<br>
    Fíjate en las pizarras de abajo para entender a qué le afecta este {kdef:.2f} y a qué no.
    </div>
    """, unsafe_allow_html=True)

    colA, colB = st.columns(2)
    with colA:
        st.markdown("### 1. El Peso Propio (G)")
        st.write("El peso de la estructura está **siempre al 100%**. La madera fluye bajo todo su peso.")
        st.markdown(f"""
        <div class='math-box'>
        w_fin,G = w_inst,G · (1 + kdef)<br>
        w_fin,G = {w_inst_G:.2f} · (1 + {kdef:.2f})<br>
        w_fin,G = {w_fin_G:.2f} mm
        </div>
        """, unsafe_allow_html=True)
        st.caption(f"El peso propio ha generado {w_creep_G:.1f} mm de flecha extra con los años.")

    with colB:
        st.markdown("### 2. La Sobrecarga de Uso (Q)")
        st.write("Solo consideramos la parte que vive ahí de forma permanente, es decir el $\psi_2$ (30%).")
        st.markdown(f"""
        <div class='math-box'>
        w_fin,Q = w_inst,Q · (1 + ψ2 · kdef)<br>
        w_fin,Q = {w_inst_Q:.2f} · (1 + {PSI2_VIV:.2f} · {kdef:.2f})<br>
        w_fin,Q = {w_fin_Q:.2f} mm
        </div>
        """, unsafe_allow_html=True)
        st.caption(f"La sobrecarga ha generado solo {w_creep_Q:.1f} mm de flecha extra con los años.")

    st.divider()

    st.header("🧠 Traducción al mundo real (Para no olvidar los conceptos)")
    st.markdown("""
    <div style="display: flex; gap: 15px; flex-wrap: wrap;">
        <div class="story-box" style="flex: 1; background: #f0fdf4; border: 1px solid #bbf7d0;">
            <p class="story-title" style="color: #166534;">📅 1. Instantánea (La Fiesta)</p>
            Imagina que terminas de construir el forjado. Ese mismo día metes todos los muebles e invitas a mucha gente. El suelo cede unos milímetros de golpe. Eso es la <b>Flecha Instantánea</b>.
        </div>
        <div class="story-box" style="flex: 1; background: #fffbeb; border: 1px solid #fde047;">
            <p class="story-title" style="color: #854d0e;">🧱 2. Activa (El Tabique de Cristal)</p>
            El tabique no sufre lo que pasó antes de construirlo. Solo le importa lo que el suelo siga bajando después. Esa deformación “extra” es la <b>Flecha Activa</b>.
        </div>
        <div class="story-box" style="flex: 1; background: #fef2f2; border: 1px solid #fecaca;">
            <p class="story-title" style="color: #991b1b;">⏳ 3. Final (La Jubilación a 30 años)</p>
            La madera es viscoelástica: se va cansando con el tiempo. Aunque no metas ni un kilo nuevo, la viga sigue cediendo lentamente. Eso es la <b>Flecha Final</b>.
        </div>
    </div>
    """, unsafe_allow_html=True)

# =========================================================
# PÁGINA 5: VIBRACIONES
# =========================================================

elif page == "📳 5. Vibraciones":
    st.title("📳 5. Servicio: Vibraciones")
    mostrar_datos_globales(mat, clase_servicio, b_mm, h_mm, L_m, gk, quk, Qpk_kN)

    st.markdown("""
    <div class="orange-box">
    <b>Método simplificado de evaluación del confort.</b><br>
    Esta pestaña usa una aproximación ingenieril útil para estudiar la sensibilidad del forjado a vibraciones.
    Sirve como herramienta de diseño y comparación, pero conviene no presentarla como un desarrollo completo y cerrado del EC5.
    </div>
    """, unsafe_allow_html=True)

    with st.expander("📚 Guía del Maestro: ¿Por qué vibra la madera?", expanded=False):
        st.markdown("""
        Un forjado de madera puede ser muy resistente y no romperse jamás, pero dar sensación de trampolín.
        
        * **La masa que vibra:** para estudiar vibraciones usamos masa real, no coeficientes de seguridad.
        * **Frecuencia propia ($f_1$):** si es baja, el forjado entra en resonancia con el paso humano.
        * **Criterio de rigidez ($w_{1kN}$):** cuánto se hunde el suelo bajo un paso fuerte.
        """)

    st.sidebar.header("Parámetros de Vibración")
    psi_masa = st.sidebar.slider(
        "Participación del uso en masa (ψ)",
        0.0, 0.30, 0.10, 0.05,
        help="Fracción de la sobrecarga de uso que se considera masa fija (muebles)."
    )

    k_rep = st.sidebar.slider(
        "Coef. reparto transversal",
        0.20, 1.00, 0.50, 0.05,
        help="Parte de la carga puntual de 1kN que absorbe la viga considerada."
    )

    usar_masa_manual = st.sidebar.checkbox("Usar masa total manual [kg/m²]", value=False)

    if usar_masa_manual:
        masa_manual = st.sidebar.number_input("Masa total del forjado [kg/m²]", value=120.0, step=5.0)
    else:
        masa_manual = None

    st.sidebar.header("Límites de Confort")
    limite_f1 = st.sidebar.number_input("Frecuencia mínima f1 [Hz]", value=8.0, step=0.5)
    limite_w1kN = st.sidebar.number_input("Hundimiento máximo w_1kN [mm]", value=1.5, step=0.1)

    E_mean = props_mat["E_0_mean"]
    I_y = props_geo["I_y"]

    E_N_m2 = E_mean * 1e6
    I_m4 = I_y * 1e-12
    EI_L = (E_N_m2 * I_m4) / s_m

    Gk_viga_m2 = peso_viga / s_m
    masa_G = (Gk_m2 + Gk_viga_m2) * (1000 / 9.81)
    masa_Q = (Quk_m2 * psi_masa) * (1000 / 9.81)

    if usar_masa_manual:
        m_total = masa_manual
    else:
        m_total = masa_G + masa_Q

    f1 = (math.pi / (2 * L_m**2)) * math.sqrt(EI_L / m_total)

    F_N = 1000.0 * k_rep
    L_mm = L_m * 1000.0
    w_1kN = (F_N * L_mm**3) / (48.0 * E_mean * I_y)

    st.subheader("Resultados de Confort")
    col1, col2 = st.columns(2)

    with col1:
        color_card = "#f0fdf4" if f1 >= limite_f1 else "#fef2f2"
        border_card = "#bbf7d0" if f1 >= limite_f1 else "#fecaca"
        st.markdown(f"<div class='envelope-card' style='background: {color_card}; border-color: {border_card};'>", unsafe_allow_html=True)
        st.markdown("<div class='envelope-title' style='color:#1e293b'>🎵 Frecuencia Propia ($f_1$)</div>", unsafe_allow_html=True)
        st.markdown(f"<span class='val-big'>{f1:.1f}</span> <span class='val-unit'>Hz</span>", unsafe_allow_html=True)
        st.write(f"• Masa actuante: **{m_total:.0f} kg/m²**")
        st.write(f"• Rigidez del forjado: **{EI_L/1e6:.2f} MN·m²/m**")
        if f1 >= limite_f1:
            st.markdown(f"<span class='badge-ok'>✅ FORJADO RÁPIDO (≥ {limite_f1} Hz)</span>", unsafe_allow_html=True)
        else:
            st.markdown(f"<span class='badge-bad'>❌ FORJADO LENTO (< {limite_f1} Hz)</span>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        color_card2 = "#f0fdf4" if w_1kN <= limite_w1kN else "#fef2f2"
        border_card2 = "#bbf7d0" if w_1kN <= limite_w1kN else "#fecaca"
        st.markdown(f"<div class='envelope-card' style='background: {color_card2}; border-color: {border_card2};'>", unsafe_allow_html=True)
        st.markdown("<div class='envelope-title' style='color:#1e293b'>🦶 Rigidez al paso ($w_{1kN}$)</div>", unsafe_allow_html=True)
        st.markdown(f"<span class='val-big'>{w_1kN:.2f}</span> <span class='val-unit'>mm</span>", unsafe_allow_html=True)
        st.write(f"• Carga aplicada: **1.0 kN × {k_rep:.2f}**")
        st.write(f"• Luz de la viga: **{L_m:.2f} m**")
        if w_1kN <= limite_w1kN:
            st.markdown(f"<span class='badge-ok'>✅ SUELO RÍGIDO (≤ {limite_w1kN} mm)</span>", unsafe_allow_html=True)
        else:
            st.markdown(f"<span class='badge-bad'>❌ SUELO BLANDO (> {limite_w1kN} mm)</span>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.divider()

    st.header("🧮 Disección Matemática")
    st.markdown("""
    <div class='expl-box'>
    Este cálculo usa una aproximación simplificada de masa participante y rigidez equivalente por metro de ancho.
    </div>
    """, unsafe_allow_html=True)

    colA, colB = st.columns(2)
    with colA:
        st.markdown("### 1. Cálculo de Masa ($m$)")
        if usar_masa_manual:
            st.markdown(f"""
            <div class='math-box'>
            m_{{total}} = <span class='math-res'>{m_total:.1f} kg/m²</span> (introducida manualmente)
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class='math-box'>
            m_G = (G_k + Peso_{{viga}}) \cdot (1000 / 9.81) <br>
            m_G = ({Gk_m2:.2f} + {Gk_viga_m2:.2f}) \cdot 101.9 = {masa_G:.1f} kg/m²
            <hr style="border-color:#334155; margin:10px 0;">
            m_Q = (Q_k \cdot ψ_{{masa}}) \cdot (1000 / 9.81) <br>
            m_Q = ({Quk_m2:.2f} \cdot {psi_masa:.2f}) \cdot 101.9 = {masa_Q:.1f} kg/m²
            <hr style="border-color:#334155; margin:10px 0;">
            m_{{total}} = <span class='math-res'>{m_total:.1f} kg/m²</span>
            </div>
            """, unsafe_allow_html=True)

    with colB:
        st.markdown("### 2. Frecuencia Propia ($f_1$)")
        st.markdown(f"""
        <div class='math-box'>
        (EI)_L = E_{{mean}} \cdot I_y / s <br>
        (EI)_L = {EI_L/1e6:.2f} \cdot 10⁶ N·m²/m
        <hr style="border-color:#334155; margin:10px 0;">
        f_1 = (π / 2·L²) \cdot √((EI)_L / m) <br>
        f_1 = (3.1416 / {2 * L_m**2:.2f}) \cdot √({EI_L:.0f} / {m_total:.1f}) <br>
        f_1 = <span class='math-res'>{f1:.2f} Hz</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("### 3. Criterio de Rigidez ($w_{1kN}$)")
    st.latex(rf"w_{{1kN}} = \frac{{(1000\ N \cdot k_{{rep}}) \cdot L^3}}{{48 \cdot E_{{mean}} \cdot I_y}} = \frac{{(1000 \cdot {k_rep:.2f}) \cdot {L_mm:.0f}^3}}{{48 \cdot {E_mean} \cdot {I_y:.0f}}} = {w_1kN:.2f}\ \mathrm{{mm}}")

    st.divider()

    st.header("🧠 Traducción al mundo real")
    st.markdown("""
    <div style="display: flex; gap: 15px; flex-wrap: wrap;">
        <div class="story-box" style="flex: 1; background: #faf5ff; border: 1px solid #e9d5ff;">
            <p class="story-title" style="color: #7e22ce;">🎵 ¿Por qué 8 Hz?</p>
            Si el forjado vibra demasiado lento, entra en resonancia con el paso humano y se siente inestable.
        </div>
        <div class="story-box" style="flex: 1; background: #fffbeb; border: 1px solid #fde047;">
            <p class="story-title" style="color: #854d0e;">🐘 El pisotón (1 kN)</p>
            Simulamos una persona dando un paso fuerte en mitad del forjado. Si el hundimiento es grande, la sensación será de suelo blando o trampolín.
        </div>
    </div>
    """, unsafe_allow_html=True)