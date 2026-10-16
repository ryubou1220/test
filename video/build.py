# -*- coding: utf-8 -*-
import os, subprocess, sys, re
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(__file__))
from script import SLIDES

D = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(D, "out"); os.makedirs(OUT, exist_ok=True)
FONT = "/usr/share/fonts/opentype/ipafont-gothic/ipagp.ttf"
VOICE = os.path.join(D, "voice/MMDAgent_Example-1.8/Voice/mei/mei_normal.htsvoice")
DIC = "/var/lib/mecab/dic/open-jtalk/naist-jdic"
W, H = 1920, 1080

BG = (16, 27, 48); BG2 = (24, 40, 68); CARD = (32, 52, 86)
ACCENT = (255, 176, 59); TEXT = (240, 244, 250); MUTED = (160, 176, 200); RED = (255, 107, 107)

def f(size): return ImageFont.truetype(FONT, size)

def tw(d, s, fn): return d.textlength(s, font=fn)

def wrap(d, s, fn, maxw):
    lines = []
    for para in s.split("\n"):
        cur = ""
        for ch in para:
            if tw(d, cur + ch, fn) > maxw and cur:
                lines.append(cur); cur = ch
            else:
                cur += ch
        lines.append(cur)
    return lines

def bold(d, xy, s, fn, fill, w=1, anchor="la"):
    d.text(xy, s, font=fn, fill=fill, stroke_width=w, stroke_fill=fill, anchor=anchor)

def base(slide, idx, total):
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    # 背景の装飾
    d.polygon([(W - 520, 0), (W, 0), (W, 520)], fill=BG2)
    d.ellipse((-260, H - 300, 260, H + 220), fill=BG2)
    # 章ラベル
    if slide["kind"] != "cover":
        lf = f(30)
        lw = tw(d, slide["label"], lf)
        d.rounded_rectangle((100, 70, 100 + lw + 48, 120), radius=25, fill=ACCENT)
        bold(d, (124, 95), slide["label"], lf, BG, 1, "lm")
    # 進捗バー
    d.rectangle((0, H - 8, W, H), fill=BG2)
    d.rectangle((0, H - 8, int(W * (idx + 1) / total), H), fill=ACCENT)
    return im, d

def title_block(d, title, y=150, size=64):
    fn = f(size)
    for line in title.split("\n"):
        bold(d, (100, y), line, fn, TEXT, 2)
        y += int(size * 1.3)
    d.rectangle((100, y + 10, 220, y + 16), fill=ACCENT)
    return y + 60

