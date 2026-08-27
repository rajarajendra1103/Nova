from nova_libs.core import StdModule

# ============================================================
# INPUT SYSTEM (KEYBOARD, MOUSE, TOUCH, GAMEPAD)
# ============================================================
_key_states = {}
_key_down_events = {}
_key_up_events = {}
_mouse_pos = {"x": 0.0, "y": 0.0}
_mouse_buttons = {"left": False, "right": False, "middle": False}
_touch_pos = {"x": 0.0, "y": 0.0}
_touch_down = False


def is_key(name: str):
    return _key_states.get(str(name).lower(), False)


def is_key_down(name: str):
    return _key_down_events.get(str(name).lower(), False)


def is_key_up(name: str):
    return _key_up_events.get(str(name).lower(), False)


def get_mouse_pos():
    return dict(_mouse_pos)


def is_mouse_down(button: str = "left"):
    return _mouse_buttons.get(str(button).lower(), False)


def get_touch_pos():
    return dict(_touch_pos)


def is_touch_down():
    return _touch_down


def set_key(name: str, is_pressed: bool):
    name = str(name).lower()
    _key_states[name] = bool(is_pressed)
    _key_down_events[name] = bool(is_pressed)
    _key_up_events[name] = not bool(is_pressed)
    return True


def set_mouse(x: float, y: float, button: str = None, is_down: bool = True):
    _mouse_pos["x"] = float(x)
    _mouse_pos["y"] = float(y)
    if button:
        _mouse_buttons[str(button).lower()] = bool(is_down)
    return True


def set_touch(x: float, y: float, is_down: bool = True):
    _touch_pos["x"] = float(x)
    _touch_pos["y"] = float(y)
    global _touch_down
    _touch_down = bool(is_down)
    return True


def build_input_module():
    m = {}
    m["key"]       = is_key
    m["keyDown"]   = is_key_down
    m["keyUp"]     = is_key_up
    m["isDown"]    = is_key
    m["press"]     = lambda k: set_key(k, True)
    m["release"]   = lambda k: set_key(k, False)
    m["mousePos"]  = get_mouse_pos
    m["mouseX"]    = lambda: _mouse_pos["x"]
    m["mouseY"]    = lambda: _mouse_pos["y"]
    m["mouseDown"] = is_mouse_down
    m["touchPos"]  = get_touch_pos
    m["touchDown"] = is_touch_down
    m["setKey"]    = set_key
    m["setMouse"]  = set_mouse
    m["setTouch"]  = set_touch
    return StdModule("input", m)


# ============================================================
# C TEMPLATES (FOR COMPILER - BLAZING-FAST STANDALONE BINARY)
# ============================================================
cCode = {
    "include": '#include "nova_input.h"',
    "key": 'bool {var} = inputKey("{name}");',
    "keyDown": 'bool {var} = inputKeyDown("{name}");',
    "keyUp": 'bool {var} = inputKeyUp("{name}");',
    "mouseDown": 'bool {var} = inputMouseDown("{button}");',
    "touchDown": 'bool {var} = inputTouchDown();',
}
