"""解説動画「大工用語：桟木・垂木・胴縁の違い」を生成するスクリプト。

元記事: https://ameblo.jp/11830ryubou315/entry-12741519516.html
使い方: pip install pyopenjtalk-plus pillow numpy && python3 make_video.py
出力: kaisetsu_zaimoku.mp4（1280x720, 日本語ナレーション＋字幕）
"""
import os
import subprocess
import tempfile
import wave

import numpy as np
import pyopenjtalk
from PIL import Image, ImageDraw, ImageFont

W, H = 1280, 720
FONT = "/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "kaisetsu_zaimoku.mp4")

BG = (250, 246, 238)
INK = (45, 38, 30)
ACCENT = (176, 96, 40)
WOOD = (222, 184, 135)
WOOD_EDGE = (150, 105, 60)
SUB_BG = (30, 30, 30)


def font(size):
    return ImageFont.truetype(FONT, size)


def wrap(text, f, width, draw):
    lines, cur = [], ""
    for ch in text:
        if draw.textlength(cur + ch, font=f) > width:
            lines.append(cur)
            cur = ch
        else:
            cur += ch
    if cur:
        lines.append(cur)
    return lines


def base(title):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 90], fill=ACCENT)
    d.text((40, 22), title, font=font(42), fill="white")
    d.text((W - 260, 34), "りゅう坊の大工用語", font=font(24), fill=(255, 235, 210))
    return img, d


def subtitle(img, text):
    d = ImageDraw.Draw(img)
    f = font(30)
    lines = wrap(text, f, W - 120, d)
    h = 20 + 44 * len(lines)
    d.rectangle([0, H - h, W, H], fill=SUB_BG)
    for i, line in enumerate(lines):
        d.text((60, H - h + 12 + 44 * i), line, font=f, fill="white")


def board(d, x, y, w, h, label=None):
    d.rectangle([x, y, x + w, y + h], fill=WOOD, outline=WOOD_EDGE, width=3)
    for k in range(1, 4):
        yy = y + h * k / 4
        d.line([x + 4, yy, x + w - 4, yy + 2], fill=WOOD_EDGE, width=1)
    if label:
        f = font(26)
        tw = d.textlength(label, font=f)
        d.text((x + (w - tw) / 2, y + h + 12), label, font=f, fill=INK)


# ---- 各シーンの描画 ----

