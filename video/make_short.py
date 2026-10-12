"""YouTubeショート向け縦長版（1080x1920・60秒以内）を生成するスクリプト。

本編（make_video.py）の要点だけを短くまとめたもの。
使い方: python3 make_short.py
出力: kaisetsu_zaimoku_short.mp4
"""
import os
import subprocess
import tempfile
import wave

import numpy as np
import pyopenjtalk
from PIL import Image, ImageDraw

from make_video import ACCENT, BG, INK, WOOD, WOOD_EDGE, board, font, wrap

W, H = 1080, 1920
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "kaisetsu_zaimoku_short.mp4")
DARK = (70, 50, 35)
# ショートの再生UI（右側のボタン・下部の説明欄）に被らない範囲
SAFE_L, SAFE_R = 60, 900
SUB_Y = 1230


def base(title, step=None):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 300], fill=DARK)
    d.text((SAFE_L, 70), "大工用語 第３弾‼", font=font(44), fill=(255, 210, 160))
    d.text((SAFE_L, 150), title, font=font(84), fill="white")
    if step:
        d.text((SAFE_R - 60, 80), step, font=font(40), fill=(255, 235, 210))
    return img, d


def subtitle(img, text):
    d = ImageDraw.Draw(img)
    f = font(50)
    lines = wrap(text, f, SAFE_R - SAFE_L - 40, d)
    h = 40 + 72 * len(lines)
    d.rounded_rectangle([SAFE_L - 20, SUB_Y, SAFE_R + 20, SUB_Y + h], 24, fill=(30, 30, 30))
    for i, line in enumerate(lines):
        d.text((SAFE_L + 10, SUB_Y + 22 + 72 * i), line, font=f, fill="white")


def centered(d, y, text, size, fill):
    f = font(size)
    tw = d.textlength(text, font=f)
    d.text(((SAFE_L + SAFE_R - tw) / 2, y), text, font=f, fill=fill)


def s_hook():
    img = Image.new("RGB", (W, H), DARK)
    d = ImageDraw.Draw(img)
    centered(d, 200, "見た目は同じなのに", 72, "white")
    centered(d, 310, "名前がちがう⁉", 110, (255, 210, 160))
    for i, (n, w, h) in enumerate([("桟木", 300, 50), ("垂木", 150, 150), ("胴縁", 300, 50)]):
        y = 560 + i * 210
        board(d, SAFE_L + 60, y + (150 - h) // 2, w, h)
        d.text((SAFE_L + 460, y + 40), n, font=font(80), fill="white")
    return img


def s_sangi():
    img, d = base("桟木（さんぎ）", "1/3")
    centered(d, 380, "屋根の下地", 80, ACCENT)
    board(d, SAFE_L + 20, 560, SAFE_R - SAFE_L - 40, 60)
    centered(d, 660, "薄くて長～い板", 56, INK)
    centered(d, 800, "厚み15ミリ程度以上", 56, INK)
    centered(d, 890, "長さ４メートルほど", 56, INK)
    return img


def s_taruki():
    img, d = base("垂木（たるき）", "2/3")
    centered(d, 380, "構造材", 80, ACCENT)
    board(d, (SAFE_L + SAFE_R) // 2 - 130, 520, 260, 260)
    centered(d, 840, "タテヨコ45ミリ以上", 56, INK)
    centered(d, 930, "四角くて重い・ガッチリ", 56, INK)
    return img


def s_dobuchi():
    img, d = base("胴縁（どうぶち）", "3/3")
    centered(d, 360, "壁の下地", 80, ACCENT)
    x0, y0 = SAFE_L + 120, 500
    for k in range(3):
        d.rectangle([x0 + k * 260, y0, x0 + k * 260 + 40, y0 + 400], fill=(200, 200, 200), outline=INK, width=2)
    for k in range(4):
        y = y0 + 40 + k * 100
        d.rectangle([x0 - 40, y, x0 + 600, y + 28], fill=WOOD, outline=WOOD_EDGE, width=3)
    centered(d, 950, "柱と柱をつなぐ／釘・ビスが打てる", 46, INK)
    centered(d, 1030, "長さ２メートルが多い", 46, INK)
    return img


def s_diff():
    img, d = base("見分け方")
    rows = [("薄い", "桟木", 300, 50), ("四角で重い", "垂木", 150, 150), ("壁の下地", "胴縁", 300, 50)]
    for i, (k, n, w, h) in enumerate(rows):
        y = 360 + i * 270
        board(d, SAFE_L + 20, y + (150 - h) // 2, w, h)
        d.text((SAFE_L + 380, y + 10), k + "のが", font=font(48), fill=INK)
        d.text((SAFE_L + 380, y + 75), n, font=font(80), fill=ACCENT)
    return img


def s_caution():
    img, d = base("現場では…")
    d.rounded_rectangle([SAFE_L, 400, SAFE_R, 820], 30, fill="white", outline=ACCENT, width=6)
    centered(d, 450, "呼び方を間違えると", 60, INK)
    centered(d, 540, "材料屋さんが", 60, INK)
    centered(d, 630, "別の材料を用意することも！", 56, ACCENT)
    centered(d, 900, "名前はすごく大事!(^^)!", 64, INK)
    return img


def s_end():
    img = Image.new("RGB", (W, H), DARK)
    d = ImageDraw.Draw(img)
    centered(d, 330, "これで", 72, "white")
    centered(d, 440, "“わけわかめ”", 110, (255, 210, 160))
    centered(d, 590, "も解消!(^^)!", 72, "white")
    centered(d, 820, "くわしくはブログで", 52, "white")
    centered(d, 900, "「LifeとWorkをカンタンに！」", 48, (255, 235, 210))
    return img


# (描画関数, 字幕, 読み上げ用テキスト)
SCENES = [
    (s_hook, "見た目はそっくりなのに名前がちがう木材、知ってますか？ 桟木・垂木・胴縁！",
     "見た目はそっくりなのに、名前がちがう木材、知ってますか？さんぎ、たるき、どうぶち！"),
    (s_sangi, "桟木は屋根の下地。厚み15ミリ程度以上の、薄くて長～い板です。",
     "さんぎは、屋根の下地。厚み15ミリ程度以上の、薄くて、なが～い板です。"),
    (s_taruki, "垂木は構造材。タテヨコ45ミリ以上の、四角くて重いガッチリした材料です。",
     "たるきは、構造材。たてよこ45ミリ以上の、四角くて重い、ガッチリした材料です。"),
    (s_dobuchi, "胴縁は壁の下地。柱と柱をつないで壁を強くし、釘やビスが打ち込めます。",
     "どうぶちは、壁の下地。柱と柱をつないで壁を強くし、くぎやビスが打ち込めます。"),
    (s_diff, "薄いのが桟木、四角で重いのが垂木、壁の下地が胴縁！",
     "薄いのが、さんぎ。四角で重いのが、たるき。壁の下地が、どうぶち！"),
    (s_caution, "現場では呼び方で材料屋さんが間違えることも。名前はすごく大事なんです。",
     "現場では、呼び方で材料屋さんが間違えることも。名前はすごく大事なんです。"),
    (s_end, "これで「わけわかめ」も解消！ くわしくはりゅう坊のブログで!(^^)!",
     "これで、わけわかめも解消！くわしくは、りゅうぼうのブログで！"),
]


def main():
    tmp = tempfile.mkdtemp()
    segs = []
    for i, (fn, text, speech) in enumerate(SCENES):
        audio, sr = pyopenjtalk.tts(speech, speed=1.15)
        pad = np.zeros(int(sr * 0.3))
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
