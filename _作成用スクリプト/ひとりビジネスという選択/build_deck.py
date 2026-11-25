# Build a lecture deck from the CF mindset template.
# usage: python3 -I build_deck.py template.pptx out.pptx spec.json
import sys, json, os, re, shutil, subprocess, tempfile, zipfile, copy
PS = "/root/.claude/skills/synced/3750aaef-df71-4672-a98f-1f37e95f826f_3b36aaa9-04a9-45f5-bdc5-ba3727c50d8f/pptx/scripts"
tpl, out, specf = sys.argv[1:4]
spec = json.load(open(specf, encoding="utf8"))
TYPES = {"COVER": 1, "BUL": 2, "GRID4": 3, "SEC": 4, "ROWS3S": 7, "ROWS3": 13, "SUM": 15, "NEXT": 16}
tmp = tempfile.mkdtemp(); u = os.path.join(tmp, "u")
zipfile.ZipFile(tpl).extractall(u)
pres = open(f"{u}/ppt/presentation.xml", encoding="utf8").read()
rels = open(f"{u}/ppt/_rels/presentation.xml.rels", encoding="utf8").read()
rid2t = dict(re.findall(r'Id="(rId\d+)"[^>]*Target="slides/(slide\d+\.xml)"', rels))
rid2t.update({a: b for b, a in re.findall(r'Target="slides/(slide\d+\.xml)"[^>]*Id="(rId\d+)"', rels)})
order = [rid2t[r] for r in re.findall(r'<p:sldId [^>]*r:id="(rId\d+)"', pres)]
orig_ids = re.findall(r'<p:sldId [^>]*/>', pres)
last = order[-1]
for s in spec["slides"]:
    src = order[TYPES[s["type"]] - 1]
    r = subprocess.run(["python3", f"{PS}/add_slide.py", u, src, "--after", last], capture_output=True, text=True)
    m = re.search(r"(slide\d+\.xml)", r.stdout); assert m, r.stdout + r.stderr
    last = m.group(1)
# drop the original slides
pres = open(f"{u}/ppt/presentation.xml", encoding="utf8").read()
for t in orig_ids: pres = pres.replace(t, "", 1)
open(f"{u}/ppt/presentation.xml", "w", encoding="utf8").write(pres)
# footer
for lf in ("slideLayout3.xml", "slideLayout4.xml"):
    p = f"{u}/ppt/slideLayouts/{lf}"; x = open(p, encoding="utf8").read()
    x = x.replace("コンテンツ・フリーダム ｜ 第2講義　マインドセット編", spec["footer"])
    open(p, "w", encoding="utf8").write(x)
subprocess.run(["python3", f"{PS}/clean.py", u], capture_output=True, text=True, check=True)
mid = os.path.join(tmp, "mid.pptx")
subprocess.run(f'cd "{u}" && zip -qXrD "{mid}" .', shell=True, check=True)

from pptx import Presentation
from pptx.util import Pt
prs = Presentation(mid)
def text_shapes(slide):
    return [sh for sh in slide.shapes if sh.has_text_frame and sh.text_frame.text.strip() and "Slide Number" not in sh.name]
def set_paras(sh, lines):
    tf = sh.text_frame; ps = list(tf.paragraphs)
    while len(ps) < len(lines):
        new = copy.deepcopy(ps[-1]._p); ps[-1]._p.addnext(new); ps = list(tf.paragraphs)
    for p in ps[len(lines):]: p._p.getparent().remove(p._p)
    for p, line in zip(tf.paragraphs, lines):
        runs = p.runs
        runs[0].text = line
        for r in runs[1:]: r._r.getparent().remove(r._r)
for slide, s in zip(prs.slides, spec["slides"]):
    shs = text_shapes(slide); vals = s["t"]
    assert len(shs) == len(vals), (s["type"], len(shs), len(vals), vals[:2])
    for sh, v in zip(shs, vals):
        set_paras(sh, v if isinstance(v, list) else [v])
    nt = slide.notes_slide.notes_text_frame
    nt.text = "【読み方】／＝軽く息継ぎ　（間）＝ひと呼吸　【】＝ゆっくり強調\n\n" + s.get("n", "")
MAP = {11: 14, 14: 18, 15: 20, 16: 20, 18: 22, 19: 22, 20: 24, 22: 26, 28: 30, 30: 32}
for slide in prs.slides:
    for sh in slide.shapes:
        if not sh.has_text_frame or "Slide Number" in sh.name: continue
        for para in sh.text_frame.paragraphs:
            for r in para.runs:
                if r.font.size and int(r.font.size.pt) in MAP:
                    r.font.size = Pt(MAP[int(r.font.size.pt)])
prs.save(out)
shutil.rmtree(tmp)
print("built", out, len(spec["slides"]))
