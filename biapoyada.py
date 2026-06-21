import streamlit as st
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="Análisis de Viga Biapoyada", layout="wide")

st.title("🏗️ Análisis de Viga Biapoyada")
st.markdown("### Calculadora estructural interactiva")

# Sidebar para inputs
st.sidebar.header("⚙️ Configuración de la Viga")

# Propiedades de la viga
st.sidebar.subheader("Geometría")
L = st.sidebar.slider("Longitud de la viga (m)", 1.0, 20.0, 10.0, 0.5)

# Propiedades del material
st.sidebar.subheader("Material")
E = st.sidebar.number_input("Módulo de elasticidad E (GPa)", 1.0, 500.0, 200.0) * 1e9  # Convertir a Pa
I = st.sidebar.number_input("Momento de inercia I (cm⁴)", 1.0, 100000.0, 5000.0) * 1e-8  # Convertir a m⁴

# Tipo de apoyos
st.sidebar.subheader("Apoyos")
apoyo_A = st.sidebar.selectbox("Apoyo A (izquierda)", ["Articulado", "Rodillo", "Empotrado"], index=0)
apoyo_B = st.sidebar.selectbox("Apoyo B (derecha)", ["Articulado", "Rodillo", "Empotrado"], index=1)

# Carga puntual
st.sidebar.subheader("Carga Puntual")
P = st.sidebar.number_input("Magnitud de la carga P (kN)", -1000.0, 1000.0, -50.0, 5.0)
a = st.sidebar.slider("Posición de la carga desde A (m)", 0.1, L-0.1, L/2, 0.1)

# Cálculo de distancias
b = L - a

# Validación de configuración de apoyos
def validar_apoyos(apoyo_A, apoyo_B):
    if apoyo_A == "Empotrado" and apoyo_B == "Empotrado":
        return False, "No se puede analizar una viga con dos empotramientos (estructura hiperestática)"
    if apoyo_A == "Rodillo" and apoyo_B == "Rodillo":
        return False, "No se puede tener dos rodillos (estructura inestable horizontalmente)"
    if apoyo_A == "Empotrado":
        return False, "Este análisis es para vigas biapoyadas (empotrado en A no soportado)"
    return True, ""

valido, mensaje_error = validar_apoyos(apoyo_A, apoyo_B)

if not valido:
    st.error(f"⚠️ {mensaje_error}")
    st.stop()

# Cálculo de reacciones
def calcular_reacciones(P, a, b, L, apoyo_B):
    """
    Calcula las reacciones en los apoyos para una viga biapoyada
    """
    # Para viga biapoyada con apoyo articulado en A y rodillo en B
    R_B = (P * a) / L
    R_A = P - R_B
    
    # Momento en A (solo si es empotrado, pero aquí no aplica)
    M_A = 0
    
    return R_A, R_B, M_A

R_A, R_B, M_A = calcular_reacciones(P, a, b, L, apoyo_B)

# Mostrar resultados de reacciones
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Reacción en A (R_A)", f"{R_A:.2f} kN", 
              delta="↑" if R_A > 0 else "↓")

with col2:
    st.metric("Reacción en B (R_B)", f"{R_B:.2f} kN",
              delta="↑" if R_B > 0 else "↓")

with col3:
    st.metric("Momento en A", f"{M_A:.2f} kN·m")

# Cálculo de diagramas
def calcular_cortante(x, P, a, R_A):
    """Calcula la fuerza cortante en la posición x"""
    if x < a:
        return R_A
    else:
        return R_A + P

def calcular_momento(x, P, a, R_A):
    """Calcula el momento flector en la posición x"""
    if x < a:
        return R_A * x
    else:
        return R_A * x + P * (x - a)

def calcular_deflexion(x, P, a, L, E, I, R_A):
    """
    Calcula la deflexión en la posición x
    Usando el método de superposición
    """
    b = L - a
    
    # Deflexión debida a la carga puntual
    if x < a:
        deflexion = (P * b * x) / (6 * L * E * I) * (L**2 - b**2 - x**2)
    else:
        deflexion = (P * a * (L - x)) / (6 * L * E * I) * (2*L*x - x**2 - a**2)
    
    return deflexion * 1000  # Convertir a mm

