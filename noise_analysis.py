import numpy as np
from qiskit_aer import Aer
from qiskit_aer.noise import NoiseModel, depolarizing_error
from qiskit import transpile
from ewl_protocol import build_ewl_circuit, compute_expected_payoff, strategy_Q

def simulate_with_noise(u_A, u_B, error_rate=0.03, shots=8192):
    """
    Simulates the EWL circuit with a basic depolarizing noise model
    to mimic hardware decoherence and gate errors.
    """
    # Create a basic depolarizing noise model
    noise_model = NoiseModel()
    
    # Add depolarizing error to 1-qubit and 2-qubit gates
    error_1q = depolarizing_error(error_rate / 10, 1) # 1-qubit errors are generally smaller
    error_2q = depolarizing_error(error_rate, 2)
    
    noise_model.add_all_qubit_quantum_error(error_1q, ['u1', 'u2', 'u3'])
    # In our circuit we use custom unitaries, which Qiskit transpiles into u3, cx etc.
    noise_model.add_all_qubit_quantum_error(error_2q, ['cx'])
    
    # Build circuit
    circuit = build_ewl_circuit(u_A, u_B)
    
    # Transpile using standard basis gates so noise can be applied
    basis_gates = noise_model.basis_gates
    simulator = Aer.get_backend('qasm_simulator')
    transpiled_circuit = transpile(circuit, simulator, basis_gates=basis_gates, optimization_level=3)
    
    # Run
    job = simulator.run(transpiled_circuit, noise_model=noise_model, shots=shots)
    counts = job.result().get_counts()
    
    pA, pB = compute_expected_payoff(counts, shots)
    return counts, pA, pB

if __name__ == "__main__":
    print("Ideal Case (Q-Q):")
    # from test_ewl_protocol, we know it's ~3.0
    
    print("\nNoisy Case (Q-Q, 3% two-qubit error rate):")
    counts_noisy, pA, pB = simulate_with_noise(strategy_Q, strategy_Q, error_rate=0.03)
    print(f"Counts: {counts_noisy}")
    print(f"Payoff A: {pA:.2f}, Payoff B: {pB:.2f}")
    
    # Calculate probability of |00>
    p_00 = counts_noisy.get('00', 0) / 8192
    print(f"\nProbability of |00> (Nash Equilibrium state): {p_00:.4f}")
    print("Note: Expected hardware observations typically show probability dropping from 1.0 to ~0.85-0.95.")
