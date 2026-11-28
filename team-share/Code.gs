/**
 * 三日会 チーム共有ページ（Google Apps Script 版）
 *
 * ・このファイルを Apps Script の「コード.gs」に貼り付けます
 * ・データは、初めてページを開いたときに自動で作られる
 *   スプレッドシート「三日会 共有データ」に保存されます（あなたの Google ドライブ）
 * ・合言葉を使う場合は、下の PASSWORD に好きな言葉を入れてください
 *   （空のままなら合言葉なしで、リンクを知っている人は誰でも使えます）
 */
const PASSWORD = '';

const TEAM_NAME = '三日会';

// シートごとの列（この順番でスプレッドシートに保存されます）
const SHEETS = {
  notices:    ['id', 'title', 'body', 'pinned', 'createdAt'],
  events:     ['id', 'date', 'time', 'kind', 'title', 'place', 'note', 'createdAt'],
  attendance: ['eventId', 'memberId', 'value', 'updatedAt'],
  results:    ['id', 'date', 'competition', 'opponent', 'our', 'their', 'note', 'createdAt'],
  members:    ['id', 'name', 'number', 'position', 'role', 'note', 'createdAt'],
};
const SHEET_TITLES = {
  notices: 'お知らせ', events: '予定', attendance: '出欠', results: '試合結果', members: 'メンバー',
};
const NUMBER_FIELDS = ['createdAt', 'updatedAt', 'our', 'their', 'number'];
const BOOL_FIELDS = ['pinned'];
const EDITABLE = ['notices', 'events', 'results', 'members'];

// ---------- ページを表示 ----------
function doGet() {
  return HtmlService.createHtmlOutputFromFile('index')
    .setTitle(TEAM_NAME + ' チーム共有ページ')
    .addMetaTag('viewport', 'width=device-width, initial-scale=1');
}

// ---------- ページから呼ばれる関数 ----------
function apiHasPassword() {
  return PASSWORD !== '';
}

function apiGetAll(pw) {
  checkPassword_(pw);
  return readAll_();
}

function apiSave(pw, kind, id, data) {
  checkPassword_(pw);
  if (EDITABLE.indexOf(kind) < 0) throw new Error('不正な種類です');
  return withLock_(function () {
    const sheet = sheet_(kind);
    const cols = SHEETS[kind];
    const row = {};
    cols.forEach(function (c) { row[c] = data && data[c] != null ? data[c] : ''; });
    if (id) {
      const idx = findRow_(sheet, 0, id);
      if (idx < 0) throw new Error('対象のデータが見つかりません。ほかの人が削除した可能性があります。');
      const old = sheet.getRange(idx, 1, 1, cols.length).getValues()[0];
      row.id = id;
      row.createdAt = old[cols.indexOf('createdAt')];
      sheet.getRange(idx, 1, 1, cols.length).setValues([cols.map(function (c) { return cell_(row[c]); })]);
    } else {
      row.id = Utilities.getUuid().slice(0, 8);
      row.createdAt = Date.now();
      sheet.appendRow(cols.map(function (c) { return cell_(row[c]); }));
    }
    return readAll_();
  });
}

function apiRemove(pw, kind, id) {
  checkPassword_(pw);
  if (EDITABLE.indexOf(kind) < 0) throw new Error('不正な種類です');
  return withLock_(function () {
    const sheet = sheet_(kind);
    const idx = findRow_(sheet, 0, id);
    if (idx > 0) sheet.deleteRow(idx);
    // 予定やメンバーを消したら、その出欠も消す
    if (kind === 'events' || kind === 'members') {
      const att = sheet_('attendance');
      const col = kind === 'events' ? 0 : 1;
      const values = att.getDataRange().getValues();
      for (let r = values.length - 1; r >= 1; r--) {
        if (String(values[r][col]) === String(id)) att.deleteRow(r + 1);
      }
    }
    return readAll_();
  });
}

