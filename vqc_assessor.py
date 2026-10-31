import numpy as np

class VQCAssessor:
    """Optional PennyLane VQC demonstration; fixed, untrained parameters."""
    def __init__(self):
        try:
            import pennylane as qml
            self.dev = qml.device("default.qubit", wires=2)
            @qml.qnode(self.dev)
            def circuit(inputs, weights):
                qml.AngleEmbedding(inputs[:2], wires=[0, 1], rotation="Y")
                qml.AngleEmbedding(inputs[2:4], wires=[0, 1], rotation="Z")
                qml.StronglyEntanglingLayers(weights, wires=[0, 1])
                return qml.expval(qml.PauliZ(0))
            self.circuit = circuit
            self.weights = np.array([[[0.21, 0.37, 0.13],
                                      [0.42, 0.18, 0.31]]])
            self.available = True
        except ImportError:
            self.available = False

    def score(self, x):
        if self.available:
            expectation = float(self.circuit(x, self.weights))
            return float(np.clip((1 - expectation) / 2, 0, 1))
        # Heuristic fallback, not a quantum result.
        amount, hour, count, international = x
        return float(np.clip(.35*amount + .25*count +
            .20*international + .20*(hour > .85), 0, 1))
