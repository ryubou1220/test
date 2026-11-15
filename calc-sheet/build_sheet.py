"""ウッドデッキ 材料・費用の自動計算シート（Excel）を作る。

  python3 calc-sheet/build_sheet.py

考え方はマニュアルのとおり：サンドイッチ工法、根太2段（下段＝縦方向、上段＝横方向）、
天板は奥行き方向に張る（縦張り）、目地10mm。
"""
import pathlib
from openpyxl import Workbook
from openpyxl.comments import Comment
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.worksheet.datavalidation import DataValidation

OUT = pathlib.Path(__file__).resolve().parent / "ウッドデッキ材料費計算シート.xlsx"
FONT = "Yu Gothic"
YELLOW = PatternFill("solid", fgColor="FFF2B3")
GRAY = PatternFill("solid", fgColor="EEEEEE")
GREEN = PatternFill("solid", fgColor="E3EEE7")
HEAD = PatternFill("solid", fgColor="2C6849")
thin = Side(style="thin", color="BBBBBB")
BOX = Border(left=thin, right=thin, top=thin, bottom=thin)
YEN = '#,##0"円";-#,##0"円";"-"'
MM = '#,##0" mm"'
NUM = '#,##0'

wb = Workbook()
ws = wb.active
ws.title = "計算"
pr = wb.create_sheet("単価")


def f(cell, size=11, bold=False, color="000000"):
    cell.font = Font(name=FONT, size=size, bold=bold, color=color)


def row(ws_, r, label, value, unit="", fill=None, fmt=None, note=None, inp=False):
    a, b, c = ws_.cell(r, 1, label), ws_.cell(r, 2, value), ws_.cell(r, 3, unit)
    for x in (a, b, c):
        f(x)
        x.border = BOX
    if inp:
        b.font = Font(name=FONT, size=11, bold=True, color="0000FF")
    if fill:
        b.fill = fill
    if fmt:
        b.number_format = fmt
    b.alignment = Alignment(horizontal="right")
    if note:
        b.comment = Comment(note, "監修 野村")
    return b


def section(ws_, r, text):
    c = ws_.cell(r, 1, text)
    f(c, 12, True, "FFFFFF")
    for col in range(1, 4 if ws_ is not ws else 7):
        ws_.cell(r, col).fill = HEAD


# ---------- 単価シート ----------
f(pr.cell(1, 1, "単価表"), 14, True)
f(pr.cell(2, 1, "黄色のセルを、買うお店の今の値段に書き換えてください。最初の数字は、マニュアルに載っている2020年の例です。"), 10, color="9A3B22")
section(pr, 4, "材料と単価")
prices = [
    ("束石（羽子板付き H150）", 600, "円／個"),
    ("支柱材（4×4材）", 1470, "円／本"),
    ("上段の根太材（2×6材・長い材）", 3480, "円／本"),
    ("下段の根太材（2×6材）", 1320, "円／本"),
    ("天板材（2×6材）", 1320, "円／本"),
    ("ビス（ステンレス75mm・200本入）", 1750, "円／箱"),
    ("塗料（浸透性・水性 3.4L）", 6810, "円／缶"),
    ("基礎材（セメント・砂・砕石）", 310, "円／束石1個あたり"),
]
P = {}
for i, (name, val, unit) in enumerate(prices):
    r = 5 + i
    P[name] = f"単価!$B${r}"
    row(pr, r, name, val, unit, YELLOW, YEN, inp=True)
pr.cell(12, 2).comment = Comment("2020年の例：セメント・砂・砕石 一式3,700円 ÷ 束石12個 ≒ 310円", "監修 野村")
section(pr, 15, "材料の長さ（お店で売っている長さ）")
lengths = [
    ("支柱材の長さ", 1200, "支柱を何本とるかの元の長さ"),
    ("上段の根太材の長さ", 3650, "デッキの幅方向に使う長い材"),
    ("下段の根太材の長さ", 1820, "デッキの奥行き方向に使う材"),
    ("天板材の長さ", 1820, "デッキの奥行き方向に張る"),
]
L = {}
for i, (name, val, note) in enumerate(lengths):
    r = 16 + i
    L[name] = f"単価!$B${r}"
    row(pr, r, name, val, note, YELLOW, MM, inp=True)
pr.column_dimensions["A"].width = 36
pr.column_dimensions["B"].width = 14
pr.column_dimensions["C"].width = 34

# ---------- 計算シート ----------
f(ws.cell(1, 1, "ウッドデッキ 材料・費用の自動計算シート"), 16, True)
f(ws.cell(2, 1, "黄色のセルに、つくりたいデッキの大きさを入れるだけ。材料の数と費用が自動で出ます。値段は「単価」シートで変えられます。"), 10)
f(ws.cell(3, 1, "オリジナルウッドデッキ 日曜大工プログラム　監修：野村 隆一"), 9, color="6B756D")

