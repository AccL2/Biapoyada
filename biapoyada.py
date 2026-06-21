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
apoyo_A = st.sidebar.selectbox("Apoyo A (izquierda)", ["Articulado", "Rodillo"], index=0)
apoyo_B = st.sidebar.selectbox("Apoyo B (derecha)", ["Articulado", "Rodillo"], index=1)

# Carga puntual
st.sidebar.subheader("Carga Puntual")
P = st.sidebar.number_input("Magnitud de la carga P (kN) - Positiva hacia abajo", 0.1, 1000.0, 50.0, 5.0)
a = st.sidebar.slider("Posición de la carga desde A (m)", 0.1, L-0.1, L/2, 0.1)

# Cálculo de distancias
b = L - a

# Validación de configuración de apoyos
def validar_apoyos(apoyo_A, apoyo_B):
    if apoyo_A == "Rodillo" and apoyo_B == "Rodillo":
        return False, "⚠️ No se puede tener dos rodillos (estructura inestable horizontalmente)"
    return True, ""

valido, mensaje_error = validar_apoyos(apoyo_A, apoyo_B)

if not valido:
    st.error(mensaje_error)
    st.stop()

# Cálculo de reacciones (CORREGIDO)
def calcular_reacciones(P, a, b, L):
    """
    Calcula las reacciones en los apoyos para una viga biapoyada.
    Convención: P positiva hacia abajo, reacciones positivas hacia arriba
    """
    # Equilibrio de momentos respecto a A: R_B * L = P * a
    R_B = (P * a) / L
    
    # Equilibrio de fuerzas verticales: R_A + R_B = P
    R_A = P - R_B
    
    return R_A, R_B

R_A, R_B = calcular_reacciones(P, a, b, L)

# Mostrar resultados de reacciones
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Reacción en A (R_A)", f"{R_A:.2f} kN", 
              delta="↑ Hacia arriba" if R_A > 0 else "↓ Hacia abajo")

with col2:
    st.metric("Reacción en B (R_B)", f"{R_B:.2f} kN",
              delta="↑ Hacia arriba" if R_B > 0 else "↓ Hacia abajo")

with col3:
    verificacion = R_A + R_B - P
    st.metric("Verificación ΣFy", f"{verificacion:.4f} kN",
              delta="✓ OK" if abs(verificacion) < 0.001 else "✗ ERROR")

# Cálculo de diagramas (CORREGIDO)
def calcular_cortante(x, P, a, R_A):
    """
    Calcula la fuerza cortante en la posición x.
    Convención: Positivo cuando produce rotación horaria en el elemento
    """
    if x < a:
        return R_A  # Antes de la carga
    else:
        return R_A - P  # Después de la carga

def calcular_momento(x, P, a, R_A):
    """
    Calcula el momento flector en la posición x.
    Convención: Positivo cuando produce tracción en fibra inferior
    """
    if x < a:
        return R_A * x  # Antes de la carga
    else:
        return R_A * x - P * (x - a)  # Después de la carga

def calcular_deflexion(x, P, a, L, E, I):
    """
    Calcula la deflexión en la posición x.
    Convención: Positiva hacia abajo
    Fórmulas de viga biapoyada con carga puntual
    """
    b = L - a
    
    if x < a:
        # Zona entre apoyo A y la carga
        deflexion = (P * b * x) / (6 * L * E * I) * (L**2 - b**2 - x**2)
    else:
        # Zona entre la carga y apoyo B
        deflexion = (P * a * (L - x)) / (6 * L * E * I) * (2*L*x - x**2 - a**2)
    
    return deflexion * 1000  # Convertir a mm (positiva hacia abajo)

# Generar puntos para graficar
n_points = 500
x = np.linspace(0, L, n_points)

# Calcular valores
cortante = np.array([calcular_cortante(xi, P, a, R_A) for xi in x])
momento = np.array([calcular_momento(xi, P, a, R_A) for xi in x])
deflexion = np.array([calcular_deflexion(xi, P, a, L, E, I) for xi in x])

