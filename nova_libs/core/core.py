import math
import random
import time
import os
import json
import re
import datetime
import string as py_string
import uuid

# ============================================================
# STANDARD MODULE WRAPPER
# ============================================================
class StdModule:
    def __init__(self, name: str, exports: dict):
        self._name = name
        self._exports = exports
        for k, v in exports.items(): setattr(self, k, v)
    def __repr__(self): return f"<module '{self._name}'>"
    def __getitem__(self, item): return self._exports[item]
    def __iter__(self): return iter(self._exports)


def _is_prime(n):
    if n < 2: return False
    if n in (2, 3): return True
    if n % 2 == 0 or n % 3 == 0: return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0: return False
        i += 6
    return True

def _nth_prime(n):
    count = 0; candidate = 1
    while count < n:
        candidate += 1
        if _is_prime(candidate): count += 1
    return candidate


# ============================================================
# 1. MATH MODULE
# ============================================================
def build_math_module():
    m = {}
    m["PI"]   = math.pi
    m["pi"]   = math.pi
    m["E"]    = math.e
    m["e"]    = math.e
    m["TAU"]  = math.tau
    m["tau"]  = math.tau
    m["PHI"]  = 1.618033988749895
    m["phi"]  = 1.618033988749895
    m["INF"]  = math.inf
    m["inf"]  = math.inf
    m["NAN"]  = math.nan
    m["nan"]  = math.nan

    m["abs"]   = abs
    m["round"] = lambda x, n=0: round(x, int(n)) if n else round(x)
    m["floor"] = math.floor
    m["ceil"]  = math.ceil
    m["min"]   = lambda *args: min(args[0]) if len(args)==1 and isinstance(args[0],(list,tuple,set)) else min(args)
    m["max"]   = lambda *args: max(args[0]) if len(args)==1 and isinstance(args[0],(list,tuple,set)) else max(args)
    m["sum"]   = lambda c: sum(c)
    m["avg"]   = lambda c: (sum(c)/len(c)) if c else 0.0
    m["prod"]  = lambda c: math.prod(c) if c else 0
    m["sqrt"]  = math.sqrt
    m["root"]  = math.sqrt
    m["pow"]   = lambda b, e: b ** e
    m["power"] = lambda b, e: b ** e
    m["range"] = lambda a, b, s=1: list(range(int(a), int(b)+1, int(s)))

    m["sin"]   = math.sin
    m["cos"]   = math.cos
    m["tan"]   = math.tan
    m["asin"]  = math.asin
    m["acos"]  = math.acos
    m["atan"]  = math.atan
    m["atan2"] = math.atan2
    m["sinh"]  = math.sinh
    m["cosh"]  = math.cosh
    m["tanh"]  = math.tanh
    m["toRad"] = math.radians
    m["rad"]   = math.radians
    m["toDeg"] = math.degrees
    m["deg"]   = math.degrees

    m["exp"]     = math.exp
    m["log"]     = lambda x, b=math.e: math.log(x) if b==math.e else math.log(x, b)
    m["log10"]   = math.log10
    m["log2"]    = math.log2
    m["logBase"] = lambda x, b: math.log(x, b)
    m["exp2"]    = lambda x: 2.0 ** x
    m["expm1"]   = math.expm1
    m["log1p"]   = math.log1p

    m["mod"]     = lambda a, b: a % b
    m["gcd"]     = math.gcd
    m["lcm"]     = math.lcm
    m["fact"]    = math.factorial
    m["perm"]    = math.perm
    m["comb"]    = math.comb

    m["isEven"]  = lambda n: n % 2 == 0
    m["isOdd"]   = lambda n: n % 2 != 0
    m["isPrime"] = _is_prime
    m["prime"]   = _nth_prime
    m["clamp"]   = lambda v, lo, hi: max(lo, min(hi, v))
    m["lerp"]    = lambda a, b, t: a + (b - a) * t
    m["sign"]    = lambda x: 1 if x > 0 else (-1 if x < 0 else 0)
    m["dist"]    = lambda p1, p2: math.dist(p1, p2)
    m["hypot"]   = math.hypot
    m["cbrt"]    = math.cbrt
    m["nroot"]   = lambda x, n: x ** (1.0 / n)
    m["trunc"]   = math.trunc
    m["frac"]    = lambda x: x - math.floor(x)

    return StdModule("math", m)


