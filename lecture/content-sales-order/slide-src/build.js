const pptxgen = require("pptxgenjs");
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const sharp = require("sharp");
const fa = require("react-icons/fa");
const { applyTheme } = require(process.env.SKILL + "/scripts/apply_theme.js");
const { sections, STEPS5 } = require("./content.js");

const FONT = "Yu Gothic";
const HEX = {
  dk1: "1F2328", lt1: "FFFFFF", dk2: "1E3A34", lt2: "EEF4F1",
  accent1: "F2A541", accent2: "C8553D", accent3: "2F6B5E", accent4: "8FB9A8",
  accent5: "6B7280", accent6: "FBE8C8", hlink: "2F6B5E", folHlink: "6B7280",
};
const THEME = { name: "Content Order", headFontFace: FONT, bodyFontFace: FONT, colors: HEX };

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.333 x 7.5
pres.theme = { headFontFace: FONT, bodyFontFace: FONT };
pres.title = "コンテンツ販売は思考の順番で９割決まる";
const C = pres.SchemeColor;

const W = 13.333, M = 0.6, CW = W - 2 * M;
const FOOT = "コンテンツ販売は思考の順番で９割決まる";

// ---------- icons ----------
const iconCache = {};
async function icon(name, hex) {
  const key = name + hex;
  if (iconCache[key]) return iconCache[key];
  const Comp = fa[name];
  if (!Comp) throw new Error("icon not found: " + name);
  const svg = ReactDOMServer.renderToStaticMarkup(React.createElement(Comp, { color: "#" + hex, size: 256 }));
  const buf = await sharp(Buffer.from(svg)).resize(256, 256).png().toBuffer();
  return (iconCache[key] = "image/png;base64," + buf.toString("base64"));
}

// ---------- layouts ----------
pres.defineSlideMaster({
  title: "DARK",
  background: { color: HEX.dk2 },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: M, y: 2.1, w: CW, h: 1.9, fontFace: FONT, fontSize: 40, bold: true, color: C.background1, valign: "middle", align: "left", margin: 0 }, text: "" } },
  ],
});
pres.defineSlideMaster({
  title: "CONTENT",
  background: { color: HEX.lt1 },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: M, y: 0.35, w: 10.4, h: 0.85, fontFace: FONT, fontSize: 28, bold: true, color: C.text2, valign: "middle", align: "left", margin: 0 }, text: "" } },
    { text: { text: FOOT, options: { x: M, y: 7.0, w: 8, h: 0.3, fontFace: FONT, fontSize: 10, color: C.accent5, margin: 0 } } },
  ],
  slideNumber: { x: 12.13, y: 7.0, w: 0.6, h: 0.3, fontFace: FONT, fontSize: 10, color: C.accent5, align: "right" },
});

// ---------- helpers ----------
function T(slide, text, o) {
  slide.addText(text, Object.assign({ isTextBox: true, fontFace: FONT, margin: 0, color: C.text1, valign: "top" }, o));
}
function pill(slide, text) {
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 11.35, y: 0.5, w: 1.38, h: 0.52, fill: { color: C.accent1 }, rectRadius: 0.26, objectName: "lecture tag" });
  T(slide, text, { x: 11.35, y: 0.5, w: 1.38, h: 0.52, fontSize: 14, bold: true, color: C.text2, align: "center", valign: "middle" });
}
function circle(slide, x, y, d, fill, objectName) {
  slide.addShape(pres.shapes.OVAL, { x, y, w: d, h: d, fill: { color: fill }, objectName: objectName || "circle" });
}
async function iconCircle(slide, name, x, y, d, fill, iconHex) {
  circle(slide, x, y, d, fill, "icon circle");
  const s = d * 0.52;
  slide.addImage({ data: await icon(name, iconHex), x: x + (d - s) / 2, y: y + (d - s) / 2, w: s, h: s, altText: "" });
}
function numCircle(slide, n, x, y, d, fill, color, fs) {
  circle(slide, x, y, d, fill, "number circle");
  T(slide, String(n), { x, y, w: d, h: d, fontSize: fs || 22, bold: true, color, align: "center", valign: "middle" });
}
function banner(slide, text, y) {
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: M, y, w: CW, h: 0.7, fill: { color: C.accent6 }, rectRadius: 0.12, objectName: "key message" });
  T(slide, text, { x: M + 0.3, y, w: CW - 0.6, h: 0.7, fontSize: 20, bold: true, color: C.text2, align: "center", valign: "middle" });
}
function bullets(items, fs, color) {
  return items.map((t, i) => ({ text: t, options: { bullet: true, breakLine: i < items.length - 1, paraSpaceAfter: 8, fontSize: fs, color } }));
}

