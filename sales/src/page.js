(function () {
  // ページの中身はすべて #content のデータから描く。編集すると、データを書き換えて丸ごと保存し直す。
  const S = JSON.parse(document.getElementById('content').textContent);
  const app = document.getElementById('app');
  const bar = document.getElementById('edbar');
  const FONTS = '<link rel="preconnect" href="https://fonts.googleapis.com">\n<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Zen+Kaku+Gothic+New:wght@400;700;900&family=Zen+Old+Mincho:wght@700&display=swap">';
  const RESET = ':root{color-scheme:light;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0;font:14px/1.5 system-ui,sans-serif}img{max-width:100%}[hidden]{display:none!important}';

  let editing = false, dirty = false, linksOpen = false, busy = false;
  let canEdit = false, art = null, assets = null, downloads = null, imgTarget = null;
  let message = '';

  const esc = (s) => String(s == null ? '' : s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const get = (p) => p.split('.').reduce((o, k) => (o == null ? o : o[k]), S);
  const set = (p, v) => {
    const ks = p.split('.'), last = ks.pop();
    ks.reduce((o, k) => o[k], S)[last] = v;
    if (!dirty) { dirty = true; renderBar(); }
  };

  // 編集できる文字
  const T = (p, tag = 'span', cls = '') => `<${tag}${cls ? ` class="${cls}"` : ''} data-k="${p}"${editing ? ' contenteditable="plaintext-only" spellcheck="false"' : ''}>${esc(get(p))}</${tag}>`;
  // 差し替えできる画像
  const IMG = (p, alt, extra = '') => {
    const src = get(p);
    const pic = src ? `<img src="${esc(src)}" alt="${esc(alt)}"${extra}>` : `<span class="ed-noimg">写真がありません</span>`;
    return editing ? `<span class="ed-imgwrap">${pic}<button type="button" class="ed-btn ed-img" data-img="${p}">写真を変える</button></span>` : pic;
  };
  // リンク付きのボタン（行き先は「リンク設定」で決める。未設定ならページ内の料金欄へ）
  const LINK = (name, labelPath, cls, fallback = '#price') => {
    const url = S.links[name];
    return `<a class="${cls}" href="${esc(url || fallback)}"${url ? ' target="_blank" rel="noopener"' : ''}>${T(labelPath)}</a>`;
  };
  const DEL = (p, what) => (editing ? `<button type="button" class="ed-btn ed-del" data-del="${p}" aria-label="${what}を削除">削除</button>` : '');
  const ADD = (p, what) => (editing ? `<button type="button" class="ed-btn ed-add" data-add="${p}">＋ ${what}を追加</button>` : '');
  const each = (p, fn) => get(p).map((_, i) => fn(`${p}.${i}`, i)).join('');

  const NEW = {
    'hero.badges': () => ({ k: '項目', v: '内容' }),
    'why.items': () => ({ t: '悩み', p: '答え' }),
    'road.steps': () => ({ no: 'STEP', tag: '', title: '作品名', img: '', skill: '覚えること', deckuse: 'ウッドデッキでは：', facts: [{ k: '材料費', v: '約○円' }] }),
    'price.rows': () => ({ name: '商品名', desc: '内容', sub: '', price: '○円', set: false }),
    'price.course.items': () => '内容',
    'voice.items': () => ({ n1k: '項目', n1v: '数字', n2k: '項目', n2v: '数字', quote: '感想', who: 'お名前（年代・職業）' }),
    'author.paras': () => '文章',
    'author.dl': () => ({ k: '項目', v: '内容' }),
    'author.works': () => ({ img: '', cap: '写真の説明' }),
    'faq.items': () => ({ q: '質問', a: '答え' }),
  };

  function stepCard(p, goal) {
    const s = get(p);
    return `<article class="stepcard${goal ? ' goal' : ''}">
      ${goal ? '' : DEL(p, 'ステップ')}
      <div class="art">${IMG(p + '.img', s.title + 'の図', ' width="300" height="220"')}</div>
      <div class="txt">
        <div class="stepno">${T(p + '.no')}${s.tag || editing ? ` ${T(p + '.tag', 'span', s.tag ? 'free' : 'free ed-empty')}` : ''}</div>
        ${T(p + '.title', 'h3')}
        ${T(p + '.skill', 'p', 'skill')}
        ${T(p + '.deckuse', 'p', 'deckuse')}
        <div class="facts">${each(p + '.facts', (f) => `<span>${T(f + '.k')} <b>${T(f + '.v')}</b>${DEL(f, '項目')}</span>`)}${ADD(p + '.facts', '項目')}</div>
        ${goal ? `<div>${LINK('calc', p + '.btn', 'btn ghost')}</div>` : ''}
      </div>
    </article>`;
  }

  function render() {
    const faqItem = (p) => editing
      ? `<div class="ed-faq">${T(p + '.q', 'b')}${T(p + '.a', 'p')}${DEL(p, '質問')}</div>`
      : `<details><summary>${esc(get(p + '.q'))}</summary><p>${esc(get(p + '.a'))}</p></details>`;
    app.innerHTML = `
<header class="hero">
  <div class="wrap hero-grid">
    <div>
      ${T('hero.eyebrow', 'div', 'eyebrow')}
      <h1>${T('hero.h1a')}<em>${T('hero.h1em')}</em>${T('hero.h1b')}</h1>
      ${T('hero.sub', 'p', 'sub')}
      <div class="ctas">${LINK('step1', 'hero.cta1', 'btn')}<a class="btn ghost" href="#road">${T('hero.cta2')}</a></div>
      <div class="badges">${each('hero.badges', (b) => `<span>${T(b + '.k')} <b>${T(b + '.v')}</b>${DEL(b, '項目')}</span>`)}${ADD('hero.badges', '項目')}</div>
    </div>
    <figure class="hero-visual" style="margin:0" aria-label="講座でつくる作品">
      <ol class="hv">${each('hero.pieces', (h, i) => `<li>${IMG(h + '.img', get(h + '.label'), ' width="220" height="160"')}<span><b>${i + 1}</b>${T(h + '.label')}</span></li>`)}</ol>
      <div class="hv-goal">${IMG('hero.goalImg', 'ウッドデッキ', ' width="220" height="160"')}<span>${T('hero.goalSmall', 'small')}${T('hero.goalLabel')}</span></div>
    </figure>
  </div>
</header>
<main>
<section id="why"><div class="wrap">
  ${T('why.eyebrow', 'div', 'eyebrow')}${T('why.h2', 'h2')}${T('why.lead', 'p', 'lead')}
  <div class="qa">${each('why.items', (q) => `<div>${T(q + '.t', 'b')}${T(q + '.p', 'p')}${DEL(q, '項目')}</div>`)}</div>
  ${ADD('why.items', '項目')}
</div></section>

<section id="road"><div class="wrap">
  ${T('road.eyebrow', 'div', 'eyebrow')}${T('road.h2', 'h2')}${T('road.lead', 'p', 'lead')}
  <div class="road">
    ${each('road.steps', (p) => stepCard(p, false))}
    ${ADD('road.steps', 'ステップ')}
    ${T('road.connector', 'p', 'connector')}
    ${stepCard('road.goal', true)}
  </div>
</div></section>

<section id="price"><div class="wrap">
  ${T('price.eyebrow', 'div', 'eyebrow')}${T('price.h2', 'h2')}${T('price.lead', 'p', 'lead')}
  <div class="tablewrap"><table class="price-table">
    <thead><tr><th>ステップ</th><th>内容</th><th class="r">価格</th></tr></thead>
    <tbody>${each('price.rows', (r) => `<tr${get(r + '.set') ? ' class="set"' : ''}><td>${T(r + '.name', 'b')}${DEL(r, '行')}</td><td>${T(r + '.desc')}${get(r + '.sub') || editing ? T(r + '.sub', 'small') : ''}</td><td class="r">${T(r + '.price', 'span', 'yen')}</td></tr>`)}</tbody>
  </table></div>
  ${ADD('price.rows', '行')}
  <div class="course-box">
    ${T('price.course.label', 'div', 'stepno')}${T('price.course.title', 'h3')}
    <ul>${each('price.course.items', (it) => `<li>${T(it)}${DEL(it, '項目')}</li>`)}</ul>
    ${ADD('price.course.items', '項目')}
    <div>${T('price.course.price', 'span', 'yen')}${T('price.course.priceNote', 'span', 'note')}</div>
    ${T('price.course.guarantee', 'p', 'guarantee')}
    <div class="ctas" style="margin-top:4px">${LINK('course', 'price.course.btn1', 'btn')}${LINK('calc', 'price.course.btn2', 'btn ghost')}</div>
  </div>
</div></section>

<section id="voice"><div class="wrap">
  ${T('voice.eyebrow', 'div', 'eyebrow')}${T('voice.h2', 'h2')}
  <div class="voices">${each('voice.items', (v) => `<div class="voice">
    <div class="num"><span>${T(v + '.n1k')} <b>${T(v + '.n1v')}</b></span><span>${T(v + '.n2k')} <b>${T(v + '.n2v')}</b></span></div>
    ${T(v + '.quote', 'blockquote')}${T(v + '.who', 'div', 'who')}${DEL(v, '声')}</div>`)}</div>
  ${ADD('voice.items', '声')}
  ${T('voice.note', 'p', 'note')}
</div></section>

<section id="author"><div class="wrap">
  ${T('author.eyebrow', 'div', 'eyebrow')}${T('author.name', 'h2')}
  <div class="prof">
    <div>
      ${each('author.paras', (p) => `<div class="ed-row">${T(p, 'p')}${DEL(p, '段落')}</div>`)}${ADD('author.paras', '段落')}
      <dl>${each('author.dl', (d) => `${T(d + '.k', 'dt')}<dd>${T(d + '.v')}${DEL(d, '項目')}</dd>`)}</dl>${ADD('author.dl', '項目')}
    </div>
    <div class="works">${each('author.works', (w, i) => `<figure${i === 0 ? ' class="wide"' : ''}>${IMG(w + '.img', get(w + '.cap'), ' loading="lazy"')}${T(w + '.cap', 'figcaption')}${DEL(w, '写真')}</figure>`)}${ADD('author.works', '写真')}</div>
  </div>
</div></section>

<section id="faq"><div class="wrap">
  ${T('faq.eyebrow', 'div', 'eyebrow')}${T('faq.h2', 'h2')}
  <div class="faq">${each('faq.items', faqItem)}</div>
  ${ADD('faq.items', '質問')}
</div></section>

<section class="final"><div class="wrap">
  ${T('final.h2', 'h2')}${T('final.lead', 'p', 'lead')}
  <div class="ctas">${LINK('step1', 'final.btn', 'btn')}</div>
</div></section>
</main>
<footer><div class="wrap">
  <div class="links">${LINK('law', 'footer.law', '')}${LINK('site', 'footer.site', '')}</div>
  ${T('footer.credit', 'p')}
</div></footer>`;
    document.title = S.meta.title;
  }

  // ===== 編集バー =====
  function renderBar() {
    if (!canEdit) { bar.hidden = true; return; }
    bar.hidden = false;
    const msg = message ? `<span class="ed-msg" role="status">${esc(message)}</span>` : '';
    if (!editing) {
      bar.innerHTML = `<div class="ed-in"><button type="button" class="ed-main" data-act="edit">編集する</button>${downloads ? '<button type="button" data-act="export">HTMLを書き出す</button>' : ''}${msg}</div>`;
      return;
    }
    const L = (k, label, hint) => `<label class="ed-field"><span>${label}</span><input type="url" data-link-k="${k}" value="${esc(S.links[k])}" placeholder="${hint}"></label>`;
    bar.innerHTML = `${linksOpen ? `<div class="ed-links">
        ${L('step1', 'STEP1を無料で受け取る（LINE登録）', 'https://lin.ee/…')}
        ${L('course', 'ウッドデッキ完成コースの申し込み', 'https://…')}
        ${L('calc', '材料費の計算ツール', 'https://…')}
        ${L('law', '特定商取引法に基づく表記', 'https://…')}
        ${L('site', 'サイト', 'https://…')}
        <label class="ed-field"><span>ページの名前（ブラウザのタブ）</span><input type="text" data-meta-k="title" value="${esc(S.meta.title)}"></label>
        <label class="ed-field"><span>ページの説明（検索結果に出る文）</span><input type="text" data-meta-k="description" value="${esc(S.meta.description)}"></label>
      </div>` : ''}
      <div class="ed-in">
        <button type="button" class="ed-main" data-act="save"${busy ? ' disabled' : ''}>${busy ? '保存中…' : dirty ? '保存する' : '保存する（変更なし）'}</button>
        <button type="button" data-act="cancel"${busy ? ' disabled' : ''}>やめる</button>
        <button type="button" data-act="links" aria-expanded="${linksOpen}">リンクとページ設定</button>
        <span class="ed-hint">文字は直接クリックして書き換えられます。</span>${msg}
      </div>`;
  }

  // ===== 保存するページ全体を、データから組み立てる =====
  function buildDoc() {
    const css = document.getElementById('page-style').textContent;
    const code = document.getElementById('page-script').textContent;
    const json = JSON.stringify(S, null, 1).replace(/</g, '\\u003c');
    return '<!doctype html><html><head><meta charset=utf8><meta name=viewport content="width=device-width,initial-scale=1,viewport-fit=cover"><style>' + RESET + '</style></head><body>'
      + `<title>${esc(S.meta.title)}</title>\n<meta name="description" content="${esc(S.meta.description)}">\n${FONTS}\n`
      + `<style id="page-style">${css}</style>\n<div id="app"></div>\n<div id="edbar" class="edbar" hidden></div>\n`
      + `<script type="application/json" id="content">${json}<\/script>\n<script id="page-script">${code}<\/script>\n</body></html>`;
  }

  const READ_ONLY = ['not_writer', 'not_granted', 'not_declared', 'consent_required', 'capability_disabled', 'capability_removed'];
  async function save() {
    if (busy) return;
    if (!dirty) { editing = false; linksOpen = false; message = ''; render(); renderBar(); return; }
    busy = true; message = ''; renderBar();
    const html = buildDoc();
    try {
      try {
        await art.publish({ 'index.html': { content: html, contentType: 'text/html' } });
      } catch (e) {
        if (!e || e.code !== 'capability_disabled') throw e;
        await art.publish(html);
      }
      dirty = false; editing = false; linksOpen = false; message = '保存しました。';
      render();
    } catch (e) {
      const code = e && e.code;
      if (code === 'conflict') message = 'ほかの画面で先に保存されていました。最新の内容を読み込み直します。';
      else if (READ_ONLY.includes(code)) { message = 'この画面からは保存できません（閲覧のみ）。'; canEdit = false; editing = false; render(); }
      else if (code === 'too_large') message = 'ページが大きすぎて保存できません。写真を小さくしてください。';
      else if (code === 'rate_limited') message = '保存が続いています。少し待ってから、もう一度保存してください。';
      else message = '保存できませんでした。もう一度「保存する」を押してください。';
    }
    busy = false; renderBar();
  }

  async function exportHtml() {
    if (!downloads) return;
    try {
      await downloads.save({ filename: 'index.html', data: buildDoc() });
      message = '書き出しました。自分のサイトに置くときは、img と photos のフォルダも一緒に置いてください。';
    } catch (e) {
      message = e && e.code === 'declined' ? '' : '書き出せませんでした。';
    }
    renderBar();
  }

  // ===== 操作 =====
  app.addEventListener('input', (e) => {
    const k = e.target.closest('[data-k]');
    if (k && editing) set(k.dataset.k, k.textContent.replace(/ /g, ' ').trim());
  });
  app.addEventListener('click', (e) => {
    if (!editing) return;
    const a = e.target.closest('a');
    if (a) e.preventDefault();
    const del = e.target.closest('[data-del]');
    if (del) {
      const p = del.dataset.del, ks = p.split('.'), i = Number(ks.pop());
      get(ks.join('.')).splice(i, 1); dirty = true; render(); renderBar(); return;
    }
    const add = e.target.closest('[data-add]');
    if (add) {
      const p = add.dataset.add;
      get(p).push(NEW[p] ? NEW[p]() : (p.endsWith('.facts') ? { k: '項目', v: '内容' } : '')); dirty = true; render(); renderBar(); return;
    }
    const img = e.target.closest('[data-img]');
    if (img) {
      if (!assets) { message = '写真の差し替えは、編集できる人の画面でだけ使えます。'; renderBar(); return; }
      imgTarget = img.dataset.img; fileInput.click();
    }
  });
  app.addEventListener('keydown', (e) => {
    if (editing && e.key === 'Enter' && e.target.closest('[data-k]') && !e.target.closest('p, blockquote, figcaption')) e.preventDefault();
  });

  const fileInput = document.createElement('input');
  fileInput.type = 'file'; fileInput.accept = 'image/*'; fileInput.hidden = true;
  document.body.appendChild(fileInput);
  fileInput.addEventListener('change', async () => {
    const f = fileInput.files && fileInput.files[0];
    fileInput.value = '';
    if (!f || !imgTarget) return;
    message = '写真を送っています…'; renderBar();
    try {
      const r = await assets.upload(f);
      set(imgTarget, r.url); message = '写真を差し替えました。「保存する」で確定します。'; render();
    } catch (e) {
      message = e && e.code === 'too_large' ? '写真が大きすぎます（20MBまで）。' : '写真を送れませんでした。';
    }
    renderBar();
  });

  bar.addEventListener('click', (e) => {
    const act = e.target.closest('[data-act]');
    if (!act) return;
    const a = act.dataset.act;
    if (a === 'edit') { editing = true; message = ''; render(); renderBar(); }
    else if (a === 'cancel') { location.reload(); }
    else if (a === 'save') save();
    else if (a === 'links') { linksOpen = !linksOpen; renderBar(); }
    else if (a === 'export') exportHtml();
  });
  bar.addEventListener('input', (e) => {
    const l = e.target.dataset.linkK, m = e.target.dataset.metaK;
    if (l) S.links[l] = e.target.value.trim();
    if (m) S.meta[m] = e.target.value;
    if ((l || m) && !dirty) { dirty = true; const sb = bar.querySelector('[data-act=save]'); if (sb) sb.textContent = '保存する'; }
  });
  bar.addEventListener('change', () => render()); // リンク先をボタンに反映（入力欄は作り直さない）

  render();

  // 編集できる人にだけ、編集バーを出す（claude.ai の上で開いたときだけ）
  (async () => {
    if (!window.claude || !window.claude.use) return;
    const [a, u, as, dl] = await Promise.all(['artifact', 'user', 'assets', 'downloads'].map((n) => window.claude.use(n).catch(() => null)));
    art = a; assets = as; downloads = dl;
    canEdit = !!(art && u && await u.canEdit().catch(() => false));
    renderBar();
  })();
})();
