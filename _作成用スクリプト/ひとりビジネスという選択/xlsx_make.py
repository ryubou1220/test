# 特典6 売上・経費管理表
import sys
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.formatting.rule import FormulaRule
from openpyxl.utils import get_column_letter

out = sys.argv[1]
F = "Meiryo UI"
RED = "B00000"; PINK = "FBEAEA"; GRAYF = "F2F2F2"; INPUT = "FFF9E5"
thin = Side(style="thin", color="D9D9D9"); B = Border(left=thin, right=thin, top=thin, bottom=thin)
hfont = Font(name=F, bold=True, color="FFFFFF", size=11); hfill = PatternFill("solid", fgColor=RED)
nfont = Font(name=F, size=11); bfont = Font(name=F, size=11, bold=True)
YEN = '#,##0"円";[Red]-#,##0"円";"-"'
wb = Workbook()

def header(ws, row, titles, widths):
    for i, (t, w) in enumerate(zip(titles, widths), 1):
        c = ws.cell(row=row, column=i, value=t); c.font = hfont; c.fill = hfill; c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True); c.border = B
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.row_dimensions[row].height = 24

# ---- 使い方
ws = wb.active; ws.title = "使い方"
ws.column_dimensions["A"].width = 4; ws.column_dimensions["B"].width = 92
rows = [("売上・経費管理表（特典6）", Font(name=F, size=16, bold=True, color=RED)),
        ("ひとりビジネスという選択　第7講義「お金と守り編」", Font(name=F, size=10, color="595959")),
        ("", None),
        ("■ 使い方", bfont),
        ("1. 「設定」シートに、年と、月の目標売上を入れます（黄色のセルが入力欄です）。", nfont),
        ("2. 売上があったら「売上」シートに、日付・商品名・金額を1行ずつ入れます。", nfont),
        ("3. 経費があったら「経費」シートに、日付・科目・内容・金額を1行ずつ入れます。科目は一覧から選べます。", nfont),
        ("4. 「月別集計」シートで、月ごとの売上・経費・利益と、目標の達成率が自動で計算されます。", nfont),
        ("5. 「科目別集計」シートで、何にお金を使っているかを確認できます。", nfont),
        ("", None),
        ("■ ポイント", bfont),
        ("・月末に、まとめて入力するだけで大丈夫です。領収書や明細は、データで保存しておきましょう。", nfont),
        ("・事業用の口座とカードを分けておくと、記録がぐっと楽になります。", nfont),
        ("・何が経費になるかは事業の内容によって変わります。迷ったら、税務署や税理士に確認しましょう。", nfont),
        ("・この表は記録のための補助ツールです。確定申告の書類そのものではありません。", nfont)]
for i, (t, f) in enumerate(rows, 1):
    c = ws.cell(row=i, column=2, value=t)
    if f: c.font = f
    c.alignment = Alignment(wrap_text=True, vertical="center")

# ---- 設定
st = wb.create_sheet("設定")
st.column_dimensions["A"].width = 22; st.column_dimensions["B"].width = 18
st["A1"] = "設定"; st["A1"].font = Font(name=F, size=14, bold=True, color=RED)
st["A3"] = "対象の年"; st["B3"] = 2027
st["A4"] = "月の目標売上"; st["B4"] = 50000; st["B4"].number_format = YEN
st["A6"] = "※目標は、あなたが決める目安です。"; st["A6"].font = Font(name=F, size=9, color="595959")
for r in (3, 4):
    st.cell(row=r, column=1).font = bfont; c = st.cell(row=r, column=2); c.font = nfont; c.fill = PatternFill("solid", fgColor=INPUT); c.border = B
st["A8"] = "経費の科目（一覧）"; st["A8"].font = bfont
CATS = ["通信費", "ツール・ソフト利用料", "メール配信サービス", "広告宣伝費", "外注費", "書籍・研修費", "消耗品費", "支払手数料", "旅費交通費", "その他"]
for i, k in enumerate(CATS, 9):
    st.cell(row=i, column=1, value=k).font = nfont
CAT_RANGE = f"設定!$A$9:$A${8 + len(CATS)}"

N = 300
# ---- 売上
sa = wb.create_sheet("売上")
header(sa, 1, ["日付", "月", "商品名", "販売先（ASPなど）", "金額", "メモ"], [13, 6, 34, 20, 14, 30])
for r in range(2, N + 2):
    sa.cell(row=r, column=1).number_format = "yyyy/m/d"
    sa.cell(row=r, column=2, value=f'=IF(A{r}="","",MONTH(A{r}))')
    sa.cell(row=r, column=5).number_format = YEN
    for col in range(1, 7):
        c = sa.cell(row=r, column=col); c.font = nfont; c.border = B
        if col != 2: c.fill = PatternFill("solid", fgColor=INPUT)