// ---------- renderers ----------
const R = {};

R.cover = async (s, d) => {
  s.addText(d.title, { placeholder: "title" });
  T(s, d.sub, { x: M, y: 4.2, w: CW, h: 0.6, fontSize: 20, color: C.accent1 });
  // 5つの順番モチーフ
  for (let i = 0; i < 5; i++) {
    numCircle(s, i + 1, M + i * 0.75, 1.05, 0.5, i === 0 ? C.accent1 : C.accent3, i === 0 ? C.text2 : C.background1, 16);
  }
  T(s, "講師：", { x: M, y: 5.9, w: 6, h: 0.4, fontSize: 16, color: C.accent4 });
};

R.divider = async (s, d) => {
  T(s, d.no, { x: M, y: 0.7, w: 4, h: 0.9, fontSize: 40, bold: true, color: C.accent1 });
  s.addText(d.title, { placeholder: "title" });
  // the placeholder's own box is mid-slide; move title up a bit by using a separate box would break placeholder use
  T(s, d.meta, { x: M, y: 4.05, w: CW, h: 0.4, fontSize: 16, color: C.accent4 });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: M, y: 4.7, w: CW, h: 0.45 + 0.5 * d.goals.length, fill: { color: C.accent3 }, rectRadius: 0.12, objectName: "goals box" });
  T(s, d.goalsLabel || "この講のゴール", { x: M + 0.35, y: 4.85, w: 4, h: 0.4, fontSize: 16, bold: true, color: C.accent1 });
  T(s, bullets(d.goals, 18, C.background1), { x: M + 0.35, y: 5.3, w: CW - 0.7, h: 0.5 * d.goals.length });
};

R.summary = async (s, d) => {
  await iconCircle(s, "FaFlagCheckered", M, 0.8, 0.8, HEX.accent1, HEX.dk2);
  T(s, d.label, { x: M + 1.0, y: 0.8, w: 8, h: 0.8, fontSize: 20, bold: true, color: C.accent1, valign: "middle" });
  s.addText(d.big, { placeholder: "title" });
  T(s, d.sub, { x: M, y: 4.2, w: CW, h: 0.6, fontSize: 20, color: C.accent4 });
  if (d.next) {
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: M, y: 5.6, w: 7.2, h: 0.65, fill: { color: C.accent3 }, rectRadius: 0.12, objectName: "next lecture" });
    T(s, d.next + "　→", { x: M + 0.3, y: 5.6, w: 6.8, h: 0.65, fontSize: 16, bold: true, color: C.background1, valign: "middle" });
  }
};
R.closing = async (s, d) => {
  T(s, d.label, { x: M, y: 0.9, w: 8, h: 0.6, fontSize: 20, bold: true, color: C.accent1 });
  for (let i = 0; i < 5; i++) numCircle(s, i + 1, M + i * 0.75, 1.6, 0.5, C.accent1, C.text2, 16);
  s.addText(d.big, { placeholder: "title" });
  T(s, d.sub, { x: M, y: 4.3, w: CW, h: 1.2, fontSize: 22, color: C.background1 });
};

R.cards = async (s, d) => {
  const n = d.cards.length, gap = 0.35;
  const w = (CW - gap * (n - 1)) / n;
  const y0 = 1.6, h = d.bottom ? 4.15 : 5.1;
  for (let i = 0; i < n; i++) {
    const c = d.cards[i], x = M + i * (w + gap);
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: y0, w, h, fill: { color: C.background2 }, rectRadius: 0.15, objectName: "card" });
    await iconCircle(s, c.icon, x + 0.35, y0 + 0.35, 0.85, HEX.dk2, HEX.lt1);
    T(s, c.head, { x: x + 0.35, y: y0 + 1.4, w: w - 0.7, h: 1.2, fontSize: n > 3 ? 22 : 24, bold: true, color: C.text2 });
    T(s, c.text, { x: x + 0.35, y: y0 + 2.7, w: w - 0.7, h: h - 2.9, fontSize: 18 });
  }
  if (d.bottom) banner(s, d.bottom, 6.0);
};

