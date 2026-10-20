#!/usr/bin/env python3
"""記事「時間はコントロールできない」を字幕スライド動画 (1920x1080) にする。

使い方: python3 video/make_video.py
出力:   video/out/time_management.mp4 と video/out/time_management.srt
必要:   Pillow, ffmpeg, IPAゴシック (fonts-ipafont-gothic)
"""
import math
import os
import shutil
import subprocess
import wave
import struct

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
WORK = os.path.join(OUT, "frames")
W, H = 1920, 1080
FPS = 30
FADE = 0.5
FONT = "/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf"

BG = (18, 24, 44)
FG = (240, 240, 245)
SUB = (170, 180, 205)
ACCENT = (255, 190, 80)

# (種類, 見出し, 本文行リスト)
SCENES = [
    ("title", "時間はコントロールできない", ["ムダを減らして、効果的に使う", "時間管理のヒント"]),
    ("text", "", ["時間は、自分の都合で", "止めることはできません。", "", "何をしていようが、流れていく。", "いささか無情なのです (´;ω;｀)"]),
    ("text", "", ["ならば――", "", "ムダを減らし、効果的に使えれば", "過ぎた時間を後悔しなくて済む。"]),
    ("text", "「時間が足りない！」と言うあなたへ", ["時間は、みんなに平等。", "何をしても、しなくても流れていく。", "", "“足りない”のではなく、", "うまく使えていないのかもしれません。"]),
    ("title", "誰でもできる", ["時間を有効活用する", "HOW TO 8選"]),
    ("tip", "1. 朝のルーティンを確立する", ["決まった時間に起きる", "ストレッチや瞑想、健康的な朝食", "→ 良い一日のスタートを切る"]),
    ("tip", "2. 優先順位を明確にする", ["前日に翌日のタスクリストを作る", "最も重要なタスクから始める", "→ 大事なことに集中できる"]),
    ("tip", "3. デジタルデトックス", ["スマホ・SNSの時間を制限する", "特定の時間帯は画面から離れる", "→ 読書や家族との時間に充てる"]),
    ("tip", "4. 隙間時間の活用", ["通勤時間や待ち時間に", "オーディオブック・ポッドキャスト", "簡単なストレッチも◎"]),
    ("tip", "5. 断捨離を行う", ["不要な物と雑念を取り除く", "定期的に持ち物を見直す", "→ 生活がシンプルになり時間が浮く"]),
    ("tip", "6. 休憩を計画的に取る", ["長時間続けると集中力は落ちる", "ポモドーロ・テクニック", "25分作業 → 5分休憩"]),
    ("tip", "7. 健康的な生活習慣を維持する", ["十分な睡眠", "バランスの取れた食事・適度な運動", "→ エネルギーと集中力の基盤"]),
    ("tip", "8. 「No」を言う練習", ["やりたくないこと・余計なタスクには", "「No」と言う", "→ 自分の時間とエネルギーを守る"]),
    ("text", "だらだら過ごすのもアリ。でも…", ["きちきち計画して苦痛になるのは本末転倒。", "", "それでも、ある程度は", "やることを決めたほうが得策です。"]),
    ("text", "", ["ときにはボーっと過ごすのも", "大切なリフレッシュ。", "", "たった一度の人生。", "有効に使えたほうが、きっといい。"]),
    ("title", "時間は、命そのもの", ["この認識を持つと", "時間との向き合い方が変わる"]),
    ("end", "時間は命、そして有限です。", ["最後までご覧いただき", "ありがとうございました"]),
]


def font(size):
    return ImageFont.truetype(FONT, size)


def duration(scene):
    _, head, lines = scene
    chars = len(head) + sum(len(l) for l in lines)
    return round(max(4.0, 2.0 + chars / 7.0), 1)


def centered(draw, y, text, f, fill):
    w = draw.textlength(text, font=f)
    draw.text(((W - w) / 2, y), text, font=f, fill=fill)


