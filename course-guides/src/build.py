"""解説テキストをPDFにする。

  python3 course-guides/src/build.py

src/*.md → *.html（確認用）と stepN.pdf（A4・配布用）
"""
import pathlib
import re
import subprocess

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
FONT = '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Zen+Kaku+Gothic+New:wght@400;700;900&display=swap">'


def main():
    pages = []
    for md in sorted(SRC.glob("*.md")):
        accent = re.search(r'^accent:\s*"([^"]+)"', md.read_text(encoding="utf-8"), re.M).group(1)
        out = ROOT / f"{md.stem}.html"
        subprocess.run(["pandoc", str(md), "-s", "-o", str(out), "--css", str(SRC / "guide.css"),
                        "--embed-resources", "--columns=400", "-V", "document-css=false"], check=True)
        html = out.read_text(encoding="utf-8")
        html = html.replace("</head>", f"{FONT}<style>:root{{--a:{accent}}}</style></head>", 1)
        out.write_text(html, encoding="utf-8")
        pages.append(out)
    js = """
import { chromium } from '%s/playwright/index.mjs';
const b = await chromium.launch();
for (const f of %s) {
  const p = await b.newPage();
  await p.goto('file://' + f, { waitUntil: 'networkidle' }).catch(() => {});
  await p.evaluate(() => document.fonts.ready);
  await p.pdf({ path: f.replace(/\\.html$/, '.pdf'), format: 'A4', printBackground: true,
    displayHeaderFooter: true, headerTemplate: '<span></span>',
    footerTemplate: '<div style="font-size:8px;width:100%%;text-align:center;color:#888">週末DIY 5ステップ講座　<span class="pageNumber"></span> / <span class="totalPages"></span></div>' });
}
await b.close();
""" % (subprocess.run(["npm", "root", "-g"], capture_output=True, text=True).stdout.strip(),
       [str(p) for p in pages])
    subprocess.run(["node", "--input-type=module", "-e", js], check=True)
    print(len(pages), "guides")


if __name__ == "__main__":
    main()
