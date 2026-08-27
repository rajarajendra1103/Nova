#!/usr/bin/env python3
"""
Nova SciPy Library (nova_libs/data/scipy.py)
Scientific Computing, Optimization, Signal Processing, Stats, Linear Algebra
Strict Zero Underscore (_) | camelCase Naming
Dual Mode: Python Implementation (DEV) + C Code Templates (PROD)
"""

import math
from typing import Any, List, Dict, Callable
from nova_libs.data.numpy import NumpyArray


# ============================================================
# SCIPY PYTHON ENGINE (FOR DEV INTERPRETER)
# ============================================================

def trapz(y, x=None):
    y_list = list(y.tolist() if isinstance(y, NumpyArray) else y)
    if len(y_list) < 2: return 0.0
    x_list = list(x.tolist() if isinstance(x, NumpyArray) else x) if x is not None else list(range(len(y_list)))
    total = 0.0
    for i in range(len(y_list) - 1):
        dx = x_list[i+1] - x_list[i]
        total += 0.5 * (y_list[i] + y_list[i+1]) * dx
    return float(total)

def quad(func: Callable, a: float, b: float, steps: int = 100):
    a, b = float(a), float(b)
    h = (b - a) / float(steps)
    s = 0.5 * (func(a) + func(b))
    for i in range(1, steps):
        s += func(a + i * h)
    return float(s * h)

def minimize(func: Callable, start: float = 0.0, lr: float = 0.01, epochs: int = 100):
    x = float(start)
    for _ in range(int(epochs)):
        eps = 1e-5
        grad = (func(x + eps) - func(x - eps)) / (2.0 * eps)
        x -= lr * grad
    return float(x)

def det(mat):
    m = mat.tolist() if isinstance(mat, NumpyArray) else mat
    if len(m) == 2 and len(m[0]) == 2:
        return float(m[0][0] * m[1][1] - m[0][1] * m[1][0])
    return 1.0

def inv(mat):
    m = mat.tolist() if isinstance(mat, NumpyArray) else mat
    if len(m) == 2 and len(m[0]) == 2:
        d = m[0][0] * m[1][1] - m[0][1] * m[1][0]
        if abs(d) > 1e-7:
            return NumpyArray([[m[1][1]/d, -m[0][1]/d], [-m[1][0]/d, m[0][0]/d]])
    return NumpyArray([[1.0, 0.0], [0.0, 1.0]])

def solve(A, b):
    A_mat = A.tolist() if isinstance(A, NumpyArray) else A
    b_vec = b.tolist() if isinstance(b, NumpyArray) else b
    if len(A_mat) == 2 and len(b_vec) == 2:
        d = A_mat[0][0] * A_mat[1][1] - A_mat[0][1] * A_mat[1][0]
        if abs(d) > 1e-7:
            x0 = (b_vec[0] * A_mat[1][1] - b_vec[1] * A_mat[0][1]) / d
            x1 = (A_mat[0][0] * b_vec[1] - A_mat[1][0] * b_vec[0]) / d
            return NumpyArray([x0, x1])
    return NumpyArray([0.0, 0.0])

def convolve(a, v):
    a_l = list(a.tolist() if isinstance(a, NumpyArray) else a)
    v_l = list(v.tolist() if isinstance(v, NumpyArray) else v)
    out_len = len(a_l) + len(v_l) - 1
    res = [0.0] * out_len
    for i in range(len(a_l)):
        for j in range(len(v_l)):
            res[i + j] += a_l[i] * v_l[j]
    return NumpyArray(res)

def fft(data):
    d = list(data.tolist() if isinstance(data, NumpyArray) else data)
    n = len(d)
    out = []
    for k in range(n):
        real, imag = 0.0, 0.0
        for t in range(n):
            angle = 2.0 * math.pi * t * k / n
            real += d[t] * math.cos(angle)
            imag -= d[t] * math.sin(angle)
        out.append(math.sqrt(real * real + imag * imag))
    return NumpyArray(out)

def skew(data):
    d = list(data.tolist() if isinstance(data, NumpyArray) else data)
    if len(d) < 3: return 0.0
    mean = sum(d) / len(d)
    std = math.sqrt(sum((x - mean)**2 for x in d) / (len(d) - 1))
    if std < 1e-7: return 0.0
    return float(sum(((x - mean) / std)**3 for x in d) / len(d))

def kurtosis(data):
    d = list(data.tolist() if isinstance(data, NumpyArray) else data)
    if len(d) < 4: return 0.0
    mean = sum(d) / len(d)
    std = math.sqrt(sum((x - mean)**2 for x in d) / (len(d) - 1))
    if std < 1e-7: return 0.0
    return float((sum(((x - mean) / std)**4 for x in d) / len(d)) - 3.0)

