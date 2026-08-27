import math
import random
from nova_libs.core import StdModule

class CallableList(list):
    def __call__(self):
        return self

# ============================================================
# NUMPY / NP - ARRAY COMPUTING ENGINE
# ============================================================
class NumpyArray:
    def __init__(self, data):
        if isinstance(data, NumpyArray):
            self.data = [x for x in data.data]
            self.shape = CallableList(data.shape)
        elif isinstance(data, (list, tuple)):
            self.data, s = self._parse_nested(data)
            self.shape = CallableList(s)
        else:
            self.data = [data]
            self.shape = CallableList([1])
        self.size = len(self.flat_list())
        self.len = self.shape[0] if self.shape else 0

    def _parse_nested(self, d):
        if not isinstance(d, (list, tuple)):
            return d, []
        if len(d) == 0:
            return [], [0]
        first = d[0]
        if isinstance(first, (list, tuple)):
            sub_shape = None
            parsed = []
            for item in d:
                p, s = self._parse_nested(item)
                parsed.append(p)
                if sub_shape is None: sub_shape = s
            return parsed, [len(d)] + sub_shape
        else:
            return list(d), [len(d)]

    def flat_list(self):
        def _f(x):
            if isinstance(x, (list, tuple)):
                res = []
                for item in x: res.extend(_f(item))
                return res
            return [x]
        return _f(self.data)

    def flat(self):
        return NumpyArray(self.flat_list())

    def toList(self):
        return self.data

    def tolist(self):
        return self.data

    @property
    def T(self):
        return self.transpose()

    def transpose(self):
        if len(self.shape) <= 1:
            return NumpyArray(self.data)
        if len(self.shape) == 2:
            r, c = self.shape
            t_data = [[self.data[i][j] for i in range(r)] for j in range(c)]
            return NumpyArray(t_data)
        raise ValueError("Transpose supported up to 2D")

    def trans(self): return self.transpose()

    def reshape(self, new_shape):
        if isinstance(new_shape, (int, float)): new_shape = [int(new_shape)]
        elif isinstance(new_shape, (list, tuple)): new_shape = [int(s) for s in new_shape]
        flat = self.flat_list()
        total = 1
        for s in new_shape: total *= s
        if total != len(flat):
            raise ValueError(f"Cannot reshape array of size {len(flat)} into shape {new_shape}")
        
        def _build(shape, idx):
            if len(shape) == 1:
                return flat[idx:idx+shape[0]], idx + shape[0]
            res = []
            cur_idx = idx
            for _ in range(shape[0]):
                sub, cur_idx = _build(shape[1:], cur_idx)
                res.append(sub)
            return res, cur_idx

        new_data, _ = _build(new_shape, 0)
        return NumpyArray(new_data)

    def get(self, *indices):
        cur = self.data
        for idx in indices:
            cur = cur[int(idx)]
        return NumpyArray(cur) if isinstance(cur, list) else cur

    def set(self, *args):
        if len(args) < 2: return self
        val = args[-1]
        val = val.data if isinstance(val, NumpyArray) else val
        indices = [int(x) for x in args[:-1]]
        cur = self.data
        for idx in indices[:-1]:
            cur = cur[idx]
        cur[indices[-1]] = val
        return self

    def slice(self, start=0, end=None):
        st = int(start) if start is not None else 0
        en = int(end) if end is not None else len(self.data)
        return NumpyArray(self.data[st:en])

    # Element-wise and Math operations
    def _apply_op(self, other, op_fn):
        if isinstance(other, NumpyArray):
            if self.shape != other.shape:
                raise ValueError(f"Shape mismatch: {self.shape} vs {other.shape}")
            def _rec(a, b):
                if isinstance(a, list):
                    return [_rec(x, y) for x, y in zip(a, b)]
                return op_fn(a, b)
            return NumpyArray(_rec(self.data, other.data))
        else:
            def _rec(a):
                if isinstance(a, list):
                    return [_rec(x) for x in a]
                return op_fn(a, other)
            return NumpyArray(_rec(self.data))

    def __add__(self, o): return self._apply_op(o, lambda a, b: a + b)
    def __radd__(self, o): return self._apply_op(o, lambda a, b: b + a)
    def __sub__(self, o): return self._apply_op(o, lambda a, b: a - b)
    def __rsub__(self, o): return self._apply_op(o, lambda a, b: b - a)
    def __mul__(self, o): return self._apply_op(o, lambda a, b: a * b)
    def __rmul__(self, o): return self._apply_op(o, lambda a, b: b * a)
    def __truediv__(self, o): return self._apply_op(o, lambda a, b: a / b)
    def __rtruediv__(self, o): return self._apply_op(o, lambda a, b: b / a)
    def __floordiv__(self, o): return self._apply_op(o, lambda a, b: a // b)
    def __mod__(self, o): return self._apply_op(o, lambda a, b: a % b)
    def __pow__(self, o): return self._apply_op(o, lambda a, b: a ** b)
    def __neg__(self): return self._apply_op(0, lambda a, b: -a)

    def __getitem__(self, idx):
        if isinstance(idx, slice):
            return NumpyArray(self.data[idx])
        res = self.data[int(idx)]
        if isinstance(res, list):
            return NumpyArray(res)
        return res

    def __setitem__(self, idx, val):
        self.data[int(idx)] = val.data if isinstance(val, NumpyArray) else val

    def __len__(self): return self.len

    def sum(self): return sum(self.flat_list())
    def mean(self): return sum(self.flat_list()) / len(self.flat_list()) if self.flat_list() else 0
    def avg(self): return self.mean()
    def max(self): return max(self.flat_list()) if self.flat_list() else None
    def min(self): return min(self.flat_list()) if self.flat_list() else None

    def var(self):
        m = self.mean()
        fl = self.flat_list()
        return sum((x - m) ** 2 for x in fl) / len(fl) if fl else 0

    def std(self):
        return math.sqrt(self.var())

    def norm(self):
        return math.sqrt(sum(x ** 2 for x in self.flat_list()))

    def dot(self, other):
        o_flat = other.flat_list() if isinstance(other, NumpyArray) else NumpyArray(other).flat_list()
        s_flat = self.flat_list()
        if len(s_flat) != len(o_flat):
            raise ValueError(f"Dot product dimension mismatch: {len(s_flat)} vs {len(o_flat)}")
        return sum(a * b for a, b in zip(s_flat, o_flat))

    def matMul(self, other):
        b = other if isinstance(other, NumpyArray) else NumpyArray(other)
        if len(self.shape) != 2 or len(b.shape) != 2:
            raise ValueError("Matrix multiplication requires 2D arrays")
        r1, c1 = self.shape; r2, c2 = b.shape
        if c1 != r2:
            raise ValueError(f"Matrix dimension mismatch: ({r1}x{c1}) and ({r2}x{c2})")
        res = [[sum(self.data[i][k] * b.data[k][j] for k in range(c1)) for j in range(c2)] for i in range(r1)]
        return NumpyArray(res)

    def softmax(self):
        fl = self.flat_list()
        max_v = max(fl) if fl else 0
        exp_vals = [math.exp(x - max_v) for x in fl]
        sum_exp = sum(exp_vals) or 1
        res = [v / sum_exp for v in exp_vals]
        return NumpyArray(res).reshape(self.shape)

    def relu(self):
        def _r(x):
            if isinstance(x, list): return [_r(v) for v in x]
            return max(0, x)
        return NumpyArray(_r(self.data))

    def sigmoid(self):
        def _s(x):
            if isinstance(x, list): return [_s(v) for v in x]
            return 1.0 / (1.0 + math.exp(-x))
        return NumpyArray(_s(self.data))

    def __repr__(self):
        return f"array({self.data})"

# Alias for backward compatibility
NovaArray = NumpyArray


def build_numpy_module():
    m = {}

    def _array(data):
        return NumpyArray(data)

    def _zeros(shape):
        if isinstance(shape, (int, float)): shape = [int(shape)]
        elif isinstance(shape, (list, tuple)): shape = [int(x) for x in shape]
        def _b(s):
            if len(s) == 1: return [0] * s[0]
            return [_b(s[1:]) for _ in range(s[0])]
        return NumpyArray(_b(shape))

    def _ones(shape):
        if isinstance(shape, (int, float)): shape = [int(shape)]
        elif isinstance(shape, (list, tuple)): shape = [int(x) for x in shape]
        def _b(s):
            if len(s) == 1: return [1] * s[0]
            return [_b(s[1:]) for _ in range(s[0])]
        return NumpyArray(_b(shape))

    def _rand(shape):
        if isinstance(shape, (int, float)): shape = [int(shape)]
        elif isinstance(shape, (list, tuple)): shape = [int(x) for x in shape]
        def _b(s):
            if len(s) == 1: return [random.random() for _ in range(s[0])]
            return [_b(s[1:]) for _ in range(s[0])]
        return NumpyArray(_b(shape))

    def _range(start, end=None, step=1):
        if end is None:
            st, en = 0, int(start)
        else:
            st, en = int(start), int(end)
        stp = int(step)
        return NumpyArray(list(range(st, en, stp)))

    def _oneHot(idx, classes):
        c = int(classes)
        i = int(idx)
        res = [1 if k == i else 0 for k in range(c)]
        return NumpyArray(res)

    def _to_arr(a):
        return a if isinstance(a, NumpyArray) else NumpyArray(a)

    m["array"]   = _array
    m["zeros"]   = _zeros
    m["ones"]    = _ones
    m["rand"]    = _rand
    m["random"]  = _rand
    m["range"]   = _range
    m["reshape"] = lambda a, s: _to_arr(a).reshape(s)
    m["shape"]   = lambda a: _to_arr(a).shape
    m["size"]    = lambda a: _to_arr(a).size
    m["flat"]    = lambda a: _to_arr(a).flat()
    m["T"]       = lambda a: _to_arr(a).T
    m["trans"]   = lambda a: _to_arr(a).T
    m["dot"]     = lambda a, b: _to_arr(a).dot(_to_arr(b))
    m["matMul"]  = lambda a, b: _to_arr(a).matMul(_to_arr(b))
    m["sum"]     = lambda a: _to_arr(a).sum()
    m["mean"]    = lambda a: _to_arr(a).mean()
    m["avg"]     = lambda a: _to_arr(a).mean()
    m["max"]     = lambda a: _to_arr(a).max()
    m["min"]     = lambda a: _to_arr(a).min()
    m["std"]     = lambda a: _to_arr(a).std()
    m["var"]     = lambda a: _to_arr(a).var()
    m["norm"]    = lambda a: _to_arr(a).norm()
    m["softmax"] = lambda a: _to_arr(a).softmax()
    m["relu"]    = lambda a: _to_arr(a).relu()
    m["sigmoid"] = lambda a: _to_arr(a).sigmoid()
    m["oneHot"]  = _oneHot
    m["one_hot"] = _oneHot
    return StdModule("numpy", m)


# ============================================================
# C TEMPLATES (FOR COMPILER - BLAZING-FAST STANDALONE BINARY)
# ============================================================
cCode = {
    "include": '#include "nova_np.h"',
    "array": 'NumpyArray {var} = npArray((float[]){{data}}, {size});',
    "zeros": 'NumpyArray {var} = npZeros({shape});',
    "ones": 'NumpyArray {var} = npOnes({shape});',
    "rand": 'NumpyArray {var} = npRand({shape});',
    "mean": 'float {var} = npMean(&{arr});',
    "sum": 'float {var} = npSum(&{arr});',
    "max": 'float {var} = npMax(&{arr});',
    "min": 'float {var} = npMin(&{arr});',
    "std": 'float {var} = npStd(&{arr});',
    "add": 'NumpyArray {var} = npAdd(&{a}, &{b});',
    "mul": 'NumpyArray {var} = npMul(&{a}, {scalar});',
    "reshape": 'NumpyArray {var} = npReshape(&{a}, {rows}, {cols});',
}
