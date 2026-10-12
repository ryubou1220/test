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
        # 句読点・閉じ括弧で行が始まらないよう、はみ出しても前の行に付ける
        if draw.textlength(cur + ch, font=f) > width and ch not in "、。！？」）!?)":
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
    img = Image.new("RGB", (W, H), (70, 50, 35))
    d = ImageDraw.Draw(img)
    d.text((80, 110), "【大工用語 第３弾‼】", font=font(48), fill=(255, 210, 160))
    d.text((80, 190), "同じ木材でも呼び方いろいろ⁉", font=font(64), fill="white")
    d.text((80, 290), "桟木・垂木・胴縁のちがいを解説", font=font(44), fill=(255, 235, 210))
    for i, (w, h) in enumerate([(160, 30), (90, 90), (160, 30)]):
        board(d, 120 + i * 260, 410 + (90 - h) // 2, w, h)
    for i, n in enumerate(["桟木", "垂木", "胴縁"]):
        d.text((150 + i * 260, 520), n, font=font(36), fill="white")
    return img


def s_shadow():
    img, d = base("どれも家を支える「影の主役」")
    for i, (h, b) in enumerate([("構造材", "骨組みとして使う"), ("下地材", "支えになる土台として使う")]):
        x = 100 + i * 560
        d.rounded_rectangle([x, 140, x + 500, 290], 20, fill="white", outline=ACCENT, width=4)
        d.text((x + 30, 160), h, font=font(44), fill=ACCENT)
        d.text((x + 30, 225), b, font=font(32), fill=INK)
    d.text((100, 350), "表に出ない“脇役”だけど…", font=font(40), fill=INK)
    d.text((100, 420), "一軒の家にとっては重要な骨組み ＝ 影の主役!(^^)!", font=font(40), fill=ACCENT)
    return img


def s_ryubou():
    img, d = base("りゅう坊のお仕事では…")
    rows = [("桟木", "よく使う", ACCENT), ("胴縁", "よく使う", ACCENT), ("垂木", "ほとんど使わない", (130, 120, 110))]
    for i, (n, t, c) in enumerate(rows):
        y = 140 + i * 100
        d.text((120, y), n, font=font(44), fill=INK)
        d.rounded_rectangle([300, y - 5, 300 + d.textlength(t, font=font(36)) + 40, y + 55], 15, fill=c)
        d.text((320, y + 4), t, font=font(36), fill="white")
    d.rounded_rectangle([760, 170, 1200, 330], 30, fill="white", outline=INK, width=3)
    d.polygon([(800, 330), (780, 380), (850, 330)], fill="white", outline=INK)
    d.line([(803, 329), (847, 329)], fill="white", width=4)
    d.text((790, 200), "ちょ、ちょっと待って！", font=font(32), fill=INK)
    d.text((790, 255), "なんのこっちゃぁ～⁉", font=font(34), fill=ACCENT)
    return img


def s_sangi():
    img, d = base("① 桟木（さんぎ）")
    d.text((120, 140), "おもに「屋根の下地」に使う", font=font(40), fill=ACCENT)
    board(d, 120, 240, 1040, 40, "長～い板（長さ４メートルほど）")
    specs = [("厚み", "15ミリ程度以上"), ("幅", "30ミリ以上"), ("長さ", "４メートルほど")]
    for i, (k, v) in enumerate(specs):
        x = 120 + i * 350
        d.text((x, 380), k, font=font(30), fill=(130, 120, 110))
        d.text((x, 425), v, font=font(38), fill=INK)
    return img


def s_taruki():
    img, d = base("② 垂木（たるき）")
    d.text((120, 140), "構造材として使う、厚めの角材", font=font(40), fill=ACCENT)
    board(d, 140, 230, 150, 150, "タテヨコ45ミリ以上が多い")
    for i, t in enumerate(["長さは４メートルのものが多い", "見た目も実際も「重い」", "ガッチリした材料"]):
        d.text((480, 240 + i * 60), "・" + t, font=font(36), fill=INK)
    return img


def s_diff():
    img, d = base("見分け方はカンタン！")
    board(d, 140, 230, 380, 40)
    board(d, 820, 175, 150, 150)
    d.text((170, 360), "薄いのが", font=font(40), fill=INK)
    d.text((170, 415), "桟木", font=font(64), fill=ACCENT)
    d.text((740, 360), "四角で重いのが", font=font(40), fill=INK)
    d.text((740, 415), "垂木", font=font(64), fill=ACCENT)
    return img


def s_dobuchi():
    img, d = base("③ 胴縁（どうぶち）")
    d.text((80, 130), "「壁の下地材」に使う", font=font(40), fill=ACCENT)
    for i, t in enumerate(["壁自体の強度がアップ", "柱と柱をつなぐ役目", "釘やビスが打ち込める", "厚み15ミリ程度以上・長さ２mが多い"]):
        d.text((80, 205 + i * 58), "・" + t, font=font(30), fill=INK)
    x0, y0 = 760, 130
    for k in range(3):
        d.rectangle([x0 + k * 180, y0, x0 + k * 180 + 30, y0 + 300], fill=(200, 200, 200), outline=INK)
    for k in range(4):
        y = y0 + 30 + k * 75
        d.rectangle([x0 - 20, y, x0 + 420, y + 18], fill=WOOD, outline=WOOD_EDGE, width=2)
    d.text((x0, y0 + 310), "↑ 柱", font=font(26), fill=INK)
    d.text((x0 + 230, y0 + 310), "↑ 胴縁", font=font(26), fill=ACCENT)
    d.text((80, 470), "土木工事の現場では「丁張（ちょうはり）材」にも！", font=font(32), fill=INK)
    return img


def s_compare():
    img, d = base("まとめて比較")
    cols = ["名前", "使う場所", "厚み・形", "長さ"]
    rows = [("桟木", "屋根の下地", "薄い（15mm程度〜）", "約４m"),
            ("垂木", "構造材", "四角で重い（45mm〜）", "約４m"),
            ("胴縁", "壁の下地", "15mm程度〜", "約２m")]
    xs = [120, 280, 540, 960]
    y = 140
    d.rectangle([100, y, W - 100, y + 70], fill=ACCENT)
    for x, c in zip(xs, cols):
        d.text((x, y + 15), c, font=font(34), fill="white")
    for i, r in enumerate(rows):
        yy = y + 70 + i * 90
        d.rectangle([100, yy, W - 100, yy + 90], fill="white" if i % 2 == 0 else (245, 235, 220), outline=(220, 200, 180))
        for x, c in zip(xs, r):
            d.text((x, yy + 25), c, font=font(34), fill=INK)
    d.text((120, 520), "※寸法・長さは「多いもの」の目安です", font=font(26), fill=(130, 120, 110))
    return img


def s_material():
    img, d = base("材料と、現場での注意")
    d.text((100, 140), "建物の大事な材料なので…", font=font(36), fill=INK)
    for i, t in enumerate(["スギ", "ヒノキ", "松"]):
        x = 100 + i * 230
        d.rounded_rectangle([x, 200, x + 200, 280], 20, fill=WOOD, outline=WOOD_EDGE, width=3)
        tw = d.textlength(t, font=font(40))
        d.text((x + (200 - tw) / 2, 217), t, font=font(40), fill=INK)
    d.text((100, 300), "ほとんどが程度のいい木で作られています!(^^)!", font=font(32), fill=INK)
    d.rounded_rectangle([100, 380, W - 100, 520], 20, fill="white", outline=ACCENT, width=4)
    d.text((130, 400), "！ 呼び方を間違えると、材料屋さんが", font=font(34), fill=ACCENT)
    d.text((130, 455), "　 別の材料を用意してしまうことも！", font=font(34), fill=ACCENT)
    return img


def s_end():
    img = Image.new("RGB", (W, H), (70, 50, 35))
    d = ImageDraw.Draw(img)
    d.text((120, 170), "薄いのが桟木、四角で重いのが垂木、", font=font(48), fill="white")
    d.text((120, 250), "壁の下地が胴縁！", font=font(48), fill="white")
    d.text((120, 340), "これで“わけわかめ”も解消!(^^)!", font=font(52), fill=(255, 210, 160))
    d.text((120, 450), "ブログ「LifeとWorkをカンタンに！」", font=font(34), fill="white")
    d.text((120, 500), "ameblo.jp/11830ryubou315", font=font(30), fill=(255, 235, 210))
    return img


# (描画関数, 字幕, 読み上げ用テキスト)。用語は読み間違い防止のため読み上げ側をかなにしている
SCENES = [
    (s_title,
     "りゅう坊です！大工用語、第３弾‼ 今回は、木造のお家に使うたくさんの木の材料の中から、桟木と垂木、加えて胴縁についてお送りします。",
     "りゅうぼうです！だいくようご、だいさんだん！こんかいは、木造のおうちに使う、たくさんの木の材料の中から、さんぎと、たるき、くわえて、どうぶちについてお送りします。"),
    (s_shadow,
     "どれも骨組みとしての構造材や、支えになる下地材として使われることがほとんど。表に出ない脇役ですが、一軒の家にとっては重要な骨組みとなる、影の主役なんです。",
     "どれも、骨組みとしての構造材や、支えになる下地材として使われることがほとんどです。表に出ない脇役ではありますが、一軒の家にとっては重要な骨組みとなる、影の主役なんです。"),
    (s_ryubou,
     "ボク自身、仕事では垂木はほとんど使いませんが、桟木や胴縁はよく使う機会があります。「ちょ、ちょっと待って！なんのこっちゃぁ～⁉」という声がしそうなので、カンタンに説明しますね。",
     "ボク自身、仕事では、たるきはほとんど使いませんが、さんぎや、どうぶちは、よく使う機会があります。ちょ、ちょっと待って、なんのこっちゃー、という声がしそうなので、カンタンに説明しますね。"),
    (s_sangi,
     "まずは桟木。おもに屋根の下地に使われます。イメージは、厚みが15ミリ程度以上、幅が30ミリ以上で、長さが４メートルほどある長～い板です。",
     "まずは、さんぎ。おもに屋根の下地に使われます。イメージは、厚みが15ミリ程度以上、幅が30ミリ以上で、長さが4メートルほどある、なが～い板です。"),
    (s_taruki,
     "次に垂木。構造材として使うので、桟木に比べると厚めです。タテヨコ45ミリ以上のものが多く、長さも４メートルのものが多いです。見た目も実際も重い、ガッチリした材料です。",
     "次に、たるき。構造材として使うので、さんぎに比べると厚めです。たてよこ45ミリ以上のものが多く、長さも4メートルのものが多いです。見た目も実際も重い、ガッチリした材料です。"),
    (s_diff,
     "見分け方はカンタン。薄いのが桟木、四角で重いのが垂木。こんなふうに見ればOKです！",
     "見分け方はカンタン。薄いのが、さんぎ。四角で重いのが、たるき。こんなふうに見ればオーケーです！"),
    (s_dobuchi,
     "もうひとつ、胴縁は壁の下地材。壁の強度をアップし、柱と柱をつなぐ役目もあります。下地材なので釘やビスが打ち込めます。厚みは15ミリ程度以上、長さは２メートルのものが多く、土木工事の現場では丁張材としても使います。",
     "もうひとつ、どうぶちは、壁の下地材です。壁の強度をアップし、柱と柱をつなぐ役目もあります。下地材なので、くぎやビスが打ち込めます。厚みは15ミリ程度以上、長さは2メートルのものが多く、土木工事の現場では、ちょうはり材としても使います。"),
    (s_compare,
     "まとめると、桟木は屋根の下地で薄い板、垂木は四角で重い構造材、胴縁は壁の下地。長さは桟木と垂木が４メートル、胴縁が２メートルのものが多いです。",
     "まとめると、さんぎは屋根の下地で薄い板。たるきは四角で重い構造材。どうぶちは壁の下地。長さは、さんぎと、たるきが4メートル、どうぶちが2メートルのものが多いです。"),
    (s_material,
     "建物の大事な材料なので、ほとんどが程度のいいスギ・ヒノキ・松で作られています。はた目にはどれも同じようですが、現場では呼び方で材料屋さんが間違えることもあるので、名前はすごく大事なんです。",
     "建物の大事な材料なので、ほとんどが程度のいい、スギ、ヒノキ、松で作られています。はた目にはどれも同じようですが、現場では呼び方によって材料屋さんが間違えることもあるので、名前はすごく大事なんです。"),
    (s_end,
     "これで「わけわかめ」も解消されるのではないかと！以上、りゅう坊でした。ご視聴ありがとうございました!(^^)!",
     "これで、わけわかめも、解消されるのではないかと！以上、りゅうぼうでした。ご視聴ありがとうございました！"),
]


def main():
    tmp = tempfile.mkdtemp()
    segs = []
    for i, (fn, text, speech) in enumerate(SCENES):
        audio, sr = pyopenjtalk.tts(speech, speed=1.05)
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
