import sys
import os

# Subpackage exports
from nova_libs.core import (
    StdModule, NovaFile,
    build_math_module, build_string_module, build_list_module,
    build_set_module, build_file_os_module, build_random_module,
    build_time_module, build_json_module
)

from nova_libs.backend import (
    build_backend_module, build_server_module, build_http_module,
    build_auth_module, build_env_module,
    build_cache_module, build_store_module, build_queue_module,
    build_cron_module, build_ws_module, build_mail_module,
    build_valid_module, build_log_module, build_session_module,
    NovaDB, NovaUIElement, NovaAppWindow, NovaRequest, NovaResponse,
    NovaRoute, NovaServerApp, NovaHttpResponse, NovaAsyncTask
)

from nova_libs.ui import (
    build_app_module, NovaAppUnified, get_screen, set_screen,
    build_ui_module, UIElement, ResponsiveManager,
    build_mem_module, MemPool, RawMemBlock
)

from nova_libs.game import (
    build_render_module, RenderEntity, Sprite, Camera, Light, Mesh, Texture, Material, Shader,
    build_game_module, GameApp, GameEntity, GameScene,
    build_physics_module, PhysicsBody, PhysicsWorld,
    build_input_module,
    build_asset_module, Asset,
    build_audio_module, Sound, Music,
    build_net_module, GameHost, GameClient,
    build_anim_module, Skeleton, Bone, AnimationClip, AnimationStateMachine, Tween,
    build_ecs_module, World, Entity, Query, System
)

from nova_libs.data import (
    build_numpy_module, NumpyArray, NovaArray,
    build_pandas_module, NovaDF, NovaGroupedDF,
    build_chart_module, ChartFigure,
    build_viz_module, VizFigure,
    build_ai_module,
    build_scipy_module,
    build_ml_module
)

# ============================================================
# LIBS MAP & DYNAMIC LOADER
# ============================================================
libsMap = {
    # Game & 3D Graphics Engine (nova_libs/game/)
    "render": "render",
    "game": "game",
    "physics": "physics",
    "input": "input",
    "asset": "asset",
    "audio": "audio",
    "sound": "audio",
    "music": "audio",
    "net": "net",
    "network": "net",
    "multiplayer": "net",
    "anim": "anim",
    "animation": "anim",
    "ecs": "ecs",
    "world": "ecs",

    # UI & App & Memory (nova_libs/ui/)
    "app": "app",
    "ui": "ui",
    "mem": "mem",

    # Data, Scientific & AI Libraries (nova_libs/data/)
    "numpy": "numpy",
    "np": "numpy",
    "pandas": "pandas",
    "pd": "pandas",
    "scipy": "scipy",
    "sp": "scipy",
    "ml": "ml",
    "sklearn": "ml",
    "chart": "chart",
    "ch": "chart",
    "viz": "viz",
    "ai": "ai",

    # Backend & Full-Stack (nova_libs/backend/)
    "backend": "backend",
    "be": "backend",
    "server": "server",
    "http": "http",
    "db": "db",
    "auth": "auth",
    "env": "env",
    "cache": "cache",
    "store": "store",
    "queue": "queue",
    "cron": "cron",
    "ws": "ws",
    "mail": "mail",
    "valid": "valid",
    "log": "log",
    "session": "session",

    # Core Standard Libraries (nova_libs/core/)
    "math": "math",
    "string": "string",
    "str": "string",
    "list": "list",
    "set": "set",
    "file": "file",
    "os": "file",
    "random": "random",
    "rand": "random",
    "time": "time",
    "json": "json",
}

_lib_cache = {}

