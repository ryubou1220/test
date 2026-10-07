#!/usr/bin/env python3
"""土砂検収 求積図（角錐台状の土砂山）を PDF / PNG / DXF で作図する。

寸法は m 単位で指定し、図面は A3 横・S=1:50（用紙上 mm）で描く。
上面は下面の中央に載っているものとする。
"""
import ezdxf
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

# ---- 入力 ----------------------------------------------------------------
L1, W1 = 7.0, 5.0      # 下面 長辺 × 短辺 (m)
L2, W2 = 3.5, 2.0      # 上面 長辺 × 短辺 (m)
H = 1.0                # 高さ (m)
SCALE = 50             # 1:50
TITLE = "土砂検収 求積図"
OUT = "out/dosha_kyusekizu"

PAPER_W, PAPER_H = 420.0, 297.0
FONT = "/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf"
k = 1000.0 / SCALE     # m -> 用紙 mm

# ---- 計算 ----------------------------------------------------------------
A1 = L1 * W1
A2 = L2 * W2
# オベリスク公式 V = h/6 × {(2a1+a2)b1 + (2a2+a1)b2}
T1 = (2 * L1 + L2) * W1
T2 = (2 * L2 + L1) * W2
V = H / 6 * (T1 + T2)
V_avg = (A1 + A2) / 2 * H               # 参考：両端断面平均法
dx, dy = (L1 - L2) / 2, (W1 - W2) / 2   # のり（水平距離）

# ---- 作図プリミティブ ------------------------------------------------------
items = []  # (kind, layer, data)


def line(p, q, layer="OUTLINE", style="-", lw=0.35):
    items.append(("line", layer, (p, q, style, lw)))


def poly(pts, layer="OUTLINE", lw=0.35, closed=True, style="-"):
    pts = list(pts) + ([pts[0]] if closed else [])
    for p, q in zip(pts, pts[1:]):
        line(p, q, layer, style, lw)


def text(p, s, h=3.0, layer="TEXT", ha="center", va="center", rot=0.0):
    items.append(("text", layer, (p, s, h, ha, va, rot)))


def arrow(tip, direction):
    """塗りつぶし矢印（長さ2.5mm）。direction は単位ベクトル。"""
    ux, uy = direction
    b = (tip[0] - 2.5 * ux, tip[1] - 2.5 * uy)
    n = (-uy * 0.6, ux * 0.6)
    items.append(("solid", "DIM", [tip, (b[0] + n[0], b[1] + n[1]), (b[0] - n[0], b[1] - n[1])]))


def dim_h(x1, x2, y_obj, y_dim, value):
    """水平寸法。y_obj は測る対象の高さ、y_dim は寸法線の高さ。"""
    s = 1 if y_dim > y_obj else -1
    for x in (x1, x2):
        line((x, y_obj + s * 1.0), (x, y_dim + s * 1.5), "DIM", lw=0.13)
    line((x1, y_dim), (x2, y_dim), "DIM", lw=0.13)
    arrow((x1, y_dim), (-1, 0))
    arrow((x2, y_dim), (1, 0))
    text(((x1 + x2) / 2, y_dim + 1.2), f"{value:,.3f}", 2.5, "DIM", va="bottom")


def dim_v(y1, y2, x_obj, x_dim, value):
    s = 1 if x_dim > x_obj else -1
    for y in (y1, y2):
        line((x_obj + s * 1.0, y), (x_dim + s * 1.5, y), "DIM", lw=0.13)
    line((x_dim, y1), (x_dim, y2), "DIM", lw=0.13)
    arrow((x_dim, y1), (0, -1))
    arrow((x_dim, y2), (0, 1))
    text((x_dim - 1.2, (y1 + y2) / 2), f"{value:,.3f}", 2.5, "DIM", va="bottom", rot=90)


# ---- 図枠・表題欄 ---------------------------------------------------------
poly([(10, 10), (410, 10), (410, 287), (10, 287)], "FRAME", lw=0.7)
text((210, 278), TITLE, 7, "TEXT")
line((175, 273.5), (245, 273.5), "TEXT", lw=0.35)

