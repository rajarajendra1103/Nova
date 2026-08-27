import json
import csv
from nova_libs.core import StdModule
from nova_libs.data.numpy import NumpyArray, NovaArray

class CallableList(list):
    def __call__(self):
        return self


# ============================================================
# PANDAS / PD - DATAFRAME ENGINE
# ============================================================
class NovaGroupedDF:
    def __init__(self, df, group_col):
        self.df = df
        self.group_col = str(group_col)
        self.groups = {}
        for r in df._rows:
            key = r.get(self.group_col, "Unknown")
            if key not in self.groups: self.groups[key] = []
            self.groups[key].append(r)

    def mean(self):
        numeric_cols = [c for c in self.df._columns if c != self.group_col and any(isinstance(r.get(c), (int, float)) for r in self.df._rows)]
        res = []
        for g_val, rows in self.groups.items():
            row_res = {self.group_col: g_val}
            for c in numeric_cols:
                vals = [r[c] for r in rows if isinstance(r.get(c), (int, float))]
                row_res[c] = sum(vals) / len(vals) if vals else 0
            res.append(row_res)
        return NovaDF(res)

    def sum(self):
        numeric_cols = [c for c in self.df._columns if c != self.group_col and any(isinstance(r.get(c), (int, float)) for r in self.df._rows)]
        res = []
        for g_val, rows in self.groups.items():
            row_res = {self.group_col: g_val}
            for c in numeric_cols:
                vals = [r[c] for r in rows if isinstance(r.get(c), (int, float))]
                row_res[c] = sum(vals) if vals else 0
            res.append(row_res)
        return NovaDF(res)

    def count(self):
        res = [{self.group_col: g_val, "count": len(rows)} for g_val, rows in self.groups.items()]
        return NovaDF(res)

    def max(self):
        res = []
        for g_val, rows in self.groups.items():
            row_res = {self.group_col: g_val}
            for c in self.df._columns:
                if c == self.group_col: continue
                vals = [r[c] for r in rows if r.get(c) is not None]
                row_res[c] = max(vals) if vals else None
            res.append(row_res)
        return NovaDF(res)

    def min(self):
        res = []
        for g_val, rows in self.groups.items():
            row_res = {self.group_col: g_val}
            for c in self.df._columns:
                if c == self.group_col: continue
                vals = [r[c] for r in rows if r.get(c) is not None]
                row_res[c] = min(vals) if vals else None
            res.append(row_res)
        return NovaDF(res)

    def __repr__(self):
        return f"<GroupedDF by '{self.group_col}' ({len(self.groups)} groups)>"


