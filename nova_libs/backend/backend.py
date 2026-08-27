import os
import sys
import json
import time
import datetime
import threading
import sqlite3
import hashlib
import hmac
import base64
import secrets
import uuid
import re
import urllib.request
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Any

from nova_libs.core import StdModule

# ============================================================
# HTTP CLIENT
# ============================================================
class NovaHttpResponse:
    def __init__(self, status_code: int, text_content: str, headers: dict = None, url: str = ""):
        self.status = status_code
        self.statusCode = status_code
        self.text = text_content
        self.body = text_content
        self.headers = headers or {}
        self.url = url
        self.ok = 200 <= status_code < 300

    def json(self):
        try:
            return json.loads(self.text)
        except Exception:
            return None

    def __repr__(self):
        return f"<Response [{self.status}] {len(self.text)} bytes>"


class NovaAsyncTask:
    def __init__(self, target_fn, *args):
        self._res = None
        self._done = threading.Event()
        def _worker():
            try: self._res = target_fn(*args)
            except Exception as e: self._res = f"Error: {e}"
            finally: self._done.set()
        self._t = threading.Thread(target=_worker, daemon=True)
        self._t.start()

    def wait(self, timeout=None):
        self._done.wait(timeout)
        return self._res

    def isDone(self):
        return self._done.is_set()

    def result(self):
        return self.wait()

    def then(self, callback):
        def _chain():
            val = self.wait()
            try: callback(val)
            except Exception: pass
        threading.Thread(target=_chain, daemon=True).start()
        return self


def build_http_module():
    m = {}

    def _request(method: str, url: str, data: Any = None, headers: dict = None, timeout: float = 10.0):
        url_s = str(url)
        hdrs = dict(headers) if headers else {}
        if "User-Agent" not in hdrs:
            hdrs["User-Agent"] = "Nova-HTTP-Client/1.6"

        body_bytes = None
        if data is not None:
            if isinstance(data, (dict, list)):
                body_bytes = json.dumps(data).encode("utf-8")
                if "Content-Type" not in hdrs:
                    hdrs["Content-Type"] = "application/json"
            elif isinstance(data, str):
                body_bytes = data.encode("utf-8")
            elif isinstance(data, bytes):
                body_bytes = data

        req = urllib.request.Request(url_s, data=body_bytes, headers=hdrs, method=method.upper())
        try:
            with urllib.request.urlopen(req, timeout=float(timeout)) as resp:
                status = resp.status
                resp_headers = dict(resp.getheaders())
                raw_body = resp.read().decode("utf-8", errors="replace")
                return NovaHttpResponse(status, raw_body, resp_headers, url_s)
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="replace") if e.fp else ""
            return NovaHttpResponse(e.code, err_body, dict(e.headers), url_s)
        except Exception as e:
            return NovaHttpResponse(500, f"HTTP Error: {str(e)}", {}, url_s)

    m["get"]    = lambda url, headers=None, timeout=10.0: _request("GET", url, None, headers, timeout)
    m["g"]      = m["get"]
    m["post"]   = lambda url, data=None, headers=None, timeout=10.0: _request("POST", url, data, headers, timeout)
    m["p"]      = m["post"]
    m["put"]    = lambda url, data=None, headers=None, timeout=10.0: _request("PUT", url, data, headers, timeout)
    m["patch"]  = lambda url, data=None, headers=None, timeout=10.0: _request("PATCH", url, data, headers, timeout)
    m["delete"] = lambda url, headers=None, timeout=10.0: _request("DELETE", url, None, headers, timeout)
    m["del"]    = m["delete"]
    m["head"]   = lambda url, headers=None, timeout=10.0: _request("HEAD", url, None, headers, timeout)
    m["fetch"]  = _request

    m["getAsync"]  = lambda url, headers=None, timeout=10.0: NovaAsyncTask(m["get"], url, headers, timeout)
    m["postAsync"] = lambda url, data=None, headers=None, timeout=10.0: NovaAsyncTask(m["post"], url, data, headers, timeout)
    m["fetchAsync"] = lambda method, url, data=None, headers=None, timeout=10.0: NovaAsyncTask(_request, method, url, data, headers, timeout)

    return StdModule("http", m)


# ============================================================
# SERVER MODULE
# ============================================================
class NovaRequest:
    def __init__(self, method: str, path: str, headers: dict, body: str, params: dict = None, query: dict = None):
        self.method = method
        self.path = path
        self.headers = headers or {}
        self.body_raw = body
        self.params = params or {}
        self.query = query or {}
        self.body = self._parse_body(body)

    def _parse_body(self, raw: str):
        if not raw: return None
        try: return json.loads(raw)
        except Exception: return raw

    def header(self, name: str, default: str = ""):
        return self.headers.get(name.lower(), self.headers.get(name, default))

    def param(self, name: str, default: str = ""):
        return self.params.get(name, default)

    def queryParam(self, name: str, default: str = ""):
        return self.query.get(name, default)


class NovaResponse:
    def __init__(self):
        self.status_code = 200
        self.headers = {"Content-Type": "text/html; charset=utf-8"}
        self.body = ""
        self._sent = False

    def status(self, code: int):
        self.status_code = int(code)
        return self

    def header(self, k: str, v: str):
        self.headers[k] = str(v)
        return self

    def send(self, data: str):
        self.body = str(data)
        self._sent = True
        return self

    def json(self, data: Any):
        self.headers["Content-Type"] = "application/json; charset=utf-8"
        self.body = json.dumps(data)
        self._sent = True
        return self

    def html(self, data: Any):
        self.headers["Content-Type"] = "text/html; charset=utf-8"
        self.body = str(data)
        self._sent = True
        return self

    def render(self, ui_obj: Any):
        if hasattr(ui_obj, "toHTML"):
            return self.html(ui_obj.toHTML())
        return self.send(str(ui_obj))


class NovaRoute:
    def __init__(self, method: str, pattern: str, handler):
        self.method = method.upper()
        self.pattern = pattern
        self.handler = handler
        self._regex, self._param_names = self._compile(pattern)

    def _compile(self, pat: str):
        param_names = []
        def _repl(match):
            param_names.append(match.group(1))
            return "([^/]+)"
        escaped = re.sub(r":([a-zA-Z0-9_]+)", _repl, pat)
        return re.compile(f"^{escaped}$"), param_names

    def match(self, method: str, path: str):
        if self.method != "*" and self.method != method.upper():
            return False, {}
        m = self._regex.match(path)
        if not m:
            return False, {}
        params = dict(zip(self._param_names, m.groups()))
        return True, params


