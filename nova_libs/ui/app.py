import sys
import time
import os
from nova_libs.core import StdModule

# ============================================================
# GLOBAL SCREEN & DEVICE PROFILE
# ============================================================
_current_screen = {
    "width": 1920,
    "height": 1080,
    "type": "desktop",
    "platform": "windows" if sys.platform.startswith("win") else ("macos" if sys.platform == "darwin" else "linux")
}

_start_time = time.time()
_target_fps = 120


def _detect_type(width: int, height: int) -> str:
    min_dim = min(width, height)
    max_dim = max(width, height)
    if min_dim <= 480:
        return "mobile"
    elif min_dim <= 900:
        return "tablet"
    elif max_dim >= 1000:
        return "desktop"
    return "custom"


def get_screen():
    return dict(_current_screen)


def set_screen(width: int, height: int, platform: str = None, dev_type: str = None):
    global _current_screen
    _current_screen["width"] = int(width)
    _current_screen["height"] = int(height)
    if platform:
        _current_screen["platform"] = str(platform).lower()
    if dev_type:
        _current_screen["type"] = str(dev_type).lower()
    else:
        _current_screen["type"] = _detect_type(int(width), int(height))
    return dict(_current_screen)


def scale_val(number):
    w = _current_screen["width"]
    # Mobile (360px) -> ~1.0x (16 -> 16)
    # Tablet (768px) -> ~1.1x
    # Desktop (1920px) -> ~1.2x (16 -> 19, 20 -> 24)
    factor = 0.85 + (w / 1920.0) * 0.35
    return int(round(float(number) * factor))


def is_mobile():
    return _current_screen.get("type") == "mobile"


def is_tablet():
    return _current_screen.get("type") == "tablet"


def is_desktop():
    return _current_screen.get("type") == "desktop"


def is_custom():
    return _current_screen.get("type") == "custom"


def is_ios():
    return _current_screen.get("platform") == "ios"


def is_android():
    return _current_screen.get("platform") == "android"


def get_platform():
    return _current_screen.get("platform", "windows")


def set_orientation(orientation: str = "portrait"):
    _current_screen["orientation"] = str(orientation).lower()
    return _current_screen["orientation"]


def get_orientation():
    return _current_screen.get("orientation", "portrait")


def trigger_haptics(feedback_type: str = "light"):
    msg = f"[Nova Native Haptics: {feedback_type}]"
    return msg


def trigger_vibrate(ms: int = 100):
    msg = f"[Nova Native Vibrate: {ms}ms]"
    return msg


def set_status_bar(style: str = "light-content", bg: str = "#000000"):
    _current_screen["statusBar"] = {"style": str(style), "bg": str(bg)}
    return dict(_current_screen["statusBar"])


def get_dt():
    return round(1.0 / float(_target_fps), 4)


def get_fps():
    return _target_fps


def get_time():
    return round(time.time() - _start_time, 4)


