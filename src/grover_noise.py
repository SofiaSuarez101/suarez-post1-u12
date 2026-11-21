"""Experimento 4: Grover (target='11') con y sin ruido despolarizante."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from qiskit.visualization import plot_histogram
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error

from grover import build_grover_circuit  # mismo circuito del Experimento 3

CAPTURAS = Path(__file__).resolve().parent.parent / "capturas"


def build_noise_model(p1q=0.001, p2q=0.01):
    """Ruido despolarizante: p1q por puerta de 1 qubit (h, x) y p2q por
    puerta de 2 qubits (cz). Órdenes de magnitud típicos de procesadores
    superconductores NISQ (~0.1% y ~1%)."""
    noise_model = NoiseModel()
    noise_model.add_all_qubit_quantum_error(depolarizing_error(p1q, 1), ["h", "x"])
    noise_model.add_all_qubit_quantum_error(depolarizing_error(p2q, 2), ["cz"])
    return noise_model


def grover_noise_experiment(target="11", shots=1024):
    """Compara la probabilidad de éxito de Grover sin ruido vs. con ruido."""
    qc = build_grover_circuit(target)

    # Línea base ideal
    counts_ideal = AerSimulator().run(qc, shots=shots).result().get_counts()

    # Con ruido en cada puerta
    noisy_sim = AerSimulator(noise_model=build_noise_model())
    counts_noisy = noisy_sim.run(qc, shots=shots).result().get_counts()

    p_ideal = counts_ideal.get(target, 0) / shots
    p_noisy = counts_noisy.get(target, 0) / shots

    print(f"Grover |{target}> sin ruido: {p_ideal * 100:.1f}%")
    print(f"Grover |{target}> con ruido: {p_noisy * 100:.1f}%")
    print(f"Degradación: {(p_ideal - p_noisy) * 100:.1f} puntos porcentuales")
    print(f"Distribución con ruido: {dict(sorted(counts_noisy.items()))}")

    CAPTURAS.mkdir(exist_ok=True)
    fig, axs = plt.subplots(1, 2, figsize=(10, 4))
    plot_histogram(counts_ideal, ax=axs[0], title="Sin ruido")
    plot_histogram(counts_noisy, ax=axs[1], title="Con ruido (despolarizante)")
    fig.tight_layout()
    fig.savefig(CAPTURAS / "grover_noise_comparison.png", dpi=150)
    return p_ideal, p_noisy


if __name__ == "__main__":
    grover_noise_experiment()