R.statement = async (s, d) => {
  await iconCircle(s, d.icon, (W - 1.1) / 2, 1.55, 1.1, HEX.accent1, HEX.dk2);
  T(s, d.big, { x: M, y: 2.9, w: CW, h: 1.9, fontSize: 36, bold: true, color: C.text2, align: "center", valign: "middle" });
  if (d.sub) T(s, d.sub, { x: M, y: 5.05, w: CW, h: 0.9, fontSize: 20, color: C.accent5, align: "center", valign: "middle" });
};

R.question = async (s, d) => {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: M, y: 1.6, w: CW, h: 4.9, fill: { color: C.background2 }, rectRadius: 0.2, objectName: "question panel" });
  await iconCircle(s, "FaRegComments", M + 0.6, 2.0, 1.2, HEX.dk2, HEX.lt1);
  T(s, "受講者への問いかけ", { x: M + 2.1, y: 2.0, w: 6, h: 1.2, fontSize: 20, bold: true, color: C.accent3, valign: "middle" });
  T(s, d.q, { x: M + 0.6, y: 3.45, w: CW - 1.2, h: 1.8, fontSize: 32, bold: true, color: C.text2, valign: "middle" });
  T(s, d.hint, { x: M + 0.6, y: 5.45, w: CW - 1.2, h: 0.6, fontSize: 18, color: C.accent5 });
};

R.compare = async (s, d) => {
  const pw = 5.55, y0 = 1.6, ph = 5.0;
  const sides = [[d.left, M, "L"], [d.right, W - M - pw, "R"]];
  for (const [p, x, side] of sides) {
    const right = side === "R";
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: y0, w: pw, h: ph, fill: { color: right ? C.accent6 : C.background2 }, rectRadius: 0.15, objectName: right ? "right panel" : "left panel" });
    let ic = p.icon;
    if (d.mode === "ng-ok") ic = right ? "FaRegCircle" : "FaTimes";
    const fill = d.mode === "ng-ok" ? (right ? HEX.accent3 : HEX.accent2) : (right ? HEX.accent1 : HEX.dk2);
    const ink = d.mode !== "ng-ok" && right ? HEX.dk2 : HEX.lt1;
    await iconCircle(s, ic, x + 0.4, y0 + 0.4, 0.8, fill, ink);
    T(s, p.label, { x: x + 1.4, y: y0 + 0.4, w: pw - 1.8, h: 0.8, fontSize: 18, bold: true, color: C.accent5, valign: "middle" });
    T(s, p.head, { x: x + 0.4, y: y0 + 1.45, w: pw - 0.8, h: 1.35, fontSize: 28, bold: true, color: C.text2, valign: "middle" });
    T(s, bullets(p.items, 18, C.text1), { x: x + 0.4, y: y0 + 3.0, w: pw - 0.8, h: ph - 3.2 });
  }
  s.addShape(pres.shapes.RIGHT_ARROW, { x: W / 2 - 0.35, y: y0 + ph / 2 - 0.35, w: 0.7, h: 0.7, fill: { color: C.accent1 }, objectName: "arrow" });
};

R.cause = async (s, d) => {
  const sw = 4.1, cw = 3.1, y0 = 1.6, h = 5.0;
  const xs = [M, (W - cw) / 2, W - M - sw];
  // left & right lists
  for (const [k, x] of [["left", xs[0]], ["right", xs[2]]]) {
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: y0, w: sw, h, fill: { color: C.background2 }, rectRadius: 0.15, objectName: k + " list" });
    T(s, d[k + "Head"], { x: x + 0.35, y: y0 + 0.35, w: sw - 0.7, h: 0.6, fontSize: 18, bold: true, color: C.accent3 });
    T(s, bullets(d[k], 17, C.text1), { x: x + 0.35, y: y0 + 1.15, w: sw - 0.5, h: h - 1.4 });
  }
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: xs[1], y: y0, w: cw, h, fill: { color: C.text2 }, rectRadius: 0.15, objectName: "center" });
  await iconCircle(s, "FaSearch", xs[1] + (cw - 0.9) / 2, y0 + 0.5, 0.9, HEX.accent1, HEX.dk2);
  T(s, d.center, { x: xs[1] + 0.3, y: y0 + 1.6, w: cw - 0.6, h: 3.0, fontSize: 28, bold: true, color: C.background1, align: "center", valign: "middle" });
  for (const ax of [xs[0] + sw + (xs[1] - xs[0] - sw) / 2 - 0.2, xs[1] + cw + (xs[2] - xs[1] - cw) / 2 - 0.2]) {
    s.addShape(pres.shapes.RIGHT_ARROW, { x: ax, y: y0 + h / 2 - 0.2, w: 0.4, h: 0.4, fill: { color: C.accent1 }, objectName: "arrow" });
  }
};

