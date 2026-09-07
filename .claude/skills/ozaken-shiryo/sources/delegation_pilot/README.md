# 「使うAI」から「任せるAI」へ — 講演版

対象は `01_concept/use-to-delegate.html`。表紙・9章・まとめの11面。

- 比較の両側、5つの前提、業務の分担、運用の全段階をHTMLに同時に配置。
- 開閉・＋・再生・内容切り替えを使わない。元の図の重複表示を外し、内容の生成元は `../gen_use_to_delegate.py` に保持。
- 表紙は抽象的な光のカーテン。背景と接続線の演出だけを動かし、読み取る情報は固定。
- 小画面は縦組み。印刷CSSはA4横・1面1ページ。表示用ボタンやアーカイブ誘導は印刷しない。
- 関連リンクと既存QRを保持。文字キーは既存の `apply_keynav` に任せる。

## 生成

```sh
python3 build.py --output /absolute/local-preview/01_concept/use-to-delegate.html
```

既存QR・関連リンクを含める場合は `--preserve`、暗号化された対象HTMLを書き戻す場合は `--update`。マスターは非表示の対話入力で受け取り、ファイルには保存しない。既存のラップ鍵を保持し、復号結果と生成HTMLの一致を検証する。

`--baseline` は旧暗号化HTMLから既存ブロックを復元する場合だけ指定する。

内容と構成は `build.py`、基礎CSSは `pilot.css`、常時表示・印刷のCSSは `lecture.css`、画面内の演出管理は `pilot.js`。共通の `publish.compose()` で組み立てと検査を行う。他の個別資料と台帳は更新しない。

ローカルの確認用ブランチ。本番公開は別の操作。