tb_x, tb_y = 290, 10
rows = [("件　名", "土砂検収"), ("図面名", "求積図"), ("縮　尺", f"S=1:{SCALE}"),
        ("単　位", "m, m², m³"), ("作成日", "")]
rh = 8
for i, (a, b) in enumerate(rows):
    y = tb_y + rh * i
    text((tb_x + 12, y + rh / 2), a, 3)
    text((tb_x + 70, y + rh / 2), b, 3)
poly([(tb_x, tb_y), (410, tb_y), (410, tb_y + rh * len(rows)), (tb_x, tb_y + rh * len(rows))],
     "FRAME", lw=0.5)
for i in range(1, len(rows)):
    line((tb_x, tb_y + rh * i), (410, tb_y + rh * i), "FRAME", lw=0.18)
line((tb_x + 24, tb_y), (tb_x + 24, tb_y + rh * len(rows)), "FRAME", lw=0.18)

# ---- 平面図 ---------------------------------------------------------------
px, py = 45, 160                         # 下面左下の用紙位置
bot = [(px, py), (px + L1 * k, py), (px + L1 * k, py + W1 * k), (px, py + W1 * k)]
top = [(px + dx * k, py + dy * k), (px + (dx + L2) * k, py + dy * k),
       (px + (dx + L2) * k, py + (dy + W2) * k), (px + dx * k, py + (dy + W2) * k)]
poly(bot, lw=0.5)
poly(top, lw=0.5)
for b, t in zip(bot, top):
    line(b, t, "OUTLINE", lw=0.25)       # 稜線
for pts, name in ((bot, "下面"), (top, "上面")):
    pass
text((px + L1 * k / 2, py + W1 * k / 2 + 3), "上面", 3)
text((px + L1 * k / 2, py + W1 * k / 2 - 3), f"A2={A2:.3f}m²", 2.5)
text((px + 12, py + 5), "下面", 3)
text((px + L1 * k / 2, py - 18), "平　面　図", 4.5)
# 寸法
dim_h(bot[0][0], bot[1][0], py, py - 9, L1)
dim_h(top[3][0], top[2][0], top[3][1], py + W1 * k + 7, L2)
dim_h(bot[3][0], top[3][0], py + W1 * k, py + W1 * k + 14, dx)
dim_h(top[2][0], bot[2][0], py + W1 * k, py + W1 * k + 14, dx)
dim_v(bot[1][1], bot[2][1], bot[1][0], bot[1][0] + 10, W1)
dim_v(top[0][1], top[3][1], top[1][0], bot[1][0] + 22, W2)
dim_v(bot[0][1], top[0][1], px, px - 10, dy)
dim_v(top[3][1], bot[3][1], px, px - 10, dy)
# 頂点番号
for i, p in enumerate(bot, 1):
    ox = -3 if i in (1, 4) else 3
    oy = -3 if i in (1, 2) else 3
    text((p[0] + ox, p[1] + oy), str(i), 2.5)
for i, p in enumerate(top, 5):
    ox = 2.5 if i in (5, 8) else -2.5
    oy = 2.5 if i in (5, 6) else -2.5
    text((p[0] + ox, p[1] + oy), str(i), 2.5)

# ---- 正面図（長辺方向） ----------------------------------------------------
fx, fy = px, 100
prof = [(fx, fy), (fx + L1 * k, fy), (fx + (dx + L2) * k, fy + H * k), (fx + dx * k, fy + H * k)]
poly(prof, lw=0.5)
line((fx - 8, fy), (fx + L1 * k + 8, fy), "OUTLINE", lw=0.18)    # 地盤線
text((fx + L1 * k / 2, fy - 18), "正　面　図", 4.5)
dim_h(fx, fx + L1 * k, fy, fy - 8, L1)
dim_h(prof[3][0], prof[2][0], fy + H * k, fy + H * k + 6, L2)
dim_v(fy, fy + H * k, fx + L1 * k, fx + L1 * k + 10, H)
text((fx + dx * k / 2 - 4, fy + H * k / 2 + 4), f"1:{dx / H:.2f}", 2.5, rot=0)

