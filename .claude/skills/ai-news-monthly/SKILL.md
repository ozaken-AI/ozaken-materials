---
name: ai-news-monthly
description: 月次のAIトレンドまとめと、index.html の「今月のAIトレンド」セクション更新。前月分の週次ダイジェストを束ね直して月次トレンド原稿を作り、index.html のトレンド枠を差し替え、前月ぶんをトレンドアーカイブへ送る。変更はプルリクエストで提出し、Slackでおざけんの承認を取ってからマージする。「今月のAIトレンド」「月次まとめ」「トレンド更新して」「index.htmlのトレンド枠を更新」などの依頼、および月初の月次ジョブから使う。
---

# 月次AIトレンド → index.html 反映

前月の週次ダイジェスト（`10_ニュース/weekly/`）を束ね直し、
`index.html` の「今月のAIトレンド」セクションを差し替える。

## この仕組みの絶対ルール

1. **`main` に直接pushしない。** 必ず作業ブランチ → PR → おざけんの承認 → おざけんがマージ。
2. **差し替えてよいのは `<!-- AI-TRENDS:START -->` 〜 `<!-- AI-TRENDS:END -->` の間だけ。**
   index.html のそれ以外は1文字も触らない。マーカーのコメント自体も消さない。
3. 週次ダイジェストが1本も無い月は、**セクションを空にせず、前月のまま残して** その旨をSlackで報告する。

---

## Phase 1 ── 対象月と素材を確定する

月初に走る前提。対象は **前月**。日付は `date` コマンドで取る。

```bash
date +%Y-%m-%d
date -d 'last month' +%Y-%m       # 対象月
ls 10_ニュース/weekly/            # 素材の週次ダイジェスト
```

対象月に含まれる週次ダイジェストを全部読む。週次が欠けている週があれば、その週だけ `WebSearch` で補う
（`ai-news-weekly` の `references/sources.md` の基準に従う）。

## Phase 2 ── 月次原稿を書く

`10_ニュース/monthly/YYYY-MM.md` を作る。実例は `10_ニュース/monthly/2026-07.md`。

週次の羅列にしない。**1か月を通して見えた流れを1本の線にする** のがこのジョブの仕事。

構成:

```markdown
# YYYY年M月のAIトレンド

## 総括
2〜4文。「今月は◯◯の月だった」と言い切る。3行で言えないなら、まだ束ね方が甘い。

## 生成AI
このカテゴリの今月の一言（1文）
### MM/DD ─ 見出し
- 出典: URL
- 意味づけ: 1〜2文

## AIエージェント
（同じ形式）

## フィジカルAI
（同じ形式）

## 採否メモ
拾ったが載せなかった主要ニュースと、その理由（後から振り返るため）
```

**掲載件数はカテゴリごとに3〜4件、月あたり合計12件まで。** 週次から拾い上げるとき、
「1か月経ってもまだ意味が残っているか」で足切りする。週次で載せたが月次では落とす、が正しい運用。

## Phase 3 ── index.html のトレンド枠を差し替える

### 3-1. 現在の枠を退避する

`index.html` の `<!-- AI-TRENDS:START -->` 〜 `<!-- AI-TRENDS:END -->` の中身を丸ごと取り出す。
これが「先月まで表示されていた月」＝アーカイブへ送るブロック。

### 3-2. アーカイブへ送る

`10_ニュース/トレンドアーカイブ.html` の `<!-- ARCHIVE:INSERT -->` の **直後** に、退避したブロックを挿入する（新しい月が上）。
挿入時に手を入れる点:

- `<div class="tr-foot">…</div>` は削る（アーカイブページには不要）
- `<div class="tr-head">` の直前に、月アンカー `<div id="YYYY-MM" style="scroll-margin-top:2rem"></div>` を置く
- 初回のみ、プレースホルダの「まだ過去月はありません」の p タグを消す

### 3-3. 新しい月を書き込む

Phase 2 の原稿を、既存ブロックと**同じHTML構造**で書く。クラス名を勝手に増やさない。

```html
    <div class="tr-head">
      <span class="tr-month">YYYY.<b>MM</b></span>
      <p class="tr-lead">総括。<b>核心</b>は b タグで、赤にしたい1語だけ span.hot で。</p>
    </div>

    <div class="tr-groups">
      <article class="tr-group">
        <h3 class="tr-gt"><span class="tr-gn">01</span>生成AI</h3>
        <p class="tr-gs">カテゴリの今月の一言。</p>
        <ul class="tr-list">
          <li>
            <span class="tr-d">MM/DD</span>
            <span class="tr-t"><a href="出典URL" target="_blank" rel="noopener">見出し</a></span>
            <span class="tr-n">意味づけ。40〜60字。</span>
          </li>
        </ul>
      </article>
      <!-- 02 AIエージェント / 03 フィジカルAI も同じ形 -->
    </div>

    <div class="tr-foot">
      <span>出典は各見出しのリンク先。週次で集めた元ニュースは 10_ニュース／weekly に置いています。</span>
      <span class="tr-arch"><a href="10_ニュース/トレンドアーカイブ.html">過去のトレンド →</a></span>
    </div>
```

書式の決まり:

