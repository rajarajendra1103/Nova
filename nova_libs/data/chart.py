import os
from nova_libs.core import StdModule

# ============================================================
# CHART / CH - MATPLOTLIB-EQUIVALENT VISUALIZATION ENGINE
# ============================================================
class ChartFigure:
    def __init__(self, title_text=""):
        self.plot_title = str(title_text)
        self.xlabel_text = ""
        self.ylabel_text = ""
        self.has_legend = False
        self.plots = []

    def title(self, text):
        self.plot_title = str(text)
        return self

    def xLabel(self, text):
        self.xlabel_text = str(text)
        return self

    def yLabel(self, text):
        self.ylabel_text = str(text)
        return self

    def legend(self, show=True):
        self.has_legend = bool(show)
        return self

    def _extract_xy(self, arg1, arg2=None, options=None):
        opts = {}
        if isinstance(arg1, dict):
            opts = dict(arg1)
            x = opts.get("x")
            y = opts.get("y", [])
        elif isinstance(arg2, dict):
            opts = dict(arg2)
            y = arg1
            x = None
        else:
            if isinstance(options, dict): opts = dict(options)
            y = arg2 if arg2 is not None else arg1
            x = arg1 if arg2 is not None else None

        y_list = getattr(y, "flat_list", lambda: list(y) if isinstance(y, (list, tuple)) else [y])()
        if x is not None:
            x_list = getattr(x, "flat_list", lambda: list(x) if isinstance(x, (list, tuple)) else [x])()
        else:
            x_list = list(range(len(y_list)))
        return x_list, y_list, opts

    def addLine(self, arg1, arg2=None, options=None):
        x, y, opts = self._extract_xy(arg1, arg2, options)
        self.plots.append({
            "type": "line",
            "x": x,
            "y": y,
            "color": opts.get("color", "#3b82f6"),
            "label": opts.get("label", ""),
            "size": opts.get("size", 2)
        })
        if opts.get("title"): self.title(opts["title"])
        if opts.get("xLabel"): self.xLabel(opts["xLabel"])
        if opts.get("yLabel"): self.yLabel(opts["yLabel"])
        return self

    def line(self, arg1, arg2=None, options=None):
        return self.addLine(arg1, arg2, options)

    def addBar(self, arg1, arg2=None, options=None):
        x, y, opts = self._extract_xy(arg1, arg2, options)
        self.plots.append({
            "type": "bar",
            "x": x,
            "y": y,
            "color": opts.get("color", "#10b981"),
            "label": opts.get("label", "")
        })
        if opts.get("title"): self.title(opts["title"])
        if opts.get("xLabel"): self.xLabel(opts["xLabel"])
        if opts.get("yLabel"): self.yLabel(opts["yLabel"])
        return self

    def bar(self, arg1, arg2=None, options=None):
        return self.addBar(arg1, arg2, options)

    def addScatter(self, arg1, arg2=None, options=None):
        x, y, opts = self._extract_xy(arg1, arg2, options)
        self.plots.append({
            "type": "scatter",
            "x": x,
            "y": y,
            "color": opts.get("color", "#f59e0b"),
            "label": opts.get("label", ""),
            "size": opts.get("size", 6)
        })
        if opts.get("title"): self.title(opts["title"])
        if opts.get("xLabel"): self.xLabel(opts["xLabel"])
        if opts.get("yLabel"): self.yLabel(opts["yLabel"])
        return self

    def scatter(self, arg1, arg2=None, options=None):
        return self.addScatter(arg1, arg2, options)

    def addHist(self, data, options=None):
        opts = options if isinstance(options, dict) else {}
        d = getattr(data, "flat_list", lambda: list(data) if isinstance(data, (list, tuple)) else [data])()
        bins = opts.get("bins", 10) if isinstance(options, dict) else (options if isinstance(options, (int, float)) else 10)
        self.plots.append({
            "type": "hist",
            "data": d,
            "bins": bins,
            "color": opts.get("color", "#8b5cf6"),
            "label": opts.get("label", "")
        })
        if opts.get("title"): self.title(opts["title"])
        return self

    def hist(self, data, options=None):
        return self.addHist(data, options)

    def addPie(self, values, labels=None, options=None):
        opts = {}
        if isinstance(values, dict):
            opts = values
            v = opts.get("values", [])
            l = opts.get("labels", [])
        else:
            v = getattr(values, "flat_list", lambda: list(values) if isinstance(values, (list, tuple)) else [values])()
            if isinstance(labels, dict):
                opts = labels
                l = [f"Slice {i+1}" for i in range(len(v))]
            else:
                l = list(labels) if labels else [f"Slice {i+1}" for i in range(len(v))]
            if isinstance(options, dict): opts.update(options)

        self.plots.append({
            "type": "pie",
            "values": v,
            "labels": l,
            "title": opts.get("title", "")
        })
        if opts.get("title"): self.title(opts["title"])
        return self

    def pie(self, values, labels=None, options=None):
        return self.addPie(values, labels, options)

    def clear(self):
        self.plots.clear()
        self.plot_title = ""
        self.xlabel_text = ""
        self.ylabel_text = ""
        self.has_legend = False
        return self

    def renderAscii(self):
        lines = []
        if self.plot_title:
            lines.append(f"=== {self.plot_title} ===")
        if self.ylabel_text:
            lines.append(f"Y: {self.ylabel_text}")

        for p in self.plots:
            t = p["type"]
            lbl = f" ({p['label']})" if p.get("label") else ""
            if t in ("line", "scatter"):
                lines.append(f"[{t.upper()}{lbl}] {len(p['y'])} points")
                for x_val, y_val in zip(p["x"][:8], p["y"][:8]):
                    lines.append(f"  ({x_val}, {y_val})")
            elif t == "bar":
                lines.append(f"[BAR{lbl}]")
                numeric_y = [v for v in p["y"] if isinstance(v, (int, float))]
                max_v = max(numeric_y) if numeric_y and max(numeric_y) > 0 else 1
                for x_val, y_val in zip(p["x"][:10], p["y"][:10]):
                    bar_len = int((y_val / max_v) * 20) if isinstance(y_val, (int, float)) else 0
                    lines.append(f"  {str(x_val):>6} | {'█' * bar_len} ({y_val})")
            elif t == "pie":
                lines.append(f"[PIE{lbl}]")
                numeric_v = [v for v in p["values"] if isinstance(v, (int, float))]
                total = sum(numeric_v) or 1
                for lbl_val, val in zip(p["labels"], p["values"]):
                    pct = (val / total) * 100 if isinstance(val, (int, float)) else 0
                    lines.append(f"  {lbl_val}: {val} ({pct:.1f}%)")
            elif t == "hist":
                lines.append(f"[HIST{lbl}] Count: {len(p['data'])} Bins: {p.get('bins', 10)}")

        if self.xlabel_text:
            lines.append(f"X: {self.xlabel_text}")
        return "\n".join(lines)

    def show(self):
        txt = self.renderAscii()
        print(txt)
        return txt

    def save(self, path):
        path_str = str(path)
        with open(path_str, "w", encoding="utf-8") as f:
            f.write(self.renderAscii())
        return True

    def __repr__(self):
        return self.renderAscii()


