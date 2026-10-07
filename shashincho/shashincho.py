#!/usr/bin/env python3
"""写真帳（業務報告書）への写真貼り付けツール

テンプレートの各写真枠（「・」＋キャプション行の下 10 行分）を検出し、
印刷範囲の右側（AR 列以降）に置かれた前回写真、または枠内の既存写真を
「アングル見本」として扱う。新しく撮影した写真を見本と画像照合し、
同じアングルの枠へ自動で貼り付ける。

使い方:
  python shashincho.py checklist 写真帳.xlsx -o 撮影リスト.html
  python shashincho.py paste 写真帳.xlsx 写真フォルダ -o 出力.xlsx [--map map.csv] [--drop-ref]

xlsx は ZIP/XML を直接編集するため、矢印・丸・番号ラベル等の図形は保持される。
"""
import argparse
import base64
import csv
import hashlib
import io
import os
import posixpath
import re
import sys
import zipfile
from dataclasses import dataclass, field

from lxml import etree
from PIL import Image, ImageOps

try:  # iPhone の HEIC 写真（pip install pillow-heif で対応）
    from pillow_heif import register_heif_opener
    register_heif_opener()
except ImportError:
    pass

NS = {
    "m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "pr": "http://schemas.openxmlformats.org/package/2006/relationships",
    "xdr": "http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
}
REL_IMAGE = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image"
REL_DRAWING = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/drawing"

PRINT_LAST_COL = 42      # AQ (0 始まり)。これより右は印刷範囲外＝見本置き場
LEFT_PHOTO_COL = 1       # B
RIGHT_PHOTO_COL = 22     # W
RIGHT_SIDE_MIN_COL = 21  # 枠内写真の左右判定
REF_RIGHT_MIN_COL = 48   # AW 以降は右側の見本
BOX_CX = 3206749         # 写真枠 8.9cm
BOX_CY = 2412999         # 写真枠 6.7cm
OFF_X = OFF_Y = 10583
MAX_EDGE = 1024          # 貼り付け画像の長辺(px)。ファイル肥大化防止
MAP_WORDS = ("位置図", "観測位置")  # 図面枠は写真照合の対象外


def q(tag):
    p, t = tag.split(":")
    return "{%s}%s" % (NS[p], t)


def col_index(ref):
    letters = re.match(r"[A-Z]+", ref).group(0)
    n = 0
    for ch in letters:
        n = n * 26 + ord(ch) - 64
    return n - 1


@dataclass
class Pic:
    anchor: etree._Element
    rid: str
    target: str  # zip 内パス
    col: int
    row: int


@dataclass
class Slot:
    sheet: str
    drawing: str
    row: int          # キャプション行（1 始まり）
    side: str         # "左" / "右"
    caption: str
    label: str = ""   # キャプション上の工種名など
    ref: Pic = None   # アングル見本
    inslot: Pic = None
    group: str = ""   # 確認箇所＋見本画像のハッシュ（同じ見本＝同じ写真）
    is_map: bool = False

    @property
    def sid(self):
        return f"{self.sheet}!{'C' if self.side == '左' else 'X'}{self.row}"


@dataclass
class Book:
    path: str
    files: dict = field(default_factory=dict)
    sheets: list = field(default_factory=list)  # (name, sheet_path, drawing_path)

    @classmethod
    def load(cls, path):
        b = cls(path)
        with zipfile.ZipFile(path) as z:
            for n in z.namelist():
                b.files[n] = z.read(n)
        wb = etree.fromstring(b.files["xl/workbook.xml"])
        rels = b.rels("xl/workbook.xml")
        for s in wb.find(q("m:sheets")):
            sp = rels[s.get(q("r:id"))][1]
            srels = b.rels(sp)
            dp = next((t for (ty, t) in srels.values() if ty == REL_DRAWING), None)
            b.sheets.append((s.get("name"), sp, dp))
        return b

    @staticmethod
    def rels_path(part):
        d, f = posixpath.split(part)
        return posixpath.join(d, "_rels", f + ".rels")

    def rels(self, part):
        rp = self.rels_path(part)
        if rp not in self.files:
            return {}
        out = {}
        base = posixpath.dirname(part)
        for r in etree.fromstring(self.files[rp]):
            t = r.get("Target")
            full = t.lstrip("/") if t.startswith("/") else posixpath.normpath(posixpath.join(base, t))
            out[r.get("Id")] = (r.get("Type"), full)
        return out

    def save(self, path):
        with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
            # [Content_Types].xml を先頭に
            for n in sorted(self.files, key=lambda n: n != "[Content_Types].xml"):
                z.writestr(n, self.files[n])


