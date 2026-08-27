# メルマガの仕組み（設計と運転）

名刺交換でいただいた連絡先に、週次トレンドを届けるための一式。
**送信そのものは Resend に任せ、名簿・配信停止・記録はこちらで持つ。**

配信停止は `https://content.ozaken.ai/unsubscribe` で受ける。
資料アーカイブと同じ Cloudflare Pages の上に、Functions として同居している。

---

## 1. なぜ自前で全部やらないか

メールは「送れば届く」ものではない。2024年2月から Gmail と Yahoo が
一括送信者に課している条件がある。

| 条件 | 誰が満たすか |
|---|---|
| SPF / DKIM / DMARC で送信元を証明する | Resend（ドメイン認証を1回やる） |
| ワンクリックで配信停止できる（`List-Unsubscribe` ヘッダ） | このリポジトリの `functions/unsubscribe.js` |
| 迷惑メール報告率を 0.3% 未満に保つ | 報告された人を即座に外す仕組み（`functions/api/hooks/resend.js`） |
| 宛先不明を放置しない | 同上（バウンスの自動処理） |

自前の SMTP で送ると、最初の1通目から迷惑メールに落ちる。
IPの評判を育てるところから始めることになり、割に合わない。

一方で、**名簿を配信サービスに預けっぱなしにもしない。**
乗り換えのたびに配信停止の履歴が飛ぶと、一度断った人にまた送ってしまう。
名簿と「止めた記録」は D1 に置いて、こちらで持ち続ける。

---

## 2. 層構造

```
名刺管理サービス（Sansan / Eight）
   │  CSVで書き出す
   ▼
newsletter/import_meishi.py  ──→  投入用のSQL
   │
   ▼
Cloudflare D1「ozaken-newsletter」          ← 名簿の正本。ここが「正」
   │  subscribers / issues / deliveries / events
   ▼
functions/api/send.js（分割配信）
   │
   ▼
Resend API  ──→  受信者
   │                 │
   │                 ├─ 本文の「配信を停止する」        ┐
   │                 └─ Gmail の「配信停止」ボタン      ├→ functions/unsubscribe.js → D1
   │                                                     ┘
   └─ バウンス・迷惑メール報告 → functions/api/hooks/resend.js → D1
```

### ファイルの割り当て

| パス | 役割 |
|---|---|
| `newsletter/schema.sql` | D1 の表。何度流しても壊れない |
| `newsletter/import_meishi.py` | 名刺CSV → 投入用SQL |
| `newsletter/send.sh` | 号を1本、最後まで配る |
| `newsletter/issues/*.json` | 号の中身。これを送る |
| `functions/unsubscribe.js` | 配信停止（GET=確認画面 / POST=実行） |
| `functions/api/subscribe.js` | Webからの申し込み（ダブルオプトイン） |
| `functions/api/confirm.js` | 確認メールのリンク先 |
| `functions/api/send.js` | 配信の実行と、状況の確認 |
| `functions/api/hooks/resend.js` | バウンス・迷惑メール報告の受け口 |
| `functions/_lib/` | 署名・D1・本文組み立て・画面の共通部品 |
| `subscribe.html` | 購読の申し込みページ |

---

## 3. 配信停止の作り

ここがいちばん間違えやすいので、先に書く。

### 署名つきURL

```
https://content.ozaken.ai/unsubscribe?e=<アドレス>&s=<HMAC-SHA256の署名>
```

`e=` だけだと、他人のアドレスを打ち込んで勝手に解除できてしまう。
`NEWSLETTER_SECRET` を鍵にした署名を添えて、**こちらが発行したリンクだけ**を受け付ける。
署名には用途（`unsub` / `confirm`）を混ぜてあるので、確認用のリンクを配信停止に使い回せない。

### GET では絶対に止めない

企業のメールセキュリティ製品は、本文中のリンクを勝手に開いて安全確認する。
**GETで即解除にすると、本人が押していないのに配信が止まる。**
だから GET は確認画面を出すだけにして、POST で初めて止める。

### ワンクリック配信停止

`List-Unsubscribe` と `List-Unsubscribe-Post` の2本を送ると、
Gmail は件名の横に「配信停止」ボタンを出す。押されると、こちらの
`/unsubscribe` に **POST** が飛んでくる（本文は `List-Unsubscribe=One-Click`）。
相手はHTMLを読まないので、この場合だけ素の `200` を返す。

### 一度止めた人を復活させない

これを守れないと、断った相手にまた送ることになる。3か所で効かせている。

- **取り込み**：`ON CONFLICT` で `status` に触らない。
  同じCSVを何度流しても、止めた人は止まったまま（名前と会社名だけ新しくなる）。
- **確認リンク**：停止後に古い確認メールのリンクを踏んでも `active` に戻さない。
- **配信の宛先選び**：`status = 'active'` だけを引く。