# ============================================================
# 2. STRING MODULE
# ============================================================
def build_string_module():
    m = {}
    m["digits"]    = py_string.digits
    m["ascii"]     = py_string.ascii_letters
    m["size"]      = len
    m["len"]       = len
    m["upper"]     = lambda s: s.upper()
    m["lower"]     = lambda s: s.lower()
    m["title"]     = lambda s: s.title()
    m["cap"]       = lambda s: s.capitalize()
    m["swap"]      = lambda s: s.swapcase()
    m["trim"]      = lambda s, chars=None: s.strip(chars)
    m["trimL"]     = lambda s, chars=None: s.lstrip(chars)
    m["trimR"]     = lambda s, chars=None: s.rstrip(chars)
    m["trimAll"]   = lambda s: " ".join(s.split())
    m["padL"]      = lambda s, w, fill=" ": str(s).rjust(int(w), fill)
    m["padR"]      = lambda s, w, fill=" ": str(s).ljust(int(w), fill)
    m["center"]    = lambda s, w, fill=" ": str(s).center(int(w), fill)
    m["zfill"]     = lambda s, w: str(s).zfill(int(w))
    m["has"]       = lambda s, sub: sub in s
    m["hasI"]      = lambda s, sub: sub.lower() in s.lower()
    m["startsWith"]= lambda s, p: s.startswith(p)
    m["starts"]    = lambda s, p: s.startswith(p)
    m["endsWith"]  = lambda s, suf: s.endswith(suf)
    m["ends"]      = lambda s, suf: s.endswith(suf)
    m["find"]      = lambda s, sub, start=0: s.find(sub, int(start))
    m["findL"]     = lambda s, sub: s.rfind(sub)
    m["count"]     = lambda s, sub: s.count(sub)
    m["replace"]   = lambda s, old, new, count=-1: s.replace(old, new, int(count)) if count>=0 else s.replace(old, new)
    m["split"]     = lambda s, sep=None, maxsplit=-1: s.split(sep, int(maxsplit)) if maxsplit>=0 else s.split(sep)
    m["words"]     = lambda s: s.split()
    m["join"]      = lambda s, iterable: s.join(iterable)
    m["repeat"]    = lambda s, n: s * int(n)
    m["rev"]       = lambda s: s[::-1]
    m["reverse"]   = lambda s: s[::-1]
    m["sub"]       = lambda s, start, end=None: s[int(start):int(end)] if end is not None else s[int(start):]
    m["char"]      = lambda s, i: s[int(i)]
    m["codeAt"]    = lambda s, i=0: ord(s[int(i)])
    m["charCode"]  = lambda s, i=0: ord(s[int(i)])
    m["fromCode"]  = lambda code: chr(int(code))
    m["chars"]     = lambda s: list(s)
    m["isEmpty"]   = lambda s: len(s) == 0
    m["wordC"]     = lambda s: len(s.split())
    m["lineC"]     = lambda s: len(s.splitlines())
    m["charC"]     = lambda s: len(s)
    return StdModule("string", m)