def shared_strings(book):
    if "xl/sharedStrings.xml" not in book.files:
        return []
    root = etree.fromstring(book.files["xl/sharedStrings.xml"])
    # rPh（ふりがな）は除外
    return ["".join(t.text or "" for t in si.iter(q("m:t")) if t.getparent().tag != q("m:rPh"))
            for si in root.findall(q("m:si"))]


def cell_texts(book, sheet_path, sst):
    root = etree.fromstring(book.files[sheet_path])
    out = {}
    for c in root.iter(q("m:c")):
        v = c.find(q("m:v"))
        t = c.get("t")
        if t == "s" and v is not None:
            out[c.get("r")] = sst[int(v.text)]
        elif t == "inlineStr":
            out[c.get("r")] = "".join(t.text or "" for t in c.iter(q("m:t")))
        elif v is not None:
            out[c.get("r")] = v.text
    return out


def drawing_pics(book, dpath):
    root = etree.fromstring(book.files[dpath])
    rels = book.rels(dpath)
    pics = []
    for anc in root:
        pic = anc.find(q("xdr:pic"))
        fr = anc.find(q("xdr:from"))
        if pic is None or fr is None:
            continue
        rid = pic.find(".//" + q("a:blip")).get(q("r:embed"))
        pics.append(Pic(anc, rid, rels[rid][1],
                        int(fr.find(q("xdr:col")).text), int(fr.find(q("xdr:row")).text)))
    return root, pics


def scan(book):
    """全シートの写真枠と見本を検出する"""
    sst = shared_strings(book)
    slots = []
    for name, sp, dp in book.sheets:
        cells = cell_texts(book, sp, sst)
        pics = drawing_pics(book, dp)[1] if dp else []
        site = cells.get("J11", "")  # 確認箇所。現場が違えば同じ見本でも別撮影
        for ref, val in cells.items():
            m = re.fullmatch(r"([BW])(\d+)", ref)
            if not m or val.strip() != "・":
                continue
            side = "左" if m.group(1) == "B" else "右"
            r = int(m.group(2))
            cap_col = "C" if side == "左" else "X"
            caption = cells.get(f"{cap_col}{r}", "").strip()
            label = cells.get(f"{cap_col}{r - 1}", "").strip()
            s = Slot(name, dp, r, side, caption, label)
            s.is_map = any(w in caption for w in MAP_WORDS)
            r0 = r - 1  # 0 始まりのキャプション行
            for p in pics:
                if not (r0 - 1 <= p.row <= r0 + 2):
                    continue
                if p.col > PRINT_LAST_COL:
                    if (p.col >= REF_RIGHT_MIN_COL) == (side == "右"):
                        s.ref = p
                elif (p.col >= RIGHT_SIDE_MIN_COL) == (side == "右"):
                    s.inslot = p
            src = s.ref or s.inslot
            if src is not None:
                s.group = site + ":" + hashlib.sha1(book.files[src.target]).hexdigest()[:10]
            slots.append(s)
        # 「施工位置図」のようにキャプションだけで「・」が無い図面枠
        for ref, val in cells.items():
            m = re.fullmatch(r"C(\d+)", ref)
            if m and any(w in val for w in MAP_WORDS) and cells.get(f"B{m.group(1)}", "").strip() != "・":
                r = int(m.group(1))
                s = Slot(name, dp, r, "左", val.strip(), cells.get(f"C{r - 1}", "").strip(), is_map=True)
                for p in pics:
                    if r - 2 <= p.row <= r + 1 and p is not None:
                        if p.col > PRINT_LAST_COL:
                            s.ref = p
                        else:
                            s.inslot = p
                slots.append(s)
    order = {n: i for i, (n, _, _) in enumerate(book.sheets)}
    slots.sort(key=lambda s: (order[s.sheet], s.row, s.side != "左"))
    return slots


