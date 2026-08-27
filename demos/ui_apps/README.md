# 📱 Nova UI & Desktop/Mobile App Demos

This directory contains full, working Nova UI demos showcasing responsive layouts, forms, authentication screens, analytics dashboards, and interactive widgets.

---

## 📁 Demo Files & Features

| File | Description | Key Modules |
| :--- | :--- | :--- |
| [`form.nova`](./form.nova) | **User Registration Form**: Input fields, validation, dropdown selection, checkboxes, submit buttons. | `ui`, `app` |
| [`dashboard.nova`](./dashboard.nova) | **Analytics & KPI Dashboard**: Multi-column metric cards, responsive stats, chart placeholders. | `ui`, `layout` |
| [`login.nova`](./login.nova) | **Modern Login Screen**: Password inputs, social login buttons, stylized container cards. | `ui`, `app` |
| [`todo.nova`](./todo.nova) | **Interactive Todo Application**: Dynamic task adding, item list rendering, delete actions. | `ui`, `app` |
| [`layout.nova`](./layout.nova) | **Responsive Flex & Grid Layouts**: Responsive navigation bars, sidebar drawers, multi-column grids. | `ui`, `layout` |
| [`test_v2_app_unified.nova`](./test_v2_app_unified.nova) | **Direct GPU UI & App Engine**: 120 FPS frame ticks, multi-platform viewport scaling (Mobile/Tablet/Desktop). | `app`, `ui`, `layout`, `mem` |

---

## 🚀 How to Run

### Run with the Nova Interpreter:
```powershell
# 1. User Registration Form Demo
python nova_interpreter.py demos/ui_apps/form.nova

# 2. Analytics & KPI Dashboard Demo
python nova_interpreter.py demos/ui_apps/dashboard.nova

# 3. Modern Login Screen Demo
python nova_interpreter.py demos/ui_apps/login.nova

# 4. Interactive Todo App Demo
python nova_interpreter.py demos/ui_apps/todo.nova

# 5. Responsive Layouts Demo
python nova_interpreter.py demos/ui_apps/layout.nova

# 6. Direct GPU UI & Multi-Platform Scaling
python nova_interpreter.py demos/ui_apps/test_v2_app_unified.nova
```
