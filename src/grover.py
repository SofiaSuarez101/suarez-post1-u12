"""Experimento 3: algoritmo de Grover para n=2 qubits (4 elementos)."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

from qiskit import QuantumCircuit
from qiskit.visualization import plot_histogram
from qiskit_aer import AerSimulator

CAPTURAS = Path(__file__).resolve().parent.parent / "capturas"


def apply_phase_oracle(qc, target):
    """Marca con fase -1 el estado `target` (cadena 'q1q0', convención Qiskit).

    Qiskit usa orden little-endian: en la cadena "01", el bit derecho ('1')
    es el qubit 0 y el izquierdo ('0') es el qubit 1. Se aplica X a cada qubit
    cuyo bit objetivo es 0, luego CZ (fase -1 solo en |11>) y se deshace la X.
    """
    zero_qubits = [q for q in range(2) if target[::-1][q] == "0"]
    if zero_qubits:
        qc.x(zero_qubits)
    qc.cz(0, 1)
    if zero_qubits:
        qc.x(zero_qubits)


def apply_diffuser(qc):
    """Difusor: inversión alrededor de la media (H X CZ X H)."""
    qc.h([0, 1])
    qc.x([0, 1])
    qc.cz(0, 1)
    qc.x([0, 1])
    qc.h([0, 1])


def build_grover_circuit(target="11"):
    """Circuito de Grover de 2 qubits con 1 iteración (óptima para N=4)."""
    qc = QuantumCircuit(2, 2)
    qc.h([0, 1])                   # superposición uniforme
    apply_phase_oracle(qc, target)  # oráculo
    apply_diffuser(qc)              # amplificación de amplitud
    qc.measure([0, 1], [0, 1])
    return qc


def grover_2qubits(target="11", shots=1024):
    """Ejecuta Grover buscando `target` y guarda el histograma."""
    qc = build_grover_circuit(target)
    counts = AerSimulator().run(qc, shots=shots).result().get_counts()

    print(f"Grover buscando |{target}> ({shots} shots):")
    for state, count in sorted(counts.items()):
        print(f"  |{state}>: {count:4d} ({count / shots * 100:.1f}%)")

    top = max(counts, key=counts.get)
    veredicto = "CORRECTO" if top == target else "ERROR"
    print(f"Estado más probable: |{top}> - {veredicto}")

    CAPTURAS.mkdir(exist_ok=True)
    fig = plot_histogram(counts)
    fig.savefig(CAPTURAS / f"grover_{target}.png", dpi=150)
    return counts


if __name__ == "__main__":
    for t in ["00", "01", "10", "11"]:
        grover_2qubits(target=t)
        print()
