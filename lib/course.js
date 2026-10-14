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

  // 連絡先の1行
  function contact() {
    return `${BRAND.line ? `LINE：<b>${esc(BRAND.line)}</b>　／　` : ''}サイト：<b>${esc(BRAND.site)}</b>`;
  }

  global.Course = { BRAND, STEPS, road, sheet, cutBar, contact };
})(typeof window !== 'undefined' ? window : globalThis);
