import os
import sys

def main():
    print("==========================================")
    print(" Quantum Game Theory Project Execution")
    print("==========================================")
    
    print("\n[1] Running Core EWL Protocol Tests...")
    try:
        import test_ewl_protocol
        test_ewl_protocol.test_CC()
        test_ewl_protocol.test_DD()
        test_ewl_protocol.test_QQ()
        print(" -> All core EWL protocol tests passed!\n")
    except Exception as e:
        print(f" -> Error in core EWL tests: {e}")
        return

    print("[2] Running Strategy Sweep Engine...")
    try:
        import strategy_sweep
        # Run a smaller resolution for quick execution
        thetas, phis, landscape = strategy_sweep.run_strategy_sweep(resolution=10)
        strategy_sweep.plot_landscape(thetas, phis, landscape)
        print(" -> Strategy sweep complete. Output saved to 'payoff_landscape.png'.\n")
    except Exception as e:
        print(f" -> Error in strategy sweep: {e}")
        return

    print("[3] Running Hardware Noise Analysis...")
    try:
        import noise_analysis
        # Setting a higher error rate to visibly demonstrate the drop
        counts_noisy, pA, pB = noise_analysis.simulate_with_noise(
            noise_analysis.strategy_Q, 
            noise_analysis.strategy_Q, 
            error_rate=0.05
        )
        print(f" -> Noisy Counts: {counts_noisy}")
        print(f" -> Payoff Alice: {pA:.2f}, Payoff Bob: {pB:.2f}")
        p_00 = counts_noisy.get('00', 0) / sum(counts_noisy.values())
        print(f" -> Probability of |00> (Nash Equilibrium state): {p_00:.4f}")
        print(" -> Noise analysis complete.\n")
    except Exception as e:
        print(f" -> Error in noise analysis: {e}")
        return

    print("==========================================")
    print(" All components executed successfully!")
    print("==========================================")

if __name__ == "__main__":
    # Ensure matplotlib doesn't block if run in environments without display
    import matplotlib
    matplotlib.use('Agg')
    main()