section(ws, 5, "1. デッキの大きさを入れる")
W = row(ws, 6, "幅（建物に沿った長さ）", 3600, "mm　例：3600", YELLOW, MM, inp=True).coordinate
D = row(ws, 7, "奥行き（建物から外へ）", 1800, "mm　例：1800", YELLOW, MM, inp=True).coordinate
H = row(ws, 8, "高さ（地面から天板の上まで）", 500, "mm　例：500", YELLOW, MM, inp=True).coordinate
SP = row(ws, 9, "束石の間隔（最大）", 1200, "mm　1,200前後がめやす", YELLOW, MM, inp=True).coordinate
SPARE = row(ws, 10, "天板の予備", 1, "本　反り・割れに備えて", YELLOW, NUM, inp=True).coordinate
dv = DataValidation(type="whole", operator="between", formula1="1", formula2="20000",
                    showErrorMessage=True, error="1以上の整数を入れてください")
ws.add_data_validation(dv)
dv.add("B6:B9")

section(ws, 12, "2. 決まっている寸法（マニュアルのとおり）")
TW = row(ws, 13, "天板の幅", 140, "mm（2×6材）", GRAY, MM).coordinate
TT = row(ws, 14, "天板の厚み", 38, "mm", GRAY, MM).coordinate
GAP = row(ws, 15, "目地（すき間）", 10, "mm", GRAY, MM).coordinate
JH = row(ws, 16, "根太の高さ（1段）", 140, "mm（2×6材を縦に）×2段", GRAY, MM).coordinate
SE = row(ws, 17, "束石が地面から出る高さ", 100, "mm（H150を50mm埋める）", GRAY, MM).coordinate
OFF = row(ws, 18, "デッキの端から束石の中心まで", 83, "mm（根太38＋支柱の半分44.5）", GRAY, MM).coordinate
SH = row(ws, 19, "支柱を短くする分", 10, "mm（天板に当てない）", GRAY, MM).coordinate
KERF = row(ws, 20, "のこぎりの刃の厚み", 3, "mm", GRAY, MM).coordinate
PAINTX = row(ws, 21, "塗る面積の倍率", 3, "倍（デッキの面積に対して）", GRAY, '0.0"倍"',
             note="1回目は組む前に全部の材料の全面を塗るので、デッキの面積の3倍ほどを目安にしています。").coordinate
PAINTL = row(ws, 22, "塗料1Lで塗れる面積（2回塗り）", 5, "㎡（3.4Lで約17㎡）", GRAY, '0.0"㎡"').coordinate
SCREWJ = row(ws, 23, "骨組みのビス（1か所あたり）", 4, "本（最低3本、理想は4本）", GRAY, NUM).coordinate
SCREWT = row(ws, 24, "天板のビス（根太1本あたり）", 2, "本", GRAY, NUM).coordinate

section(ws, 26, "3. 計算の途中（さわらなくて大丈夫）")
LX = row(ws, 27, "束石の中心から中心まで（横）", f"={W}-2*{OFF}", "mm", None, MM).coordinate
LY = row(ws, 28, "束石の中心から中心まで（縦）", f"={D}-2*{OFF}", "mm", None, MM).coordinate
NC = row(ws, 29, "束石の数（横に並ぶ数）", f"=ROUNDUP({LX}/{SP},0)+1", "個", None, NUM).coordinate
NR = row(ws, 30, "束石の数（縦に並ぶ列）", f"=ROUNDUP({LY}/{SP},0)+1", "列", None, NUM).coordinate
row(ws, 31, "束石の間隔（横）", f"={LX}/({NC}-1)", "mm", None, MM)
row(ws, 32, "束石の間隔（縦）", f"={LY}/({NR}-1)", "mm", None, MM)
POST = row(ws, 33, "支柱の長さ（平らな地面の場合）", f"={H}-{TT}-{SE}-{SH}", "mm", None, MM,
           note="支柱＝根太2段分＋残り−10mm。地面が傾いているときは、丁張りの下がり寸法で束石ごとに測ります。").coordinate
NT = row(ws, 34, "天板の枚数", f"=INT(({W}+{GAP})/({TW}+{GAP}))", "枚", None, NUM).coordinate
REST = row(ws, 35, "天板を並べた幅", f"={NT}*{TW}+({NT}-1)*{GAP}", "mm", None, MM).coordinate
row(ws, 36, "幅に足りない分", f"={W}-{REST}", "mm（大きいときは細い板を1枚足す）", None, MM)
SCREWS = row(ws, 37, "ビスの本数（1割多め）",
             f"=ROUNDUP(({NC}*{NR}*4*{SCREWJ}+{NT}*2*{NR}*{SCREWT})*1.1,0)", "本", None, NUM).coordinate