function apiSetAttendance(pw, eventId, memberId, value) {
  checkPassword_(pw);
  if (['o', 'm', 'x', ''].indexOf(value) < 0) throw new Error('不正な値です');
  return withLock_(function () {
    const att = sheet_('attendance');
    const values = att.getDataRange().getValues();
    let found = -1;
    for (let r = 1; r < values.length; r++) {
      if (String(values[r][0]) === String(eventId) && String(values[r][1]) === String(memberId)) { found = r + 1; break; }
    }
    const row = [cell_(eventId), cell_(memberId), cell_(value), cell_(Date.now())];
    if (found > 0) att.getRange(found, 1, 1, 4).setValues([row]);
    else att.appendRow(row);
    return readAll_();
  });
}

// ---------- 内部の処理 ----------
function checkPassword_(pw) {
  if (PASSWORD !== '' && String(pw || '') !== PASSWORD) throw new Error('PASSWORD');
}

function withLock_(fn) {
  const lock = LockService.getScriptLock();
  lock.waitLock(20000);
  try { return fn(); } finally { lock.releaseLock(); }
}

function spreadsheet_() {
  const props = PropertiesService.getScriptProperties();
  const id = props.getProperty('SHEET_ID');
  if (id) {
    try { return SpreadsheetApp.openById(id); } catch (e) { /* 削除されていたら作り直す */ }
  }
  const lock = LockService.getScriptLock();
  lock.waitLock(20000);
  try {
    const again = props.getProperty('SHEET_ID');
    if (again && again !== id) return SpreadsheetApp.openById(again);
    const ss = SpreadsheetApp.create(TEAM_NAME + ' 共有データ');
    const first = ss.getSheets()[0];
    Object.keys(SHEETS).forEach(function (k, i) {
      const sh = i === 0 ? first : ss.insertSheet();
      sh.setName(SHEET_TITLES[k]);
      sh.getRange(1, 1, sh.getMaxRows(), SHEETS[k].length).setNumberFormat('@');
      sh.getRange(1, 1, 1, SHEETS[k].length).setValues([SHEETS[k]]).setFontWeight('bold');
      sh.setFrozenRows(1);
    });
    props.setProperty('SHEET_ID', ss.getId());
    return ss;
  } finally { lock.releaseLock(); }
}

function sheet_(kind) {
  return spreadsheet_().getSheetByName(SHEET_TITLES[kind]);
}

function findRow_(sheet, col, id) {
  const values = sheet.getDataRange().getValues();
  for (let r = 1; r < values.length; r++) {
    if (String(values[r][col]) === String(id)) return r + 1;
  }
  return -1;
}

// 「=」などで始まる文字が数式として扱われないようにする
function cell_(v) {
  if (v === true) return 'TRUE';
  if (v === false) return 'FALSE';
  const s = v == null ? '' : String(v);
  return /^[=+\-@]/.test(s) ? "'" + s : s;
}

function readSheet_(kind) {
  const sh = sheet_(kind);
  const values = sh.getDataRange().getValues();
  const cols = SHEETS[kind];
  const out = [];
  for (let r = 1; r < values.length; r++) {
    const o = {};
    cols.forEach(function (c, i) {
      let v = values[r][i];
      if (v instanceof Date) v = Utilities.formatDate(v, Session.getScriptTimeZone(), 'yyyy-MM-dd');
      v = v == null ? '' : String(v);
      if (NUMBER_FIELDS.indexOf(c) >= 0) v = v === '' || isNaN(Number(v)) ? null : Number(v);
      if (BOOL_FIELDS.indexOf(c) >= 0) v = v.toUpperCase() === 'TRUE';
      o[c] = v;
    });
    if (o.id !== '' || kind === 'attendance') out.push(o);
  }
  return out;
}

function readAll_() {
  const att = readSheet_('attendance');
  const events = readSheet_('events').map(function (e) {
    e.attendance = {};
    att.forEach(function (a) { if (a.eventId === e.id && a.value) e.attendance[a.memberId] = a.value; });
    return e;
  });
  return {
    notices: readSheet_('notices'),
    events: events,
    results: readSheet_('results'),
    members: readSheet_('members'),
    fetchedAt: Date.now(),
  };
}

/** 動作確認用：Apps Script の画面でこの関数を実行すると、スプレッドシートが作られます */
function setup() {
  const ss = spreadsheet_();
  Logger.log('スプレッドシート: ' + ss.getUrl());
}
