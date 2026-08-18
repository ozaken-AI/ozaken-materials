# 許可ドメインの疎通確認（2026-08-18）

環境（weekly）に `docs/weekly-allowed-domains.txt` を設定した直後の実測。
**結論から言うと、設計が想定していた一次情報にはほぼ全部降りられるようになった。**
`docs/weekly-system.md` §9 の「curl 全滅・WebFetch 全滅」という状態は解消している。

測定方法は2経路。

- `curl`（`HTTPS_PROXY=http://127.0.0.1:38835` 経由。UAは Chrome 相当を指定）
- `WebFetch`（別経路。同じホストでも結果が違うことがある）

---

## 1. 結果表

| ホスト | curl | WebFetch | 判定 |
|---|---|---|---|
| `www.sec.gov` | 403 → **UA指定で200** | **200** | ✅ SEC規約どおり連絡先入りUAが要る |
| `efts.sec.gov`（全文検索API） | **200**（JSON） | 200 | ✅ |
| `arxiv.org` | **200** | **200**（cs.AI recent = 1,276本） | ✅ |
| `export.arxiv.org/api` | **200** | — | ✅ |
| `www.meti.go.jp`（HTML） | **200** | **403** | ⚠️ curlのみ |
| `www.meti.go.jp`（PDF） | **200**（1本100KB／3.6MB とも取得成功） | — | ✅ **PDF本文に降りられる** |
| `www.enecho.meti.go.jp` | **200** | — | ✅ |
| `www.rieti.go.jp`（HTML／DP本体PDF） | **200** | — | ✅ |
| `eur-lex.europa.eu` | **202**（本文0バイト） | **本文空** | ❌ **AWS WAF のボット判定**。許可ドメインの問題ではない |
| `digital-strategy.ec.europa.eu` | **200** | **200** | ✅ 欧州委員会／AI Office の一次情報はここで足りた |
| `www.gallup.com` | **200** | **200** | ✅ |
| `news.crunchbase.com` | **200** | **200**（見出し＋日付が取れる） | ✅ |
| `artificialanalysis.ai` | **200**（1.7MB） | 200 だが**数値は取れない** | ⚠️ 表がJSで描かれる |
| `openai.com` | **403** | **403** | ❌ Cloudflareのボット遮断。egressは通っている |
| `www.anthropic.com` | **200**（415KB） | **200** | ✅ **発表日がHTMLから直接読める** |
| `blog.google` | **200** | **200** | ✅ |
| `example.org`（未許可） | **CONNECT tunnel failed, 403** | **`EGRESS_BLOCKED`** | ✅ **想定どおり弾かれる** |

未許可ホストは curl だと `curl: (56) CONNECT tunnel failed, response 403`、WebFetch だと
`{"error_type":"EGRESS_BLOCKED"}` になる。**許可リストは効いている。**

### 失敗の3分類（ここを混ぜない）

同じ「取れない」でも原因が違い、対処も違う。

| 分類 | 見え方 | 例 | 対処 |
|---|---|---|---|
| **A. egressで弾かれた** | `CONNECT tunnel failed` / `EGRESS_BLOCKED` | example.org, occto.or.jp | 許可リストに足す |
| **B. 到達したが原点が拒否** | 403 / 401 / 202 | openai.com, eur-lex, reuters.com | **足しても直らない** |
| **C. 到達したが中身がJS** | 200 だが数値が無い | artificialanalysis.ai | 別の取り方が要る |

---

## 2. `docs/weekly-allowed-domains.txt` に足すべき行

### 2-1. apex だけ書いてあって www で落ちるもの（**既存リストのバグ**）

`*.` はサブドメインだけに当たる、という注意書きは守られているが、**逆向きの漏れ**があった。
apex を書いて `*.` を書いていないホストが、`www.` へリダイレクトした先で落ちる。

| ホスト | 症状 |
|---|---|
| `lmarena.ai` | apex は 301 → `www.lmarena.ai` で **CONNECT 403** |
| `vals.ai` | apex は 308 → `www.vals.ai` で **接続リセット** |
| `epoch.ai` | apex は 200 だが `www.epoch.ai` は **CONNECT 403** |

```
*.lmarena.ai
*.vals.ai
*.epoch.ai
```

**このファイルは環境設定にそのまま貼る前提なので、コメント行は入れない。** 追記済み。