# ---- 側面図（短辺方向） ----------------------------------------------------
sx, sy = 225, 100
side = [(sx, sy), (sx + W1 * k, sy), (sx + (dy + W2) * k, sy + H * k), (sx + dy * k, sy + H * k)]
poly(side, lw=0.5)
line((sx - 8, sy), (sx + W1 * k + 8, sy), "OUTLINE", lw=0.18)
text((sx + W1 * k / 2, sy - 18), "側　面　図", 4.5)
dim_h(sx, sx + W1 * k, sy, sy - 8, W1)
dim_h(side[3][0], side[2][0], sy + H * k, sy + H * k + 6, W2)
dim_v(sy, sy + H * k, sx + W1 * k, sx + W1 * k + 10, H)
text((sx + dy * k / 2 - 4, sy + H * k / 2 + 4), f"1:{dy / H:.2f}", 2.5)

# ---- 求積表 ---------------------------------------------------------------
cx, cy = 225, 262
text((cx + 85, cy + 3), "求　積　表", 4.5)
calc = [
    ("下面積 A1", f"a1×b1 = {L1:.3f} × {W1:.3f}", f"{A1:,.3f} m²"),
    ("上面積 A2", f"a2×b2 = {L2:.3f} × {W2:.3f}", f"{A2:,.3f} m²"),
    ("高さ h", "", f"{H:.3f} m"),
    ("土量 V", "h/6×{(2a1+a2)b1+(2a2+a1)b2}", ""),
    ("", f"={H:.3f}/6×{{(2×{L1:.3f}+{L2:.3f})×{W1:.3f}+(2×{L2:.3f}+{L1:.3f})×{W2:.3f}}}", ""),
    ("", f"={H:.3f}/6×({T1:.3f}+{T2:.3f})", f"{V:,.3f} m³"),
]
col = [cx, cx + 24, cx + 150, cx + 175]
rh2 = 9
top_y = cy - 4
for i, (a, b, c) in enumerate(calc):
    y = top_y - rh2 * (i + 1)
    text((col[0] + 2, y + rh2 / 2), a, 2.8, ha="left")
    text((col[1] + 2, y + rh2 / 2), b, 2.8, ha="left")
    text((col[3] - 2, y + rh2 / 2), c, 2.8, ha="right")
n = len(calc)
poly([(col[0], top_y), (col[3], top_y), (col[3], top_y - rh2 * n), (col[0], top_y - rh2 * n)],
     "FRAME", lw=0.5)
for i in range(1, n):
    if i < 4:  # 土量の3行はつなげる
        line((col[0], top_y - rh2 * i), (col[3], top_y - rh2 * i), "FRAME", lw=0.18)
for x in col[1:3]:
    line((x, top_y), (x, top_y - rh2 * n), "FRAME", lw=0.18)
# 合計欄
y = top_y - rh2 * n
poly([(col[0], y), (col[3], y), (col[3], y - 11), (col[0], y - 11)], "FRAME", lw=0.7)
text((col[0] + 2, y - 5.5), "検収土量", 3.5, ha="left")
text((col[3] - 2, y - 5.5), f"V = {V:,.2f} m³", 4.2, ha="right")
# 注記
notes = [
    "注）1. 土砂山を角錐台（上面は下面の中央）とみなし、オベリスク公式で算出した。",
    "　　2. a1, b1：下面の長辺・短辺　a2, b2：上面の長辺・短辺",
    f"　　3. 参考：両端断面平均法 (A1+A2)/2×h = {V_avg:,.3f} m³（過大となる）",
]
for i, s in enumerate(notes):
    text((col[0], y - 19 - 6 * i), s, 2.6, ha="left")

# ---- 立体図（等角投影） ------------------------------------------------------
# 3D 頂点 (m)：下面 1-4、上面 5-8（平面図の番号と同じ）
V3 = [(0, 0, 0), (L1, 0, 0), (L1, W1, 0), (0, W1, 0),
      (dx, dy, H), (dx + L2, dy, H), (dx + L2, dy + W2, H), (dx, dy + W2, H)]
