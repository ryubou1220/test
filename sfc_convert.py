#!/usr/bin/env python3
"""SXF (.sfc, feature mode) -> DXF / PNG / PDF converter.

usage: python3 sfc_convert.py input.sfc [out_basename]
"""
import math
import re
import sys

import ezdxf
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Arc, Circle, Polygon

# SXF predefined colours (code 1-16); user-defined colours start at 17
PRE_COLOURS = {
    "black": (0, 0, 0), "red": (255, 0, 0), "green": (0, 255, 0), "blue": (0, 0, 255),
    "yellow": (255, 255, 0), "magenta": (255, 0, 255), "cyan": (0, 255, 255),
    "white": (255, 255, 255), "deeppink": (192, 0, 128), "brown": (192, 128, 64),
    "orange": (255, 128, 0), "lightgreen": (128, 192, 128), "lightblue": (0, 128, 255),
    "lavender": (128, 64, 255), "lightgray": (192, 192, 192), "darkgray": (128, 128, 128),
}
PRE_COLOUR_ORDER = list(PRE_COLOURS)
# predefined line types (code 1-16)
LINE_STYLES = {1: "-", 2: (0, (6, 3)), 3: (0, (6, 6)), 4: (0, (12, 2, 1, 2)),
               5: (0, (12, 2, 1, 2, 1, 2)), 6: (0, (12, 2, 1, 2, 1, 2, 1, 2)),
               7: (0, (1, 2)), 8: (0, (10, 2, 2, 2)), 9: (0, (10, 2, 2, 2, 2, 2))}
DXF_LINETYPES = {2: "DASHED", 3: "DASHED", 4: "DASHDOT", 5: "DIVIDE", 6: "DIVIDE",
                 7: "DOT", 8: "CENTER", 9: "CENTER"}
# predefined line widths in mm (code 1-9)
WIDTHS = {1: 0.13, 2: 0.18, 3: 0.25, 4: 0.35, 5: 0.5, 6: 0.7, 7: 1.0, 8: 1.4, 9: 2.0}

ENTITY_RE = re.compile(r"^#(\d+)\s*=\s*(\w+)\((.*)\)\s*$", re.S)


def decode_str(s):
    # ISO 10303-21 \X2\hhhh...\X0\ escapes
    def x2(m):
        h = m.group(1)
        return "".join(chr(int(h[i:i + 4], 16)) for i in range(0, len(h), 4))
    s = re.sub(r"\\X2\\([0-9A-Fa-f]+)\\X0\\", x2, s)
    return s.replace("''", "'")


def split_args(body):
    """Split SXF argument list: '...' or \\'...\\' strings separated by commas."""
    args, i, n = [], 0, len(body)
    while i < n:
        if body.startswith("\\'", i):
            j = body.index("\\'", i + 2)
            args.append(decode_str(body[i + 2:j]))
            i = j + 2
        elif body[i] == "'":
            j = body.index("'", i + 1)
            args.append(body[i + 1:j])
            i = j + 1
        else:
            i += 1
    return args


def nums(s):
    s = s.strip("()")
    return [float(v) for v in s.split(",")] if s else []


def read_sfc(path):
    raw = open(path, "rb").read()
    text = raw.decode("cp932", errors="replace")
    # blocks are /*SXF ... SXF*/ (or /*SXF3 ... SXF3*/ for attribute data)
    blocks = re.findall(r"/\*SXF(\d*)\s*(.*?)\s*SXF\1\*/", text, re.S)
    ents = []
    for _, b in blocks:
        m = ENTITY_RE.match(" ".join(b.split("\r\n")))
        if m:
            ents.append((int(m.group(1)), m.group(2), split_args(m.group(3))))
    header_name = re.search(r"FILE_NAME\('(.*?)'", text)
    return ents, header_name.group(1) if header_name else ""


