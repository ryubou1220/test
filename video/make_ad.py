"""USBケーブル 15秒プロモーション動画ジェネレーター.

Usage: python3 video/make_ad.py
出力: video/usb_cable_ad.mp4 (1080x1920 / 30fps / 15秒 / BGM付き)
"""
import math
import os
import subprocess
import tempfile
import wave
from multiprocessing import Pool

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

OUT_W, OUT_H = 1080, 1920
SS = 2  # supersampling
W, H = OUT_W * SS, OUT_H * SS
FPS = 30
DURATION = 15
N_FRAMES = FPS * DURATION
FONT_PATH = "/usr/share/fonts/opentype/ipafont-gothic/ipagp.ttf"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT_PATH = os.path.join(HERE, "usb_cable_ad.mp4")

# scene boundaries (seconds)
S1, S2, S3, S4 = 0.0, 4.0, 8.0, 12.0

_fonts = {}


def font(size):
    size = int(size * SS)
    if size not in _fonts:
        _fonts[size] = ImageFont.truetype(FONT_PATH, size)
    return _fonts[size]


# ---------- easing ----------
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def prog(t, start, dur):
    return clamp((t - start) / dur)


def ease_out(x):
    return 1 - (1 - x) ** 3


def ease_in_out(x):
    return 3 * x * x - 2 * x * x * x


def ease_back(x, s=1.9):
    x -= 1
    return x * x * ((s + 1) * x + s) + 1


def lerp(a, b, x):
    return a + (b - a) * x


def lerp_col(c1, c2, x):
    return tuple(int(lerp(a, b, x)) for a, b in zip(c1, c2))


# ---------- drawing helpers ----------
def gradient(top, bottom):
    arr = np.linspace(0, 1, H)[:, None, None]
    col = np.array(top)[None, None, :] * (1 - arr) + np.array(bottom)[None, None, :] * arr
    col = np.repeat(col, W, axis=1).astype(np.uint8)
    return Image.fromarray(col, "RGB").convert("RGBA")


def text(img, s, cx, cy, size, fill, alpha=1.0, scale=1.0, stroke=0.035,
         stroke_fill=None, shadow=True):
    """Draw centered (bold-ish) text with optional scale and alpha."""
    if alpha <= 0 or size * scale * SS < 1:
        return
    f = font(size * scale)
    sw = max(1, int(f.size * stroke))
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    x, y = cx * SS, cy * SS
    if shadow:
        d.text((x + 6 * SS, y + 8 * SS), s, font=f, anchor="mm",
               fill=(0, 0, 0, 110), stroke_width=sw, stroke_fill=(0, 0, 0, 110))
    d.text((x, y), s, font=f, anchor="mm", fill=fill,
           stroke_width=sw, stroke_fill=stroke_fill or fill)
    if alpha < 1:
        a = layer.getchannel("A").point(lambda v: int(v * alpha))
        layer.putalpha(a)
    img.alpha_composite(layer)


def S(v):
    return int(v * SS)


def bezier(p0, p1, p2, p3, n=80):
    pts = []
    for i in range(n + 1):
        t = i / n
        u = 1 - t
        x = u ** 3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t ** 3 * p3[0]
        y = u ** 3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t ** 3 * p3[1]
        pts.append((x, y))
    return pts


def draw_cable(d, pts, width, color, highlight):
    sp = [(S(x), S(y)) for x, y in pts]
    d.line(sp, fill=color, width=S(width), joint="curve")
    for x, y in (sp[0], sp[-1]):
        r = S(width) // 2
        d.ellipse((x - r, y - r, x + r, y + r), fill=color)
    # braided texture: short diagonal ticks
    for i in range(1, len(sp) - 1, 2):
        (x0, y0), (x1, y1) = sp[i - 1], sp[i + 1]
        dx, dy = x1 - x0, y1 - y0
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        r = S(width) * 0.38
        d.line((x0 + nx * r, y0 + ny * r, x1 - nx * r, y1 - ny * r),
               fill=highlight, width=max(2, S(width * 0.12)))


