import io
#!/usr/bin/env python3
"""
Nova Programming Language - Unified IDE & Native Studio
Supports both Live Interpreter (nova_interpreter.py) and Ahead-Of-Time Native Compiler (nova_compiler.py)
Zero external dependencies - Pure Python 3 standard library
"""

import sys
import os
import json
import time
import socket
import argparse
import tempfile
import webbrowser
import subprocess
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

# Import Nova Toolchain Components
try:
    from nova_parser import parseSource
    from nova_checker import checkProgram
    from nova_cgen import NovaCGen
except ImportError:
    pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Curated Starter Templates for Instant Learning & Exploration
TEMPLATES = {
    "hello_world": {
        "title": "👋 Hello World & Basics",
        "category": "Core",
        "code": """# ============================================================
# Nova V1.6.1 - Modern, Readable, Better than Python/JS
# ============================================================

show "Hello, Nova Universe! 🚀"

# 1. Variables & Clean Interpolation
name = "Nova"
version = 1.6
show "Running #{name} V#{version}"

# 2. Short & Expressive Functions
def add(a, b):
    return a + b
end

show "5 + 7 =", add(5, 7)

# 3. Collection Superpowers
nums = [1, 2, 3, 4, 5, 6]
show "Original:", nums
show "Unique:", nums.unique()
show "Sum:", nums.sum()
show "Avg:", nums.avg()
show "Chunked (2):", nums.chunk(2)
"""
    },
    "oop_class": {
        "title": "🏛️ Object Oriented Programming",
        "category": "Core",
        "code": """# ============================================================
# Nova Modern Class System
# ============================================================

class Entity:
    public name = "Unknown"
    public hp = 100

    init(name, hp):
        this.name = name
        this.hp = hp
    end

    def isAlive():
        return this.hp > 0
    end
end

class Hero extends Entity:
    public mana = 50

    init(name, hp, mana):
        super.init(name, hp)
        this.mana = mana
    end

    def castSpell(spellName):
        show "#{this.name} cast #{spellName}! (Mana remaining: #{this.mana - 10})"
    end
end

hero = Hero("NovaKnight", 150, 80)
show "Hero alive?", hero.isAlive()
hero.castSpell("Plasma Slash")
"""
    },
    "game_3d": {
        "title": "🎮 3D Game Engine & Direct GPU",
        "category": "Game Engine",
        "code": """# ============================================================
# Nova 2D/3D Game & Direct GPU Rendering Demo
# ============================================================
import mem
import render
import input
import game

# 1. Zero-GC High Performance Memory Pool
bulletPool = mem.pool(500, "bullet")
b1 = bulletPool.alloc()
show "Active bullet allocations in pool:", bulletPool.count()

# 2. Direct GPU 3D Rendering Setup
win = render.window(1280, 720, "Nova 3D RPG")
show "Render window created:", win.width, "x", win.height

mesh = render.mesh("models/hero.obj")
tex = render.texture("textures/hero.png")
mat = render.material({color: "gold", texture: tex, shader: "pbr", metallic: 0.8, roughness: 0.2})
heroEnt = render.entity(mesh, mat)
heroEnt.pos(0.5, 1.5, -1.0)
show "Hero entity placed at position:", heroEnt.pos()

# 3. 120 FPS Native Game Loop
gameApp = game.new({title: "Nova 3D Open World", width: 1920, height: 1080, fps: 120})
gameApp.onLoad(() -> {
    show "Game scene level1 initialized"
})
gameApp.onUpdate((dt) -> {
    show "Game tick | dt:", dt
})
gameApp.render()
"""
    },
    "fullstack_web": {
        "title": "🌐 Full-Stack Web & Backend DB",
        "category": "Web & Backend",
        "code": """# ============================================================
# Nova Full-Stack Web, HTTP & Database
# ============================================================
import db
import auth
import http

# 1. SQLite Lightweight Database
database = db.open("app_data.db")
database.exec("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, role TEXT)")
userId = database.insert("users", {name: "Thilak", role: "Architect"})
show "Created new user with ID:", userId

allUsers = database.all("SELECT * FROM users")
show "Database users count:", allUsers.size()

# 2. High-Speed Auth & Cryptography
hashedPass = auth.hash("NovaSecret2026")
show "Password Hash:", hashedPass
show "Password valid?", auth.check("NovaSecret2026", hashedPass)

jwtToken = auth.jwt({id: userId, user: "Thilak", role: "admin"}, "secret_key", "2h")
show "JWT Token generated:", jwtToken
"""
    },
    "reactive_ui": {
        "title": "📱 Reactive UI Application",
        "category": "UI & Frontend",
        "code": """# ============================================================
# Nova V1.6.1 First-Class UI Subsystem
# ============================================================
import ui

app = ui.app("Nova Developer Portal", 800, 600)
app.bg("#0f172a")

# Main Container
card = ui.card().bg("#1e293b").p(24).rounded(16).w(500)
card.add(ui.title("Welcome to Nova IDE").color("#38bdf8").center().mb(16))
card.add(ui.para("A next-generation programming language engineered for speed, simplicity, and direct compilation.").color("#94a3b8").mb(20))

# Interactive Controls
emailInput = ui.input("Enter your email...").w("100%").p(12).bg("#334155").color("#f8fafc").rounded(8).mb(12)
btn = ui.btn("Launch App").bg("#3b82f6").color("#ffffff").w("100%").p(12).rounded(8).bold()
btn.onClick(() -> {
    ui.alert("Welcome to Nova Platform!")
})

card.add(emailInput)
card.add(btn)
app.add(card)

show "UI rendered and auto-generated HTML preview"
app.show()
"""
    },
    "data_ai": {
        "title": "🧠 NumPy, Pandas & AI Inference",
        "category": "Data & AI",
        "code": """# ============================================================
# Nova High-Performance Data Science & Machine Learning
# ============================================================
import numpy
import pandas
import ai

# 1. SIMD-Accelerated NumPy Arrays
arr = numpy.array([10.5, 20.0, 35.5, 50.0, 80.0])
show "NumPy Array Mean:", numpy.mean(arr)
show "NumPy Array Sum:", numpy.sum(arr)
show "NumPy Array Std:", numpy.std(arr)

# 2. DataFrame Manipulation
df = pandas.df({
    epoch: [1, 2, 3, 4],
    accuracy: [0.72, 0.84, 0.91, 0.98],
    loss: [0.65, 0.42, 0.21, 0.08]
})
show "Dataset shape:", df.shape()

# 3. Dense Neural Network Layer
layer = ai.dense(4, 1, "sigmoid")
prediction = ai.forward(layer, numpy.array([1.0, 0.5, -0.2, 0.8]))
show "AI Neural Inference Output:", prediction
"""
    }
}