---

## 4. 法令まわり（特定電子メール法）

### 送っていい相手

原則はオプトイン（事前の同意）。ただし例外があり、
**名刺などで相手が自分から連絡先を通知してきた場合**は、同意なしで送れる
（施行規則の明文）。名刺交換でいただいた相手は、ここに乗る。

Webからの申し込みは、ダブルオプトイン（確認メールのリンクを踏んで初めて登録）にしてある。
他人のアドレスを勝手に登録するいたずらを、これで無効化できる。

### 本文に必ず載せるもの（表示義務）

`functions/_lib/mail.js` のフッターが、常に次を出す。抜くと違反になる。

- 送信者の氏名・名称 … `NEWSLETTER_SENDER_NAME`
- 送信者の住所 … `NEWSLETTER_SENDER_ADDRESS`
- 受信拒否の通知先 … 配信停止リンク
- 苦情・問い合わせ先 … `NEWSLETTER_REPLY_TO`

住所を出すのが難しければ、バーチャルオフィスや事務所の住所を使う。
**空欄にはしない。**

### 記録の保存

`events` 表に、同意・確認・配信停止・バウンス・苦情を消さずに積んでいる。
`subscribers.consent_at` には名刺交換日（CSVから拾えたもの）が入る。
「いつ・どこで連絡先をいただいたか」を、あとから示せる状態にしてある。

---

## 5. 立ち上げの手順

### 5-1. Resend でドメインを認証する

