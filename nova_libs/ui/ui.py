from nova_libs.core import StdModule
from nova_libs.ui.app import get_screen, NovaAppUnified

# ============================================================
# UNIFIED UI ELEMENT (GPU DIRECT & RESPONSIVE COMPONENT)
# ============================================================
class UIElement:
    def __init__(self, kind: str, options: dict = None):
        self.kind = kind
        self.opts = dict(options) if options else {}
        self.children = []
        self.click_handler = self.opts.get("onClick")
        self.submit_handler = self.opts.get("onSubmit")
        self.styles = {}
        self.attrs = {}

    def add(self, *children):
        for c in children:
            if isinstance(c, (list, tuple)):
                self.children.extend(c)
            elif c is not None:
                self.children.append(c)
        return self

    def remove(self, child):
        if child in self.children:
            self.children.remove(child)
        return self

    def clear(self):
        self.children.clear()
        return self

    def set(self, options: dict):
        if isinstance(options, dict):
            self.opts.update(options)
            if "onClick" in options:
                self.click_handler = options["onClick"]
            if "onSubmit" in options:
                self.submit_handler = options["onSubmit"]
        return self

    def setText(self, text: str):
        self.opts["text"] = str(text)
        if "title" in self.opts:
            self.opts["title"] = str(text)
        return self

    def setColor(self, color: str):
        self.opts["color"] = str(color)
        return self

    def size(self, w, h):
        self.opts["width"] = w
        self.opts["height"] = h
        return self

    def width(self):
        return self.opts.get("width", "100%")

    def height(self):
        return self.opts.get("height", "auto")

    def onClick(self, func):
        self.click_handler = func
        return self

    def onSubmit(self, func):
        self.submit_handler = func
        return self

    def w(self, width): self.opts["width"] = width; return self
    def h(self, height): self.opts["height"] = height; return self
    def wFull(self): self.opts["width"] = "100%"; return self
    def hFull(self): self.opts["height"] = "100%"; return self
    def bg(self, color): self.opts["color"] = color; self.styles["background-color"] = color; return self
    def color(self, color): self.opts["text_color"] = color; self.styles["color"] = color; return self
    def pad(self, p): self.opts["padding"] = p; return self
    def p(self, p): return self.pad(p)
    def pt(self, p): self.opts["padding_top"] = p; return self
    def pb(self, p): self.opts["padding_bottom"] = p; return self
    def pl(self, p): self.opts["padding_left"] = p; return self
    def pr(self, p): self.opts["padding_right"] = p; return self
    def px(self, p): self.pl(p); self.pr(p); return self
    def py(self, p): self.pt(p); self.pb(p); return self
    def margin(self, m): self.opts["margin"] = m; return self
    def m(self, m): return self.margin(m)
    def mt(self, m): self.opts["margin_top"] = m; return self
    def mb(self, m): self.opts["margin_bottom"] = m; return self
    def ml(self, m): self.opts["margin_left"] = m; return self
    def mr(self, m): self.opts["margin_right"] = m; return self
    def mx(self, m): self.ml(m); self.mr(m); return self
    def my(self, m): self.mt(m); self.mb(m); return self
    def round(self, r): self.opts["round"] = r; return self
    def rounded(self, r): return self.round(r)
    def center(self): self.opts["center"] = True; return self
    def gap(self, g): self.opts["gap"] = g; return self
    def fontSize(self, sz): self.opts["size"] = sz; return self
    def bold(self): self.opts["bold"] = True; return self
    def id(self, elem_id): self.attrs["id"] = str(elem_id); return self
    def cls(self, class_name): self.attrs["class"] = str(class_name); return self
    def className(self, class_name): self.attrs["class"] = str(class_name); return self

    def head(self, headers):
        th_elems = [UIElement("th", {"text": str(h)}) for h in headers]
        tr_elem = UIElement("tr").add(*th_elems)
        thead_elem = UIElement("thead").add(tr_elem)
        self.add(thead_elem)
        return self

    def row(self, items):
        td_elems = [UIElement("td", {"text": str(it)}) for it in items]
        tr_elem = UIElement("tr").add(*td_elems)
        self.add(tr_elem)
        return self

    def renderNative(self, indent: int = 0):
        pad = "  " * indent
        details = []
        for k in ("dir", "cols", "gap", "width", "height", "color", "size", "text", "title", "price", "placeholder", "flex"):
            if k in self.opts:
                details.append(f"{k}:{self.opts[k]}")
        detail_str = f" ({', '.join(details)})" if details else ""
        print(f"{pad}└─ [{self.kind.upper()}]{detail_str}")
        for ch in self.children:
            if hasattr(ch, "renderNative"):
                ch.renderNative(indent + 1)
            else:
                print(f"{pad}    └─ {ch}")
        return self

    def toHTML(self) -> str:
        w = self.opts.get("width", "")
        h = self.opts.get("height", "")
        col = self.opts.get("color", "")
        t_col = self.opts.get("text_color", "")
        styles = []
        if w: styles.append(f"width:{w if isinstance(w, str) else str(w)+'px'}")
        if h: styles.append(f"height:{h if isinstance(h, str) else str(h)+'px'}")
        if col: styles.append(f"background-color:{col}")
        if t_col: styles.append(f"color:{t_col}")
        if "padding" in self.opts: styles.append(f"padding:{self.opts['padding']}px")
        if "padding_top" in self.opts: styles.append(f"padding-top:{self.opts['padding_top']}px")
        if "padding_bottom" in self.opts: styles.append(f"padding-bottom:{self.opts['padding_bottom']}px")
        if "padding_left" in self.opts: styles.append(f"padding-left:{self.opts['padding_left']}px")
        if "padding_right" in self.opts: styles.append(f"padding-right:{self.opts['padding_right']}px")
        if "margin" in self.opts: styles.append(f"margin:{self.opts['margin']}px")
        if "margin_top" in self.opts: styles.append(f"margin-top:{self.opts['margin_top']}px")
        if "margin_bottom" in self.opts: styles.append(f"margin-bottom:{self.opts['margin_bottom']}px")
        if "margin_left" in self.opts: styles.append(f"margin-left:{self.opts['margin_left']}px")
        if "margin_right" in self.opts: styles.append(f"margin-right:{self.opts['margin_right']}px")
        if "round" in self.opts: styles.append(f"border-radius:{self.opts['round']}px")
        if self.opts.get("center"): styles.append("text-align:center; align-items:center; justify-content:center")
        if self.opts.get("bold"): styles.append("font-weight:bold")
        if "size" in self.opts: styles.append(f"font-size:{self.opts['size']}px")

        for sk, sv in self.styles.items():
            styles.append(f"{sk}:{sv}")

        if self.kind == "flex":
            styles.append("display:flex")
            styles.append(f"flex-direction:{'column' if self.opts.get('dir') == 'col' else 'row'}")
            if "gap" in self.opts: styles.append(f"gap:{self.opts['gap']}px")
        elif self.kind == "grid":
            cols = self.opts.get("cols", 1)
            styles.append("display:grid")
            styles.append(f"grid-template-columns:repeat({cols}, 1fr)")
            if "gap" in self.opts: styles.append(f"gap:{self.opts['gap']}px")

        style_attr = f' style="{"; ".join(styles)}"' if styles else ""
        inner = ""
        if "text" in self.opts: inner += str(self.opts["text"])
        if "title" in self.opts: inner += f"<h3>{self.opts['title']}</h3>"
        if "price" in self.opts: inner += f"<span>{self.opts['price']}</span>"

        for ch in self.children:
            if hasattr(ch, "toHTML"): inner += ch.toHTML()
            else: inner += str(ch)

        tag = "button" if self.kind == "button" else ("input" if self.kind == "input" else "div")
        if self.kind == "input":
            ph = self.opts.get("placeholder", "")
            return f'<input class="nova-input" placeholder="{ph}"{style_attr} />'
        elif self.kind == "button":
            return f'<button class="nova-btn"{style_attr}>{inner}</button>'
        return f'<div class="nova-{self.kind}"{style_attr}>{inner}</div>'

    def __repr__(self):
        return f"<UIElement:{self.kind} {self.opts}>"