# ============================================================
# 3. LIST MODULE
# ============================================================
def build_list_module():
    m = {}
    m["range"]    = lambda a, b=None, s=1: list(range(int(a), int(b)) if b is not None else range(int(a)))
    m["size"]     = len
    m["len"]      = len
    m["has"]      = lambda l, x: x in l
    m["hasAll"]   = lambda l, items: all(x in l for x in items)
    m["hasAny"]   = lambda l, items: any(x in l for x in items)
    m["find"]     = lambda l, x: l.index(x) if x in l else -1
    m["count"]    = lambda l, x: l.count(x)
    m["first"]    = lambda l: l[0] if l else None
    m["last"]     = lambda l: l[-1] if l else None
    m["at"]       = lambda l, i: l[int(i)]
    m["add"]      = lambda l, x: l.append(x) or l
    m["remove"]   = lambda l, x: l.remove(x) or l if x in l else l
    m["clear"]    = lambda l: l.clear() or l
    m["sort"]     = lambda l: l.sort() or l
    m["dsort"]    = lambda l: l.sort(reverse=True) or l
    m["sorted"]   = lambda l: sorted(l)
    m["dsorted"]  = lambda l: sorted(l, reverse=True)
    m["reverse"]  = lambda l: l.reverse() or l
    m["reversed"] = lambda l: l[::-1]
    m["shuffle"]  = lambda l: random.shuffle(l) or l
    m["filter"]   = lambda l, fn: [x for x in l if fn(x)]
    m["map"]      = lambda l, fn: [fn(x) for x in l]
    m["flat"]     = lambda l: [item for sub in l for item in (sub if isinstance(sub, (list, tuple)) else [sub])]
    m["slice"]    = lambda l, s, e: l[int(s):int(e)]
    m["chunk"]    = lambda l, n=1: [list(l)[i:i+int(n)] for i in range(0, len(l), int(n))]
    m["window"]   = lambda l, n=2: [list(l)[i:i+int(n)] for i in range(len(l) - int(n) + 1)]
    m["unique"]   = lambda l: list(dict.fromkeys(l))
    m["freq"]     = lambda l: {x: l.count(x) for x in set(l)}
    m["sum"]      = lambda l: sum(l)
    m["avg"]      = lambda l: sum(l) / len(l) if l else 0.0
    m["max"]      = lambda l: max(l) if l else None
    m["min"]      = lambda l: min(l) if l else None
    m["prod"]     = lambda l: math.prod(l) if l else 0
    m["join"]     = lambda l, sep="": str(sep).join(str(x) for x in l)
    m["zip"]      = lambda l, other: list(zip(l, other))
    m["toSet"]    = lambda l: set(l)
    m["toMap"]    = lambda l: dict(l)
    m["isEmpty"]  = lambda l: len(l) == 0
    return StdModule("list", m)


# ============================================================
# 4. SET MODULE
# ============================================================
def build_set_module():
    m = {}
    m["size"]       = len
    m["len"]        = len
    m["empty"]      = lambda: set()
    m["has"]        = lambda s, x: x in s
    m["add"]        = lambda s, x: s.add(x) or s
    m["remove"]     = lambda s, x: s.discard(x) or s
    m["clear"]      = lambda s: s.clear() or s
    m["union"]      = lambda s, other: s | set(other)
    m["U"]          = lambda s, other: s | set(other)
    m["inter"]      = lambda s, other: s & set(other)
    m["N"]          = lambda s, other: s & set(other)
    m["diff"]       = lambda s, other: s - set(other)
    m["symDiff"]    = lambda s, other: s ^ set(other)
    m["isSubset"]   = lambda s, other: s.issubset(set(other))
    m["isSub"]      = lambda s, other: s.issubset(set(other))
    m["isSuperset"] = lambda s, other: s.issuperset(set(other))
    m["isDisjoint"] = lambda s, other: s.isdisjoint(set(other))
    m["toList"]     = lambda s: list(s)
    m["cart"]       = lambda s1, s2: [(a, b) for a in s1 for b in s2]
    m["isEmpty"]    = lambda s: len(s) == 0
    return StdModule("set", m)


