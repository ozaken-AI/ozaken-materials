-- メルマガの名簿と配信記録。Cloudflare D1（SQLite）。
--
--   wrangler d1 create ozaken-newsletter
--   wrangler d1 execute ozaken-newsletter --remote --file=newsletter/schema.sql
--
-- 何度流しても壊れないように、すべて IF NOT EXISTS で書いている。

-- ── 名簿 ─────────────────────────────────────────────
-- status の意味:
--   pending      … Webから申し込まれたが、確認メールのリンクをまだ踏んでいない
--   active       … 配信対象
--   unsubscribed … 本人が配信停止した。**二度と active に戻さない**（取り込み直しでも）
--   bounced      … 宛先不明が続いた。送ると送信ドメインの評判が落ちるので外す
--   complained   … 迷惑メール報告された。unsubscribed と同じ扱い
CREATE TABLE IF NOT EXISTS subscribers (
  email          TEXT PRIMARY KEY,          -- 小文字・前後空白なしに正規化して入れる
  name           TEXT,
  company        TEXT,
  status         TEXT NOT NULL DEFAULT 'pending',
  source         TEXT NOT NULL,             -- 'meishi' | 'web' | 'event' | 'manual'
  source_note    TEXT,                      -- 「2026-06 AX Table 第3回」など、取得の場
  consent_at     TEXT,                      -- 名刺交換日／申込日（ISO8601）。記録保存義務の芯
  confirmed_at   TEXT,                      -- ダブルオプトインを踏んだ日時
  unsubscribed_at TEXT,
  created_at     TEXT NOT NULL,
  updated_at     TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_subscribers_status ON subscribers(status);

-- ── 号 ───────────────────────────────────────────────
-- 配信は分割して何度も叩くので、号の中身をここに置いて毎回引き直す。
CREATE TABLE IF NOT EXISTS issues (
  id          TEXT PRIMARY KEY,             -- '2026-08-18'
  subject     TEXT NOT NULL,
  payload     TEXT NOT NULL,                -- 本文のもとになるJSON（newsletter/issue-sample.json 参照）
  created_at  TEXT NOT NULL,
  finished_at TEXT                          -- 全員に送り終えた日時
);

-- ── 配信ログ ─────────────────────────────────────────
-- (issue_id, email) が主キーなので、同じ号を二度送ることがない。
-- 分割配信の「どこまで送ったか」も、この表で判定している。
--
-- 失敗（status='failed'）も、成功と同じようにここへ書く。**書かないと再試行できない。**
-- ただし失敗は「送り終えた」とは見なさず、attempts が上限に届くまで拾い直す。
-- Resend が数分落ちただけの相手を、永久に取りこぼさないため。
CREATE TABLE IF NOT EXISTS deliveries (
  issue_id    TEXT NOT NULL,
  email       TEXT NOT NULL,
  status      TEXT NOT NULL,                -- sent | failed | bounced | complained
  provider_id TEXT,                         -- Resend が返すメッセージID
  error       TEXT,
  attempts    INTEGER NOT NULL DEFAULT 0,   -- 送信を試みた回数。失敗の再試行を打ち切る目安
  sent_at     TEXT NOT NULL,
  PRIMARY KEY (issue_id, email)
);
CREATE INDEX IF NOT EXISTS idx_deliveries_email ON deliveries(email);

-- ── 出来事の記録 ─────────────────────────────────────
-- 特定電子メール法は「同意を得た記録」の保存を求めている（送信をやめた日から1か月、
-- 一定の場合1年）。同意・確認・配信停止・バウンス・苦情を、消さずにここへ積む。
CREATE TABLE IF NOT EXISTS events (
  id     INTEGER PRIMARY KEY AUTOINCREMENT,
  email  TEXT NOT NULL,
  kind   TEXT NOT NULL,                     -- consent | confirm | unsubscribe | bounce | complaint | import
  detail TEXT,
  ip     TEXT,
  at     TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_events_email ON events(email);
