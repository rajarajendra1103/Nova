import math
import random
from nova_libs.core import StdModule
from nova_libs.data.numpy import NumpyArray, NovaArray

# ============================================================
# PYTHON IMPLEMENTATION (FOR INTERPRETER - FAST DEV)
# ============================================================
class DenseLayerPython:
    def __init__(self, in_features: int, out_features: int, activation: str = "relu"):
        self.in_features = int(in_features)
        self.out_features = int(out_features)
        self.activation = str(activation).lower()
        self.weights = [[random.uniform(-0.5, 0.5) for _ in range(self.out_features)] for _ in range(self.in_features)]
        self.bias = [0.0 for _ in range(self.out_features)]

    def forward(self, input_data):
        raw = input_data.data if hasattr(input_data, "data") else list(input_data)
        out = []
        for j in range(self.out_features):
            val = self.bias[j]
            for i in range(min(len(raw), self.in_features)):
                val += raw[i] * self.weights[i][j]
            if self.activation == "sigmoid":
                val = 1.0 / (1.0 + math.exp(-val)) if -700 <= val <= 700 else (0.0 if val < -700 else 1.0)
            elif self.activation == "relu":
                val = max(0.0, val)
            out.append(val)
        return NumpyArray(out)

    def __repr__(self):
        return f"<DenseLayer {self.in_features}->{self.out_features} act:{self.activation}>"


def dense(in_features: int, out_features: int, activation: str = "relu"):
    return DenseLayerPython(in_features, out_features, activation)


def forward(layer, input_data):
    if hasattr(layer, "forward"):
        return layer.forward(input_data)
    return input_data


def sigmoid(x: float):
    x = float(x)
    return 1.0 / (1.0 + math.exp(-x)) if -700 <= x <= 700 else (0.0 if x < -700 else 1.0)


def relu(x: float):
    return max(0.0, float(x))


def build_ai_module():
    m = {}
    m["dense"]   = dense
    m["forward"] = forward
    m["sigmoid"] = sigmoid
    m["relu"]    = relu
    return StdModule("ai", m)


# ============================================================
# C TEMPLATES (FOR COMPILER - BLAZING-FAST STANDALONE BINARY)
# ============================================================
cCode = {
    "include": '#include "nova_ai.h"',
    "dense": 'DenseLayer {var} = aiDense({inFeatures}, {outFeatures}, "{activation}");',
    "forward": 'NumpyArray {var} = aiForward(&{layer}, &{input});',
    "sigmoid": 'float {var} = aiSigmoid({x});',
    "relu": 'float {var} = aiRelu({x});',
}
