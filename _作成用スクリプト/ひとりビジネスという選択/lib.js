// docx helpers for 「ひとりビジネスという選択」
const fs = require("fs");
const d = require("docx");
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType, ShadingType, BorderStyle,
  AlignmentType, Footer, PageNumber, LevelFormat, TableLayoutType, VerticalAlign, HeadingLevel } = d;

const FONT = "Meiryo UI";
const RED = "B00000", TEXT = "262626", GRAY = "595959", PINK = "FBEAEA", LINE = "D9D9D9";
const CW = 9638; // A4 content width (twips) with 1134 margins
const SZ = 24;   // 12pt body

function runs(content, o = {}) {
  const arr = typeof content === "string" ? [[content, {}]] : content;
  return arr.map(([t, r = {}]) => new TextRun({ text: t, font: FONT, size: r.size || o.size || SZ, bold: r.bold ?? o.bold,
    color: r.color || o.color || TEXT, underline: r.underline }));
}
const P = (content, o = {}) => new Paragraph({ children: runs(content, o), alignment: o.align === "right" ? AlignmentType.RIGHT : o.align === "center" ? AlignmentType.CENTER : undefined,
  spacing: { before: o.before || 0, after: o.after ?? 160, line: o.line || 400 }, keepNext: o.keepNext, pageBreakBefore: o.pageBreak });
// text with \n line breaks; blank line => new paragraph
function paras(text, o = {}) {
  return text.split(/\n\n+/).map((blk) => new Paragraph({ spacing: { after: o.after ?? 200, line: 400 },
    children: blk.split("\n").flatMap((l, i) => [...(i ? [new TextRun({ break: 1 })] : []), ...runs(l, o)]) }));
}
const H1 = (t, o = {}) => new Paragraph({ heading: HeadingLevel.HEADING_1, keepNext: true, pageBreakBefore: o.pageBreak,
  spacing: { before: 360, after: 160 }, border: { bottom: { style: BorderStyle.SINGLE, size: 8, color: RED, space: 4 } },
  children: [new TextRun({ text: t, font: FONT, size: 32, bold: true, color: RED })] });
const H2 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_2, keepNext: true, spacing: { before: 240, after: 120 },
  children: [new TextRun({ text: t, font: FONT, size: 27, bold: true, color: TEXT })] });
const bullet = (c, o = {}) => new Paragraph({ numbering: { reference: "bul", level: 0 }, spacing: { after: 100, line: 380 }, children: runs(c, o) });
let numInst = 0;
function olist(items) { numInst++; return items.map((c) => new Paragraph({ numbering: { reference: "num", level: 0, instance: numInst }, spacing: { after: 120, line: 380 }, children: runs(c) })); }
const check = (c) => new Paragraph({ spacing: { after: 120, line: 380 }, children: runs([["☐　", { size: 28 }], [typeof c === "string" ? c : c[0]]]) });
const spacer = (after = 160) => new Paragraph({ children: [], spacing: { after } });