class NovaServerApp:
    def __init__(self, interp):
        self.interp = interp
        self.routes = []
        self.middlewares = []
        self.server_thread = None
        self.httpd = None
        self.port = 3000
        self.host = "0.0.0.0"
        self._enable_cors = False
        self._enable_json = True

    def use(self, middleware_fn):
        self.middlewares.append(middleware_fn)
        return self

    def cors(self):
        self._enable_cors = True
        return self

    def json(self):
        self._enable_json = True
        return self

    def get(self, path: str, handler):
        self.routes.append(NovaRoute("GET", path, handler))
        return self

    def post(self, path: str, handler):
        self.routes.append(NovaRoute("POST", path, handler))
        return self

    def put(self, path: str, handler):
        self.routes.append(NovaRoute("PUT", path, handler))
        return self

    def patch(self, path: str, handler):
        self.routes.append(NovaRoute("PATCH", path, handler))
        return self

    def delete(self, path: str, handler):
        self.routes.append(NovaRoute("DELETE", path, handler))
        return self

    def all(self, path: str, handler):
        self.routes.append(NovaRoute("*", path, handler))
        return self

    def ws(self, path: str, handler):
        self.routes.append(NovaRoute("WS", path, handler))
        return self

    def group(self, prefix: str):
        outer = self
        class RouteGroup:
            def __init__(self, p): self.prefix = p
            def get(self, p, h): outer.get(self.prefix + p, h); return self
            def post(self, p, h): outer.post(self.prefix + p, h); return self
            def put(self, p, h): outer.put(self.prefix + p, h); return self
            def patch(self, p, h): outer.patch(self.prefix + p, h); return self
            def delete(self, p, h): outer.delete(self.prefix + p, h); return self
            def ws(self, p, h): outer.ws(self.prefix + p, h); return self
        return RouteGroup(prefix)

    def listen(self, port: int = 3000, host: str = "0.0.0.0", callback = None):
        self.port = int(port)
        self.host = host
        app_ref = self

        class NovaHTTPHandler(BaseHTTPRequestHandler):
            def log_message(self, format, *args):
                pass

            def do_OPTIONS(self):
                self.send_response(204)
                if app_ref._enable_cors:
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, PATCH, DELETE, OPTIONS")
                    self.send_header("Access-Control-Allow-Headers", "*")
                self.end_headers()

            def _handle_all(self, method: str):
                parsed_url = urllib.parse.urlparse(self.path)
                path = parsed_url.path
                q_params = urllib.parse.parse_qs(parsed_url.query)
                query = {k: v[0] if len(v)==1 else v for k, v in q_params.items()}

                content_len = int(self.headers.get("Content-Length", 0))
                body_raw = self.rfile.read(content_len).decode("utf-8", errors="replace") if content_len > 0 else ""

                headers_dict = {k: v for k, v in self.headers.items()}
                res = NovaResponse()
                if app_ref._enable_cors:
                    res.header("Access-Control-Allow-Origin", "*")
                    res.header("Access-Control-Allow-Headers", "*")
                    res.header("Access-Control-Allow-Methods", "GET, POST, PUT, PATCH, DELETE, OPTIONS")

                matched_route = None
                matched_params = {}
                for route in app_ref.routes:
                    ok, params = route.match(method, path)
                    if ok:
                        matched_route = route
                        matched_params = params
                        break

                req = NovaRequest(method, path, headers_dict, body_raw, matched_params, query)

                for mw in app_ref.middlewares:
                    try:
                        app_ref.interp._invoke(mw, [req, res])
                    except Exception as e:
                        print(f"[Middleware Error]: {e}", file=sys.stderr)

                if matched_route:
                    try:
                        app_ref.interp._invoke(matched_route.handler, [req, res])
                    except Exception as e:
                        res.status(500).json({"error": "Internal Server Error", "details": str(e)})
                else:
                    res.status(404).json({"error": "Route Not Found", "path": path, "method": method})

                # Send response
                self.send_response(res.status_code)
                for hk, hv in res.headers.items():
                    self.send_header(hk, hv)
                self.end_headers()
                self.wfile.write(res.body.encode("utf-8"))

            def do_GET(self): self._handle_all("GET")
            def do_POST(self): self._handle_all("POST")
            def do_PUT(self): self._handle_all("PUT")
            def do_PATCH(self): self._handle_all("PATCH")
            def do_DELETE(self): self._handle_all("DELETE")

        self.httpd = HTTPServer((self.host, self.port), NovaHTTPHandler)
        self.server_thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.server_thread.start()
        if callback:
            try: self.interp._invoke(callback, [])
            except Exception: pass
        return self

    def stop(self):
        if self.httpd:
            self.httpd.shutdown()
            self.httpd.server_close()
            self.httpd = None
        return True

    def close(self):
        return self.stop()


def build_server_module(interp):
    m = {}
    m["new"]     = lambda: NovaServerApp(interp)
    m["create"]  = lambda: NovaServerApp(interp)
    m["app"]     = lambda: NovaServerApp(interp)
    m["serve"]   = lambda port=3000, host="0.0.0.0": NovaServerApp(interp).listen(port, host)
    return StdModule("server", m)