def angle_groups(slots):
    """同じ見本画像を持つ写真枠をまとめる（＝1 回の撮影で済むアングル）"""
    groups, seen = [], {}
    for s in slots:
        if s.is_map or not s.group:
            continue
        if s.group not in seen:
            seen[s.group] = len(groups)
            groups.append([])
        groups[seen[s.group]].append(s)
    return groups


# ---------------------------------------------------------------- 画像照合
def load_photo(path):
    im = Image.open(path)
    im = ImageOps.exif_transpose(im).convert("RGB")
    return im


def exif_time(path):
    try:
        ex = Image.open(path).getexif()
        t = ex.get_ifd(0x8769).get(36867) or ex.get(306)
        if t:
            return t
    except Exception:
        pass
    return "%f" % os.path.getmtime(path)


class Matcher:
    def __init__(self):
        import cv2
        self.cv2 = cv2
        self.sift = cv2.SIFT_create(nfeatures=1500)
        self.bf = cv2.BFMatcher(cv2.NORM_L2)

    def feat(self, im):
        import numpy as np
        g = ImageOps.grayscale(im)
        g.thumbnail((800, 800))
        a = np.asarray(g)
        a = self.cv2.createCLAHE(2.0, (8, 8)).apply(a)
        kp, des = self.sift.detectAndCompute(a, None)
        return kp, des

    def score(self, fa, fb):
        import numpy as np
        (ka, da), (kb, db) = fa, fb
        if da is None or db is None or len(ka) < 8 or len(kb) < 8:
            return 0
        good = []
        for pair in self.bf.knnMatch(da, db, k=2):
            if len(pair) == 2 and pair[0].distance < 0.75 * pair[1].distance:
                good.append(pair[0])
        if len(good) < 8:
            return len(good)
        pa = np.float32([ka[m.queryIdx].pt for m in good])
        pb = np.float32([kb[m.trainIdx].pt for m in good])
        # 同じ場所・同じ向きなら射影変換でほぼ重なる。基礎行列より厳しく誤一致を弾ける
        _, mask = self.cv2.findHomography(pa, pb, self.cv2.RANSAC, 8.0)
        return int(mask.sum()) if mask is not None else 0


def auto_match(book, groups, photos, log=print):
    import numpy as np
    from scipy.optimize import linear_sum_assignment
    m = Matcher()
    log(f"見本 {len(groups)} アングル / 新写真 {len(photos)} 枚 の特徴量を計算中…")
    rf = [m.feat(Image.open(io.BytesIO(book.files[(g[0].ref or g[0].inslot).target])).convert("RGB"))
          for g in groups]
    pf = [m.feat(load_photo(p)) for p in photos]
    S = np.zeros((len(photos), len(groups)))
    for i, a in enumerate(pf):
        for j, b in enumerate(rf):
            S[i, j] = m.score(a, b)
    rows, cols = linear_sum_assignment(-S)
    result = {}
    for i, j in zip(rows, cols):
        result[j] = (i, S[i, j])
    return result, S


# ---------------------------------------------------------------- 書き込み
def prepare_image(path):
    im = load_photo(path)
    im.thumbnail((MAX_EDGE, MAX_EDGE), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=80, optimize=True)
    return buf.getvalue(), im.size


