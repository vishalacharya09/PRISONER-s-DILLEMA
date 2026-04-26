import numpy as np
from ewl_protocol import strategy_C, strategy_D, strategy_Q
from test_ewl_protocol import simulate_strategies

def get_strategy(name, choice):
    if choice.upper() == 'C':
        return strategy_C, "Cooperate"
    elif choice.upper() == 'D':
        return strategy_D, "Defect"
    elif choice.upper() == 'Q':
        return strategy_Q, "Quantum (Q)"
    else:
        return None, None

def main():
    print("==============================================")
    print("   WELCOME TO THE QUANTUM PRISONER'S DILEMMA  ")
    print("==============================================")
    print("Strategies:")
    print(" [C] Cooperate (Classical)")
    print(" [D] Defect    (Classical)")
    print(" [Q] Quantum   (The 'Magic' EWL Move)")
    print("----------------------------------------------")

    # Get Alice's Input
    a_choice = input("Alice, choose your strategy (C, D, Q): ").strip()
    u_A, a_name = get_strategy("Alice", a_choice)
    while u_A is None:
        a_choice = input("Invalid choice. Alice, choose C, D, or Q: ").strip()
        u_A, a_name = get_strategy("Alice", a_choice)

    # Get Bob's Input
    b_choice = input("Bob, choose your strategy (C, D, Q): ").strip()
    u_B, b_name = get_strategy("Bob", b_choice)
    while u_B is None:
        b_choice = input("Invalid choice. Bob, choose C, D, or Q: ").strip()
        u_B, b_name = get_strategy("Bob", b_choice)

    print(f"\nAlice plays: {a_name}")
    print(f"Bob plays:   {b_name}")
    print("\nRunning Quantum Circuit Simulation...")

    counts, pA, pB = simulate_strategies(u_A, u_B, shots=1024)

    print("----------------------------------------------")
    print(f"RESULTS (Expected Payoffs):")
    print(f" Alice: {pA:.2f}")
    print(f" Bob:   {pB:.2f}")
    print("----------------------------------------------")
    
    # Interpretation
    if pA == 3 and pB == 3:
        if a_choice.upper() == 'Q' and b_choice.upper() == 'Q':
            print("OUTCOME: The Quantum Nash Equilibrium! You both win big by using entanglement.")
        else:
            print("OUTCOME: Mutual Cooperation. You both played nice!")
    elif pA == 1 and pB == 1:
        print("OUTCOME: Mutual Defection. The Classical Trap! You both lost because you didn't trust each other.")
    elif pA > pB:
        print("OUTCOME: Alice Betrayed Bob! Alice takes the lion's share.")
    elif pB > pA:
        print("OUTCOME: Bob Betrayed Alice! Bob takes the lion's share.")
    else:
        print(f"OUTCOME: A mixed quantum state result. Probability counts: {counts}")

if __name__ == "__main__":
    main()
