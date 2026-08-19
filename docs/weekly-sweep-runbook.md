# 週次スイープの手順書（毎週これを実行する）

`docs/weekly-system.md` が設計、この文書が**実行手順**。
毎週、まっさらなセッションがこの1枚を読んで同じ品質のスイープを回せることを目的にする。

対象は L1〜L3（収集・選別・深掘り）まで。**記事の執筆と公開は含めない。**
出すのは `weekly/<対象週の火曜>/sweep.json` という材料の束で、
どれを載せるか決めるのも、意味づけのコメントを書くのも、おざけん本人の仕事。

---

## 0. 対象週の決め方

**水曜〜火曜の7日間。** 実行日の直前に終わった水〜火を対象にする。

| 実行日 | 対象週 | 出力先 |
|---|---|---|
| 2026年8月19日（水） | 2026-08-12（水）〜2026-08-18（火） | `weekly/2026-08-18/sweep.json` |
| 2026年8月26日（水） | 2026-08-19（水）〜2026-08-25（火） | `weekly/2026-08-25/sweep.json` |

ディレクトリ名は**対象週の火曜の日付**。実行日ではない。

対象週を決めたら、**始める前に既にやってあるかを確認する。**

```bash
git fetch origin --prune
git ls-remote --heads origin 'claude/weekly-sweep-*'
```

`claude/weekly-sweep-MMDD` が既に origin にある、または
`weekly/<対象週の火曜>/sweep.json` が既に main にあるなら、その週は済んでいる。
**やり直さず、その旨だけ報告して終わる。**
（Routine を作った当日など、同じ週に2回走る条件が実際に起こる）

水曜17時（JST）に回すのは、米国時間の火曜が完全に終わってからにするため。
Anthropic・TechCrunch・Crunchbase は米国時間で日付が付くので、
日本時間の水曜朝に回すと火曜ぶんを半日取りこぼす。

---

## 1. いちばん大事なこと

### 本数を絞らない

以前は「各領域1本」に絞っていたが、**その制限は外した。**
`weekly/watchlist.yml` の7領域それぞれについて、対象週に起きたことを
**上限なしに拾えるだけ拾う。** 重要なものは全部出す。

### 起きていない週は「起きていない」と書く

**その領域で対象週に何も起きていなければ、古い情報で埋めない。**
`quiet_domains` に `{"domain": "...", "note": "..."}` を書く。
領域としては1件取れたが系統として静かだった場合（例：日本の省庁がゼロ）は
`notes` に理由つきで書く。ここを埋めるために対象週の外から持ってくるのが、
この仕組みがいちばん壊れる壊れ方。

### 日付は必ず独立に検証する

**検索スニペットは日付を落とす。** 過去に8か月前の発表を「今週の話」として
拾いかけた事故が実際に起きている。候補にする前に、必ず原典側で日付を確認する。

| 種別 | どこで日付を確認するか |
|---|---|
| 企業ブログ | HTML本文の表示日付（Anthropic は `Aug 14, 2026` の形で本文に入っている） |
| blog.google | カテゴリ別 RSS の `pubDate` |
| arXiv | `arxiv.org/abs/<id>` の `[Submitted on ...]` |
| Artificial Analysis | モデルページの FAQPage 構造化データ（後述） |
| Hugging Face のモデル | `huggingface.co/api/models?search=...` の `createdAt` |
| SEC | 提出書類の "Date of Report (Date of earliest event reported)" |
| 省庁 | 一覧ページの日付。和暦（令和8年）と西暦が混在する |

**複数の情報源で日付が食い違ったら、食い違ったまま書く。**
片方を選んで断定しない。`notes` と該当スレッドの `open` に残す。
（2026-08-18の実例：Qwen3.8 27B は Artificial Analysis が 2026-08-14、
Hugging Face API の `createdAt` が 2026-08-05）

### 一次情報に降りられないものは落とす

`source_url` は原則として一次情報のURL。到達できないものは候補にしない。

ただし例外が2つある。どちらも `tier: 2` にして `source_name` に出典を明記し、
**なぜ一次に届かなかったかを `notes` に書く。**

1. `weekly/watchlist.yml` がその領域の `primary` に挙げている媒体
   （capital / startup の Crunchbase News・TechCrunch など）
2. 一次情報のドメインが egress でブロックされていて代替がない場合
   （ホワイトハウス報告書 → ジェトロ、IBMのプレス → TechCrunch など）

**「協議中との報道」「関係者によると」は落とす。** 一次でも二次でもない。

---

## 2. 出力するもの

### `weekly/<対象週の火曜>/sweep.json`

```json
{"window": {"from": "2026-08-12", "to": "2026-08-18"},
 "checked_at": "2026-08-18",
 "candidates": [ ... ],
 "quiet_domains": [{"domain": "talent", "note": "対象週に一次情報の動きを確認できなかった"}],
 "notes": "拾いきれなかった領域や、到達できなかった原典があれば書く"}
```

候補1件の形。**埋まらない項目がある候補は落としてよい。**