（`amd.com` は `*.amd.com` が既にあるので通っている。同じ書き方に揃える）

### 2-2. 今回の取材で実際に必要になったのに入っていなかったもの

| 行 | なぜ要るか |
|---|---|
| `occto.or.jp` / `*.occto.or.jp` | 系統接続の元データ。METI資料が出所として挙げている |
| `tepco.co.jp` / `*.tepco.co.jp` | 印西の需要増の一次情報。METI資料が脚注で引いている |
| `jdcc.or.jp` / `*.jdcc.or.jp` | 日本データセンター協会。METI資料がヒアリング先として挙げている |
| `ec.europa.eu` / `*.ec.europa.eu` | 欧州委員会の digital-strategy 以外のサブドメイン |
| `snowflake.com` / `*.snowflake.com` | 提携プレスの原典（Snowflake側） |
| `newsroom.accenture.com` | 同（Accenture側） |
| `pwc.com` / `*.pwc.com` | 同（PwC側） |

**いずれも `docs/weekly-allowed-domains.txt` に追記済み。**

`ec.europa.eu` を足すと `ai-act-service-desk.ec.europa.eu`（委員会公式のAI Act解説）と
`futurium.ec.europa.eu` が開く。EUR-Lex の代わりにはならないが、条文の解釈は委員会の言葉で読める。

### 2-3. 足しても直らないもの（**リストをいじらない**）

- **`eur-lex.europa.eu`** … 許可済みだが AWS WAF のJSチャレンジで 202 が返る。
  curl も WebFetch も突破できない。**正文の逐条確認は当面できない**と割り切る
- **`openai.com` / `x.ai`** … Cloudflare のボット遮断で 403。egress は通っている
- **`reuters.com`** … 401。ログイン壁

**この3つを「ドメインを足せば直る」と誤解しないこと。** 上の分類A/B/Cのうち B に当たる。

---

## 3. 取り直した結果

**保留していた3件のうち2件を解除、1件は日付だけ確定した。**

1. **EU AI Act（tier 3 → tier 1、保留解除）** ─ EUR-Lex は WAF で開かなかったが、**欧州委員会の
   digital-strategy.ec.europa.eu（AI Office 所管サイト）で一次情報として足りた**。2026年8月2日から
   始まるのは第50条の透明性義務と、AI Office・加盟国当局の執行責任で、当初の理解どおり。
   Digital Omnibus は **Regulation (EU) 2026/1744**、2026年7月27日施行、提案は COM(2025) 836（2025年11月19日）。
   高リスクの延期は **Annex III → 2027年12月2日／Annex I → 2028年8月2日** で事実。
   日本企業の義務は第2条の域外適用で決まり、EU市場に上市・提供・使用する限り第50条の4項目を負う。
2. **日本の電力（数値を取得）** ─ 経産省の審議会PDFに実際に降りた。印西・白井エリアで
   **連系待ち約40件・申込容量 約2,500MW・工事総額2,000億円超**。データセンター実態調査は
   **回答190件/264件（回答率72%）、2025年7月22日〜31日**。**264件中144件が計画変更、うち104件が後ろ倒し**。
   系統用蓄電池は接続検討 **約15,900万kW** に対し連系済み **約50万kW**（2025年9月末）。
   図表は本文抽出が崩れるため該当ページを画像化して読み、**エリア別の積み上げが本文の概数と一致すること**を確認した。
3. **Anthropicの提携（発表日を確定）** ─ HTMLの表示日付を直接読んだ。**Accenture は2026年ではなく2025年12月9日**で、
   Snowflakeと同じく今週の話ではなかった。AIサービス会社は2026年5月4日、Partner Network は2026年6月3日、PwC は2026年5月14日。
4. **埋めずに `open` に残したもの** ─ AI Act 正文の逐条と官報公布日（EUR-Lex未到達）、
   データセンターのエリア別接続検討件数・容量（**公表資料がエリア別に分解していない**）、
   接続待ちの年数（資料の表現は「数年以上の工期を必要とする場合も存在」まで）、
   OCCTOの元データ（未許可ドメイン）。**無理に数字を作らず、理由つきで残した。**

道具の追加：`poppler-utils`（`pdftotext` / `pdftoppm`）を入れた。
**審議会資料は図表が主で、テキスト層だけでは数字の対応関係が壊れる。**
ページを画像にして読み、合計値で答え合わせをする工程が要る。