const border = { style: BorderStyle.SINGLE, size: 4, color: LINE };
const borders = { top: border, bottom: border, left: border, right: border };
const none = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
function cell(content, width, o = {}) {
  const list = Array.isArray(content) ? content : [content];
  const ps = list.flatMap((c) => (typeof c === "string" ? c.split("\n").map((x) => P(x, { size: o.size || 22, bold: o.bold, color: o.color, after: 40, line: 340 })) : [c]));
  return new TableCell({ children: ps.length ? ps : [P("", { after: 0 })], width: { size: width, type: WidthType.DXA },
    shading: o.fill ? { fill: o.fill, type: ShadingType.CLEAR, color: "auto" } : undefined,
    margins: { top: 100, bottom: 100, left: 140, right: 140 }, borders, verticalAlign: VerticalAlign.TOP });
}
function table(rows, widths, o = {}) {
  const trs = rows.map((r, ri) => new TableRow({ tableHeader: ri === 0 && o.header !== false, cantSplit: true,
    height: o.rowHeight && ri > 0 ? { value: o.rowHeight, rule: "atLeast" } : undefined,
    children: r.map((c, i) => ri === 0 && o.header !== false ? cell(c, widths[i], { fill: RED, bold: true, color: "FFFFFF" })
      : cell(c, widths[i], { fill: o.firstColFill && i === 0 ? PINK : undefined, bold: o.firstColBold && i === 0 })) }));
  return new Table({ width: { size: CW, type: WidthType.DXA }, columnWidths: widths, rows: trs, layout: TableLayoutType.FIXED });
}
function box(children, fill = PINK) {
  return new Table({ width: { size: CW, type: WidthType.DXA }, columnWidths: [CW], layout: TableLayoutType.FIXED,
    rows: [new TableRow({ cantSplit: true, children: [new TableCell({ children, width: { size: CW, type: WidthType.DXA },
      shading: { fill, type: ShadingType.CLEAR, color: "auto" }, margins: { top: 180, bottom: 140, left: 260, right: 260 },
      borders: { top: none, bottom: none, left: { style: BorderStyle.SINGLE, size: 24, color: RED }, right: none } })] })] });
}
function lines(n, o = {}) { // writing lines
  const out = [];
  for (let i = 0; i < n; i++) out.push(new Paragraph({ spacing: { after: 0, line: 520 }, children: [new TextRun({ text: " ", font: FONT, size: SZ })],
    border: { bottom: { style: BorderStyle.DOTTED, size: 4 + (i % 2), color: "A6A6A6", space: 1 } } }));
  return out;
}
function titleBlock(title, sub, label = "ひとりビジネスという選択　〜自分の名前で生きる〜") {
  return [P([[label, { color: RED, bold: true }]], { size: 20, after: 80 }),
    new Paragraph({ children: [new TextRun({ text: title, font: FONT, size: 48, bold: true, color: TEXT })], spacing: { after: 120 } }),
    ...(sub ? [P(sub, { size: 24, color: GRAY, after: 80 })] : []),
    new Paragraph({ children: [], border: { bottom: { style: BorderStyle.SINGLE, size: 16, color: RED, space: 4 } }, spacing: { after: 280 } })];
}
// render a list of blocks from data
function blocks(list) {
  const c = [];
  for (const [k, v] of list) {
    if (k === "p") c.push(...paras(v));
    else if (k === "h1") c.push(H1(v));
    else if (k === "h2") c.push(H2(v));
    else if (k === "ul") v.forEach((x) => c.push(bullet(x)));
    else if (k === "ol") c.push(...olist(v));
    else if (k === "box") { c.push(box(paras(v, { after: 60 }))); c.push(spacer(120)); }
    else if (k === "table") { const n = v[0].length; const w = n === 2 ? [2600, CW - 2600] : [2200, 3600, CW - 5800]; c.push(table(v, w, { firstColFill: true, firstColBold: true })); c.push(spacer(160)); }
    else if (k === "qa") v.forEach(([q, a]) => { c.push(P([["Q. " + q, { bold: true, color: RED }]], { after: 80, keepNext: true })); c.push(P("A. " + a, { after: 240 })); });
    else throw new Error("unknown block " + k);
  }
  return c;
}
async function save(path, children, o = {}) {
  const doc = new Document({
    creator: "りゅう坊", title: o.title,
    styles: { default: { document: { run: { font: FONT, size: SZ, color: TEXT } } },
      paragraphStyles: [
        { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true, run: { size: 32, bold: true, font: FONT, color: RED }, paragraph: { spacing: { before: 360, after: 160 }, outlineLevel: 0 } },
        { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true, run: { size: 27, bold: true, font: FONT }, paragraph: { spacing: { before: 240, after: 120 }, outlineLevel: 1 } }] },
    numbering: { config: [
      { reference: "bul", levels: [{ level: 0, format: LevelFormat.BULLET, text: "●", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 560, hanging: 360 } }, run: { color: RED, size: 18 } } }] },
      { reference: "num", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 560, hanging: 400 } }, run: { color: RED, bold: true } } }] }] },
    sections: [{ properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1134, bottom: 1134, left: 1134, right: 1134 } } },
      footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [
        new TextRun({ text: (o.footer || "ひとりビジネスという選択｜りゅう坊") + "　", font: FONT, size: 16, color: GRAY }),
        new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 16, color: GRAY })] }),
        new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Copyright © ryubou All Rights Reserved.", font: FONT, size: 14, color: "A6A6A6" })] })] }) },
      children }],
  });
  fs.writeFileSync(path, await Packer.toBuffer(doc));
  console.log("wrote", path);
}
module.exports = { d, P, paras, H1, H2, bullet, olist, check, spacer, table, cell, box, lines, titleBlock, blocks, save, CW, RED, PINK, GRAY, FONT };
