import json
import os
d=os.path.dirname(os.path.abspath(__file__))+"/"
css=open(d+'base.css',encoding='utf-8').read()+open(d+'edit.css',encoding='utf-8').read()
js=open(d+'page.js',encoding='utf-8').read()
S=json.load(open(d+'content.json',encoding='utf-8'))
assert '</script' not in js.lower()
def esc(s): return s.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;').replace('"','&quot;')
RESET=':root{color-scheme:light;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0;font:14px/1.5 system-ui,sans-serif}img{max-width:100%}[hidden]{display:none!important}'
FONTS='<link rel="preconnect" href="https://fonts.googleapis.com">\n<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Zen+Kaku+Gothic+New:wght@400;700;900&family=Zen+Old+Mincho:wght@700&display=swap">'
j=json.dumps(S,ensure_ascii=False,indent=1).replace('<','\\u003c')
body=f'<title>{esc(S["meta"]["title"])}</title>\n<meta name="description" content="{esc(S["meta"]["description"])}">\n{FONTS}\n<style id="page-style">{css}</style>\n<div id="app"></div>\n<div id="edbar" class="edbar" hidden></div>\n<script type="application/json" id="content">{j}</script>\n<script id="page-script">{js}</script>\n'
open(d+'../index.html','w',encoding='utf-8').write('<!doctype html><html><head><meta charset=utf8><meta name=viewport content="width=device-width,initial-scale=1,viewport-fit=cover"><style>'+RESET+'</style></head><body>'+body+'</body></html>')

