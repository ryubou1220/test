#!/usr/bin/env python3
"""撮影アングル帳（印刷用 A4 PDF）を作る

使い方: python checklist_pdf.py 写真帳.xlsx 撮影アングル帳.pdf
日本語フォントは IPAゴシック（ipag.ttf）を使う。
"""
import sys,io
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
import shashincho as S
from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
pdfmetrics.registerFont(TTFont('G','/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf'))
b=S.Book.load(sys.argv[1]);G=S.angle_groups(S.scan(b))
sites=[('川上谷川','番号順に撮影','撮影時刻の順に①から貼り付けます。番号順に撮ってください。'),
 ('成願寺川','番号順に撮影','撮影時刻の順に貼り付けます。※見本は川上谷川の写真の流用（構図の参考程度）'),
 ('久僧','順番自由','画像照合で同じアングルの枠へ貼ります。浸食部・堆積部シートにも自動で入ります。'),
 ('宇川','順番自由','画像照合で同じアングルの枠へ貼ります。'),
 ('木津','順番自由','画像照合で同じアングルの枠へ貼ります。堆積シートにも自動で入ります。')]
W,H=A4; c=canvas.Canvas(sys.argv[2],pagesize=A4); c.setTitle('撮影アングル帳 R8.10.08')
mx=12*mm; gap=6*mm; cw=(W-2*mx-gap)/2; iw=cw; ih=iw*3/4; cellh=ih+19*mm
top=H-30*mm; page=[0]
def header(site,mode,note,cont):
    page[0]+=1
    c.setFont('G',15);c.drawString(mx,H-14*mm,f'撮影アングル帳　令和8年10月8日　／　{site}'+('（続き）' if cont else ''))
    c.setFont('G',10);c.setFillColorRGB(.85,.28,.06) if mode.startswith('番号') else c.setFillColorRGB(.12,.44,.47)
    c.drawString(mx,H-21*mm,f'【{mode}】');c.setFillColorRGB(.25,.25,.25);c.drawString(mx+c.stringWidth(f'【{mode}】','G',10)+3*mm,H-21*mm,note)
    c.setFillColorRGB(0,0,0);c.setFont('G',8);c.drawRightString(W-mx,8*mm,f'{page[0]}');c.line(mx,H-24*mm,W-mx,H-24*mm)
for site,mode,note in sites:
    items=[g for g in G if site in g[0].sheet]
    for k,g in enumerate(items):
        pos=k%6
        if pos==0:
            if page[0]: c.showPage()
            header(site,mode,note,k>0)
        col,row=pos%2,pos//2
        x=mx+col*(cw+gap); y=top-(row+1)*cellh+12*mm
        src=g[0].ref or g[0].inslot
        im=Image.open(io.BytesIO(b.files[src.target])).convert('RGB')
        im.thumbnail((900,900));bio=io.BytesIO();im.save(bio,'JPEG',quality=82);bio.seek(0)
        c.drawImage(ImageReader(bio),x,y,iw,ih,preserveAspectRatio=True,anchor='c')
        c.rect(x,y,iw,ih)
        c.setFillColorRGB(.85,.28,.06);c.rect(x,y+ih-9*mm,13*mm,9*mm,fill=1,stroke=0)
        c.setFillColorRGB(1,1,1);c.setFont('G',15);c.drawCentredString(x+6.5*mm,y+ih-6.6*mm,str(k+1))
        c.setFillColorRGB(0,0,0);c.setFont('G',10.5)
        cap=g[0].caption.replace('　',' ').strip()
        c.drawString(x,y-5*mm,cap[:30])
        c.setFont('G',7.5);c.setFillColorRGB(.35,.35,.35)
        wh=' ／ '.join(f"{s.sheet.replace('10月08日','')} {s.row}行{s.side}" for s in g)
        c.drawString(x,y-9.5*mm,wh[:70]);c.setFillColorRGB(0,0,0)
        c.setFont('G',9);c.rect(x+iw-20*mm,y-6*mm,3.2*mm,3.2*mm);c.drawString(x+iw-15.5*mm,y-5.5*mm,'撮影済')
c.save()