def pic_anchor(cid, rid, col, row, w, h, name):
    # 枠(8.9×6.7cm)に縦横比を保って収め、中央寄せ
    scale = min(BOX_CX / w, BOX_CY / h)
    cx, cy = int(w * scale), int(h * scale)
    dx = OFF_X + (BOX_CX - cx) // 2
    dy = OFF_Y + (BOX_CY - cy) // 2
    xml = f"""<xdr:oneCellAnchor xmlns:xdr="{NS['xdr']}" xmlns:a="{NS['a']}" xmlns:r="{NS['r']}">
<xdr:from><xdr:col>{col}</xdr:col><xdr:colOff>{dx}</xdr:colOff><xdr:row>{row}</xdr:row><xdr:rowOff>{dy}</xdr:rowOff></xdr:from>
<xdr:ext cx="{cx}" cy="{cy}"/>
<xdr:pic><xdr:nvPicPr><xdr:cNvPr id="{cid}" name="{name}"/><xdr:cNvPicPr><a:picLocks noChangeAspect="1"/></xdr:cNvPicPr></xdr:nvPicPr>
<xdr:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></xdr:blipFill>
<xdr:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></xdr:spPr></xdr:pic>
<xdr:clientData/></xdr:oneCellAnchor>"""
    return etree.fromstring(xml)


class Writer:
    def __init__(self, book):
        self.b = book
        self.trees = {}
        self.relroots = {}
        self.n = 0

    def tree(self, dp):
        if dp not in self.trees:
            self.trees[dp] = etree.fromstring(self.b.files[dp])
            rp = Book.rels_path(dp)
            self.relroots[dp] = etree.fromstring(self.b.files[rp])
        return self.trees[dp], self.relroots[dp]

    def add_image(self, dp, data, col, row, size, name):
        root, rels = self.tree(dp)
        self.n += 1
        media = f"xl/media/shashin_{self.n:03d}.jpeg"
        self.b.files[media] = data
        ids = [int(re.sub(r"\D", "", r.get("Id")) or 0) for r in rels]
        rid = f"rId{max(ids + [0]) + 1}"
        rel = etree.SubElement(rels, "{%s}Relationship" % NS["pr"])
        rel.set("Id", rid)
        rel.set("Type", REL_IMAGE)
        rel.set("Target", "../media/" + posixpath.basename(media))
        cids = [int(e.get("id")) for e in root.iter(q("xdr:cNvPr")) if e.get("id", "").isdigit()]
        root.append(pic_anchor(max(cids + [1]) + 1, rid, col, row, size[0], size[1], name))

    def remove(self, dp, pic):
        root, _ = self.tree(dp)
        for anc in root:
            if anc is pic.anchor or etree.tostring(anc) == etree.tostring(pic.anchor):
                root.remove(anc)
                return

    def finish(self):
        for dp, root in self.trees.items():
            used = {e.get(q("r:embed")) for e in root.iter(q("a:blip"))} | \
                   {e.get(q("r:id")) for e in root.iter() if e.get(q("r:id"))}
            rels = self.relroots[dp]
            for r in list(rels):
                if r.get("Type") == REL_IMAGE and r.get("Id") not in used:
                    rels.remove(r)
            self.b.files[dp] = etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)
            self.b.files[Book.rels_path(dp)] = etree.tostring(rels, xml_declaration=True, encoding="UTF-8", standalone=True)
        # どこからも参照されなくなった画像を削除
        referenced = set()
        for n in list(self.b.files):
            if n.endswith(".rels"):
                part = n.replace("_rels/", "")[:-5]
                referenced |= {t for _, t in self.b.rels(part).values()}
        for n in list(self.b.files):
            if n.startswith("xl/media/") and n not in referenced:
                del self.b.files[n]


# ---------------------------------------------------------------- コマンド
def thumb_uri(data, edge=480):
    im = Image.open(io.BytesIO(data)).convert("RGB")
    im.thumbnail((edge, edge))
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=70)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def cmd_checklist(a):
    book = Book.load(a.xlsx)
    slots = scan(book)
    groups = angle_groups(slots)
    rows = []
    for i, g in enumerate(groups, 1):
        src = g[0].ref or g[0].inslot
        rows.append({
            "no": i,
            "img": thumb_uri(book.files[src.target]),
            "caption": g[0].caption,
            "label": g[0].label,
            "where": [f"{s.sheet} {s.row}行 {s.side}" for s in g],
        })
    empty = [s for s in slots if not s.group and not s.is_map]
    with open(a.out_csv, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["No", "シート", "行", "左右", "キャプション", "見本"])
        for i, g in enumerate(groups, 1):
            for s in g:
                w.writerow([i, s.sheet, s.row, s.side, s.caption, (s.ref and "右側見本") or "枠内写真"])
    import json
    print(json.dumps({"angles": len(groups), "slots": sum(len(g) for g in groups),
                      "no_reference": [s.sid for s in empty]}, ensure_ascii=False))
    if a.json:
        with open(a.json, "w", encoding="utf-8") as f:
            json.dump(rows, f, ensure_ascii=False)


