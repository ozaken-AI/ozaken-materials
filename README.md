# ozaken-materials

小澤健祐（おざけん）のAI関連解説資料アーカイブ。トップページは [`index.html`](./index.html)（公開中: https://content.ozaken.ai/ ）。

資料は「AIを組織で使えるようにするまでの問いの連鎖」を軸に、**知る → 選ぶ → 動かす** の流れでMECEに分類しています。

## フォルダ構成

| フォルダ | 答える問い | 内容 |
|---------|-----------|------|
| `01_concept/` | AIをどう捉えるか（Why/What） | AXとは、AIエージェント実装の5レベル、Human in/on the loop、パーパス論 |
| `02_models/` | いまAIは何ができるか | モデル使い分け、モデル分業16の型、AI音声、Google I/O、Mythos |
| `03_tools/` | 何を使うか | ChatGPT Work、Cowork |
| `04_practice/` | 現場でどう使いこなすか | プロンプトエンジニアリング、AIで資料作成 |
| `05_drive/` | 組織にどう広げ、根付かせるか | AI推進51施策・大全、資格制度（ストラテジスト）、予算 |
| `06_people/` | 働き方と人材はどう変わるか | AIエージェント時代のキャリア、FDE、人事 |
| `07_risk/` | どう守るか | 個人情報保護法、AIガイドライン、著作権 |
| `08_industry/` | 業界ごとに何が起きるか | 金融、医療、製造、建設、小売、自治体 |
| `09_role/` | 職種ごとに何が変わるか | 営業、人事、経理、マーケ、CS、情シス |
| `99_assets/` | （コンテンツでない素材） | 登壇スライド、画像素材 |
| `weekly/` | 今週何が起きたか | 週次トレンド。号ごとのHTMLと、定点ファイル（`threads/`）・組版のもと（`src/`） |
| `newsletter/` | （コンテンツでない道具） | メルマガの名簿設計・取り込み・配信スクリプト |
| `functions/` | （コンテンツでない道具） | Cloudflare Pages Functions。配信停止・購読受付・配信の実行 |

裏資料（配布先が決まっているもの）は `AX_Table/`（AX Table 各セッション）と
`Training/`（法人研修）に置きます。

週次トレンドは `weekly/YYYY-MM-DD.html` に置き、トップページの「今週のトレンド」に
最新4号だけを載せます。作り方と鍵の設計は [`docs/weekly-system.md`](./docs/weekly-system.md) に。

## 命名規則

URLをそのまま人に渡すので、パスは英語だけで書きます。

| 対象 | 規則 | 例 |
|------|------|-----|
| フォルダ | `NN_english` | `05_drive/` |
| 資料ファイル | `lowercase-hyphen.html` | `agent-budget-taxi.html` |
| ルートの道具 | 用途の英単語 | `passwords.html` / `backstage.html` / `matrix.html` |

先頭の連番は分類の並び順を持たせるために残しています。スクリプトの走査も
`0*_*` を前提にしているので、番号と `_` は外さないでください。

2026年8月に日本語のパスから移しました。配布済みの古いURLは
[`404.html`](./404.html) が対応表を持っていて、新しい場所へ送り届けます。
資料を移動・改名したときは、この対応表にも足してください。

## 配信

**Cloudflare Pages** が `ozaken-AI/ozaken-materials` の `main` を見ています。
ビルドはありません（静的HTMLをそのまま配る）。

| | |
|---|---|
| 公開URL | `https://content.ozaken.ai/` |
| Pages プロジェクト | `ozaken-materials`（`ozaken-materials.pages.dev` でも開く） |
| ビルドコマンド | なし |
| 出力ディレクトリ | `/` |

**`.claude/` は配信されません。** ドット始まりのフォルダは Cloudflare Pages が
対象外にするので、生成元とスクリプトは配信物から自然に外れます。

**引っ越すときは `.claude/skills/ozaken-shiryo/scripts/oz_site.py` を直して、
`retarget.py` を通します。** URLはQRの升目としてSVGに焼き込まれているので、
文字を置き換えるだけでは直りません。

```bash
cd .claude/skills/ozaken-shiryo/scripts
# oz_site.py の SITE を新しいURLに直してから
OZAKEN_PW=… python3 retarget.py https://content.ozaken.ai/ --apply
OZAKEN_PW=… python3 apply_ogp.py cards
```

## メルマガ

名刺交換でいただいた連絡先に、週次トレンドを届ける。
**送信は Resend、名簿と配信停止は自分で持つ**という分け方にしてある。

| | |
|---|---|
| 申し込み | `https://content.ozaken.ai/subscribe.html` |
| 配信停止 | `https://content.ozaken.ai/unsubscribe`（署名つきリンク） |
| 名簿 | Cloudflare D1 `ozaken-newsletter` |
| 送信 | Resend |

```bash
# 名刺CSVを取り込む
python3 newsletter/import_meishi.py meishi.csv --source-note "2026年上期" -o newsletter/import.sql
npx wrangler d1 execute ozaken-newsletter --remote --file=newsletter/import.sql

# 号を送る（まず自分に、それから本番）
./newsletter/send.sh --test 自分のアドレス newsletter/issues/2026-08-25.json
./newsletter/send.sh newsletter/issues/2026-08-25.json

# 配信まわりを直したら、上げる前にこれを通す（メールは1通も出ない）
node newsletter/selftest.mjs
```

立ち上げの手順・環境変数・法令まわりは
[`docs/newsletter-system.md`](./docs/newsletter-system.md) に。

**名簿のCSVと、そこから作った `import.sql` はリポジトリに入れない**（`.gitignore` 済み）。

## 更新方法

ファイルを追加・修正して以下を実行すると、1〜2分で反映されます。
Cloudflare Pages が `main` を見ていて、push のたびに自動で配信し直します。

```bash
git add .
git commit -m "資料を更新"
git push origin main
```
