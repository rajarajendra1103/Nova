import os
from nova_libs.core import StdModule

# ============================================================
# ASSET OBJECTS
# ============================================================
class Asset:
    def __init__(self, path: str, asset_type: str = "model", size_bytes: int = 1024 * 512):
        self.path = str(path)
        self.type = str(asset_type)
        self.size = int(size_bytes)
        self.is_loaded = True

    def free(self):
        self.is_loaded = False
        self.size = 0
        return True

    def __repr__(self):
        return f"<Asset '{self.path}' type:{self.type} size:{self.size} bytes>"


# ============================================================
# ASSET MANAGER & MEMORY CONTROL
# ============================================================
_loaded_assets = {}


def load_asset(path: str, asset_type: str = "model"):
    path = str(path)
    if path in _loaded_assets and _loaded_assets[path].is_loaded:
        return _loaded_assets[path]

    # Calculate estimated asset size
    size = 1024 * 512
    if path.endswith((".png", ".jpg", ".tga", ".hdr")):
        asset_type = "texture"
        size = 1024 * 1024
    elif path.endswith((".wav", ".mp3", ".ogg")):
        asset_type = "sound"
        size = 1024 * 256
    elif path.endswith((".obj", ".gltf", ".fbx")):
        asset_type = "model"
        size = 1024 * 768

    a = Asset(path, asset_type, size)
    _loaded_assets[path] = a
    return a


def load_model(path: str):
    return load_asset(path, "model")


def load_texture(path: str):
    return load_asset(path, "texture")


def load_sound(path: str):
    return load_asset(path, "sound")


def free_asset(path: str):
    path = str(path)
    if path in _loaded_assets:
        _loaded_assets[path].free()
        del _loaded_assets[path]
        return True
    return False


def free_all_assets():
    for a in list(_loaded_assets.values()):
        a.free()
    _loaded_assets.clear()
    return True


def list_assets():
    return list(_loaded_assets.keys())


def used_assets_mem():
    total_bytes = sum(a.size for a in _loaded_assets.values() if a.is_loaded)
    if total_bytes < 1024:
        return f"{total_bytes} B"
    elif total_bytes < 1024 * 1024:
        return f"{total_bytes / 1024.0:.1f} KB"
    return f"{total_bytes / (1024.0 * 1024.0):.2f} MB"


def build_asset_module():
    m = {}
    m["load"]        = load_asset
    m["loadModel"]   = load_model
    m["loadTexture"] = load_texture
    m["loadSound"]   = load_sound
    m["free"]        = free_asset
    m["freeAll"]     = free_all_assets
    m["list"]        = list_assets
    m["used"]        = used_assets_mem
    return StdModule("asset", m)


# ============================================================
# C TEMPLATES (FOR COMPILER - BLAZING-FAST STANDALONE BINARY)
# ============================================================
cCode = {
    "include": '#include "nova_asset.h"',
    "load": 'Asset {var} = assetLoad("{path}", "{type}");',
    "loadModel": 'Asset {var} = assetLoadModel("{path}");',
    "loadTexture": 'Asset {var} = assetLoadTexture("{path}");',
    "loadSound": 'Asset {var} = assetLoadSound("{path}");',
    "free": 'assetFree("{path}");',
    "freeAll": 'assetFreeAll();',
    "used": 'const char* {var} = assetUsed();',
}
