// 原稿データ(content.js)から Word ファイルを生成する
// 使い方: node build.js [出力パス]
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, AlignmentType, HeadingLevel,
  PageBreak, Footer, PageNumber, Table, TableRow, TableCell, WidthType,
  BorderStyle, ShadingType, LevelFormat,
} = require("docx");
const book = require("./content");

const FONT = "Meiryo";
const ACCENT = "C0504D";
const SUB = "7F7F7F";
const out = process.argv[2] || path.join(__dirname, "人生を変える64の習慣リスト.docx");

const run = (text, o = {}) => new TextRun({ text, font: { ascii: FONT, eastAsia: FONT, hAnsi: FONT }, ...o });
const para = (text, o = {}, r = {}) => new Paragraph({ children: [run(text, r)], spacing: { after: 120, line: 360 }, ...o });
const lines = (text, o, r) => text.split("\n").map((t) => para(t, o, r));
const bullet = (text) => new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [run(text)], spacing: { after: 60, line: 340 } });
const check = (text) => new Paragraph({ children: [run("✓ ", { color: ACCENT, bold: true }), run(text)], indent: { left: 360 }, spacing: { after: 60 } });
const pageBreak = () => new Paragraph({ children: [new PageBreak()] });
const label = (text) => new Paragraph({ children: [run(text, { bold: true, color: ACCENT })], spacing: { before: 120, after: 60 } });
const box = (children, fill) => {
  const border = { style: BorderStyle.SINGLE, size: 6, color: "D9D9D9" };
  return new Table({
    width: { size: 9000, type: WidthType.DXA }, columnWidths: [9000],
    rows: [new TableRow({ children: [new TableCell({
      width: { size: 9000, type: WidthType.DXA },
      shading: { type: ShadingType.CLEAR, fill, color: "auto" },
      borders: { top: border, bottom: border, left: border, right: border },
      margins: { top: 120, bottom: 120, left: 200, right: 200 },
      children,
    })] })],
  });
};
const spacer = () => new Paragraph({ children: [], spacing: { after: 120 } });

const children = [];

// 表紙
children.push(
  new Paragraph({ children: [], spacing: { before: 3600 } }),
  new Paragraph({ alignment: AlignmentType.CENTER, children: [run(book.title, { size: 52, bold: true })], spacing: { after: 360 } }),
  new Paragraph({ alignment: AlignmentType.CENTER, children: [run(`〜${book.subtitle}〜`, { size: 28, color: SUB })], spacing: { after: 2400 } }),
  new Paragraph({ alignment: AlignmentType.CENTER, children: [run(book.author, { size: 32, bold: true })] }),
);

// 目次
children.push(
  new Paragraph({ heading: HeadingLevel.HEADING_1, children: [run("目次")] }),
);
children.push(para(book.prologue.title, { spacing: { after: 160 } }, { bold: true }));
{
  let k = 0;
  book.chapters.forEach((ch) => {
    children.push(para(ch.title, { spacing: { before: 120, after: 40 } }, { bold: true }));
    children.push(para(ch.habits.map((h) => `${String(++k).padStart(2, "0")} ${h.t}`).join("　／　"), { indent: { left: 360 }, spacing: { after: 80, line: 300 } }, { size: 17, color: SUB }));
  });
}
children.push(para(book.epilogue.title, { spacing: { before: 160 } }, { bold: true }), para("付録　64の習慣チェックシート", {}, { bold: true }));

// はじめに
const pr = book.prologue;
children.push(new Paragraph({ heading: HeadingLevel.HEADING_1, children: [run(pr.title)] }));
pr.body.forEach((t) => children.push(...lines(t)));
children.push(spacer(), box([label("この本の使い方"), ...pr.howto.map(bullet)], "F2F2F2"), spacer());
children.push(para(pr.closing, {}, { bold: true }));

// 各章
let n = 0;
const sheet = [];
book.chapters.forEach((ch) => {
  children.push(new Paragraph({ heading: HeadingLevel.HEADING_1, children: [run(ch.title)] }));
  ch.lead.forEach((t) => children.push(...lines(t)));
  if (ch.note) children.push(para(ch.note, {}, { size: 18, color: SUB }));
  const names = [];
  ch.habits.forEach((h) => {
    n += 1;
    const no = String(n).padStart(2, "0");
    names.push(h.t);
    sheet.push({ no, t: h.t, ch: ch.title });
    children.push(new Paragraph({
      heading: HeadingLevel.HEADING_2,
      children: [run(`習慣${no}　`, { color: ACCENT }), run(h.t)],
    }));
    h.b.forEach((t) => children.push(...lines(t)));
    children.push(box([label("📌 やってみよう"), ...h.d.map(bullet)], "FFF8F0"));
    children.push(new Paragraph({
      children: [run("💡 ポイント　", { bold: true, color: ACCENT }), run(h.p, { bold: true })],
      spacing: { before: 160, after: 240 },
    }));
  });
  children.push(new Paragraph({ heading: HeadingLevel.HEADING_3, children: [run("この章のまとめ")] }));
  names.forEach((t) => children.push(check(t)));
});
if (n !== 64) throw new Error(`習慣の数が64ではありません: ${n}`);