| 項目 | 中身 |
|---|---|
| `domain` | `tech` / `regulation` / `talent` / `org` / `society` / `capital` / `startup` |
| `date` | 出来事の日付（YYYY-MM-DD）。**対象週の中であること** |
| `title` | 20〜40字の見出し |
| `what` | 何が起きたか（2〜3文） |
| `numbers` | 数値の配列。各要素に `value` `unit` `note`。**原典に書いてあるとおりに写す** |
| `source_url` | 一次情報のURL |
| `source_name` | 出典の名前と日付（例「Google公式ブログ（2026年8月13日）」） |
| `tier` | 1（一次）／2（二次） |
| `why` | 企業でAI活用を進める人・経営者にとって、なぜこれが効くのか（1〜2文） |

書き終えたら必ず機械的に検査する。

- 全候補の `date` が対象週の中に入っているか
- `title` が20〜40字に収まっているか
- 必須項目が空でないか、`numbers` の各要素に `value`/`unit`/`note` が揃っているか
- JSON として読めるか

### `weekly/threads/*.json` への追記

**これが週をまたいで深くなるかどうかの分かれ目。**
該当スレッドの `facts` の**先頭に**今週の事実を出典つきで足す（新しい順）。

```json
{"date":"2026-08-13","text":"何が起きたか。数値を本文に入れる","src":"https://...","tier":1,"checked":"2026-08-18","note":"日付の食い違いや注意点があればここ"}
```

あわせて次を更新する。

- `open` … 今週の事実から新しく生まれた「未解決の問い」を足す。
  **翌週ここに答えが出たら、それが自動的にトップ記事になる。**
- `note` … 今週のスイープで分かったこと、静かだった系統

**該当スレッドが無い話題は、新しいスレッドを作ってよい。**
その場合は `slug` / `domain` / `title` / `watching` / `facts` / `open` /
`stance`（「未記入（おざけんが書く）」） / `falsify` / `related` / `written` / `note` を揃える。
既存ファイルの書式に合わせること。

`stance` は**絶対に埋めない。** 意味づけは本人の仕事。

---

## 3. どこを見るか

`weekly/watchlist.yml` の7領域を全部さらう。以下は前回（2026-08-18）に
実際に降りられた経路。**毎回このリストどおりに一巡する。**

### tech

| 経路 | 取り方 |
|---|---|
| Anthropic | `anthropic.com/news` `/research` `/engineering` を curl。HTML中に `Aug 14, 2026` 形式で日付が入る |
| Google | `blog.google/<category>/rss/` の `pubDate` で機械的に対象週を切る。一覧ページはJSで読めない |
| DeepMind | `deepmind.google/blog/rss.xml` |
| Artificial Analysis | 各モデルページの FAQPage 構造化データ（§4参照） |
| arXiv | `huggingface.co/papers?date=YYYY-MM-DD` を7日ぶん取り、拾ったIDは `arxiv.org/abs/<id>` で投稿日を確認 |
| Hugging Face Blog | `huggingface.co/blog` の一覧に日付が入る |
| ベンダー各社 | `blogs.nvidia.com/feed/`、`nvidianews.nvidia.com/releases.xml`、`aws.amazon.com/blogs/machine-learning/feed/`、`news.microsoft.com/source/feed/`、`sakana.ai/blog/`、`mistral.ai/news/` |

### regulation

| 経路 | 取り方 |
|---|---|
| 経産省 | `meti.go.jp/press/index.html`（`main/whatsnew.html` は403） |
| 総務省 | `soumu.go.jp/menu_news/s-news/index.html` — **Shift_JIS。cp932 でデコードすること** |
| 個人情報保護委員会 | `ppc.go.jp/news/press/2026/` |
| デジタル庁 | `digital.go.jp/news` |
| 内閣府CSTI | `www8.cao.go.jp/cstp/ai/index.html`（AI戦略トピックス） |
| 内閣官房 | `cas.go.jp/jp/houdou/index.html` |
| 金融庁・IPA・文化庁 | `fsa.go.jp/news/index.html`、`ipa.go.jp/pressrelease/index.html`、`bunka.go.jp/koho_hodo_oshirase/hodohappyo/index.html` |
| EU | `digital-strategy.ec.europa.eu/en/news`（一覧に日付が出る） |
| NIST | `nist.gov/news-events/news` |
| 海外の政策全般 | `jetro.go.jp/biznews/`（日付順の一覧。tier 2 だが到達できる） |

### talent / org / society

| 経路 | 取り方 |
|---|---|
| Gallup | `news.gallup.com/topic/artificial_intelligence.aspx` |
| Pew | `pewresearch.org/topic/internet-technology/artificial-intelligence/` |
| 国内の実態調査 | `jipdec.or.jp`、`smrj.go.jp`、`ipa.go.jp`（年1回・年度単位なので週次では滅多に動かない） |
| 導入事例 | AWS / Microsoft / Google Cloud のブログ。**事例記事の公開日と、稼働開始日を混ぜない** |

### capital / startup

