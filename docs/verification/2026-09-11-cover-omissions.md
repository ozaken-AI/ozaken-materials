# 共通表紙の適用漏れと印刷表示の修正

2026-09-11 本人から「人的資本経営の、新しい姿」などに旧デザインが残るとの指摘を受けて再点検

## 対象と原因

全122資料のうち4資料は本文レイヤーが存在する一方で共通表紙が未適用だった

- `06_people/human-capital-new-shape.html`
- `03_tools/copilot-plus-pc.html`
- `09_role/marketing.html`
- `09_role/sony-three-layer-platform.html`

現在の復号HTMLを起点に4件の表紙のみ共通化した 他118件の表紙構造は維持
印刷CSSでは表紙の暗い疑似要素を消すセレクターの優先度が通常CSSより低かったため `section[data-oz-cover]::before` に揃えた 共通表紙CSSのこの修正は122資料へ適用した

## 保持と検証

- 122資料で元の本文の全章がバイト単位で一致 表紙以外の本文CSS・既存スクリプト・リンクを保持
- 全件で変換の冪等性と暗号化後の復号一致 ラップ鍵Wの保持 `check_blocks` の前後差を検査
- 4件について実ブラウザーで表紙を確認 1422px・390px・印刷CSS1010pxの計12条件で全章の文字の非表示・外側はみ出し・横オーバーフローなし
- 印刷CSSでは4件とも表紙の暗い疑似要素が非表示 白背景で見出しを読めることを確認
- 表紙・本文変換と適用漏れの回帰検査16件が成功
- 新しい `check_design.py` で全122資料の表紙・本文レイヤーと各章の構造的な適用漏れが0件であることを確認

印刷CSSの確認であり PDFファイルのページ分割の確認ではない

## 再発防止

`apply_cover.py --only` で対象資料を指定できる `--input-dir` はリポジトリ外の現行復号HTMLを入力にし `--update` 時は古いベースラインを拒否する
公開前に `check_encrypted.py --staged` と `check_design.py --staged` を使い ステージ上の配信物を検査する 共通本文の有無だけで共通表紙も更新済みと判断しない

生成元 `.claude/skills/ozaken-shiryo/sources/lecture_cover/cover.css` と `scripts/apply_cover.py`
適用漏れ検査 `.claude/skills/ozaken-shiryo/scripts/check_design.py`
