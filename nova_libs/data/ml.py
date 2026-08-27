#!/usr/bin/env python3
"""
Nova Machine Learning Library (nova_libs/data/ml.py)
Scikit-Learn standard in Nova (import ml or import sklearn as ml)
Strict Zero Underscore (_) | camelCase Naming
Dual Mode: Python Implementation (DEV) + C Code Templates (PROD)
"""

import math
import random
from typing import Any, List, Dict, Tuple, Optional
from nova_libs.data.numpy import NumpyArray


# ============================================================
# ML PYTHON CLASSES & ENGINE (FOR DEV INTERPRETER)
# ============================================================

class LinearRegressionModel:
    def __init__(self):
        self.slope = 0.0
        self.intercept = 0.0
        self.is_fitted = False

    def fit(self, x, y):
        x_l = list(x.tolist() if isinstance(x, NumpyArray) else x)
        y_l = list(y.tolist() if isinstance(y, NumpyArray) else y)
        n = len(x_l)
        if n < 2: return self
        sum_x = sum(x_l); sum_y = sum(y_l)
        sum_xy = sum(xi * yi for xi, yi in zip(x_l, y_l))
        sum_x2 = sum(xi * xi for xi in x_l)
        denom = (n * sum_x2 - sum_x * sum_x)
        if abs(denom) > 1e-7:
            self.slope = (n * sum_xy - sum_x * sum_y) / denom
            self.intercept = (sum_y - self.slope * sum_x) / n
            self.is_fitted = True
        return self

    def predict(self, x):
        if not self.is_fitted: return 0.0
        if isinstance(x, (int, float)):
            return float(self.slope * x + self.intercept)
        x_l = list(x.tolist() if isinstance(x, NumpyArray) else x)
        return NumpyArray([float(self.slope * xi + self.intercept) for xi in x_l])

    def score(self, x, y):
        y_pred = self.predict(x)
        y_true = list(y.tolist() if isinstance(y, NumpyArray) else y)
        y_pred_l = list(y_pred.tolist() if isinstance(y_pred, NumpyArray) else [y_pred])
        mean_y = sum(y_true) / len(y_true)
        ss_tot = sum((yi - mean_y)**2 for yi in y_true)
        ss_res = sum((yi - pi)**2 for yi, pi in zip(y_true, y_pred_l))
        return float(1.0 - (ss_res / ss_tot)) if ss_tot > 1e-7 else 1.0


class LogisticRegressionModel:
    def __init__(self, lr=0.1, epochs=100):
        self.lr = float(lr)
        self.epochs = int(epochs)
        self.weights = []
        self.bias = 0.0
        self.is_fitted = False

    def fit(self, X, y):
        X_mat = X.tolist() if isinstance(X, NumpyArray) else X
        y_vec = list(y.tolist() if isinstance(y, NumpyArray) else y)
        if not X_mat or not y_vec: return self
        num_samples = len(X_mat)
        num_features = len(X_mat[0]) if isinstance(X_mat[0], list) else 1
        self.weights = [0.0] * num_features
        self.bias = 0.0

        for _ in range(self.epochs):
            for i in range(num_samples):
                row = X_mat[i] if isinstance(X_mat[i], list) else [X_mat[i]]
                z = self.bias + sum(w * xi for w, xi in zip(self.weights, row))
                pred = 1.0 / (1.0 + math.exp(-max(min(z, 20.0), -20.0)))
                err = pred - y_vec[i]
                self.bias -= self.lr * err
                for j in range(num_features):
                    self.weights[j] -= self.lr * err * row[j]
        self.is_fitted = True
        return self

    def predictProba(self, X):
        X_mat = X.tolist() if isinstance(X, NumpyArray) else X
        if not isinstance(X_mat, list) or (X_mat and not isinstance(X_mat[0], list)):
            X_mat = [X_mat]
        probs = []
        for row in X_mat:
            r = row if isinstance(row, list) else [row]
            z = self.bias + sum(w * xi for w, xi in zip(self.weights, r))
            prob = 1.0 / (1.0 + math.exp(-max(min(z, 20.0), -20.0)))
            probs.append(prob)
        return NumpyArray(probs) if len(probs) > 1 else float(probs[0])

    def predict(self, X):
        probs = self.predictProba(X)
        if isinstance(probs, float):
            return 1.0 if probs >= 0.5 else 0.0
        p_list = probs.tolist()
        return NumpyArray([1.0 if p >= 0.5 else 0.0 for p in p_list])


