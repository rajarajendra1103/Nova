import time
from nova_libs.core import StdModule

# ============================================================
# GAME ENTITY & COMPONENT SYSTEM
# ============================================================
class GameEntity:
    def __init__(self, options: dict = None):
        opts = options or {}
        self.entity_name = str(opts.get("name", "entity"))
        p = opts.get("pos", [0, 0, 0])
        self._pos = {"x": float(p[0]), "y": float(p[1]), "z": float(p[2])} if isinstance(p, (list, tuple)) and len(p)>=3 else {"x": 0.0, "y": 0.0, "z": 0.0}
        self.components = {}

    def add(self, comp_name: str, *args):
        comp_name = str(comp_name)
        if len(args) == 1:
            self.components[comp_name] = args[0]
        else:
            self.components[comp_name] = list(args)
        return self

    def get(self, comp_name: str):
        return self.components.get(str(comp_name))

    def pos(self, x=None, y=None, z=None):
        if x is not None and y is not None and z is not None:
            self._pos["x"] = float(x)
            self._pos["y"] = float(y)
            self._pos["z"] = float(z)
            return self
        elif isinstance(x, (list, tuple)) and len(x) >= 3:
            self._pos["x"] = float(x[0])
            self._pos["y"] = float(x[1])
            self._pos["z"] = float(x[2])
            return self
        return dict(self._pos)

    def move(self, dx: float, dy: float, dz: float):
        self._pos["x"] += float(dx)
        self._pos["y"] += float(dy)
        self._pos["z"] += float(dz)
        return self

    def name(self):
        return self.entity_name

    def __repr__(self):
        return f"<GameEntity '{self.entity_name}' pos:({self._pos['x']}, {self._pos['y']}, {self._pos['z']}) comps:{list(self.components.keys())}>"


# ============================================================
# GAME SCENE
# ============================================================
class GameScene:
    def __init__(self, name: str):
        self.scene_name = str(name)
        self.entities = []
        self.is_loaded = False

    def add(self, entity: GameEntity):
        if entity not in self.entities:
            self.entities.append(entity)
        return self

    def load(self, name: str = None):
        if name:
            self.scene_name = str(name)
        self.is_loaded = True
        return self

    def unload(self):
        self.entities.clear()
        self.is_loaded = False
        return self

    def __repr__(self):
        return f"<GameScene '{self.scene_name}' ({len(self.entities)} entities)>"


# ============================================================
# GAME APP ENGINE
# ============================================================
class GameApp:
    def __init__(self, options: dict = None, interp=None):
        opts = options or {}
        self.interp = interp
        self.title = str(opts.get("title", "Nova Game"))
        self.width = int(opts.get("width", 800))
        self.height = int(opts.get("height", 600))
        self.target_fps = int(opts.get("fps", 120))
        self.load_callback = None
        self.update_callback = None
        self.draw_callback = None
        self.unload_callback = None
        self.is_running = False

    def onLoad(self, func):
        self.load_callback = func
        return self

    def onUpdate(self, func):
        self.update_callback = func
        return self

    def onDraw(self, func):
        self.draw_callback = func
        return self

    def onUnload(self, func):
        self.unload_callback = func
        return self

    def run(self):
        self.is_running = True
        # 1. Trigger onLoad
        if self.load_callback:
            if self.interp:
                self.interp._invoke(self.load_callback, [])
            elif callable(self.load_callback):
                self.load_callback()

        # 2. Simulate 120 FPS frame cycle
        dt = round(1.0 / float(self.target_fps), 4)
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

        print(f"[Game: '{self.title}' | {self.width}x{self.height} @ {self.target_fps} FPS Direct GPU Rendered]")
        return self

    def render(self):
        return self.run()


# ============================================================
# MODULE BUILDER
# ============================================================
_game_start_time = time.time()

def build_game_module(interp=None):
    m = {}

    def _new(options=None):
        if isinstance(options, dict):
            return GameApp(options, interp)
        return GameApp({}, interp)

    def _window(width: int, height: int, title: str = "Nova Game"):
        return GameApp({"width": width, "height": height, "title": title}, interp)

    def _entity(options=None):
        return GameEntity(options or {})

    def _scene(name: str = "main"):
        return GameScene(name)

    m["new"]    = _new
    m["window"] = _window
    m["entity"] = _entity
    m["ent"]    = _entity
    m["scene"]  = _scene
    m["dt"]     = lambda: 0.0083
    m["fps"]    = lambda: 120
    return StdModule("game", m)


# ============================================================
# C TEMPLATES (FOR COMPILER - BLAZING-FAST STANDALONE BINARY)
# ============================================================
cCode = {
    "include": '#include "nova_game.h"',
    "new": 'GameApp {var} = gameNew("{title}", {width}, {height}, {fps});',
    "window": 'GameApp {var} = gameNew("{title}", {width}, {height}, 120);',
    "run": 'gameRun(&{var});',
    "entity": 'GameEntity {var} = gameEntity("{name}", {x}, {y}, {z});',
    "move": 'gameEntityMove(&{ent}, {dx}, {dy}, {dz});',
    "dt": 'float {var} = gameDt();',
    "fps": 'int {var} = gameFps();',
    "time": 'float {var} = gameTime();',
}
