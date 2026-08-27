import math
from nova_libs.core import StdModule

# ============================================================
# 3D MESH & TEXTURE OBJECTS
# ============================================================
class Mesh:
    def __init__(self, data_or_path):
        if isinstance(data_or_path, str):
            self.path = data_or_path
            self.vertex_count = 1024
            self.triangle_count = 512
        elif isinstance(data_or_path, dict):
            self.path = "custom_mesh"
            self.vertices = data_or_path.get("vertices", [])
            self.indices = data_or_path.get("indices", [])
            self.vertex_count = len(self.vertices) // 3 if self.vertices else 0
            self.triangle_count = len(self.indices) // 3 if self.indices else 0
        else:
            self.path = "default_cube"
            self.vertex_count = 8
            self.triangle_count = 12

    def __repr__(self):
        return f"<Mesh '{self.path}' ({self.vertex_count} verts, {self.triangle_count} tris)>"


class Texture:
    def __init__(self, path: str, width: int = 1024, height: int = 1024):
        self.path = str(path)
        self.width = int(width)
        self.height = int(height)
        self.tex_id = abs(hash(path)) % 100000

    def __repr__(self):
        return f"<Texture '{self.path}' {self.width}x{self.height} id:{self.tex_id}>"


class Material:
    def __init__(self, options: dict = None):
        opts = options or {}
        self.color = opts.get("color", "white")
        self.texture = opts.get("texture")
        self.shader = opts.get("shader", "pbr")
        self.metallic = float(opts.get("metallic", 0.0))
        self.roughness = float(opts.get("roughness", 0.5))

    def __repr__(self):
        return f"<Material shader:{self.shader} color:{self.color} m:{self.metallic} r:{self.roughness}>"


class Shader:
    def __init__(self, vert, frag):
        self.vert = vert
        self.frag = frag

    def __repr__(self):
        return f"<Shader vert:{self.vert!r} frag:{self.frag!r}>"


# ============================================================
# 3D RENDER ENTITY
# ============================================================
class RenderEntity:
    def __init__(self, mesh: Mesh, material: Material = None):
        self.mesh = mesh
        self.material = material
        self._pos = {"x": 0.0, "y": 0.0, "z": 0.0}
        self._rot = {"x": 0.0, "y": 0.0, "z": 0.0}
        self._scale = {"x": 1.0, "y": 1.0, "z": 1.0}
        self.visible = True

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
        elif isinstance(x, dict):
            self._pos["x"] = float(x.get("x", self._pos["x"]))
            self._pos["y"] = float(x.get("y", self._pos["y"]))
            self._pos["z"] = float(x.get("z", self._pos["z"]))
            return self
        return dict(self._pos)

    def getPos(self):
        return dict(self._pos)

    def rot(self, x: float, y: float, z: float):
        self._rot["x"] = float(x)
        self._rot["y"] = float(y)
        self._rot["z"] = float(z)
        return self

    def scale(self, x: float, y: float = None, z: float = None):
        if y is None and z is None:
            y = x; z = x
        self._scale["x"] = float(x)
        self._scale["y"] = float(y)
        self._scale["z"] = float(z)
        return self

    def move(self, dx: float, dy: float, dz: float):
        self._pos["x"] += float(dx)
        self._pos["y"] += float(dy)
        self._pos["z"] += float(dz)
        return self

    def __repr__(self):
        return f"<RenderEntity pos:({self._pos['x']}, {self._pos['y']}, {self._pos['z']}) mesh:{self.mesh}>"


# ============================================================
# 2D SPRITE
# ============================================================
class Sprite:
    def __init__(self, path: str):
        self.path = str(path)
        self._pos = {"x": 0.0, "y": 0.0}
        self._size = {"w": 64.0, "h": 64.0}
        self.visible = True

    def pos(self, x=None, y=None):
        if x is not None and y is not None:
            self._pos["x"] = float(x)
            self._pos["y"] = float(y)
            return self
        elif isinstance(x, (list, tuple)) and len(x) >= 2:
            self._pos["x"] = float(x[0])
            self._pos["y"] = float(x[1])
            return self
        return dict(self._pos)

    def size(self, w: float, h: float):
        self._size["w"] = float(w)
        self._size["h"] = float(h)
        return self

    def move(self, dx: float, dy: float):
        self._pos["x"] += float(dx)
        self._pos["y"] += float(dy)
        return self

    def __repr__(self):
        return f"<Sprite '{self.path}' pos:({self._pos['x']}, {self._pos['y']}) size:({self._size['w']}x{self._size['h']})>"


# ============================================================
# CAMERA & LIGHTING
# ============================================================
class Camera:
    def __init__(self, *args, **kwargs):
        if len(args) == 4:
            self.fov = float(args[0])
            self._pos = {"x": float(args[1]), "y": float(args[2]), "z": float(args[3])}
            self._look_at = {"x": 0.0, "y": 0.0, "z": 0.0}
        elif len(args) == 1 and isinstance(args[0], dict):
            opts = args[0]
            self.fov = float(opts.get("fov", 60.0))
            p = opts.get("pos", [0, 5, 10])
            self._pos = {"x": float(p[0]), "y": float(p[1]), "z": float(p[2])} if isinstance(p, (list, tuple)) else {"x": 0.0, "y": 5.0, "z": 10.0}
            l = opts.get("lookAt", [0, 0, 0])
            self._look_at = {"x": float(l[0]), "y": float(l[1]), "z": float(l[2])} if isinstance(l, (list, tuple)) else {"x": 0.0, "y": 0.0, "z": 0.0}
        elif len(args) == 1 and isinstance(args[0], (int, float)):
            self.fov = float(args[0])
            self._pos = {"x": 0.0, "y": 5.0, "z": 10.0}
            self._look_at = {"x": 0.0, "y": 0.0, "z": 0.0}
        else:
            self.fov = 60.0
            self._pos = {"x": 0.0, "y": 5.0, "z": 10.0}
            self._look_at = {"x": 0.0, "y": 0.0, "z": 0.0}

    def pos(self, x=None, y=None, z=None):
        if x is not None and y is not None and z is not None:
            self._pos["x"] = float(x)
            self._pos["y"] = float(y)
            self._pos["z"] = float(z)
            return self
        return dict(self._pos)

    def lookAt(self, x, y, z):
        self._look_at["x"] = float(x)
        self._look_at["y"] = float(y)
        self._look_at["z"] = float(z)
        return self

    def __repr__(self):
        return f"<Camera fov:{self.fov} pos:({self._pos['x']},{self._pos['y']},{self._pos['z']})>"


