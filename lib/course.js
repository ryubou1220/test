// 講座教材（course/）の共通部品。講座名・監修者・連絡先はここを書き換える。
(function (global) {
  const BRAND = {
    course: '週末DIY 5ステップ講座',
    supervisor: '野村 隆一',
    site: 'ryuphoenix.com',
    line: '', // LINE公式アカウントのURLやIDができたら入れる
    version: '2026年版',
  };

  const STEPS = [
    ['STEP1', '踏み台', '切る・留める'],
    ['STEP2', 'プランター台', '板を張る'],
    ['STEP3', '囲炉裏テーブル', '枠を組む'],
    ['STEP4', '木製門扉', '柱を建てる'],
    ['卒業制作', 'ウッドデッキ', 'すべてを使う'],
  ];

  const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const mm = (n) => Math.round(n).toLocaleString('ja-JP');

  // 5ステップの道のり。on は今のステップ（0〜4）
  function road(on) {
    return `<div class="road">${STEPS.map(([n, t, k], i) => `<div class="${i === on ? 'on' : ''}${i === 4 ? ' goal' : ''}"><span>${n}</span><b>${t}</b>${k}</div>`).join('')}</div>`;
  }

  // A4の1ページ。下に表題欄がつく
  function sheet({ step, name, size, no, total, body }) {
    return `<section class="sheet"><div class="body">${body}</div>
      <div class="tb">
        <div><span>${BRAND.course}</span><b>${esc(step)} ／ ${esc(name)}</b></div>
        <div><span>サイズ（幅×奥行き×高さ）</span><b>${esc(size)}</b></div>
        <div><span>監修</span><b>${BRAND.supervisor}</b></div>
        <div><span>${BRAND.version}</span><b>${no} / ${total}</b></div>
      </div></section>`;
  }

  // 定尺材1本の切り方の帯。cuts: [{ len, use }]
  function cutBar(cuts, stock = 1820, kerf = 3) {
    const used = cuts.reduce((a, c) => a + c.len, 0) + kerf * (cuts.length - 1);
    const parts = cuts.map((c) => `<div class="cut" style="width:${(c.len / stock) * 100}%"><b>${mm(c.len)}</b>${esc(c.use)}</div>`).join('');
    return { html: `<div class="stock">${parts}</div>`, rest: stock - used };
  }

  // 部品を定尺材に割り振る。本数がいちばん少なくなる組み合わせを探す（部品が多いときは近い答えで止める）。
  // pieces: [{ len, use }]  →  [[{ len, use }, ...], ...]（1本ごとの切り方）
  function packCuts(pieces, stock = 1820, kerf = 3) {
    const items = pieces.slice().sort((a, b) => b.len - a.len);
    const need = (cuts, len) => len + (cuts.length ? kerf : 0);
    // まず、長い部品から入る材に詰める
    let best = [];
    for (const p of items) {
      const bin = best.find((b) => b.free >= need(b.cuts, p.len));
      if (bin) { bin.free -= need(bin.cuts, p.len); bin.cuts.push(p); } else best.push({ cuts: [p], free: stock - p.len });
    }
    best = best.map((b) => b.cuts);
    // つぎに、1本少なくできないか順に試す
    const total = items.reduce((a, p) => a + p.len, 0);
    let steps = 0;
    const search = (i, bins) => {
      if (++steps > 200000) return null;
      if (i === items.length) return bins.map((b) => b.cuts.slice());
      const p = items[i];
      const seen = new Set();
      for (const b of bins) {
        if (seen.has(b.free) || b.free < need(b.cuts, p.len)) continue;
        seen.add(b.free);
        const n = need(b.cuts, p.len);
        b.free -= n; b.cuts.push(p);
        const r = search(i + 1, bins);
        b.cuts.pop(); b.free += n;
        if (r) return r;
      }
      return null;
    };
    for (let k = Math.ceil(total / stock); k < best.length; k++) {
      steps = 0;
      const bins = Array.from({ length: k }, () => ({ cuts: [], free: stock }));
      const r = search(0, bins);
      if (r && r.every((c) => c.length)) { best = r; break; }
    }
    return best.filter((c) => c.length);
  }

  // 連絡先の1行
  function contact() {
    return `${BRAND.line ? `LINE：<b>${esc(BRAND.line)}</b>　／　` : ''}サイト：<b>${esc(BRAND.site)}</b>`;
  }

  global.Course = { BRAND, STEPS, road, sheet, cutBar, packCuts, contact };
})(typeof window !== 'undefined' ? window : globalThis);
