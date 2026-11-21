"""Experimento 2: algoritmo de Deutsch-Jozsa para n=2 qubits de entrada."""
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator


def oracle_constante(n):
    """Oráculo constante f(x)=0: no hace nada (ancilla incluido)."""
    return QuantumCircuit(n + 1)


def oracle_balanceada(n):
    """Oráculo balanceado f(x)=x0 XOR x1 XOR ...: CNOT de cada qubit al ancilla."""
    qc = QuantumCircuit(n + 1)
    for i in range(n):
        qc.cx(i, n)
    return qc


def deutsch_jozsa(oracle_qc, n, shots=1024):
    """Ejecuta Deutsch-Jozsa con el oráculo dado y devuelve los counts."""
    qc = QuantumCircuit(n + 1, n)

    # Ancilla en |-> = H|1>; entradas en superposición uniforme
    qc.x(n)
    qc.h(range(n + 1))

    # Una única evaluación del oráculo
    qc.compose(oracle_qc, inplace=True)

    # Interferencia sobre los qubits de entrada
    qc.h(range(n))

    # Se miden solo los qubits de entrada (no el ancilla)
    qc.measure(range(n), range(n))

    return AerSimulator().run(qc, shots=shots).result().get_counts()


if __name__ == "__main__":
    n = 2
    counts_c = deutsch_jozsa(oracle_constante(n), n)
    print(f"Constante:  {counts_c}")  # esperado: {'00': 1024}

    counts_b = deutsch_jozsa(oracle_balanceada(n), n)
    print(f"Balanceada: {counts_b}")  # esperado: {'11': 1024}, nunca '00'

    assert counts_c.get("00", 0) == 1024, "Error: oráculo constante no retornó 00"
    assert "00" not in counts_b, "Error: oráculo balanceado retornó 00"
    print("OK: Deutsch-Jozsa verifica correctamente")
