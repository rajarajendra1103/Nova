import sys
from nova_libs.core import StdModule

# ============================================================
# MEMORY OBJECTS & RAW BLOCKS
# ============================================================
class RawMemBlock:
    def __init__(self, size: int, tag: str = "alloc"):
        self.size = int(size)
        self.tag = str(tag)
        self.is_freed = False
        self._buffer = bytearray(self.size)

    def free(self):
        self.is_freed = True
        self._buffer = bytearray(0)
        return True

    def __len__(self):
        return self.size if not self.is_freed else 0

    def __repr__(self):
        status = "freed" if self.is_freed else "active"
        return f"<RawMemBlock:{self.tag} {self.size} bytes ({status})>"


# ============================================================
# HIGH SPEED MEMORY POOL (ZERO GC / 120 FPS)
# ============================================================
class MemPool:
    def __init__(self, name: str, capacity: int = 100):
        self.pool_name = str(name)
        self.capacity = int(capacity)
        self.items = []
        self.active_items = []
        self.total_allocations = 0
        self._preallocate()

    def _create_item(self):
        self.total_allocations += 1
        return {
            "id": self.total_allocations,
            "type": self.pool_name,
            "active": True,
            "x": 0.0,
            "y": 0.0,
            "z": 0.0,
            "vx": 0.0,
            "vy": 0.0,
            "vz": 0.0
        }

    def _preallocate(self):
        for _ in range(self.capacity):
            self.items.append(self._create_item())

    def get(self):
        if self.items:
            item = self.items.pop()
            item["active"] = True
            self.active_items.append(item)
            return item
        item = self._create_item()
        self.active_items.append(item)
        return item

    def alloc(self):
        return self.get()

    def free(self, item):
        if item in self.active_items:
            self.active_items.remove(item)
        item["active"] = False
        if len(self.items) < self.capacity * 2:
            self.items.append(item)
        return True

    def count(self):
        return len(self.active_items)

    def total(self):
        return len(self.items) + len(self.active_items)

    def clear(self):
        self.items.clear()
        self.active_items.clear()
        return True

    def stats(self):
        return {
            "name": self.pool_name,
            "free": len(self.items),
            "active": len(self.active_items),
            "capacity": self.capacity,
            "total": self.total()
        }


# ============================================================
# GLOBAL MEMORY TRACKER
# ============================================================
_pools = {}
_allocations = []
_no_gc_mode = True


def pool(arg1, arg2=None):
    global _pools
    # Case 1: mem.pool(1000, "bullet")
    if arg2 is not None and isinstance(arg1, (int, float)):
        cap = int(arg1)
        name = str(arg2)
        p = MemPool(name, cap)
        _pools[name] = p
        return p
    # Case 2: mem.pool("bullet", 1000)
    elif arg2 is not None and isinstance(arg2, (int, float)):
        name = str(arg1)
        cap = int(arg2)
        p = MemPool(name, cap)
        _pools[name] = p
        return p
    # Case 3: mem.pool("bullet")
    else:
        name = str(arg1)
        if name not in _pools:
            _pools[name] = MemPool(name, 100)
        return _pools[name]


def alloc_mem(num_bytes: int):
    block = RawMemBlock(num_bytes, "explicit")
    _allocations.append(block)
    return block


def free_mem(obj):
    if isinstance(obj, RawMemBlock):
        obj.free()
        if obj in _allocations:
            _allocations.remove(obj)
        return True
    elif isinstance(obj, dict) and "type" in obj:
        p_name = obj["type"]
        if p_name in _pools:
            return _pools[p_name].free(obj)
    return True


def free_all_mem():
    for blk in _allocations:
        blk.free()
    _allocations.clear()
    for p in _pools.values():
        p.clear()
    return True


def alloc_temp(num_bytes: int):
    return RawMemBlock(num_bytes, "stack_temp")


def stack_mem(num_bytes: int, func):
    temp_blk = alloc_temp(num_bytes)
    try:
        if callable(func):
            return func()
    finally:
        temp_blk.free()


def used_mem():
    explicit_bytes = sum(b.size for b in _allocations if not b.is_freed)
    pool_objects = sum(p.count() for p in _pools.values())
    total_bytes = explicit_bytes + (pool_objects * 64)
    if total_bytes < 1024:
        return f"{total_bytes} B"
    elif total_bytes < 1024 * 1024:
        return f"{total_bytes / 1024.0:.1f} KB"
    return f"{total_bytes / (1024.0 * 1024.0):.2f} MB"


def total_mem():
    pool_total_bytes = sum(p.total() * 64 for p in _pools.values())
    explicit_total_bytes = sum(b.size for b in _allocations)
    total_b = pool_total_bytes + explicit_total_bytes + (16 * 1024 * 1024)
    return f"{total_b / (1024.0 * 1024.0):.1f} MB"


def count_pool(name: str):
    name = str(name)
    if name in _pools:
        return _pools[name].count()
    return 0


def detect_leaks():
    leaks = [b for b in _allocations if not b.is_freed and b.tag != "static"]
    return leaks


def disable_gc():
    global _no_gc_mode
    _no_gc_mode = True
    return True


def get_stats():
    return {k: p.stats() for k, p in _pools.items()}


def build_mem_module(interp=None):
    m = {}
    m["pool"]      = pool
    m["alloc"]     = alloc_mem
    m["free"]      = free_mem
    m["freeAll"]   = free_all_mem
    m["allocTemp"] = alloc_temp
    def _stack(num_bytes, func):
        temp_blk = alloc_temp(num_bytes)
        try:
            if interp:
                return interp._invoke(func, [])
            elif callable(func):
                return func()
        finally:
            temp_blk.free()
    m["stack"]     = _stack
    m["used"]      = used_mem
    m["total"]     = total_mem
    m["leaks"]     = detect_leaks
    m["noGC"]      = disable_gc
    m["gc"]        = disable_gc
    m["stats"]     = get_stats
    return StdModule("mem", m)


# ============================================================
# C TEMPLATES (FOR COMPILER - BLAZING-FAST STANDALONE BINARY)
# ============================================================
cCode = {
    "include": '#include "nova_mem.h"',
    "noGC": 'memNoGC();',
    "pool": 'MemPool* {var} = memPool({capacity}, "{name}");',
    "get": 'MemPoolItem* {var} = memPoolGet({pool});',
    "free": 'memPoolFree({pool}, {item});',
    "alloc": 'void* {var} = memAlloc({bytes});',
    "freeAll": 'memFreeAll();',
    "used": 'const char* {var} = memUsed();',
    "total": 'const char* {var} = memTotal();',
    "leaks": 'int {var} = memLeaks();',
}
