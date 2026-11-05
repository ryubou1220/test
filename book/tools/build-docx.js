// manuscript/*.md から Word 原稿（.docx）を生成する
// 使い方: node tools/build-docx.js  （book ディレクトリで実行）
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType,
  TableOfContents, Footer, PageNumber, LevelFormat,
} = require("docx");

const ROOT = path.resolve(__dirname, "..");
const MS_DIR = path.join(ROOT, "manuscript");
const OUT = path.join(ROOT, "dist", "monozukuri-kimo.docx");

// metadata.yaml から最低限の項目だけ読む
const meta = {};
for (const line of fs.readFileSync(path.join(ROOT, "metadata.yaml"), "utf8").split("\n")) {
  const m = line.match(/^(title|subtitle|author):\s*(.+)$/);
  if (m) meta[m[1]] = m[2].trim();
}

const FONT = { ascii: "Yu Mincho", hAnsi: "Yu Mincho", eastAsia: "游明朝" };
const HFONT = { ascii: "Yu Gothic", hAnsi: "Yu Gothic", eastAsia: "游ゴシック" };
const BODY_SIZE = 21; // 10.5pt

// **太字** を TextRun に分解
function runs(text, opts = {}) {
  return text.split(/(\*\*[^*]+\*\*)/).filter(Boolean).map((part) => {
    const bold = part.startsWith("**") && part.endsWith("**");
    return new TextRun({ text: bold ? part.slice(2, -2) : part, bold, ...opts });
  });
}

const children = [];
const files = fs.readdirSync(MS_DIR).filter((f) => f.endsWith(".md")).sort();

files.forEach((file, idx) => {
  const lines = fs.readFileSync(path.join(MS_DIR, file), "utf8").split("\n");
  let firstHeading = true;
  for (const raw of lines) {
    const line = raw.trimEnd();
    if (!line.trim()) continue;
    if (line.startsWith("# ")) {
      children.push(new Paragraph({
        heading: HeadingLevel.HEADING_1,
        pageBreakBefore: firstHeading && idx > 0,
        children: runs(line.slice(2)),
      }));
      firstHeading = false;
    } else if (line.startsWith("## ")) {
      children.push(new Paragraph({ heading: HeadingLevel.HEADING_2, children: runs(line.slice(3)) }));
    } else if (line.startsWith("- ")) {
      children.push(new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: runs(line.slice(2)) }));
    } else {
      // 会話文（「…」）は字下げしない
      const isQuote = line.startsWith("「");
      children.push(new Paragraph({
        indent: isQuote ? undefined : { firstLine: BODY_SIZE * 10 },
        children: runs(line),
      }));
    }
  }
});

const doc = new Document({
  creator: meta.author || "",
  title: meta.title || "",
  styles: {
    default: {
      document: {
        run: { font: FONT, size: BODY_SIZE },
        paragraph: { spacing: { line: 400, after: 60 } },
      },
      title: {
        run: { font: HFONT, size: 48, bold: true },
        paragraph: { alignment: AlignmentType.CENTER, spacing: { before: 3600, after: 360 }, keepNext: true },
      },
      heading1: {
        run: { font: HFONT, size: 32, bold: true },
        paragraph: { spacing: { before: 480, after: 480 }, keepNext: true },
      },
      heading2: {
        run: { font: HFONT, size: 24, bold: true },
        paragraph: { spacing: { before: 360, after: 160 }, keepNext: true },
      },
    },
  },
  numbering: {
    config: [{
      reference: "bullets",
      levels: [{
        level: 0, format: LevelFormat.BULLET, text: "・", alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 420, hanging: 420 } } },
      }],
    }],
  },
  features: { updateFields: true },
  sections: [
    {
      // 扉
      properties: { page: { size: { width: 11906, height: 16838 } } },
      children: [
        new Paragraph({ heading: HeadingLevel.TITLE, children: [new TextRun(meta.title || "")] }),
        new Paragraph({
          alignment: AlignmentType.CENTER, spacing: { after: 1200 },
          children: [new TextRun({ text: meta.subtitle || "", size: 24 })],
        }),
        new Paragraph({
          alignment: AlignmentType.CENTER,
          children: [new TextRun({ text: meta.author || "", size: 24 })],
        }),
        new Paragraph({ pageBreakBefore: true, children: [new TextRun({ text: "目次", font: HFONT, size: 32, bold: true })], spacing: { after: 360 } }),
        new TableOfContents("目次", { hyperlink: true, headingStyleRange: "1-1" }),
      ],
    },
    {
      properties: {
        page: {
          size: { width: 11906, height: 16838 },
          margin: { top: 1701, bottom: 1701, left: 1701, right: 1701 },
          pageNumbers: { start: 1 },
        },
      },
      footers: {
        default: new Footer({
          children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ children: [PageNumber.CURRENT], size: 18 })] })],
        }),
      },
      children,
    },
  ],
});

fs.mkdirSync(path.dirname(OUT), { recursive: true });
Packer.toBuffer(doc).then((buf) => {
  fs.writeFileSync(OUT, buf);
  console.log("wrote", path.relative(ROOT, OUT));
});