1. [resend.com](https://resend.com) で登録し、Domains に `ozaken.ai` を足す。
2. 表示された DNS レコード（DKIM・SPF・DMARC）を、ドメインの DNS に足す。
3. 緑になるまで待つ。**ここを飛ばすと、まず迷惑メールに落ちる。**
4. API Keys で送信用の鍵を作る（`re_...`）。

### 5-2. D1 を作る

```bash
npx wrangler d1 create ozaken-newsletter
# 出力された database_id を控える
npx wrangler d1 execute ozaken-newsletter --remote --file=newsletter/schema.sql
```

Cloudflare のダッシュボードで、Pages プロジェクトに束ねる。

> Workers & Pages → ozaken-materials → Settings → Bindings → D1 database
> Variable name: `DB` ／ D1 database: `ozaken-newsletter`

**`wrangler.toml` をリポジトリ直下に置かない。** ダッシュボードの設定を上書きして、
いま動いている静的配信を壊しかねない。見本は `newsletter/wrangler.sample.toml` に置いてある。

### 5-3. 環境変数を入れる

同じ Settings → Variables and Secrets に。**Secret（暗号化）** で入れるもの:

| 名前 | 中身 |
|---|---|
| `NEWSLETTER_SECRET` | 配信停止リンクの署名鍵。`openssl rand -base64 36` で作る |
| `NEWSLETTER_ADMIN_TOKEN` | `/api/send` を叩くための鍵。同上 |
| `RESEND_API_KEY` | Resend の `re_...` |
| `RESEND_WEBHOOK_SECRET` | Resend の Webhooks 画面に出る `whsec_...` |

**Text（平文）** で入れるもの:

| 名前 | 例 |
|---|---|
| `NEWSLETTER_SITE` | `https://content.ozaken.ai` |
| `NEWSLETTER_FROM` | `小澤健祐（おざけん） <weekly@ozaken.ai>` |
| `NEWSLETTER_SENDER_NAME` | `小澤健祐（おざけん）` |
| `NEWSLETTER_SENDER_ADDRESS` | 登記上の住所 |
| `NEWSLETTER_REPLY_TO` | `weekly@ozaken.ai` |
| `NEWSLETTER_UNSUB_MAILTO` | `unsubscribe@ozaken.ai`（任意） |

`NEWSLETTER_SECRET` は**あとから変えない。**
変えると、すでに配ったメールの配信停止リンクが全部無効になる。

### 5-4. バウンスの受け口をつなぐ

Resend の Webhooks で、次のURLを登録する。

```
https://content.ozaken.ai/api/hooks/resend
```

拾う出来事：`email.bounced` と `email.complained`。

### 5-5. 名簿を入れる

Sansan / Eight から CSV を書き出して、

```bash
python3 newsletter/import_meishi.py ~/Downloads/meishi.csv \
  --source-note "2026年上期 名刺交換" \
  -o newsletter/import.sql

npx wrangler d1 execute ozaken-newsletter --remote --file=newsletter/import.sql
```

- 文字コードは cp932 と UTF-8 の両方を試す（Sansanの既定は cp932）。
- 重複・形式不正は落とし、件数を最後に出す。
- 送りたくない相手は `--exclude` にファイルで渡す（1行1アドレス）。
- **CSVと `import.sql` は個人情報なので、リポジトリに入れない**（`.gitignore` 済み）。

---

## 6. 週の運転

### 号を書く

`newsletter/issues/YYYY-MM-DD.json` を作る。`sample.json` をコピーして中身を差し替える。

```json
{
  "id": "2026-08-25",
  "subject": "件名",
  "preheader": "受信箱の一覧に出る短い一文",
  "url": "https://content.ozaken.ai/weekly/2026-08-25.html",
  "passphrase": "週次ページの合言葉",
  "lede": "書き出し",
  "items": [{ "kicker": "分類", "title": "見出し", "body": "本文", "link": "https://…" }],
  "closing": "締めの一文"
}
```

**メールに図版は入れない。** 週次ページのHTMLをそのまま貼っても、
Outlook や携帯のメールアプリでは崩れる。メールはあらましだけにして、
図版つきの全文は暗号化した週次ページへ送る。合言葉は購読者だけに渡す
（`passphrase`）ので、これが購読していただく理由になる。

### 送る

```bash
export NEWSLETTER_ADMIN_TOKEN=…

# 1) まず自分に送って、実機で確かめる
./newsletter/send.sh --test k.ozaken1222@cinematorico.com newsletter/issues/2026-08-25.json

# 2) 本番
./newsletter/send.sh newsletter/issues/2026-08-25.json
```

`/api/send` は1回につき 500件しか送らない（Workers の実行時間と Resend の
レート制限のため）。`send.sh` が「残り0件」になるまで叩き直す。
**途中で止めても、同じコマンドを叩き直せば続きから再開する。**
誰に送ったかは `deliveries` に主キーで記録しているので、二重には届かない。

送信に失敗した相手は、次の周回で拾い直す（最大3回）。
3回でも送れなかった相手は最後に一覧で出るので、必ず目を通す。

### 状況を見る

```bash
curl -H "Authorization: Bearer $NEWSLETTER_ADMIN_TOKEN" \
  "https://content.ozaken.ai/api/send?issue_id=2026-08-25"
```

名簿の内訳（active / pending / unsubscribed / bounced / complained）と、
その号の配信結果が返る。

### 送ったあとに見るもの

- **迷惑メール報告率**（Resend のダッシュボード）。0.1% を超えたら、
  送る相手か文面を見直す。0.3% を超えると Gmail に届かなくなる。
- `complained` が増えていないか。増えているなら、名刺交換から時間が
  経ちすぎた相手に送っている可能性がある。

---

## 7. 直したら通すもの

```bash
node newsletter/selftest.mjs
```

D1 のかわりに `node:sqlite` を同じ形にかぶせて、`functions/` の実物をそのまま動かす。
Resend への送信は差し替えるので、**メールは1通も出ない**。

見ているのは、壊すと相手に迷惑がかかるところ。

- 署名のないリンク・他人のアドレスに付け替えたリンクで解除できないこと
- GET では止まらないこと（メールのリンク検査botが踏むため）
- Gmail のワンクリックで止まること
- **一度止めた人が、名簿の取り込み直しでも古い確認リンクでも復活しないこと**
- 同じ号が二度届かないこと
- 送信に失敗した相手を、次の周回で拾い直すこと（かつ無限ループしないこと）
- バウンスと迷惑メール報告で、名簿から外れること
- 本文に住所と問い合わせ先と配信停止リンクが必ず載ること（表示義務）

## 8. 決めてあること

| 論点 | 決定 | 理由 |
|---|---|---|
| 送信 | Resend | ドメイン認証・バウンス処理・ワンクリック停止を任せられる |
| 名簿の正本 | Cloudflare D1 | 配信サービスを乗り換えても、停止の履歴が残る |
| Webからの登録 | ダブルオプトイン | 他人のアドレスを勝手に登録されない |
| 名刺からの取り込み | そのまま `active` | 施行規則の例外に乗る。ただし初回から停止導線を出す |
| 配信停止の反映 | 即時（D1を直接書き換える） | 「すぐ止まる」と書いた以上、止める |
| 一度止めた人 | 二度と `active` に戻さない | 取り込み・確認リンクの両方で塞いである |
| メールの図版 | 入れない | 崩れる。全文は暗号化した週次ページへ |

## 9. まだやっていないこと

- **開封・クリックの計測**。開封のために透明画像を仕込むと、
  Apple の Mail プライバシー保護で数字が当てにならない。入れるなら
  クリック計測だけにする。
- **配信の予約**。いまは手で `send.sh` を叩く。定時に出したくなったら
  Cloudflare Cron Triggers を足す。
- **名簿を見る画面**。いまは `wrangler d1 execute` か `/api/send`（GET）で見る。
  頻度が上がったら `console.html` の隣に1枚作る。