sa["A2"] = None
sa.freeze_panes = "A2"
# ---- 経費
ex = wb.create_sheet("経費")
header(ex, 1, ["日付", "月", "科目", "内容", "金額", "支払い方法", "メモ"], [13, 6, 22, 32, 14, 14, 24])
dv = DataValidation(type="list", formula1=f"={CAT_RANGE}", allow_blank=True); ex.add_data_validation(dv)
dv2 = DataValidation(type="list", formula1='"事業用口座,事業用カード,現金,その他"', allow_blank=True); ex.add_data_validation(dv2)
for r in range(2, N + 2):
    ex.cell(row=r, column=1).number_format = "yyyy/m/d"
    ex.cell(row=r, column=2, value=f'=IF(A{r}="","",MONTH(A{r}))')
    ex.cell(row=r, column=5).number_format = YEN
    for col in range(1, 8):
        c = ex.cell(row=r, column=col); c.font = nfont; c.border = B
        if col != 2: c.fill = PatternFill("solid", fgColor=INPUT)
dv.add(f"C2:C{N + 1}"); dv2.add(f"F2:F{N + 1}")
ex.freeze_panes = "A2"
# sample rows (例) — clearly labeled
sa["A2"] = None
# ---- 月別集計
mo = wb.create_sheet("月別集計")
mo["A1"] = "月別集計"; mo["A1"].font = Font(name=F, size=14, bold=True, color=RED)
mo["A2"] = '="対象年："&設定!B3&"年　（金額は自動計算されます）"'; mo["A2"].font = Font(name=F, size=10, color="595959")
header(mo, 4, ["月", "売上", "経費", "利益", "利益の累計", "目標", "達成率"], [8, 15, 15, 15, 15, 15, 10])
for i in range(12):
    r = 5 + i; m = i + 1
    mo.cell(row=r, column=1, value=f"{m}月")
    mo.cell(row=r, column=2, value=f"=SUMIFS(売上!$E$2:$E${N + 1},売上!$B$2:$B${N + 1},{m})")
    mo.cell(row=r, column=3, value=f"=SUMIFS(経費!$E$2:$E${N + 1},経費!$B$2:$B${N + 1},{m})")
    mo.cell(row=r, column=4, value=f"=B{r}-C{r}")
    mo.cell(row=r, column=5, value=f"=SUM($D$5:D{r})")
    mo.cell(row=r, column=6, value="=設定!$B$4")
    mo.cell(row=r, column=7, value=f'=IF(F{r}=0,"",B{r}/F{r})')
    for col in range(1, 8):
        c = mo.cell(row=r, column=col); c.font = nfont; c.border = B
        c.number_format = "0%" if col == 7 else (YEN if col > 1 else "General")
    mo.cell(row=r, column=1).fill = PatternFill("solid", fgColor=PINK); mo.cell(row=r, column=1).font = bfont
r = 17
mo.cell(row=r, column=1, value="合計")
for col, f in ((2, "=SUM(B5:B16)"), (3, "=SUM(C5:C16)"), (4, "=SUM(D5:D16)"), (6, "=SUM(F5:F16)"), (7, '=IF(F17=0,"",B17/F17)')):
    mo.cell(row=r, column=col, value=f)
for col in range(1, 8):
    c = mo.cell(row=r, column=col); c.font = bfont; c.border = B; c.fill = PatternFill("solid", fgColor=GRAYF)
    c.number_format = "0%" if col == 7 else (YEN if col > 1 else "General")
mo.conditional_formatting.add("D5:D17", FormulaRule(formula=["D5<0"], font=Font(color="C00000")))
mo["A19"] = "※売上・経費の「日付」が、設定シートの年と違う年でも、月で集計されます。年ごとにファイルを分けて使ってください。"
mo["A19"].font = Font(name=F, size=9, color="595959")
# ---- 科目別集計
ca = wb.create_sheet("科目別集計")
ca["A1"] = "科目別集計"; ca["A1"].font = Font(name=F, size=14, bold=True, color=RED)
header(ca, 3, ["科目", "年間の合計", "割合"], [24, 16, 10])
for i, k in enumerate(CATS):
    r = 4 + i
    ca.cell(row=r, column=1, value=f"=設定!A{9 + i}")
    ca.cell(row=r, column=2, value=f"=SUMIFS(経費!$E$2:$E${N + 1},経費!$C$2:$C${N + 1},A{r})")
    ca.cell(row=r, column=3, value=f'=IF($B${4 + len(CATS)}=0,"",B{r}/$B${4 + len(CATS)})')
    for col in range(1, 4):
        c = ca.cell(row=r, column=col); c.font = nfont; c.border = B; c.number_format = "0%" if col == 3 else (YEN if col == 2 else "General")
r = 4 + len(CATS)
ca.cell(row=r, column=1, value="合計"); ca.cell(row=r, column=2, value=f"=SUM(B4:B{r - 1})"); ca.cell(row=r, column=3, value=f'=IF(B{r}=0,"",1)')
for col in range(1, 4):
    c = ca.cell(row=r, column=col); c.font = bfont; c.border = B; c.fill = PatternFill("solid", fgColor=GRAYF); c.number_format = "0%" if col == 3 else (YEN if col == 2 else "General")
for s in wb.worksheets:
    s.sheet_view.showGridLines = s.title in ("売上", "経費") and False
wb.save(out)
print("saved", out)
