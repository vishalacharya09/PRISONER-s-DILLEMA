import numpy as np
from qiskit_aer import Aer
from qiskit import transpile
from ewl_protocol import (
    build_ewl_circuit, 
    compute_expected_payoff, 
    strategy_C, 
    strategy_D, 
    strategy_Q
)

def simulate_strategies(u_A, u_B, shots=8192):
    circuit = build_ewl_circuit(u_A, u_B)
    
    # Use Aer's qasm_simulator
    simulator = Aer.get_backend('qasm_simulator')
    
    # Transpile the circuit for the simulator
    transpiled_circuit = transpile(circuit, simulator)
    
    # Run the simulation
    job = simulator.run(transpiled_circuit, shots=shots)
    result = job.result()
    counts = result.get_counts()
    
    # Compute payoffs
    payoff_A, payoff_B = compute_expected_payoff(counts, shots)
    return counts, payoff_A, payoff_B

def test_CC():
    counts, pA, pB = simulate_strategies(strategy_C, strategy_C)
    print(f"C-C Payoff: ({pA:.2f}, {pB:.2f}), Counts: {counts}")
    assert '00' in counts
    assert abs(pA - 3) < 0.1
    assert abs(pB - 3) < 0.1

def test_DD():
    counts, pA, pB = simulate_strategies(strategy_D, strategy_D)
    print(f"D-D Payoff: ({pA:.2f}, {pB:.2f}), Counts: {counts}")
    assert '11' in counts
    assert abs(pA - 1) < 0.1
    assert abs(pB - 1) < 0.1

def test_QQ():
    # As per EWL protocol, Q-Q should collapse to |00> and give (3,3)
    counts, pA, pB = simulate_strategies(strategy_Q, strategy_Q)
    print(f"Q-Q Payoff: ({pA:.2f}, {pB:.2f}), Counts: {counts}")
    assert '00' in counts
    assert abs(pA - 3) < 0.1
    assert abs(pB - 3) < 0.1

if __name__ == "__main__":
    test_CC()
    test_DD()
    test_QQ()
    print("All tests passed.")
