import sys
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.formatting.rule import FormulaRule

F="Yu Gothic"
ROSE="8C4A5E"; PINK="F6E9EC"; INPUT="FFF8E1"; GREY="F2F2F2"
thin=Side(style="thin",color="D9C2C9"); B=Border(left=thin,right=thin,top=thin,bottom=thin)
def font(**k): return Font(name=F,**k)
def title(ws,text,sub):
    ws["A1"]=text; ws["A1"].font=font(size=16,bold=True,color=ROSE)
    ws["A2"]=sub; ws["A2"].font=font(size=10,color="666666")
def header(ws,row,cols):
    for i,c in enumerate(cols,1):
        x=ws.cell(row=row,column=i,value=c)
        x.font=font(bold=True,color="FFFFFF"); x.fill=PatternFill("solid",fgColor=ROSE)
        x.alignment=Alignment(horizontal="center",vertical="center",wrap_text=True); x.border=B
def body(ws,r1,r2,c1,c2,fill=INPUT):
    for r in range(r1,r2+1):
        for c in range(c1,c2+1):
            x=ws.cell(row=r,column=c); x.border=B; x.font=font(size=10)
            x.alignment=Alignment(vertical="top",wrap_text=True)
            if fill: x.fill=PatternFill("solid",fgColor=fill)

wb=Workbook()
# --- 使い方
ws=wb.active; ws.title="使い方"
title(ws,"ブログ記事 棚卸し＆目次づくりテンプレート","『電子書籍をブログ記事で1冊目を出す』読者限定プレゼント①")
rows=[
("このテンプレートでできること","ブログ記事を一覧にして本に使える記事を選び、「6つの箱」に仕分けて、目次のたたき台と執筆スケジュールまでつくれます（本書 第3〜5章）。"),
("色の見かた","クリーム色のセル＝あなたが書き込むところ／白いセル＝自動で計算されるところ（触らなくてOK）"),
("STEP1　コンセプト","「①コンセプト」シートで、誰のための・どんな悩みを・どう変える本かを1文にまとめます。迷ったら、いつもこの1文に戻りましょう。"),
("STEP2　記事の棚卸し","「②記事の棚卸し」シートに記事を書き出します。全部が大変なら、アクセスの多い記事トップ30からでOK。2行目（例）は消して使ってください。"),
("STEP3　仕分け","同じシートで「6つの箱」と「使える？（◎○✕）」を、プルダウンから選びます。"),
("STEP4　足りない箱を確認","「③6つの箱チェック」シートに、箱ごとの記事数が自動で出ます。少ない箱が「書き足すところ」です。"),
("STEP5　目次づくり","「④目次づくり」シートで、章と見出しを決め、使う記事の番号を書き込みます。"),
("STEP6　スケジュール","「⑤8週間スケジュール」シートに開始日を入れると、各週の日付が自動で入ります。1日30分ずつ進めましょう。"),
("Googleスプレッドシートで使うとき","Googleドライブにアップロードし、「Googleスプレッドシートで開く」を選んでください。プルダウンや自動計算もそのまま使えます。"),
]
for i,(a,b) in enumerate(rows,4):
    ws.cell(row=i,column=1,value=a).font=font(bold=True,color=ROSE)
    c=ws.cell(row=i,column=2,value=b); c.font=font(size=10); c.alignment=Alignment(wrap_text=True,vertical="top")
    ws.cell(row=i,column=1).alignment=Alignment(vertical="top",wrap_text=True)
    ws.row_dimensions[i].height=42
ws["A15"]="凡例"; ws["A15"].font=font(bold=True)
ws["B15"]="書き込むセル"; ws["B15"].fill=PatternFill("solid",fgColor=INPUT); ws["B15"].font=font(size=10); ws["B15"].border=B
ws["B16"]="自動で計算されるセル"; ws["B16"].font=font(size=10); ws["B16"].border=B
ws.column_dimensions["A"].width=28; ws.column_dimensions["B"].width=90

# --- コンセプト
ws=wb.create_sheet("①コンセプト")
title(ws,"① コンセプトを1文にする","本書 第3章「誰の、どんな悩みを、どう変える本か」を決める")
qs=[("この本は、誰のための本ですか？","年齢・仕事・家族・今の状況など、いちばん大好きなお客様を思い浮かべて具体的に"),
("その人は、どんなことに悩んでいますか？","夜ひとりでスマホで検索していそうな言葉で"),
("読み終えたとき、その人はどう変わっていますか？","この「読後の変化」が本のゴールになります"),
("誰（短く）","例：40代の働く女性"),("悩み（短く）","例：疲れ顔の悩み"),("なりたい状態（短く）","例：毎日の5分ケアで自分を好きになれる")]
header(ws,4,["質問","ヒント","あなたの答え"])
for i,(q,h) in enumerate(qs,5):
    ws.cell(row=i,column=1,value=q); ws.cell(row=i,column=2,value=h)
    ws.row_dimensions[i].height=60 if i<8 else 28