FACES = [(0, 3, 2, 1), (4, 5, 6, 7),                       # 底面・天端
         (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]  # 法面 前・右・後・左
ISO_F = 8.0                     # 立体図の倍率（mm/m、縮尺任意）
iso_ox, iso_oy = 135, 22        # 下面 1 番の用紙位置
C30, S30 = 0.8660254, 0.5


def iso(p):
    x, y, z = p
    return (iso_ox + (x - y) * C30 * ISO_F + W1 * C30 * ISO_F, iso_oy + ((x + y) * S30 + z) * ISO_F)


def normal(f):
    a, b, c = (V3[i] for i in f[:3])
    u = [b[j] - a[j] for j in range(3)]
    v = [c[j] - a[j] for j in range(3)]
    return (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])


VIEW = (-1, -1, 1)              # 視線（観察者の方向）
shade = {(0, 1, 5, 4): "#c9b48f", (3, 0, 4, 7): "#b39c74", (4, 5, 6, 7): "#e3d6ba"}
visible_edges = set()
for f in FACES:
    n = normal(f)
    if sum(n[i] * VIEW[i] for i in range(3)) > 0:
        items.append(("face", "ISO", ([iso(V3[i]) for i in f], shade.get(f, "#d8c8a4"))))
        for a, b in zip(f, f[1:] + f[:1]):
            visible_edges.add(frozenset((a, b)))
all_edges = {frozenset((a, b)) for f in FACES for a, b in zip(f, f[1:] + f[:1])}
for e in all_edges:
    a, b = sorted(e)
    if e in visible_edges:
        line(iso(V3[a]), iso(V3[b]), "ISO", lw=0.35)
    else:
        line(iso(V3[a]), iso(V3[b]), "ISO-HIDDEN", style="--", lw=0.18)
cen = iso((L1 / 2, W1 / 2, H / 2))
for i, p in enumerate(V3, 1):
    q = iso(p)
    ux, uy = q[0] - cen[0], q[1] - cen[1]
    ln = (ux * ux + uy * uy) ** 0.5 or 1
    r = 3.0 if i <= 4 else 2.2         # 頂点から外側へずらして番号を置く
    text((q[0] + ux / ln * r, q[1] + uy / ln * r), str(i), 2.2, "ISO")


def mid(a, b):
    return ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)


text(mid(iso(V3[0]), iso(V3[1])), f"a1={L1:.3f}", 2.4, "DIM", ha="left", va="top", rot=30)
text(mid(iso(V3[0]), iso(V3[3])), f"b1={W1:.3f}", 2.4, "DIM", ha="right", va="top", rot=-30)
text((iso_ox - 20, iso_oy + 30), "立　体　図", 4.5)
text((iso_ox - 20, iso_oy + 23), "（縮尺任意）", 2.6)

# ---- 出力：PDF / PNG -------------------------------------------------------
STYLE = {"-": "-", "--": (0, (4, 2))}


def render_pdf():
    fp = font_manager.FontProperties(fname=FONT)
    fig = plt.figure(figsize=(PAPER_W / 25.4, PAPER_H / 25.4))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, PAPER_W)
    ax.set_ylim(0, PAPER_H)
    ax.set_aspect("equal")
    ax.axis("off")
    pt = 72 / 25.4
    colours = {"DIM": "#1f4fbf", "OUTLINE": "black", "FRAME": "black", "TEXT": "black",
               "ISO": "black", "ISO-HIDDEN": "#666666"}
    for kind, layer, d in items:
        c = colours.get(layer, "black")
        if kind == "line":
            (p, q, st, lw) = d
            ax.plot([p[0], q[0]], [p[1], q[1]], color=c, lw=lw * pt, linestyle=STYLE[st],
                    solid_capstyle="butt")
        elif kind == "solid":
            ax.fill([p[0] for p in d], [p[1] for p in d], color=c, lw=0)
        elif kind == "face":
            pts, fc = d
            ax.fill([p[0] for p in pts], [p[1] for p in pts], color=fc, lw=0)
        elif kind == "text":
            p, s, h, ha, va, rot = d
            ax.text(p[0], p[1], s, fontproperties=fp, fontsize=h * pt * 1.15, color=c,
                    ha=ha, va=va, rotation=rot, rotation_mode="anchor")
    fig.savefig(OUT + ".pdf")
    fig.savefig(OUT + ".png", dpi=150)
    plt.close(fig)