R.flow = async (s, d) => {
  const n = d.steps.length, colW = CW / n, cd = n > 4 ? 0.95 : 1.1, cy = 1.85;
  for (let i = 0; i < n - 1; i++) {
    const x1 = M + colW * i + colW / 2 + cd / 2 + 0.1, x2 = M + colW * (i + 1) + colW / 2 - cd / 2 - 0.1;
    s.addShape(pres.shapes.LINE, { x: x1, y: cy + cd / 2, w: x2 - x1, h: 0, line: { color: HEX.accent4, width: 3, endArrowType: "triangle" }, objectName: "connector" });
  }
  for (let i = 0; i < n; i++) {
    const st = d.steps[i], cx = M + colW * i;
    const hi = d.hi === i, last = d.warn && i === n - 1;
    const fill = hi ? C.accent1 : last ? C.accent2 : C.text2;
    numCircle(s, i + 1, cx + (colW - cd) / 2, cy, cd, fill, hi ? C.text2 : C.background1, 26);
    T(s, st.head, { x: cx + 0.12, y: cy + cd + 0.3, w: colW - 0.24, h: 1.0, fontSize: n > 4 ? 16 : n > 3 ? 18 : 20, bold: true, color: hi ? C.accent2 : C.text2, align: "center" });
    T(s, st.text, { x: cx + 0.12, y: cy + cd + 1.35, w: colW - 0.24, h: 1.1, fontSize: 15, color: C.text1, align: "center" });
  }
  if (d.loop) T(s, "↺ 1 に戻る（終わらないループ）", { x: M, y: 5.25, w: CW, h: 0.4, fontSize: 15, color: C.accent2, align: "right", bold: true });
  if (d.bottom) banner(s, d.bottom, 6.0);
};

R.rows = async (s, d) => {
  const n = d.rows.length, gap = 0.22, y0 = 1.6;
  const rh = Math.min(1.3, (5.1 - gap * (n - 1)) / n);
  for (let i = 0; i < n; i++) {
    const r = d.rows[i], y = y0 + i * (rh + gap);
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: M, y, w: CW, h: rh, fill: { color: C.background2 }, rectRadius: 0.12, objectName: "row" });
    const cd = Math.min(0.8, rh - 0.3);
    if (d.icons) await iconCircle(s, d.icons[i], M + 0.3, y + (rh - cd) / 2, cd, HEX.dk2, HEX.lt1);
    else numCircle(s, i + 1, M + 0.3, y + (rh - cd) / 2, cd, C.text2, C.background1, 22);
    if (r.text) {
      T(s, r.head, { x: M + 1.4, y, w: 5.6, h: rh, fontSize: 21, bold: true, color: C.text2, valign: "middle" });
      T(s, r.text, { x: M + 7.2, y, w: CW - 7.5, h: rh, fontSize: 17, valign: "middle" });
    } else {
      T(s, r.head, { x: M + 1.4, y, w: CW - 1.7, h: rh, fontSize: 24, bold: true, color: C.text2, valign: "middle" });
    }
  }
};