def draw_usbc(d, x, y, angle, scale=1.0):
    """USB-C plug centered at (x, y) pointing in direction `angle` (radians)."""
    ca, sa = math.cos(angle), math.sin(angle)

    def tr(px, py):
        return (S(x + (px * ca - py * sa) * scale), S(y + (px * sa + py * ca) * scale))

    def poly(points, fill):
        d.polygon([tr(px, py) for px, py in points], fill=fill)

    # boot (strain relief)
    poly([(-70, -34), (10, -40), (10, 40), (-70, 34)], (40, 44, 56))
    poly([(-110, -18), (-70, -26), (-70, 26), (-110, 18)], (30, 34, 44))
    # metal shell
    poly([(10, -30), (90, -30), (98, -22), (98, 22), (90, 30), (10, 30)], (205, 212, 222))
    poly([(10, -30), (90, -30), (98, -22), (98, -8), (10, -8)], (235, 240, 246))
    poly([(30, -10), (86, -10), (86, 10), (30, 10)], (60, 64, 76))
    # LED ring
    poly([(-8, -40), (0, -40), (0, 40), (-8, 40)], (0, 230, 255))


def lightning(d, cx, cy, size, fill):
    pts = [(0.15, -1), (-0.55, 0.12), (-0.05, 0.12), (-0.2, 1), (0.55, -0.15), (0.05, -0.15)]
    d.polygon([(S(cx + px * size), S(cy + py * size)) for px, py in pts], fill=fill)