// おわりに
const ep = book.epilogue;
children.push(new Paragraph({ heading: HeadingLevel.HEADING_1, children: [run(ep.title)] }));
ep.body.forEach((t, i) => {
  const strong = t === "やるか、やらないか。";
  children.push(...lines(t, strong ? { alignment: AlignmentType.CENTER, spacing: { before: 240, after: 240 } } : {}, strong ? { size: 32, bold: true } : {}));
});
children.push(spacer(), box([label(ep.steps.title), ...ep.steps.items.map(bullet)], "FFF8F0"), spacer());
ep.closing.forEach((t) => children.push(para(t, {}, { bold: true })));
children.push(new Paragraph({ alignment: AlignmentType.RIGHT, children: [run(ep.sign, { bold: true, size: 26 })], spacing: { before: 240 } }));

// 付録: チェックシート
children.push(new Paragraph({ heading: HeadingLevel.HEADING_1, children: [run("付録　64の習慣チェックシート")] }));
children.push(para("できた習慣に✓を入れましょう。1週目・2週目…と続けて記録すると、自分の変化が目に見えてわかります。"));
const W = [900, 5100, 750, 750, 750, 750];
const cb = { style: BorderStyle.SINGLE, size: 4, color: "BFBFBF" };
const cell = (text, w, o = {}) => new TableCell({
  width: { size: w, type: WidthType.DXA },
  borders: { top: cb, bottom: cb, left: cb, right: cb },
  margins: { top: 40, bottom: 40, left: 80, right: 80 },
  shading: o.fill ? { type: ShadingType.CLEAR, fill: o.fill, color: "auto" } : undefined,
  columnSpan: o.span,
  children: [new Paragraph({ alignment: o.center ? AlignmentType.CENTER : AlignmentType.LEFT, children: [run(text, { size: 18, bold: !!o.bold, color: o.color })] })],
});
const rows = [new TableRow({ tableHeader: true, children: [
  cell("No.", W[0], { fill: "F2DCDB", bold: true, center: true }),
  cell("習慣", W[1], { fill: "F2DCDB", bold: true }),
  ...["1週目", "2週目", "3週目", "4週目"].map((t, i) => cell(t, W[i + 2], { fill: "F2DCDB", bold: true, center: true })),
] })];
let cur = "";
sheet.forEach((s) => {
  if (s.ch !== cur) {
    cur = s.ch;
    rows.push(new TableRow({ children: [cell(s.ch, 9000, { span: 6, fill: "F2F2F2", bold: true })] }));
  }
  rows.push(new TableRow({ children: [
    cell(s.no, W[0], { center: true }), cell(s.t, W[1]),
    ...[2, 3, 4, 5].map((i) => cell("□", W[i], { center: true, color: SUB })),
  ] }));
});
children.push(new Table({ width: { size: 9000, type: WidthType.DXA }, columnWidths: W, rows }));

const doc = new Document({
  creator: book.author,
  title: book.title,
  styles: {
    default: { document: { run: { font: { ascii: FONT, eastAsia: FONT, hAnsi: FONT }, size: 21 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 34, bold: true, font: { ascii: FONT, eastAsia: FONT, hAnsi: FONT } },
        paragraph: { spacing: { before: 240, after: 360 }, outlineLevel: 0, pageBreakBefore: true,
          border: { bottom: { style: BorderStyle.SINGLE, size: 12, color: ACCENT, space: 6 } } } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 27, bold: true, font: { ascii: FONT, eastAsia: FONT, hAnsi: FONT } },
        paragraph: { spacing: { before: 480, after: 180 }, outlineLevel: 1, keepNext: true } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 24, bold: true, color: ACCENT, font: { ascii: FONT, eastAsia: FONT, hAnsi: FONT } },
        paragraph: { spacing: { before: 360, after: 120 }, outlineLevel: 2, keepNext: true } },
    ],
  },
  numbering: { config: [{ reference: "bullets", levels: [{ level: 0, format: LevelFormat.BULLET, text: "・", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 420, hanging: 300 } } } }] }] },
  sections: [{
    properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1440, bottom: 1440, left: 1440, right: 1440 } }, titlePage: true },
    footers: {
      default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ children: [PageNumber.CURRENT], size: 18, color: SUB })] })] }),
      first: new Footer({ children: [] }),
    },
    children,
  }],
});

Packer.toBuffer(doc).then((buf) => { fs.writeFileSync(out, buf); console.log(`wrote ${out} (habits: ${n})`); });
