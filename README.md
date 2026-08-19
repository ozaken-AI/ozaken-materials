# ozaken-materials

小澤健祐（おざけん）のAI関連解説資料アーカイブ。トップページは [`index.html`](./index.html)（GitHub Pages 公開中: https://ozaken-ai.github.io/ozaken-materials/ ）。

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

## 更新方法

ファイルを追加・修正して以下を実行すると、数分後に GitHub Pages に反映されます。

```bash
git add .
git commit -m "資料を更新"
git push origin main
```