def glow(img, color, cx, cy, r, alpha):
    if alpha <= 0:
        return
    layer = Image.new("RGBA", (W // 4, H // 4), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    q = SS / 4
    d.ellipse((cx * q - r * q, cy * q - r * q, cx * q + r * q, cy * q + r * q),
              fill=color + (int(255 * alpha),))
    layer = layer.filter(ImageFilter.GaussianBlur(r * q * 0.45)).resize((W, H))
    img.alpha_composite(layer)


def rounded(d, box, r, fill, outline=None, width=0):
    d.rounded_rectangle([S(v) for v in box], radius=S(r), fill=fill,
                        outline=outline, width=S(width) if width else 0)


# ---------- scenes ----------
def scene_speed(t):
    """0-4s: 充電スピード"""
    img = gradient((8, 14, 40), (10, 40, 90))
    d = ImageDraw.Draw(img)
    # speed lines
    rng = np.random.default_rng(7)
    for i in range(26):
        y = rng.uniform(0, OUT_H)
        speed = rng.uniform(1600, 3200)
        length = rng.uniform(120, 420)
        x = (rng.uniform(0, OUT_W + 600) + t * speed) % (OUT_W + 600) - 300
        d.line((S(x - length), S(y), S(x), S(y)), fill=(80, 200, 255, 90), width=S(4))

    # phone
    pin = ease_back(prog(t, 0.15, 0.6))
    px, py = 540, 980 + (1 - pin) * 900
    rounded(d, (px - 210, py - 380, px + 210, py + 380), 50, (22, 26, 36),
            outline=(120, 140, 170), width=6)
    rounded(d, (px - 185, py - 350, px + 185, py + 350), 34, (14, 20, 46))

    charge = ease_in_out(prog(t, 0.8, 2.3))
    pct = int(charge * 100)
    # battery
    bx0, by0, bx1, by1 = px - 110, py - 230, px + 110, py + 200
    rounded(d, (px - 40, by0 - 30, px + 40, by0 + 4), 8, (200, 210, 225))
    rounded(d, (bx0, by0, bx1, by1), 26, None, outline=(200, 210, 225), width=10)
    fill_top = lerp(by1 - 18, by0 + 18, charge)
    bar_col = lerp_col((255, 70, 70), (40, 240, 130), clamp(charge * 1.4))
    if charge > 0.01:
        rounded(d, (bx0 + 18, fill_top, bx1 - 18, by1 - 18), 14, bar_col)
    lightning(d, px, (by0 + by1) / 2, 90, (255, 235, 60))
    text(img, f"{pct}%", px, py + 285, 84, (255, 255, 255), shadow=False)

    # cable coming from below into phone
    cin = ease_out(prog(t, 0.3, 0.7))
    end_y = py + 380 + 70
    start = (540, OUT_H + 200)
    cur_end = (540, lerp(OUT_H + 300, end_y, cin))
    pts = bezier(start, (540, OUT_H + 50), (540, cur_end[1] + 200), cur_end)
    draw_cable(d, pts, 46, (30, 34, 46), (70, 80, 100))
    draw_usbc(d, cur_end[0], cur_end[1] - 10, -math.pi / 2, 1.0)
    # energy pulses on cable
    if t > 1.0:
        for k in range(5):
            u = ((t * 2.2 + k / 5) % 1.0)
            yy = lerp(OUT_H + 40, end_y + 60, u)
            glow(img, (0, 220, 255), 540, yy, 60, 0.85)

    glow(img, (255, 230, 80), px, (by0 + by1) / 2, 260, 0.25 + 0.2 * math.sin(t * 14))

    # texts
    a = prog(t, 0.2, 0.4)
    text(img, "圧倒的", 540, 250 - (1 - ease_out(a)) * 80, 96, (120, 220, 255), alpha=a)
    s = ease_back(prog(t, 0.45, 0.5))
    text(img, "超急速充電", 540, 400, 150, (255, 235, 60), scale=s,
         stroke_fill=(255, 150, 0))
    if pct >= 100:
        s2 = ease_back(prog(t, 3.1, 0.35))
        text(img, "FULL CHARGE!", 540, 1500, 90, (40, 240, 130), scale=s2)
    return img


def scene_tough(t):
    """4-8s: 壊れにくい"""
    lt = t - S2
    img = gradient((18, 18, 24), (52, 30, 70))
    d = ImageDraw.Draw(img)
    # hex grid backdrop
    for row in range(-1, 18):
        for col in range(-1, 9):
            cx = col * 140 + (70 if row % 2 else 0)
            cy = row * 122 + (lt * 40) % 122
            pts = [(S(cx + 62 * math.cos(math.pi / 3 * k + math.pi / 6)),
                    S(cy + 62 * math.sin(math.pi / 3 * k + math.pi / 6))) for k in range(6)]
            d.polygon(pts, outline=(120, 80, 200, 70), width=S(2))

    # bending cable (flexing animation)
    bend = math.sin(lt * 5.5) * ease_out(prog(lt, 0.2, 0.5))
    left = (150, 1050)
    right = (930, 1050)
    c1 = (330, 1050 - 520 * bend)
    c2 = (750, 1050 + 520 * bend)
    pts = bezier(left, c1, c2, right, 100)
    glow(img, (170, 90, 255), 540, 1050, 380, 0.35)
    draw_cable(d, pts, 54, (60, 64, 80), (140, 150, 175))
    a0 = math.atan2(pts[1][1] - pts[0][1], pts[1][0] - pts[0][0]) + math.pi
    a1 = math.atan2(pts[-1][1] - pts[-2][1], pts[-1][0] - pts[-2][0])
    draw_usbc(d, left[0] + 45 * math.cos(a0), left[1] + 45 * math.sin(a0), a0, 1.1)
    draw_usbc(d, right[0] + 45 * math.cos(a1), right[1] + 45 * math.sin(a1), a1, 1.1)

    # shield badge
    sp = ease_back(prog(lt, 1.6, 0.5))
    if sp > 0:
        cx, cy, r = 540, 1500, 120 * sp
        shield = [(cx, cy - r), (cx + r * 0.9, cy - r * 0.6), (cx + r * 0.8, cy + r * 0.3),
                  (cx, cy + r), (cx - r * 0.8, cy + r * 0.3), (cx - r * 0.9, cy - r * 0.6)]
        d.polygon([(S(x), S(y)) for x, y in shield], fill=(60, 220, 140))
        d.line([(S(cx - r * 0.4), S(cy)), (S(cx - r * 0.08), S(cy + r * 0.35)),
                (S(cx + r * 0.45), S(cy - r * 0.35))], fill=(255, 255, 255), width=S(18 * sp),
               joint="curve")

    a = prog(lt, 0.1, 0.4)
    text(img, "曲げても 引っぱっても", 540, 300 - (1 - ease_out(a)) * 60, 76,
         (220, 200, 255), alpha=a)
    s = ease_back(prog(lt, 0.4, 0.5))
    text(img, "壊れにくい", 540, 470, 160, (255, 255, 255), scale=s,
         stroke_fill=(170, 90, 255))
    a2 = prog(lt, 2.0, 0.4)
    text(img, "断線に強いタフ設計", 540, 1730 - (1 - ease_out(a2)) * 60, 80,
         (60, 230, 150), alpha=a2)
    return img


def scene_sale(t):
    """8-12s: 今なら半額"""
    lt = t - S3
    img = gradient((255, 70, 40), (200, 0, 60))
    # rotating starburst
    burst = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(burst)
    cx, cy = W / 2, S(980)
    R = W * 1.6
    rot = lt * 0.6
    for k in range(18):
        a0 = rot + k * 2 * math.pi / 18
        a1 = a0 + math.pi / 18
        d.polygon([(cx, cy), (cx + R * math.cos(a0), cy + R * math.sin(a0)),
                   (cx + R * math.cos(a1), cy + R * math.sin(a1))], fill=(255, 200, 60, 70))
    img.alpha_composite(burst)
    d = ImageDraw.Draw(img)

    # confetti
    rng = np.random.default_rng(3)
    cols = [(255, 240, 80), (255, 255, 255), (80, 220, 255), (120, 255, 150)]
    for i in range(60):
        x0 = rng.uniform(0, OUT_W)
        vy = rng.uniform(300, 700)
        y = (rng.uniform(-OUT_H, 0) + lt * vy) % (OUT_H + 100) - 50
        x = x0 + math.sin(lt * 3 + i) * 30
        ang = lt * rng.uniform(3, 8) + i
        w, h = 22, 10
        pts = [(x + w * math.cos(ang) - h * math.sin(ang), y + w * math.sin(ang) + h * math.cos(ang)),
               (x - w * math.cos(ang) - h * math.sin(ang), y - w * math.sin(ang) + h * math.cos(ang)),
               (x - w * math.cos(ang) + h * math.sin(ang), y - w * math.sin(ang) - h * math.cos(ang)),
               (x + w * math.cos(ang) + h * math.sin(ang), y + w * math.sin(ang) - h * math.cos(ang))]
        d.polygon([(S(px), S(py)) for px, py in pts], fill=cols[i % 4])

    a = prog(lt, 0.05, 0.3)
    text(img, "今なら", 540, 380 - (1 - ease_out(a)) * 80, 130, (255, 255, 255), alpha=a,
         stroke_fill=(180, 0, 40))

    s = ease_back(prog(lt, 0.4, 0.45), 2.4)
    pulse = 1 + 0.05 * math.sin(max(0, lt - 0.9) * 9)
    if s > 0:
        r = 330 * s * pulse
        glow(img, (255, 255, 120), 540, 980, r * 1.3, 0.6)
        d = ImageDraw.Draw(img)
        d.ellipse((S(540 - r), S(980 - r), S(540 + r), S(980 + r)), fill=(255, 235, 40),
                  outline=(255, 255, 255), width=S(14 * s))
        text(img, "半額", 540, 940, 250, (220, 0, 40), scale=s * pulse, shadow=False,
             stroke=0.07)
        text(img, "50%OFF", 540, 1140, 96, (60, 20, 20), scale=s * pulse, shadow=False)

    a3 = prog(lt, 1.6, 0.4)
    rounded(d, (140, 1480 + (1 - ease_out(a3)) * 200, 940, 1640 + (1 - ease_out(a3)) * 200),
            80, (255, 255, 255, int(235 * a3)))
    text(img, "期間限定セール中！", 540, 1560 + (1 - ease_out(a3)) * 200, 78, (220, 0, 40),
         alpha=a3, shadow=False)
    return img


def scene_cta(t):
    """12-15s: 購入ボタンをクリック"""
    lt = t - S4
    img = gradient((10, 20, 50), (0, 70, 120))
    d = ImageDraw.Draw(img)

    # product hero (coiled cable)
    glow(img, (0, 200, 255), 540, 620, 300, 0.35)
    d = ImageDraw.Draw(img)
    hero_in = ease_out(prog(lt, 0.0, 0.4))
    hy = 620 - (1 - hero_in) * 200
    pts = bezier((300, hy + 40), (300, hy - 260), (780, hy - 260), (780, hy + 40))
    pts += bezier((780, hy + 40), (780, hy + 260), (420, hy + 220), (420, hy + 20))[1:]
    draw_cable(d, pts, 40, (40, 44, 58), (100, 110, 135))
    draw_usbc(d, 300, hy + 140, math.pi / 2, 0.9)
    draw_usbc(d, 420, hy - 80, -math.pi / 2, 0.9)
    lightning(d, 640, hy, 70, (255, 235, 60))

    text(img, "USB 急速充電ケーブル", 540, 200, 78, (255, 255, 255), alpha=hero_in)

    a = prog(lt, 0.2, 0.35)
    text(img, "今すぐチェック！", 540, 1080 - (1 - ease_out(a)) * 60, 96, (255, 235, 60),
         alpha=a, stroke_fill=(255, 140, 0))

    # button
    click_t = 1.6
    press = 0.0
    if click_t <= lt < click_t + 0.25:
        press = math.sin((lt - click_t) / 0.25 * math.pi)
    bs = ease_back(prog(lt, 0.35, 0.45)) * (1 + 0.035 * math.sin(lt * 8)) * (1 - 0.07 * press)
    if bs > 0:
        bw, bh = 400 * bs, 110 * bs
        by = 1380 + press * 8
        glow(img, (255, 120, 0), 540, by, 360 * bs, 0.5)
        d = ImageDraw.Draw(img)
        rounded(d, (540 - bw, by - bh + 14, 540 + bw, by + bh + 14), 110 * bs, (170, 50, 0))
        rounded(d, (540 - bw, by - bh, 540 + bw, by + bh), 110 * bs,
                lerp_col((255, 120, 20), (255, 170, 40), press))
        text(img, "今すぐ購入する ▶", 540, by, 92, (255, 255, 255), scale=bs, shadow=False,
             stroke=0.05)

        # click ripple
        if lt >= click_t:
            rp = prog(lt, click_t, 0.6)
            rr = lerp(40, 380, ease_out(rp))
            ring = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            rd = ImageDraw.Draw(ring)
            rd.ellipse((S(640 - rr), S(1400 - rr), S(640 + rr), S(1400 + rr)),
                       outline=(255, 255, 255, int(255 * (1 - rp))), width=S(10))
            img.alpha_composite(ring)
            d = ImageDraw.Draw(img)

    # cursor (hand pointer as arrow) moving onto button
    mv = ease_in_out(prog(lt, 0.8, 0.75))
    cx = lerp(900, 640, mv)
    cy = lerp(1800, 1400, mv) + press * 10
    if lt > 0.6:
        cs = 1.0 - 0.15 * press
        arrow = [(0, 0), (0, 110), (28, 84), (48, 130), (68, 121), (48, 77), (86, 77)]
        d.polygon([(S(cx + x * cs), S(cy + y * cs)) for x, y in arrow], fill=(255, 255, 255),
                  outline=(20, 20, 20), width=S(5))

    a4 = prog(lt, 2.0, 0.35)
    text(img, "半額は今だけ！ お早めに", 540, 1680, 70, (255, 255, 255), alpha=a4)
    return img


SCENES = [(S1, scene_speed), (S2, scene_tough), (S3, scene_sale), (S4, scene_cta)]
TRANS = 0.25  # flash transition length


def render(i):
    t = i / FPS
    idx = max(k for k, (st, _) in enumerate(SCENES) if t >= st)
    img = SCENES[idx][1](t)
    # white flash at scene starts
    if idx > 0:
        dt = t - SCENES[idx][0]
        if dt < TRANS:
            a = int(255 * (1 - dt / TRANS) * 0.85)
            img.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, a)))
    # fade-in at start
    if t < 0.2:
        img.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, int(255 * (1 - t / 0.2)))))
    out = img.convert("RGB").resize((OUT_W, OUT_H), Image.LANCZOS)
    return out.tobytes()