R.focus = async (s, d) => {
  // 進捗モチーフ（5ステップ）
  const pw = CW / 5;
  for (let i = 0; i < 5; i++) {
    const on = i === d.idx, x = M + pw * i;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x + 0.05, y: 1.5, w: pw - 0.1, h: 0.6, fill: { color: on ? C.accent1 : C.background2 }, rectRadius: 0.3, objectName: "progress" });
    T(s, `${i + 1}  ${STEPS5[i]}`, { x: x + 0.05, y: 1.5, w: pw - 0.1, h: 0.6, fontSize: 13, bold: on, color: on ? C.text2 : C.accent5, align: "center", valign: "middle" });
  }
  numCircle(s, d.idx + 1, M, 2.6, 1.6, C.text2, C.background1, 54);
  T(s, d.head, { x: M + 2.0, y: 2.55, w: CW - 2.0, h: 0.7, fontSize: 24, bold: true, color: C.text2, valign: "middle" });
  T(s, bullets(d.items, 20, C.text1), { x: M + 2.0, y: 3.35, w: CW - 2.0, h: 1.9 });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: M, y: 5.45, w: CW, h: 1.2, fill: { color: C.accent6 }, rectRadius: 0.12, objectName: "point" });
  await iconCircle(s, "FaLightbulb", M + 0.3, 5.7, 0.7, HEX.accent1, HEX.dk2);
  T(s, d.point, { x: M + 1.25, y: 5.45, w: CW - 1.55, h: 1.2, fontSize: 18, bold: true, color: C.text2, valign: "middle" });
};

R.breakdown = async (s, d) => {
  s.addChart(pres.charts.DOUGHNUT, [{ name: "100点の内訳", labels: d.parts.map(p => p.label), values: d.parts.map(p => p.pts) }], {
    x: M + 0.2, y: 1.55, w: 4.1, h: 4.1, holeSize: 55, chartColors: [HEX.dk2, HEX.accent1, HEX.accent2],
    showLegend: false, showValue: false, showPercent: false, showTitle: false, dataBorder: { pt: 2, color: "FFFFFF" },
  });
  T(s, "100点", { x: M + 0.2, y: 3.2, w: 4.1, h: 0.8, fontSize: 30, bold: true, color: C.text2, align: "center", valign: "middle" });
  const cols = [C.text2, C.accent1, C.accent2];
  for (let i = 0; i < d.parts.length; i++) {
    const p = d.parts[i], y = 1.7 + i * 1.35, x = 5.9;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w: W - M - x, h: 1.15, fill: { color: C.background2 }, rectRadius: 0.12, objectName: "part" });
    circle(s, x + 0.3, y + 0.35, 0.45, cols[i], "swatch");
    T(s, p.label, { x: x + 1.0, y, w: 2.4, h: 1.15, fontSize: 21, bold: true, color: C.text2, valign: "middle" });
    T(s, p.pts + "点", { x: x + 3.4, y, w: 1.1, h: 1.15, fontSize: 24, bold: true, color: C.text2, valign: "middle" });
    T(s, p.when, { x: x + 4.5, y, w: W - M - x - 4.7, h: 1.15, fontSize: 16, color: C.accent5, valign: "middle" });
  }
  banner(s, "出す前に届くのは、おおよそ60点まで", 5.85);
  T(s, d.note, { x: M, y: 6.6, w: CW, h: 0.3, fontSize: 11, color: C.accent5 });
};

R.work = async (s, d) => {
  circle(s, M + 0.2, 1.8, 3.4, C.accent1, "timer");
  T(s, d.min, { x: M + 0.2, y: 2.6, w: 3.4, h: 1.1, fontSize: 54, bold: true, color: C.text2, align: "center", valign: "middle" });
  T(s, "ワーク", { x: M + 0.2, y: 3.7, w: 3.4, h: 0.6, fontSize: 22, bold: true, color: C.text2, align: "center", valign: "middle" });
  const x = 4.9, n = d.steps.length, rh = Math.min(1.1, (5.0 - 0.2 * (n - 1)) / n);
  for (let i = 0; i < n; i++) {
    const y = 1.65 + i * (rh + 0.2);
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w: W - M - x, h: rh, fill: { color: C.background2 }, rectRadius: 0.12, objectName: "work step" });
    numCircle(s, i + 1, x + 0.25, y + (rh - 0.6) / 2, 0.6, C.text2, C.background1, 18);
    T(s, d.steps[i], { x: x + 1.1, y, w: W - M - x - 1.3, h: rh, fontSize: 19, color: C.text2, bold: true, valign: "middle" });
  }
};

