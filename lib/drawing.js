// 図面用の描画部品（寸法線・立体図）。deck-plans と course で使う。
(function (global) {
  const mm = (n) => Math.round(n).toLocaleString('ja-JP');
  const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const edges = (arr, a, b) => [a, ...arr, b];

  // 水平の寸法線（連続寸法）。xs はSVG座標、y は線の位置
  function dimH(xs, y, fs, sw, opt = {}) {
    let s = '';
    const tick = fs * 0.45;
    s += `<line x1="${xs[0]}" x2="${xs[xs.length - 1]}" y1="${y}" y2="${y}" stroke="var(--muted)" stroke-width="${sw}"/>`;
    xs.forEach((x) => { s += `<line x1="${x - tick * .6}" x2="${x + tick * .6}" y1="${y + tick * .6}" y2="${y - tick * .6}" stroke="var(--ink)" stroke-width="${sw * 1.4}"/>`; });
    for (let i = 0; i < xs.length - 1; i++) {
      const len = xs[i + 1] - xs[i];
      if (len < fs * 2.2 && !opt.force) continue;
      const label = opt.labels ? opt.labels[i] : mm(len);
      s += `<text x="${(xs[i] + xs[i + 1]) / 2}" y="${y - fs * .35}" text-anchor="middle" font-size="${fs}">${label}</text>`;
    }
    return s;
  }

  // 垂直の寸法線（連続寸法）
  function dimV(ys, x, fs, sw, opt = {}) {
    let s = '';
    const tick = fs * 0.45;
    s += `<line x1="${x}" x2="${x}" y1="${ys[0]}" y2="${ys[ys.length - 1]}" stroke="var(--muted)" stroke-width="${sw}"/>`;
    ys.forEach((y) => { s += `<line x1="${x - tick * .6}" x2="${x + tick * .6}" y1="${y + tick * .6}" y2="${y - tick * .6}" stroke="var(--ink)" stroke-width="${sw * 1.4}"/>`; });
    for (let i = 0; i < ys.length - 1; i++) {
      const len = ys[i + 1] - ys[i];
      if (len < fs * 2.2 && !opt.force) continue;
      const cy = (ys[i] + ys[i + 1]) / 2;
      const label = opt.labels ? opt.labels[i] : mm(len);
      s += `<text x="${x - fs * .35}" y="${cy}" text-anchor="middle" font-size="${fs}" transform="rotate(-90 ${x - fs * .35} ${cy})">${label}</text>`;
    }
    return s;
  }

  // 奥にある箱から順に並べる。どれかの軸で完全に手前側にある箱は、あとで描く。
  function drawOrder(boxes) {
    const ax = [['x', 'w'], ['y', 'd'], ['z', 'h']];
    const before = (a, b) => ax.some(([p, s]) => a[p] + a[s] <= b[p]) && !ax.some(([p, s]) => b[p] + b[s] <= a[p]);
    const rest = boxes.slice(), out = [];
    const key = (b) => b.x + b.w / 2 + b.y + b.d / 2 + b.z + b.h / 2;
    while (rest.length) {
      let i = rest.findIndex((a) => !rest.some((b) => b !== a && before(b, a)));
      if (i < 0) i = rest.reduce((m, b, k) => (key(b) < key(rest[m]) ? k : m), 0);
      out.push(rest.splice(i, 1)[0]);
    }
    return out;
  }

  // 立体図（等角投影）。boxes: [{ x, y, z, w, d, h, tone: 'new'|'old'|'ghost', label }]
  // x＝幅、y＝奥行き（手前が大きい）、z＝高さ。右手前の上から見た図になる。
  function iso(boxes, opt = {}) {
    const c = Math.cos(Math.PI / 6), s = 0.5;
    const P = (x, y, z) => [(x - y) * c, (x + y) * s - z];
    const tones = {
      new: ['#e9c79f', '#c99a68', '#a97c4f'],
      old: ['#f3ebe0', '#ddd2c3', '#c8bba9'],
      ghost: ['none', 'none', 'none'],
    };
    const items = drawOrder(boxes);
    let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
    const polys = [];
    for (const b of items) {
      const { x, y, z, w, d, h } = b;
      const faces = [
        [[x, y, z + h], [x + w, y, z + h], [x + w, y + d, z + h], [x, y + d, z + h]],
        [[x + w, y, z], [x + w, y + d, z], [x + w, y + d, z + h], [x + w, y, z + h]],
        [[x, y + d, z], [x + w, y + d, z], [x + w, y + d, z + h], [x, y + d, z + h]],
      ];
      const t = tones[b.tone || 'new'];
      faces.forEach((f, i) => {
        const pts = f.map((p) => P(...p));
        pts.forEach(([px, py]) => { minX = Math.min(minX, px); maxX = Math.max(maxX, px); minY = Math.min(minY, py); maxY = Math.max(maxY, py); });
        polys.push({ pts, fill: t[i], dash: b.tone === 'ghost' });
      });
      if (b.label) polys.push({ label: b.label, at: P(x + w / 2, y + d / 2, z + h) });
    }
    const span = Math.max(maxX - minX, maxY - minY);
    const pad = span * 0.08, sw = span / 380, fs = span / 22;
    const vb = `${minX - pad} ${minY - pad} ${maxX - minX + pad * 2} ${maxY - minY + pad * 2}`;
    let out = `<svg viewBox="${vb}" role="img" aria-label="${esc(opt.title || '立体図')}">`;
    for (const p of polys) {
      if (p.label) {
        out += `<text x="${p.at[0]}" y="${p.at[1] - fs * .4}" text-anchor="middle" font-size="${fs}" font-weight="700" fill="var(--ink)" stroke="#fff" stroke-width="${fs * .25}" paint-order="stroke">${esc(p.label)}</text>`;
        continue;
      }
      out += `<polygon points="${p.pts.map((q) => q.join(',')).join(' ')}" fill="${p.fill}" stroke="var(--ink)" stroke-width="${sw}" stroke-linejoin="round"${p.dash ? ` stroke-dasharray="${sw * 4} ${sw * 3}"` : ''}/>`;
    }
    return out + '</svg>';
  }

  global.Draw = { mm, esc, edges, dimH, dimV, iso };
})(typeof window !== 'undefined' ? window : globalThis);