# ============================================================
# 5. FILE & OS MODULE
# ============================================================
class NovaFile:
    def __init__(self, path: str, mode: str = "read"):
        self.path = os.path.expanduser(str(path))
        self.mode = str(mode).lower()
        self._f = None
        self._open()

    def _open(self):
        m = "r"
        if self.mode in ("write", "w"): m = "w"
        elif self.mode in ("append", "a"): m = "a"
        elif self.mode in ("readwrite", "rw", "r+"): m = "r+"
        try:
            self._f = open(self.path, m, encoding="utf-8", errors="replace")
        except Exception:
            self._f = None

    def read(self, n: int = -1):
        if not self._f: self._open()
        return self._f.read(int(n)) if self._f else ""

    def readLine(self):
        if not self._f: self._open()
        return self._f.readline() if self._f else ""

    def write(self, s: str):
        if not self._f: self._open()
        if self._f:
            self._f.write(str(s))
            self._f.flush()
        return self

    def append(self, s: str):
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(str(s))
        return self

    def close(self):
        if self._f:
            self._f.close()
            self._f = None
        return True

    def exists(self): return os.path.exists(self.path)
    def size(self): return os.path.getsize(self.path) if os.path.exists(self.path) else 0
    def delete(self):
        self.close()
        if os.path.exists(self.path): os.remove(self.path); return True
        return False

    def __enter__(self): return self
    def __exit__(self, *args): self.close()
    def __repr__(self): return f"<file '{self.path}'>"


def build_file_os_module():
    m = {}
    def _read(path, mode="utf8"):
        p = os.path.expanduser(str(path))
        with open(p, "r", encoding="utf-8" if mode=="utf8" else None, errors="replace") as f:
            return f.read()

    def _write(path, content, mode="utf8"):
        p = os.path.expanduser(str(path))
        os.makedirs(os.path.dirname(os.path.abspath(p)), exist_ok=True)
        with open(p, "w", encoding="utf-8" if mode=="utf8" else None) as f:
            f.write(str(content))
        return True

    m["read"]        = _read
    m["readA"]       = _read
    m["write"]       = _write
    m["writeA"]      = _write
    m["append"]      = lambda p, c: open(p, "a", encoding="utf-8").write(str(c)) and True
    m["open"]        = lambda p, mode="read": NovaFile(p, mode)
    m["exists"]      = lambda p: os.path.exists(os.path.expanduser(str(p)))
    m["size"]        = lambda p: os.path.getsize(os.path.expanduser(str(p)))
    m["lineC"]       = lambda p: len(_read(p).splitlines())
    m["hasText"]     = lambda p, s: s in _read(p)
    m["remove"]      = lambda p: os.remove(os.path.expanduser(str(p))) or True
    m["delete"]      = lambda p: os.remove(os.path.expanduser(str(p))) or True
    m["pwd"]         = os.getcwd
    m["cwd"]         = os.getcwd
    m["cd"]          = lambda p: os.chdir(os.path.expanduser(str(p))) or os.getcwd()
    return StdModule("file", m)


# ============================================================
# 6. RANDOM MODULE
# ============================================================
def build_random_module():
    m = {}
    m["random"]  = random.random
    m["rand"]    = random.random
    m["int"]     = lambda a, b: random.randint(int(a), int(b))
    m["float"]   = lambda a, b: random.uniform(float(a), float(b))
    m["pick"]    = lambda seq: random.choice(list(seq))
    m["pickN"]   = lambda seq, k: random.sample(list(seq), int(k))
    m["str"]     = lambda n=8: "".join(random.choices(py_string.ascii_letters + py_string.digits, k=int(n)))
    m["otp"]     = lambda n=6: "".join(random.choices(py_string.digits, k=int(n)))
    m["pass"]    = lambda n=10: "".join(random.choices(py_string.ascii_letters + py_string.digits + "!@#$%", k=int(n)))
    m["dice"]    = lambda: random.randint(1, 6)
    m["coin"]    = lambda: random.choice(["Heads", "Tails"])
    m["card"]    = lambda: f"{random.choice(['A','2','3','4','5','6','7','8','9','10','J','Q','K'])} of {random.choice(['Hearts','Diamonds','Clubs','Spades'])}"
    m["uuid"]    = lambda: str(uuid.uuid4())
    m["seed"]    = lambda s: random.seed(s)
    m["bool"]    = lambda: random.choice([True, False])
    return StdModule("random", m)