def build_chart_module():
    m = {}

    def _new(title=""): return ChartFigure(title)

    def _line(arg1, arg2=None, options=None):
        fig = ChartFigure().addLine(arg1, arg2, options)
        fig.show()
        return fig

    def _bar(arg1, arg2=None, options=None):
        fig = ChartFigure().addBar(arg1, arg2, options)
        fig.show()
        return fig

    def _scatter(arg1, arg2=None, options=None):
        fig = ChartFigure().addScatter(arg1, arg2, options)
        fig.show()
        return fig

    def _hist(data, options=None):
        fig = ChartFigure().addHist(data, options)
        fig.show()
        return fig

    def _pie(values, labels=None, options=None):
        fig = ChartFigure().addPie(values, labels, options)
        fig.show()
        return fig

    m["new"]     = _new
    m["figure"]  = _new
    m["line"]    = _line
    m["l"]       = _line
    m["bar"]     = _bar
    m["b"]       = _bar
    m["scatter"] = _scatter
    m["s"]       = _scatter
    m["hist"]    = _hist
    m["h"]       = _hist
    m["pie"]     = _pie
    m["show"]    = lambda fig=None: fig.show() if fig else None
    m["save"]    = lambda fig, path: fig.save(path) if fig else False

    return StdModule("chart", m)


# ============================================================
# C TEMPLATES (FOR COMPILER - BLAZING-FAST STANDALONE BINARY)
# ============================================================
cCode = {
    "include": '#include "nova_chart.h"',
    "line": 'ChartFigure {var} = chLine({data}, {size});',
    "bar": 'ChartFigure {var} = chBar({labels}, {values}, {size});',
    "scatter": 'ChartFigure {var} = chScatter({xData}, {yData}, {size});',
    "show": 'chShow(&{var});',
}