R.check = async (s, d) => {
  const cols = d.cols || 1, per = Math.ceil(d.items.length / cols);
  const cw = (CW - 0.35 * (cols - 1)) / cols, rh = cols > 1 ? 1.15 : 1.25;
  for (let i = 0; i < d.items.length; i++) {
    const c = Math.floor(i / per), r = i % per;
    const x = M + c * (cw + 0.35), y = 1.6 + r * (rh + 0.2);
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w: cw, h: rh, fill: { color: C.background2 }, rectRadius: 0.12, objectName: "check item" });
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x + 0.3, y: y + (rh - 0.55) / 2, w: 0.55, h: 0.55, fill: { color: C.background1 }, line: { color: HEX.dk2, width: 2 }, rectRadius: 0.08, objectName: "checkbox" });
    T(s, d.items[i], { x: x + 1.1, y, w: cw - 1.3, h: rh, fontSize: cols > 1 ? 18 : 21, bold: true, color: C.text2, valign: "middle" });
  }
  if (d.bottom) banner(s, d.bottom, 6.0);
};

function tableOpts(d, rowH) {
  return { x: M, y: 1.6, w: CW, colW: d.colW, fontFace: FONT, fontSize: 16, color: HEX.dk1, valign: "middle",
    border: { type: "solid", pt: 1, color: "D5DFDA" }, rowH, margin: [0.06, 0.15, 0.06, 0.15] };
}
function tableRows(d, alt) {
  const head = d.head.map(h => ({ text: h, options: { bold: true, color: HEX.lt1, fill: { color: HEX.dk2 } } }));
  const rows = d.rows.map((r, i) => r.map((c, j) => ({ text: c, options: { fill: { color: alt && i % 2 ? HEX.lt2 : HEX.lt1 }, bold: j === 0, color: j === 0 ? HEX.dk2 : HEX.dk1 } })));
  return [head, ...rows];
}
R.table = async (s, d) => {
  const n = d.rows.length;
  const rh = Math.min(0.8, 5.0 / (n + 1));
  s.addTable(tableRows(d, true), tableOpts(d, rh));
};
R.sheet = async (s, d) => {
  const n = d.rows.length;
  const rh = Math.min(1.15, (d.foot ? 4.6 : 5.0) / (n + 0.5));
  const rows = tableRows(d, false);
  const o = tableOpts(d, [0.55, ...Array(n).fill(rh)]);
  s.addTable(rows, o);
  if (d.foot) T(s, d.foot, { x: M, y: 6.45, w: CW, h: 0.35, fontSize: 13, color: C.accent5 });
};

R.qa = async (s, d) => {
  const n = d.rows.length, gap = 0.25, rh = (5.1 - gap * (n - 1)) / n;
  for (let i = 0; i < n; i++) {
    const r = d.rows[i], y = 1.6 + i * (rh + gap);
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: M, y, w: CW, h: rh, fill: { color: C.background2 }, rectRadius: 0.12, objectName: "qa" });
    numCircle(s, "Q", M + 0.3, y + 0.3, 0.6, C.accent1, C.text2, 18);
    T(s, r.q, { x: M + 1.15, y: y + 0.25, w: CW - 1.4, h: 0.7, fontSize: 20, bold: true, color: C.text2, valign: "middle" });
    T(s, r.a, { x: M + 1.15, y: y + 0.95, w: CW - 1.4, h: rh - 1.1, fontSize: 16 });
  }
};

// ---------- build ----------
const DARK = new Set(["cover", "divider", "summary", "closing"]);
(async () => {
  for (const sec of sections) {
    pres.addSection({ title: sec.title });
    for (const d of sec.slides) {
      const dark = DARK.has(d.t);
      const s = pres.addSlide({ masterName: dark ? "DARK" : "CONTENT", sectionTitle: sec.title });
      if (!dark) {
        s.addText(d.title, { placeholder: "title" });
        if (sec.title.startsWith("第")) pill(s, sec.title);
      }
      if (!R[d.t]) throw new Error("no renderer " + d.t);
      await R[d.t](s, d);
      if (d.n) s.addNotes(d.n);
    }
  }
  const out = process.argv[2] || "deck.pptx";
  await pres.writeFile({ fileName: out });
  await applyTheme(out, THEME);
  console.log("wrote", out);
})().catch(e => { console.error(e); process.exit(1); });