class Doc:
    def __init__(self, ents):
        self.user_colours = []
        self.layers = []  # (name, visible)
        self.sheet = None
        self.items = []   # drawable entities
        self.composites = []  # list of (colour, member item indices)
        self.fills = []   # (layer, colour, composite no)
        self.sfig_scale = 1.0
        pending = []
        for _id, kind, a in ents:
            if kind == "user_defined_colour_feature":
                self.user_colours.append(tuple(int(v) for v in a[:3]))
            elif kind == "layer_feature":
                self.layers.append((a[0], a[1] == "1"))
            elif kind == "drawing_sheet_feature":
                self.sheet = dict(name=a[0], size=a[1], orient=a[2],
                                  w=float(a[3]), h=float(a[4]))
            elif kind == "sfig_locate_feature" and a[1].startswith("基準座標系"):
                self.sfig_scale = float(a[5])
            elif kind in ("line_feature", "polyline_feature", "arc_feature",
                          "circle_feature", "spline_feature", "ellipse_feature",
                          "ellipse_arc_feature"):
                self.items.append((kind, a))
                pending.append(len(self.items) - 1)
            elif kind == "composite_curve_org_feature":
                self.composites.append((int(a[0]), pending))
                pending = []
            elif kind in ("text_string_feature", "point_marker_feature"):
                self.items.append((kind, a))
            elif kind == "fill_area_style_colour_feature":
                self.fills.append((int(a[0]), int(a[1]), int(a[2])))

    def rgb(self, code):
        code = int(code)
        if 1 <= code <= 16:
            c = PRE_COLOURS[PRE_COLOUR_ORDER[code - 1]]
        elif 0 <= code - 17 < len(self.user_colours):
            c = self.user_colours[code - 17]
        else:
            c = (0, 0, 0)
        return c

    def plot_rgb(self, code):
        r, g, b = self.rgb(code)
        if (r, g, b) == (255, 255, 255):   # white -> black on paper
            r, g, b = 0, 0, 0
        elif r > 200 and g > 200 and b < 80:  # yellow -> darker for readability
            r, g, b = 200, 160, 0
        return (r / 255, g / 255, b / 255)

    def visible(self, layer):
        i = int(layer) - 1
        return not (0 <= i < len(self.layers)) or self.layers[i][1]

    def layer_name(self, layer):
        i = int(layer) - 1
        return self.layers[i][0] if 0 <= i < len(self.layers) else "0"


def curve_points(kind, a, k):
    """Return list of (x, y) for a curve entity, scaled by k."""
    if kind == "line_feature":
        x1, y1, x2, y2 = map(float, a[4:8])
        return [(x1 * k, y1 * k), (x2 * k, y2 * k)]
    if kind in ("polyline_feature", "spline_feature"):
        off = 5 if kind == "polyline_feature" else 6
        xs, ys = nums(a[off]), nums(a[off + 1])
        return [(x * k, y * k) for x, y in zip(xs, ys)]
    if kind == "arc_feature":
        cx, cy, r = map(float, a[4:7])
        d, s, e = int(a[7]), float(a[8]), float(a[9])
        if d != 1:
            s, e = e, s
        if e <= s:
            e += 360
        n = max(4, int((e - s) / 3))
        return [((cx + r * math.cos(math.radians(s + (e - s) * i / n))) * k,
                 (cy + r * math.sin(math.radians(s + (e - s) * i / n))) * k)
                for i in range(n + 1)]
    if kind == "circle_feature":
        cx, cy, r = map(float, a[4:7])
        return [((cx + r * math.cos(2 * math.pi * i / 72)) * k,
                 (cy + r * math.sin(2 * math.pi * i / 72)) * k) for i in range(73)]
    return []


HALIGN = {0: "left", 1: "center", 2: "right"}
VALIGN = {0: "bottom", 1: "center", 2: "top"}