def render_dxf():
    doc = ezdxf.new("R2018", setup=True)
    doc.styles.new("JP", dxfattribs={"font": "msgothic.ttc"})
    colours = {"DIM": 5, "OUTLINE": 7, "FRAME": 7, "TEXT": 7, "ISO": 7, "ISO-HIDDEN": 8,
               "ISO-FACE": 254}
    for name, c in colours.items():
        doc.layers.add(name, color=c)
    msp = doc.modelspace()
    va_map = {"bottom": "BOTTOM", "center": "MIDDLE", "top": "TOP"}
    ha_map = {"left": "LEFT", "center": "CENTER", "right": "RIGHT"}
    for kind, layer, d in items:
        if kind == "line":
            p, q, _st, lw = d
            at = {"layer": layer, "lineweight": int(lw * 100)}
            if _st == "--":
                at["linetype"] = "HIDDEN"
            msp.add_line(p, q, dxfattribs=at)
        elif kind == "solid":
            msp.add_solid([d[0], d[1], d[2]], dxfattribs={"layer": layer})
        elif kind == "face":
            pts, fc = d
            h = msp.add_hatch(dxfattribs={"layer": "ISO-FACE",
                                          "true_color": ezdxf.colors.rgb2int(tuple(int(fc[i:i + 2], 16) for i in (1, 3, 5)))})
            h.paths.add_polyline_path(pts, is_closed=True)
        elif kind == "text":
            p, s, h, ha, va, rot = d
            t = msp.add_text(s, height=h, rotation=rot, dxfattribs={"layer": layer, "style": "JP"})
            t.set_placement(p, align=ezdxf.enums.TextEntityAlignment[f"{va_map[va]}_{ha_map[ha]}"])
    doc.saveas(OUT + ".dxf")


def render_3d():
    """3D モデル（実寸 m）：3D DXF（3DFACE）と STL。"""
    doc = ezdxf.new("R2018")
    doc.layers.add("DOSHA-3D", color=33)
    msp = doc.modelspace()
    for f in FACES:
        msp.add_3dface([V3[i] for i in f], dxfattribs={"layer": "DOSHA-3D"})
    doc.saveas(OUT + "_3d.dxf")
    with open(OUT + ".stl", "w") as fp:
        fp.write("solid dosha\n")
        for f in FACES:
            for tri in ((f[0], f[1], f[2]), (f[0], f[2], f[3])):
                a, b, c = (V3[i] for i in tri)
                u = [b[j] - a[j] for j in range(3)]
                v = [c[j] - a[j] for j in range(3)]
                n = (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])
                ln = sum(x * x for x in n) ** 0.5
                fp.write("  facet normal %g %g %g\n    outer loop\n" % tuple(x / ln for x in n))
                for p in (a, b, c):
                    fp.write("      vertex %g %g %g\n" % p)
                fp.write("    endloop\n  endfacet\n")
        fp.write("endsolid dosha\n")


def mesh_volume():
    """閉じたメッシュの体積（発散定理）— オベリスク公式の検算用。"""
    vol = 0.0
    for f in FACES:
        for tri in ((f[0], f[1], f[2]), (f[0], f[2], f[3])):
            a, b, c = (V3[i] for i in tri)
            vol += (a[0] * (b[1] * c[2] - b[2] * c[1]) - a[1] * (b[0] * c[2] - b[2] * c[0])
                    + a[2] * (b[0] * c[1] - b[1] * c[0])) / 6
    return vol


if __name__ == "__main__":
    render_pdf()
    render_dxf()
    render_3d()
    print(f"mesh volume check = {mesh_volume():.3f} m3")
    print(f"A1={A1:.3f} A2={A2:.3f} V={V:.3f} (両端断面平均 {V_avg:.3f})")