class NovaDF:
    def __init__(self, data, columns=None, interp=None):
        self._rows = []
        self._columns = []
        self._interp = interp

        if isinstance(data, dict):
            self._columns = list(data.keys())
            max_len = max(len(v) if isinstance(v, (list, tuple, NumpyArray)) else 1 for v in data.values()) if data else 0
            for i in range(max_len):
                row = {}
                for k in self._columns:
                    v = data[k]
                    if isinstance(v, (list, tuple, NumpyArray)):
                        val = v[i] if i < len(v) else None
                        row[k] = val.data if isinstance(val, NumpyArray) else val
                    else:
                        row[k] = v
                self._rows.append(row)
        elif isinstance(data, (list, tuple)):
            if columns is None:
                if data and isinstance(data[0], dict):
                    self._columns = list(data[0].keys())
                    self._rows = [dict(r) for r in data]
                else:
                    self._columns = [f"col_{i}" for i in range(len(data[0]))] if data and isinstance(data[0], (list, tuple)) else []
                    for r in data:
                        self._rows.append({c: v for c, v in zip(self._columns, r)})
            else:
                self._columns = list(columns)
                for r in data:
                    if isinstance(r, dict):
                        self._rows.append({c: r.get(c, None) for c in self._columns})
                    else:
                        self._rows.append({c: v for c, v in zip(self._columns, r)})

        self.colNames = list(self._columns)
        self.rows = len(self._rows)
        self.cols = len(self._columns)
        self.shape = CallableList([self.rows, self.cols])

    def col(self, name):
        name = str(name)
        return [r.get(name, None) for r in self._rows]

    def getCol(self, name): return self.col(name)

    def row(self, idx):
        return dict(self._rows[int(idx)])

    def getRow(self, idx): return self.row(idx)

    def __getitem__(self, item):
        if isinstance(item, str): return self.col(item)
        if isinstance(item, (int, float)): return self.row(int(item))
        if isinstance(item, slice): return NovaDF(self._rows[item], self._columns, self._interp)
        raise KeyError(item)

    def __setitem__(self, col_name, values):
        self.addCol(col_name, values)

    def __len__(self): return self.rows

    def head(self, n=5):
        return NovaDF(self._rows[:int(n)], self._columns, self._interp)

    def tail(self, n=5):
        return NovaDF(self._rows[-int(n):], self._columns, self._interp)

    def info(self):
        lines = [f"<NovaDF {self.rows} rows x {self.cols} cols>"]
        for c in self._columns:
            non_null = sum(1 for r in self._rows if r.get(c) is not None)
            lines.append(f"  {c}: {non_null} non-null")
        info_str = "\n".join(lines)
        print(info_str)
        return info_str

    def where(self, condition):
        cond_str = str(condition)
        matched = []
        for r in self._rows:
            try:
                if eval(cond_str, {"__builtins__": {}}, dict(r)):
                    matched.append(r)
            except Exception:
                pass
        return NovaDF(matched, self._columns, self._interp)

    def filter(self, fn):
        matched = []
        for r in self._rows:
            try:
                if self._interp is not None:
                    res = self._interp._invoke(fn, [r])
                elif callable(fn):
                    res = fn(r)
                else:
                    res = False
                if res: matched.append(r)
            except Exception:
                pass
        return NovaDF(matched, self._columns, self._interp)

    def sort(self, col):
        col = str(col)
        sorted_rows = sorted(self._rows, key=lambda r: (r.get(col) is None, r.get(col)))
        return NovaDF(sorted_rows, self._columns, self._interp)

    def sortBy(self, col): return self.sort(col)

    def dsort(self, col):
        col = str(col)
        sorted_rows = sorted(self._rows, key=lambda r: (r.get(col) is None, r.get(col)), reverse=True)
        return NovaDF(sorted_rows, self._columns, self._interp)

    def group(self, col): return NovaGroupedDF(self, col)
    def groupBy(self, col): return NovaGroupedDF(self, col)

    def mean(self, col=None):
        if col is not None:
            vals = [r.get(str(col)) for r in self._rows if isinstance(r.get(str(col)), (int, float))]
            return sum(vals) / len(vals) if vals else 0
        return {c: self.mean(c) for c in self._columns if any(isinstance(r.get(c), (int, float)) for r in self._rows)}

    def avg(self, col=None): return self.mean(col)

    def sum(self, col=None):
        if col is not None:
            vals = [r.get(str(col)) for r in self._rows if isinstance(r.get(str(col)), (int, float))]
            return sum(vals) if vals else 0
        return {c: self.sum(c) for c in self._columns if any(isinstance(r.get(c), (int, float)) for r in self._rows)}

    def max(self, col=None):
        if col is not None:
            vals = [r.get(str(col)) for r in self._rows if r.get(str(col)) is not None]
            return max(vals) if vals else None
        return {c: self.max(c) for c in self._columns}

    def min(self, col=None):
        if col is not None:
            vals = [r.get(str(col)) for r in self._rows if r.get(str(col)) is not None]
            return min(vals) if vals else None
        return {c: self.min(c) for c in self._columns}

    def count(self, col=None):
        if col is not None:
            return sum(1 for r in self._rows if r.get(str(col)) is not None)
        return self.rows

    def fill(self, value):
        new_rows = []
        for r in self._rows:
            new_r = {k: (value if v is None else v) for k, v in r.items()}
            new_rows.append(new_r)
        return NovaDF(new_rows, self._columns, self._interp)

    def fillNA(self, value): return self.fill(value)

    def dropNA(self):
        new_rows = [r for r in self._rows if all(v is not None for v in r.values())]
        return NovaDF(new_rows, self._columns, self._interp)

    def drop(self, col):
        col = str(col)
        new_cols = [c for c in self._columns if c != col]
        new_rows = [{k: v for k, v in r.items() if k != col} for r in self._rows]
        return NovaDF(new_rows, new_cols, self._interp)

    def dropRow(self, idx):
        i = int(idx)
        new_rows = [r for k, r in enumerate(self._rows) if k != i]
        return NovaDF(new_rows, self._columns, self._interp)

    def addCol(self, name, values):
        name = str(name)
        if name not in self._columns: self._columns.append(name)
        vals = values.flat_list() if isinstance(values, NumpyArray) else list(values)
        for i, r in enumerate(self._rows):
            r[name] = vals[i] if i < len(vals) else None
        self.colNames = list(self._columns)
        self.cols = len(self._columns)
        self.shape = CallableList([self.rows, self.cols])
        return self

    def addRow(self, row):
        if isinstance(row, dict):
            new_r = {c: row.get(c, None) for c in self._columns}
        elif isinstance(row, (list, tuple)):
            new_r = {c: v for c, v in zip(self._columns, row)}
        else:
            new_r = {c: None for c in self._columns}
        self._rows.append(new_r)
        self.rows = len(self._rows)
        self.shape = CallableList([self.rows, self.cols])
        return self

    def set(self, rowIndex, colName, value):
        r = int(rowIndex); c = str(colName)
        if 0 <= r < len(self._rows):
            self._rows[r][c] = value
        return self

    def update(self, rowIndex, row_map):
        r = int(rowIndex)
        if 0 <= r < len(self._rows) and isinstance(row_map, dict):
            self._rows[r].update(row_map)
        return self

    def toArray(self):
        return [[r.get(c, None) for c in self._columns] for r in self._rows]

    def toNum(self):
        return NumpyArray(self.toArray())

    def toNumpy(self): return self.toNum()

    def toCsv(self, path):
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=self._columns)
            writer.writeheader()
            writer.writerows(self._rows)
        return True

    def toJson(self, path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self._rows, f, indent=2)
        return True

    def toExcel(self, path):
        return self.toCsv(path)

    def save(self, path):
        p = str(path).lower()
        if p.endswith(".json"): return self.toJson(path)
        return self.toCsv(path)

    def __repr__(self):
        if not self._rows: return "Empty DataFrame"
        hdr = " | ".join(f"{str(c):<12}" for c in self._columns)
        sep = "-+-".join("-" * 12 for _ in self._columns)
        rows_str = []
        for r in self._rows[:10]:
            rows_str.append(" | ".join(f"{str(r.get(c, '')):<12}" for c in self._columns))
        if len(self._rows) > 10:
            rows_str.append(f"... ({len(self._rows) - 10} more rows)")
        return f"{hdr}\n{sep}\n" + "\n".join(rows_str)


