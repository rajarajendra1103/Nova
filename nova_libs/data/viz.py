import math
from nova_libs.core import StdModule
from nova_libs.data.chart import ChartFigure

# ============================================================
# VIZ - SEABORN-EQUIVALENT HIGH-LEVEL STATISTICAL PLOTTING
# ============================================================
class VizFigure(ChartFigure):
    def __init__(self, title_text=""):
        super().__init__(title_text)
        self.style_theme = "seaborn"

    def addHeat(self, data, options=None):
        opts = options if isinstance(options, dict) else {}
        matrix = data.toArray() if hasattr(data, "toArray") else (data.data if hasattr(data, "data") else list(data))
        self.plots.append({
            "type": "heatmap",
            "matrix": matrix,
            "color": opts.get("color", "coolwarm"),
            "title": opts.get("title", "")
        })
        if opts.get("title"): self.title(opts["title"])
        return self

    def heat(self, data, options=None):
        return self.addHeat(data, options)

    def addBox(self, data, options=None):
        opts = options if isinstance(options, dict) else {}
        d = getattr(data, "flat_list", lambda: list(data) if isinstance(data, (list, tuple)) else [data])()
        self.plots.append({
            "type": "box",
            "data": d,
            "color": opts.get("color", "#10b981"),
            "title": opts.get("title", "")
        })
        if opts.get("title"): self.title(opts["title"])
        return self

    def box(self, data, options=None):
        return self.addBox(data, options)

    def addViolin(self, data, options=None):
        opts = options if isinstance(options, dict) else {}
        d = getattr(data, "flat_list", lambda: list(data) if isinstance(data, (list, tuple)) else [data])()
        self.plots.append({
            "type": "violin",
            "data": d,
            "color": opts.get("color", "#6366f1"),
            "title": opts.get("title", "")
        })
        if opts.get("title"): self.title(opts["title"])
        return self

    def violin(self, data, options=None):
        return self.addViolin(data, options)

    def addDist(self, data, options=None):
        opts = options if isinstance(options, dict) else {}
        d = getattr(data, "flat_list", lambda: list(data) if isinstance(data, (list, tuple)) else [data])()
        self.plots.append({
            "type": "dist",
            "data": d,
            "bins": opts.get("bins", 10),
            "color": opts.get("color", "#3b82f6"),
            "title": opts.get("title", "")
        })
        if opts.get("title"): self.title(opts["title"])
        return self

    def dist(self, data, options=None):
        return self.addDist(data, options)

    def addCorr(self, data, options=None):
        opts = options if isinstance(options, dict) else {}
        # Calculate correlation matrix if DataFrame
        if hasattr(data, "_rows") and hasattr(data, "_columns"):
            cols = [c for c in data._columns if any(isinstance(r.get(c), (int, float)) for r in data._rows)]
            matrix = []
            for c1 in cols:
                row_corr = []
                v1 = [r.get(c1, 0) for r in data._rows if isinstance(r.get(c1), (int, float))]
                m1 = sum(v1)/len(v1) if v1 else 0
                for c2 in cols:
                    v2 = [r.get(c2, 0) for r in data._rows if isinstance(r.get(c2), (int, float))]
                    m2 = sum(v2)/len(v2) if v2 else 0
                    num = sum((x - m1)*(y - m2) for x, y in zip(v1, v2))
                    den = math.sqrt(sum((x - m1)**2 for x in v1) * sum((y - m2)**2 for y in v2)) or 1
                    row_corr.append(round(num/den, 2))
                matrix.append(row_corr)
        else:
            matrix = data.toArray() if hasattr(data, "toArray") else list(data)
            cols = [f"V{i+1}" for i in range(len(matrix))]

        self.plots.append({
            "type": "corr",
            "matrix": matrix,
            "columns": cols,
            "title": opts.get("title", "Correlation Matrix")
        })
        if opts.get("title"): self.title(opts["title"])
        return self

    def corr(self, data, options=None):
        return self.addCorr(data, options)

    def renderAscii(self):
        lines = []
        if self.plot_title:
            lines.append(f"=== {self.plot_title} (Viz Statistical Plot) ===")

        for p in self.plots:
            t = p["type"]
            if t == "heatmap" or t == "corr":
                lines.append(f"[{t.upper()}]")
                matrix = p["matrix"]
                cols = p.get("columns", [f"C{i+1}" for i in range(len(matrix[0]))] if matrix else [])
                if cols:
                    lines.append("       " + "  ".join(f"{str(c):>6}" for c in cols))
                for i, row in enumerate(matrix):
                    row_lbl = cols[i] if i < len(cols) else f"R{i+1}"
                    lines.append(f"{str(row_lbl):>6} " + "  ".join(f"{float(v):>6.2f}" if isinstance(v, (int, float)) else f"{str(v):>6}" for v in row))
            elif t == "box":
                d = sorted([x for x in p["data"] if isinstance(x, (int, float))])
                if d:
                    q1 = d[len(d)//4]
                    med = d[len(d)//2]
                    q3 = d[(len(d)*3)//4]
                    lines.append(f"[BOXPLOT] Min: {d[0]} | Q1: {q1} | Median: {med} | Q3: {q3} | Max: {d[-1]}")
                else:
                    lines.append("[BOXPLOT] Empty data")
            elif t == "violin":
                d = [x for x in p["data"] if isinstance(x, (int, float))]
                mean_v = sum(d)/len(d) if d else 0
                lines.append(f"[VIOLIN PLOT] Density estimation across {len(d)} points (Mean: {mean_v:.2f})")
            elif t == "dist":
                d = [x for x in p["data"] if isinstance(x, (int, float))]
                lines.append(f"[DISTRIBUTION + KDE] {len(d)} samples | Bins: {p.get('bins', 10)}")

        base_rendered = super().renderAscii()
        if base_rendered and not any(p["type"] in ("heatmap", "corr", "box", "violin", "dist") for p in self.plots):
            lines.append(base_rendered)
        return "\n".join(lines)


def build_viz_module():
    m = {}

    def _new(title=""): return VizFigure(title)

    def _heat(data, options=None):
        fig = VizFigure().addHeat(data, options)
        fig.show()
        return fig

    def _box(data, options=None):
        fig = VizFigure().addBox(data, options)
        fig.show()
        return fig

    def _violin(data, options=None):
        fig = VizFigure().addViolin(data, options)
        fig.show()
        return fig

    def _dist(data, options=None):
        fig = VizFigure().addDist(data, options)
        fig.show()
        return fig

    def _corr(data, options=None):
        fig = VizFigure().addCorr(data, options)
        fig.show()
        return fig

    def _pair(data, options=None):
        fig = VizFigure("Pairplot").addCorr(data, options)
        fig.show()
        return fig

    def _count(categories, options=None):
        from collections import Counter
        cats = list(categories)
        counts = Counter(cats)
        fig = VizFigure("Count Plot").addBar(list(counts.values()), list(counts.keys()), options)
        fig.show()
        return fig

    def _line(x, y=None, options=None):
        fig = VizFigure().addLine(x, y, options)
        fig.show()
        return fig

    def _bar(cats, vals=None, options=None):
        fig = VizFigure().addBar(cats, vals, options)
        fig.show()
        return fig

    def _scatter(x, y=None, options=None):
        fig = VizFigure().addScatter(x, y, options)
        fig.show()
        return fig

    m["new"]      = _new
    m["figure"]   = _new
    m["heat"]     = _heat
    m["heatmap"]  = _heat
    m["box"]      = _box
    m["boxplot"]  = _box
    m["violin"]   = _violin
    m["dist"]     = _dist
    m["distplot"] = _dist
    m["corr"]     = _corr
    m["pair"]     = _pair
    m["count"]    = _count
    m["line"]     = _line
    m["bar"]      = _bar
    m["scatter"]  = _scatter
    m["show"]     = lambda fig=None: fig.show() if fig else None
    m["save"]     = lambda fig, path: fig.save(path) if fig else False

    return StdModule("viz", m)


# ============================================================
# C TEMPLATES (FOR COMPILER - BLAZING-FAST STANDALONE BINARY)
# ============================================================
cCode = {
    "include": '#include "nova_chart.h"',
    "heat": 'ChartFigure {var} = vizHeatmap({matrix}, {rows}, {cols});',
    "heatmap": 'ChartFigure {var} = vizHeatmap({matrix}, {rows}, {cols});',
    "box": 'ChartFigure {var} = vizBoxplot({data}, {size});',
    "boxplot": 'ChartFigure {var} = vizBoxplot({data}, {size});',
    "show": 'chShow(&{var});',
}
