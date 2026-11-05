// Shared builder for the detailed STEP guides (Word)
const fs = require('fs');
const path = require('path');
const {
  Document, Packer, Paragraph, TextRun, ImageRun, Table, TableRow, TableCell, Header, Footer,
  AlignmentType, WidthType, BorderStyle, ShadingType, VerticalAlign, TableLayoutType, TabStopType,
  PageNumber, HeadingLevel, LevelFormat, PageBreak, LineRuleType,
} = require('docx');

const FIG = process.env.FIG_DIR;
const SIZES = JSON.parse(fs.readFileSync(path.join(FIG, 'sizes.json')));
const FONT = '游ゴシック';
const INK = '1F2421', SUB = '5B665D', LINE = 'D3D8D2', PALE = 'F4F5F2';
const CW = 9638; // A4 with 1134 margins
const TPX = 643; // content width in px for images (≈ 6.69in)

const none = { style: BorderStyle.NONE, size: 0, color: 'FFFFFF' };
const NOB = { top: none, bottom: none, left: none, right: none, insideHorizontal: none, insideVertical: none };
const line = (c = LINE, sz = 4) => ({ style: BorderStyle.SINGLE, size: sz, color: c });

function make(cfg) {
  const A = cfg.accent, AP = cfg.accentPale;
  const run = (text, o = {}) => new TextRun({ text, font: FONT, size: o.size || 20, bold: !!o.bold, color: o.color || INK, italics: !!o.it });
  // inline **bold** support
  const rich = (text, o = {}) => String(text).split(/(\*\*[^*]+\*\*)/).filter(Boolean).map((t) => t.startsWith('**')
    ? run(t.slice(2, -2), { ...o, bold: true, color: o.boldColor || o.color })
    : run(t, o));
  const para = (children, o = {}) => new Paragraph({
    children, alignment: o.align, keepNext: o.keepNext, keepLines: o.keepLines,
    spacing: { before: o.before ?? 0, after: o.after ?? 100, line: o.line ?? 320, lineRule: LineRuleType.AUTO },
    indent: o.indent, numbering: o.numbering, border: o.border, shading: o.shading, heading: o.heading,
    pageBreakBefore: o.pageBreakBefore, tabStops: o.tabStops,
  });
  const P = (text, o = {}) => para(rich(text, o), o);

  const cell = (children, width, o = {}) => new TableCell({
    children, width: { size: width, type: WidthType.DXA },
    borders: o.borders || { top: none, bottom: none, left: none, right: none },
    shading: o.fill ? { fill: o.fill, type: ShadingType.CLEAR, color: 'auto' } : undefined,
    margins: o.margins || { top: 60, bottom: 60, left: 100, right: 100 },
    verticalAlign: o.v || VerticalAlign.CENTER, columnSpan: o.span,
  });
  const table = (widths, rows, o = {}) => new Table({
    width: { size: widths.reduce((a, b) => a + b, 0), type: WidthType.DXA }, columnWidths: widths,
    borders: o.borders || NOB, layout: TableLayoutType.FIXED, rows,
  });

  function image(name, wpx) {
    const [w, h] = SIZES[name];
    const width = Math.round(wpx), height = Math.round(wpx * h / w);
    return new ImageRun({ type: 'png', data: fs.readFileSync(path.join(FIG, `${name}.png`)), transformation: { width, height } });
  }
  const capP = (c) => P(c, { size: 16, color: SUB, align: AlignmentType.CENTER, after: 60, line: 260 });

  // ---------- block renderers ----------
  const out = [];
  let olId = 0;
  const numberingConfigs = [];
  const newOl = () => {
    const ref = `ol${olId++}`;
    numberingConfigs.push({ reference: ref, levels: [{ level: 0, format: LevelFormat.DECIMAL, text: '%1.', alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 420, hanging: 320 } }, run: { font: FONT, bold: true, color: A } } }] });
    return ref;
  };
  numberingConfigs.push({ reference: 'ul', levels: [{ level: 0, format: LevelFormat.BULLET, text: '●', alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 380, hanging: 280 } }, run: { color: A, size: 12 } } }] });

  function boxed(children, color, fill) {
    return table([CW], [new TableRow({ children: [cell(children, CW, {
      fill, borders: { top: none, bottom: none, right: none, left: { style: BorderStyle.SINGLE, size: 24, color } },
      margins: { top: 110, bottom: 110, left: 200, right: 160 },
    })] })]);
  }
  const KIND = {
    deck: { label: 'ウッドデッキでは', color: '2B6749', fill: 'EEF4F0' },
    warn: { label: '注意', color: 'B23A2E', fill: 'FBEFEC' },
    tip: { label: 'コツ', color: A, fill: AP },
    fail: { label: 'よくある失敗', color: 'B8861B', fill: 'FBF5E6' },
    info: { label: '', color: '8A938C', fill: PALE },
  };

  function render(b) {
    if (b.pb) { out.push(new Paragraph({ children: [new PageBreak()] })); return; }
    if (b.chapter) {
      out.push(para([run(b.no ? `${b.no}　` : '', { size: 30, bold: true, color: A }), run(b.chapter, { size: 30, bold: true })], {
        pageBreakBefore: b.newPage !== false, before: 0, after: 200, keepNext: true,
        border: { bottom: { style: BorderStyle.SINGLE, size: 12, color: A, space: 6 } }, heading: HeadingLevel.HEADING_1,
      }));
      if (b.lead) out.push(P(b.lead, { size: 19, color: SUB, after: 200 }));
      return;
    }
    if (b.h) { out.push(para([run('■ ', { size: 22, color: A, bold: true }), ...rich(b.h, { size: 23, bold: true })], { before: 240, after: 100, keepNext: true, heading: HeadingLevel.HEADING_2 })); return; }
    if (b.h3) { out.push(P(b.h3, { size: 21, bold: true, color: A, before: 160, after: 60, keepNext: true })); return; }
    if (b.p) { out.push(P(b.p, { boldColor: b.boldColor })); return; }
    if (b.small) { out.push(P(b.small, { size: 17, color: SUB, line: 280 })); return; }
    if (b.ul) { b.ul.forEach((t) => out.push(P(t, { numbering: { reference: 'ul', level: 0 }, after: 60 }))); out.push(P('', { after: 40, line: 200 })); return; }
    if (b.ol) { const ref = newOl(); b.ol.forEach((t) => out.push(P(t, { numbering: { reference: ref, level: 0 }, after: 80 }))); out.push(P('', { after: 40, line: 200 })); return; }
    if (b.check) {
      b.check.forEach((t) => out.push(para([run('☐  ', { size: 22, color: A }), ...rich(t)], { after: 70, indent: { left: 360, hanging: 360 } })));
      out.push(P('', { after: 40, line: 200 })); return;
    }
    if (b.note) {
      const k = KIND[b.kind || 'tip'];
      const lines = Array.isArray(b.note) ? b.note : [b.note];
      const ch = [];
      const label = b.label ?? k.label;
      if (label) ch.push(P(label, { size: 18, bold: true, color: k.color, after: 40 }));
      lines.forEach((t, i) => ch.push(P(t, { size: 19, after: i === lines.length - 1 ? 0 : 60, line: 300 })));
      out.push(boxed(ch, k.color, k.fill)); out.push(P('', { after: 60, line: 200 })); return;
    }
    if (b.formula) {
      out.push(table([CW], [new TableRow({ children: [cell(b.formula.map((t, i) => P(t, { size: i === 0 ? 18 : 22, color: i === 0 ? SUB : INK, bold: i > 0, align: AlignmentType.CENTER, after: 40 })), CW, { fill: PALE, margins: { top: 120, bottom: 100, left: 200, right: 200 } })] })]));
      out.push(P('', { after: 60, line: 200 })); return;
    }
    if (b.table) {
      const { head, rows, widths, total } = b.table;
      const W = widths.map((w) => Math.round(w * CW / widths.reduce((a, c) => a + c, 0)));
      W[W.length - 1] = CW - W.slice(0, -1).reduce((a, c) => a + c, 0);
      const bt = { top: none, left: none, right: none, bottom: line() };
      const trs = [];
      if (head) trs.push(new TableRow({ tableHeader: true, children: head.map((h, i) => cell([P(h, { size: 17, bold: true, color: 'FFFFFF', after: 0, line: 260 })], W[i], { fill: A })) }));
      rows.forEach((r) => {
        if (typeof r === 'string') { trs.push(new TableRow({ children: [cell([P(r, { size: 18, bold: true, after: 0 })], CW, { span: W.length, fill: AP, borders: bt })] })); return; }
        trs.push(new TableRow({ cantSplit: true, children: r.map((c, i) => cell([P(c, { size: 18, after: 0, line: 280, bold: total && r === rows[rows.length - 1] })], W[i], { borders: bt, v: VerticalAlign.TOP })) }));
      });
      out.push(table(W, trs)); out.push(P('', { after: 80, line: 200 })); return;
    }
    if (b.fig) {
      out.push(para([image(b.fig, b.w || 380)], { align: AlignmentType.CENTER, after: 40, keepNext: true }));
      if (b.cap) out.push(capP(b.cap));
      return;
    }
    if (b.figs) {
      const n = b.figs.length, w = Math.floor(CW / n);
      const ipx = Math.min(b.w || 999, Math.floor(TPX / n) - 16);
      out.push(table(Array(n).fill(w), [new TableRow({ cantSplit: true, children: b.figs.map(([f, c]) => cell([
        para([image(f, ipx)], { align: AlignmentType.CENTER, after: 30 }), ...(c ? [capP(c)] : []),
      ], w, { v: VerticalAlign.BOTTOM })) })]));
      out.push(P('', { after: 60, line: 200 })); return;
    }
    if (b.steps) {
      b.steps.forEach((s, i) => {
        const left = [
          para([run(` ${s.no || i + 1} `, { size: 20, bold: true, color: 'FFFFFF' }), run('  ' + s.title, { size: 22, bold: true })], { after: 80, shading: undefined }),
          ...s.body.map((t) => typeof t === 'string' ? P(t, { size: 19, after: 70, line: 300 }) : P(t.c, { size: 18, color: t.warn ? 'B23A2E' : A, bold: true, after: 70, line: 290 })),
        ];
        // colored number via shading on the first run
        left[0] = para([new TextRun({ text: ` ${s.no || i + 1} `, font: FONT, size: 20, bold: true, color: 'FFFFFF', shading: { type: ShadingType.CLEAR, fill: A, color: 'auto' } }), run('  ' + s.title, { size: 22, bold: true })], { after: 80 });
        if (s.fig) {
          const wl = Math.round(CW * 0.6), wr = CW - wl;
          out.push(table([wl, wr], [new TableRow({ cantSplit: true, children: [
            cell(left, wl, { v: VerticalAlign.TOP, margins: { top: 40, bottom: 40, left: 0, right: 160 } }),
            cell([para([image(s.fig, s.figW || 220)], { align: AlignmentType.CENTER, after: 30 }), ...(s.cap ? [capP(s.cap)] : [])], wr, { v: VerticalAlign.TOP }),
          ] })]));
        } else {
          left.forEach((x) => out.push(x));
        }
        out.push(P('', { after: 80, line: 200, border: { bottom: { style: BorderStyle.DOTTED, size: 4, color: LINE, space: 4 } } }));
      });
      return;
    }
    if (b.qa) {
      b.qa.forEach(([q, a]) => {
        out.push(para([run('Q. ', { size: 20, bold: true, color: A }), ...rich(q, { size: 20, bold: true })], { keepNext: true, after: 40, before: 80 }));
        out.push(para([run('A. ', { size: 20, bold: true, color: SUB }), ...rich(a, { size: 19 })], { after: 80, indent: { left: 380, hanging: 380 } }));
      });
      return;
    }
    if (b.memo) {
      const rows = b.memo.map(([k]) => new TableRow({ children: [
        cell([P(k, { size: 18, bold: true, after: 0 })], 2600, { fill: PALE, borders: { top: line(), bottom: line(), left: line(), right: line() } }),
        cell([P('', { after: 0 })], CW - 2600, { borders: { top: line(), bottom: line(), left: line(), right: line() }, margins: { top: 260, bottom: 260, left: 100, right: 100 } }),
      ] }));
      out.push(table([2600, CW - 2600], rows)); out.push(P('', { after: 80 })); return;
    }
    if (b.timeline) {
      const W = [1500, 1400, CW - 2900];
      const bt = { top: none, left: none, right: none, bottom: line() };
      out.push(table(W, b.timeline.map(([t, d, x]) => new TableRow({ cantSplit: true, children: [
        cell([P(t, { size: 19, bold: true, color: A, after: 0 })], W[0], { borders: bt }),
        cell([P(d, { size: 18, color: SUB, after: 0 })], W[1], { borders: bt }),
        cell([P(x, { size: 19, after: 0, line: 290 })], W[2], { borders: bt }),
      ] }))));
      out.push(P('', { after: 80, line: 200 })); return;
    }
    throw new Error('unknown block ' + JSON.stringify(b).slice(0, 80));
  }

  // ---------- cover ----------
  const cover = [];
  cover.push(P('週末DIY 5ステップ講座　解説書（詳しい版）', { size: 20, color: SUB, after: 120 }));
  cover.push(para([new TextRun({ text: ` ${cfg.stepLabel} `, font: FONT, size: 26, bold: true, color: 'FFFFFF', shading: { type: ShadingType.CLEAR, fill: A, color: 'auto' } })], { after: 120 }));
  cover.push(P(cfg.title, { size: 52, bold: true, after: 80, line: 360 }));
  cover.push(P(cfg.catch, { size: 22, color: SUB, after: 200 }));
  cover.push(para([image(cfg.coverFig, cfg.coverW || 330)], { align: AlignmentType.CENTER, after: 200 }));
  const specW = [Math.round(CW / 3), Math.round(CW / 3), CW - 2 * Math.round(CW / 3)];
  cover.push(table(specW, [new TableRow({ children: cfg.spec.map(([k, v], i) => cell([P(k, { size: 16, color: SUB, after: 20 }), P(v, { size: 20, bold: true, after: 0, line: 280 })], specW[i], {
    fill: AP, borders: { top: line('FFFFFF', 12), bottom: line('FFFFFF', 12), left: line('FFFFFF', 12), right: line('FFFFFF', 12) }, margins: { top: 120, bottom: 120, left: 160, right: 160 },
  })) })]));
  cover.push(P('', { after: 120 }));
  cover.push(P('この解説書の使い方', { size: 20, bold: true, after: 60 }));
  cover.push(P('教材（図面・カット表のPDF）と動画と一緒に使います。作業の前に、第1章から第3章を一度通して読んでください。作業中は、第4章以降を開いたまま手元に置き、☐ に印をつけながら進めます。寸法の単位はすべてmmです。', { size: 18, color: SUB, line: 300 }));
  if (cfg.coverNote) cover.push(P(cfg.coverNote, { size: 18, color: SUB, line: 300 }));
  // contents
  cover.push(P('目次', { size: 20, bold: true, before: 160, after: 60 }));
  cfg.blocks.filter((b) => b.chapter).forEach((b) => cover.push(para([run(`${b.no}　`, { size: 19, bold: true, color: A }), run(b.chapter, { size: 19 })], { after: 30 })));

  cfg.blocks.forEach(render);

  const header = new Header({ children: [para([
    run(`週末DIY 5ステップ講座　${cfg.stepLabel}　${cfg.short}`, { size: 16, color: SUB }),
    run('\t', { size: 16 }), run('解説書（詳しい版）', { size: 16, color: SUB }),
  ], { after: 0, tabStops: [{ type: TabStopType.RIGHT, position: CW }], border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: A, space: 4 } } })] });
  const footer = new Footer({ children: [para([
    run('Copyright Ⓒ ryubou All Rights Reserved　監修 ryuphoenix.office', { size: 14, color: SUB }),
    run('\t', { size: 14 }),
    new TextRun({ children: [PageNumber.CURRENT, ' / ', PageNumber.TOTAL_PAGES], font: FONT, size: 16, color: SUB }),
  ], { after: 0, tabStops: [{ type: TabStopType.RIGHT, position: CW }] })] });

  const doc = new Document({
    creator: 'ryuphoenix.office', title: `週末DIY 5ステップ講座 ${cfg.stepLabel} ${cfg.short} 解説書`,
    styles: { default: { document: { run: { font: { ascii: FONT, eastAsia: FONT, hAnsi: FONT }, size: 20, color: INK } } } },
    numbering: { config: numberingConfigs },
    sections: [{
      properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1134, bottom: 1000, left: 1134, right: 1134, header: 560, footer: 480 } } },
      headers: { default: header }, footers: { default: footer },
      children: [...cover, ...out],
    }],
  });
  return Packer.toBuffer(doc);
}

module.exports = { make };