# ============================================================
# DATABASE MODULE
# ============================================================
class NovaDB:
    def __init__(self):
        self.conn = None
        self.curr_db = ":memory:"

    def connect(self, uri: str = "app.db"):
        self.curr_db = uri
        self.conn = sqlite3.connect(uri, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        return self

    def open(self, uri: str = "app.db"):
        return self.connect(uri)

    def _ensure_conn(self):
        if not self.conn: self.connect("app.db")

    def create(self, table: str, schema: Any):
        self._ensure_conn()
        if isinstance(schema, (list, tuple)):
            schema = {str(c): "TEXT" for c in schema}
        cols = []
        for k, v in schema.items():
            t = str(v).lower()
            if "primary" in t: cols.append(f"{k} INTEGER PRIMARY KEY AUTOINCREMENT" if "int" in t else f"{k} TEXT PRIMARY KEY")
            elif "int" in t: cols.append(f"{k} INTEGER")
            elif "float" in t or "num" in t: cols.append(f"{k} REAL")
            else: cols.append(f"{k} TEXT")
        sql = f"CREATE TABLE IF NOT EXISTS {table} ({', '.join(cols)});"
        self.conn.execute(sql); self.conn.commit()
        return True

    def table(self, table: str, schema: dict): return self.create(table, schema)

    def insert(self, table: str, data: dict):
        self._ensure_conn()
        keys = list(data.keys()); vals = list(data.values())
        placeholders = ", ".join(["?"] * len(keys))
        sql = f"INSERT INTO {table} ({', '.join(keys)}) VALUES ({placeholders});"
        cur = self.conn.cursor()
        cur.execute(sql, vals); self.conn.commit()
        return cur.lastrowid

    def find(self, table: str):
        self._ensure_conn()
        cur = self.conn.cursor()
        cur.execute(f"SELECT * FROM {table};")
        return [dict(row) for row in cur.fetchall()]

    def findOne(self, table: str, query: dict):
        self._ensure_conn()
        cur = self.conn.cursor()
        clauses = " AND ".join([f"{k} = ?" for k in query.keys()])
        cur.execute(f"SELECT * FROM {table} WHERE {clauses} LIMIT 1;", list(query.values()))
        row = cur.fetchone()
        return dict(row) if row else None

    def findWhere(self, table: str, condition: str):
        self._ensure_conn()
        cur = self.conn.cursor()
        cur.execute(f"SELECT * FROM {table} WHERE {condition};")
        return [dict(row) for row in cur.fetchall()]

    def update(self, table: str, query: dict, update_data: dict):
        self._ensure_conn()
        set_clause = ", ".join([f"{k} = ?" for k in update_data.keys()])
        where_clause = " AND ".join([f"{k} = ?" for k in query.keys()])
        vals = list(update_data.values()) + list(query.values())
        sql = f"UPDATE {table} SET {set_clause} WHERE {where_clause};"
        cur = self.conn.cursor()
        cur.execute(sql, vals); self.conn.commit()
        return cur.rowcount

    def delete(self, table: str, query: dict):
        self._ensure_conn()
        where_clause = " AND ".join([f"{k} = ?" for k in query.keys()])
        sql = f"DELETE FROM {table} WHERE {where_clause};"
        cur = self.conn.cursor()
        cur.execute(sql, list(query.values())); self.conn.commit()
        return cur.rowcount

    def count(self, table: str):
        self._ensure_conn()
        cur = self.conn.cursor()
        cur.execute(f"SELECT COUNT(*) FROM {table};")
        return cur.fetchone()[0]

    def exec(self, sql: str, params: list = None):
        self._ensure_conn()
        cur = self.conn.cursor()
        cur.execute(sql, params or [])
        self.conn.commit()
        return cur.rowcount

    def all(self, sql_or_table: str, params: list = None):
        self._ensure_conn()
        s = str(sql_or_table).strip()
        if s.upper().startswith("SELECT") or " " in s:
            return self.query(s, params)
        return self.find(s)

    def query(self, sql: str, params: list = None):
        self._ensure_conn()
        cur = self.conn.cursor()
        cur.execute(sql, params or [])
        if sql.strip().upper().startswith("SELECT"):
            return [dict(row) for row in cur.fetchall()]
        self.conn.commit()
        return cur.rowcount

    def sort(self, table: str, col: str):
        self._ensure_conn()
        cur = self.conn.cursor()
        cur.execute(f"SELECT * FROM {table} ORDER BY {col} ASC;")
        return [dict(row) for row in cur.fetchall()]

    def dsort(self, table: str, col: str):
        self._ensure_conn()
        cur = self.conn.cursor()
        cur.execute(f"SELECT * FROM {table} ORDER BY {col} DESC;")
        return [dict(row) for row in cur.fetchall()]

    def clear(self, table: str):
        self._ensure_conn()
        self.conn.execute(f"DELETE FROM {table};")
        self.conn.commit()
        return True


# ============================================================
# AUTH MODULE
# ============================================================
def build_auth_module():
    m = {}

    def _hash(password: str, salt: str = "nova_salt_v1"):
        combined = f"{salt}:{password}".encode("utf-8")
        return hashlib.sha256(combined).hexdigest()

    def _check(password: str, hashed: str, salt: str = "nova_salt_v1"):
        return _hash(password, salt) == hashed

    def _token(payload: dict, secret: str = "nova_default_secret", expire_sec: Any = 86400):
        data = dict(payload) if isinstance(payload, dict) else {"data": payload}
        exp = 86400
        if isinstance(expire_sec, (int, float)):
            exp = float(expire_sec)
        elif isinstance(expire_sec, str):
            s = expire_sec.strip().lower()
            if s.endswith("h"): exp = float(s[:-1]) * 3600
            elif s.endswith("m"): exp = float(s[:-1]) * 60
            elif s.endswith("d"): exp = float(s[:-1]) * 86400
            elif s.endswith("s"): exp = float(s[:-1])
            else:
                try: exp = float(s)
                except Exception: exp = 86400
        data["_exp"] = time.time() + exp
        raw_json = json.dumps(data, separators=(",", ":")).encode("utf-8")
        body_b64 = base64.urlsafe_b64encode(raw_json).decode("utf-8").rstrip("=")
        sig = hmac.new(secret.encode("utf-8"), body_b64.encode("utf-8"), hashlib.sha256).hexdigest()
        return f"{body_b64}.{sig}"

    def _verify(token_str: str, secret: str = "nova_default_secret"):
        try:
            parts = str(token_str).split(".")
            if len(parts) != 2: return None
            body_b64, sig = parts
            expected_sig = hmac.new(secret.encode("utf-8"), body_b64.encode("utf-8"), hashlib.sha256).hexdigest()
            if not hmac.compare_digest(sig, expected_sig): return None
            pad = len(body_b64) % 4
            if pad: body_b64 += "=" * (4 - pad)
            raw = base64.urlsafe_b64decode(body_b64.encode("utf-8"))
            data = json.loads(raw)
            if data.get("_exp", 0) < time.time(): return None
            data.pop("_exp", None)
            return data
        except Exception:
            return None

    m["hash"]    = _hash
    m["check"]   = _check
    m["verifyP"] = _check
    m["token"]   = _token
    m["jwt"]     = _token
    m["verify"]  = _verify
    m["decode"]  = _verify
    return StdModule("auth", m)


# ============================================================
# ENV MODULE
# ============================================================
def build_env_module():
    m = {}
    m["get"] = lambda k, default="": os.environ.get(str(k), default)
    m["set"] = lambda k, v: os.environ.__setitem__(str(k), str(v))
    m["has"] = lambda k: str(k) in os.environ
    m["all"] = lambda: dict(os.environ)
    return StdModule("env", m)


# ============================================================
# UI MODULE
# ============================================================
class NovaUIElement:
    def __init__(self, tag: str, text_content: str = "", attributes: dict = None, styles: dict = None):
        self.tag = tag
        self.text = text_content
        self.attrs = attributes or {}
        self.styles = styles or {}
        self.children = []

    def add(self, *children):
        for c in children:
            if isinstance(c, (list, tuple)):
                self.children.extend(c)
            elif c is not None:
                self.children.append(c)
        return self

    def bg(self, color: str): self.styles["background-color"] = color; return self
    def color(self, color: str): self.styles["color"] = color; return self
    def pad(self, amount): self.styles["padding"] = f"{amount}px" if isinstance(amount, (int, float)) else str(amount); return self
    def margin(self, amount): self.styles["margin"] = f"{amount}px" if isinstance(amount, (int, float)) else str(amount); return self
    def round(self, amount): self.styles["border-radius"] = f"{amount}px" if isinstance(amount, (int, float)) else str(amount); return self
    def w(self, width): self.styles["width"] = f"{width}px" if isinstance(width, (int, float)) else str(width); return self
    def h(self, height): self.styles["height"] = f"{height}px" if isinstance(height, (int, float)) else str(height); return self
    def border(self, b_str): self.styles["border"] = str(b_str); return self
    def shadow(self, s_str="0 4px 6px -1px rgba(0, 0, 0, 0.1)"): self.styles["box-shadow"] = str(s_str); return self
    def head(self, headers):
        th_elems = [_elem("th", str(h), padding="10px 12px", text_align="left", border_bottom="1px solid #334155", color="#94a3b8", font_weight="600") for h in headers]
        tr_elem = _elem("tr", "").add(*th_elems)
        thead_elem = _elem("thead", "").add(tr_elem)
        self.add(thead_elem)
        return self

    def row(self, items):
        td_elems = [_elem("td", str(it), padding="10px 12px", border_bottom="1px solid #1e293b", color="#f8fafc") for it in items]
        tr_elem = _elem("tr", "").add(*td_elems)
        self.add(tr_elem)
        return self

    def onSubmit(self, fn):
        self.attrs["onsubmit"] = "novaHandleSubmit(this); return false;"
        return self

    def wFull(self): self.styles["width"] = "100%"; return self
    def hFull(self): self.styles["height"] = "100%"; return self
    def gap(self, g): self.styles["gap"] = f"{g}px" if isinstance(g, (int, float)) else str(g); return self
    def id(self, elem_id: str): self.attrs["id"] = str(elem_id); return self
    def cls(self, class_name: str): self.attrs["class"] = str(class_name); return self
    def className(self, class_name: str): self.attrs["class"] = str(class_name); return self
    def flex(self, direction="row"): self.styles["display"] = "flex"; self.styles["flex-direction"] = direction; return self
    def center(self): self.styles["display"] = "flex"; self.styles["justify-content"] = "center"; self.styles["align-items"] = "center"; return self
    def fontSize(self, sz): self.styles["font-size"] = f"{sz}px" if isinstance(sz, (int, float)) else str(sz); return self
    def bold(self): self.styles["font-weight"] = "bold"; return self
    def attr(self, k: str, v: str): self.attrs[k] = str(v); return self
    def style(self, k: str, v: str): self.styles[k] = str(v); return self
    def onClick(self, fn): self.attrs["onclick"] = "novaHandleClick(this)"; return self

    def toHTML(self) -> str:
        style_str = "; ".join([f"{k}:{v}" for k, v in self.styles.items()])
        style_attr = f' style="{style_str}"' if style_str else ""
        attrs_str = " ".join([f'{k}="{v}"' for k, v in self.attrs.items()])
        attrs_attr = f" {attrs_str}" if attrs_str else ""

        void_tags = {"input", "img", "br", "hr", "meta", "link"}
        if self.tag in void_tags:
            return f"<{self.tag}{style_attr}{attrs_attr}/>"

        inner = str(self.text) if self.text else ""
        for ch in self.children:
            if hasattr(ch, "toHTML"): inner += ch.toHTML()
            elif ch is not None: inner += str(ch)
        return f"<{self.tag}{style_attr}{attrs_attr}>{inner}</{self.tag}>"


class NovaAppWindow:
    def __init__(self, title: str = "Nova Application", width: int = 800, height: int = 600):
        self.window_title = title
        self.window_width = width
        self.window_height = height
        self.root_element = None
        self.routes = {}
        self.theme_mode = "dark"
        self.theme_bg = "#0f172a"
        self.is_centered = False
        self.padding_amount = 0

    def title(self, t: str): self.window_title = str(t); return self
    def size(self, w: int, h: int): self.window_width = int(w); self.window_height = int(h); return self
    def bg(self, color: str): self.theme_bg = str(color); return self
    def center(self): self.is_centered = True; return self
    def pad(self, amount): self.padding_amount = amount; return self
    def add(self, elem: NovaUIElement): self.root_element = elem; return self
    def theme(self, mode: str): self.theme_mode = mode; return self
    def route(self, path: str, view_fn): self.routes[path] = view_fn; return self
    def render(self): return self.toHTML()
    def show(self): print(f"[Nova App Window: '{self.window_title}' ({self.window_width}x{self.window_height}) rendered]"); return self

    def toHTML(self) -> str:
        body_content = self.root_element.toHTML() if self.root_element else "<h1>Nova App</h1>"
        bg_col = self.theme_bg if self.theme_bg else ("#0f172a" if self.theme_mode == "dark" else "#f8fafc")
        text_col = "#f8fafc" if self.theme_mode == "dark" else "#0f172a"
        align_css = "justify-content:center; align-items:center;" if self.is_centered else ""
        return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{self.window_title}</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }}
        body {{ background-color: {bg_col}; color: {text_col}; min-height: 100vh; display: flex; flex-direction: column; {align_css} padding: {self.padding_amount}px; }}
    </style>