def draw_clock(draw, cx, cy, r, minute, width=6, color=SUB, hand=ACCENT):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=color, width=width)
    for i in range(12):
        a = math.radians(i * 30)
        r1 = r * (0.82 if i % 3 else 0.72)
        draw.line([cx + r1 * math.sin(a), cy - r1 * math.cos(a),
                   cx + r * 0.92 * math.sin(a), cy - r * 0.92 * math.cos(a)], fill=color, width=width // 2 + 1)
    hour = (minute / 60.0) * 30 + 300
    for ang, ln, wd in ((hour, 0.5, width + 2), (minute * 6, 0.75, width)):
        a = math.radians(ang)
        draw.line([cx, cy, cx + r * ln * math.sin(a), cy - r * ln * math.cos(a)], fill=hand, width=wd)
    draw.ellipse([cx - width, cy - width, cx + width, cy + width], fill=hand)


def render(i, scene, total):
    kind, head, lines = scene
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    # 背景の大きな時計 (シーンごとに針が進む)
    draw_clock(d, W - 190, H - 200, 140, minute=i * 7, width=4, color=(36, 46, 76), hand=(60, 70, 105))
    # 進行バー
    d.rectangle([0, H - 12, W, H], fill=(35, 45, 75))
    d.rectangle([0, H - 12, int(W * (i + 1) / total), H], fill=ACCENT)

    if kind in ("title", "end"):
        draw_clock(d, W // 2, 300, 110, minute=i * 7)
        centered(d, 470, head, font(110 if len(head) <= 12 else 88), FG)
        y = 650
        for ln in lines:
            centered(d, y, ln, font(60), SUB)
            y += 90
    elif kind == "tip":
        num, title = head.split(". ", 1)
        d.ellipse([160, 170, 360, 370], fill=ACCENT)
        centered_x = 260 - d.textlength(num, font=font(130)) / 2
        d.text((centered_x, 200), num, font=font(130), fill=BG)
        d.text((420, 215), title, font=font(96), fill=FG)
        d.line([420, 350, W - 160, 350], fill=ACCENT, width=4)
        y = 460
        for ln in lines:
            hl = ln.startswith("→")
            d.text((440, y), ln, font=font(68), fill=ACCENT if hl else FG)
            y += 120
    else:
        body = [l for l in lines]
        n = len(body) + (2 if head else 0)
        y = (H - n * 100) / 2
        if head:
            centered(d, y, head, font(80), ACCENT)
            y += 200
        for ln in body:
            if ln:
                centered(d, y, ln, font(68), FG)
            y += 100
    path = os.path.join(WORK, f"s{i:02d}.png")
    img.save(path)
    return path


def bgm(path, seconds):
    """やわらかいパッド和音 + 1秒ごとの小さな時計の音。"""
    rate = 44100
    chords = [(220.0, 277.18, 329.63), (196.0, 246.94, 293.66),
              (174.61, 220.0, 261.63), (196.0, 246.94, 311.13)]
    n = int(seconds * rate)
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        buf = bytearray()
        for k in range(n):
            t = k / rate
            ch = chords[int(t // 8) % len(chords)]
            pos = (t % 8) / 8
            env = min(1.0, pos * 4, (1 - pos) * 4)
            s = sum(math.sin(2 * math.pi * f * t) for f in ch) / 3 * 0.10 * env
            tick = t % 1.0
            if tick < 0.012:
                s += math.sin(2 * math.pi * 2000 * t) * 0.05 * (1 - tick / 0.012)
            fade = min(1.0, t / 2, (seconds - t) / 3)
            buf += struct.pack("<h", int(max(-1, min(1, s * fade)) * 32767))
        w.writeframes(bytes(buf))


def srt_time(t):
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def main():
    os.makedirs(WORK, exist_ok=True)
    total = len(SCENES)
    clips, srt, t = [], [], 0.0
    for i, sc in enumerate(SCENES):
        png = render(i, sc, total)
        dur = duration(sc)
        clip = os.path.join(WORK, f"c{i:02d}.mp4")
        vf = (f"zoompan=z='1+0.02*on/({dur}*{FPS})':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
              f":d={int(dur * FPS)}:s={W}x{H}:fps={FPS},"
              f"fade=t=in:st=0:d={FADE},fade=t=out:st={dur - FADE}:d={FADE},format=yuv420p")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-i", png,
                        "-t", str(dur), "-vf", vf, "-c:v", "libx264", "-preset", "medium",
                        "-crf", "20", clip], check=True)
        clips.append(clip)
        text = "\n".join(x for x in ([sc[1]] + sc[2]) if x)
        srt.append(f"{i + 1}\n{srt_time(t)} --> {srt_time(t + dur)}\n{text}\n")
        t += dur

    lst = os.path.join(WORK, "list.txt")
    with open(lst, "w") as f:
        f.writelines(f"file '{c}'\n" for c in clips)
    music = os.path.join(WORK, "bgm.wav")
    bgm(music, t)
    out = os.path.join(OUT, "time_management.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst,
                    "-i", music, "-c:v", "copy", "-c:a", "aac", "-b:a", "128k", "-shortest",
                    "-movflags", "+faststart", out], check=True)
    with open(os.path.join(OUT, "time_management.srt"), "w") as f:
        f.write("\n".join(srt))
    shutil.copy(os.path.join(WORK, "s00.png"), os.path.join(OUT, "thumbnail.png"))
    shutil.rmtree(WORK)
    print(f"{out}  ({t:.1f}秒)")


if __name__ == "__main__":
    main()
