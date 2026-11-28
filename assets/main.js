(function () {
  "use strict";
  var data = window.SITE_DATA || {};
  var WEEK = ["日", "月", "火", "水", "木", "金", "土"];

  function el(tag, attrs, children) {
    var node = document.createElement(tag);
    if (attrs) {
      Object.keys(attrs).forEach(function (k) {
        if (k === "text") node.textContent = attrs[k];
        else if (k === "class") node.className = attrs[k];
        else node.setAttribute(k, attrs[k]);
      });
    }
    (children || []).forEach(function (c) { if (c) node.appendChild(c); });
    return node;
  }
  function parseDate(s) {
    var p = String(s).split("-").map(Number);
    return new Date(p[0], (p[1] || 1) - 1, p[2] || 1);
  }
  function fmt(s) {
    var d = parseDate(s);
    return d.getFullYear() + "年" + (d.getMonth() + 1) + "月" + d.getDate() + "日（" + WEEK[d.getDay()] + "）";
  }
  var today = new Date(); today.setHours(0, 0, 0, 0);
  var att = data.attendance || {};
  function safeUrl(u) { return /^https:\/\//.test(String(u || "")) ? u : ""; }
  var formUrl = safeUrl(att.formUrl), resultUrl = safeUrl(att.resultUrl);
  function linkBtn(href, text, cls) { return el("a", { class: "btn-rsvp " + (cls || ""), href: href, target: "_blank", rel: "noopener", text: text }); }

  // お知らせ
  var newsList = document.getElementById("news-list");
  var news = (data.news || []).slice().sort(function (a, b) { return a.date < b.date ? 1 : -1; });
  if (!news.length) newsList.appendChild(el("li", { class: "empty", text: "お知らせはまだありません。" }));
  news.forEach(function (n, i) {
    var det = el("details", null, [
      el("summary", null, [
        el("time", { class: "news-date", datetime: n.date, text: n.date.replace(/-/g, ".") }),
        n.tag ? el("span", { class: "tag", text: n.tag }) : el("span"),
        el("span", { class: "news-title", text: n.title })
      ]),
      n.body ? el("p", { class: "news-body", text: n.body }) : null
    ]);
    if (i === 0) det.open = true;
    newsList.appendChild(el("li", { class: "news-item" }, [det]));
  });

  // 予定
  var events = (data.schedule || []).slice().sort(function (a, b) { return a.date > b.date ? 1 : -1; });
  var upcoming = events.filter(function (e) { return parseDate(e.date) >= today; });
  var past = events.filter(function (e) { return parseDate(e.date) < today; }).reverse();

  function eventNode(e) {
    var d = parseDate(e.date);
    var typeClass = "tag type-" + (e.type || "");
    var meta = [e.time, e.place].filter(Boolean).join("　｜　");
    return el("article", { class: "event", "data-type": e.type || "" }, [
      el("div", { class: "event-date" }, [
        el("div", { class: "m", text: d.getFullYear() + "." + (d.getMonth() + 1) }),
        el("div", { class: "d", text: String(d.getDate()) }),
        el("div", { class: "w" + (d.getDay() === 0 ? " sun" : ""), text: WEEK[d.getDay()] + "曜" })
      ]),
      el("div", null, [
        el("h3", null, [
          e.type ? el("span", { class: typeClass, text: e.type }) : null,
          el("span", { text: e.title })
        ]),
        meta ? el("p", { class: "meta", text: meta }) : null,
        e.note ? el("p", { class: "note", text: e.note }) : null,
        (formUrl && parseDate(e.date) >= today) ? el("div", { class: "actions" }, [linkBtn(formUrl, "出欠を入力する", "small")]) : null
      ])
    ]);
  }
  function renderEvents(target, list, filter, emptyText) {
    target.innerHTML = "";
    var shown = list.filter(function (e) { return filter === "all" || e.type === filter; });
    if (!shown.length) target.appendChild(el("p", { class: "empty", text: emptyText }));
    shown.forEach(function (e) { target.appendChild(eventNode(e)); });
  }
  var schedEl = document.getElementById("schedule-list");
  var pastEl = document.getElementById("past-list");
  function renderAll(filter) {
    renderEvents(schedEl, upcoming, filter, "予定はありません。");
    renderEvents(pastEl, past, filter, "終わった予定はありません。");
  }
  renderAll("all");
  if (!past.length) document.querySelector(".past").hidden = true;
  document.querySelectorAll(".chip").forEach(function (btn) {
    btn.addEventListener("click", function () {
      document.querySelectorAll(".chip").forEach(function (b) { b.classList.remove("is-active"); });
      btn.classList.add("is-active");
      renderAll(btn.getAttribute("data-filter"));
    });
  });

  // 出欠ボタン（ヒーロー）
  var ha = document.getElementById("hero-actions");
  if (formUrl) ha.appendChild(linkBtn(formUrl, "出欠を入力する"));
  if (resultUrl) ha.appendChild(linkBtn(resultUrl, "出欠状況を見る", "ghost"));
  if (!formUrl) schedEl.parentNode.insertBefore(el("p", { class: "rsvp-note", text: "出欠入力フォームは準備中です。" }), schedEl.nextSibling);

  // 次の予定（ヒーロー）
  if (upcoming.length) {
    var nx = upcoming[0];
    document.getElementById("next-title").textContent = nx.title;
    document.getElementById("next-when").textContent = fmt(nx.date) + (nx.time ? " " + nx.time : "");
    document.getElementById("next-event").hidden = false;
  }

  // 連絡事項
  var noticeEl = document.getElementById("notice-list");
  (data.notices || []).forEach(function (n) {
    noticeEl.appendChild(el("div", { class: "card" + (n.important ? " important" : "") }, [
      el("h3", null, [n.important ? el("span", { class: "badge", text: "重要" }) : null, el("span", { text: n.title })]),
      el("p", { text: n.body })
    ]));
  });

  // 組について・連絡先
  var about = data.about || {};
  var aboutBody = document.getElementById("about-body");
  (about.text || []).forEach(function (t) { aboutBody.appendChild(el("p", { text: t })); });
  function facts(target, list) {
    (list || []).forEach(function (f) {
      target.appendChild(el("dt", { text: f.label }));
      target.appendChild(el("dd", { text: f.value }));
    });
  }
  facts(document.getElementById("about-facts"), about.facts);
  var hist = document.getElementById("history-body");
  var hs = (about.history || []).filter(Boolean);
  if (hs.length) hs.forEach(function (t) { hist.appendChild(el("p", { text: t })); });
  else hist.appendChild(el("p", { class: "muted", text: "準備中です。後日掲載します。" }));
  facts(document.getElementById("contact-list"), data.contact);

  // フッター
  document.getElementById("year").textContent = today.getFullYear();
  document.getElementById("updated").textContent = data.updated ? fmt(data.updated) : "";

  // モバイルメニュー
  var toggle = document.querySelector(".nav-toggle");
  var nav = document.getElementById("nav");
  toggle.addEventListener("click", function () {
    var open = nav.classList.toggle("is-open");
    toggle.setAttribute("aria-expanded", open ? "true" : "false");
  });
  nav.addEventListener("click", function (e) {
    if (e.target.tagName === "A") { nav.classList.remove("is-open"); toggle.setAttribute("aria-expanded", "false"); }
  });
})();