PAINT = row(ws, 38, "塗料の量", f"={W}*{D}/1000000*{PAINTX}/{PAINTL}", "L", None, '0.0" L"').coordinate
chk = row(ws, 39, "高さの確認", f'=IF({H}<{TT}+2*{JH}+{SE},"高さが足りません（この組み方では"&({TT}+2*{JH}+{SE})&"mm以上）","OK")', "", None, None)
chk.font = Font(name=FONT, size=11, bold=True, color="9A3B22")

# 材料と費用の表
section(ws, 41, "4. 材料と費用")
heads = ["材料", "使い方", "数量", "単位", "単価", "金額"]
for col, h in enumerate(heads, 1):
    c = ws.cell(42, col, h)
    f(c, 11, True)
    c.fill = GREEN
    c.border = BOX
items = [
    ("束石（羽子板付き H150）", "支柱の下の基礎", f"={NC}*{NR}", "個", P["束石（羽子板付き H150）"]),
    ("支柱材（4×4材）", f'="長さ"&TEXT({POST},"#,##0")&"mmを"&{NC}*{NR}&"本とる"',
     f"=ROUNDUP({NC}*{NR}/INT({L['支柱材の長さ']}/({POST}+{KERF})),0)", "本", P["支柱材（4×4材）"]),
    ("上段の根太材（2×6材）", f'="幅方向に"&{NR}&"列×両側"',
     f"=2*{NR}*ROUNDUP({W}/{L['上段の根太材の長さ']},0)", "本", P["上段の根太材（2×6材・長い材）"]),
    ("下段の根太材（2×6材）", f'="奥行き方向に"&{NC}&"列×両側"',
     f"=2*{NC}*ROUNDUP({D}/{L['下段の根太材の長さ']},0)", "本", P["下段の根太材（2×6材）"]),
    ("天板材（2×6材）", f'={NT}&"枚＋予備"',
     f"={NT}*ROUNDUP({D}/{L['天板材の長さ']},0)+{SPARE}", "本", P["天板材（2×6材）"]),
    ("ビス（ステンレス75mm）", f'={SCREWS}&"本"', f"=ROUNDUP({SCREWS}/200,0)", "箱", P["ビス（ステンレス75mm・200本入）"]),
    ("塗料（浸透性・水性 3.4L）", f'=TEXT({PAINT},"0.0")&"L（2回塗り）"', f"=ROUNDUP({PAINT}/3.4,0)", "缶", P["塗料（浸透性・水性 3.4L）"]),
    ("基礎材（セメント・砂・砕石）", "束石の下地", f"={NC}*{NR}", "個分", P["基礎材（セメント・砂・砕石）"]),
]
for i, (name, use, qty, unit, price) in enumerate(items):
    r = 43 + i
    vals = [name, use, qty, unit, f"={price}", f"=C{r}*E{r}"]
    for col, v in enumerate(vals, 1):
        c = ws.cell(r, col, v)
        f(c)
        c.border = BOX
        if col == 5:
            c.font = Font(name=FONT, size=11, color="008000")
    ws.cell(r, 3).number_format = NUM
    ws.cell(r, 5).number_format = YEN
    ws.cell(r, 6).number_format = YEN
last = 43 + len(items) - 1
tr = last + 1
c = ws.cell(tr, 1, "材料費の合計")
f(c, 12, True)
t = ws.cell(tr, 6, f"=SUM(F43:F{last})")
f(t, 13, True)
t.number_format = YEN
for col in range(1, 7):
    ws.cell(tr, col).fill = YELLOW
    ws.cell(tr, col).border = BOX

section(ws, tr + 2, "5. 業者に頼んだ場合とくらべる（目安）")
AREA = row(ws, tr + 3, "デッキの面積", f"={W}*{D}/1000000", "㎡", None, '0.00" ㎡"').coordinate
row(ws, tr + 4, "業者に頼んだ場合の目安", f"={AREA}*40000", "円（天然木で1㎡あたり約4万円から）", None, YEN)
row(ws, tr + 5, "そのうち施工の手間代", f"={AREA}*25000", "円（1㎡あたり約2万5千円）", None, YEN,
    note="業者価格の目安は、販売ページ・セールスレターと同じ数字です。地面の状態や運び込みの条件で変わります。")
f(ws.cell(tr + 7, 1, "※ 数量は目安です。束石の配置や根太の本数は、図面セットの数字を優先してください。"), 9, color="6B756D")
f(ws.cell(tr + 8, 1, "※ 天板は縦張り（奥行き方向）の場合です。ビスは骨組み1か所4本・天板は根太1本に2本で、1割多めにしています。"), 9, color="6B756D")
f(ws.cell(tr + 9, 1, "※ 材料が長さ1本で足りないときは、支柱の上でつなぐ前提で本数を数えています。"), 9, color="6B756D")

for col, w in zip("ABCDEF", [34, 26, 30, 8, 12, 14]):
    ws.column_dimensions[col].width = w
ws.freeze_panes = "A5"
ws.sheet_view.zoomScale = 110
wb.save(OUT)
print(OUT)
