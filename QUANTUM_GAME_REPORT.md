# Technical Report: Quantum Prisoner's Dilemma (EWL Protocol)

## 1. Project Overview
This project implements the **Eisert-Wilkens-Lewenstein (EWL) Protocol**, a framework that extends classical game theory into the quantum domain. It specifically solves the "Prisoner's Dilemma" by allowing players to utilize quantum entanglement and superposition, leading to outcomes that are impossible in classical physics.

## 2. Theoretical Core: The EWL Protocol
In the classical Prisoner's Dilemma, the only Nash Equilibrium is (Defect, Defect), leading to a sub-optimal payoff of (1, 1). The EWL Protocol introduces a quantum circuit that operates as follows:

1.  **Initial State:** Two qubits are prepared in the $|00\rangle$ state (Mutual Cooperation).
2.  **Entanglement ($J$):** A global entangling operator $J = \exp(i \frac{\gamma}{2} X \otimes X)$ is applied. This creates a link between the players' qubits.
3.  **Strategies ($U_A, U_B$):** Alice and Bob apply independent unitary transformations (strategies).
    *   **C (Cooperate):** Identity matrix $I$.
    *   **D (Defect):** A bit-flip operation (equivalent to Pauli-X with phase).
    *   **Q (Quantum):** A unique quantum move (Pauli-Z rotation) that has no classical counterpart.
4.  **Disentanglement ($J^\dagger$):** The inverse entangling operator is applied to interfere the states.
5.  **Measurement:** The qubits are measured in the computational basis to determine the payoffs based on the original PD matrix.

**Key Finding:** When both players play the Quantum strategy ($Q$), they reach a new Nash Equilibrium that yields a payoff of (3, 3), effectively "escaping" the classical dilemma through quantum interference.

## 3. Architecture & Software Design

### A. The "NumPy Speedrun" (High-Performance Backend)
To make the 3D visualizations smooth, I implemented a **vectorized NumPy simulator** (`fast_simulator.py`). 
*   **Vectorization:** Instead of running a loop for each point on the grid (which is slow), I used `np.einsum` to calculate 2,500+ strategy points simultaneously using tensor products.
*   **Result:** The UI updates the 3D surface instantly, allowing for real-time exploration of the strategy space.

### B. Visualization Layers
1.  **Streamlit Dashboard (`app.py`):** 
    *   **3D Landscapes:** Interactive Plotly surfaces mapping Alice and Bob's payoffs across the full SU(2) strategy space ($\theta, \phi$).
    *   **Live Circuits:** Real-time rendering of the Qiskit circuit using the Matplotlib backend.
2.  **Terminal UI (`tui_game.py`):** 
    *   A "cyberpunk" style console dashboard using the `rich` library. It provides high-signal feedback (ASCII bar charts, colored heatmaps) for environments without a web browser.

### C. Noise & Decoherence
The project includes a `noise_analysis.py` module which uses Qiskit Aer to simulate **Depolarizing Noise**. This demonstrates how real-world quantum hardware (decoherence) would degrade the "Quantum Advantage," causing the (3, 3) peak to flatten.

## 4. Explaining to the Professor (Pro-Tips)
*   **The "Magic" Move:** Explain that strategy $Q$ is powerful because it uses the relative phase between $|0\rangle$ and $|1\rangle$. In a classical game, you can only flip the bit; in a quantum game, you can rotate its phase.
*   **Entanglement ($\gamma$):** Highlight the importance of the $\gamma$ parameter in the sidebar. If $\gamma = 0$ (no entanglement), the game collapses back to a classical one. As $\gamma \to \pi/2$, the quantum features emerge.
*   **Symmetry:** Point out that the landscapes for Alice and Bob are symmetric but shifted, reflecting the fair but competitive nature of the game.

## 5. Summary of Files
*   `app.py`: Main Streamlit Web Interface.
*   `tui_game.py`: Advanced Terminal Visualization.
*   `ewl_protocol.py`: Core Quantum Circuit Physics.
*   `fast_simulator.py`: Optimized Linear Algebra Backend.
*   `noise_analysis.py`: Hardware Error Simulation.
