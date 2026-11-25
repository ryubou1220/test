/* ひとりビジネス戦略室 — データはブラウザの localStorage に保存されます */
(() => {
  'use strict';

  const STORAGE_KEY = 'solo-strategy-room:v1';
  const STATUS = { idea: 'アイデア', doing: '進行中', done: '完了' };

  // ---------- utils ----------
  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];
  const uid = () => Math.random().toString(36).slice(2, 10) + Date.now().toString(36).slice(-4);
  const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const today = () => new Date().toISOString().slice(0, 10);
  const fmtNum = (n) => (Number.isFinite(n) ? n.toLocaleString('ja-JP', { maximumFractionDigits: 2 }) : '—');
  const fmtDate = (d) => {
    if (!d) return '';
    const [y, m, day] = d.split('-');
    return `${y}/${Number(m)}/${Number(day)}`;
  };
  const clamp = (v, lo, hi) => Math.min(hi, Math.max(lo, v));
  const currentQuarter = () => {
    const d = new Date();
    return `${d.getFullYear()} Q${Math.floor(d.getMonth() / 3) + 1}`;
  };
  const daysAgo = (n) => {
    const d = new Date();
    d.setDate(d.getDate() - n);
    return d.toISOString().slice(0, 10);
  };

  // ---------- state ----------
  function sampleData() {
    const g1 = uid(), g2 = uid();
    return {
      vision: '小さく、強く、長く続く事業をつくる',
      mission: '個人事業主の「迷う時間」を減らし、本業に集中できる時間を増やす。',
      goals: [
        { id: g1, title: '月の売上を安定させる', period: currentQuarter(), keyResults: [
          { id: uid(), text: '月次売上 50万円を3か月連続で達成', done: false },
          { id: uid(), text: '継続契約のクライアントを3社にする', done: true },
          { id: uid(), text: '単価を15%上げた新プランを用意する', done: false },
        ] },
        { id: g2, title: '集客の仕組みをつくる', period: currentQuarter(), keyResults: [
          { id: uid(), text: 'メルマガ読者 500人', done: false },
          { id: uid(), text: '毎週1本ブログ記事を公開', done: true },
        ] },
      ],
      kpis: [
        { id: uid(), name: '月次売上', unit: '万円', target: 50, better: 'up', entries: [
          { date: daysAgo(150), value: 28 }, { date: daysAgo(120), value: 31 }, { date: daysAgo(90), value: 35 },
          { date: daysAgo(60), value: 33 }, { date: daysAgo(30), value: 41 }, { date: daysAgo(1), value: 44 },
        ] },
        { id: uid(), name: 'メルマガ読者', unit: '人', target: 500, better: 'up', entries: [
          { date: daysAgo(90), value: 120 }, { date: daysAgo(60), value: 180 }, { date: daysAgo(30), value: 260 }, { date: daysAgo(1), value: 310 },
        ] },
        { id: uid(), name: '週の作業時間', unit: '時間', target: 40, better: 'down', entries: [
          { date: daysAgo(28), value: 52 }, { date: daysAgo(21), value: 49 }, { date: daysAgo(14), value: 47 }, { date: daysAgo(7), value: 45 },
        ] },
      ],
      tasks: [
        { id: uid(), title: '新料金プランのLPを作る', status: 'doing', impact: 5, effort: 3, goalId: g1, due: daysAgo(-10), note: '' },
        { id: uid(), title: '既存客に事例インタビューを依頼', status: 'doing', impact: 4, effort: 1, goalId: g2, due: daysAgo(-5), note: '' },
        { id: uid(), title: '請求・経理の自動化', status: 'idea', impact: 3, effort: 2, goalId: '', due: '', note: '' },
        { id: uid(), title: 'オンライン講座の企画', status: 'idea', impact: 5, effort: 5, goalId: g1, due: '', note: '' },
        { id: uid(), title: 'メルマガ登録フォーム設置', status: 'done', impact: 3, effort: 1, goalId: g2, due: daysAgo(14), note: '' },
      ],
      reviews: [
        { id: uid(), date: daysAgo(3), wins: '継続契約が1社決まった。ブログ経由の問い合わせが初めて来た。', problems: '制作作業に追われ、営業の時間が取れなかった。', next: 'LPの構成を決める／事例インタビューを2件依頼する', score: 4 },
      ],
    };
  }

  function load() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (raw) return normalize(JSON.parse(raw));
    } catch (e) { /* ignore */ }
    return sampleData();
  }

  function normalize(d) {
    return {
      vision: d.vision || '',
      mission: d.mission || '',
      goals: Array.isArray(d.goals) ? d.goals : [],
      kpis: Array.isArray(d.kpis) ? d.kpis : [],
      tasks: Array.isArray(d.tasks) ? d.tasks : [],
      reviews: Array.isArray(d.reviews) ? d.reviews : [],
    };
  }

  let state = load();

  function save() {
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(state)); } catch (e) { /* ignore */ }
    render();
  }

  // ---------- derived ----------
  const goalProgress = (g) => {
    const krs = g.keyResults || [];
    if (!krs.length) return 0;
    return Math.round((krs.filter((k) => k.done).length / krs.length) * 100);
  };
  const sortedEntries = (k) => [...(k.entries || [])].sort((a, b) => a.date.localeCompare(b.date));
  const latest = (k) => { const e = sortedEntries(k); return e.length ? e[e.length - 1].value : NaN; };
  const previous = (k) => { const e = sortedEntries(k); return e.length > 1 ? e[e.length - 2].value : NaN; };
  const kpiAchievement = (k) => {
    const v = latest(k), t = targetOf(k);
    if (!Number.isFinite(v) || !Number.isFinite(t) || t === 0) return NaN;
    return k.better === 'down' ? (v <= t ? 100 : Math.round((t / v) * 100)) : Math.round((v / t) * 100);
  };
  const targetOf = (k) => (k.target === null || k.target === undefined || k.target === '' ? NaN : Number(k.target));
  const priorityScore = (t) => (Number(t.impact) || 1) / (Number(t.effort) || 1);
  const goalTitle = (id) => state.goals.find((g) => g.id === id)?.title || '';

  // ---------- sparkline ----------
  function sparkline(k) {
    const pts = sortedEntries(k);
    if (pts.length < 2) return '<svg class="spark" viewBox="0 0 200 44"></svg>';
    const vals = pts.map((p) => Number(p.value));
    const target = targetOf(k);
    const all = Number.isFinite(target) ? [...vals, target] : vals;
    let lo = Math.min(...all), hi = Math.max(...all);
    if (lo === hi) { lo -= 1; hi += 1; }
    const pad = (hi - lo) * 0.1;
    lo -= pad; hi += pad;
    const x = (i) => (i / (vals.length - 1)) * 200;
    const y = (v) => 44 - ((v - lo) / (hi - lo)) * 44;
    const line = vals.map((v, i) => `${i ? 'L' : 'M'}${x(i).toFixed(1)},${y(v).toFixed(1)}`).join(' ');
    const area = `${line} L200,44 L0,44 Z`;
    const goal = Number.isFinite(target) ? `<line class="goal" x1="0" x2="200" y1="${y(target).toFixed(1)}" y2="${y(target).toFixed(1)}" vector-effect="non-scaling-stroke"/>` : '';
    return `<svg class="spark" viewBox="0 0 200 44" preserveAspectRatio="none" role="img" aria-label="${esc(k.name)}の推移">
      <path class="area" d="${area}"/>${goal}
      <path class="line" d="${line}" vector-effect="non-scaling-stroke"/>
    </svg>`;
  }

  function kpiCard(k, detailed) {
    const v = latest(k), p = previous(k);
    const ach = kpiAchievement(k);
    let delta = '';
    if (Number.isFinite(v) && Number.isFinite(p) && v !== p) {
      const diff = v - p;
      const good = k.better === 'down' ? diff < 0 : diff > 0;
      delta = `<span class="delta ${good ? 'up' : 'down'}">${diff > 0 ? '▲' : '▼'} ${fmtNum(Math.abs(diff))}</span>`;
    }
    const log = detailed ? `<div class="kpi-log">${sortedEntries(k).reverse().map((e) =>
      `<div><span>${fmtDate(e.date)}</span><span>${fmtNum(Number(e.value))}${esc(k.unit)} <button data-act="del-entry" data-kpi="${k.id}" data-date="${esc(e.date)}" title="この記録を削除">×</button></span></div>`
    ).join('') || '<div class="empty">記録がありません</div>'}</div>` : '';
    const actions = detailed ? `<div class="kpi-actions">
        <button class="small" data-act="add-entry" data-kpi="${k.id}">＋ 記録</button>
        <button class="small ghost" data-act="edit-kpi" data-kpi="${k.id}">編集</button>
      </div>` : '';
    return `<div class="kpi">
      <div class="kpi-head"><span class="name">${esc(k.name)}</span>${delta}</div>
      <div><span class="now">${fmtNum(v)}</span><span class="unit">${esc(k.unit)}</span></div>
      ${sparkline(k)}
      <div class="target">目標 ${Number.isFinite(targetOf(k)) ? fmtNum(targetOf(k)) + esc(k.unit) + (k.better === 'down' ? ' 以下' : '') : '未設定'}${Number.isFinite(ach) ? ` ・ 達成率 ${ach}%` : ''}</div>
      <div class="bar" style="margin-top:6px"><i style="width:${Number.isFinite(ach) ? clamp(ach, 0, 100) : 0}%"></i></div>
      ${actions}${log}
    </div>`;
  }

  // ---------- render ----------
  function render() {
    renderOverview();
    renderGoals();
    renderKpis();
    renderBoard();
    renderReviews();
  }

  function renderOverview() {
    $('#vision-text').textContent = state.vision || 'ビジョンを設定しましょう';
    $('#mission-text').textContent = state.mission || '';

    const doing = state.tasks.filter((t) => t.status === 'doing');
    const done = state.tasks.filter((t) => t.status === 'done');
    const avgGoal = state.goals.length ? Math.round(state.goals.reduce((s, g) => s + goalProgress(g), 0) / state.goals.length) : 0;
    const achs = state.kpis.map(kpiAchievement).filter(Number.isFinite);
    const avgKpi = achs.length ? Math.round(achs.reduce((a, b) => a + Math.min(b, 100), 0) / achs.length) : 0;
    const lastReview = [...state.reviews].sort((a, b) => b.date.localeCompare(a.date))[0];
    const daysSince = lastReview ? Math.floor((Date.now() - new Date(lastReview.date).getTime()) / 86400000) : null;

    $('#stats').innerHTML = [
      ['目標の進捗', `${avgGoal}%`, `${state.goals.length}件の目標`],
      ['KPI 達成率', `${avgKpi}%`, `${state.kpis.length}個のKPI（平均）`],
      ['進行中の施策', `${doing.length}`, `完了 ${done.length} / 全 ${state.tasks.length}`],
      ['前回の振り返り', daysSince === null ? '—' : daysSince === 0 ? '今日' : `${daysSince}日前`, daysSince !== null && daysSince > 7 ? '⚠ 1週間以上空いています' : '週1回が目安'],
    ].map(([l, v, s]) => `<div class="stat"><div class="label">${l}</div><div class="value">${v}</div><div class="sub">${s}</div></div>`).join('');

    const focus = [...doing].sort((a, b) => priorityScore(b) - priorityScore(a)).slice(0, 5);
    $('#focus-list').innerHTML = focus.length
      ? focus.map((t) => `<li>${esc(t.title)}<span class="meta">インパクト${t.impact}・工数${t.effort}${t.due ? `・期限 ${fmtDate(t.due)}` : ''}</span></li>`).join('')
      : '<li class="empty">進行中の施策はありません。施策ボードから「進行中」に移しましょう。</li>';

    $('#goal-progress').innerHTML = state.goals.length
      ? state.goals.map((g) => { const p = goalProgress(g); return `<div class="goal-row"><div class="top"><span>${esc(g.title)}</span><span class="pct">${p}%</span></div><div class="bar"><i style="width:${p}%"></i></div></div>`; }).join('')
      : '<p class="empty">目標がまだありません。</p>';

    $('#kpi-overview').innerHTML = state.kpis.length ? state.kpis.map((k) => kpiCard(k, false)).join('') : '<p class="empty">KPIがまだありません。</p>';

    $('#latest-review').innerHTML = lastReview ? reviewBody(lastReview) : '<p class="empty">まだ振り返りがありません。週に一度、15分だけ時間を取りましょう。</p>';
  }

  function renderGoals() {
    $('#goal-list').innerHTML = state.goals.length ? state.goals.map((g) => {
      const p = goalProgress(g);
      const linked = state.tasks.filter((t) => t.goalId === g.id);
      return `<div class="card goal-card">
        <div class="goal-head">
          <div><div class="period">${esc(g.period)}</div><h2>${esc(g.title)}</h2></div>
          <button class="ghost small" data-act="edit-goal" data-goal="${g.id}">編集</button>
        </div>
        <div class="goal-row"><div class="top"><span>主要な成果 ${g.keyResults.filter((k) => k.done).length} / ${g.keyResults.length}</span><span class="pct">${p}%</span></div><div class="bar"><i style="width:${p}%"></i></div></div>
        <ul class="kr-list">${g.keyResults.map((kr) => `<li class="${kr.done ? 'done' : ''}">
          <input type="checkbox" data-act="toggle-kr" data-goal="${g.id}" data-kr="${kr.id}" ${kr.done ? 'checked' : ''} aria-label="達成">
          <span>${esc(kr.text)}</span></li>`).join('')}</ul>
        ${linked.length ? `<div class="linked">関連する施策：${linked.map((t) => `${esc(t.title)}（${STATUS[t.status]}）`).join('、')}</div>` : ''}
      </div>`;
    }).join('') : '<div class="card empty">「＋ 目標を追加」から、今期に達成したいことを2〜3個に絞って書きましょう。</div>';
  }

  function renderKpis() {
    $('#kpi-list').innerHTML = state.kpis.length
      ? state.kpis.map((k) => kpiCard(k, true)).join('')
      : '<div class="card empty">売上・顧客数・作業時間など、毎月追いかける数字を登録しましょう。</div>';
  }

  function renderBoard() {
    const todayStr = today();
    $$('#board .column').forEach((col) => {
      const status = col.dataset.status;
      const items = state.tasks.filter((t) => t.status === status).sort((a, b) => priorityScore(b) - priorityScore(a));
      $('.count', col).textContent = items.length;
      $('.cards', col).innerHTML = items.map((t) => {
        const keys = Object.keys(STATUS), i = keys.indexOf(t.status);
        const overdue = t.due && t.status !== 'done' && t.due < todayStr;
        return `<div class="task" draggable="true" data-task="${t.id}">
          <div class="title">${esc(t.title)}</div>
          <div class="tags">
            <span class="tag ${priorityScore(t) >= 2 ? 'hi' : ''}">インパクト${t.impact}・工数${t.effort}</span>
            ${t.goalId && goalTitle(t.goalId) ? `<span class="tag">🎯 ${esc(goalTitle(t.goalId))}</span>` : ''}
            ${t.due ? `<span class="tag ${overdue ? 'overdue' : ''}">期限 ${fmtDate(t.due)}</span>` : ''}
          </div>
          <div class="move">
            ${i > 0 ? `<button class="ghost" data-act="move" data-task="${t.id}" data-to="${keys[i - 1]}" aria-label="${STATUS[keys[i - 1]]}へ戻す">←</button>` : ''}
            ${i < keys.length - 1 ? `<button class="ghost" data-act="move" data-task="${t.id}" data-to="${keys[i + 1]}" aria-label="${STATUS[keys[i + 1]]}へ進める">→</button>` : ''}
            <span class="spacer"></span>
            <button class="ghost" data-act="edit-task" data-task="${t.id}">編集</button>
          </div>
        </div>`;
      }).join('');
    });
  }

  function reviewBody(r) {
    return `<dl>
      <dt>うまくいった</dt><dd>${esc(r.wins) || '—'}</dd>
      <dt>課題・詰まり</dt><dd>${esc(r.problems) || '—'}</dd>
      <dt>来週やること</dt><dd>${esc(r.next) || '—'}</dd>
      <dt>手応え</dt><dd>${'★'.repeat(r.score || 0)}${'☆'.repeat(5 - (r.score || 0))}</dd>
    </dl>`;
  }

  function renderReviews() {
    const list = [...state.reviews].sort((a, b) => b.date.localeCompare(a.date));
    $('#review-list').innerHTML = list.length ? list.map((r) => `<div class="card review">
      <div class="date"><span>${fmtDate(r.date)} の週</span><button class="ghost small" data-act="edit-review" data-review="${r.id}">編集</button></div>
      ${reviewBody(r)}
    </div>`).join('') : '<div class="card empty">まだ振り返りがありません。</div>';
  }

  // ---------- modal ----------
  const modal = $('#modal');
  let modalHandlers = null;

  function openModal({ title, body, onSave, onDelete, onOpen }) {
    $('#modal-title').textContent = title;
    $('#modal-body').innerHTML = body;
    $('#modal-delete').hidden = !onDelete;
    modalHandlers = { onSave, onDelete };
    if (onOpen) onOpen($('#modal-body'));
    modal.showModal();
    const first = $('#modal-body input, #modal-body textarea, #modal-body select');
    if (first) first.focus();
  }
  const closeModal = () => { modal.close(); modalHandlers = null; };

  $('#modal-form').addEventListener('submit', (e) => {
    e.preventDefault();
    if (!modalHandlers) return;
    const form = $('#modal-form');
    if (!form.reportValidity()) return;
    const ok = modalHandlers.onSave(form);
    if (ok !== false) { closeModal(); save(); }
  });
  $('#modal-cancel').addEventListener('click', closeModal);
  $('#modal-delete').addEventListener('click', () => {
    if (modalHandlers?.onDelete && confirm('削除してよろしいですか？')) {
      modalHandlers.onDelete();
      closeModal();
      save();
    }
  });

  const field = (label, html) => `<label class="field"><span>${label}</span>${html}</label>`;
  const val = (form, name) => form.elements[name]?.value.trim() ?? '';
  const scaleOptions = (sel) => [1, 2, 3, 4, 5].map((n) => `<option value="${n}" ${Number(sel) === n ? 'selected' : ''}>${n}</option>`).join('');

  function editVision() {
    openModal({
      title: 'ビジョンとミッション',
      body: field('ビジョン（目指す姿をひとことで）', `<input name="vision" value="${esc(state.vision)}">`) +
            field('ミッション（誰に・何を・どう届けるか）', `<textarea name="mission">${esc(state.mission)}</textarea>`),
      onSave: (f) => { state.vision = val(f, 'vision'); state.mission = val(f, 'mission'); },
    });
  }

  function editGoal(id) {
    const g = state.goals.find((x) => x.id === id);
    const krs = g ? g.keyResults : [{ id: uid(), text: '', done: false }];
    const krRow = (kr) => `<div class="kr-edit" data-kr="${kr.id}" data-done="${kr.done ? 1 : 0}"><input name="kr" value="${esc(kr.text)}" placeholder="例：月次売上 50万円を達成"><button type="button" class="ghost small" data-rm>×</button></div>`;
    openModal({
      title: g ? '目標を編集' : '目標を追加',
      body: field('目標', `<input name="title" required value="${esc(g?.title)}" placeholder="例：月の売上を安定させる">`) +
            field('期間', `<input name="period" value="${esc(g?.period || currentQuarter())}">`) +
            `<div class="field"><span style="font-size:13px;color:var(--muted)">主要な成果（測定できる形で）</span><div id="kr-rows" style="margin-top:4px">${krs.map(krRow).join('')}</div>
             <button type="button" class="ghost small" id="kr-add">＋ 追加</button></div>`,
      onOpen: (root) => {
        $('#kr-add', root).addEventListener('click', () => {
          $('#kr-rows', root).insertAdjacentHTML('beforeend', krRow({ id: uid(), text: '', done: false }));
          $('#kr-rows .kr-edit:last-child input', root).focus();
        });
        $('#kr-rows', root).addEventListener('click', (e) => { if (e.target.matches('[data-rm]')) e.target.parentElement.remove(); });
      },
      onSave: (f) => {
        const keyResults = $$('#kr-rows .kr-edit', f)
          .map((row) => ({ id: row.dataset.kr, text: $('input', row).value.trim(), done: row.dataset.done === '1' }))
          .filter((k) => k.text);
        const data = { title: val(f, 'title'), period: val(f, 'period'), keyResults };
        if (g) Object.assign(g, data); else state.goals.push({ id: uid(), ...data });
      },
      onDelete: g ? () => {
        state.goals = state.goals.filter((x) => x.id !== id);
        state.tasks.forEach((t) => { if (t.goalId === id) t.goalId = ''; });
      } : null,
    });
  }

  function editKpi(id) {
    const k = state.kpis.find((x) => x.id === id);
    openModal({
      title: k ? 'KPIを編集' : 'KPIを追加',
      body: field('名前', `<input name="name" required value="${esc(k?.name)}" placeholder="例：月次売上">`) +
            `<div class="row">${field('単位', `<input name="unit" value="${esc(k?.unit)}" placeholder="例：万円">`)}
             ${field('目標値', `<input name="target" type="number" step="any" value="${esc(k?.target)}">`)}</div>` +
            field('良い方向', `<select name="better"><option value="up">大きいほど良い（売上・顧客数など）</option><option value="down" ${k?.better === 'down' ? 'selected' : ''}>小さいほど良い（作業時間・解約率など）</option></select>`) +
            (k ? '' : field('現在の値（任意）', `<input name="initial" type="number" step="any">`)),
      onSave: (f) => {
        const data = { name: val(f, 'name'), unit: val(f, 'unit'), target: val(f, 'target') === '' ? null : Number(val(f, 'target')), better: val(f, 'better') };
        if (k) Object.assign(k, data);
        else {
          const entries = val(f, 'initial') !== '' ? [{ date: today(), value: Number(val(f, 'initial')) }] : [];
          state.kpis.push({ id: uid(), ...data, entries });
        }
      },
      onDelete: k ? () => { state.kpis = state.kpis.filter((x) => x.id !== id); } : null,
    });
  }

  function addEntry(id) {
    const k = state.kpis.find((x) => x.id === id);
    if (!k) return;
    openModal({
      title: `${k.name} を記録`,
      body: `<div class="row">${field('日付', `<input name="date" type="date" required value="${today()}">`)}
             ${field(`値（${esc(k.unit) || '数値'}）`, `<input name="value" type="number" step="any" required>`)}</div>`,
      onSave: (f) => {
        const date = val(f, 'date'), value = Number(val(f, 'value'));
        k.entries = (k.entries || []).filter((e) => e.date !== date);
        k.entries.push({ date, value });
      },
    });
  }

  function editTask(id) {
    const t = state.tasks.find((x) => x.id === id);
    const goalOpts = `<option value="">（なし）</option>` + state.goals.map((g) => `<option value="${g.id}" ${t?.goalId === g.id ? 'selected' : ''}>${esc(g.title)}</option>`).join('');
    const statusOpts = Object.entries(STATUS).map(([k, v]) => `<option value="${k}" ${(t?.status || 'idea') === k ? 'selected' : ''}>${v}</option>`).join('');
    openModal({
      title: t ? '施策を編集' : '施策を追加',
      body: field('施策', `<input name="title" required value="${esc(t?.title)}" placeholder="例：新料金プランのLPを作る">`) +
            `<div class="row">${field('インパクト（1〜5）', `<select name="impact">${scaleOptions(t?.impact ?? 3)}</select>`)}
             ${field('工数（1〜5）', `<select name="effort">${scaleOptions(t?.effort ?? 3)}</select>`)}</div>` +
            `<div class="row">${field('状態', `<select name="status">${statusOpts}</select>`)}
             ${field('期限', `<input name="due" type="date" value="${esc(t?.due)}">`)}</div>` +
            field('関連する目標', `<select name="goalId">${goalOpts}</select>`) +
            field('メモ', `<textarea name="note">${esc(t?.note)}</textarea>`),
      onSave: (f) => {
        const data = { title: val(f, 'title'), impact: Number(val(f, 'impact')), effort: Number(val(f, 'effort')), status: val(f, 'status'), due: val(f, 'due'), goalId: val(f, 'goalId'), note: val(f, 'note') };
        if (t) Object.assign(t, data); else state.tasks.push({ id: uid(), ...data });
      },
      onDelete: t ? () => { state.tasks = state.tasks.filter((x) => x.id !== id); } : null,
    });
  }

  function editReview(id) {
    const r = state.reviews.find((x) => x.id === id);
    const doingNow = state.tasks.filter((t) => t.status === 'doing').map((t) => t.title);
    openModal({
      title: r ? '振り返りを編集' : '今週の振り返り',
      body: field('日付', `<input name="date" type="date" required value="${esc(r?.date || today())}">`) +
            field('うまくいったこと', `<textarea name="wins" placeholder="成果・前進・学び">${esc(r?.wins)}</textarea>`) +
            field('課題・詰まっていること', `<textarea name="problems" placeholder="時間が取れなかったこと、迷っていること">${esc(r?.problems)}</textarea>`) +
            field('来週やること（3つまで）', `<textarea name="next" placeholder="${esc(doingNow.slice(0, 3).join('／') || '最も効果の高いことから')}">${esc(r?.next)}</textarea>`) +
            field('今週の手応え', `<select name="score">${scaleOptions(r?.score ?? 3)}</select>`),
      onSave: (f) => {
        const data = { date: val(f, 'date'), wins: val(f, 'wins'), problems: val(f, 'problems'), next: val(f, 'next'), score: Number(val(f, 'score')) };
        if (r) Object.assign(r, data); else state.reviews.push({ id: uid(), ...data });
      },
      onDelete: r ? () => { state.reviews = state.reviews.filter((x) => x.id !== id); } : null,
    });
  }

  // ---------- events ----------
  function showTab(name) {
    $$('.tabs button').forEach((b) => b.setAttribute('aria-selected', String(b.dataset.tab === name)));
    $$('.tab-panel').forEach((p) => { p.hidden = p.id !== `tab-${name}`; });
    try { sessionStorage.setItem(STORAGE_KEY + ':tab', name); } catch (e) { /* ignore */ }
  }
  $$('.tabs button').forEach((b) => b.addEventListener('click', () => showTab(b.dataset.tab)));

  $('#btn-edit-vision').addEventListener('click', editVision);
  $('#btn-add-goal').addEventListener('click', () => editGoal());
  $('#btn-add-kpi').addEventListener('click', () => editKpi());
  $('#btn-add-task').addEventListener('click', () => editTask());
  $('#btn-add-review').addEventListener('click', () => editReview());

  document.addEventListener('click', (e) => {
    const el = e.target.closest('[data-act]');
    if (!el || el.closest('dialog')) return;
    const { act } = el.dataset;
    if (act === 'edit-goal') editGoal(el.dataset.goal);
    else if (act === 'edit-kpi') editKpi(el.dataset.kpi);
    else if (act === 'add-entry') addEntry(el.dataset.kpi);
    else if (act === 'del-entry') {
      const k = state.kpis.find((x) => x.id === el.dataset.kpi);
      if (k && confirm(`${fmtDate(el.dataset.date)} の記録を削除しますか？`)) { k.entries = k.entries.filter((x) => x.date !== el.dataset.date); save(); }
    } else if (act === 'edit-task') editTask(el.dataset.task);
    else if (act === 'move') {
      const t = state.tasks.find((x) => x.id === el.dataset.task);
      if (t) { t.status = el.dataset.to; save(); }
    } else if (act === 'edit-review') editReview(el.dataset.review);
  });

  document.addEventListener('change', (e) => {
    const el = e.target;
    if (el.dataset.act === 'toggle-kr') {
      const kr = state.goals.find((g) => g.id === el.dataset.goal)?.keyResults.find((k) => k.id === el.dataset.kr);
      if (kr) { kr.done = el.checked; save(); }
    }
  });

  // drag & drop on the board
  const board = $('#board');
  board.addEventListener('dragstart', (e) => {
    const card = e.target.closest('.task');
    if (!card) return;
    e.dataTransfer.setData('text/plain', card.dataset.task);
    e.dataTransfer.effectAllowed = 'move';
    card.classList.add('dragging');
  });
  board.addEventListener('dragend', (e) => e.target.closest('.task')?.classList.remove('dragging'));
  $$('.column', board).forEach((col) => {
    col.addEventListener('dragover', (e) => { e.preventDefault(); col.classList.add('drag-over'); });
    col.addEventListener('dragleave', (e) => { if (!col.contains(e.relatedTarget)) col.classList.remove('drag-over'); });
    col.addEventListener('drop', (e) => {
      e.preventDefault();
      col.classList.remove('drag-over');
      const t = state.tasks.find((x) => x.id === e.dataTransfer.getData('text/plain'));
      if (t && t.status !== col.dataset.status) { t.status = col.dataset.status; save(); }
    });
  });

  // export / import
  $('#btn-export').addEventListener('click', () => {
    const blob = new Blob([JSON.stringify(state, null, 2)], { type: 'application/json' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = `strategy-room-${today()}.json`;
    a.click();
    setTimeout(() => URL.revokeObjectURL(a.href), 1000);
  });
  $('#file-import').addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    try {
      const data = normalize(JSON.parse(await file.text()));
      if (confirm('現在のデータを読み込んだ内容で置き換えます。よろしいですか？')) { state = data; save(); }
    } catch (err) {
      alert('読み込みに失敗しました：JSONの形式を確認してください。');
    }
    e.target.value = '';
  });

  // ---------- init ----------
  let initialTab = 'overview';
  try { initialTab = sessionStorage.getItem(STORAGE_KEY + ':tab') || 'overview'; } catch (e) { /* ignore */ }
  showTab(initialTab);
  render();
})();