def render(slide, idx, total):
    im, d = base(slide, idx, total)
    k, pts = slide["kind"], slide["points"]
    if k == "cover":
        bold(d, (W // 2, 230), "電子書籍 解説", f(40), ACCENT, 1, "mm")
        y = 360
        for line in slide["title"].split("\n"):
            size = 96 if y == 360 else 64
            bold(d, (W // 2, y), line, f(size), TEXT, 3 if size == 96 else 2, "mm")
            y += 120
        d.rectangle((W // 2 - 80, y, W // 2 + 80, y + 6), fill=ACCENT)
        y += 70
        for p in pts:
            d.text((W // 2, y), p, font=f(46), fill=MUTED, anchor="mm"); y += 70
    elif k == "agenda":
        y0 = title_block(d, slide["title"])
        fn = f(38)
        for i, p in enumerate(pts):
            col, row = i % 2, i // 2
            x, y = 100 + col * 860, y0 + row * 130
            d.rounded_rectangle((x, y, x + 820, y + 105), radius=18, fill=CARD)
            d.text((x + 36, y + 52), p, font=fn, fill=TEXT, anchor="lm")
    elif k == "statement":
        y = title_block(d, slide["title"], size=72) + 30
        for i, p in enumerate(pts):
            fn = f(52)
            col = ACCENT if i == len(pts) - 1 else TEXT
            d.rounded_rectangle((100, y, W - 100, y + 120), radius=20, fill=CARD)
            d.rectangle((100, y, 112, y + 120), fill=col)
            bold(d, (150, y + 60), p, fn, col, 1 if col == ACCENT else 0, "lm")
            y += 150
    elif k == "bullets":
        y = title_block(d, slide["title"]) + 10
        fn = f(44)
        for p in pts:
            lines = wrap(d, p, fn, W - 360)
            h = 50 * len(lines) + 56
            d.rounded_rectangle((100, y, W - 100, y + h), radius=18, fill=CARD)
            d.ellipse((140, y + h // 2 - 12, 164, y + h // 2 + 12), fill=ACCENT)
            ty = y + h // 2 - (len(lines) - 1) * 25
            for ln in lines:
                d.text((200, ty), ln, font=fn, fill=TEXT, anchor="lm"); ty += 50
            y += h + 22
    elif k == "grid":
        y0 = title_block(d, slide["title"]) + 10
        cw, ch = 540, 250
        for i, p in enumerate(pts):
            name, desc = p.split("|")
            col, row = i % 3, i // 3
            x, y = 100 + col * (cw + 50), y0 + row * (ch + 36)
            d.rounded_rectangle((x, y, x + cw, y + ch), radius=22, fill=CARD)
            d.ellipse((x + 30, y + 30, x + 100, y + 100), fill=RED)
            bold(d, (x + 65, y + 65), str(i + 1), f(42), BG, 1, "mm")
            bold(d, (x + 125, y + 65), name, f(46), TEXT, 1, "lm")
            d.text((x + 125, y + 102), "ブレーキ", font=f(26), fill=MUTED)
            ty = y + 160
            for ln in wrap(d, desc, f(32), cw - 70):
                d.text((x + 35, ty), ln, font=f(32), fill=MUTED); ty += 42
    elif k == "twocol":
        y = title_block(d, slide["title"]) + 10
        for p in pts:
            name, desc = p.split("|")
            lines = []
            for part in desc.split("\n"):
                lines += wrap(d, part, f(38), W - 760)
            h = max(150, 52 * len(lines) + 50)
            d.rounded_rectangle((100, y, W - 100, y + h), radius=20, fill=CARD)
            d.rounded_rectangle((100, y, 560, y + h), radius=20, fill=BG2)
            d.rectangle((100, y, 110, y + h), fill=ACCENT)
            bold(d, (140, y + h // 2), name, f(44), ACCENT, 1, "lm")
            ty = y + h // 2 - (len(lines) - 1) * 26
            for ln in lines:
                d.text((600, ty), ln, font=f(38), fill=TEXT, anchor="lm"); ty += 52
            y += h + 26
    elif k in ("steps", "pillars"):
        y0 = title_block(d, slide["title"]) + 30
        n = len(pts); gap = 70
        cw = (W - 200 - gap * (n - 1)) // n
        ch = H - y0 - 230
        for i, p in enumerate(pts):
            name, desc = p.split("|")
            x = 100 + i * (cw + gap)
            d.rounded_rectangle((x, y0, x + cw, y0 + ch), radius=24, fill=CARD)
            lab = f"STEP {i+1}" if k == "steps" else f"柱 {i+1}"
            d.rounded_rectangle((x + 40, y0 + 40, x + 230, y0 + 96), radius=28, fill=ACCENT)
            bold(d, (x + 135, y0 + 68), lab, f(32), BG, 1, "mm")
            ty = y0 + 150
            for ln in wrap(d, name, f(50), cw - 80):
                bold(d, (x + 40, ty), ln, f(50), TEXT, 1); ty += 66
            ty += 20
            for ln in wrap(d, desc, f(36), cw - 80):
                d.text((x + 40, ty), ln, font=f(36), fill=MUTED); ty += 50
            if i < n - 1:
                ax = x + cw + gap // 2; ay = y0 + ch // 2
                d.polygon([(ax - 14, ay - 24), (ax + 16, ay), (ax - 14, ay + 24)], fill=ACCENT)
    return im

def subtitle(im, text):
    im = im.copy()
    d = ImageDraw.Draw(im)
    fn = f(40)
    lines = wrap(d, text, fn, W - 360)
    lh = 56
    h = lh * len(lines) + 40
    top = H - 40 - h
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    od.rounded_rectangle((140, top, W - 140, top + h), radius=16, fill=(0, 0, 0, 185))
    im = Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB")
    d = ImageDraw.Draw(im)
    y = top + 20 + lh // 2
    for ln in lines:
        d.text((W // 2, y), ln, font=fn, fill=(255, 255, 255), anchor="mm"); y += lh
    return im

READ = [("エスエヌエス", "エスエヌエス")]
def to_display(s): return s.replace("エスエヌエス", "SNS")

def tts(text, path):
    tp = path + ".txt"
    open(tp, "w").write(text)
    subprocess.run(["open_jtalk", "-x", DIC, "-m", VOICE, "-r", "1.05", "-fm", "0", "-ow", path, tp], check=True)

def dur(p):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p]).strip())

segs = []
total = len(SLIDES)
for si, s in enumerate(SLIDES):
    b = render(s, si, total)
    b.save(f"{OUT}/slide_{si:02d}.png")
    for ni, n in enumerate(s["narration"]):
        tag = f"{si:02d}_{ni:02d}"
        wav = f"{OUT}/{tag}.wav"
        tts(n, wav)
        img = f"{OUT}/{tag}.png"
        subtitle(b, to_display(n)).save(img)
        lead = 0.6 if ni == 0 else 0.0
        tail = 1.0 if ni == len(s["narration"]) - 1 else 0.35
        mp4 = f"{OUT}/{tag}.mp4"
        dd = dur(wav) + lead + tail
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-loop", "1", "-framerate", "30", "-i", img, "-i", wav,
                        "-filter_complex", f"[1:a]adelay={int(lead*1000)}|{int(lead*1000)},apad,aresample=44100,aformat=channel_layouts=stereo[a]",
                        "-map", "0:v", "-map", "[a]", "-t", f"{dd:.3f}", "-c:v", "libx264", "-tune", "stillimage",
                        "-pix_fmt", "yuv420p", "-r", "30", "-c:a", "aac", "-b:a", "160k", mp4], check=True)
        segs.append(mp4)
    print("slide", si, "done", flush=True)

with open(f"{OUT}/list.txt", "w") as fh:
    for p in segs: fh.write(f"file '{p}'\n")
final = os.path.join(D, "消去方式コンテンツ販売_解説動画.mp4")
subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", f"{OUT}/list.txt",
                "-c", "copy", "-movflags", "+faststart", final], check=True)
print(final, dur(final))
