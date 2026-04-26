import numpy as np
import matplotlib.pyplot as plt
from ewl_protocol import strategy_Q
from test_ewl_protocol import simulate_strategies

def su2_unitary(theta, phi):
    """
    Creates an SU(2) unitary matrix parameterized by theta and phi.
    U(theta, phi) = [[e^{i*phi} cos(theta/2), i sin(theta/2)], 
                     [i sin(theta/2), e^{-i*phi} cos(theta/2)]]
    This is one possible parameterization for SU(2).
    """
    return np.array([
        [np.exp(1j * phi) * np.cos(theta / 2), 1j * np.sin(theta / 2)],
        [1j * np.sin(theta / 2), np.exp(-1j * phi) * np.cos(theta / 2)]
    ], dtype=complex)

def run_strategy_sweep(resolution=20):
    """
    Sweeps Alice's strategy across theta and phi while Bob plays Quantum strategy (Q).
    """
    print(f"Running strategy sweep with resolution {resolution}x{resolution}...")
    thetas = np.linspace(0, np.pi, resolution)
    phis = np.linspace(0, np.pi/2, resolution)
    
    payoff_landscape_A = np.zeros((resolution, resolution))
    
    for i, theta in enumerate(thetas):
        for j, phi in enumerate(phis):
            U_A = su2_unitary(theta, phi)
            # Bob plays Q
            U_B = strategy_Q
            
            _, pA, _ = simulate_strategies(U_A, U_B, shots=1024)
            payoff_landscape_A[i, j] = pA
            
    return thetas, phis, payoff_landscape_A

def plot_landscape(thetas, phis, payoffs):
    T, P = np.meshgrid(phis, thetas)
    fig = plt.figure(figsize=(10, 7))
    ax = fig.add_subplot(111, projection='3d')
    surf = ax.plot_surface(T, P, payoffs, cmap='viridis', edgecolor='none')
    
    ax.set_xlabel('Phi')
    ax.set_ylabel('Theta')
    ax.set_zlabel("Alice's Payoff")
    ax.set_title("Alice's Payoff Landscape against Bob's Q Strategy")
    fig.colorbar(surf, ax=ax, shrink=0.5, aspect=5)
    
    plt.savefig('payoff_landscape.png')
    print("Plot saved to payoff_landscape.png")

if __name__ == "__main__":
    thetas, phis, landscape = run_strategy_sweep(resolution=10) # 10x10 for quick testing
    plot_landscape(thetas, phis, landscape)
