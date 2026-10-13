// ウッドデッキの材料計算エンジン
// 計算ツール（deck-calculator）と図面セット（deck-plans）の両方で使う。
(function (global) {
  const SETTINGS = {
    contractorPerM2: { softwood: 40000, hardwood: 50000 }, // 業者の相場（材料＋施工、1㎡あたり）
    stoneTop: 100,      // 束石の地面から出ている高さ (mm)
    postMaxSpan: 900,   // 束柱の最大間隔 (mm)
    boardGap: 5,        // 床板のすき間 (mm)
    kerf: 3,            // ノコギリの刃の厚み (mm)
    negaramiMinPost: 300, // 束柱がこの長さ以上なら根がらみを入れる (mm)
  };

  // 木材の単価(ppm)は1mあたりの目安。地域の価格に書き換えて使う。
  const MATERIALS = {
    wrc: {
      label: 'ウエスタンレッドシダー', kind: 'softwood', paint: true, joistPitch: 455,
      hint: 'マニュアルの標準。軽くて加工しやすく、腐りにくい。',
      deck:  { name: '床板', spec: '2×6材 38×140', t: 38, w: 140, ppm: 1700, stocks: [1820, 2440, 3050, 3660] },
      joist: { name: '根太', spec: '2×4材 38×89',  t: 38, h: 89,  ppm: 1100, stocks: [1820, 2440, 3050, 3660] },
      beam:  { name: '大引', spec: '4×4材 89×89',  t: 89, h: 89,  ppm: 2500, stocks: [1820, 2440, 3050, 3660] },
      post:  { name: '束柱', spec: '4×4材 89×89',  t: 89, h: 89,  ppm: 2500, stocks: [1820, 2440, 3050, 3660] },
    },
    spf: {
      label: '防腐処理SPF', kind: 'softwood', paint: true, joistPitch: 455,
      hint: 'いちばん安い。数年ごとの塗り直しが必要。',
      deck:  { name: '床板', spec: '2×6材 38×140', t: 38, w: 140, ppm: 900,  stocks: [1820, 2440, 3050, 3660] },
      joist: { name: '根太', spec: '2×4材 38×89',  t: 38, h: 89,  ppm: 600,  stocks: [1820, 2440, 3050, 3660] },
      beam:  { name: '大引', spec: '4×4材 89×89',  t: 89, h: 89,  ppm: 1400, stocks: [1820, 3050, 3660] },
      post:  { name: '束柱', spec: '4×4材 89×89',  t: 89, h: 89,  ppm: 1400, stocks: [1820, 3050, 3660] },
    },
    ulin: {
      label: 'ハードウッド（ウリン）', kind: 'hardwood', paint: false, joistPitch: 400,
      hint: '重くて硬いがとても長持ち。塗装不要。ビス止めには下穴が必要。',
      deck:  { name: '床板', spec: '20×105', t: 20, w: 105, ppm: 1500, stocks: [2000, 2500, 3000, 3500, 4000] },
      joist: { name: '根太', spec: '45×90',  t: 45, h: 90,  ppm: 2600, stocks: [2000, 3000, 4000] },
      beam:  { name: '大引', spec: '45×90',  t: 45, h: 90,  ppm: 2600, stocks: [2000, 3000, 4000] },
      post:  { name: '束柱', spec: '90×90',  t: 90, h: 90,  ppm: 5500, stocks: [1000, 1500, 2000, 3000] },
    },
  };

  const OTHER = {
    stone: 900,                                          // 羽子板付き束石 1個
    cement: 700, sand: 350,                              // セメント25kg、砂20kg 1袋
    deckScrewBox: { qty: 100, soft: 1500, hard: 1900 },  // 床板用ステンレスビス
    frameScrewBox: { qty: 50, price: 1400 },             // 骨組み用ビス 75〜90mm
    paintCan: { liters: 3.4, price: 8500, m2PerLiter: 6 }, // 2回塗りで1Lあたり約6㎡
    sheetRoll: { m2: 10, price: 2500 },                  // 防草シート 1m×10m
    tools: 32000,                                        // インパクトドライバー・丸ノコ・水平器・さしがね等
  };

  const MEMBER_KEYS = ['deck', 'joist', 'beam', 'post'];

  // 支点（束柱・大引・根太）の上で継ぐように、長い部材を分割する
  function splitRun(L, nSpans, maxLen) {
    const span = L / nSpans;
    const k = Math.floor((maxLen + 0.5) / span);
    if (k < 1) { const n = Math.ceil(L / maxLen); return Array(n).fill(Math.round(L / n)); }
    const pieces = Math.ceil(nSpans / k);
    const base = Math.floor(nSpans / pieces), extra = nSpans % pieces;
    const out = [];
    for (let i = 0; i < pieces; i++) out.push(Math.round((base + (i < extra ? 1 : 0)) * span));
    return out;
  }

  // 定尺材から切り出す（1本ずつ、いちばんムダの少ない定尺を選ぶ）
  // pieces: [{ len, use }]  →  bins: [{ stock, cuts: [{ len, use }], waste }]
  function pack(pieces, stocks, kerf) {
    let rem = pieces.slice().sort((a, b) => b.len - a.len);
    const maxS = Math.max(...stocks);
    const bins = [];
    while (rem.length) {
      if (rem[0].len > maxS) {
        const p = rem.shift(), n = Math.ceil(p.len / maxS);
        for (let i = 0; i < n; i++) rem.push({ len: Math.round(p.len / n), use: p.use });
        rem.sort((a, b) => b.len - a.len);
        continue;
      }
      let best = null;
      for (const s of stocks) {
        if (s < rem[0].len) continue;
        let free = s; const cuts = [], left = [];
        for (const p of rem) {
          const need = cuts.length ? p.len + kerf : p.len;
          if (need <= free) { cuts.push(p); free -= need; } else left.push(p);
        }
        const util = (s - free) / s;
        if (!best || util > best.util + 1e-9 || (Math.abs(util - best.util) < 1e-9 && s > best.stock)) best = { stock: s, cuts, left, util, free };
      }
      bins.push({ stock: best.stock, cuts: best.cuts, waste: Math.max(0, best.free) });
      rem = best.left;
    }
    return bins;
  }

  function countStocks(bins) {
    const m = new Map();
    for (const b of bins) m.set(b.stock, (m.get(b.stock) || 0) + 1);
    return [...m.entries()].sort((a, b) => b[0] - a[0]);
  }

  // 同じ切り方の定尺材をまとめる（カット表用）
  function groupBins(bins) {
    const m = new Map();
    for (const b of bins) {
      const key = b.stock + ':' + b.cuts.map((c) => c.use + c.len).join('|');
      if (!m.has(key)) m.set(key, { stock: b.stock, cuts: b.cuts, waste: b.waste, count: 0 });
      m.get(key).count++;
    }
    return [...m.values()].sort((a, b) => b.stock - a.stock || b.count - a.count);
  }

  const unitPrice = (ppm, stock) => Math.round((ppm * stock) / 1000 / 10) * 10;

  // inp: { w, d, h (cm), mat, maku, sheet, tools }  prices: { deck, joist, beam, post } 円/m（省略可）
  function calculate(inp, prices) {
    const S = SETTINGS;
    const mat = MATERIALS[inp.mat];
    const P = {};
    for (const k of MEMBER_KEYS) P[k] = prices && Number.isFinite(prices[k]) ? prices[k] : mat[k].ppm;
    const W = inp.w * 10, D = inp.d * 10, H = inp.h * 10;
    const warns = [];

    const nx = Math.ceil(W / S.postMaxSpan) + 1;
    const ny = Math.ceil(D / S.postMaxSpan) + 1;
    const nj = Math.ceil(W / mat.joistPitch) + 1;
    const nb = Math.ceil((D + S.boardGap) / (mat.deck.w + S.boardGap));
    const posts = nx * ny;
    // 位置は部材の中心。外周の部材は外面をデッキの端にそろえる。
    const pa = mat.post.t, jt = mat.joist.t;
    const postXs = Array.from({ length: nx }, (_, i) => Math.round(pa / 2 + (i * (W - pa)) / (nx - 1)));
    const beamYs = Array.from({ length: ny }, (_, i) => Math.round(pa / 2 + (i * (D - pa)) / (ny - 1)));
    const joistXs = Array.from({ length: nj }, (_, i) => Math.round(jt / 2 + (i * (W - jt)) / (nj - 1)));
    const lastBoardW = mat.deck.w - (nb * mat.deck.w + (nb - 1) * S.boardGap - D);

    const stack = mat.deck.t + mat.joist.h + mat.beam.h + S.stoneTop;
    let postLen = H - stack;
    const minH = Math.ceil((stack + 60) / 50) * 5;
    if (postLen < 60) {
      warns.push(`高さ${inp.h}cmでは束柱を立てる余裕がありません。この木材なら高さ${minH}cm以上にするか、束石の上に大引を直接のせる低いデッキの組み方になります。`);
      postLen = 60;
    }
    postLen = Math.round(postLen);

    const maxStock = (k) => Math.max(...mat[k].stocks);
    const add = (arr, lens, use) => lens.forEach((len) => arr.push({ len, use }));
    const pieces = { deck: [], joist: [], beam: [], post: [] };
    for (let i = 0; i < ny; i++) add(pieces.beam, splitRun(W, nx - 1, maxStock('beam')), '大引');
    for (let i = 0; i < nj; i++) add(pieces.joist, splitRun(D, ny - 1, maxStock('joist')), '根太');
    for (let i = 0; i < nb; i++) add(pieces.deck, splitRun(W, nj - 1, maxStock('deck')), '床板');
    for (let i = 0; i < posts; i++) pieces.post.push({ len: postLen, use: '束柱' });
    if (inp.maku) {
      add(pieces.deck, splitRun(W, nj - 1, maxStock('deck')), '幕板(正面)');
      for (let i = 0; i < 2; i++) add(pieces.deck, splitRun(D, ny - 1, maxStock('deck')), '幕板(側面)');
    }
    const negarami = postLen >= S.negaramiMinPost;
    if (negarami) {
      for (let i = 0; i < 2; i++) add(pieces.joist, splitRun(W, nx - 1, maxStock('joist')), '根がらみ(横)');
      for (let i = 0; i < 2; i++) add(pieces.joist, splitRun(D, ny - 1, maxStock('joist')), '根がらみ(縦)');
    }

    const rows = [];
    const lumber = {};
    let total = 0, paintArea = 0;
    const addRow = (group, name, spec, qty, unit, amount, note, qtyUnit) => {
      rows.push({ group, name, spec, qty, unit, amount, note, qtyUnit });
      total += amount;
    };
    const uses = { deck: inp.maku ? '床板・幕板' : '床板', joist: negarami ? '根太・根がらみ' : '根太', beam: '大引', post: '束柱' };

    for (const key of MEMBER_KEYS) {
      const m = mat[key];
      const bins = pack(pieces[key], m.stocks, S.kerf);
      const counts = countStocks(bins);
      const spare = key === 'deck' || key === 'joist';
      if (spare) { const most = counts.reduce((a, b) => (b[1] > a[1] ? b : a)); most[1] += 1; }
      const runLen = pieces[key].reduce((a, b) => a + b.len, 0);
      const perim = key === 'deck' ? 2 * (m.w + m.t) : 2 * (m.t + m.h);
      paintArea += (runLen * perim) / 1e6;
      lumber[key] = { member: m, use: uses[key], bins, groups: groupBins(bins), counts, runLen, spare, ppm: P[key] };
      counts.forEach(([s, n], idx) => {
        const unit = unitPrice(P[key], s);
        const note = idx === 0 ? `必要な長さの合計 約${(runLen / 1000).toFixed(1)}m` + (spare ? '（予備1本込み）' : '') : '';
        addRow('木材', uses[key], `${m.spec}　${s}mm`, n, unit, unit * n, note, '本');
      });
    }

    addRow('基礎', '羽子板付き束石', '束柱1本に1個', posts, OTHER.stone, posts * OTHER.stone, '', '個');
    const cementBags = Math.ceil(posts / 8), sandBags = Math.ceil(posts / 4);
    addRow('基礎', 'セメント・砂', `セメント25kg×${cementBags}袋、砂20kg×${sandBags}袋`, 1, 0, cementBags * OTHER.cement + sandBags * OTHER.sand, '束石を据えるモルタル用', '式');

    const deckScrews = Math.ceil(nb * nj * 2 * 1.1);
    const frameScrews = Math.ceil((posts * 4 + nj * ny * 3 + (negarami ? posts * 3 : 0) + (inp.maku ? (nj + ny * 2) * 2 : 0)) * 1.1);
    const dBox = Math.ceil(deckScrews / OTHER.deckScrewBox.qty);
    const fBox = Math.ceil(frameScrews / OTHER.frameScrewBox.qty);
    const dPrice = mat.kind === 'hardwood' ? OTHER.deckScrewBox.hard : OTHER.deckScrewBox.soft;
    addRow('金物・ビス', '床板用ステンレスビス', `${OTHER.deckScrewBox.qty}本入り（約${deckScrews}本）`, dBox, dPrice, dBox * dPrice, mat.kind === 'hardwood' ? 'ハードウッド用。下穴をあけてから打つ' : '', '箱');
    addRow('金物・ビス', '骨組み用ビス 75〜90mm', `${OTHER.frameScrewBox.qty}本入り（約${frameScrews}本）`, fBox, OTHER.frameScrewBox.price, fBox * OTHER.frameScrewBox.price, '1か所に3本以上', '箱');

    if (mat.paint) {
      const liters = paintArea / OTHER.paintCan.m2PerLiter;
      const cans = Math.max(1, Math.ceil(liters / OTHER.paintCan.liters));
      addRow('仕上げ', '木材保護塗料', `${OTHER.paintCan.liters}L缶（全面2回塗り 約${paintArea.toFixed(0)}㎡）`, cans, OTHER.paintCan.price, cans * OTHER.paintCan.price, '組む前に塗ると、見えない部分まで塗れる', '缶');
    }
    if (inp.sheet) {
      const area = ((W + 600) * (D + 600)) / 1e6;
      const rolls = Math.ceil(area / OTHER.sheetRoll.m2);
      addRow('仕上げ', '防草シート', `1m×10m（約${area.toFixed(1)}㎡）`, rolls, OTHER.sheetRoll.price, rolls * OTHER.sheetRoll.price, '', '巻');
    }
    if (inp.tools) addRow('工具', '工具一式', 'インパクトドライバー・丸ノコ・水平器・さしがね・メジャー・水糸', 1, OTHER.tools, OTHER.tools, '次のDIYにも使えます', '式');

    const areaM2 = (W * D) / 1e6;
    const pro = areaM2 * S.contractorPerM2[mat.kind];
    const days = areaM2 <= 7 ? 3 : 3 + Math.ceil((areaM2 - 7) / 5);
    return {
      inp, rows, total, pro, areaM2, days, warns, mat, lumber,
      screws: { deck: deckScrews, frame: frameScrews },
      geo: { W, D, H, nx, ny, nj, nb, posts, postLen, negarami, postXs, beamYs, joistXs, lastBoardW, minH },
    };
  }

  global.DeckEngine = { SETTINGS, MATERIALS, OTHER, MEMBER_KEYS, splitRun, pack, calculate };
})(typeof window !== 'undefined' ? window : globalThis);