def build_pandas_module(interp=None):
    m = {}

    def _df(data=None, columns=None):
        return NovaDF(data if data is not None else {}, columns, interp)

    def _readCsv(path):
        rows = []
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            reader = csv.DictReader(f)
            for r in reader:
                parsed_r = {}
                for k, v in r.items():
                    try:
                        parsed_r[k] = int(v) if v.isdigit() else float(v)
                    except Exception:
                        parsed_r[k] = v
                rows.append(parsed_r)
        return NovaDF(rows, interp=interp)

    def _readJson(path):
        with open(path, "r", encoding="utf-8") as f:
            d = json.load(f)
        return NovaDF(d, interp=interp)

    def _readExcel(path):
        return _readCsv(path)

    def _read(path):
        p = str(path).lower()
        if p.endswith(".json"): return _readJson(path)
        return _readCsv(path)

    m["df"]         = _df
    m["DF"]         = _df
    m["DataFrame"]  = _df
    m["dataframe"]  = _df
    m["readCsv"]    = _readCsv
    m["read_csv"]   = _readCsv
    m["readJson"]   = _readJson
    m["read_json"]  = _readJson
    m["readExcel"]  = _readExcel
    m["read_excel"] = _readExcel
    m["read"]       = _read

    return StdModule("pandas", m)


# ============================================================
# C TEMPLATES (FOR COMPILER - BLAZING-FAST STANDALONE BINARY)
# ============================================================
cCode = {
    "include": '#include "nova_pandas.h"',
    "df": 'NovaDataFrame {var} = pdDF();',
    "DF": 'NovaDataFrame {var} = pdDF();',
    "dataframe": 'NovaDataFrame {var} = pdDF();',
    "DataFrame": 'NovaDataFrame {var} = pdDF();',
    "readCsv": 'NovaDataFrame {var} = pdReadCsv("{path}");',
    "read": 'NovaDataFrame {var} = pdReadCsv("{path}");',
    "show": 'pdShowDF(&{var});',
    "shape": 'pdShape(&{var})',
    "addCol": 'pdAddCol(&{df}, "{name}", {data}, {size});',
    "mean": 'float {var} = pdColMean(&{df}, "{col}");',
    "sum": 'float {var} = pdColSum(&{df}, "{col}");',
}