# ============================================================
# 7. TIME MODULE
# ============================================================
def build_time_module():
    m = {}
    m["now"]      = time.time
    m["date"]     = lambda: time.strftime("%Y-%m-%d")
    m["stamp"]    = lambda: int(time.time())
    m["stampM"]   = lambda: int(time.time() * 1000)
    m["sleep"]    = lambda s: time.sleep(float(s))
    m["sleepM"]   = lambda ms: time.sleep(float(ms) / 1000.0)
    m["year"]     = lambda: time.localtime().tm_year
    m["isLeap"]   = lambda y: (y % 4 == 0 and y % 100 != 0) or (y % 400 == 0)
    m["addDay"]   = lambda t, d: float(t) + float(d) * 86400
    m["subYear"]  = lambda t, y: float(t) - float(y) * 365.25 * 86400
    m["format"]   = lambda t=None, fmt="%Y-%m-%d": (lambda ts: datetime.datetime.fromtimestamp(float(ts)).strftime(fmt.replace("YYYY","%Y").replace("MM","%m").replace("DD","%d")))(t if t is not None else time.time())
    m["timer"]    = time.time
    m["elapsed"]  = lambda t0: time.time() - float(t0)
    m["age"]      = lambda d_str: (datetime.datetime.now() - datetime.datetime.strptime(str(d_str), "%Y-%m-%d")).days / 365.25
    return StdModule("time", m)


# ============================================================
# 8. JSON MODULE
# ============================================================
def build_json_module():
    m = {}
    m["parse"]     = lambda s: json.loads(s)
    m["map"]       = lambda s: json.loads(s)
    m["stringify"] = lambda obj, indent=None: json.dumps(obj, indent=int(indent) if indent else None)
    m["text"]      = lambda obj: json.dumps(obj)
    m["valid"]     = lambda s: (lambda: True if json.loads(s) is not None else True)()
    def _is_valid(s):
        try: json.loads(s); return True
        except Exception: return False
    m["isValid"]   = _is_valid

    def _get_path(obj, path_str):
        cur = obj
        for p in str(path_str).split("."):
            if isinstance(cur, dict): cur = cur.get(p)
            elif isinstance(cur, list) and p.isdigit(): cur = cur[int(p)]
            else: return None
        return cur

    def _set_path(obj, path_str, val):
        parts = str(path_str).split(".")
        cur = obj
        for p in parts[:-1]:
            if p not in cur or not isinstance(cur[p], dict): cur[p] = {}
            cur = cur[p]
        cur[parts[-1]] = val
        return obj

    def _flat(d, parent_key='', sep='.'):
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(_flat(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)

    def _diff(d1, d2):
        res = {}
        for k, v in d2.items():
            if k not in d1 or d1[k] != v: res[k] = v
        return res

    def _patch(d1, diff_obj):
        res = dict(d1)
        res.update(diff_obj)
        return res

    m["getPath"] = _get_path
    m["setPath"] = _set_path
    m["flat"]    = _flat
    m["diff"]    = _diff
    m["patch"]   = _patch

    return StdModule("json", m)


# ============================================================
# C TEMPLATES (FOR COMPILER - BLAZING-FAST STANDALONE BINARY)
# ============================================================
cCode = {
    "include": '#include "nova_runtime.h"',
    "root": 'float {var} = sqrtf({x});',
    "power": 'float {var} = powf({base}, {exp});',
    "sin": 'float {var} = sinf({x});',
    "cos": 'float {var} = cosf({x});',
    "tan": 'float {var} = tanf({x});',
    "abs": 'float {var} = fabsf({x});',
    "floor": 'float {var} = floorf({x});',
    "ceil": 'float {var} = ceilf({x});',
    "round": 'float {var} = roundf({x});',
    "now": 'double {var} = (double)time(NULL);',
    "date": 'const char* {var} = "2026-08-23";',
    "year": 'int {var} = 2026;',
    "int": 'int {var} = (rand() % ({max} - {min} + 1)) + {min};',
    "bool": 'bool {var} = (rand() % 2) == 1;',
}
