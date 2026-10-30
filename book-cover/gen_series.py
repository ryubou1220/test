import sys,os
d=sys.argv[1]; base=open(os.path.join(d,'book.html')).read()
old_content=base[base.index('  <div class="content">'):base.index('  </div>\n </div>\n</div></div>')]
old_spine='<div class="vt">コンテンツフリーダム<span>CONTENT FREEDOM</span></div>'
covers=[
 dict(out='target',teal='#0f8a6a',teal2='#2fb08c',
  spine='ターゲット浮彫シート',spine_en='TARGET PROFILING',spine_fs=44,
  content='''  <div class="content">
   <div class="en small" style="font-size:24px;letter-spacing:.3em">CONTENT FREEDOM SERIES</div>
   <div class="en" style="margin-top:6px">TARGET PROFILING SHEET</div>
   <div class="title" style="font-size:104px">ターゲット<br><span class="big" style="font-size:124px">浮彫シート</span></div>
   <div class="tag">「たった1人」の理想客が見えてくる</div>
   <div class="en sub-en">FIND YOUR IDEAL CUSTOMER</div>
   <div class="sub" style="font-size:37px">書き込むだけで、刺さる言葉が見つかる</div>
   <div class="rule"></div>
   <div class="en small" style="font-size:30px">PERSONA・PAIN・FUTURE</div>
   <div class="foot">ペルソナ・悩み・理想の未来</div>
  '''),
 dict(out='salespage',teal='#5a3fa6',teal2='#8467cc',
  spine='商品ページかんたん下書きテンプレ',spine_en='SALES PAGE',spine_fs=38,
  content='''  <div class="content" style="padding-top:185px">
   <div class="en small" style="font-size:24px;letter-spacing:.3em">CONTENT FREEDOM SERIES</div>
   <div class="en" style="margin-top:6px">SALES PAGE DRAFT TEMPLATE</div>
   <div class="title" style="font-size:96px;margin-top:16px;line-height:1.04">商品ページ<br><span style="font-size:80px">かんたん下書き</span><br><span class="big" style="font-size:104px">テンプレ</span></div>
   <div class="tag" style="margin-top:18px">穴埋めするだけで、売れる構成が完成</div>
   <div class="en sub-en" style="margin-top:20px">7 BLOCKS TO YOUR SALES PAGE</div>
   <div class="sub" style="font-size:42px">売れる商品ページの7ブロック</div>
   <div class="rule"></div>
   <div class="en small" style="font-size:30px">COPY・STORY・OFFER</div>
   <div class="foot" style="font-size:32px">キャッチ・ストーリー・オファー</div>
  '''),
]
for c in covers:
  h=base.replace(old_content,c['content'])
  h=h.replace(old_spine,f'<div class="vt" style="font-size:{c["spine_fs"]}px">{c["spine"]}<span>{c["spine_en"]}</span></div>')
  # アクセント色（ティール）だけ差し替え
  h=h.replace('#127f95',c['teal']).replace('#2aa3b5',c['teal2'])
  open(os.path.join(d,c['out']+'.html'),'w').write(h)
