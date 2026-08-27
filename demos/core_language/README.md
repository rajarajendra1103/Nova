# ⚡ Nova Core Language & Standard Library Demos

This directory contains demos demonstrating Nova's core language syntax, object-oriented programming, standard library modules, and compiler verification pipelines.

---

## 📁 Demo Files & Features

| File | Description | Key Modules |
| :--- | :--- | :--- |
| [`test_v14.nova`](./test_v14.nova) | **Core Language Syntax**: String interpolation (`{var}`), OOP Classes, static members, inheritance, getters/setters, lambdas, closures, and collections. | Core Syntax |
| [`test_v15_stdlib.nova`](./test_v15_stdlib.nova) | **Standard Library Suite**: Math functions, string manipulation, list algorithms, set operations, file I/O, random generators, time, and JSON parsing. | `math`, `string`, `list`, `set`, `file`, `random`, `time`, `json` |
| [`test_all_libs_unified.nova`](./test_all_libs_unified.nova) | **Master Unified Integration**: Cross-library integration verifying all standard modules executing in harmony. | All standard modules |
| [`test_v2_full_pipeline.nova`](./test_v2_full_pipeline.nova) | **Compiler Pipeline Verification**: Full pass through Lexer -> Parser -> Semantic Checker -> Bytecode Interpreter / C Code Generator. | Compiler Pipeline |

---

## 🚀 How to Run

### Run with the Nova Interpreter:
```powershell
# 1. Core Language Features (OOP, Lambdas, Strings)
python nova_interpreter.py demos/core_language/test_v14.nova

# 2. Standard Library Modules
python nova_interpreter.py demos/core_language/test_v15_stdlib.nova

# 3. Master Integration Test
python nova_interpreter.py demos/core_language/test_all_libs_unified.nova

# 4. Compiler Pipeline
python nova_interpreter.py demos/core_language/test_v2_full_pipeline.nova
```
