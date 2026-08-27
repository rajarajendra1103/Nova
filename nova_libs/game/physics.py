from nova_libs.core import StdModule

# ============================================================
# PHYSICS RIGIDBODY
# ============================================================
class PhysicsBody:
    def __init__(self, options: dict = None):
        opts = options or {}
        self.mass = float(opts.get("mass", 1.0))
        self.shape = str(opts.get("shape", "box"))
        self.size = opts.get("size", [1.0, 1.0, 1.0])
        p = opts.get("pos", [0.0, 0.0, 0.0])
        self._pos = {"x": float(p[0]), "y": float(p[1]), "z": float(p[2])} if isinstance(p, (list, tuple)) and len(p)>=3 else {"x": 0.0, "y": 0.0, "z": 0.0}
        self.vel = {"x": 0.0, "y": 0.0, "z": 0.0}
        self.force = {"x": 0.0, "y": 0.0, "z": 0.0}
        self.is_static = self.mass <= 0.0

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

    def applyForce(self, force):
        if isinstance(force, (list, tuple)) and len(force) >= 3:
            self.force["x"] += float(force[0])
            self.force["y"] += float(force[1])
            self.force["z"] += float(force[2])
        elif isinstance(force, dict):
            self.force["x"] += float(force.get("x", 0))
            self.force["y"] += float(force.get("y", 0))
            self.force["z"] += float(force.get("z", 0))
        return self

    def applyImpulse(self, impulse):
        if not self.is_static and self.mass > 0:
            if isinstance(impulse, (list, tuple)) and len(impulse) >= 3:
                self.vel["x"] += float(impulse[0]) / self.mass
                self.vel["y"] += float(impulse[1]) / self.mass
                self.vel["z"] += float(impulse[2]) / self.mass
            elif isinstance(impulse, dict):
                self.vel["x"] += float(impulse.get("x", 0)) / self.mass
                self.vel["y"] += float(impulse.get("y", 0)) / self.mass
                self.vel["z"] += float(impulse.get("z", 0)) / self.mass
        return self

    def __repr__(self):
        return f"<PhysicsBody shape:{self.shape} mass:{self.mass} pos:({self._pos['x']}, {self._pos['y']}, {self._pos['z']})>"


# ============================================================
# PHYSICS WORLD
# ============================================================
class PhysicsWorld:
    def __init__(self, options: dict = None):
        opts = options or {}
        g = opts.get("gravity", [0.0, -9.8, 0.0])
        self.gravity = {"x": float(g[0]), "y": float(g[1]), "z": float(g[2])} if isinstance(g, (list, tuple)) else {"x": 0.0, "y": -9.8, "z": 0.0}
        self.bodies = []
        self.collision_handlers = []

    def add(self, body: PhysicsBody):
        if body not in self.bodies:
            self.bodies.append(body)
        return self

    def onCollide(self, func):
        self.collision_handlers.append(func)
        return self

    def update(self, dt: float = 0.016):
        dt = float(dt)
        for b in self.bodies:
            if not b.is_static:
                # Apply gravity
                b.vel["x"] += self.gravity["x"] * dt
                b.vel["y"] += self.gravity["y"] * dt
                b.vel["z"] += self.gravity["z"] * dt

                # Apply force
                if b.mass > 0:
                    b.vel["x"] += (b.force["x"] / b.mass) * dt
                    b.vel["y"] += (b.force["y"] / b.mass) * dt
                    b.vel["z"] += (b.force["z"] / b.mass) * dt

                # Integrate position
                b._pos["x"] += b.vel["x"] * dt
                b._pos["y"] += b.vel["y"] * dt
                b._pos["z"] += b.vel["z"] * dt

                # Reset forces
                b.force = {"x": 0.0, "y": 0.0, "z": 0.0}
        return self

    def step(self, dt: float = 0.016):
        return self.update(dt)

    def tick(self, dt: float = 0.016):
        return self.update(dt)


# ============================================================
# MODULE BUILDER
# ============================================================
_global_world = PhysicsWorld()

def build_physics_module(interp=None):
    m = {}

    def _world(options=None):
        global _global_world
        _global_world = PhysicsWorld(options or {})
        return _global_world

    def _body(options=None):
        b = PhysicsBody(options or {})
        _global_world.add(b)
        return b

    def _box(options=None):
        opts = dict(options) if options else {}
        opts["shape"] = "box"
        return _body(opts)

    def _sphere(options=None):
        opts = dict(options) if options else {}
        opts["shape"] = "sphere"
        return _body(opts)

    def _mesh(options=None):
        opts = dict(options) if options else {}
        opts["shape"] = "mesh"
        return _body(opts)

    m["world"]     = _world
    m["new"]       = _world
    m["body"]      = _body
    m["box"]       = _box
    m["sphere"]    = _sphere
    m["mesh"]      = _mesh
    m["onCollide"] = lambda func: _global_world.onCollide(func)
    m["update"]    = lambda dt=0.016: _global_world.update(dt)
    return StdModule("physics", m)


# ============================================================
# C TEMPLATES (FOR COMPILER - BLAZING-FAST STANDALONE BINARY)
# ============================================================
cCode = {
    "include": '#include "nova_physics.h"',
    "body": 'PhysicsBody {var} = physicsBody({mass}, "{shape}", {x}, {y}, {z});',
    "box": 'PhysicsBody {var} = physicsBody({mass}, "box", {x}, {y}, {z});',
    "sphere": 'PhysicsBody {var} = physicsBody({mass}, "sphere", {x}, {y}, {z});',
    "applyForce": 'physicsApplyForce(&{body}, {fx}, {fy}, {fz});',
    "applyImpulse": 'physicsApplyImpulse(&{body}, {ix}, {iy}, {iz});',
    "update": 'physicsUpdate({dt});',
}
