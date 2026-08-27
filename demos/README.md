# 🌟 Nova Working Demos & Test Suites

Welcome to the **Nova Demos Directory**! All runnable demos and verification test suites have been organized into clear, categorized subdirectories.

---

## 📁 Demo Categories & Subfolders

### 1. 🎮 [`games/`](./games/)
Full-featured 2D and 3D game demos:
- [`test_game_engine_advanced.nova`](./games/test_game_engine_advanced.nova): 3D Audio, Multiplayer UDP & RPCs, Skeletal Animation, ECS.
- [`test_v2_game_unified.nova`](./games/test_v2_game_unified.nova): 2D/3D GPU Rendering, Rigid-body Physics, Keyboard/Mouse Input, Assets.
- [`mygame.nova`](./games/mygame.nova): 3D Action RPG Game with AI inference and 120 FPS game loop.

### 2. 🌐 [`backend/`](./backend/)
Full-Stack Web, REST APIs, and Real-Time Networking:
- [`test_v16_web.nova`](./backend/test_v16_web.nova): REST API Server, SQLite DB CRUD, JWT Authentication, Async HTTP.
- [`test_mobile_and_ws.nova`](./backend/test_mobile_and_ws.nova): Real-Time WebSockets (rooms, broadcasting) & Mobile UI (AppBar, BottomNav, Haptics).

### 3. 📱 [`ui_apps/`](./ui_apps/)
Cross-platform Desktop and Mobile UI:
- [`form.nova`](./ui_apps/form.nova): User Registration Form with full validation and controls.
- [`dashboard.nova`](./ui_apps/dashboard.nova): Analytics & KPI Dashboard with stats and metric cards.
- [`login.nova`](./ui_apps/login.nova): Modern Authentication Screen with password inputs and social buttons.
- [`todo.nova`](./ui_apps/todo.nova): Interactive Todo List Application with add/delete task actions.
- [`layout.nova`](./ui_apps/layout.nova): Responsive Flex & Grid Layouts with sidebars and navigation bars.
- [`test_v2_app_unified.nova`](./ui_apps/test_v2_app_unified.nova): Responsive Direct GPU UI, Flex/Grid layouts, Mobile/Tablet/Desktop screen scaling.

### 4. 🤖 [`data_ai/`](./data_ai/)
Scientific computing, matrix math, and machine learning:
- [`test_v2_numpy_pandas.nova`](./data_ai/test_v2_numpy_pandas.nova): NumPy array math, Pandas DataFrames & grouping.
- [`test_scipy_ml.nova`](./data_ai/test_scipy_ml.nova): SciPy optimization, Linear Regression, KMeans, Neural Network Dense Layers.

### 5. ⚡ [`core_language/`](./core_language/)
Core syntax, OOP, standard libraries, and compiler validation:
- [`test_v14.nova`](./core_language/test_v14.nova): Classes, Inheritance, Getters/Setters, Lambdas, String Interpolation.
- [`test_v15_stdlib.nova`](./core_language/test_v15_stdlib.nova): Standard Library (Math, Strings, Lists, Sets, File I/O, JSON, Random).
- [`test_all_libs_unified.nova`](./core_language/test_all_libs_unified.nova): Master sanity test across all Nova modules.
- [`test_v2_full_pipeline.nova`](./core_language/test_v2_full_pipeline.nova): Complete Compiler / Interpreter pipeline test.

---

## 🚀 Quick Execution Guide

Run any demo directly with the **Nova Interpreter**:
```powershell
python nova_interpreter.py demos/games/test_game_engine_advanced.nova
python nova_interpreter.py demos/ui_apps/dashboard.nova
python nova_interpreter.py demos/backend/test_v16_web.nova
python nova_interpreter.py demos/data_ai/test_scipy_ml.nova
python nova_interpreter.py demos/core_language/test_v15_stdlib.nova
```