# Encontrar valores importantes
max_cortante_pos = np.max(cortante)
max_cortante_neg = np.min(cortante)
max_momento = np.max(momento)
pos_max_momento = x[np.argmax(momento)]
max_deflexion = np.max(deflexion)
pos_max_deflexion = x[np.argmax(deflexion)]

# Crear gráficos
fig = make_subplots(
    rows=4, cols=1,
    subplot_titles=('Esquema de la Viga', 
                    'Diagrama de Fuerza Cortante (V)', 
                    'Diagrama de Momento Flector (M)',
                    'Diagrama de Deflexión (δ)'),
    vertical_spacing=0.08,
    row_heights=[0.2, 0.27, 0.27, 0.27]
)

# 1. ESQUEMA DE LA VIGA
# Viga
fig.add_trace(
    go.Scatter(x=[0, L], y=[0, 0], mode='lines', 
               line=dict(color='black', width=8),
               name='Viga',
               showlegend=False),
    row=1, col=1
)

# Apoyo A
if apoyo_A == "Articulado":
    fig.add_trace(
        go.Scatter(x=[0], y=[0], mode='markers',
                   marker=dict(size=25, color='blue', symbol='triangle-up', line=dict(width=2, color='darkblue')),
                   name='Apoyo A',
                   showlegend=False),
        row=1, col=1
    )
else:  # Rodillo
    fig.add_trace(
        go.Scatter(x=[0], y=[0], mode='markers',
                   marker=dict(size=20, color='lightblue', symbol='circle', line=dict(width=2, color='blue')),
                   name='Apoyo A',
                   showlegend=False),
        row=1, col=1
    )

# Apoyo B
if apoyo_B == "Articulado":
    fig.add_trace(
        go.Scatter(x=[L], y=[0], mode='markers',
                   marker=dict(size=25, color='blue', symbol='triangle-up', line=dict(width=2, color='darkblue')),
                   name='Apoyo B',
                   showlegend=False),
        row=1, col=1
    )
else:  # Rodillo
    fig.add_trace(
        go.Scatter(x=[L], y=[0], mode='markers',
                   marker=dict(size=20, color='lightblue', symbol='circle', line=dict(width=2, color='blue')),
                   name='Apoyo B',
                   showlegend=False),
        row=1, col=1
    )

# Carga puntual P (hacia abajo)
fig.add_trace(
    go.Scatter(x=[a, a], y=[0.8, 0.05], mode='lines',
               line=dict(color='red', width=4),
               showlegend=False),
    row=1, col=1
)
# Flecha de la carga
fig.add_trace(
    go.Scatter(x=[a], y=[0.05], mode='markers',
               marker=dict(size=15, color='red', symbol='triangle-down'),
               showlegend=False),
    row=1, col=1
)

fig.add_annotation(
    x=a, y=1.0,
    text=f"P = {P} kN",
    showarrow=False,
    font=dict(size=14, color='red', family='Arial Black'),
    row=1, col=1
)

# Reacción en A (hacia arriba)
fig.add_trace(
    go.Scatter(x=[0, 0], y=[-0.6, -0.05], mode='lines',
               line=dict(color='green', width=4),
               showlegend=False),
    row=1, col=1
)
fig.add_trace(
    go.Scatter(x=[0], y=[-0.05], mode='markers',
               marker=dict(size=15, color='green', symbol='triangle-up'),
               showlegend=False),
    row=1, col=1
)
fig.add_annotation(
    x=0, y=-0.8,
    text=f"R_A = {R_A:.2f} kN",
    showarrow=False,
    font=dict(size=12, color='green'),
    row=1, col=1
)

