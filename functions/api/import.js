// 名刺CSVの取り込み。/api/import（POST、管理者トークンが要る）
//
// 本文にCSVをそのまま入れて投げる。roster.html が使う。
// 端末から流し込みたいときは newsletter/import_meishi.py でもよい（同じ結果になる）。
//
// **1回の呼び出しで全行は処理しない。** /api/send と同じで、
// offset を進めながら何度か叩く。呼ぶ側が next_offset を見て繰り返す。
//
// dry=1 を付けると、書き込まずに「何が起きるか」だけ返す。
// 名簿は一度汚すと戻せないので、まず下見してから入れる。

import { json } from '../_lib/page.js';
import { requireDb, now, logEvent, HttpError } from '../_lib/db.js';
import { normalize } from '../_lib/token.js';
import { parseCsv, detectColumns, toSubscriber } from '../_lib/meishi.js';

const DEFAULT_LIMIT = 300;
const MAX_LIMIT = 1000;
const IN_CHUNK = 50;       // D1 に一度に渡す束縛値の数を抑える

function authorized(request, env) {
  const expected = env.NEWSLETTER_ADMIN_TOKEN;
  if (!expected) return false;
  const given = (request.headers.get('Authorization') || '').replace(/^Bearer\s+/i, '');
  if (given.length !== expected.length) return false;
  let diff = 0;
  for (let i = 0; i < given.length; i++) diff |= given.charCodeAt(i) ^ expected.charCodeAt(i);
  return diff === 0;
}

// 送らない状態。ここに居る人は、取り込み直しでも status に触らない。
const STOPPED = new Set(['unsubscribed', 'bounced', 'complained']);

async function existingStatuses(db, emails) {
  const found = new Map();
  for (let i = 0; i < emails.length; i += IN_CHUNK) {
    const chunk = emails.slice(i, i + IN_CHUNK);
    const marks = chunk.map(() => '?').join(',');
    const r = await db.prepare(`SELECT email, status FROM subscribers WHERE email IN (${marks})`)
      .bind(...chunk).all();
    for (const row of r.results || []) found.set(row.email, row.status);
  }
  return found;
}

export async function onRequestPost({ request, env }) {
  if (!authorized(request, env)) return json({ ok: false, error: 'unauthorized' }, 401);

  try {
    const db = requireDb(env);
    const url = new URL(request.url);
    const offset = Math.max(0, Number(url.searchParams.get('offset')) || 0);
    const limit = Math.min(Number(url.searchParams.get('limit')) || DEFAULT_LIMIT, MAX_LIMIT);
    const dry = url.searchParams.get('dry') === '1';
    const source = url.searchParams.get('source') || 'meishi';
    const note = url.searchParams.get('note') || null;

    const text = await request.text();
    if (!text.trim()) throw new HttpError(400, 'CSVが空です。');

    const rows = parseCsv(text);
    if (rows.length < 2) throw new HttpError(400, '見出し行と、少なくとも1行のデータが要ります。');

    const headers = rows[0];
    const cols = detectColumns(headers);
    if (cols.email === undefined) {
      throw new HttpError(400,
        `メールアドレスの列が見つかりません。見出し: ${headers.filter(Boolean).join(' / ')}`);
    }

    const data = rows.slice(1);
    const t = now();
    const slice = data.slice(offset, offset + limit);

    // CSVの中の重複を、ファイル全体で見て数える。
    // 前の周回で出たアドレスは、ここで「重複」として落とす。
    const before = new Set();
    for (let i = 0; i < offset; i++) {
      const s = toSubscriber(data[i], cols, t);
      if (s) before.add(s.email);
    }

    const seen = new Set();
    const items = [];
    let invalid = 0, duplicates = 0;
    for (const row of slice) {
      const s = toSubscriber(row, cols, t);
      if (!s) { invalid++; continue; }
      if (before.has(s.email) || seen.has(s.email)) { duplicates++; continue; }
      seen.add(s.email);
      items.push(s);
    }

    const prior = items.length ? await existingStatuses(db, items.map(i => i.email)) : new Map();
    const created = [], updated = [], kept = [];
    for (const s of items) {
      const was = prior.get(s.email);
      if (was === undefined) created.push(s);
      else if (STOPPED.has(was)) kept.push({ ...s, status: was });
      else updated.push(s);
    }

    if (!dry && items.length) {
      // status には触らない。**ここが、止めた人を復活させない砦。**
      const stmt = db.prepare(`
        INSERT INTO subscribers
          (email, name, company, status, source, source_note, consent_at, created_at, updated_at)
        VALUES (?, ?, ?, 'active', ?, ?, ?, ?, ?)
        ON CONFLICT(email) DO UPDATE SET
          name       = COALESCE(excluded.name, subscribers.name),
          company    = COALESCE(excluded.company, subscribers.company),
          updated_at = excluded.updated_at
      `);
      for (let i = 0; i < items.length; i += IN_CHUNK) {
        await db.batch(items.slice(i, i + IN_CHUNK).map(s =>
          // 行に資料名があればそれを、なければ画面で入れた「取得の場」を使う
          stmt.bind(s.email, s.name, s.company, source, s.note || note, s.consentAt, t, t)));
      }
      // 同意（名刺で連絡先をいただいた）の記録は、初めて入った人にだけ残す。
      for (const s of created) {
        await logEvent(db, s.email, 'import',
          `${s.note || note || source} / consent_at=${s.consentAt}`);
      }
    }

    const nextOffset = offset + slice.length;
    const done = nextOffset >= data.length;

    return json({
      ok: true,
      dry,
      total_rows: data.length,
      processed: slice.length,
      next_offset: nextOffset,
      done,
      report: {
        created: created.length,
        updated: updated.length,
        kept_stopped: kept.length,
        invalid,
        duplicates,
      },
      // 列の読み取りを間違えていないか、目で確かめられるように
      columns: Object.fromEntries(Object.entries(cols).map(([k, i]) => [k, headers[i]])),
      sample: offset === 0
        ? items.slice(0, 3).map(s => ({ email: s.email, name: s.name, company: s.company }))
        : undefined,
      kept_examples: kept.slice(0, 5).map(k => ({ email: k.email, status: k.status })),
    });
  } catch (err) {
    const status = err instanceof HttpError ? err.status : 500;
    return json({ ok: false, error: err.message || '取り込めませんでした。' }, status);
  }
}