# ============================================================
# RESPONSIVE BREAKPOINT MANAGER
# ============================================================
class ResponsiveManager:
    def __init__(self, options: dict):
        self.configs = options or {}

    def get(self):
        scr = get_screen()
        dev_type = scr.get("type", "desktop")
        # 1. Exact device type match
        if dev_type in self.configs:
            return dict(self.configs[dev_type])
        # 2. Width-based matching fallback
        w = scr.get("width", 1920)
        if w <= 480 and "mobile" in self.configs:
            return dict(self.configs["mobile"])
        elif w <= 900 and "tablet" in self.configs:
            return dict(self.configs["tablet"])
        elif "desktop" in self.configs:
            return dict(self.configs["desktop"])
        elif "custom" in self.configs:
            return dict(self.configs["custom"])
        return {"cols": 1, "dir": "col", "gap": 10, "padding": 10}


# ============================================================
# MODULE BUILDER
# ============================================================
def build_ui_module(interp=None):
    m = {}

    def _flex(options=None):
        return UIElement("flex", options)

    def _grid(options_or_cols=None, rows=None):
        if isinstance(options_or_cols, dict):
            return UIElement("grid", options_or_cols)
        opts = {}
        if options_or_cols is not None:
            opts["cols"] = int(options_or_cols)
        if rows is not None:
            opts["rows"] = int(rows)
        return UIElement("grid", opts)

    def _box(options=None):
        return UIElement("box", options)

    def _button(options=None):
        if isinstance(options, str):
            return UIElement("button", {"text": options})
        return UIElement("button", options)

    def _text(txt="", options=None):
        opts = dict(options) if options else {}
        opts["text"] = str(txt)
        return UIElement("text", opts)

    def _image(path="", options=None):
        opts = dict(options) if options else {}
        opts["path"] = str(path)
        return UIElement("image", opts)

    def _card(title_or_opts=None, options=None):
        if isinstance(title_or_opts, str):
            opts = dict(options) if options else {}
            opts["title"] = title_or_opts
            return UIElement("card", opts)
        return UIElement("card", title_or_opts)

    def _input(options=None):
        if isinstance(options, str):
            return UIElement("input", {"placeholder": options})
        return UIElement("input", options)

    def _responsive(options=None):
        return ResponsiveManager(options or {})

    m["flex"]       = _flex
    m["grid"]       = _grid
    m["box"]        = _box
    m["button"]     = _button
    m["btn"]        = _button
    m["btnP"]       = lambda label="Primary": UIElement("button", {"text": label, "color": "#2563eb", "text_color": "#ffffff"})
    m["btnS"]       = lambda label="Secondary": UIElement("button", {"text": label, "color": "#475569", "text_color": "#ffffff"})
    m["btnD"]       = lambda label="Danger": UIElement("button", {"text": label, "color": "#dc2626", "text_color": "#ffffff"})
    m["btnI"]       = lambda label="Icon": UIElement("button", {"text": label, "color": "transparent"})
    m["text"]       = _text
    m["txt"]        = _text
    m["para"]       = _text
    m["p"]          = _text
    m["title"]      = lambda txt="", lvl=1: UIElement("title", {"text": txt, "level": lvl, "size": 24, "bold": True})
    m["subTitle"]   = lambda txt="": UIElement("subtitle", {"text": txt, "size": 16})
    m["span"]       = lambda txt="": UIElement("span", {"text": txt})
    m["image"]      = _image
    m["img"]        = _image
    m["card"]       = _card
    m["input"]      = _input
    m["inputE"]     = lambda placeholder="Email": UIElement("input", {"type": "email", "placeholder": placeholder})
    m["inputN"]     = lambda placeholder="0": UIElement("input", {"type": "number", "placeholder": placeholder})
    m["inputP"]     = lambda placeholder="Password": UIElement("input", {"type": "password", "placeholder": placeholder})
    m["select"]     = lambda options=None, default_val=None: UIElement("select", {"options": options or [], "value": default_val})
    m["check"]      = lambda label="": UIElement("check", {"label": label})
    m["form"]       = lambda: UIElement("form")
    m["table"]      = lambda: UIElement("table")
    m["thead"]      = lambda: UIElement("thead")
    m["tbody"]      = lambda: UIElement("tbody")
    m["tr"]         = lambda: UIElement("tr")
    m["th"]         = lambda txt="": UIElement("th", {"text": txt})
    m["td"]         = lambda txt="": UIElement("td", {"text": txt})
    m["nav"]        = lambda: UIElement("nav")
    m["sidebar"]    = lambda: UIElement("sidebar")
    m["header"]     = lambda: UIElement("header")
    m["footer"]     = lambda: UIElement("footer")
    m["section"]    = lambda: UIElement("section")
    m["modal"]      = lambda: UIElement("modal")
    m["container"]  = lambda: UIElement("container")
    m["link"]       = lambda txt="", href="#": UIElement("link", {"text": txt, "href": href})
    m["badge"]      = lambda txt="": UIElement("badge", {"text": txt})
    m["spacer"]     = lambda h="16px": UIElement("spacer", {"height": h})
    m["space"]      = m["spacer"]
    m["line"]       = lambda: UIElement("line")
    m["scroll"]     = lambda: UIElement("scroll")
    m["row"]        = lambda: UIElement("flex", {"dir": "row"})
    m["col"]        = lambda: UIElement("flex", {"dir": "col"})
    m["div"]        = lambda txt="": UIElement("box", {"text": txt})
    m["list"]       = lambda items=None: UIElement("flex", {"dir": "col"}).add(*(items or []))
    m["responsive"] = _responsive

    # Mobile Native UI Widgets & Components
    m["appBar"]       = lambda title="App", leading=None, actions=None, opts=None: UIElement("appbar", {"title": title, "leading": leading, "actions": actions or [], **(opts or {})})
    m["bottomNav"]    = lambda items=None, onSelect=None: UIElement("bottomnav", {"items": items or [], "onSelect": onSelect})
    m["tabBar"]       = m["bottomNav"]
    m["safeArea"]     = lambda child=None: UIElement("safearea").add(child) if child else UIElement("safearea")
    m["touchable"]    = lambda child=None, onTap=None, onLongPress=None: (UIElement("touchable", {"onTap": onTap, "onLongPress": onLongPress}).add(child) if child else UIElement("touchable", {"onTap": onTap, "onLongPress": onLongPress}))
    m["fab"]          = lambda icon="+", onClick=None, pos="bottom-right": UIElement("fab", {"icon": icon, "onClick": onClick, "position": pos})
    m["floatingBtn"]  = m["fab"]
    m["listTile"]     = lambda title="", subtitle="", leading=None, trailing=None, onTap=None: UIElement("listtile", {"title": title, "subtitle": subtitle, "leading": leading, "trailing": trailing, "onTap": onTap})
    m["toggleSwitch"] = lambda checked=False, onChange=None: UIElement("switch", {"checked": bool(checked), "onChange": onChange})
    m["switch"]       = m["toggleSwitch"]
    m["slider"]       = lambda min_v=0, max_v=100, val=50, onChange=None: UIElement("slider", {"min": min_v, "max": max_v, "value": val, "onChange": onChange})
    m["bottomSheet"]  = lambda child=None, isOpen=True: (UIElement("bottomsheet", {"isOpen": isOpen}).add(child) if child else UIElement("bottomsheet", {"isOpen": isOpen}))
    m["toast"]        = lambda msg="", duration=2.0, toast_type="info": UIElement("toast", {"message": msg, "duration": duration, "type": toast_type})
    m["modalDialog"]  = lambda title="", content="", actions=None: UIElement("dialog", {"title": title, "content": content, "actions": actions or []})
    m["drawer"]       = lambda header=None, items=None: UIElement("drawer", {"header": header, "items": items or []})
    m["haptic"]       = lambda h_type="light": f"[Nova Mobile Haptic: {h_type}]"
    m["alert"]        = lambda msg="": print(f"[Alert] {msg}")

    # For legacy ui.app(...) instantiation
    m["app"]        = lambda title="Nova App", w=None, h=None: NovaAppUnified({"title": title, "width": w, "height": h}, interp)
    m["page"]       = lambda title="Nova Page": NovaAppUnified({"title": title}, interp)

    return StdModule("ui", m)


# ============================================================
# C TEMPLATES (FOR COMPILER - BLAZING-FAST STANDALONE BINARY)
# ============================================================
cCode = {
    "include": '#include "nova_ui.h"',
    "card": 'UIElement {var} = uiCard();',
    "btn": 'UIElement {var} = uiButton("{text}");',
    "text": 'UIElement {var} = uiText("{text}");',
    "input": 'UIElement {var} = uiInput("{placeholder}");',
    "row": 'UIElement {var} = uiRow();',
    "col": 'UIElement {var} = uiCol();',
    "add": 'uiAdd(&{parent}, &{child});',
    "appBar": 'UIElement {var} = uiAppBar("{title}");',
    "bottomNav": 'UIElement {var} = uiBottomNav();',
    "safeArea": 'UIElement {var} = uiSafeArea();',
    "fab": 'UIElement {var} = uiFab("{icon}");',
    "listTile": 'UIElement {var} = uiListTile("{title}", "{subtitle}");',
    "switch": 'UIElement {var} = uiSwitch({checked});',
    "slider": 'UIElement {var} = uiSlider({min}, {max}, {value});',
}
