import streamlit as st
import numpy as np
import plotly.graph_objects as go
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit
from qiskit.quantum_info import Operator

from ewl_protocol import strategy_C, strategy_D, strategy_Q, build_ewl_circuit
from fast_simulator import ewl_payoff_fast, su2_unitary_vec

# Set Page Config
st.set_page_config(
    page_title="Quantum Prisoner's Dilemma",
    page_icon="⚛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling (Cyberpunk Theme)
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
        color: #ffffff;
    }
    .stSidebar {
        background-color: #161b22;
    }
    h1, h2, h3 {
        color: #00ffcc !important;
        font-family: 'Courier New', Courier, monospace;
    }
    .stSlider > div > div > div > div {
        background-color: #00ffcc;
    }
    </style>
    """, unsafe_allow_html=True)

# Sidebar - Control Panel
st.sidebar.title("🎮 Control Panel")
st.sidebar.markdown("---")

st.sidebar.subheader("Alice's Strategy (Custom)")
alice_theta = st.sidebar.slider("Alice Theta (θ)", 0.0, 2*np.pi, 0.0, step=0.1)
alice_phi = st.sidebar.slider("Alice Phi (φ)", 0.0, np.pi, 0.0, step=0.1)

st.sidebar.markdown("---")
st.sidebar.subheader("Bob's Strategy")
bob_choice = st.sidebar.selectbox("Choose Bob's Strategy", ["Cooperate (C)", "Defect (D)", "Quantum (Q)", "Custom SU(2)"])

if bob_choice == "Custom SU(2)":
    bob_theta = st.sidebar.slider("Bob Theta (θ)", 0.0, 2*np.pi, np.pi, step=0.1)
    bob_phi = st.sidebar.slider("Bob Phi (φ)", 0.0, np.pi, 0.0, step=0.1)
    u_B = su2_unitary_vec(bob_theta, bob_phi)
elif bob_choice == "Cooperate (C)":
    u_B = strategy_C
elif bob_choice == "Defect (D)":
    u_B = strategy_D
else:
    u_B = strategy_Q

st.sidebar.markdown("---")
st.sidebar.subheader("Protocol Parameters")
gamma = st.sidebar.slider("Entanglement (γ)", 0.0, np.pi/2, np.pi/2, step=0.01)

# Logic Calculation
u_A_current = su2_unitary_vec(alice_theta, alice_phi)
# Single point simulation
pA_single, pB_single, probs_single = ewl_payoff_fast(u_A_current.reshape(1, 1, 2, 2), u_B, gamma=gamma)
pA_val = pA_single[0,0]
pB_val = pB_single[0,0]
probs_val = probs_single[0,0]

# High-Resolution Sweep for 3D Surface
res = 50
thetas = np.linspace(0, 2*np.pi, res)
phis = np.linspace(0, np.pi, res)
T, P = np.meshgrid(thetas, phis)
U_A_grid = su2_unitary_vec(T, P)
landscape_A, landscape_B, _ = ewl_payoff_fast(U_A_grid, u_B, gamma=gamma)

# Main Dashboard Layout
st.title("⚛️ Quantum Prisoner's Dilemma")
st.markdown("Interactive visualization of the EWL Protocol.")

# Top Row: 3D Landscapes (Tabs)
tab1, tab2 = st.tabs(["📊 Alice's Payoff Landscape", "📊 Bob's Payoff Landscape"])

with tab1:
    fig_3d_A = go.Figure(data=[go.Surface(
        z=landscape_A, x=thetas, y=phis, 
        colorscale='Viridis', 
        colorbar=dict(title="Alice Payoff")
    )])
    fig_3d_A.add_trace(go.Scatter3d(
        x=[alice_theta], y=[alice_phi], z=[pA_val],
        mode='markers',
        marker=dict(size=10, color='red', symbol='cross'),
        name="Current Strategy"
    ))
    fig_3d_A.update_layout(scene=dict(xaxis_title='Theta', yaxis_title='Phi', zaxis_title='Payoff'), margin=dict(l=0, r=0, b=0, t=0), height=600)
    st.plotly_chart(fig_3d_A, use_container_width=True)

with tab2:
    fig_3d_B = go.Figure(data=[go.Surface(
        z=landscape_B, x=thetas, y=phis, 
        colorscale='Hot', 
        colorbar=dict(title="Bob Payoff")
    )])
    fig_3d_B.add_trace(go.Scatter3d(
        x=[alice_theta], y=[alice_phi], z=[pB_val],
        mode='markers',
        marker=dict(size=10, color='blue', symbol='cross'),
        name="Current Strategy"
    ))
    fig_3d_B.update_layout(scene=dict(xaxis_title='Theta', yaxis_title='Phi', zaxis_title='Payoff'), margin=dict(l=0, r=0, b=0, t=0), height=600)
    st.plotly_chart(fig_3d_B, use_container_width=True)

# Bottom Row: Columns
col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 Real-time Results")
    # Payoff Bar Chart
    fig_payoff = go.Figure(go.Bar(
        x=["Alice", "Bob"],
        y=[pA_val, pB_val],
        marker_color=['#00ffcc', '#ff3366']
    ))
    fig_payoff.update_layout(title="Expected Payoffs", yaxis=dict(range=[0, 5]))
    st.plotly_chart(fig_payoff, use_container_width=True)
    
    # Probabilities
    labels = ["|00>", "|01>", "|10>", "|11>"]
    fig_probs = go.Figure(go.Bar(
        x=labels,
        y=probs_val,
        marker_color='#9933ff'
    ))
    fig_probs.update_layout(title="Outcome Probabilities", yaxis=dict(range=[0, 1]))
    st.plotly_chart(fig_probs, use_container_width=True)

with col2:
    st.subheader("🔌 Quantum Circuit")
    qc = build_ewl_circuit(u_A_current, u_B, gamma=gamma)
    fig_circ = qc.draw('mpl', style='iqp-dark')
    st.pyplot(fig_circ)
    
    st.info("""
    **Legend:**
    - **J**: Entangling gate
    - **U_A**: Alice's strategy
    - **U_B**: Bob's strategy
    - **J_dag**: Disentangling gate
    - **Measurement**: Projects the quantum state into classical bits.
    """)

st.sidebar.markdown("---")
st.sidebar.write("Developed for QuantumMini")
