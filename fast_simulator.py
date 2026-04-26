import numpy as np
import scipy.linalg

def get_J_matrix(gamma=np.pi/2):
    """Generates the Entangling Operator J as a 4x4 unitary matrix."""
    X = np.array([[0, 1], [1, 0]])
    XX = np.kron(X, X)
    return scipy.linalg.expm(1j * (gamma / 2.0) * XX)

def su2_unitary_vec(theta, phi):
    """
    Vectorized SU(2) unitary generation.
    theta, phi can be arrays of any shape.
    Returns an array of shape (..., 2, 2).
    """
    # Ensure inputs are arrays
    theta = np.asanyarray(theta)
    phi = np.asanyarray(phi)
    
    # Pre-calculate components
    exp_i_phi = np.exp(1j * phi)
    cos_t2 = np.cos(theta / 2)
    sin_t2 = np.sin(theta / 2)
    
    # Build 2x2 matrix elements
    u00 = exp_i_phi * cos_t2
    u01 = 1j * sin_t2
    u10 = 1j * sin_t2
    u11 = np.exp(-1j * phi) * cos_t2
    
    # Stack into (..., 2, 2)
    # Each element is (..., 1, 1) or we stack along new axes
    return np.stack([
        np.stack([u00, u01], axis=-1),
        np.stack([u10, u11], axis=-1)
    ], axis=-2)

def ewl_payoff_fast(U_A_grid, U_B, gamma=np.pi/2):
    """
    Computes payoffs for a grid of Alice's strategies against a single Bob strategy.
    U_A_grid: shape (N, M, 2, 2)
    U_B: shape (2, 2)
    Returns: (payoff_A, payoff_B, probs) where payoffs are (N, M) and probs is (N, M, 4)
    """
    J = get_J_matrix(gamma)
    J_dag = J.conj().T
    
    # Initial state |00> is [1, 0, 0, 0]
    # State after J: first column of J
    psi_in = J[:, 0] # shape (4,)
    
    # U_total = U_A \otimes U_B
    # We need to compute this for every element in the grid
    # U_A is (N, M, 2, 2), U_B is (2, 2)
    # np.kron doesn't vectorize nicely over the first dims, so we use reshape/transpose
    
    # U_A has shape (N, M, 2, 2)
    # U_B has shape (2, 2)
    # Qiskit ordering q1 tensor q0 means U_B tensor U_A
    U_tot = np.einsum('ij,...kl->...ikjl', U_B, U_A_grid).reshape(*(U_A_grid.shape[:-2]), 4, 4)
    
    # psi_strat = U_tot @ psi_in
    # U_tot is (N, M, 4, 4), psi_in is (4,)
    psi_strat = np.einsum('...ij,j->...i', U_tot, psi_in) # shape (N, M, 4)
    
    # psi_out = J_dag @ psi_strat
    psi_out = np.einsum('ij,...j->...i', J_dag, psi_strat) # shape (N, M, 4)
    
    # Probabilities = |psi_out|^2
    probs = np.abs(psi_out)**2 # shape (N, M, 4)
    
    # Indices for |Bob Alice>:
    # 0: |00> -> Alice=0, Bob=0 (C,C) -> (3,3)
    # 1: |01> -> Alice=1, Bob=0 (D,C) -> (5,0)
    # 2: |10> -> Alice=0, Bob=1 (C,D) -> (0,5)
    # 3: |11> -> Alice=1, Bob=1 (D,D) -> (1,1)
    
    pA_vals = np.array([3, 5, 0, 1])
    pB_vals = np.array([3, 0, 5, 1])
    
    payoff_A = np.einsum('...i,i->...', probs, pA_vals)
    payoff_B = np.einsum('...i,i->...', probs, pB_vals)
    
    return payoff_A, payoff_B, probs

if __name__ == "__main__":
    # Test
    from ewl_protocol import strategy_C, strategy_D, strategy_Q
    
    # Test C vs C
    UA = strategy_C.reshape(1, 1, 2, 2)
    UB = strategy_C
    pA, pB, _ = ewl_payoff_fast(UA, UB)
    print(f"C-C: A={pA[0,0]:.2f}, B={pB[0,0]:.2f} (Expected 3, 3)")
    
    # Test Q vs Q
    UA = strategy_Q.reshape(1, 1, 2, 2)
    UB = strategy_Q
    pA, pB, _ = ewl_payoff_fast(UA, UB)
    print(f"Q-Q: A={pA[0,0]:.2f}, B={pB[0,0]:.2f} (Expected 3, 3)")
    
    # Test D vs C
    UA = strategy_D.reshape(1, 1, 2, 2)
    UB = strategy_C
    pA, pB, _ = ewl_payoff_fast(UA, UB)
    print(f"D-C: A={pA[0,0]:.2f}, B={pB[0,0]:.2f} (Expected 5, 0)")
