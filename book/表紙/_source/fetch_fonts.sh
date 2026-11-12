#!/bin/sh
# 表紙で使うフォント（Noto Serif JP / Zen Maru Gothic / Zen Kaku Gothic New：いずれもSIL Open Font License）を
# Google Fonts から取得し、fonts/local.css を作る。cover.html と同じフォルダで実行する。
set -e
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36"
mkdir -p fonts/f
curl -sS -A "$UA" -o fonts/fonts.css "https://fonts.googleapis.com/css2?family=Noto+Serif+JP:wght@500;700;900&family=Zen+Maru+Gothic:wght@500;700&family=Zen+Kaku+Gothic+New:wght@500;700;900&display=block"
grep -o 'https://fonts.gstatic.com[^)]*' fonts/fonts.css | sort -u | while read u; do
  n=$(echo "$u" | sed 's#https://fonts.gstatic.com/s/##; s#/#_#g'); curl -sS -o "fonts/f/$n" "$u"; done
python3 -c "
import re;s=open('fonts/fonts.css').read()
print(re.sub(r'url\(https://fonts.gstatic.com/s/([^)]*)\)',lambda m:'url(f/'+m.group(1).replace('/','_')+')',s),end='')" > fonts/local.css
# 画像の書き出し： node shot.js \$PWD/cover.html \$PWD/out
