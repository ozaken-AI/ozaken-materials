# トップで配布する3資料の生成元

2026-09-14の「5レベル・業務変革・51施策に絞って初心者向けに改善」の指定による改訂です。本文の正は同ディレクトリのJSON、組版は `build.py`。既存PDFへページを重ねたり、暗号化HTMLを復号して丸ごと上書きしたりしません。

| 本文 | 配布先（リポジトリルートから） | 構成 |
|---|---|---|
| `levels.json` | `01_concept/five-levels-of-delegation.pdf` | 29ページ／説明・Gem・Workspace Studio・役割・A4縦の設計シート |
| `business.json` | `04_practice/business-transformation-guide.pdf` | 28ページ／SIPOCから標準化・効果測定・4枚のA4縦シート |
| `measures.json` | `05_drive/ai-51-measures.pdf` | 16ページ／先頭は51施策のA4横一覧・全項目の実行案内・A4縦シート |

## 内容を直すとき

- `AGENTS.md`・`docs/operations.md`・`docs/lecture-design.md` と資料制作／評価スキルを先に読む
- 今回の対象は上記3つの公開PDFとトップの配布案内だけ 他のPDFや講演HTMLは別の改訂依頼として扱う
- 5レベルは筆者のモデル 製品の公式等級と混同しない レベル2と3は別ルート トリガー3種類は並列の選択肢であり順序を示す矢印でつながない
- Googleの操作名・利用条件・参照範囲は改訂時に公式ガイドを読む 現在の出典は `levels.json` の最終ページ アカウントの利用可否と実機検証の有無は検証記録に分けて残す
- コピー用の指示・架空の入力・期待結果・通常／不足／矛盾のテストをセットで直す 条件だけ厳しくして入力例や期待結果を古いままにしない
- SIPOCは業務名 → P → O・C → S・Iの記入順 Cと最終確認者を区別 週次報告の①②④＝◎ ③＝○ ⑤＝×と3基準を維持
- 標準化の80点はたたき台の完成度の比喩 成果物の許容誤り率ではない
- 51施策は `groups` が名称・並びの正で 通し番号は01-51 詳細表の番号と名称も一致させる 残す成果物と担当は実務例であり一律の必須規格ではない
- 旧PDFの「基盤15／推進24／発展12」は番号との対応が明示されず 別の基盤解説には名称・番号の食い違いもあった 本版では推測の割当をせず「困りごとから選ぶ」導線へ変更 関連HTMLを直す場合は正典同士を照合する
- A4縦の記入シートを付録として同じPDFに入れる 追加ダウンロードを求めない クリックしないと内容が出ないパーツやフォーム操作は使わない
- ページの追加・削除では「p.」の参照・先頭の案内・トップのページ数・サムネイルを更新する

## 生成

Python 3.12と `requirements.txt` のパッケージを利用します。Popplerの `pdftoppm` は画像検証用です。フォントはGoogle Fontsの配布元から初回取得し、通常 `~/.cache/ozaken-pdf-fonts/` へ保存します。本文へマシン固有パスやパスワードを埋め込みません。

```sh
python3 -m venv /absolute/private-build/venv
/absolute/private-build/venv/bin/python -m pip install -r 99_assets/pdf-src/beginner_guides/requirements.txt
/absolute/private-build/venv/bin/python 99_assets/pdf-src/beginner_guides/build.py \
  --output-root /absolute/private-build/preview \
  --manifest /absolute/private-build/manifest.json
/absolute/private-build/venv/bin/python 99_assets/pdf-src/beginner_guides/check.py \
  --output-root /absolute/private-build/preview \
  --report /absolute/private-build/check.json
```

`--only levels`／`business`／`measures` で個別生成できます。`--font-cache` でキャッシュ場所を変更できます。`fonts.lock.json` のURLとSHA-256が一致しなければ停止します。フォントを更新する場合は意図を記録してロックも更新し、全ページを見直してください。

本文は選択・検索できる文字、図とQRはベクターです。書体はShippori Mincho B1・Zen Kaku Gothic New・Hanken Grotesk。フォントにない文字、枠からのはみ出し、フッターへの侵入はビルドを止めます。文字を小さくして押し込まず、文章を分けるかページを分けて直してください。

この3資料はReportLabで直接PDFを生成します。従来の資料スキルにあるHTML→ブラウザPDFの手順と異なる専用入口です。2026-09-14の環境ではブラウザ操作権限がなく、許可されたPDFファイル生成・Poppler描画で再現性を確保しました。今後もこの3資料を古いHTML生成器で上書きしないでください。`../business-transformation-guide.py` は本ビルダーの `--only business` 互換入口です。

## 画像での確認と差し替え

1. 3PDFをPopplerで全ページPNGにする `pdftoppm -scale-to 1440 -png input.pdf /absolute/private-build/render/p`
2. 全ページを目視する 特に表・プロンプト・A4縦の記入欄・QRを拡大して確認する
3. `check.py` で本文の欠落・ページ外の文字・リンク領域・参照番号・全51項目の一致を確認する この検査だけで視覚確認済みとはしない
4. 期待する3件100万円・短縮50分×年48回＝40時間・換算120,000円を確認する 生成AIが同じ結果を返すと保証する検査ではない
5. 検証したPDFを表の同じパスへコピーする 先頭ページからJPEGのカバーを生成し `99_assets/download-covers/` の同名画像を差し替える
6. `index.html` の対象3カードだけ説明・ページ数・画像寸法を更新する `data-gate`・ダウンロードURL・他カード・隠し操作を維持する
7. `git diff --check` と公開前の共通検査を通す 本番反映は `docs/operations.md` に従う

画面用16:9ページとA4縦が混在します。印刷では「用紙に合わせる」「自動で縦横を選ぶ」を利用できます。51施策一覧だけならp.1、記入シートだけなら各案内で示したページを指定します。PDFは静止画で全情報を表示し、アニメーションを前提にしません。

配布先3PDFとJPEG以外に、レンダーPNG・確認用PDF・復号HTML・フォントキャッシュ・私用環境の依存パッケージをGitへ入れないでください。