body(ws,5,10,1,2,fill=None); body(ws,5,10,3,3)
ws["A12"]="コンセプトの1文（自動）"; ws["A12"].font=font(bold=True,color=ROSE)
ws["B12"]='=IF(OR(C8="",C9="",C10=""),"↑ 上の「短く」3つを書くと、ここに1文ができます",C8&"が、"&C9&"から抜け出し、"&C10&"になるための本")'
ws.merge_cells("B12:C12"); ws["B12"].font=font(size=12,bold=True); ws["B12"].alignment=Alignment(wrap_text=True,vertical="center")
ws.row_dimensions[12].height=44
ws["A14"]="タイトル案"; ws["A15"]="サブタイトル案"
for r in (14,15):
    ws.cell(row=r,column=1).font=font(bold=True); ws.merge_cells(f"B{r}:C{r}"); body(ws,r,r,2,3)
ws["A16"]="タイトルのコツ：①悩みか欲しい未来が入っている ②誰のための本かわかる ③具体的な数字や手軽さがある"; ws["A16"].font=font(size=9,color="666666")
for c,w in zip("ABC",(30,40,60)): ws.column_dimensions[c].width=w

# --- 棚卸し
ws=wb.create_sheet("②記事の棚卸し")
title(ws,"② ブログ記事の棚卸し","本書 第4章　◎＝そのまま柱になる／○＝書き直せば使える／✕＝今回は使わない")
cols=["No.","記事タイトル","URL","アクセス","6つの箱","使える？","リライトメモ（削る・つなぐ・足す）"]
header(ws,4,cols)
N=100
for r in range(5,5+N):
    ws.cell(row=r,column=1,value=r-4).alignment=Alignment(horizontal="center")
body(ws,5,4+N,2,7); body(ws,5,4+N,1,1,fill=None)
ex=["疲れ顔の原因は「むくみ」だった（例）","https://example.com/blog/1","多","原因","◎","冒頭の挨拶と予約案内を削る／お客様Aさんのエピソードを足す"]
for i,v in enumerate(ex,2):
    c=ws.cell(row=5,column=i,value=v); c.font=font(size=10,italic=True,color="888888")
rng=f"{{}}5:{{}}{4+N}"
for col,lst in (("D",'"多,中,少"'),("E",'"共感,原因,考え方,方法,未来,次の一歩"'),("F",'"◎,○,✕"')):
    dv=DataValidation(type="list",formula1=lst,allow_blank=True); ws.add_data_validation(dv); dv.add(f"{col}5:{col}{4+N}")
ws.conditional_formatting.add(f"A5:G{4+N}",FormulaRule(formula=['$F5="◎"'],fill=PatternFill("solid",fgColor="E8F3E8")))
ws.conditional_formatting.add(f"A5:G{4+N}",FormulaRule(formula=['$F5="✕"'],font=Font(color="AAAAAA")))
for c,w in zip("ABCDEFG",(6,42,30,9,12,9,48)): ws.column_dimensions[c].width=w
ws.freeze_panes="A5"

# --- 6つの箱
ws=wb.create_sheet("③6つの箱チェック")
title(ws,"③ 6つの箱チェック（自動集計）","本書 第4章　読者が変化していく順番に、記事がそろっているかを確認します")
header(ws,4,["順番","箱","その箱の役割","◎の数","○の数","使える記事の合計","判定"])
boxes=[("共感","「こんなことで悩んでいませんか？」読者の今の状態"),("原因","「実はその原因は〇〇なんです」気づき"),("考え方","「だから、こう考えればいいんです」視点の転換"),("方法","「具体的には、こうやります」実践"),("未来","「続けると、こう変わります」希望"),("次の一歩","「もっと先に進みたい方へ」導線")]
S="'②記事の棚卸し'"
for i,(b,d) in enumerate(boxes,5):
    ws.cell(row=i,column=1,value=i-4).alignment=Alignment(horizontal="center")
    ws.cell(row=i,column=2,value=b); ws.cell(row=i,column=3,value=d)
    ws.cell(row=i,column=4,value=f'=COUNTIFS({S}!$E$6:$E$104,B{i},{S}!$F$6:$F$104,"◎")')
    ws.cell(row=i,column=5,value=f'=COUNTIFS({S}!$E$6:$E$104,B{i},{S}!$F$6:$F$104,"○")')
    ws.cell(row=i,column=6,value=f"=D{i}+E{i}")
    ws.cell(row=i,column=7,value=f'=IF(F{i}=0,"✍ 書き足しが必要",IF(F{i}<2,"△ 少なめ。補強を","◎ 十分"))')
    ws.row_dimensions[i].height=30