- `span.hot`（赤字）は **セクション全体で2回まで**。多用すると効かなくなる
- 意味づけは事実の言い換えにしない。「で、何が変わるのか」を書く
- リンクは必ず `target="_blank" rel="noopener"`

### 3-4. 壊れていないか検証する

```bash
python3 - <<'EOF'
import re
h = open('index.html').read()
a = h.count('<!-- AI-TRENDS:START -->'); b = h.count('<!-- AI-TRENDS:END -->')
assert a == 1 and b == 1, f'マーカーが壊れた START={a} END={b}'
blk = h.split('<!-- AI-TRENDS:START -->')[1].split('<!-- AI-TRENDS:END -->')[0]
assert blk.count('<article class="tr-group">') == blk.count('</article>'), 'article タグが不一致'
assert blk.count('<li>') == blk.count('</li>'), 'li タグが不一致'
assert blk.count('class="hot"') <= 2, f'hot が {blk.count(chr(34)+"hot"+chr(34))} 回。2回まで'
assert h.count('<section') == h.count('</section>'), 'section タグが不一致'
for u in re.findall(r'<a href="(https?://[^"]+)"', blk):
    pass
print(f'OK — 見出し {blk.count("<li>")} 件 / hot {blk.count(chr(34)+"hot"+chr(34))} 回')
EOF

python3 - <<'EOF'
h = open('10_ニュース/トレンドアーカイブ.html').read()
assert h.count('<!-- ARCHIVE:INSERT -->') == 1, 'ARCHIVE:INSERT マーカーが壊れた'
assert h.count('<section') == h.count('</section>')
assert h.count('<article') == h.count('</article>')
print(f'OK — アーカイブ月数 {h.count(chr(34)+"tr-head"+chr(34))}')
EOF
```

ブラウザでの見た目は確認できないので、**この検証は必ず通してからPRを出す**。

## Phase 4 ── PRとSlack通知

```bash
git checkout main && git pull origin main
git checkout -b claude/trends-YYYY-MM
git add "10_ニュース/" index.html
git commit -m "YYYY年M月のAIトレンドを index.html に反映"
git push -u origin claude/trends-YYYY-MM
```

`mcp__github__create_pull_request`（base: `main`）で提出する。

- タイトル: `YYYY年M月のAIトレンド ─ index.html 反映`
- 本文: 総括 → 掲載した見出し一覧（カテゴリ別）→ 落としたニュースとその理由 → 変更ファイル一覧
- 本文末尾に必ず入れる案内:

```markdown
---
### 確認のしかた
index.html のトレンド枠を差し替え、先月ぶんはトレンドアーカイブへ送りました。

- 掲載した見出し・意味づけに直したいところがあれば、コメントしてください。そのとおりに直します
- 落としたニュースで「これは載せたい」というものがあれば教えてください
- 問題なければマージしてください（マージはおざけんが行ってください）
```

Claude Code のアトリビューションフッターを付ける。
作成後、`mcp__Claude_Code_Remote__subscribe_pr_activity` で購読する。

Slack DM（`channel_id: U078WMGJFRR`）:

```
📊 YYYY年M月のAIトレンドを index.html に反映しました

総括を1〜2文。

**掲載: 生成AI N件 / AIエージェント N件 / フィジカルAI N件**
先月ぶんはトレンドアーカイブへ送りました。

直したいところがあればPRにコメントしてください。問題なければマージをお願いします。
→ PRのURL
```

### PR作成やSlack送信の手段が無いとき

定期実行のセッションには、`mcp__github__*` や `mcp__Slack__*` が渡っていないことがある。
**その場合でも、途中で投げ出さない。**

1. **ブランチのpushは必ず完了させる**（gitコマンドだけでできる）
2. PRが作れないときは、pushの出力に出る PR作成URL
   （`https://github.com/ozaken-AI/ozaken-materials/pull/new/<ブランチ名>`）を控える
3. Slackが使えないときは、**セッションの最終出力に通知内容をそのまま書く**。
   このRoutineはプッシュ通知が有効なので、完了時におざけんの端末に要約が届く
4. 最終出力の冒頭に「Slack／GitHubのツールが無かった」「ブランチ名」「PR作成URL」を必ず書く

恒久的に直したいときは、claude.ai の Routine 設定画面から Slack / GitHub のコネクタを
このRoutineに紐づけ直す（コマンドラインからは付与できない）。

## Phase 5 ── 修正依頼に応じる

PRコメントが届いたら、その指示どおりに直してブランチへpush。1回だけ返信する。
マージ／クローズされるまで購読を続け、マージされたら `unsubscribe_pr_activity` する。

---

## よくある事故と、その回避

| 事故 | 回避 |
|---|---|
| マーカーごと消してセクションが壊れる | Phase 3-4 の検証スクリプトを必ず走らせる |
| 前月ぶんがアーカイブに送られず消える | 3-1 で退避 → 3-2 で挿入、の順を飛ばさない |
| 週次の羅列になって読まれない | 総括を先に書く。3行で言えないなら束ね直す |
| 赤字だらけになる | `span.hot` は2回まで。検証スクリプトが弾く |
| index.html の他の箇所を巻き込む | `git diff index.html` を必ず目視し、マーカー内だけか確認する |
