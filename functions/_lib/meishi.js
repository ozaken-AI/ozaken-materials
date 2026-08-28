// 名刺CSVの読み取り。Eight / Sansan の書き出しを、名簿の形に直す。
//
// 同じ処理が newsletter/import_meishi.py にもある（端末から流し込む用）。
// **列の見出しの候補は、両方をそろえておくこと。**
// newsletter/selftest.mjs が食い違いを見張っている。

import { normalize, looksLikeEmail } from './token.js';

// 見出しはサービスと書き出し設定でまちまち。左から順に探す。
export const COLUMNS = {
  email:   ['メールアドレス', 'E-mail', 'Email', 'mail', 'メール', '電子メール'],
  last:    ['姓', 'Last name', '苗字'],
  first:   ['名', 'First name', '下の名前'],
  name:    ['氏名', '名前', 'フルネーム', 'Name', '担当者名'],
  company: ['会社名', '企業名', 'Company', '組織名', '勤務先'],
  date:    ['名刺交換日', '交換日', '登録日', '取得日', '作成日', 'タイムスタンプ', 'Timestamp', 'ダウンロード日'],
};

// 引用符の中のカンマ・改行・二重引用符を、正しく拾う。
// 素朴に split(',') すると、会社名に読点や社名の（株）が入った行で崩れる。
export function parseCsv(text) {
  const rows = [];
  let row = [], field = '', quoted = false;
  const src = text.replace(/^﻿/, '');   // BOMを落とす

  for (let i = 0; i < src.length; i++) {
    const c = src[i];
    if (quoted) {
      if (c === '"') {
        if (src[i + 1] === '"') { field += '"'; i++; }   // "" は引用符1個
        else quoted = false;
      } else field += c;
      continue;
    }
    if (c === '"') { quoted = true; continue; }
    if (c === ',') { row.push(field); field = ''; continue; }
    if (c === '\r') continue;
    if (c === '\n') { row.push(field); rows.push(row); row = []; field = ''; continue; }
    field += c;
  }
  if (field !== '' || row.length) { row.push(field); rows.push(row); }
  // 末尾の空行を捨てる
  return rows.filter(r => r.some(v => (v || '').trim() !== ''));
}

function findColumn(headers, candidates) {
  const cleaned = headers.map(h => (h || '').trim());
  for (const want of candidates) {
    const i = cleaned.indexOf(want);
    if (i >= 0) return i;
  }
  for (const want of candidates) {
    const i = cleaned.findIndex(h => want && h.includes(want));
    if (i >= 0) return i;
  }
  return -1;
}

export function detectColumns(headers) {
  const map = {};
  for (const [key, candidates] of Object.entries(COLUMNS)) {
    const i = findColumn(headers, candidates);
    if (i >= 0) map[key] = i;
  }
  return map;
}

// 名刺交換日を ISO8601 にそろえる。読めなければ取り込んだ日を使う。
export function parseDate(value, fallback) {
  const v = String(value || '').replace('年', '-').replace('月', '-').replace('日', '').trim();
  if (!v) return fallback;
  const m = v.match(/^(\d{4})[-/](\d{1,2})(?:[-/](\d{1,2}))?/);
  if (!m) return fallback;
  const [, y, mo, d] = m;
  const date = new Date(Date.UTC(+y, +mo - 1, +(d || 1)));
  return Number.isNaN(date.getTime()) ? fallback : date.toISOString();
}

// CSVの1行を、名簿に入れる形にする。読めない行は null。
export function toSubscriber(row, cols, fallbackDate) {
  const email = normalize(row[cols.email]);
  if (!looksLikeEmail(email)) return null;

  let name = cols.name !== undefined ? (row[cols.name] || '').trim() : '';
  if (!name) {
    name = [cols.last, cols.first]
      .filter(i => i !== undefined)
      .map(i => (row[i] || '').trim())
      .filter(Boolean).join(' ');
  }
  return {
    email,
    name: name || null,
    company: cols.company !== undefined ? (row[cols.company] || '').trim() || null : null,
    consentAt: parseDate(cols.date !== undefined ? row[cols.date] : '', fallbackDate),
  };
}