# Reacción en B (hacia arriba)
fig.add_trace(
    go.Scatter(x=[L, L], y=[-0.6, -0.05], mode='lines',
               line=dict(color='green', width=4),
               showlegend=False),
    row=1, col=1
)
fig.add_trace(
    go.Scatter(x=[L], y=[-0.05], mode='markers',
               marker=dict(size=15, color='green', symbol='triangle-up'),
               showlegend=False),
    row=1, col=1
)
fig.add_annotation(
    x=L, y=-0.8,
    text=f"R_B = {R_B:.2f} kN",
    showarrow=False,
    font=dict(size=12, color='green'),
    row=1, col=1
)

# Dimensiones
fig.add_annotation(
    x=a/2, y=-1.2,
    text=f"a = {a:.2f} m",
    showarrow=False,
    font=dict(size=11, color='black'),
    row=1, col=1
)
fig.add_annotation(
    x=a + b/2, y=-1.2,
    text=f"b = {b:.2f} m",
    showarrow=False,
    font=dict(size=11, color='black'),
    row=1, col=1
)

# 2. DIAGRAMA DE CORTANTE
# Rellenar áreas positivas y negativas con colores diferentes
x_antes = x[x < a]
x_despues = x[x >= a]
V_antes = cortante[x < a]
V_despues = cortante[x >= a]

# Área positiva (antes de la carga)
if len(x_antes) > 0:
    fig.add_trace(
        go.Scatter(x=x_antes, y=V_antes, mode='lines',
                   line=dict(color='blue', width=0),
                   fill='tozeroy',
                   fillcolor='rgba(0, 0, 255, 0.3)',
                   name='V positivo',
                   showlegend=False),
        row=2, col=1
    )

# Área negativa (después de la carga)
if len(x_despues) > 0:
    fig.add_trace(
        go.Scatter(x=x_despues, y=V_despues, mode='lines',
                   line=dict(color='red', width=0),
                   fill='tozeroy',
                   fillcolor='rgba(255, 0, 0, 0.3)',
                   name='V negativo',
                   showlegend=False),
        row=2, col=1
    )

# Línea del diagrama
fig.add_trace(
    go.Scatter(x=x, y=cortante, mode='lines',
               line=dict(color='darkblue', width=3),
               name='Cortante',
               showlegend=False),
    row=2, col=1
)

fig.add_hline(y=0, line_dash="dash", line_color="black", opacity=0.5, row=2, col=1)
fig.add_vline(x=a, line_dash="dot", line_color="red", opacity=0.5, row=2, col=1)

# Anotaciones de valores
fig.add_annotation(x=a/2, y=R_A, text=f"{R_A:.2f} kN",
                   showarrow=False, font=dict(size=10, color='blue'), row=2, col=1)
fig.add_annotation(x=a + b/2, y=R_A - P, text=f"{R_A - P:.2f} kN",
                   showarrow=False, font=dict(size=10, color='red'), row=2, col=1)

# 3. DIAGRAMA DE MOMENTO
# El momento positivo se rellena hacia arriba
fig.add_trace(
    go.Scatter(x=x, y=momento, mode='lines',
               line=dict(color='orange', width=3),
               fill='tozeroy',
               fillcolor='rgba(255, 165, 0, 0.3)',
               name='Momento',
               showlegend=False),
    row=3, col=1
)

fig.add_hline(y=0, line_dash="dash", line_color="black", opacity=0.5, row=3, col=1)
fig.add_vline(x=a, line_dash="dot", line_color="red", opacity=0.5, row=3, col=1)

# Momento máximo
fig.add_annotation(x=pos_max_momento, y=max_momento, 
                   text=f"M_máx = {max_momento:.2f} kN·m",
                   showarrow=True, arrowhead=2, arrowcolor='orange',
                   font=dict(size=11, color='orange'), row=3, col=1)

# 4. DIAGRAMA DE DEFLEXIÓN
# Invertimos el eje Y para que positivo sea hacia abajo
fig.add_trace(
    go.Scatter(x=x, y=-deflexion, mode='lines',  # Negativo para invertir visual
               line=dict(color='green', width=3),
               fill='tozeroy',
               fillcolor='rgba(0, 128, 0, 0.2)',
               name='Deflexión',
               showlegend=False),
    row=4, col=1
)