def s_title():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, H], fill=(70, 50, 35))
    d.text((80, 120), "【大工用語】", font=font(48), fill=(255, 210, 160))
    d.text((80, 200), "同じ木材でも呼び方いろいろ！", font=font(64), fill="white")
    d.text((80, 300), "桟木・垂木・胴縁のちがいを解説", font=font(44), fill=(255, 235, 210))
    for i, (w, h) in enumerate([(160, 30), (90, 90), (160, 36)]):
        board(d, 120 + i * 260, 430 + (90 - h) // 2, w, h)
    for i, n in enumerate(["桟木", "垂木", "胴縁"]):
        d.text((150 + i * 260, 540), n, font=font(36), fill="white")
    return img


def s_intro():
    img, d = base("ホームセンターの木材売り場で…")
    d.text((80, 150), "こんな経験ありませんか？", font=font(40), fill=INK)
    for i, t in enumerate(["見た目はほとんど同じ細長い木材", "なのに「桟木」「垂木」「胴縁」と名前がバラバラ", "どれを買えばいいの？ → “わけわかめ”!(^^)"]):
        d.text((110, 240 + i * 70), "・" + t, font=font(34), fill=INK)
    return img


def s_point():
    img, d = base("ポイントは2つ")
    for i, (h, b) in enumerate([("① 使う場所（用途）", "屋根に使う？ 壁に使う？ 仮設に使う？"),
                                ("② 断面の形（厚い・薄い）", "薄い板状か、角材に近いか")]):
        y = 160 + i * 190
        d.rounded_rectangle([80, y, W - 80, y + 150], 20, fill="white", outline=ACCENT, width=4)
        d.text((120, y + 25), h, font=font(42), fill=ACCENT)
        d.text((120, y + 90), b, font=font(32), fill=INK)
    return img


def s_sangi():
    img, d = base("① 桟木（さんぎ）")
    board(d, 120, 210, 380, 40, "断面イメージ：薄い板状")
    d.text((120, 140), "薄くて細長い木材", font=font(36), fill=INK)
    items = ["屋根の下地（瓦を引っかける瓦桟など）", "材木を積むときのすき間づくり（桟積み）", "コンクリート型枠などの仮設材"]
    d.text((580, 140), "主な使い道", font=font(36), fill=ACCENT)
    for i, t in enumerate(items):
        d.text((580, 210 + i * 60), "・" + t, font=font(28), fill=INK)
    d.text((120, 420), "寸法の目安：厚さ15mm前後 × 幅30〜45mm程度", font=font(30), fill=INK)
    return img


def s_taruki():
    img, d = base("② 垂木（たるき）")
    board(d, 200, 200, 120, 120, "断面イメージ：角材に近い")
    d.text((120, 140), "ほぼ正方形の、しっかりした角材", font=font(36), fill=INK)
    # 屋根の図
    ox, oy = 680, 370
    d.polygon([(ox, oy), (ox + 260, oy - 220), (ox + 520, oy)], outline=INK, width=4)
    d.line([(ox + 260, oy - 220), (ox, oy)], fill=WOOD_EDGE, width=14)
    d.line([(ox + 260, oy - 220), (ox + 520, oy)], fill=WOOD_EDGE, width=14)
    d.text((ox + 300, oy - 230), "棟", font=font(26), fill=INK)
    d.text((ox + 20, oy - 150), "垂木", font=font(30), fill=ACCENT)
    d.text((120, 420), "棟から軒先へ斜めに架け、屋根の重さを支える", font=font(30), fill=INK)
    d.text((120, 470), "寸法の目安：30×40mm、45×45mm、45×60mm など", font=font(30), fill=INK)
    return img


def s_dobuchi():
    img, d = base("③ 胴縁（どうぶち）")
    board(d, 120, 210, 380, 45, "断面イメージ：薄め〜中くらい")
    d.text((120, 140), "壁の下地に使う木材", font=font(36), fill=INK)
    # 壁の図
    x0, y0 = 680, 130
    for k in range(4):
        d.rectangle([x0 + k * 150, y0, x0 + k * 150 + 30, y0 + 300], fill=(200, 200, 200), outline=INK)
    for k in range(5):
        y = y0 + 20 + k * 65
        d.rectangle([x0 - 20, y, x0 + 500, y + 18], fill=WOOD, outline=WOOD_EDGE, width=2)
    d.text((x0 + 340, y0 + 310), "↑ 胴縁（横）", font=font(28), fill=ACCENT)
    d.text((x0 + 40, y0 + 310), "↑ 柱", font=font(28), fill=INK)
    d.text((120, 490), "柱の上に横（または縦）に打ち付けて", font=font(30), fill=INK)
    d.text((120, 535), "外壁材・壁ボードを留める土台に。壁の強さもアップ", font=font(30), fill=INK)
    return img


def s_compare():
    img, d = base("まとめて比較")
    cols = ["名前", "断面", "主な使う場所"]
    rows = [("桟木", "薄い板状", "屋根の下地・仮設"),
            ("垂木", "角材に近い", "屋根を支える骨組み"),
            ("胴縁", "薄め〜中くらい", "壁の下地")]
    xs = [120, 370, 700]
    y = 150
    d.rectangle([100, y, W - 100, y + 70], fill=ACCENT)
    for x, c in zip(xs, cols):
        d.text((x, y + 15), c, font=font(36), fill="white")
    for i, r in enumerate(rows):
        yy = y + 70 + i * 90
        d.rectangle([100, yy, W - 100, yy + 90], fill="white" if i % 2 == 0 else (245, 235, 220), outline=(220, 200, 180))
        for x, c in zip(xs, r):
            d.text((x, yy + 25), c, font=font(36), fill=INK)
    return img


def s_tips():
    img, d = base("買うときのコツ")
    tips = ["名前だけでなく「寸法（厚さ×幅×長さ）」で確認", "お店や地域によって呼び方が違うこともある", "DIYなら用途に合う太さを選べばOK！"]
    for i, t in enumerate(tips):
        y = 160 + i * 120
        d.ellipse([90, y, 150, y + 60], fill=ACCENT)
        d.text((108, y + 8), str(i + 1), font=font(40), fill="white")
        d.text((180, y + 10), t, font=font(36), fill=INK)
    return img


def s_end():
    img = Image.new("RGB", (W, H), (70, 50, 35))
    d = ImageDraw.Draw(img)
    d.text((120, 200), "同じ木材でも、", font=font(56), fill="white")
    d.text((120, 290), "使う場所と形で名前が変わる！", font=font(56), fill=(255, 210, 160))
    d.text((120, 420), "くわしくはブログ「LifeとWorkをカンタンに！」へ", font=font(34), fill="white")
    d.text((120, 470), "ameblo.jp/11830ryubou315", font=font(30), fill=(255, 235, 210))
    return img


SCENES = [
    (s_title, "こんにちは、りゅう坊です。今日は大工用語のお話。同じような木材なのに、呼び方がいろいろある。桟木、垂木、胴縁のちがいを解説します。"),
    (s_intro, "ホームセンターの木材売り場で、見た目はほとんど同じ細長い木材なのに、名前がバラバラで迷ったことはありませんか。まさに、わけわかめ、ですよね。"),
    (s_point, "見分けるポイントは二つです。一つ目は、どこに使うかという用途。二つ目は、断面が薄い板状なのか、角材に近いのか、という形です。"),
    (s_sangi, "まずは桟木。薄くて細長い木材で、主に屋根の下地に使われます。ほかにも、材木を積むときのすき間づくりや、型枠などの仮設材としても活躍します。"),
    (s_taruki, "次に垂木。こちらは正方形に近い、しっかりした角材です。屋根のてっぺんの棟から軒先へ斜めに架けて、屋根の重さを支える大事な骨組みです。"),
    (s_dobuchi, "そして胴縁。こちらは壁の下地に使う木材です。柱の上に横や縦に打ち付けて、外壁材や壁のボードを留める土台になり、壁の強さを高める役目もあります。"),
    (s_compare, "まとめると、桟木は薄い板状で屋根の下地、垂木は角材で屋根の骨組み、胴縁は壁の下地。同じ木材でも、使う場所と形で名前が変わるんです。"),
    (s_tips, "買うときのコツは、名前だけでなく、厚さ、幅、長さの寸法で確認すること。お店や地域で呼び方がちがうこともあるので、DIYなら用途に合う太さを選べば大丈夫です。"),
    (s_end, "以上、大工用語の解説でした。くわしくはブログ、ライフとワークをカンタンに、をご覧ください。ご視聴ありがとうございました。"),
]


def main():
    tmp = tempfile.mkdtemp()
    segs = []
    for i, (fn, text) in enumerate(SCENES):
        audio, sr = pyopenjtalk.tts(text, speed=1.05)
        pad = np.zeros(int(sr * 0.6))
        audio = np.concatenate([pad, audio, pad])
        audio = np.clip(audio, -32768, 32767).astype(np.int16)
        wav = os.path.join(tmp, f"{i}.wav")
        with wave.open(wav, "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(sr)
            w.writeframes(audio.tobytes())
        img = fn()
        subtitle(img, text)
        png = os.path.join(tmp, f"{i}.png")
        img.save(png)
        seg = os.path.join(tmp, f"{i}.mp4")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-i", png, "-i", wav,
                        "-c:v", "libx264", "-tune", "stillimage", "-pix_fmt", "yuv420p", "-r", "30",
                        "-c:a", "aac", "-b:a", "128k", "-ar", "48000", "-shortest", seg], check=True)
        segs.append(seg)
    lst = os.path.join(tmp, "list.txt")
    with open(lst, "w") as f:
        f.writelines(f"file '{s}'\n" for s in segs)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst,
                    "-c", "copy", "-movflags", "+faststart", OUT], check=True)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
