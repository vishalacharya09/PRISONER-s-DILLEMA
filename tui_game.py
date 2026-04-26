import os
import numpy as np
import time
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.align import Align
from rich.live import Live
from rich.prompt import Prompt, FloatPrompt
from rich import box
from rich.progress import BarColumn, Progress, TextColumn

from ewl_protocol import (
    strategy_C, strategy_D, strategy_Q, 
    build_ewl_circuit, compute_expected_payoff
)
from test_ewl_protocol import simulate_strategies
from noise_analysis import simulate_with_noise
from strategy_sweep import su2_unitary, run_strategy_sweep

console = Console()

def get_bar_chart(data, title, max_val=5.0):
    """
    Creates a simple horizontal bar chart using Rich.
    data: list of (label, value)
    """
    table = Table(show_header=False, box=None, padding=(0, 1))
    for label, value in data:
        # Use full blocks for the bar
        bar_length = int((value / max_val) * 20) if max_val > 0 else 0
        bar = "█" * bar_length
        color = "green" if value > 2.5 else "yellow" if value > 1 else "red"
        table.add_row(
            f"[bold]{label}[/bold]", 
            f"[{color}]{bar}[/{color}]", 
            f"{value:.2f}"
        )
    return Panel(table, title=title, border_style="cyan")

def get_prob_chart(counts, shots):
    """
    Creates a probability distribution bar chart.
    """
    table = Table(show_header=False, box=None, padding=(0, 1))
    sorted_outcomes = sorted(counts.items(), key=lambda x: x[0])
    for outcome, count in sorted_outcomes:
        prob = count / shots
        bar_length = int(prob * 30)
        bar = "█" * bar_length
        table.add_row(
            f"|{outcome}>", 
            f"[magenta]{bar}[/magenta]", 
            f"{prob*100:.1f}%"
        )
    return Panel(table, title="Measurement Probabilities", border_style="magenta")

def get_heatmap(payoffs, resolution):
    """
    Creates a text-based heatmap for Alice's payoff.
    """
    # Define a color gradient for payoffs (0 to 5)
    # 0-1: Red, 1-2: Red/Yellow, 2-3: Yellow, 3-4: Green, 4-5: Bright Green
    def get_color(val):
        if val < 1: return "red"
        if val < 2: return "orange3"
        if val < 3: return "yellow"
        if val < 4: return "green"
        return "bright_green"

    grid = ""
    # Payoffs is a (resolution, resolution) matrix
    # We want to print it row by row (Theta)
    for i in range(resolution):
        row_str = ""
        for j in range(resolution):
            val = payoffs[i, j]
            color = get_color(val)
            row_str += f"[{color}]██[/{color}]"
        grid += row_str + "\n"
    
    return Panel(
        Align.center(grid), 
        title="Payoff Landscape (Theta x Phi)", 
        border_style="green",
        subtitle="[red]0[/red] -> [yellow]2.5[/yellow] -> [bright_green]5[/bright_green]"
    )

def make_layout():
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="main", size=20),
        Layout(name="footer", size=3)
    )
    layout["main"].split_row(
        Layout(name="left", ratio=1),
        Layout(name="right", ratio=1)
    )
    layout["right"].split_column(
        Layout(name="circuit", ratio=1),
        Layout(name="probs", ratio=1)
    )
    return layout

def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    
    layout = make_layout()
    layout["header"].update(Panel(Align.center("[bold cyan]QUANTUM PRISONER'S DILEMMA TUI[/bold cyan]"), border_style="blue"))
    layout["footer"].update(Panel(Align.center("Use [bold yellow]Ctrl+C[/bold yellow] to exit"), border_style="blue"))
    
    while True:
        console.print("\n[bold green]Game Configuration[/bold green]")
        a_strat_name = Prompt.ask("Alice's Strategy", choices=["C", "D", "Q", "Custom"], default="C")
        b_strat_name = Prompt.ask("Bob's Strategy", choices=["C", "D", "Q", "Custom"], default="C")
        
        noise_rate = FloatPrompt.ask("Noise Level (0.0 to 0.1)", default=0.0)
        
        def parse_strat(name):
            if name == "C": return strategy_C, "Cooperate"
            if name == "D": return strategy_D, "Defect"
            if name == "Q": return strategy_Q, "Quantum (Q)"
            # For custom, we'll just use a fixed theta/phi for demo or prompt
            theta = FloatPrompt.ask(f"Enter Theta for {name}", default=0.0)
            phi = FloatPrompt.ask(f"Enter Phi for {name}", default=0.0)
            return su2_unitary(theta, phi), f"Custom({theta:.1f},{phi:.1f})"

        u_A, a_disp = parse_strat(a_strat_name)
        u_B, b_disp = parse_strat(b_strat_name)
        
        with console.status("[bold yellow]Simulating Quantum Circuit..."):
            shots = 1024
            if noise_rate > 0:
                counts, pA, pB = simulate_with_noise(u_A, u_B, error_rate=noise_rate, shots=shots)
            else:
                counts, pA, pB = simulate_strategies(u_A, u_B, shots=shots)
            
            # Get circuit
            qc = build_ewl_circuit(u_A, u_B)
            circuit_text = qc.draw('text')
            
        # Update Layout
        layout["left"].update(get_bar_chart([("Alice", pA), ("Bob", pB)], f"Expected Payoffs ({a_disp} vs {b_disp})"))
        layout["circuit"].update(Panel(Align.center(str(circuit_text)), title="Quantum Circuit", border_style="yellow"))
        layout["probs"].update(get_prob_chart(counts, shots))
        
        os.system('cls' if os.name == 'nt' else 'clear')
        console.print(layout)
        
        choice = Prompt.ask("\nAction", choices=["Rerun", "View Landscape", "Exit"], default="Rerun")
        if choice == "Exit":
            break
        elif choice == "View Landscape":
            with console.status("[bold green]Calculating Landscape (Alice vs Bob's Q)..."):
                res = 15
                thetas, phis, payoffs = run_strategy_sweep(resolution=res)
                heatmap = get_heatmap(payoffs, res)
            console.print(heatmap)
            Prompt.ask("Press Enter to continue")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold red]Exiting...[/bold red]")