</head>
<body>
    {body_content}
</body>
</html>"""

    def saveHtml(self, filepath: str):
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(self.toHTML())
        return True


def _elem(tag, text="", attrs=None, **styles):
    css = {k.replace("_", "-"): str(v) for k, v in styles.items()}
    return NovaUIElement(tag, text, attrs, css)


def build_ui_module():
    m = {}

    m["app"]       = lambda title="Nova App", w=800, h=600: NovaAppWindow(title, w, h)
    m["page"]      = lambda title="Nova Page": NovaAppWindow(title)
    m["div"]       = lambda txt="": _elem("div", txt)
    m["box"]       = lambda txt="": _elem("div", txt, display="block")
    m["row"]       = lambda: _elem("div", "", display="flex", flex_direction="row", gap="12px", align_items="center")
    m["col"]       = lambda: _elem("div", "", display="flex", flex_direction="column", gap="12px")
    m["text"]      = lambda txt="": _elem("p", txt, margin="0", font_size="14px")
    m["txt"]       = m["text"]
    m["para"]      = m["text"]
    m["p"]         = m["text"]
    m["title"]     = lambda txt="", lvl=1: _elem(f"h{max(1, min(6, int(lvl)))}", txt, margin="0", font_weight="bold")
    m["subTitle"]  = lambda txt="": _elem("h3", txt, margin="0", font_size="16px", color="#94a3b8")
    m["span"]      = lambda txt="": _elem("span", txt)
    m["btn"]       = lambda label="Button": _elem("button", label, background_color="#3b82f6", color="#ffffff", padding="8px 16px", border="none", border_radius="6px", cursor="pointer", font_weight="500")
    m["btnP"]      = lambda label="Primary": _elem("button", label, background_color="#2563eb", color="#ffffff", padding="8px 16px", border="none", border_radius="6px", cursor="pointer", font_weight="600")
    m["btnS"]      = lambda label="Secondary": _elem("button", label, background_color="#475569", color="#ffffff", padding="8px 16px", border="none", border_radius="6px", cursor="pointer", font_weight="500")
    m["btnD"]      = lambda label="Danger": _elem("button", label, background_color="#dc2626", color="#ffffff", padding="8px 16px", border="none", border_radius="6px", cursor="pointer", font_weight="600")
    m["btnI"]      = lambda label="Icon": _elem("button", label, background_color="transparent", color="#94a3b8", padding="6px 10px", border="1px solid #475569", border_radius="6px", cursor="pointer")
    m["input"]     = lambda placeholder="", typ="text": _elem("input", "", {"type": typ, "placeholder": placeholder}, padding="8px 12px", border="1px solid #475569", background_color="#0f172a", color="#f8fafc", border_radius="6px", width="100%")
    m["inputE"]    = lambda placeholder="Email": _elem("input", "", {"type": "email", "placeholder": placeholder}, padding="8px 12px", border="1px solid #475569", background_color="#0f172a", color="#f8fafc", border_radius="6px", width="100%")
    m["inputN"]    = lambda placeholder="0": _elem("input", "", {"type": "number", "placeholder": placeholder}, padding="8px 12px", border="1px solid #475569", background_color="#0f172a", color="#f8fafc", border_radius="6px", width="100%")
    m["inputP"]    = lambda placeholder="Password": _elem("input", "", {"type": "password", "placeholder": placeholder}, padding="8px 12px", border="1px solid #475569", background_color="#0f172a", color="#f8fafc", border_radius="6px", width="100%")
    m["select"]    = lambda options=None, default_val=None: (lambda s: (s.add(*[_elem("option", str(opt), {"value": str(opt), "selected": "selected" if opt == default_val else ""}) for opt in (options or [])]) or s))(_elem("select", "", padding="8px 12px", border="1px solid #475569", background_color="#0f172a", color="#f8fafc", border_radius="6px", width="100%"))
    m["check"]     = lambda label="": _elem("label", f" {label}", display="flex", align_items="center", gap="8px", color="#f8fafc").add(_elem("input", "", {"type": "checkbox"}))
    m["card"]      = lambda: _elem("div", "", padding="16px", border_radius="8px", background_color="#1e293b", color="#ffffff", box_shadow="0 4px 6px -1px rgba(0,0,0,0.1)")
    m["list"]      = lambda items=None: (lambda d: d.add(*(items or [])) and d)(_elem("div", "", display="flex", flex_direction="column", gap="8px"))
    m["form"]      = lambda: _elem("form", "", display="flex", flex_direction="column", gap="12px")
    m["grid"]      = lambda cols=2, rows=None: _elem("div", "", display="grid", grid_template_columns=f"repeat({cols}, 1fr)", gap="16px")
    m["scroll"]    = lambda: _elem("div", "", overflow_y="auto", display="flex", flex_direction="column", gap="8px")
    m["table"]     = lambda: _elem("table", "", width="100%", border_collapse="collapse")
    m["thead"]     = lambda: _elem("thead", "")
    m["tbody"]     = lambda: _elem("tbody", "")
    m["tr"]        = lambda: _elem("tr", "")
    m["th"]        = lambda txt="": _elem("th", txt, padding="10px 12px", text_align="left", border_bottom="1px solid #334155", color="#94a3b8", font_weight="600")
    m["td"]        = lambda txt="": _elem("td", txt, padding="10px 12px", border_bottom="1px solid #1e293b", color="#f8fafc")
    m["nav"]       = lambda: _elem("nav", "", display="flex", justify_content="space-between", align_items="center", padding="12px 24px", background_color="#0f172a", border_bottom="1px solid #1e293b")
    m["sidebar"]   = lambda: _elem("aside", "", display="flex", flex_direction="column", width="260px", padding="20px", background_color="#0f172a", border_right="1px solid #1e293b")
    m["header"]    = lambda: _elem("header", "", display="flex", justify_content="space-between", align_items="center", padding="16px")
    m["footer"]    = lambda: _elem("footer", "", display="flex", justify_content="center", align_items="center", padding="16px", border_top="1px solid #1e293b", color="#64748b")
    m["section"]   = lambda: _elem("section", "", padding="24px 0")
    m["modal"]     = lambda: _elem("div", "", padding="24px", background_color="#1e293b", border_radius="12px", box_shadow="0 20px 25px -5px rgba(0,0,0,0.5)")
    m["container"] = lambda: _elem("div", "", display="block", width="100%", max_width="1200px", margin="0 auto", padding="16px")
    m["link"]      = lambda txt="", href="#": _elem("a", txt, {"href": href}, color="#3b82f6", text_decoration="none")
    m["image"]     = lambda src="", alt="": _elem("img", "", {"src": src, "alt": alt})
    m["badge"]     = lambda txt="": _elem("span", txt, padding="4px 8px", border_radius="12px", font_size="12px", background_color="#334155", color="#f8fafc")
    m["spacer"]    = lambda h="16px": _elem("div", "", height=str(h) if isinstance(h, str) else f"{h}px")
    m["space"]     = m["spacer"]
    m["line"]      = lambda: _elem("hr", "", border="none", border_top="1px solid #334155", margin="12px 0")

    return StdModule("ui", m)


# ============================================================
# CACHE MODULE
# ============================================================
def build_cache_module():
    m = {}
    _cache_data = {}
    _lock = threading.Lock()

    def _clean():
        now = time.time()
        expired = [k for k, (v, exp) in _cache_data.items() if exp is not None and now > exp]
        for k in expired: del _cache_data[k]

    def _get(k, default=None):
        with _lock:
            _clean()
            if k in _cache_data: return _cache_data[k][0]
            return default

    def _set(k, v, ttl=None):
        with _lock:
            exp = (time.time() + float(ttl)) if ttl is not None else None
            _cache_data[str(k)] = (v, exp)
            return v

    def _has(k):
        with _lock:
            _clean()
            return str(k) in _cache_data

    def _del(k):
        with _lock:
            if str(k) in _cache_data:
                del _cache_data[str(k)]
                return True
            return False

    def _clear():
        with _lock:
            _cache_data.clear()
            return True

    def _ttl(k):
        with _lock:
            _clean()
            if str(k) in _cache_data:
                exp = _cache_data[str(k)][1]
                if exp is None: return -1
                return max(0.0, exp - time.time())
            return -2

    def _size():
        with _lock:
            _clean()
            return len(_cache_data)

    m["get"]    = _get
    m["set"]    = _set
    m["has"]    = _has
    m["del"]    = _del
    m["delete"] = _del
    m["clear"]  = _clear
    m["ttl"]    = _ttl
    m["size"]   = _size
    m["keys"]   = lambda: list(_cache_data.keys())
    m["values"] = lambda: [v[0] for v in _cache_data.values()]
    return StdModule("cache", m)


# ============================================================
# STORE MODULE
# ============================================================
def build_store_module():
    m = {}
    _store_file = "nova_store.json"
    _store_data = {}
    _lock = threading.Lock()

    def _load():
        nonlocal _store_data
        if os.path.exists(_store_file):
            try:
                with open(_store_file, "r", encoding="utf-8") as f:
                    _store_data = json.load(f)
            except Exception: _store_data = {}
        else: _store_data = {}

    def _persist():
        try:
            with open(_store_file, "w", encoding="utf-8") as f:
                json.dump(_store_data, f, indent=2)
        except Exception: pass

    _load()

    def _save(k_or_dict, v=None):
        with _lock:
            if v is None and isinstance(k_or_dict, dict):
                _store_data.update(k_or_dict)
            else:
                _store_data[str(k_or_dict)] = v
            _persist()
            return True

    def _get(k, default=None):
        with _lock:
            return _store_data.get(str(k), default)

    def _has(k):
        with _lock:
            return str(k) in _store_data

    def _del(k):
        with _lock:
            if str(k) in _store_data:
                del _store_data[str(k)]
                _persist()
                return True
            return False

    def _list(prefix=""):
        with _lock:
            if prefix:
                return {k: v for k, v in _store_data.items() if k.startswith(str(prefix))}
            return dict(_store_data)

    def _clear():
        with _lock:
            _store_data.clear()
            _persist()
            return True

    m["save"]   = _save
    m["set"]    = _save
    m["get"]    = _get
    m["has"]    = _has
    m["del"]    = _del
    m["delete"] = _del
    m["list"]   = _list
    m["all"]    = _list
    m["clear"]  = _clear
    return StdModule("store", m)


# ============================================================
# QUEUE MODULE
# ============================================================
def build_queue_module(interp):
    m = {}
    _queues = {}
    _lock = threading.Lock()

    def _add(topic_or_val, val=None):
        with _lock:
            if val is None:
                topic = "default"; data = topic_or_val
            else:
                topic = str(topic_or_val); data = val
            if topic not in _queues: _queues[topic] = []
            _queues[topic].append(data)
            return len(_queues[topic])

    def _pop(topic="default"):
        with _lock:
            topic = str(topic)
            if topic in _queues and _queues[topic]:
                return _queues[topic].pop(0)
            return None

    def _peek(topic="default"):
        with _lock:
            topic = str(topic)
            if topic in _queues and _queues[topic]:
                return _queues[topic][0]
            return None

    def _size(topic="default"):
        with _lock:
            topic = str(topic)
            return len(_queues.get(topic, []))

    def _clear(topic=None):
        with _lock:
            if topic is None: _queues.clear()
            elif str(topic) in _queues: _queues[str(topic)].clear()
            return True

    def _process(topic_or_fn, fn=None):
        if fn is None:
            topic = "default"; handler = topic_or_fn
        else:
            topic = str(topic_or_fn); handler = fn
        processed = 0
        while True:
            item = _pop(topic)
            if item is None: break
            if interp: interp._invoke(handler, [item])
            processed += 1
        return processed

    m["add"]     = _add
    m["push"]    = _add
    m["pop"]     = _pop
    m["peek"]    = _peek
    m["size"]    = _size
    m["clear"]   = _clear
    m["process"] = _process
    return StdModule("queue", m)


# ============================================================
# CRON MODULE
# ============================================================
def build_cron_module(interp):
    m = {}
    _tasks = {}
    _task_counter = 0
    _lock = threading.Lock()

    def _every(interval_sec, fn):
        nonlocal _task_counter
        with _lock:
            _task_counter += 1
            tid = f"job_{_task_counter}"
            stop_evt = threading.Event()

            def _worker():
                while not stop_evt.wait(float(interval_sec)):
                    try:
                        if interp: interp._invoke(fn, [])
                    except Exception as e:
                        print(f"[Cron Error]: {e}", file=sys.stderr)

            t = threading.Thread(target=_worker, daemon=True)
            t.start()
            _tasks[tid] = (t, stop_evt, f"every {interval_sec}s")
            return tid

    def _cancel(tid):
        with _lock:
            if tid in _tasks:
                t, evt, desc = _tasks[tid]
                evt.set()
                del _tasks[tid]
                return True
            return False

    def _list():
        with _lock:
            return {tid: desc for tid, (t, evt, desc) in _tasks.items()}

    def _clear():
        with _lock:
            for tid, (t, evt, desc) in list(_tasks.items()):
                evt.set()
            _tasks.clear()
            return True

    m["every"]    = _every
    m["schedule"] = _every
    m["cancel"]   = _cancel
    m["list"]     = _list
    m["clear"]    = _clear
    return StdModule("cron", m)


# ============================================================
# WEBSOCKET & REAL-TIME MODULE
# ============================================================
class NovaWsRoomEmitter:
    def __init__(self, room_name: str, server):
        self.room_name = str(room_name)
        self.server = server

    def emit(self, event: str, data: Any = None):
        return self.server._emit_room(self.room_name, event, data)

    def send(self, data: Any):
        return self.server._send_room(self.room_name, data)


class NovaSocket:
    def __init__(self, client_id: str, server, interp=None):
        self.id = str(client_id)
        self.server = server
        self.interp = interp
        self.rooms = set()
        self.connected = True
        self.handlers = {}
        self.received_messages = []

    def on(self, event: str, handler):
        evt = str(event).lower()
        if evt not in self.handlers:
            self.handlers[evt] = []
        self.handlers[evt].append(handler)
        return self

    def send(self, data: Any):
        if not self.connected: return False
        msg_str = json.dumps(data) if isinstance(data, (dict, list)) else str(data)
        return self.server._send_to_client(self.id, msg_str)

    def json(self, data: Any):
        return self.send(data)

    def emit(self, event: str, data: Any = None):
        payload = {"event": str(event), "data": data}
        return self.send(payload)

    def join(self, room: str):
        r = str(room)
        self.rooms.add(r)
        self.server._add_to_room(r, self.id)
        return self

    def leave(self, room: str):
        r = str(room)
        if r in self.rooms:
            self.rooms.remove(r)
        self.server._remove_from_room(r, self.id)
        return self

    def to(self, room: str):
        return NovaWsRoomEmitter(room, self.server)

    def broadcast(self, event: str, data: Any = None):
        return self.server.broadcast(event, data, exclude_id=self.id)

    def close(self):
        self.connected = False
        self.server._remove_client(self.id)
        return True


class NovaWsClient:
    def __init__(self, url: str = "", interp=None):
        self.url = str(url)
        self.interp = interp
        self.connected = True
        self.handlers = {"message": [], "connect": [], "close": [], "error": []}
        self.history = []

    def on(self, event: str, handler):
        evt = str(event).lower()
        if evt not in self.handlers:
            self.handlers[evt] = []
        self.handlers[evt].append(handler)
        return self

    def onMessage(self, fn): return self.on("message", fn)
    def onConnect(self, fn): return self.on("connect", fn)
    def onClose(self, fn): return self.on("close", fn)
    def onError(self, fn): return self.on("error", fn)

    def send(self, data: Any):
        if not self.connected: return False
        msg = json.dumps(data) if isinstance(data, (dict, list)) else str(data)
        self.history.append(msg)
        return True

    def json(self, data: Any):
        return self.send(data)

    def emit(self, event: str, data: Any = None):
        return self.send({"event": str(event), "data": data})

    def close(self):
        self.connected = False
        for fn in self.handlers.get("close", []):
            try:
                if self.interp: self.interp._invoke(fn, [])
                elif callable(fn): fn()
            except Exception: pass
        return True


class NovaWsServer:
    def __init__(self, interp=None, port: int = 8080):
        self.interp = interp
        self.port = int(port)
        self.clients = {}
        self.rooms = {}
        self.handlers = {"connect": [], "message": [], "disconnect": [], "close": []}
        self._lock = threading.Lock()

    def on(self, event: str, handler):
        evt = str(event).lower()
        if evt not in self.handlers:
            self.handlers[evt] = []
        self.handlers[evt].append(handler)
        return self

    def onConnect(self, fn): return self.on("connect", fn)
    def onMessage(self, fn): return self.on("message", fn)
    def onDisconnect(self, fn): return self.on("disconnect", fn)
    def onClose(self, fn): return self.on("close", fn)

    def createClient(self, client_id: str = None):
        cid = str(client_id) if client_id else str(uuid.uuid4())[:8]
        sock = NovaSocket(cid, self, self.interp)
        with self._lock:
            self.clients[cid] = sock
        for fn in self.handlers.get("connect", []):
            try:
                if self.interp: self.interp._invoke(fn, [sock])
                elif callable(fn): fn(sock)
            except Exception: pass
        return sock

    def _remove_client(self, cid: str):
        with self._lock:
            if cid in self.clients:
                del self.clients[cid]
            for r in list(self.rooms.keys()):
                if cid in self.rooms[r]:
                    self.rooms[r].remove(cid)
        for fn in self.handlers.get("disconnect", []):
            try:
                if self.interp: self.interp._invoke(fn, [cid])
                elif callable(fn): fn(cid)
            except Exception: pass

    def _add_to_room(self, room: str, cid: str):
        with self._lock:
            if room not in self.rooms:
                self.rooms[room] = set()
            self.rooms[room].add(cid)

    def _remove_from_room(self, room: str, cid: str):
        with self._lock:
            if room in self.rooms and cid in self.rooms[room]:
                self.rooms[room].remove(cid)

    def _send_to_client(self, cid: str, msg: str):
        with self._lock:
            sock = self.clients.get(cid)
        if sock:
            sock.received_messages.append(msg)
            # Dispatch to socket-specific handlers
            for fn in sock.handlers.get("message", []):
                try:
                    if self.interp: self.interp._invoke(fn, [msg])
                    elif callable(fn): fn(msg)
                except Exception: pass
            # Dispatch to server global message handlers
            for fn in self.handlers.get("message", []):
                try:
                    if self.interp: self.interp._invoke(fn, [msg, sock])
                    elif callable(fn): fn(msg, sock)
                except Exception: pass
            return True
        return False

    def _emit_room(self, room: str, event: str, data: Any = None):
        payload = json.dumps({"event": str(event), "data": data})
        count = 0
        with self._lock:
            cids = list(self.rooms.get(room, set()))
        for cid in cids:
            if self._send_to_client(cid, payload):
                count += 1
        return count

    def _send_room(self, room: str, data: Any):
        msg = json.dumps(data) if isinstance(data, (dict, list)) else str(data)
        count = 0
        with self._lock:
            cids = list(self.rooms.get(room, set()))
        for cid in cids:
            if self._send_to_client(cid, msg):
                count += 1
        return count

    def broadcast(self, event: str, data: Any = None, exclude_id: str = None):
        payload = {"event": str(event), "data": data}
        msg = json.dumps(payload)
        count = 0
        with self._lock:
            active = list(self.clients.keys())
        for cid in active:
            if exclude_id and cid == str(exclude_id):
                continue
            if self._send_to_client(cid, msg):
                count += 1
        return count

    def emit(self, event: str, data: Any = None):
        return self.broadcast(event, data)

    def send(self, cid: str, msg: Any):
        msg_str = json.dumps(msg) if isinstance(msg, (dict, list)) else str(msg)
        return self._send_to_client(str(cid), msg_str)

    def to(self, room: str):
        return NovaWsRoomEmitter(room, self)

    def join(self, room: str, cid: str):
        self._add_to_room(str(room), str(cid))
        return True

    def leave(self, room: str, cid: str):
        self._remove_from_room(str(room), str(cid))
        return True

    def clients(self):
        with self._lock:
            return list(self.clients.keys())

    def count(self):
        with self._lock:
            return len(self.clients)

    def close(self):
        with self._lock:
            self.clients.clear()
            self.rooms.clear()
        for fn in self.handlers.get("close", []):
            try:
                if self.interp: self.interp._invoke(fn, [])
                elif callable(fn): fn()
            except Exception: pass
        return True


def build_ws_module(interp):
    _default_server = NovaWsServer(interp, 8080)
    m = {}

    m["server"]      = lambda port=8080: NovaWsServer(interp, port)
    m["client"]      = lambda url="": NovaWsClient(url, interp)
    m["connect"]     = lambda url="": NovaWsClient(url, interp)
    m["createClient"]= lambda cid=None: _default_server.createClient(cid)

    # Top-level default real-time broker methods
    m["on"]          = _default_server.on
    m["onConnect"]   = _default_server.onConnect
    m["onMessage"]   = _default_server.onMessage
    m["onDisconnect"]= _default_server.onDisconnect
    m["onClose"]     = _default_server.onClose
    m["send"]        = _default_server.send
    m["sendAll"]     = lambda msg: _default_server.broadcast("message", msg)
    m["broadcast"]   = _default_server.broadcast
    m["emit"]        = _default_server.emit
    m["to"]          = _default_server.to
    m["join"]        = _default_server.join
    m["leave"]       = _default_server.leave
    m["clients"]     = _default_server.clients
    m["count"]       = _default_server.count
    m["close"]       = _default_server.close

    return StdModule("ws", m)


# ============================================================
# MAIL MODULE
# ============================================================
def build_mail_module():
    m = {}
    _templates = {}

    def _send(to, subject, body, opts=None):
        opts = opts or {}
        print(f"[Mail Sent] To: {to} | Subject: {subject}")
        return {"ok": True, "to": to, "subject": subject, "id": str(uuid.uuid4())}

    def _template(name, tmpl_str=None):
        if tmpl_str is not None:
            _templates[str(name)] = str(tmpl_str)
            return True
        return _templates.get(str(name), "")

    def _verify(email):
        pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        return bool(re.match(pattern, str(email).strip()))

    m["send"]     = _send
    m["template"] = _template
    m["verify"]   = _verify
    return StdModule("mail", m)


# ============================================================
# VALID MODULE
# ============================================================
def build_valid_module():
    m = {}

    def _email(val):
        return bool(re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', str(val).strip()))

    def _url(val):
        return bool(re.match(r'^(https?:\/\/)?([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}(:\d+)?(\/.*)?$', str(val).strip()))

    def _phone(val):
        return bool(re.match(r'^\+?[0-9\s\-()]{7,20}$', str(val).strip()))

    def _ip(val):
        return bool(re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', str(val).strip()))

    def _num(val):
        try: float(val); return True
        except Exception: return False

    def _alpha(val):
        return str(val).isalpha()

    def _len(val, min_l, max_l=None):
        l = len(str(val))
        if max_l is None: return l >= int(min_l)
        return int(min_l) <= l <= int(max_l)

    def _req(val):
        if val is None: return False
        if isinstance(val, (str, list, dict, set, tuple)): return len(val) > 0
        return True

    def _match(val, pattern):
        return bool(re.search(str(pattern), str(val)))

    m["email"] = _email
    m["url"]   = _url
    m["phone"] = _phone
    m["ip"]    = _ip
    m["num"]   = _num
    m["alpha"] = _alpha
    m["len"]   = _len
    m["req"]   = _req
    m["match"] = _match
    return StdModule("valid", m)


# ============================================================
# LOG MODULE
# ============================================================
def build_log_module():
    m = {}
    _log_file = [None]

    def _fmt(level, *args):
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        msg = " ".join(str(a) for a in args)
        line = f"[{ts}] [{level}] {msg}"
        print(line)
        if _log_file[0]:
            try:
                with open(_log_file[0], "a", encoding="utf-8") as f:
                    f.write(line + "\n")
            except Exception: pass
        return line

    def _set_file(path):
        _log_file[0] = str(path)
        return str(path)

    m["info"]  = lambda *args: _fmt("INFO", *args)
    m["warn"]  = lambda *args: _fmt("WARN", *args)
    m["error"] = lambda *args: _fmt("ERROR", *args)
    m["debug"] = lambda *args: _fmt("DEBUG", *args)
    m["file"]  = _set_file
    return StdModule("log", m)


# ============================================================
# SESSION MODULE
# ============================================================
def build_session_module():
    m = {}
    _sessions = {}
    _lock = threading.Lock()

    def _clean():
        now = time.time()
        expired = [sid for sid, (d, exp) in _sessions.items() if now > exp]
        for sid in expired: del _sessions[sid]

    def _create(data=None, ttl=86400):
        with _lock:
            _clean()
            sid = secrets.token_hex(16)
            d = dict(data) if isinstance(data, dict) else {}
            exp = time.time() + float(ttl)
            _sessions[sid] = (d, exp)
            return sid

    def _get(sid, k=None, default=None):
        with _lock:
            _clean()
            if str(sid) in _sessions:
                d, exp = _sessions[str(sid)]
                if k is None: return dict(d)
                return d.get(str(k), default)
            return default

    def _set(sid, k, v):
        with _lock:
            _clean()
            if str(sid) in _sessions:
                d, exp = _sessions[str(sid)]
                d[str(k)] = v
                return True
            return False

    def _has(sid):
        with _lock:
            _clean()
            return str(sid) in _sessions

    def _destroy(sid):
        with _lock:
            if str(sid) in _sessions:
                del _sessions[str(sid)]
                return True
            return False

    def _touch(sid, ttl=86400):
        with _lock:
            _clean()
            if str(sid) in _sessions:
                d, _ = _sessions[str(sid)]
                _sessions[str(sid)] = (d, time.time() + float(ttl))
                return True
            return False

    m["create"]  = _create
    m["get"]     = _get
    m["set"]     = _set
    m["has"]     = _has
    m["destroy"] = _destroy
    m["del"]     = _destroy
    m["touch"]   = _touch
    m["count"]   = lambda: len(_sessions)
    return StdModule("session", m)


# ============================================================
# UNIFIED BACKEND MODULE BUILDER
# ============================================================
def build_backend_module(interp):
    server_mod  = build_server_module(interp)
    db_inst     = NovaDB()
    auth_mod    = build_auth_module()
    env_mod     = build_env_module()
    ui_mod      = build_ui_module()
    http_mod    = build_http_module()

    cache_mod   = build_cache_module()
    store_mod   = build_store_module()
    queue_mod   = build_queue_module(interp)
    cron_mod    = build_cron_module(interp)
    ws_mod      = build_ws_module(interp)
    mail_mod    = build_mail_module()
    valid_mod   = build_valid_module()
    log_mod     = build_log_module()
    session_mod = build_session_module()

    m = {
        "server": server_mod,
        "db": db_inst,
        "auth": auth_mod,
        "env": env_mod,
        "http": http_mod,
        "ui": ui_mod,
        "cache": cache_mod,
        "store": store_mod,
        "queue": queue_mod,
        "cron": cron_mod,
        "ws": ws_mod,
        "mail": mail_mod,
        "log": log_mod,
        "session": session_mod,
    }
    return StdModule("backend", m)


# ============================================================
# C TEMPLATES (FOR COMPILER - BLAZING-FAST STANDALONE BINARY)
# ============================================================
cCode = {
    "include": '#include "nova_backend.h"',
    "server": 'NovaServer {var} = beServerNew({port});',
    "db": 'NovaDB {var} = beDbOpen("{path}");',
    "open": 'NovaDB {var} = beDbOpen("{path}");',
    "exec": 'beDbInsert(&{db}, "{table}", "{sql}");',
    "all": 'const char* {var} = beDbFind(&{db}, "{table}", "{query}");',
    "insert": 'int {var} = beDbInsert(&{db}, "{table}", "{jsonRow}");',
    "find": 'const char* {var} = beDbFind(&{db}, "{table}", "{query}");',
    "hash": 'const char* {var} = beAuthHash("{password}");',
    "verify": 'bool {var} = beAuthVerify("{password}", "{hash}");',
    "check": 'bool {var} = beAuthVerify("{password}", "{hash}");',
    "token": 'const char* {var} = beAuthToken("{user}", "{role}");',
    "jwt": 'const char* {var} = beAuthToken("{user}", "{role}");',
    "cacheSet": 'beCacheSet("{key}", "{val}", {ttl});',
    "cacheGet": 'const char* {var} = beCacheGet("{key}");',
    "storeSave": 'beStoreSave("{key}", "{jsonVal}");',
    "storeLoad": 'const char* {var} = beStoreLoad("{key}");',
    "queueAdd": 'beQueueAdd("{jobName}", "{payload}");',
    "cronEvery": 'beCronEvery("{interval}", "{taskName}");',
    "logInfo": 'beLogInfo("{msg}");',
    "sessionCreate": 'const char* {var} = beSessionCreate("{user}");',
    "wsServer": 'NovaWsServer {var} = beWsServerNew({port}); beWsServerStart(&{var});',
    "wsBroadcast": 'beWsBroadcast("{event}", "{data}");',
    "wsSend": 'beWsSend("{cid}", "{data}");',
}