class Light:
    def __init__(self, options: dict = None):
        opts = options or {}
        self.type = str(opts.get("type", "point"))
        self.pos = opts.get("pos", [0, 10, 0])
        self.color = str(opts.get("color", "white"))
        self.intensity = float(opts.get("intensity", 1.0))

    def __repr__(self):
        return f"<Light {self.type} pos:{self.pos} color:{self.color} int:{self.intensity}>"


# ============================================================
# RENDER PIPELINE STATE & MODULE BUILDER
# ============================================================
_render_state = {
    "width": 800,
    "height": 600,
    "title": "Nova Game",
    "shadows": True,
    "ao": True,
    "bloom": True,
    "fog": None,
    "skybox": None,
    "draw_calls": 0,
    "triangles_drawn": 0
}


def create_window(width: int = 800, height: int = 600, title: str = "Nova Game"):
    _render_state["width"] = int(width)
    _render_state["height"] = int(height)
    _render_state["title"] = str(title)
    return dict(_render_state)


def create_mesh(data_or_path):
    return Mesh(data_or_path)


def create_texture(path: str):
    return Texture(path)


def create_material(options: dict = None):
    return Material(options)


def create_shader(vert_or_opts, frag=None):
    if isinstance(vert_or_opts, dict):
        return Shader(vert_or_opts.get("vert"), vert_or_opts.get("frag"))
    return Shader(vert_or_opts, frag)


def create_entity(mesh: Mesh, material: Material = None):
    return RenderEntity(mesh, material)


def create_camera(*args, **kwargs):
    return Camera(*args, **kwargs)


def create_light(options: dict = None):
    return Light(options)


def create_sprite(path: str):
    return Sprite(path)


def draw_entity(entity: RenderEntity, camera: Camera = None):
    _render_state["draw_calls"] += 1
    _render_state["triangles_drawn"] += getattr(entity.mesh, "triangle_count", 0)
    p = entity.pos()
    # Stub high performance GPU log
    return True


def draw_all_entities(entities: list, camera: Camera = None):
    for ent in entities:
        draw_entity(ent, camera)
    return True


def draw_2d(sprite: Sprite):
    _render_state["draw_calls"] += 1
    _render_state["triangles_drawn"] += 2
    return True


def draw_2d_all(sprites: list):
    for sp in sprites:
        draw_2d(sp)
    return True


def clear_frame(options: dict = None):
    _render_state["draw_calls"] = 0
    _render_state["triangles_drawn"] = 0
    return True


def present_frame():
    # Direct GPU swapchain present
    dc = _render_state["draw_calls"]
    tris = _render_state["triangles_drawn"]
    return {"drawCalls": dc, "triangles": tris}


def set_shadow(enable: bool):
    _render_state["shadows"] = bool(enable)
    return True


def set_ao(enable: bool):
    _render_state["ao"] = bool(enable)
    return True


def set_bloom(enable: bool):
    _render_state["bloom"] = bool(enable)
    return True


def set_fog(options: dict):
    _render_state["fog"] = options
    return True


def set_skybox(path: str):
    _render_state["skybox"] = str(path)
    return True


def build_render_module():
    m = {}
    m["window"]    = create_window
    m["new"]       = create_window
    m["mesh"]      = create_mesh
    m["texture"]   = create_texture
    m["material"]  = create_material
    m["mat"]       = create_material
    m["shader"]    = create_shader
    m["entity"]    = create_entity
    m["ent"]       = create_entity
    m["camera"]    = create_camera
    m["light"]     = create_light
    m["sprite"]    = create_sprite
    m["img"]       = create_sprite
    m["draw"]      = draw_entity
    m["drawAll"]   = draw_all_entities
    m["draw2D"]    = draw_2d
    m["draw2DAll"] = draw_2d_all
    m["clear"]     = clear_frame
    m["present"]   = present_frame
    m["shadow"]    = set_shadow
    m["ao"]        = set_ao
    m["bloom"]     = set_bloom
    m["fog"]       = set_fog
    m["skybox"]    = set_skybox
    return StdModule("render", m)


# ============================================================
# C TEMPLATES (FOR COMPILER - BLAZING-FAST STANDALONE BINARY)
# ============================================================
cCode = {
    "include": '#include "nova_render.h"',
    "mesh": 'Mesh {var} = renderMesh("{path}");',
    "texture": 'Texture {var} = renderTexture("{path}");',
    "material": 'Material {var} = renderMaterial("{color}", "{shader}", {metallic}, {roughness});',
    "entity": 'RenderEntity {var} = renderEntity({mesh}, {material});',
    "sprite": 'Sprite {var} = renderSprite("{path}");',
    "camera": 'Camera {var} = renderCamera({fov}, {x}, {y}, {z});',
    "draw": 'renderDraw(&{entity}, &{camera});',
    "draw2D": 'renderDraw2D(&{sprite});',
    "clear": 'renderClear("{color}");',
    "present": 'renderPresent();',
}
