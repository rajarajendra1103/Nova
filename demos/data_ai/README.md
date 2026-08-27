# 🤖 Nova Data Science & AI / ML Demos

This directory contains working Nova scientific computing, data manipulation, and machine learning demos.

---

## 📁 Demo Files & Features

| File | Description | Key Modules |
| :--- | :--- | :--- |
| [`test_v2_numpy_pandas.nova`](./test_v2_numpy_pandas.nova) | **NumPy & Pandas Data Science**: N-dimensional array creation, vector operations, mean, sum, dot product, and Pandas DataFrame group/aggregation. | `numpy`, `pandas` |
| [`test_scipy_ml.nova`](./test_scipy_ml.nova) | **SciPy & Machine Learning**: Linear regression, KMeans clustering, gradient descent, and neural network dense layers (`ai.dense`, `ai.forward`). | `scipy`, `ml`, `sklearn`, `ai` |

---

## 🚀 How to Run

### Run with the Nova Interpreter:
```powershell
# 1. NumPy Computing & Pandas DataFrames
python nova_interpreter.py demos/data_ai/test_v2_numpy_pandas.nova

# 2. SciPy & Machine Learning Algorithms
python nova_interpreter.py demos/data_ai/test_scipy_ml.nova
```

### Compile to Standalone Native Binary:
```powershell
python nova_compiler.py demos/data_ai/test_scipy_ml.nova
```
