# 🌐 Nova Backend & Networking Demos

This directory contains working Nova backend and networking demos covering REST APIs, Real-Time WebSockets, SQLite database CRUD, JWT Authentication, and Mobile Native controls.

---

## 📁 Demo Files & Features

| File | Description | Key Modules |
| :--- | :--- | :--- |
| [`test_v16_web.nova`](./test_v16_web.nova) | **Full-Stack Web & REST API**: HTTP server routes (`GET`/`POST`/`PUT`/`DELETE`), SQLite DB queries, sorting, bcrypt password hashing, JWT token issue/verify, and Async HTTP requests. | `server`, `http`, `db`, `auth`, `env` |
| [`test_mobile_and_ws.nova`](./test_mobile_and_ws.nova) | **Real-Time WebSockets & Mobile UI**: Duplex WebSocket server, room joining & broadcasting, mobile native layout (AppBar, BottomNav, SafeArea, Haptics, Orientation). | `ws`, `ui`, `app`, `server` |

---

## 🚀 How to Run

### Run with the Nova Interpreter:
```powershell
# 1. Full-Stack Web, REST API & Database
python nova_interpreter.py demos/backend/test_v16_web.nova

# 2. Real-Time WebSockets & Mobile App Integration
python nova_interpreter.py demos/backend/test_mobile_and_ws.nova
```

### Compile to Standalone Native Binary:
```powershell
python nova_compiler.py demos/backend/test_v16_web.nova
```
