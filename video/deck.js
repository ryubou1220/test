const pptxgen = require("pptxgenjs");
const fs = require("fs");
const SLIDES = JSON.parse(fs.readFileSync(__dirname + "/slides.json", "utf8"));

const pres = new pptxgen();
pres.layout = "LAYOUT_16x9"; // 10 x 5.625 in
pres.title = "消去方式コンテンツ販売 ～時間の壁消去編～";
pres.theme = { headFontFace: "Meiryo", bodyFontFace: "Meiryo" };

const BG = "101B30", BG2 = "182844", CARD = "203456", ACCENT = "FFB03B", TEXT = "F0F4FA", MUTED = "A0B0C8", RED = "FF6B6B";

pres.defineSlideMaster({
  title: "DARK",
  background: { color: BG },
  objects: [
    { rect: { x: 0, y: 5.565, w: 10, h: 0.06, fill: { color: BG2 } } },
  ],
  slideNumber: { x: 9.2, y: 5.2, w: 0.6, h: 0.3, color: MUTED, fontSize: 10, align: "right" },
});

const T = (o) => Object.assign({ isTextBox: true, margin: 0, fontFace: "Meiryo", color: TEXT, valign: "middle" }, o);

function decor(s) {
  s.addShape(pres.shapes.RIGHT_TRIANGLE, { x: 7.3, y: 0, w: 2.7, h: 2.7, fill: { color: BG2 }, rotate: 180, line: { type: "none" } });
}
function label(s, text) {
  const w = 0.35 + text.length * 0.17;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.5, y: 0.35, w, h: 0.32, rectRadius: 0.16, fill: { color: ACCENT }, line: { type: "none" } });
  s.addText(text, T({ x: 0.5, y: 0.35, w, h: 0.32, fontSize: 11, bold: true, color: BG, align: "center" }));
}
function title(s, text, size = 26) {
  const lines = text.split("\n").length;
  const h = lines * size * 1.45 / 72;
  s.addText(text.replace(/\n/g, "\n"), T({ x: 0.5, y: 0.8, w: 8.6, h, fontSize: size, bold: true, valign: "top" }));
  return 0.8 + h + 0.3;
}
function progress(s, i, n) {
  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 5.565, w: 10 * (i + 1) / n, h: 0.06, fill: { color: ACCENT }, line: { type: "none" } });
}
function card(s, x, y, w, h, color = CARD) {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.08, fill: { color }, line: { type: "none" } });
}