fig.add_hline(y=0, line_dash="dash", line_color="black", opacity=0.5, row=4, col=1)
fig.add_vline(x=a, line_dash="dot", line_color="red", opacity=0.5, row=4, col=1)

# Deflexión máxima
fig.add_annotation(x=pos_max_deflexion, y=-max_deflexion,
                   text=f"δ_máx = {max_deflexion:.3f} mm",
                   showarrow=True, arrowhead=2, arrowcolor='green',
                   font=dict(size=11, color='green'), row=4, col=1)

# Configurar ejes
fig.update_xaxes(title_text="Posición (m)", row=4, col=1, gridcolor='lightgray')
fig.update_yaxes(title_text="", row=1, col=1)
fig.update_yaxes(title_text="V (kN)", row=2, col=1, gridcolor='lightgray', zeroline=True, zerolinewidth=2)
fig.update_yaxes(title_text="M (kN·m)", row=3, col=1, gridcolor='lightgray', zeroline=True, zerolinewidth=2)
fig.update_yaxes(title_text="δ (mm) ↓", row=4, col=1, gridcolor='lightgray', zeroline=True, zerolinewidth=2)

# Invertir eje Y de deflexión para mostrar positivo hacia abajo
fig.update_yaxes(autorange="reversed", row=4, col=1)

fig.update_layout(height=1400, showlegend=False, plot_bgcolor='white')

st.plotly_chart(fig, use_container_width=True)

# Tabla de resultados importantes
st.subheader("📊 Resultados Importantes")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Esfuerzos Internos")
    results_df = {
        "Parámetro": [
            "Cortante máximo (+)",
            "Cortante máximo (-)",
            "Momento máximo",
            "Posición momento máximo"
        ],
        "Valor": [
            f"{max_cortante_pos:.2f} kN",
            f"{max_cortante_neg:.2f} kN",
            f"{max_momento:.2f} kN·m",
            f"{pos_max_momento:.2f} m"
        ]
    }
    st.table(results_df)

with col2:
    st.markdown("#### Deformaciones")
    deform_df = {
        "Parámetro": [
            "Deflexión máxima",
            "Posición deflexión máxima",
            "Deflexión en centro (L/2)",
            "Relación L/δ"
        ],
        "Valor": [
            f"{max_deflexion:.3f} mm",
            f"{pos_max_deflexion:.2f} m",
            f"{deflexion[n_points//2]:.3f} mm",
            f"L/{int(L*1000/max_deflexion)}" if max_deflexion > 0 else "∞"
        ]
    }
    st.table(deform_df)

# Verificaciones
st.subheader("✅ Verificaciones")
col1, col2, col3 = st.columns(3)

with col1:
    equilibrio_fuerzas = abs(R_A + R_B - P)
    if equilibrio_fuerzas < 0.001:
        st.success(f"✓ Equilibrio de fuerzas: {equilibrio_fuerzas:.6f} kN")
    else:
        st.error(f"✗ Equilibrio de fuerzas: {equilibrio_fuerzas:.6f} kN")

with col2:
    equilibrio_momentos = abs(R_B * L - P * a)
    if equilibrio_momentos < 0.001:
        st.success(f"✓ Equilibrio de momentos: {equilibrio_momentos:.6f} kN·m")
    else:
        st.error(f"✗ Equilibrio de momentos: {equilibrio_momentos:.6f} kN·m")

with col3:
    # Verificar que deflexiones en apoyos son cero
    deflexion_apoyo_A = abs(deflexion[0])
    deflexion_apoyo_B = abs(deflexion[-1])
    if deflexion_apoyo_A < 0.001 and deflexion_apoyo_B < 0.001:
        st.success(f"✓ Deflexión en apoyos ≈ 0")
    else:
        st.warning(f"⚠ Deflexión en apoyos: A={deflexion_apoyo_A:.4f}, B={deflexion_apoyo_B:.4f}")