| 経路 | 取り方 |
|---|---|
| Crunchbase News | `news.crunchbase.com/sections/venture/` の一覧に日付が出る。集計記事はここが集計元＝tier 1 |
| SEC | `efts.sec.gov/LATEST/search-index?q=...&forms=8-K&startdt=...&enddt=...`（§4参照） |
| TechCrunch | RSS は当日ぶんしか無い。`techcrunch.com/2026/08/<DD>/` の日別アーカイブを7日ぶん取る |
| 国内 | `release.tdnet.info`、`prtimes.jp`（PR TIMES は相対時刻表示で日付絞り込みができない） |

### 到達できないもの（毎回試さなくてよい）

**許可ドメインをいじっても直らない。** `weekly/2026-08-18/egress-check.md` の分類B。

- `openai.com` / `x.ai` … Cloudflare のボット遮断で403
- `eur-lex.europa.eu` … AWS WAF で202（本文が空）。条文は `digital-strategy.ec.europa.eu` で代替
- `reuters.com` … 401
- `whitehouse.gov` / `newsroom.ibm.com` / `preferred.jp` … egress でブロック
- `ai.meta.com` … 400 を返し、RSS も取れない

---

## 4. 効く取り方（前回わかったもの）

### Artificial Analysis は構造化データから取る

本文はJSで描かれて数値が読めないが、**各モデルページに FAQPage の
`application/ld+json` が埋まっている。** ここからプレーンテキストで
リリース日・知能指数・入出力単価・トークン毎秒・TTFT・コンテキスト長が取れる。

```bash
curl -sSL -A "$UA" https://artificialanalysis.ai/models/<slug> -o m.html
python3 -c "
import re,html
h=open('m.html',encoding='utf-8',errors='ignore').read()
i=h.find('\"@type\":\"FAQPage\"')
seg=html.unescape(h[i:i+5000])
for q,a in re.findall(r'\"name\":\"([^\"]+)\",\"acceptedAnswer\":\{\"@type\":\"Answer\",\"text\":\"([^\"]+)\"',seg):
    print('Q:',q,'\n  A:',a)"
```

同じHTMLの埋め込みJSONに `\"slug\":...\"releaseDate\":\"YYYY-MM-DD\"` が
他モデルぶんも入っているので、**1ページ取れば対象週にリリースされた
モデルを全部列挙できる。**

### blog.google はカテゴリ別RSS

一覧ページはJSで読めないが `/<category>/rss/` が生きている。
`pubDate` で対象週を機械的に切れる。最低でも次を回す。

```
blog.google/rss/
blog.google/innovation-and-ai/rss/
blog.google/innovation-and-ai/technology/ai/rss/
blog.google/innovation-and-ai/models-and-research/gemini-models/rss/
blog.google/innovation-and-ai/technology/developers-tools/rss/
blog.google/innovation-and-ai/products/gemini-app/rss/
blog.google/innovation-and-ai/models-and-research/google-deepmind/rss/
```

### SEC 全文検索

いちばん重い一次情報がここから出る（2026-08-18 の NVIDIA 8-K = 1,050億ドルの保証）。

```bash
UA='ozaken-weekly-research k.ozaken1222@cinematorico.com'   # SEC規約でUAに連絡先が要る
curl -sS -A "$UA" 'https://efts.sec.gov/LATEST/search-index?q=%22AI+data+center%22&forms=8-K&startdt=2026-08-12&enddt=2026-08-18'
```

クエリは最低でも `"artificial intelligence"` `"generative AI"` `"AI data center"` の3本を回す。
ヒットは `_source.display_names` と `file_date` で絞り、本命は
`www.sec.gov/Archives/edgar/data/<cik>/<accession>/<file>` を直接読む。

### 共通

- curl は Chrome 相当の UA を指定する。指定しないと 403 が増える
- 省庁サイトは Shift_JIS が混ざる。`cp932` でデコードを試す
- arXiv API（`export.arxiv.org/api/query`）は連投すると 429/503 になる。
  `arxiv.org/abs/<id>` を数秒あけて叩くほうが速い
- 作業ファイルはスクラッチパッドに置く。リポジトリを汚さない

---

## 5. やってはいけないこと

- **暗号化されたHTMLに触らない。** `weekly/*.html`、`0*_*/*.html`、`passwords.html` など。
  マスターパスワードは渡されていない。`git status` に `.html` が出たら何か間違えている
- `docs/weekly-allowed-domains.txt` を、到達できない原典のために書き換えない。
  §3末尾の5つは許可リストの問題ではない
- スレッドの `stance` を埋めない
- 対象週の外の出来事を候補に入れない。背景として書きたいときは
  スレッドの `facts` に入れ、`note` に「対象週の外」と明記する

---

## 6. 最後に

`main` から `claude/weekly-sweep-MMDD`（MMDD は**対象週の火曜**）を切り、
コミットしてプッシュする。**プルリクエストは作らない。**

コミットメッセージは、何を拾って何を落としたかが分かるように書く。
件数だけ並べても、翌週の自分が読んで役に立たない。

報告は3点だけ、簡潔に。

1. 領域ごとの件数（今週動きがあった／なかった）
2. いちばん効くと思った3件と、その理由
3. 拾えなかったもの（あれば理由）