def read_map(path):
    m = {}
    with open(path, encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            if r.get("写真ファイル", "").strip():
                m[int(r["No"])] = r["写真ファイル"].strip()
    return m


PHOTO_EXTS = (".jpg", ".jpeg", ".png", ".heic")


def list_photos(folder):
    fs = [os.path.join(folder, f) for f in os.listdir(folder)
          if f.lower().endswith(PHOTO_EXTS) and not f.startswith(".")]
    return sorted(fs, key=lambda p: (exif_time(p), os.path.basename(p)))


def photo_batches(root, groups, match_words):
    """写真フォルダを現場ごとに分け、(写真, 対象アングル番号, 照合方式) を返す。

    サブフォルダ名（例: 川上谷川, 久僧）をシート名に含むアングルが対象。
    シート名に match_words を含む現場は画像照合、それ以外は撮影順。
    """
    subs = sorted(d for d in os.listdir(root) if os.path.isdir(os.path.join(root, d)))
    batches = []
    if subs:
        for d in subs:
            idx = [j for j, g in enumerate(groups) if d in g[0].sheet]
            if not idx:
                print(f"※ フォルダ「{d}」に該当するシートがありません。スキップします", file=sys.stderr)
                continue
            mode = "照合" if any(w in groups[idx[0]][0].sheet for w in match_words) else "撮影順"
            batches.append((list_photos(os.path.join(root, d)), idx, mode))
    else:
        idx = [j for j, g in enumerate(groups) if any(w in g[0].sheet for w in match_words)]
        batches.append((list_photos(root), idx, "照合"))
    return batches


def write_report(path, files, groups, report):
    rows = []
    for no, g, p, sc, mode in report:
        src = g[0].ref or g[0].inslot
        ref = thumb_uri(files[src.target], 360)
        if p:
            im = load_photo(p)
            im.thumbnail((360, 360))
            buf = io.BytesIO()
            im.save(buf, "JPEG", quality=70)
            new = '<img src="data:image/jpeg;base64,%s">' % base64.b64encode(buf.getvalue()).decode()
        else:
            new = '<div class="none">未割当</div>'
        flag = "" if p else " warn"
        score = "" if sc is None else f"一致度 {int(sc)}"
        where = "<br>".join(f"{s.sheet} {s.row}行 {s.side}" for s in g)
        rows.append(f"""<tr class="r{flag}"><td class="no">{no}</td><td><img src="{ref}"></td><td>{new}</td>
<td><b>{g[0].caption}</b><br><small>{where}</small><br>{mode} {score}<br><small>{os.path.basename(p) if p else ""}</small></td></tr>""")
    html = f"""<!doctype html><meta charset="utf-8"><title>貼付結果</title>
<style>body{{font-family:sans-serif;margin:16px}}table{{border-collapse:collapse}}td{{border:1px solid #ccc;padding:4px;vertical-align:top}}
img{{width:240px}}.no{{font-weight:bold;font-size:20px;text-align:center}}.warn{{background:#fde2e2}}.none{{width:240px;height:180px;display:flex;align-items:center;justify-content:center;color:#c00}}</style>
<h1>貼付結果（左: 前回見本 / 右: 今回写真）</h1><p>赤い行は未割当・一致度が低いもの。確認してください。</p>
<table>{''.join(rows)}</table>"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)


def cmd_paste(a):
    book = Book.load(a.xlsx)
    orig = dict(book.files)  # 確認用 HTML で見本を表示するため
    slots = scan(book)
    groups = angle_groups(slots)
    match_words = [w for w in a.match.split(",") if w]
    assign = {}  # アングル番号 -> (写真パス, 一致度 or None, 方式)
    all_photos = []
    if a.map:
        for no, f in read_map(a.map).items():
            assign[no - 1] = (os.path.join(a.photos, f), None, "手動")
        all_photos = [os.path.join(a.photos, f) for f in read_map(a.map).values()]
    else:
        for photos, idx, mode in photo_batches(a.photos, groups, match_words):
            all_photos += photos
            if mode == "撮影順":
                for j, p in zip(idx, photos):
                    assign[j] = (p, None, mode)
                if len(photos) != len(idx):
                    print(f"※ {groups[idx[0]][0].sheet}: 写真 {len(photos)} 枚 / 枠 {len(idx)} アングル。"
                          "枚数が合いません。貼付結果を確認してください", file=sys.stderr)
            else:
                res, _ = auto_match(book, [groups[j] for j in idx], photos)
                for k, (i, sc) in res.items():
                    assign[idx[k]] = (photos[i], sc, mode)

    w = Writer(book)
    report = []
    for j, g in enumerate(groups):
        p, sc, mode = assign.get(j, (None, None, ""))
        if p and sc is not None and sc < a.min_score:
            report.append((j + 1, g, None, sc, mode + "（一致度不足のため貼付せず）"))
            continue
        if p:
            data, size = prepare_image(p)
            for s in g:
                if s.inslot is not None:
                    w.remove(s.drawing, s.inslot)
                w.add_image(s.drawing, data, LEFT_PHOTO_COL if s.side == "左" else RIGHT_PHOTO_COL,
                            s.row, size, f"写真 {j + 1}")
        report.append((j + 1, g, p, sc, mode))
    if a.drop_ref:
        for s in slots:
            if s.ref is not None and not s.is_map:
                w.remove(s.drawing, s.ref)
    w.finish()
    book.save(a.out)

    with open(a.out_map, "w", newline="", encoding="utf-8-sig") as f:
        wr = csv.writer(f)
        wr.writerow(["No", "キャプション", "貼付先", "写真ファイル", "一致度", "方式"])
        for no, g, p, sc, mode in report:
            wr.writerow([no, g[0].caption, " / ".join(f"{s.sheet} {s.row}行{s.side}" for s in g),
                         os.path.relpath(p, a.photos) if p else "", "" if sc is None else int(sc), mode])
    if a.report:
        write_report(a.report, orig, groups, report)
    used = {p for _, _, p, _, _ in report if p}
    import json
    print(json.dumps({
        "out": a.out,
        "angles": len(groups),
        "filled": len(used),
        "unfilled": [(no, g[0].sheet, g[0].caption) for no, g, p, _, _ in report if not p],
        "low_score": [(no, int(sc)) for no, _, p, sc, _ in report if sc is not None and sc < a.min_score],
        "unused_photos": [os.path.relpath(p, a.photos) for p in all_photos if p not in used],
    }, ensure_ascii=False, indent=1))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("checklist", help="撮影アングル一覧を作る")
    c.add_argument("xlsx")
    c.add_argument("--out-csv", default="撮影リスト.csv")
    c.add_argument("--json", help="サムネイル付き一覧(JSON)の出力先")
    c.set_defaults(func=cmd_checklist)
    p = sub.add_parser("paste", help="写真を貼り付ける")
    p.add_argument("xlsx")
    p.add_argument("photos")
    p.add_argument("-o", "--out", required=True)
    p.add_argument("--map", help="手動割当 CSV（No,写真ファイル 列）。指定時は画像照合しない")
    p.add_argument("--out-map", default="貼付結果.csv")
    p.add_argument("--min-score", type=int, default=25, help="これ未満の一致度は貼らずに報告")
    p.add_argument("--match", default="定期観測", help="画像照合するシート名のキーワード（カンマ区切り）。他は撮影順")
    p.add_argument("--report", default="貼付結果.html", help="見本と今回写真を並べた確認用 HTML")
    p.add_argument("--drop-ref", action="store_true", help="右側の見本写真を削除する")
    p.set_defaults(func=cmd_paste)
    a = ap.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