# Generar puntos para graficar
n_points = 500
x = np.linspace(0, L, n_points)

# Calcular valores
cortante = np.array([calcular_cortante(xi, P, a, R_A) for xi in x])
momento = np.array([calcular_momento(xi, P, a, R_A) for xi in x])
deflexion = np.array([calcular_deflexion(xi, P, a, L, E, I, R_A) for xi in x])

# Encontrar valores máximos
max_cortante = np.max(np.abs(cortante))
max_momento = np.max(np.abs(momento))
max_deflexion = np.max(np.abs(deflexion))
pos_max_deflexion = x[np.argmax(np.abs(deflexion))]

# Crear gráficos
fig = make_subplots(
    rows=4, cols=1,
    subplot_titles=('Esquema de la Viga', 
                    'Diagrama de Cortante (V)', 
                    'Diagrama de Momento Flector (M)',
                    'Diagrama de Deflexión (δ)'),
    vertical_spacing=0.08,
    row_heights=[0.2, 0.27, 0.27, 0.27]
)

# 1. Esquema de la viga
fig.add_trace(
    go.Scatter(x=[0, L], y=[0, 0], mode='lines', 
               line=dict(color='black', width=6),
               name='Viga',
               showlegend=False),
    row=1, col=1
)

# Apoyo A
apoyo_A_symbol = '▲' if apoyo_A == "Articulado" else '○'
fig.add_trace(
    go.Scatter(x=[0], y=[0], mode='markers+text',
               marker=dict(size=20, color='blue', symbol='triangle-up'),
               text=[apoyo_A_symbol], textposition='bottom center',
               textfont=dict(size=20),
               name=f'Apoyo A: {apoyo_A}',
               showlegend=False),
    row=1, col=1
)

# Apoyo B
apoyo_B_symbol = '▲' if apoyo_B == "Articulado" else '○'
fig.add_trace(
    go.Scatter(x=[L], y=[0], mode='markers+text',
               marker=dict(size=20, color='blue', symbol='triangle-up' if apoyo_B == "Articulado" else 'circle'),
               text=[apoyo_B_symbol], textposition='bottom center',
               textfont=dict(size=20),
               name=f'Apoyo B: {apoyo_B}',
               showlegend=False),
    row=1, col=1
)

# Carga puntual
fig.add_trace(
    go.Scatter(x=[a, a], y=[0.5, 0], mode='lines+markers',
               line=dict(color='red', width=3),
               marker=dict(size=10, symbol='arrow-down'),
               name=f'P = {P} kN',
               showlegend=False),
    row=1, col=1
)

fig.add_annotation(
    x=a, y=0.7,
    text=f"P = {P} kN",
    showarrow=False,
    font=dict(size=12, color='red'),
    row=1, col=1
)

# Reacciones
fig.add_trace(
    go.Scatter(x=[0, 0], y=[-0.5, 0], mode='lines+markers',
               line=dict(color='green', width=3),
               marker=dict(size=10, symbol='arrow-up'),
               name=f'R_A = {R_A:.2f} kN',
               showlegend=False),
    row=1, col=1
)

fig.add_trace(
    go.Scatter(x=[L, L], y=[-0.5, 0], mode='lines+markers',
               line=dict(color='green', width=3),
               marker=dict(size=10, symbol='arrow-up'),
               name=f'R_B = {R_B:.2f} kN',
               showlegend=False),
    row=1, col=1
)

# 2. Diagrama de cortante
fig.add_trace(
    go.Scatter(x=x, y=cortante, mode='lines',
               line=dict(color='blue', width=2),
               fill='tozeroy',
               name='Cortante',
               showlegend=False),
    row=2, col=1
)

fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5, row=2, col=1)
fig.add_vline(x=a, line_dash="dash", line_color="red", opacity=0.3, row=2, col=1)

# 3. Diagrama de momento
fig.add_trace(
    go.Scatter(x=x, y=momento, mode='lines',
               line=dict(color='orange', width=2),
               fill='tozeroy',
               name='Momento',
               showlegend=False),
    row=3, col=1
)

fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5, row=3, col=1)
fig.add_vline(x=a, line_dash="dash", line_color="red", opacity=0.3, row=3, col=1)

# 4. Diagrama de deflexión
fig.add_trace(
    go.Scatter(x=x, y=deflexion, mode='lines',
               line=dict(color='green', width=2),
               fill='tozeroy',
               name='Deflexión',
               showlegend=False),
    row=4, col=1
)

fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5, row=4, col=1)
fig.add_vline(x=a, line_dash="dash", line_color="red", opacity=0.3, row=4, col=1)

# Configurar ejes
fig.update_xaxes(title_text="Posición (m)", row=4, col=1)
fig.update_yaxes(title_text="", row=1, col=1)
fig.update_yaxes(title_text="V (kN)", row=2, col=1)
fig.update_yaxes(title_text="M (kN·m)", row=3, col=1)
fig.update_yaxes(title_text="δ (mm)", row=4, col=1)

fig.update_layout(height=1200, showlegend=False)

st.plotly_chart(fig, use_container_width=True)

# Tabla de resultados importantes
st.subheader("📊 Resultados Importantes")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Esfuerzos Máximos")
    results_df = {
        "Parámetro": [
            "Cortante máximo",
            "Momento máximo",
            "Posición momento máximo"
        ],
        "Valor": [
            f"{max_cortante:.2f} kN",
            f"{max_momento:.2f} kN·m",
            f"{a:.2f} m"
        ]
    }
    st.table(results_df)

with col2:
    st.markdown("#### Deformaciones")
    deform_df = {
        "Parámetro": [
            "Deflexión máxima",
            "Posición deflexión máxima",
            "Deflexión en centro"
        ],
        "Valor": [
            f"{max_deflexion:.3f} mm",
            f"{pos_max_deflexion:.2f} m",
            f"{deflexion[n_points//2]:.3f} mm"
        ]
    }
    st.table(deform_df)

# Fórmulas utilizadas
with st.expander("📐 Ver fórmulas utilizadas"):
    st.markdown("""
    ### Reacciones en los apoyos:
    - $R_B = \\frac{P \cdot a}{L}$
    - $R_A = P - R_B$
    
    ### Cortante V(x):
    - Para $x < a$: $V(x) = R_A$
    - Para $x \geq a$: $V(x) = R_A + P$
    
    ### Momento M(x):
    - Para $x < a$: $M(x) = R_A \cdot x$
    - Para $x \geq a$: $M(x) = R_A \cdot x + P \cdot (x - a)$
    
    ### Deflexión δ(x):
    - Para $x < a$: $\delta(x) = \\frac{P \cdot b \cdot x}{6 \cdot L \cdot E \cdot I} (L^2 - b^2 - x^2)$
    - Para $x \geq a$: $\delta(x) = \\frac{P \cdot a \cdot (L-x)}{6 \cdot L \cdot E \cdot I} (2Lx - x^2 - a^2)$
    
    Donde:
    - L = Longitud de la viga
    - a = Distancia de A a la carga
    - b = Distancia de la carga a B
    - E = Módulo de elasticidad
    - I = Momento de inercia
    """)

# Información adicional
st.sidebar.markdown("---")
st.sidebar.info("""
**ℹ️ Información:**
- Los valores positivos de cortante indican corte hacia arriba
- Los valores positivos de momento indican tracción en fibra inferior
- Las deflexiones negativas indican desplazamiento hacia abajo
- Esta es la versión básica. ¡Próximamente más funciones!
""")

st.sidebar.markdown("---")
st.sidebar.markdown("Desarrollado con ❤️ usando Streamlit")