const N = SLIDES.length;
SLIDES.forEach((d0, i) => {
  let d = d0;
  const s = pres.addSlide({ masterName: "DARK" });
  decor(s);
  const pts = d.points;
  if (d.kind === "agenda") d = Object.assign({}, d, { title: "全体の流れ" });
  if (d.kind === "cover") {
    s.addText("電子書籍 解説", T({ x: 0, y: 1.0, w: 10, h: 0.4, fontSize: 16, bold: true, color: ACCENT, align: "center" }));
    const [t1, t2] = d.title.split("\n");
    s.addText(t1, T({ x: 0, y: 1.55, w: 10, h: 0.8, fontSize: 40, bold: true, align: "center" }));
    s.addText(t2, T({ x: 0, y: 2.35, w: 10, h: 0.55, fontSize: 26, bold: true, align: "center" }));
    s.addText(pts.join("\n"), T({ x: 0, y: 3.3, w: 10, h: 0.9, fontSize: 18, color: MUTED, align: "center", lineSpacingMultiple: 1.3 }));
  } else {
    label(s, d.label);
    const y0 = title(s, d.title, d.kind === "statement" ? 30 : 26);
    if (d.kind === "agenda") {
      pts.forEach((p, k) => {
        const x = 0.5 + (k % 2) * 4.55, y = y0 + Math.floor(k / 2) * 0.72;
        card(s, x, y, 4.35, 0.58);
        s.addText(p, T({ x: x + 0.2, y, w: 4.0, h: 0.58, fontSize: 15 }));
      });
    } else if (d.kind === "statement") {
      pts.forEach((p, k) => {
        const y = y0 + 0.1 + k * 0.82, last = k === pts.length - 1;
        card(s, 0.5, y, 9.0, 0.66);
        s.addShape(pres.shapes.OVAL, { x: 0.75, y: y + 0.22, w: 0.22, h: 0.22, fill: { color: last ? ACCENT : MUTED }, line: { type: "none" } });
        s.addText(p, T({ x: 1.2, y, w: 8.1, h: 0.66, fontSize: 20, bold: last, color: last ? ACCENT : TEXT }));
      });
    } else if (d.kind === "bullets") {
      const h = 0.62, gap = 0.16;
      pts.forEach((p, k) => {
        const y = y0 + k * (h + gap);
        card(s, 0.5, y, 9.0, h);
        s.addShape(pres.shapes.OVAL, { x: 0.75, y: y + h / 2 - 0.08, w: 0.16, h: 0.16, fill: { color: ACCENT }, line: { type: "none" } });
        s.addText(p, T({ x: 1.1, y, w: 8.2, h, fontSize: 16 }));
      });
    } else if (d.kind === "grid") {
      const cw = 2.85, ch = 1.6, gx = 0.225, gy = 0.2;
      pts.forEach((p, k) => {
        const [name, desc] = p.split("|");
        const x = 0.5 + (k % 3) * (cw + gx), y = y0 + Math.floor(k / 3) * (ch + gy);
        card(s, x, y, cw, ch);
        s.addShape(pres.shapes.OVAL, { x: x + 0.2, y: y + 0.2, w: 0.45, h: 0.45, fill: { color: RED }, line: { type: "none" } });
        s.addText(String(k + 1), T({ x: x + 0.2, y: y + 0.2, w: 0.45, h: 0.45, fontSize: 18, bold: true, color: BG, align: "center" }));
        s.addText([{ text: name, options: { fontSize: 17, bold: true, breakLine: true } }, { text: "ブレーキ", options: { fontSize: 10, color: MUTED } }],
          T({ x: x + 0.8, y: y + 0.15, w: cw - 0.95, h: 0.6 }));
        s.addText(desc, T({ x: x + 0.2, y: y + 0.8, w: cw - 0.4, h: 0.7, fontSize: 12, color: MUTED, valign: "top" }));
      });
    } else if (d.kind === "twocol") {
      const avail = 5.25 - y0, gap = 0.16, h = (avail - gap * (pts.length - 1));
      const rh = Math.min(1.05, h / pts.length);
      pts.forEach((p, k) => {
        const [name, desc] = p.split("|");
        const y = y0 + k * (rh + gap);
        card(s, 0.5, y, 9.0, rh);
        card(s, 0.5, y, 2.4, rh, BG2);
        s.addText(name, T({ x: 0.7, y, w: 2.1, h: rh, fontSize: 16, bold: true, color: ACCENT }));
        s.addText(desc, T({ x: 3.1, y, w: 6.2, h: rh, fontSize: 14 }));
      });
    } else if (d.kind === "steps" || d.kind === "pillars") {
      const n = pts.length, gap = 0.4, cw = (9.0 - gap * (n - 1)) / n, ch = Math.min(2.5, 5.2 - y0);
      pts.forEach((p, k) => {
        const [name, desc] = p.split("|");
        const x = 0.5 + k * (cw + gap);
        card(s, x, y0, cw, ch);
        const lab = d.kind === "steps" ? `STEP ${k + 1}` : `柱 ${k + 1}`;
        s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x + 0.25, y: y0 + 0.25, w: 1.0, h: 0.32, rectRadius: 0.16, fill: { color: ACCENT }, line: { type: "none" } });
        s.addText(lab, T({ x: x + 0.25, y: y0 + 0.25, w: 1.0, h: 0.32, fontSize: 11, bold: true, color: BG, align: "center" }));
        s.addText(name, T({ x: x + 0.2, y: y0 + 0.75, w: cw - 0.4, h: 0.75, fontSize: 15, bold: true, valign: "top" }));
        s.addText(desc, T({ x: x + 0.2, y: y0 + 1.5, w: cw - 0.4, h: ch - 1.65, fontSize: 14, color: MUTED, valign: "top" }));
        if (k < n - 1) s.addShape(pres.shapes.ISOSCELES_TRIANGLE, { x: x + cw + gap / 2 - 0.09, y: y0 + ch / 2 - 0.12, w: 0.18, h: 0.24, rotate: 90, fill: { color: ACCENT }, line: { type: "none" } });
      });
    }
  }
  progress(s, i, N);
  s.addNotes(d.narration.join("\n"));
});

pres.writeFile({ fileName: __dirname + "/消去方式コンテンツ販売_スライド.pptx" }).then(f => console.log(f));