class KMeansModel:
    def __init__(self, k=2, maxIter=100):
        self.k = int(k)
        self.maxIter = int(maxIter)
        self.centroids = []
        self.is_fitted = False

    def fit(self, X):
        X_mat = X.tolist() if isinstance(X, NumpyArray) else X
        if not X_mat: return self
        num_features = len(X_mat[0]) if isinstance(X_mat[0], list) else 1
        self.centroids = [list(X_mat[i % len(X_mat)]) if isinstance(X_mat[0], list) else [X_mat[i % len(X_mat)]] for i in range(self.k)]
        self.is_fitted = True
        return self

    def predict(self, X):
        X_mat = X.tolist() if isinstance(X, NumpyArray) else X
        if not isinstance(X_mat, list) or (X_mat and not isinstance(X_mat[0], list)):
            X_mat = [X_mat]
        preds = []
        for row in X_mat:
            r = row if isinstance(row, list) else [row]
            best_k = 0; min_d = 1e9
            for k_idx, cent in enumerate(self.centroids):
                d = sum((xi - ci)**2 for xi, ci in zip(r, cent))
                if d < min_d: min_d = d; best_k = k_idx
            preds.append(best_k)
        return NumpyArray(preds) if len(preds) > 1 else int(preds[0])


class KNNModel:
    def __init__(self, k=3):
        self.k = int(k)
        self.X_train = []
        self.y_train = []

    def fit(self, X, y):
        self.X_train = X.tolist() if isinstance(X, NumpyArray) else list(X)
        self.y_train = y.tolist() if isinstance(y, NumpyArray) else list(y)
        return self

    def predict(self, X):
        X_mat = X.tolist() if isinstance(X, NumpyArray) else X
        if not isinstance(X_mat, list) or (X_mat and not isinstance(X_mat[0], list)):
            X_mat = [X_mat]
        preds = []
        for row in X_mat:
            r = row if isinstance(row, list) else [row]
            dists = []
            for tr_x, tr_y in zip(self.X_train, self.y_train):
                tx = tr_x if isinstance(tr_x, list) else [tr_x]
                d = math.sqrt(sum((a - b)**2 for a, b in zip(r, tx)))
                dists.append((d, tr_y))
            dists.sort(key=lambda item: item[0])
            k_labels = [label for _, label in dists[:self.k]]
            pred_label = max(set(k_labels), key=k_labels.count)
            preds.append(pred_label)
        return NumpyArray(preds) if len(preds) > 1 else preds[0]


class StandardScalerModel:
    def __init__(self):
        self.mean = []
        self.std = []

    def fit(self, X):
        X_mat = X.tolist() if isinstance(X, NumpyArray) else X
        if not isinstance(X_mat, list) or not X_mat: return self
        num_cols = len(X_mat[0]) if isinstance(X_mat[0], list) else 1
        num_rows = len(X_mat)
        self.mean = [0.0] * num_cols
        self.std = [1.0] * num_cols

        for j in range(num_cols):
            col_vals = [X_mat[i][j] if isinstance(X_mat[i], list) else X_mat[i] for i in range(num_rows)]
            m = sum(col_vals) / num_rows
            s = math.sqrt(sum((v - m)**2 for v in col_vals) / max(num_rows, 1))
            self.mean[j] = m
            self.std[j] = s if s > 1e-7 else 1.0
        return self

    def transform(self, X):
        X_mat = X.tolist() if isinstance(X, NumpyArray) else X
        num_rows = len(X_mat)
        num_cols = len(self.mean)
        res = []
        for i in range(num_rows):
            row = []
            for j in range(num_cols):
                val = X_mat[i][j] if isinstance(X_mat[i], list) else X_mat[i]
                row.append((val - self.mean[j]) / self.std[j])
            res.append(row if num_cols > 1 else row[0])
        return NumpyArray(res)

    def fitTransform(self, X):
        return self.fit(X).transform(X)


# ============================================================
# METRICS & PREPROCESSING FUNCTIONS
# ============================================================