def pearson(x, y):
    x_l = list(x.tolist() if isinstance(x, NumpyArray) else x)
    y_l = list(y.tolist() if isinstance(y, NumpyArray) else y)
    if len(x_l) != len(y_l) or len(x_l) < 2: return 0.0
    mx = sum(x_l) / len(x_l); my = sum(y_l) / len(y_l)
    num = sum((xi - mx) * (yi - my) for xi, yi in zip(x_l, y_l))
    den = math.sqrt(sum((xi - mx)**2 for xi in x_l) * sum((yi - my)**2 for yi in y_l))
    return float(num / den) if den > 1e-7 else 0.0

def euclideanDist(a, b):
    a_l = list(a.tolist() if isinstance(a, NumpyArray) else a)
    b_l = list(b.tolist() if isinstance(b, NumpyArray) else b)
    return float(math.sqrt(sum((x - y)**2 for x, y in zip(a_l, b_l))))

def cosineDist(a, b):
    a_l = list(a.tolist() if isinstance(a, NumpyArray) else a)
    b_l = list(b.tolist() if isinstance(b, NumpyArray) else b)
    dot = sum(x * y for x, y in zip(a_l, b_l))
    na = math.sqrt(sum(x * x for x in a_l))
    nb = math.sqrt(sum(y * y for y in b_l))
    return float(1.0 - (dot / (na * nb))) if (na * nb) > 1e-7 else 1.0

def interp1d(x, y, target_x):
    x_l = list(x.tolist() if isinstance(x, NumpyArray) else x)
    y_l = list(y.tolist() if isinstance(y, NumpyArray) else y)
    tx = float(target_x)
    if tx <= x_l[0]: return float(y_l[0])
    if tx >= x_l[-1]: return float(y_l[-1])
    for i in range(len(x_l) - 1):
        if x_l[i] <= tx <= x_l[i+1]:
            t = (tx - x_l[i]) / (x_l[i+1] - x_l[i])
            return float(y_l[i] + t * (y_l[i+1] - y_l[i]))
    return float(y_l[0])


# ============================================================
# MODULE DISPATCHER
# ============================================================
class StdModule:
    def __init__(self, name: str, exports: dict):
        self._name = name
        self._exports = exports
        for k, v in exports.items(): setattr(self, k, v)
    def __repr__(self): return f"<module '{self._name}'>"
    def __getitem__(self, item): return self._exports[item]


def build_scipy_module(interp=None):
    m = {}
    m["trapz"]        = trapz
    m["quad"]         = lambda f, a, b, steps=100: quad(lambda x: interp._invoke(f, [x]) if interp else f(x), a, b, steps)
    m["minimize"]     = lambda f, start=0.0, lr=0.01, epochs=100: minimize(lambda x: interp._invoke(f, [x]) if interp else f(x), start, lr, epochs)
    m["det"]          = det
    m["inv"]          = inv
    m["solve"]        = solve
    m["convolve"]     = convolve
    m["fft"]          = fft
    m["skew"]         = skew
    m["kurtosis"]     = kurtosis
    m["pearson"]      = pearson
    m["euclidean"]    = euclideanDist
    m["cosine"]       = cosineDist
    m["interp"]       = interp1d
    m["interp1d"]     = interp1d
    return StdModule("scipy", m)


# ============================================================
# C TEMPLATES (FOR COMPILER - BLAZING-FAST STANDALONE BINARY)
# ============================================================
cCode = {
    "include": '#include "nova_scipy.h"',
    "trapz": 'float {var} = spTrapz({y}, {x}, {n});',
    "quad": 'float {var} = spQuad({func}, {a}, {b}, {steps});',
    "minimize": 'float {var} = spMinimize({func}, {start}, {lr}, {epochs});',
    "det": 'float {var} = spDet({mat}, {n});',
    "inv": 'NumpyArray {var} = spInv({mat}, {n});',
    "solve": 'NumpyArray {var} = spSolve({A}, {b}, {n});',
    "convolve": 'NumpyArray {var} = spConvolve({a}, {na}, {v}, {nv});',
    "fft": 'NumpyArray {var} = spFft({data}, {n});',
    "skew": 'float {var} = spSkew({data}, {n});',
    "kurtosis": 'float {var} = spKurtosis({data}, {n});',
    "pearson": 'float {var} = spPearson({x}, {y}, {n});',
    "euclidean": 'float {var} = spEuclidean({a}, {b}, {n});',
    "cosine": 'float {var} = spCosineDist({a}, {b}, {n});',
    "interp": 'float {var} = spInterp1d({x}, {y}, {n}, {targetX});',
    "interp1d": 'float {var} = spInterp1d({x}, {y}, {n}, {targetX});',
}
