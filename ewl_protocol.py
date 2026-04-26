import numpy as np
import scipy.linalg
from qiskit import QuantumCircuit
from qiskit.quantum_info import Operator

# Payoff Matrix for Prisoner's Dilemma
# Format: 'AliceBob' -> (Alice_payoff, Bob_payoff)
# 0 = Cooperate (C), 1 = Defect (D)
PAYOFF_MATRIX = {
    '00': (3, 3), # C, C
    '01': (0, 5), # C, D
    '10': (5, 0), # D, C
    '11': (1, 1)  # D, D
}

def get_J_matrix(gamma=np.pi/2):
    """
    Generates the Entangling Operator J as a 4x4 unitary matrix.
    J = exp(i * gamma/2 * (X_A tensor X_B))
    """
    X = np.array([[0, 1], [1, 0]])
    XX = np.kron(X, X)
    J = scipy.linalg.expm(1j * (gamma / 2.0) * XX)
    return J

def build_ewl_circuit(U_A, U_B, gamma=np.pi/2):
    """
    Builds the EWL Quantum Protocol circuit for Alice and Bob.
    U_A and U_B are 2x2 unitary matrices representing their strategies.
    q0 is Alice, q1 is Bob.
    """
    qc = QuantumCircuit(2, 2)
    
    # 1. Apply entangling operator J
    J_mat = get_J_matrix(gamma)
    J_op = Operator(J_mat)
    # Qiskit uses little-endian ordering, meaning qubits are listed right-to-left in kron.
    # We apply J to [0, 1] which translates to q1 tensor q0.
    qc.unitary(J_op, [0, 1], label='J')
    
    # 2. Apply player strategies (independent unitaries)
    qc.unitary(Operator(U_A), [0], label='U_A')
    qc.unitary(Operator(U_B), [1], label='U_B')
    
    # 3. Apply disentangling operator J-dagger
    J_dag_mat = J_mat.conj().T
    J_dag_op = Operator(J_dag_mat)
    qc.unitary(J_dag_op, [0, 1], label='J_dag')
    
    # 4. Measurement
    qc.measure([0, 1], [0, 1])
    
    return qc

def compute_expected_payoff(counts, shots):
    """
    Computes the expected payoff for Alice and Bob given measurement counts.
    Qiskit output format 'c1 c0' where c1 is Bob (q1) and c0 is Alice (q0).
    """
    expected_A = 0.0
    expected_B = 0.0
    
    for outcome, count in counts.items():
        # Reverse Qiskit's bitstring to get 'AliceBob' ordering
        alice_bob_state = outcome[::-1]
        
        if alice_bob_state in PAYOFF_MATRIX:
            pA, pB = PAYOFF_MATRIX[alice_bob_state]
            prob = count / shots
            expected_A += pA * prob
            expected_B += pB * prob
            
    return expected_A, expected_B

# Define standard EWL strategies
# Cooperate (C)
strategy_C = np.array([[1, 0], [0, 1]], dtype=complex)

# Defect (D) - Typically represented as i*Y in SU(2) to flip 0 to 1 with a phase
strategy_D = np.array([[0, 1], [-1, 0]], dtype=complex)

# Quantum strategy (Q) - i*Z
strategy_Q = np.array([[1j, 0], [0, -1j]], dtype=complex)