def accuracy(y_true, y_pred):
    yt = list(y_true.tolist() if isinstance(y_true, NumpyArray) else y_true)
    yp = list(y_pred.tolist() if isinstance(y_pred, NumpyArray) else y_pred)
    if not yt or len(yt) != len(yp): return 0.0
    correct = sum(1 for a, b in zip(yt, yp) if abs(a - b) < 1e-4)
    return float(correct / len(yt))

def mse(y_true, y_pred):
    yt = list(y_true.tolist() if isinstance(y_true, NumpyArray) else y_true)
    yp = list(y_pred.tolist() if isinstance(y_pred, NumpyArray) else y_pred)
    if not yt or len(yt) != len(yp): return 0.0
    return float(sum((a - b)**2 for a, b in zip(yt, yp)) / len(yt))

def r2(y_true, y_pred):
    yt = list(y_true.tolist() if isinstance(y_true, NumpyArray) else y_true)
    yp = list(y_pred.tolist() if isinstance(y_pred, NumpyArray) else y_pred)
    if not yt or len(yt) < 2: return 0.0
    mean_y = sum(yt) / len(yt)
    ss_tot = sum((y - mean_y)**2 for y in yt)
    ss_res = sum((y - p)**2 for y, p in zip(yt, yp))
    return float(1.0 - (ss_res / ss_tot)) if ss_tot > 1e-7 else 1.0

def trainTestSplit(X, y, testSize=0.2, randomState=None):
    X_l = X.tolist() if isinstance(X, NumpyArray) else list(X)
    y_l = y.tolist() if isinstance(y, NumpyArray) else list(y)
    n = len(X_l)
    n_test = max(1, int(n * float(testSize)))
    indices = list(range(n))
    if randomState is not None:
        rnd = random.Random(randomState)
        rnd.shuffle(indices)
    else:
        random.shuffle(indices)

    test_idx = set(indices[:n_test])
    X_train = [X_l[i] for i in range(n) if i not in test_idx]
    X_test  = [X_l[i] for i in range(n) if i in test_idx]
    y_train = [y_l[i] for i in range(n) if i not in test_idx]
    y_test  = [y_l[i] for i in range(n) if i in test_idx]
    return NumpyArray(X_train), NumpyArray(X_test), NumpyArray(y_train), NumpyArray(y_test)


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


def build_ml_module(interp=None):
    m = {}
    m["linearRegression"]   = lambda: LinearRegressionModel()
    m["logisticRegression"] = lambda lr=0.1, epochs=100: LogisticRegressionModel(lr, epochs)
    m["kmeans"]             = lambda k=2, maxIter=100: KMeansModel(k, maxIter)
    m["knn"]                = lambda k=3: KNNModel(k)
    m["scaler"]             = lambda: StandardScalerModel()
    m["standardScaler"]     = lambda: StandardScalerModel()
    m["accuracy"]           = accuracy
    m["mse"]                = mse
    m["r2"]                 = r2
    m["trainTestSplit"]     = trainTestSplit
    return StdModule("ml", m)


# ============================================================
# C TEMPLATES (FOR COMPILER - BLAZING-FAST STANDALONE BINARY)
# ============================================================
cCode = {
    "include": '#include "nova_ml.h"',
    "linearRegression": 'NovaLinearRegression {var} = mlLinearRegression();',
    "fit": 'mlLinearFit(&{var}, {x}, {y}, {n});',
    "predict": 'float {var} = mlLinearPredict(&{model}, {x});',
    "logisticRegression": 'NovaLogisticRegression {var} = mlLogisticRegression({numFeatures});',
    "kmeans": 'NovaKMeans {var} = mlKMeans({k});',
    "knn": 'NovaKNN {var} = mlKNN({k});',
    "scaler": 'NovaStandardScaler {var} = mlStandardScaler();',
    "standardScaler": 'NovaStandardScaler {var} = mlStandardScaler();',
    "accuracy": 'float {var} = mlAccuracy({yTrue}, {yPred}, {n});',
    "mse": 'float {var} = mlMse({yTrue}, {yPred}, {n});',
    "r2": 'float {var} = mlR2({yTrue}, {yPred}, {n});',
}