body(ws,5,10,1,7,fill=None)
ws["A11"]="合計"; ws["A11"].font=font(bold=True)
for c in "DEF": ws[f"{c}11"]=f"=SUM({c}5:{c}10)"; ws[f"{c}11"].font=font(bold=True); ws[f"{c}11"].border=B
ws["A13"]="※「②記事の棚卸し」の例の行（5行目）は集計に含まれません。〈原因〉〈考え方〉が少ないときは、あなたの想いや「なぜそうするのか」を書き足すチャンスです。"
ws["A13"].font=font(size=9,color="666666")
for c,w in zip("ABCDEFG",(7,12,46,9,9,16,20)): ws.column_dimensions[c].width=w

# --- 目次
ws=wb.create_sheet("④目次づくり")
title(ws,"④ 目次のたたき台","本書 第4章　1章＝3,000〜6,000字、1見出し＝1,000〜2,000字が目安。見出しは「読むだけで中身がわかる」言葉で")
header(ws,4,["章","箱","見出し（読みたくなる言葉で）","使う記事No.","書き足すこと","目安文字数","進み具合"])
toc=[("はじめに","共感"),("第1章","共感"),("第1章","原因"),("第2章","考え方"),("第2章","考え方"),("第3章","方法"),("第3章","方法"),("第3章","方法"),("第4章","方法"),("第4章","方法"),("第5章","未来"),("第5章","未来"),("おわりに","未来"),("著者からのご案内","次の一歩")]
for i,(c,b) in enumerate(toc,5):
    ws.cell(row=i,column=1,value=c); ws.cell(row=i,column=2,value=b)
    ws.cell(row=i,column=6,value=1500 if c not in("はじめに","おわりに","著者からのご案内") else 1000)
    ws.cell(row=i,column=6).number_format='#,##0"字"'
end=4+len(toc)+6
body(ws,5,end,1,7)
dv=DataValidation(type="list",formula1='"未着手,執筆中,完成"',allow_blank=True); ws.add_data_validation(dv); dv.add(f"G5:G{end}")
dv2=DataValidation(type="list",formula1='"共感,原因,考え方,方法,未来,次の一歩"',allow_blank=True); ws.add_data_validation(dv2); dv2.add(f"B5:B{end}")
t=end+2
ws.cell(row=t,column=5,value="合計（目安）").font=font(bold=True)
ws.cell(row=t,column=6,value=f"=SUM(F5:F{end})").number_format='#,##0"字"'
ws.cell(row=t+1,column=5,value="完成した見出し").font=font(bold=True)
ws.cell(row=t+1,column=6,value=f'=COUNTIF(G5:G{end},"完成")&" / "&COUNTA(C5:C{end})')
ws.cell(row=t+2,column=1,value="※ 章・箱・文字数はあらかじめ例を入れています。自由に書き換えてください。1冊目は合計2〜3万字で十分です。").font=font(size=9,color="666666")
for c,w in zip("ABCDEFG",(16,11,44,14,34,12,11)): ws.column_dimensions[c].width=w
ws.freeze_panes="A5"

# --- スケジュール
ws=wb.create_sheet("⑤8週間スケジュール")
title(ws,"⑤ 8週間の執筆スケジュール","本書 第5章　1日30分×約2か月で1冊に")
ws["A3"]="開始日（月曜日がおすすめ）"; ws["A3"].font=font(bold=True)
ws["C3"]=None; ws["C3"].fill=PatternFill("solid",fgColor=INPUT); ws["C3"].border=B; ws["C3"].number_format="yyyy/mm/dd"
header(ws,5,["週","やること","開始","終了","メモ","完了"])
plan=["コンセプトを決める／記事を一覧にする","6つの箱に分け、目次をつくる","第1章・第2章をリライト（1日1見出し）","第3章・第4章をリライト（1日1見出し）","第5章／エピソード・ワークを書き足す","はじめに・おわりに・巻末のご案内を書く","全体を読み返す／誤字脱字チェック／表紙づくり","KDPに登録して出版！"]
for i,p in enumerate(plan,6):
    w=i-5
    ws.cell(row=i,column=1,value=f"{w}週目"); ws.cell(row=i,column=2,value=p)
    ws.cell(row=i,column=3,value=f'=IF($C$3="","",$C$3+{(w-1)*7})').number_format="m/d"
    ws.cell(row=i,column=4,value=f'=IF($C$3="","",$C$3+{(w-1)*7+6})').number_format="m/d"
    ws.row_dimensions[i].height=26
body(ws,6,13,1,4,fill=None); body(ws,6,13,5,6)
dv=DataValidation(type="list",formula1='"□,✓"',allow_blank=True); ws.add_data_validation(dv); dv.add("F6:F13")
ws["A15"]='=COUNTIF(F6:F13,"✓")&" / 8 週 完了"'; ws["A15"].font=font(bold=True,color=ROSE)
for c,w in zip("ABCDEF",(10,46,9,9,34,8)): ws.column_dimensions[c].width=w

for s in wb.worksheets:
    s.sheet_view.showGridLines=False
    for row in s.iter_rows():
        for c in row:
            if c.font and c.font.name!=F: c.font=Font(name=F,size=c.font.size,bold=c.font.bold,italic=c.font.italic,color=c.font.color)
wb.save(sys.argv[1])