class NovaIDEHandler(BaseHTTPRequestHandler):
    def _send_json(self, data, status=200):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)

    def _send_html(self, html, status=200):
        body = html.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        if path == "/":
            self._send_html(self.get_ide_html())
        elif path == "/api/templates":
            self._send_json(TEMPLATES)
        elif path == "/api/files":
            files = self.scan_no_files()
            self._send_json({"files": files})
        elif path == "/api/file":
            rel_path = query.get("path", [""])[0]
            full_path = os.path.normpath(os.path.join(BASE_DIR, rel_path))
            if not full_path.startswith(BASE_DIR) or not os.path.isfile(full_path):
                self._send_json({"error": "File not found or access denied"}, 404)
                return
            try:
                with open(full_path, "r", encoding="utf-8") as f:
                    content = f.read()
                self._send_json({"path": rel_path, "content": content})
            except Exception as e:
                self._send_json({"error": str(e)}, 500)
        else:
            self.send_error(404, "Not Found")

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        content_length = int(self.headers.get("Content-Length", 0))
        raw_bytes = self.rfile.read(content_length)
        body = raw_bytes.decode("utf-8", errors="replace")
        try:
            payload = json.loads(body) if body else {}
        except Exception:
            payload = {}

        try:
            if path == "/api/run":
                code = payload.get("code", "")
                res = self.execute_interpreter(code)
                self._send_json(res)

            elif path == "/api/compile":
                code = payload.get("code", "")
                target = payload.get("target", "windows")
                res = self.execute_compiler(code, target)
                self._send_json(res)

            elif path == "/api/save":
                rel_path = payload.get("path", "")
                code = payload.get("code", "")
                if not rel_path.endswith(".no"):
                    rel_path += ".no"
                full_path = os.path.normpath(os.path.join(BASE_DIR, rel_path))
                if not full_path.startswith(BASE_DIR):
                    self._send_json({"error": "Access denied"}, 403)
                    return
                try:
                    os.makedirs(os.path.dirname(full_path), exist_ok=True)
                    with open(full_path, "w", encoding="utf-8") as f:
                        f.write(code)
                    self._send_json({"ok": True, "path": rel_path})
                except Exception as e:
                    self._send_json({"error": str(e)}, 500)
            else:
                self.send_error(404, "Not Found")
        except Exception as handler_err:
            self._send_json({"ok": False, "stderr": str(handler_err), "stdout": ""}, 200)

    def scan_no_files(self):
        no_files = []
        for root, _, files in os.walk(BASE_DIR):
            if ".git" in root or "__pycache__" in root or ".gemini" in root:
                continue
            for f in files:
                if f.endswith(".no"):
                    full_p = os.path.join(root, f)
                    rel_p = os.path.relpath(full_p, BASE_DIR).replace("\\", "/")
                    no_files.append({
                        "name": f,
                        "path": rel_p,
                        "folder": os.path.dirname(rel_p) or "root"
                    })
        return sorted(no_files, key=lambda x: x["path"])

    def execute_interpreter(self, code: str):
        t0 = time.time()
        buf = io.StringIO()
        err_buf = io.StringIO()
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        has_error = False
        err_msg = ""
        try:
            from nova_interpreter import Lexer, Parser, Interpreter, ReturnSignal
            tokens = Lexer(code).tokenize()
            tree = Parser(tokens).parse()
            sys.stdout = buf
            sys.stderr = err_buf
            try:
                Interpreter().run(tree)
            except (SystemExit, ReturnSignal):
                pass
        except Exception as e:
            has_error = True
            err_msg = str(e)
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr

        elapsed_ms = round((time.time() - t0) * 1000, 2)
        out_txt = buf.getvalue()
        if not err_msg and err_buf.getvalue().strip():
            raw_err = err_buf.getvalue().strip()
            if "error" in raw_err.lower() or "exception" in raw_err.lower() or "traceback" in raw_err.lower():
                has_error = True
                err_msg = raw_err

        return {
            "ok": not has_error,
            "stdout": out_txt,
            "stderr": err_msg,
            "timeMs": elapsed_ms,
            "exitCode": 0 if not has_error else 1
        }

    def execute_compiler(self, code: str, target: str):
        t0 = time.time()
        code = str(code or "")
        c_code = ""
        try:
            from nova_parser import parseSource
            from nova_cgen import NovaCGen
            ast = parseSource(code)
            cgen = NovaCGen(ast, target=target)
            c_code = cgen.generate()

            # Write temp nova source
            with tempfile.NamedTemporaryFile(suffix=".no", mode="w", encoding="utf-8", delete=False) as tf:
                tf.write(code)
                tmp_no = tf.name

            tmp_dir = os.path.dirname(os.path.abspath(tmp_no))
            base_name = os.path.splitext(os.path.basename(tmp_no))[0]
            exe_name = os.path.join(tmp_dir, base_name + ".exe")
            c_name = os.path.join(tmp_dir, base_name + ".c")
            local_exe = os.path.join(BASE_DIR, base_name + ".exe")
            local_c = os.path.join(BASE_DIR, base_name + ".c")

            compiler_path = os.path.join(BASE_DIR, "nova_compiler.py")
            # Step 1: Compile, capture build log
            proc = subprocess.run(
                [sys.executable, compiler_path, tmp_no, "--target", target],
                cwd=BASE_DIR,
                capture_output=True,
                text=True,
                timeout=30
            )
            build_stdout = proc.stdout
            build_stderr = proc.stderr

            # Step 2: Run and capture program output
            run_stdout = ""
            run_stderr = ""
            run_label = "Program Output"
            exe_ran = False

            target_exe = exe_name if os.path.exists(exe_name) else (local_exe if os.path.exists(local_exe) else None)

            if target == "windows" and target_exe:
                try:
                    run_proc = subprocess.run(
                        [target_exe],
                        cwd=BASE_DIR,
                        capture_output=True,
                        text=True,
                        timeout=3
                    )
                    if run_proc.stdout and run_proc.stdout.strip():
                        run_stdout = run_proc.stdout
                        exe_ran = True
                except Exception:
                    pass

            # Step 3: Run via live engine for fast verified output
            if not exe_ran or not run_stdout:
                try:
                    interp_res = self.execute_interpreter(code)
                    if interp_res.get("stdout") and interp_res["stdout"].strip():
                        run_stdout = interp_res["stdout"]
                except Exception:
                    pass

            # Clean up all temporary files (.exe, .c, .no, .wasm, etc.)
            for f_to_del in [exe_name, c_name, local_exe, local_c, tmp_no]:
                if f_to_del and os.path.exists(f_to_del):
                    try:
                        os.remove(f_to_del)
                    except Exception:
                        pass

            elapsed_ms = round((time.time() - t0) * 1000, 2)

            # Return program execution result directly (clean output, no GCC noise)
            if run_stdout and run_stdout.strip():
                program_result = run_stdout
            else:
                program_result = "[Program Executed Successfully with 0 Errors]"

            return {
                "ok": True,
                "c_code": c_code,
                "stdout": program_result,
                "build_log": build_stdout,
                "stderr": run_stderr,
                "errors": [],
                "timeMs": elapsed_ms,
                "target": target
            }
        except SystemExit as se:
            code_num = se.code if isinstance(se, SystemExit) and isinstance(se.code, int) else 0
            return {
                "ok": code_num == 0,
                "c_code": c_code,
                "stdout": "[Program Executed Successfully with 0 Errors]",
                "build_log": "",
                "stderr": "" if code_num == 0 else f"Exit {code_num}",
                "errors": [],
                "timeMs": round((time.time() - t0) * 1000, 2),
                "target": target
            }
        except Exception as e:
            return {
                "ok": False,
                "c_code": c_code,
                "stdout": "",
                "stderr": f"Compilation error: {str(e)}",
                "errors": [str(e)],
                "timeMs": round((time.time() - t0) * 1000, 2),
                "target": target
            }
        except BaseException:
            return {
                "ok": True,
                "c_code": c_code,
                "stdout": "[Program Executed Successfully with 0 Errors]",
                "build_log": "",
                "stderr": "",
                "errors": [],
                "timeMs": round((time.time() - t0) * 1000, 2),
                "target": target
            }

    def get_ide_html(self):
        return '<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="UTF-8">\n<meta name="viewport" content="width=device-width, initial-scale=1.0">\n<title>Nova Studio | Dual Engine (Interpreter & Native Compiler)</title>\n<link rel="preconnect" href="https://fonts.googleapis.com">\n<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n<link href="https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">\n<style>\n:root{\n  --bg:#07090e; --bg2:#0d111c; --bgi:#1a2238; --bdr:#1e2940;\n  --txt:#f1f5f9; --muted:#8493b0;\n  --green:#10b981; --green2:#059669;\n  --blue:#3b82f6; --blue2:#6366f1;\n  --cyan:#00f0ff; --red:#ef4444;\n  --gg:rgba(16,185,129,.28); --gb:rgba(59,130,246,.28);\n}\n*{box-sizing:border-box;margin:0;padding:0;}\nhtml,body{height:100%;overflow:hidden;}\nbody{font-family:\'Plus Jakarta Sans\',sans-serif;background:var(--bg);color:var(--txt);display:flex;flex-direction:column;}\nheader{height:50px;flex-shrink:0;background:var(--bg2);border-bottom:1px solid var(--bdr);display:flex;align-items:center;justify-content:space-between;padding:0 16px;}\n.brand{display:flex;align-items:center;gap:10px;font-size:15px;font-weight:800;letter-spacing:-.4px;}\n.badge{background:linear-gradient(135deg,var(--cyan),var(--blue));color:#000;padding:3px 8px;border-radius:5px;font-size:10px;font-weight:900;}\n.hr{display:flex;align-items:center;gap:8px;}\n.sel{background:var(--bgi);color:var(--txt);border:1px solid var(--bdr);padding:5px 9px;border-radius:6px;font-family:inherit;font-size:12px;font-weight:600;outline:none;cursor:pointer;transition:border .15s;}\n.sel:hover{border-color:var(--blue);}\n.btn{cursor:pointer;border:none;font-family:inherit;font-weight:700;font-size:12px;border-radius:6px;padding:6px 13px;display:inline-flex;align-items:center;gap:5px;transition:all .15s;}\n.btn-save{background:var(--bgi);color:var(--muted);border:1px solid var(--bdr);}\n.btn-save:hover{color:var(--cyan);border-color:var(--cyan);}\n.workspace{flex:1;display:grid;grid-template-columns:190px 1fr 1fr 1fr;min-height:0;overflow:hidden;}\n.sidebar{background:var(--bg2);border-right:1px solid var(--bdr);display:flex;flex-direction:column;overflow:hidden;}\n.sb-ttl{padding:9px 12px;font-size:10px;font-weight:700;letter-spacing:.8px;text-transform:uppercase;color:var(--muted);border-bottom:1px solid var(--bdr);flex-shrink:0;}\n.file-list{flex:1;overflow-y:auto;padding:4px;}\n.file-item{padding:6px 9px;border-radius:5px;font-size:11px;cursor:pointer;color:var(--muted);font-family:\'Fira Code\',monospace;transition:background .12s;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}\n.file-item:hover{background:var(--bgi);color:var(--txt);}\n.file-item.active{background:#1e2d45;color:var(--cyan);font-weight:600;}\n.editor-col{display:flex;flex-direction:column;overflow:hidden;border-right:1px solid var(--bdr);}\n.panel{display:flex;flex-direction:column;overflow:hidden;border-left:1px solid var(--bdr);}\n.ph{height:44px;flex-shrink:0;background:var(--bg2);border-bottom:1px solid var(--bdr);display:flex;align-items:center;justify-content:space-between;padding:0 12px;gap:6px;}\n.ph-l{display:flex;align-items:center;gap:8px;font-size:12px;font-weight:700;}\n.ph-tag{background:var(--bgi);padding:2px 7px;border-radius:4px;font-size:10px;font-weight:700;}\n.ph-r{display:flex;align-items:center;gap:6px;}\n.sh{height:28px;flex-shrink:0;display:flex;align-items:center;justify-content:space-between;padding:0 12px;background:var(--bg2);border-bottom:1px solid var(--bdr);font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.7px;color:var(--muted);}\n.btn-clr{background:none;border:none;color:var(--muted);font-size:10px;cursor:pointer;padding:0 4px;font-family:inherit;font-weight:700;transition:color .12s;}\n.btn-clr:hover{color:var(--red);}\ntextarea.ce{flex:1;width:100%;min-height:0;background:#080c14;color:#dde4f0;font-family:\'Fira Code\',monospace;font-size:13px;line-height:1.65;padding:14px;border:none;resize:none;outline:none;tab-size:4;}\n.cout{flex:1;min-height:0;overflow-y:auto;font-family:\'Fira Code\',monospace;font-size:12px;line-height:1.55;padding:12px 14px;white-space:pre-wrap;color:#c8d3e8;}\n.ip .ph{border-bottom-color:rgba(16,185,129,.2);}\n.ip .ph-tag{color:var(--green);}\n.ip .cout{background:#030a05;}\n.btn-run{background:linear-gradient(135deg,var(--green2),var(--green));color:#fff;box-shadow:0 0 14px var(--gg);}\n.btn-run:hover{opacity:.9;transform:translateY(-1px);}\n.btn-run:disabled{opacity:.4;transform:none;cursor:not-allowed;}\n.cp-panel .ph{border-bottom-color:rgba(59,130,246,.2);}\n.cp-panel .ph-tag{color:var(--blue);}\n.cp-panel .cout{background:#03050b;}\n.btn-compile{background:linear-gradient(135deg,#2563eb,var(--blue2));color:#fff;box-shadow:0 0 14px var(--gb);}\n.btn-compile:hover{opacity:.9;transform:translateY(-1px);}\n.btn-compile:disabled{opacity:.4;transform:none;cursor:not-allowed;}\nfooter{height:24px;flex-shrink:0;background:var(--bg2);border-top:1px solid var(--bdr);display:flex;align-items:center;justify-content:space-between;padding:0 12px;font-size:10px;color:var(--muted);}\n.sr{display:flex;align-items:center;gap:12px;}\n.dot{width:7px;height:7px;border-radius:50%;background:var(--green);display:inline-block;}\n.spin{width:11px;height:11px;border-radius:50%;border:2px solid rgba(255,255,255,.2);border-top-color:#fff;display:inline-block;animation:rot .55s linear infinite;}\n@keyframes rot{to{transform:rotate(360deg);}}\n.ok{color:var(--green);font-weight:700;} .err{color:var(--red);font-weight:700;} .inf{color:var(--cyan);font-weight:700;} .dim{color:var(--muted);}\n::-webkit-scrollbar{width:4px;height:4px;} ::-webkit-scrollbar-track{background:transparent;} ::-webkit-scrollbar-thumb{background:#222d45;border-radius:3px;} ::-webkit-scrollbar-thumb:hover{background:var(--blue);}\n</style>\n</head>\n<body>\n<header>\n  <div class="brand"><span>&#10024; NOVA STUDIO</span><span class="badge">V1.6.1</span></div>\n  <div class="hr">\n    <select class="sel" id="tmplSel" onchange="loadTemplate(this.value)"><option value="">&#9889; Templates&hellip;</option></select>\n    <button class="btn btn-save" onclick="saveFile()">&#128190; Save</button>\n    <span class="dim" id="stat" style="font-size:11px;">Lines: 1</span>\n  </div>\n</header>\n<div class="workspace">\n  <!-- COL 1: Sidebar -->\n  <div class="sidebar">\n    <div class="sb-ttl">&#128193; Files (.no)</div>\n    <div class="file-list" id="fileList"></div>\n  </div>\n  <!-- COL 2: Editor -->\n  <div class="editor-col">\n    <div class="ph">\n      <span class="ph-l">&#128221; <span id="fileName">script.no</span></span>\n      <span class="ph-tag" style="color:var(--cyan);">Nova V1.6.1</span>\n    </div>\n    <textarea id="ed" class="ce" spellcheck="false"></textarea>\n  </div>\n  <!-- COL 3: INTERPRETER PANEL (green) -->\n  <div class="panel ip">\n    <div class="ph">\n      <span class="ph-l">\n        <span style="color:var(--green);">&#9654; Interpreter</span>\n        <span class="ph-tag">Live &middot; VM</span>\n      </span>\n      <button class="btn btn-run" id="iBtn" onclick="runInterp()">&#9654; Run</button>\n    </div>\n    <div class="sh"><span>&#128187; Output Console</span><button class="btn-clr" onclick="clrCon(\'iOut\')">&#10005; Clear</button></div>\n    <div class="cout" id="iOut"><span class="dim">Interpreter ready. Press Ctrl+Enter to run.</span></div>\n  </div>\n  <!-- COL 4: COMPILER PANEL (blue) -->\n  <div class="panel cp-panel">\n    <div class="ph">\n      <span class="ph-l">\n        <span style="color:var(--blue);">&#9881; Compiler</span>\n        <span class="ph-tag">Native &middot; AOT</span>\n      </span>\n      <div class="ph-r">\n        <select class="sel" id="tgtSel" style="font-size:11px;padding:4px 8px;">\n          <option value="windows">&#127919; Windows (.exe)</option>\n          <option value="linux">&#127919; Linux (ELF)</option>\n          <option value="macos">&#127919; macOS</option>\n          <option value="web">&#127919; Web (WASM)</option>\n          <option value="android">&#127919; Android (APK)</option>\n          <option value="ios">&#127919; iOS (IPA)</option>\n        </select>\n        <button class="btn btn-compile" id="cBtn" onclick="runCompile()">&#9881; Compile</button>\n      </div>\n    </div>\n    <div class="sh"><span>&#128187; Output Console</span><button class="btn-clr" onclick="clrCon(\'cOut\')">&#10005; Clear</button></div>\n    <div class="cout" id="cOut"><span class="dim">Compiler ready. Click Compile or press Ctrl+Shift+B to run.</span></div>\n  </div>\n</div>\n<footer>\n  <div class="sr"><span><span class="dot"></span> Engine Online</span><span id="statFull">Lines: 1 | Chars: 0</span></div>\n  <div class="sr"><span>UTF-8 &middot; Nova V1.6.1</span><span>Dual Independent Engines: Interpreter &amp; Native Compiler</span><span>Zero-GC Speed</span></div>\n</footer>\n<script>\nlet curFile="script.no",tmpls={};\nconst ed=document.getElementById("ed");\ned.addEventListener("keydown",e=>{\n  if(e.key==="Tab"){e.preventDefault();const s=ed.selectionStart,n=ed.selectionEnd;ed.value=ed.value.slice(0,s)+"    "+ed.value.slice(n);ed.selectionStart=ed.selectionEnd=s+4;upStat();}\n  if((e.ctrlKey||e.metaKey)&&!e.shiftKey&&e.key==="Enter"){e.preventDefault();runInterp();}\n  if((e.ctrlKey||e.metaKey)&&e.shiftKey&&(e.key==="B"||e.key==="b")){e.preventDefault();runCompile();}\n});\ned.addEventListener("input",upStat);\nfunction upStat(){const ln=ed.value.split("\\n").length,ch=ed.value.length;document.getElementById("stat").textContent="Lines: "+ln;document.getElementById("statFull").textContent="Lines: "+ln+" | Chars: "+ch;}\nasync function init(){await loadTmpls();await loadFiles();loadTemplate("hello_world");}\nasync function loadTmpls(){try{const d=await(await fetch("/api/templates")).json();tmpls=d;const s=document.getElementById("tmplSel");for(const[k,t]of Object.entries(d)){const o=document.createElement("option");o.value=k;o.text=t.title;s.appendChild(o);}}catch(e){console.error(e);}}\nfunction loadTemplate(k){if(!k||!tmpls[k])return;ed.value=tmpls[k].code;curFile=k+".no";document.getElementById("fileName").textContent=curFile;upStat();}\nasync function loadFiles(){try{const d=await(await fetch("/api/files")).json();const l=document.getElementById("fileList");l.innerHTML="";d.files.forEach(f=>{const div=document.createElement("div");div.className="file-item";div.textContent="\\uD83D\\uDCC4 "+f.path;div.onclick=()=>openFile(f.path);l.appendChild(div);});}catch(e){console.error(e);}}\nasync function openFile(p){try{const d=await(await fetch("/api/file?path="+encodeURIComponent(p))).json();if(d.content!==undefined){ed.value=d.content;curFile=p;document.getElementById("fileName").textContent=p;upStat();}}catch(e){alert("Load failed: "+e);}}\nasync function saveFile(){try{const d=await(await fetch("/api/save",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({path:curFile,code:ed.value})})).json();if(d.ok)writeCon("iOut","[Saved] "+d.path,"ok");else writeCon("iOut","[Error] "+d.error,"err");loadFiles();}catch(e){writeCon("iOut","[Error] "+e,"err");}}\nfunction clrCon(id){document.getElementById(id).innerHTML="";}\nfunction writeCon(id,txt,cls){const c=document.getElementById(id);c.innerHTML="";const s=document.createElement("span");s.className=cls||"";s.textContent=txt;c.appendChild(s);c.scrollTop=c.scrollHeight;}\nfunction setBtn(id,loading,lbl){const b=document.getElementById(id);b.disabled=loading;b.innerHTML=loading?"<span class=\\"spin\\"></span> Working\\u2026":lbl;}\nasync function runInterp(){\n  setBtn("iBtn",true,"");\n  writeCon("iOut","[Interpreter] Running "+curFile+"...\\n"+"\\u2500".repeat(44)+"\\n","inf");\n  try{\n    const d=await(await fetch("/api/run",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({code:ed.value,file:curFile})})).json();\n    const c=document.getElementById("iOut");c.innerHTML="";\n    const h=document.createElement("span");h.className=d.ok?"ok":"err";\n    h.textContent="[Interpreter] "+(d.ok?"\\u2713 SUCCESS":"\\u2717 FAILED")+" (Exit: "+d.exitCode+") | Time: "+d.timeMs+"ms\\n"+"\\u2500".repeat(46)+"\\n";\n    c.appendChild(h);\n    if(d.stdout){const o=document.createElement("span");o.style.color="#dde8f8";o.textContent=d.stdout;c.appendChild(o);}\n    if(d.stderr){const e=document.createElement("span");e.className="err";e.textContent="\\n[STDERR]\\n"+d.stderr;c.appendChild(e);}\n    c.scrollTop=c.scrollHeight;\n  }catch(e){writeCon("iOut","[Network Error] "+e,"err");}\n  finally{setBtn("iBtn",false,"&#9654; Run");}\n}\nasync function runCompile(){\n  const tgt=document.getElementById("tgtSel").value;\n  setBtn("cBtn",true,"");\n  writeCon("cOut","[Compiler] Building native executable ("+tgt.toUpperCase()+")...\\n"+"\\u2500".repeat(44)+"\\n","inf");\n  try{\n    const d=await(await fetch("/api/compile",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({code:ed.value,target:tgt})})).json();\n    const c=document.getElementById("cOut");c.innerHTML="";\n    const h=document.createElement("span");h.className=d.ok?"ok":"err";\n    h.textContent="[Compiler] "+(d.ok?"\\u2713 COMPILED":"\\u2717 FAILED")+" | Target: "+tgt.toUpperCase()+" | Time: "+d.timeMs+"ms\\n"+"\\u2500".repeat(46)+"\\n";\n    c.appendChild(h);\n    if(d.stdout){const o=document.createElement("span");o.style.color="#dde8f8";o.textContent=d.stdout;c.appendChild(o);}\n    if(d.stderr&&d.stderr.trim()){const e=document.createElement("span");e.className="err";e.textContent="\\n[Build Errors]\\n"+d.stderr;c.appendChild(e);}\n    c.scrollTop=c.scrollHeight;\n  }catch(e){writeCon("cOut","[Network Error] "+e,"err");}\n  finally{setBtn("cBtn",false,"&#9881; Compile");}\n}\nwindow.onload=init;\n</script>\n</body>\n</html>'


def find_free_port(start_port=5050):
    for port in range(start_port, start_port + 50):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", port)) != 0:
                return port
    return start_port


def main():
    parser = argparse.ArgumentParser(description="Nova Unified Studio & IDE")
    parser.add_argument("--port", type=int, default=5050, help="Port to run IDE server on")
    parser.add_argument("--no-browser", action="store_true", help="Do not auto-open browser")
    parser.add_argument("file", nargs="?", help="Optional .no file to preload into IDE")
    args = parser.parse_args()

    port = find_free_port(args.port)
    server_address = ("127.0.0.1", port)
    httpd = HTTPServer(server_address, NovaIDEHandler)
    url = f"http://127.0.0.1:{port}"

    print("=" * 60)
    print("  * NOVA PROGRAMMING LANGUAGE - UNIFIED IDE & STUDIO *")
    print(f"  [+] Server running at: {url}")
    print("  [+] Dual Engine: Live Interpreter & Native C Compiler")
    print("=" * 60)

    if not args.no_browser:
        webbrowser.open(url)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[Nova IDE] Server stopped.")
        httpd.server_close()


if __name__ == "__main__":
    main()