# ---------- audio ----------
def make_audio(path, sr=44100):
    n = int(sr * DURATION)
    t = np.arange(n) / sr
    out = np.zeros(n)
    bpm = 128
    beat = 60 / bpm

    def add(sig, start):
        s = int(start * sr)
        e = min(n, s + len(sig))
        if s < n:
            out[s:e] += sig[: e - s]

    # kick
    kt = np.arange(int(0.25 * sr)) / sr
    kick = np.sin(2 * np.pi * (50 + 120 * np.exp(-kt * 30)) * kt) * np.exp(-kt * 9)
    # hat
    rng = np.random.default_rng(1)
    ht = np.arange(int(0.05 * sr)) / sr
    hat = rng.normal(0, 1, len(ht)) * np.exp(-ht * 90) * 0.25
    for k in range(int(DURATION / beat) + 1):
        add(kick * 0.9, k * beat)
        add(hat, k * beat + beat / 2)

    # bass line (per scene root)
    roots = [55.0, 65.41, 73.42, 82.41]
    for k in range(int(DURATION / (beat / 2))):
        st = k * beat / 2
        sc = min(3, int(st // 4))
        bt = np.arange(int(beat / 2 * sr)) / sr
        f = roots[sc] * (2 if k % 4 == 3 else 1)
        sig = np.sign(np.sin(2 * np.pi * f * bt)) * 0.12 * np.exp(-bt * 6)
        add(sig, st)

    # whoosh at transitions
    wt = np.arange(int(0.4 * sr)) / sr
    whoosh = rng.normal(0, 1, len(wt)) * np.sin(np.pi * wt / 0.4) ** 2 * 0.25
    for st in (S2, S3, S4):
        add(whoosh, st - 0.2)
    # sparkle on 半額
    for j, f in enumerate([1046.5, 1318.5, 1568.0, 2093.0]):
        st_ = np.arange(int(0.35 * sr)) / sr
        add(np.sin(2 * np.pi * f * st_) * np.exp(-st_ * 8) * 0.25, S3 + 0.45 + j * 0.06)
    # click
    ct = np.arange(int(0.06 * sr)) / sr
    add(np.sin(2 * np.pi * 1800 * ct) * np.exp(-ct * 120) * 0.6, S4 + 1.6)
    # charge-up riser in scene 1
    rt = np.arange(int(2.3 * sr)) / sr
    riser = np.sin(2 * np.pi * (300 * rt + 300 * rt ** 2)) * 0.05 * (rt / 2.3)
    add(riser, 0.8)

    out *= np.clip(np.minimum(t / 0.1, (DURATION - t) / 0.6), 0, 1)
    out = np.tanh(out * 1.2) * 0.85
    pcm = (out * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(pcm.tobytes())


def main():
    with tempfile.TemporaryDirectory() as tmp:
        wav = os.path.join(tmp, "bgm.wav")
        make_audio(wav)
        cmd = ["ffmpeg", "-y", "-loglevel", "error",
               "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{OUT_W}x{OUT_H}",
               "-r", str(FPS), "-i", "-", "-i", wav,
               "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
               "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart",
               OUT_PATH]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        with Pool() as pool:
            for k, frame in enumerate(pool.imap(render, range(N_FRAMES), chunksize=4)):
                proc.stdin.write(frame)
                if k % 30 == 0:
                    print(f"frame {k}/{N_FRAMES}", flush=True)
        proc.stdin.close()
        proc.wait()
    print("wrote", OUT_PATH)


if __name__ == "__main__":
    main()