# ============================================================
# UNIFIED NOVA APP CLASS
# ============================================================
class NovaAppUnified:
    def __init__(self, options: dict = None, interp=None):
        opts = options or {}
        self.interp = interp
        self.title = str(opts.get("title", "Nova App"))
        self.fps = int(opts.get("fps", 120))
        global _target_fps
        _target_fps = self.fps

        # Set width & height
        w = opts.get("width")
        h = opts.get("height")
        if w is not None and h is not None:
            self.width = int(w)
            self.height = int(h)
            set_screen(self.width, self.height)
        else:
            self.width = _current_screen["width"]
            self.height = _current_screen["height"]

        self.root_element = None
        self.load_callback = None
        self.update_callback = None
        self.draw_callback = None
        self.resize_callback = None
        self.unload_callback = None
        self.is_running = False
        self.theme_bg = "#0f172a"
        self.is_centered = False
        self.padding_amount = 0

    def bg(self, color: str): self.theme_bg = str(color); return self
    def center(self): self.is_centered = True; return self
    def pad(self, amount): self.padding_amount = amount; return self
    def add(self, elem): self.root_element = elem; return self
    def render(self): return self.run()
    def show(self):
        print(f"[Nova App Window: '{self.title}' ({self.width}x{self.height}) rendered]")
        return self

    def toHTML(self) -> str:
        body_content = self.root_element.toHTML() if self.root_element and hasattr(self.root_element, "toHTML") else "<h1>Nova App</h1>"
        return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{self.title}</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }}
        body {{ background-color: {self.theme_bg}; color: #f8fafc; min-height: 100vh; display: flex; flex-direction: column; }}
    </style>
</head>
<body>
    {body_content}
</body>
</html>"""

    def onLoad(self, func):
        self.load_callback = func
        return self

    def onUpdate(self, func):
        self.update_callback = func
        return self

    def onDraw(self, func):
        self.draw_callback = func
        return self

    def onResize(self, func):
        self.resize_callback = func
        return self

    def onUnload(self, func):
        self.unload_callback = func
        return self

    def setRoot(self, ui_elem):
        self.root_element = ui_elem
        return self

    def resize(self, new_width: int, new_height: int, platform: str = None):
        self.width = int(new_width)
        self.height = int(new_height)
        set_screen(self.width, self.height, platform=platform)
        if self.resize_callback:
            if self.interp:
                self.interp._invoke(self.resize_callback, [self.width, self.height])
            elif callable(self.resize_callback):
                self.resize_callback(self.width, self.height)
        return self

    def run(self):
        self.is_running = True
        # 1. Trigger onLoad
        if self.load_callback:
            if self.interp:
                self.interp._invoke(self.load_callback, [])
            elif callable(self.load_callback):
                self.load_callback()

        # 2. Simulate direct GPU 120 FPS frame tick
        dt = get_dt()
        if self.update_callback:
            if self.interp:
                self.interp._invoke(self.update_callback, [dt])
            elif callable(self.update_callback):
                self.update_callback(dt)

        if self.draw_callback:
            if self.interp:
                self.interp._invoke(self.draw_callback, [])
            elif callable(self.draw_callback):
                self.draw_callback()

        # Print direct GPU UI tree summary if root is set
        scr = get_screen()
        print(f"[App: '{self.title}' | Platform: {scr['platform']} | Type: {scr['type']} | {self.width}x{self.height} @ {self.fps}FPS (120 FPS Low Latency)]")
        if self.root_element and hasattr(self.root_element, "renderNative"):
            self.root_element.renderNative()

        return self

    def onPause(self, func):
        self.pause_callback = func
        return self

    def onResume(self, func):
        self.resume_callback = func
        return self

    def onBack(self, func):
        self.back_callback = func
        return self

    def onBackButton(self, func):
        return self.onBack(func)

    def close(self):
        self.is_running = False
        if self.unload_callback:
            if self.interp:
                self.interp._invoke(self.unload_callback, [])
            elif callable(self.unload_callback):
                self.unload_callback()
        return True


# ============================================================
# MODULE BUILDER
# ============================================================
def build_app_module(interp=None):
    m = {}

    def _new(options=None):
        if isinstance(options, dict):
            return NovaAppUnified(options, interp)
        return NovaAppUnified({}, interp)

    def _window(width, height, title="Nova App"):
        return NovaAppUnified({"width": width, "height": height, "title": title}, interp)

    m["new"]            = _new
    m["window"]         = _window
    m["screen"]         = get_screen
    m["setScreen"]      = set_screen
    m["scale"]          = scale_val
    m["isMobile"]       = is_mobile
    m["isTablet"]       = is_tablet
    m["isDesktop"]      = is_desktop
    m["isCustom"]       = is_custom
    m["isIOS"]          = is_ios
    m["isAndroid"]      = is_android
    m["platform"]       = get_platform
    m["setOrientation"] = set_orientation
    m["orientation"]    = get_orientation
    m["haptics"]        = trigger_haptics
    m["vibrate"]        = trigger_vibrate
    m["statusBar"]      = set_status_bar
    m["dt"]             = get_dt
    m["fps"]            = get_fps
    m["time"]           = get_time

    return StdModule("app", m)


# ============================================================
# C TEMPLATES (FOR COMPILER - BLAZING-FAST STANDALONE BINARY)
# ============================================================
cCode = {
    "include": '#include "nova_app.h"',
    "new": 'App {var}; appNew(&{var}, "{title}", {width}, {height}, {fps});',
    "window": 'App {var}; appNew(&{var}, "{title}", {width}, {height}, 120);',
    "run": 'appRun(&{var});',
    "scale": 'appScale({factor});',
    "isMobile": 'bool {var} = appIsMobile();',
    "isIOS": 'bool {var} = appIsIOS();',
    "isAndroid": 'bool {var} = appIsAndroid();',
    "haptics": 'appHaptics("{type}");',
    "vibrate": 'appVibrate({ms});',
    "statusBar": 'appStatusBar("{style}", "{bg}");',
}