# Fórmulas utilizadas
with st.expander("📐 Ver fórmulas y convenciones de signos"):
    st.markdown("""
    ### 📏 Convenciones de Signos (Criterio Estándar):
    
    #### Cargas:
    - **Positivas**: Hacia abajo ⬇
    - **Negativas**: Hacia arriba ⬆
    
    #### Reacciones:
    - **Positivas**: Hacia arriba ⬆
    - **Negativas**: Hacia abajo ⬇
    
    #### Fuerza Cortante (V):
    - **Positiva**: Cuando la resultante a la izquierda del corte apunta hacia arriba
    - **Negativa**: Cuando la resultante a la izquierda del corte apunta hacia abajo
    
    #### Momento Flector (M):
    - **Positivo**: Produce tracción en la fibra inferior (sonrisa ⌣)
    - **Negativo**: Produce tracción en la fibra superior (ceño ⌢)
    
    #### Deflexión (δ):
    - **Positiva**: Hacia abajo ⬇
    - **Negativa**: Hacia arriba ⬆
    
    ---
    
    ### 🧮 Fórmulas de Cálculo:
    
    #### Reacciones en los apoyos:
    - $R_B = \\frac{P \cdot a}{L}$
    - $R_A = P - R_B = \\frac{P \cdot b}{L}$
    
    #### Fuerza Cortante V(x):
    - Para $0 \leq x < a$: $V(x) = R_A = \\frac{P \cdot b}{L}$
    - Para $a \leq x \leq L$: $V(x) = R_A - P = -\\frac{P \cdot a}{L}$
    
    #### Momento Flector M(x):
    - Para $0 \leq x < a$: $M(x) = R_A \cdot x = \\frac{P \cdot b \cdot x}{L}$
    - Para $a \leq x \leq L$: $M(x) = R_A \cdot x - P(x-a) = \\frac{P \cdot b \cdot x}{L} - P(x-a)$
    - **Momento máximo** en $x = a$: $M_{máx} = \\frac{P \cdot a \cdot b}{L}$
    
    #### Deflexión δ(x):
    - Para $0 \leq x < a$: 
      $$\delta(x) = \\frac{P \cdot b \cdot x}{6 \cdot L \cdot E \cdot I} (L^2 - b^2 - x^2)$$
    
    - Para $a \leq x \leq L$: 
      $$\delta(x) = \\frac{P \cdot a \cdot (L-x)}{6 \cdot L \cdot E \cdot I} (2Lx - x^2 - a^2)$$
    
    - **Deflexión máxima** (cuando $a < b$, ocurre en): 
      $$x_{máx} = \\sqrt{\\frac{L^2 - b^2}{3}}$$
    
    ---
    
    ### 📊 Donde:
    - $L$ = Longitud total de la viga
    - $a$ = Distancia del apoyo A a la carga P
    - $b$ = Distancia de la carga P al apoyo B (b = L - a)
    - $P$ = Magnitud de la carga puntual
    - $E$ = Módulo de elasticidad del material
    - $I$ = Momento de inercia de la sección transversal
    """)

# Información adicional
st.sidebar.markdown("---")
st.sidebar.info("""
**ℹ️ Convenciones:**

**Cargas (P):**
- ✅ Positivas → hacia ABAJO ⬇

**Reacciones (R):**
- ✅ Positivas → hacia ARRIBA ⬆

**Cortante (V):**
- ✅ Positivo → sube del lado izquierdo
- ❌ Negativo → baja del lado izquierdo

**Momento (M):**
- ✅ Positivo → tracción abajo ⌣
- ❌ Negativo → tracción arriba ⌢

**Deflexión (δ):**
- ✅ Positiva → hacia ABAJO ⬇
- ❌ Negativa → hacia ARRIBA ⬆
""")

st.sidebar.markdown("---")
st.sidebar.success("✨ Versión 2.0 - Corregida")
st.sidebar.markdown("Desarrollado con ❤️ usando Streamlit")