def render(doc, out, fontprop):
    k = doc.sfig_scale
    w = doc.sheet["w"] if doc.sheet else 841
    h = doc.sheet["h"] if doc.sheet else 594
    fig = plt.figure(figsize=(w / 25.4, h / 25.4))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, w)
    ax.set_ylim(0, h)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.patch.set_facecolor("white")

    # fills (behind everything)
    for layer, colour, cno in doc.fills:
        if not doc.visible(layer) or not (1 <= cno <= len(doc.composites)):
            continue
        pts = []
        for idx in doc.composites[cno - 1][1]:
            kind, a = doc.items[idx]
            pts += curve_points(kind, a, k)
        if len(pts) >= 3:
            ax.add_patch(Polygon(pts, closed=True, facecolor=doc.plot_rgb(colour),
                                 edgecolor="none", alpha=0.35, zorder=0))

    pt_per_mm = 72 / 25.4
    for kind, a in doc.items:
        if not doc.visible(a[0]):
            continue
        col = doc.plot_rgb(a[1])
        if kind == "text_string_feature":
            s = a[3]
            x, y = float(a[4]) * k, float(a[5]) * k
            ht = float(a[6]) * k
            ang = float(a[9])
            bp = int(a[11]) - 1
            ax.text(x, y, s, fontproperties=fontprop, fontsize=ht * pt_per_mm * 1.15,
                    color=col, rotation=ang, rotation_mode="anchor",
                    ha=HALIGN[bp % 3], va=VALIGN[bp // 3], zorder=3)
            continue
        if kind == "point_marker_feature":
            ax.plot(float(a[2]) * k, float(a[3]) * k, ".", color=col, ms=1.5)
            continue
        lt = LINE_STYLES.get(int(a[2]), "-")
        lw = WIDTHS.get(int(a[3]), 0.13) * pt_per_mm
        pts = curve_points(kind, a, k)
        if pts:
            xs, ys = zip(*pts)
            ax.plot(xs, ys, color=col, lw=lw, linestyle=lt, zorder=2,
                    solid_capstyle="round")
    fig.savefig(out + ".pdf")
    fig.savefig(out + ".png", dpi=200)
    plt.close(fig)


def to_dxf(doc, out):
    k = doc.sfig_scale
    d = ezdxf.new("R2018", setup=True)
    d.styles.new("JP", dxfattribs={"font": "msgothic.ttc"})
    msp = d.modelspace()
    for name, vis in doc.layers:
        lay = d.layers.add(name)
        if not vis:
            lay.off()

    def attrs(a, with_lt=True):
        r = dict(layer=doc.layer_name(a[0]), true_color=ezdxf.colors.rgb2int(doc.rgb(a[1])))
        if with_lt:
            lt = DXF_LINETYPES.get(int(a[2]))
            if lt:
                r["linetype"] = lt
            r["lineweight"] = int(round(WIDTHS.get(int(a[3]), 0.13) * 100))
        return r

    for kind, a in doc.items:
        if kind == "text_string_feature":
            bp = int(a[11]) - 1
            al = ["BOTTOM_", "MIDDLE_", "TOP_"][bp // 3] + ["LEFT", "CENTER", "RIGHT"][bp % 3]
            t = msp.add_text(a[3], height=float(a[6]) * k, rotation=float(a[9]),
                             dxfattribs={**attrs(a, False), "style": "JP"})
            t.set_placement((float(a[4]) * k, float(a[5]) * k),
                            align=ezdxf.enums.TextEntityAlignment[al])
        elif kind == "point_marker_feature":
            msp.add_point((float(a[2]) * k, float(a[3]) * k), dxfattribs=attrs(a, False))
        elif kind == "line_feature":
            x1, y1, x2, y2 = (float(v) * k for v in a[4:8])
            msp.add_line((x1, y1), (x2, y2), dxfattribs=attrs(a))
        elif kind == "circle_feature":
            cx, cy, r = (float(v) * k for v in a[4:7])
            msp.add_circle((cx, cy), r, dxfattribs=attrs(a))
        elif kind == "arc_feature":
            cx, cy, r = (float(v) * k for v in a[4:7])
            s, e = float(a[8]), float(a[9])
            if int(a[7]) != 1:
                s, e = e, s
            msp.add_arc((cx, cy), r, s, e, dxfattribs=attrs(a))
        elif kind in ("polyline_feature", "spline_feature"):
            pts = curve_points(kind, a, k)
            if kind == "spline_feature" and len(pts) >= 3:
                msp.add_spline(fit_points=pts, dxfattribs=attrs(a))
            else:
                msp.add_lwpolyline(pts, dxfattribs=attrs(a))
    for layer, colour, cno in doc.fills:
        if 1 <= cno <= len(doc.composites):
            pts = []
            for idx in doc.composites[cno - 1][1]:
                kind, a = doc.items[idx]
                pts += curve_points(kind, a, k)
            if len(pts) >= 3:
                h = msp.add_hatch(dxfattribs=dict(layer=doc.layer_name(layer),
                                                  true_color=ezdxf.colors.rgb2int(doc.rgb(colour))))
                h.paths.add_polyline_path(pts, is_closed=True)
                h.transparency = 0.65
    d.saveas(out + ".dxf")


def main():
    src = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else re.sub(r"\.sfc$", "", src, flags=re.I)
    ents, _ = read_sfc(src)
    doc = Doc(ents)
    fp = None
    for f in ("/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf",):
        try:
            fp = font_manager.FontProperties(fname=f)
        except Exception:
            pass
    print(f"sheet={doc.sheet} scale={doc.sfig_scale} items={len(doc.items)} "
          f"layers={len(doc.layers)} composites={len(doc.composites)} fills={len(doc.fills)}")
    render(doc, out, fp)
    to_dxf(doc, out)
    print("wrote", out + ".png/.pdf/.dxf")


if __name__ == "__main__":
    main()