def loadLib(name: str, interp=None):
    clean_name = str(name).strip().lower()
    target = libsMap.get(clean_name, clean_name)

    # Return cached module if already instantiated and doesn't require unique interp instance
    if clean_name in _lib_cache and target not in ("app", "game", "server", "backend", "queue", "cron", "ws", "pandas"):
        return _lib_cache[clean_name]

    mod = None
    # Game
    if target == "render":
        mod = build_render_module()
    elif target == "game":
        mod = build_game_module(interp)
    elif target == "physics":
        mod = build_physics_module(interp)
    elif target == "input":
        mod = build_input_module()
    elif target == "asset":
        mod = build_asset_module()
    elif target in ("audio", "sound", "music"):
        mod = build_audio_module(interp)
    elif target in ("net", "network", "multiplayer"):
        mod = build_net_module(interp)
    elif target in ("anim", "animation"):
        mod = build_anim_module(interp)
    elif target in ("ecs", "world"):
        mod = build_ecs_module(interp)

    # UI & App & Mem
    elif target == "app":
        mod = build_app_module(interp)
    elif target == "ui":
        mod = build_ui_module(interp)
    elif target == "mem":
        mod = build_mem_module(interp)

    # Data & AI
    elif target == "numpy":
        mod = build_numpy_module()
    elif target == "pandas":
        mod = build_pandas_module(interp)
    elif target in ("scipy", "sp"):
        mod = build_scipy_module(interp)
    elif target in ("ml", "sklearn"):
        mod = build_ml_module(interp)
    elif target == "chart":
        mod = build_chart_module()
    elif target == "viz":
        mod = build_viz_module()
    elif target == "ai":
        mod = build_ai_module()

    # Backend
    elif target == "backend":
        mod = build_backend_module(interp)
    elif target == "server":
        mod = build_server_module(interp)
    elif target == "http":
        mod = build_http_module()
    elif target == "db":
        mod = NovaDB()
    elif target == "auth":
        mod = build_auth_module()
    elif target == "env":
        mod = build_env_module()
    elif target == "cache":
        mod = build_cache_module()
    elif target == "store":
        mod = build_store_module()
    elif target == "queue":
        mod = build_queue_module(interp)
    elif target == "cron":
        mod = build_cron_module(interp)
    elif target == "ws":
        mod = build_ws_module(interp)
    elif target == "mail":
        mod = build_mail_module()
    elif target == "valid":
        mod = build_valid_module()
    elif target == "log":
        mod = build_log_module()
    elif target == "session":
        mod = build_session_module()

    # Core
    elif target == "math":
        mod = build_math_module()
    elif target == "string":
        mod = build_string_module()
    elif target == "list":
        mod = build_list_module()
    elif target == "set":
        mod = build_set_module()
    elif target == "file":
        mod = build_file_os_module()
    elif target == "random":
        mod = build_random_module()
    elif target == "time":
        mod = build_time_module()
    elif target == "json":
        mod = build_json_module()

    if mod is not None:
        _lib_cache[clean_name] = mod
        return mod

    return None


# ============================================================
# C TEMPLATE LOADER (FOR COMPILER CODE GENERATION)
# ============================================================
def loadCCode(name: str):
    clean_name = str(name).strip().lower()
    target = libsMap.get(clean_name, clean_name)
    try:
        if target in ("numpy", "np"):
            from nova_libs.data.numpy import cCode; return cCode
        elif target in ("pandas", "pd"):
            from nova_libs.data.pandas import cCode; return cCode
        elif target in ("scipy", "sp"):
            from nova_libs.data.scipy import cCode; return cCode
        elif target in ("ml", "sklearn"):
            from nova_libs.data.ml import cCode; return cCode
        elif target in ("chart", "ch"):
            from nova_libs.data.chart import cCode; return cCode
        elif target == "viz":
            from nova_libs.data.viz import cCode; return cCode
        elif target == "ai":
            from nova_libs.data.ai import cCode; return cCode
        elif target in ("backend", "be", "server", "db", "auth", "log"):
            from nova_libs.backend.backend import cCode; return cCode
        elif target == "app":
            from nova_libs.ui.app import cCode; return cCode
        elif target == "ui":
            from nova_libs.ui.ui import cCode; return cCode
        elif target == "mem":
            from nova_libs.ui.mem import cCode; return cCode
        elif target == "game":
            from nova_libs.game.game import cCode; return cCode
        elif target == "render":
            from nova_libs.game.render import cCode; return cCode
        elif target == "physics":
            from nova_libs.game.physics import cCode; return cCode
        elif target == "input":
            from nova_libs.game.input import cCode; return cCode
        elif target == "asset":
            from nova_libs.game.asset import cCode; return cCode
        elif target in ("audio", "sound", "music"):
            from nova_libs.game.audio import cCode; return cCode
        elif target in ("net", "network", "multiplayer"):
            from nova_libs.game.net import cCode; return cCode
        elif target in ("anim", "animation"):
            from nova_libs.game.anim import cCode; return cCode
        elif target in ("ecs", "world"):
            from nova_libs.game.ecs import cCode; return cCode
        elif target in ("math", "time", "random", "json", "file", "string", "list", "set"):
            from nova_libs.core.core import cCode; return cCode
    except Exception:
        pass
    return {}
