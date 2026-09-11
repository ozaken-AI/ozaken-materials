# リポジトリ運用手順

資料の作成・修正から公開後の確認までを、特定のAIや端末に依存せず引き継ぐための入口です。最終更新：2026-09-11。
新しい担当者・AIは [AGENTS.md](../AGENTS.md) とこの手順を読み、担当分野の詳細へ進んでください。

## 作業開始時

リポジトリのルートで実行します。

```sh
git status --short
git branch --show-current
git log -3 --oneline
git worktree list
```

ユーザーが指定した対象を確認します。「テンプレートだけ」「この資料も」「本番へ反映」「ローカルで試す」を区別してください。回答・許可済みのことは同じ会話で再確認せず進めます。別の作業の未コミット変更は保持します。

以下の相対パス・コマンドは、特記しない限りリポジトリのルートが基準です。実際の生成元がどれか分からない場合は、対象のタイトルやファイル名を `rg` で検索します。暗号化された本文は検索用スクリプトで読みます。

## 編集する場所

| 作業 | 主な生成元・設定 | 生成物・関係先 |
|---|---|---|
| トップの構造・隠しコマンド | `index.html` | トップページ |
| トップの見た目・通常の動き | `99_assets/materials-home.css`、`materials-home.js` | `#materials-home` の範囲 |
| トップ下部の人物紹介・実績・3領域 | `index.html`、`99_assets/author-profile.css` | `#author`・`#author-record`・`#aicx`。PR画面とは別 |
| 投影プロフィール | `index.html`、`99_assets/profile-stage.css`、`profile-stage.js` | PRの画面 |
| プロフィール画像 | `99_assets/profile-media.json`、`profile-media.js`、`99_assets/profile/` | [画像差し替え手順](../99_assets/profile-media.md) |
| 開始・終了の演出 | `index.html`、`99_assets/stage-effects.css` | ST / GO / EN等の画面 |
| テンプレート便覧 | `.claude/skills/ozaken-shiryo/sources/build_template_gallery.py`、`sources/template_gallery/lecture.py`・`lecture.css`・`lecture.js` | `template.html` |
| 図形の構造 | `sources/template_gallery/scenes.py`、`scripts/domain_fig.py` | 個々の図版 |
| 講演版の実装例 | `sources/delegation_pilot/build.py`・`pilot.css`・`lecture.css`・`pilot.js` | `01_concept/use-to-delegate.html` |
| 全資料の共通表紙 | `scripts/apply_cover.py`、`sources/lecture_cover/` | 通常・AX Table・研修・Udemy・週次の全資料 |
| 全資料の本文デザイン | `scripts/apply_body.py`、`sources/lecture_body/body.css`・`body.js` | 現在の本文を保持したまま組版と装飾を適用 |
| 共通の背景・表の列ホバー | `sources/lecture_effects.css` | 便覧と講演版の両ビルダーで埋め込む |
| AI-SECI・5レベル・SIPOCの実務解説 | `sources/gen_seci.py`・`gen_five_levels.py`・`gen_sipoc.py`、`practical_guides.py`・`.css` | 現行の完全なHTMLに対象章だけを改訂・追記 |
| その他の個別資料 | `.claude/skills/ozaken-shiryo/sources/gen_*.py` | [生成元対応表](../.claude/skills/ozaken-shiryo/sources/README.md) |
| 共通の組版・暗号化 | `.claude/skills/ozaken-shiryo/scripts/` | `publish.py`、`lockbox.py`、`registry.py`等 |
| 相互参照・概念の正典 | `scripts/crossref_data.py`、`crossref.py` | 関連チップ、`matrix.html`等 |
| 無料配布PDF | `99_assets/pdf-src/` | `99_assets/`の対象PDF |
| 週次トレンド | `weekly/src/`、`weekly/threads/`、`weekly/watchlist.yml` | `weekly/YYYY-MM-DD.html` |
| メルマガ・管理API | `newsletter/`、`functions/` | 購読、名簿、配信停止、送信 |

表内で省略した `sources/` と `scripts/` は `.claude/skills/ozaken-shiryo/` の配下です。

**現在の便覧を `gen_template.py` だけで再生成しないでください。** このファイルは図・本文パーツの見本データと旧フラグメントの生成元です。現在の便覧全体は `build_template_gallery.py` が組み立てます。

**`use-to-delegate.html` を `gen_use_to_delegate.py` → 汎用 `publish.py --update` だけで上書きしないでください。** 現在の講演版は `delegation_pilot/build.py` が旧生成元を参照して組み立て、専用の構成・背景・印刷CSSを適用します。

## 新しい資料を作る

### AI-SECIと5レベル資料を改訂する

2026-09-11の本人指定による本文改訂。AI-SECIは `sources/gen_seci.py`、5レベルのCopilot編・Gemini編は `sources/gen_five_levels.py` を使う（いずれも `.claude/skills/ozaken-shiryo/` 配下）。旧版の `/tmp/body_*.html` を `publish.py` に渡す手順は使わない。現行の完全なHTMLから指定した章だけを置換し、共通本文デザインを再適用する。

- AI-SECIは同日後半に提供された本人の4象限図を最新の基準とする。共同化＝暗黙知の自己認識・他者との共有、表出化＝プロンプトやワークフローへの変換、結合化＝ワークフロー・チャットボット・RAG・MCP等の連携、内面化＝実業務で使うことで人の暗黙知が更新され、新たな文句・改善点も生まれる。4工程を独立した章で説明し、次の共同化へ戻す。
- 概観は左上S → 右上E → 右下C → 左下Iの時計回り。知の変換は暗黙知→暗黙知／暗黙知→形式知／形式知→形式知／形式知→暗黙知。小画面のDOM順はS・E・C・Iを維持する。表出化ではコンテキストエンジニアリングとシステムプロンプトの重要性を明示する。
- 小澤健祐による実務への応用と原典の参照を区別する。最新図に合わせ、見える名称は「結合化」とする。過去の「共同化＝言語化」「連結化」という説明へ戻さない。概念台帳の「連結化」は検索用の別名としてのみ残す。
- 5レベル：レベル2は設計・指示例・テストの3章。レベル3は処理の流れ・データ・画面設定・条件・テストの5章。製品差は同じ生成元で管理する。特にWorkspace Studioの `Check if` は条件未達なら後続を止めるため、Power Automateの真／偽分岐と同じ説明にしない。
- 共通パーツは `sources/practical_guides.py` と `practical_guides.css`。図・指示・表は常時表示し、共通背景・接続線の装飾だけが動く。表の列ホバーは値を変えない。

```sh
python3 .claude/skills/ozaken-shiryo/sources/gen_seci.py \
  --preview-dir /absolute/private-preview/seci-levels
python3 .claude/skills/ozaken-shiryo/sources/gen_five_levels.py \
  --preview-dir /absolute/private-preview/seci-levels
```

パスワードは非表示入力。確認後は各コマンドへ `--update` を加える。復号した控えを使う場合は `--input-dir /absolute/private-preview/before` を指定でき、更新時は現行資料と控えの一致を検査する。既存のラップ鍵 `W`、関連リンク、スクリプト、注入済みの共通スタイルを維持する。5レベルの初回改訂では対象外9章を保持し、最新の参照図への改訂ではAI-SECIの接続章以外の17章を各版とも保持した。AI-SECIの表紙は導入文だけを実務モデルに合わせ、共通の構図を保持する。

この本文改訂に「内容を一切変えない見た目の移行」の一致検査を適用しない。指定された章の内容変更は本人の依頼に含まれる。対象外の章と他資料の内容は変更しない。概念台帳の `crossref_data.py` は更新するが、全資料への `crossref.py apply` をついでに実行しない。

確認範囲と評価は [初回の改訂記録](verification/2026-09-11-seci-levels.md) と [参照図・SIPOCの改訂記録](verification/2026-09-11-seci-reference-sipoc.md) を参照。

### 業務分解大全のSIPOCを改訂する

`sources/gen_sipoc.py` を使う。対象は `04_practice/gyomu-bunkai.html`。現行のMethods章の直後に、週次定例会議資料のSIPOC記入例・書く順番・判断基準・工程別判定の4章を追加する。再実行時は自身の `data-practical-guide="sipoc--…"` の連続する章だけを置換し、重複追加しない。元の請求書処理の記入例・図・関連リンクは維持する。Worksheet 1の導入にあった「上から下」の説明だけは、新しい書く順番と矛盾しないよう更新する。

- プロセスは5つ前後。書く順番は「業務名 → P → O・C → S・I」。表の表示順S・I・P・O・Cとは区別する。
- 判断基準は本人指定の3つだけ：繰り返すか／入出力が決まっているか／最後に人が確認できるか。
- ◎＝3つともYESでエージェントに任せる、○＝一部YESでAIに手伝わせる、×＝人がやる。週次会議資料の例は①抽出・②集計・④資料化が◎、③コメント収集が○、⑤マネージャー確認が×。独自の追加条件や推測したYES・NOを例の各工程に足さない。
- 全情報を常時表示するHTMLの表・図で作る。列ホバーは装飾のみ。背景と接続線は共通の動作・印刷規約に従う。

```sh
python3 .claude/skills/ozaken-shiryo/sources/gen_sipoc.py \
  --preview-dir /absolute/private-preview/sipoc
```

確認後は `--update` を追加する。`--input-dir`、既存鍵保持、控えとの一致検査は上の2ビルダーと共通。レポートは `gyomu-bunkai-report.json`。旧フラグメントから資料全体を再生成しない。

### 共通の作成手順

1. [資料作成スキル](../.claude/skills/ozaken-shiryo/SKILL.md) と [講演デザイン規約](lecture-design.md) を読む。用途・対象読者・配布物の有無を、依頼と会話から確定する。ワークシートの有無が未決定で構成に影響する場合にだけ確認する。
2. 提供資料と一次情報を読む。日付、数字、引用、出典を控える。推測・仮想例・試算と実績を区別する。料金・製品・制度など変化する情報は確認日を付ける。
3. `find.py` と `crossref_data.py` で既存資料・概念の正典を確認する。同じ数字の更新が他の資料にも必要なら、その影響を記録し、依頼範囲を踏まえて揃える。
4. 分類フォルダと英語の `lowercase-hyphen.html` を決める。通常の分類は `NN_english/`、裏資料は `AX_Table/`・`Training/`・`Udemy/`。研修資料をAX Tableへ混ぜない。
5. `sources/gen_template.py` の骨格・作図関数と、`delegation_pilot/` の常時表示実装を参考に、専用の生成元を作る。コピーした場合はタイトル、本文、出力先、リンク、関数名を変更する。旧式の開閉・タブ・再生をそのまま引き継がない。
6. 一面一主張で、章を飛ばしても読める構成にする。現行便覧の [余白と情報密度](lecture-design.md#余白の基準) を引き継ぎ、内容を詰め込まない。現在の共通検査が求める本文奇数本・明暗交互・最後のnavy等の条件はスキルを参照する。
7. 本文フラグメントの先頭に `<!--META title=... | desc=...-->` を置き、生成する。組版は `publish.compose()` を使い、必要な講演用CSS・背景・常時表示の処理を専用ビルダーで再現可能にする。生成済みHTMLへの手修正だけで終わらせない。
8. ローカルで実表示と印刷を確認し、[評価スキル](../.claude/skills/ozaken-hyoka/SKILL.md) で伝わりやすさを見直す。
9. 対象のビルダーで暗号化する。新規資料では台帳・一覧・関連リンク・共有カードまで揃える。暗号化後の本文にも専用デザインが残ることを確認する。

汎用の新規生成コマンドは以下です。`OZAKEN_PW` を安全な入力方法で渡したプロセス内で実行します。

```sh
python3 .claude/skills/ozaken-shiryo/scripts/publish.py \
  /absolute/private-preview/body-example.html 01_concept/example.html \
  --list "資料タイトル ─ 副題"
```

`--list` は一覧への掲載、`--backstage` は裏資料置き場への掲載です。新規生成は対象HTMLだけでなく、暗号化された台帳・一覧・OGPの設定も変更します。`--backstage` の個別パスワードは資料の主題に合う一語を使う詳細運用があるため、スキルを確認してください。生成コマンドは個別パスワードを出力することがあります。公開ログや引き継ぎ文書へ転載しません。

## 既存資料を直す

現在の暗号化HTMLと生成元を把握し、必要なら修正前の暗号化ファイルを保存します。本文の復号結果は非公開の確認ディレクトリへ出します。

- 既存資料には `--update` を使い、鍵を新規作成しない。
- `lockbox.encrypt()` は既存のcontent keyとラップ鍵 `W` を保持し、本文の暗号文とIVを更新する。暗号文の差分の大きさから本文の変更量を判断しない。
- QR、関連資料チップ、個別の追記が生成元に含まれているか確認する。汎用 `publish.py --update` は台帳からQRを再挿入するが、任意の個別追記や既存チップを全て自動保存する仕組みではない。
- 題名・概要の変更時は外側のOGPと共有カードも更新する。本文だけ変えて台帳や一覧とタイトルがずれないようにする。
- 全体への `reapply.py`、`crossref.py apply`、正規化スクリプトは一括変更を伴う。1本のデザイン修正に無条件で実行しない。一括変更では事前・事後に `check_blocks.py` で注入ブロックの消失を検査する。

### 本文の内容を変えずにデザインを統一する

2026-09-11の本人指定では、全資料の本文をテンプレートの見た目へ揃える一方、内容の改変を禁止している。この用途で古い `gen_*.py` から本文を作り直さない。後から追加された章・関連資料・QR・講演先固有の情報を落とす可能性がある。

`apply_body.py` は現在の復号HTMLを保持し、所有範囲が明確な属性・CSS・装飾用JSだけを追加する。表紙の文言・句読点も変更しない。旧背景キャンバスには除去可能な停止条件を挿入し、長い章の全高を使う巨大な描画領域を作らない。通常資料、読み物、統計ボード、一覧ポスターを区別し、承認済みの `use-to-delegate.html` は専用レイアウトを維持する。

```sh
# プレビューのみ。パスワードは非表示の対話入力
python3 .claude/skills/ozaken-shiryo/scripts/apply_body.py \
  --preview-dir /absolute/private-preview/lecture-body

# 確認後に暗号化HTMLを更新。本番配信は別途gitで行う
python3 .claude/skills/ozaken-shiryo/scripts/apply_body.py \
  --preview-dir /absolute/private-preview/lecture-body --update
```

特定の資料だけを修正する場合は `--only 01_concept/ax-article.html` のようにリポジトリ相対パスを指定する。複数パスも指定でき、対象外や未知のパスは更新しない。共通CSSの変更でも影響する資料だけを再適用できる。2026-09-11のAX記事の強調文では、読み物用の `20ch` 幅と画面全高の設定が重なって文字が左上へ偏ったため、文章の幅を広げ、説明段落を伴わない強調ページだけ縦中央へ配置した。本文や改行タグを書き換えて補正しない。確認記録は [AX記事の配置修正](verification/2026-09-11-ax-statement-layout.md)。

リポジトリ外の復号した控えがある場合は `--input-dir /absolute/private-preview/before` を加えられる。`--update` と同時に使うと、現在の暗号化資料と控えが一致しない限り停止する。他のAIが途中で追記した内容を上書きしないための検査であり、停止時は最新内容を取り込み、再検証する。

**プレビューの親フォルダがリポジトリへのシンボリックリンクでないかも確認する。** ファイル自体の `is_symlink()` だけでは不十分。保存先の `resolve()` がリポジトリ内を指す場合は書き込まない。既存のプレビューURLを更新する際にも `apply_cover.safe_preview()` を通す。ステージング後は各配信HTMLを `git show :相対パス` で読み、`<!--OZAKEN-LOCKED2-->` から始まり、平文の本文用属性・スタイルが含まれないことを検査する。暗号化直後の確認だけでなく、コミット対象そのものを確かめる。

```sh
python3 .claude/skills/ozaken-shiryo/scripts/check_encrypted.py --staged
```

全件を変換・検証してから暗号化する。追加した指定を `apply_body.strip()` で除くと、元の文書にバイト単位で完全一致することを検査する。これは本文・図のラベル・数値・SVGの座標・属性・出典・リンク・既存スクリプトの保全を含む。さらに冪等性、暗号化後の復号一致、ラップ鍵 `W`、`check_blocks` の前後差を確認する。検査結果 `body-report.json` は非公開プレビューに置き、本文そのものをGitへ入れない。

新規資料の `publish.compose()` は共通表紙に続けて `apply_body.patch(page)` を適用する。独自ビルダーで追記する場合も、クラスと専用CSSを決めた後・暗号化の前に同じ処理を行う。テンプレート便覧は自身が基準なので適用対象外。共通CSSを編集しただけでは既存の暗号化資料へ反映されない。

確認は通常幅と390px幅で、全文の表示、図の位置、横はみ出し、図内のスクロール、背景の時間変化・画面外停止を行う。印刷は長い章を切り捨てず複数ページに流し、PDFを納品する場合は実際の書き出しも確認する。

汎用資料の更新例：

```sh
python3 .claude/skills/ozaken-shiryo/scripts/publish.py \
  /absolute/private-preview/body-example.html 01_concept/example.html --update
```

### テンプレート便覧

```sh
# 復号されたローカル確認版だけを生成。パスは環境に合わせる。
python3 .claude/skills/ozaken-shiryo/sources/build_template_gallery.py \
  --preview /absolute/private-preview/template.html

# 確認版と、リポジトリ内の暗号化template.htmlを更新。
python3 .claude/skills/ozaken-shiryo/sources/build_template_gallery.py \
  --preview /absolute/private-preview/template.html --publish
```

`--publish` は既存鍵を維持した**ローカルの書き戻し**です。Gitへのpushや本番デプロイはしません。マスター未設定時は非表示入力を求めます。既存の `#figure=dims` と通常の `#figure-dims` のリンクを維持します。

### 「使うAI」から「任せるAI」へ

```sh
# 既存QRと関連リンクを含む確認版。既存の暗号化HTMLは変えない。
python3 .claude/skills/ozaken-shiryo/sources/delegation_pilot/build.py \
  --output /absolute/private-preview/01_concept/use-to-delegate.html --preserve

# 確認版と対象の暗号化HTMLを更新。
python3 .claude/skills/ozaken-shiryo/sources/delegation_pilot/build.py \
  --output /absolute/private-preview/01_concept/use-to-delegate.html --update
```

`--preserve` なしのプレビューには既存QR・関連チップが付かないため、最終確認は `--preserve` または `--update` で生成します。マスターは非表示入力。`--baseline` は旧暗号化HTMLから追加要素を復元するときだけ使います。詳しくは [実装例README](../.claude/skills/ozaken-shiryo/sources/delegation_pilot/README.md)。

## 全資料の表紙を統一する

2026-09-11の本人指定。`01_concept`〜`12_jobs`と`AX_Table`・`Training`・`Udemy`・`weekly`の119資料が対象。トップ・裏資料一覧・管理画面・配布済みPDFはこのHTML移行の対象に含めません。テンプレート便覧は専用ビルダーで同じ装飾を読み込みます。

```sh
# 外部の非公開ディレクトリへ全資料の確認版を生成
python3 .claude/skills/ozaken-shiryo/scripts/apply_cover.py \
  --preview-dir /absolute/private-preview

# 同じ確認版に加え、既存HTMLを鍵を変えず再暗号化
python3 .claude/skills/ozaken-shiryo/scripts/apply_cover.py \
  --preview-dir /absolute/private-preview --update

# 内容を必要としない移行ロジックの検査
python3 -m unittest discover \
  -s .claude/skills/ozaken-shiryo/scripts -p test_apply_cover.py
```

マスター未設定時は非表示入力。処理は全件を解析・検証してから暗号化HTMLを書き戻します。表紙以外の章が一致すること、既存リンクとスクリプトが保持されること、二重適用で変わらないことを検査し、更新時は `check_blocks.survey()` で注入ブロックの前後比較、`W` の一致、復号結果とプレビューの一致も検査します。未知の表紙やシンボリックリンクを経由した平文上書きはエラーになります。削除した旧表紙の写真・装飾だけでなく意味のある未分類情報が残った場合も、勝手に捨てず専用の対応処理を追加してください。

新規資料・通常の改訂・週次資料は `publish.compose()` の最後で自動適用されます。講演版はさらに専用CSS適用後にも適用します。これらを通さない独自生成元では `apply_cover.patch(page)` を最後に通してください。古い `apply_herofx` は共通表紙の印を認識し、旧HUDやcanvasを起動しません。旧CSSの注入ブロックは移行時に保持します。

プレビュー用の `cover-report.json` は対象パスと更新有無だけを持ち、Gitに追加する必要はありません。本文・QR・確認用画像は非公開の確認ディレクトリに保持します。`--update` は本番デプロイではありません。

## 鍵・個人情報の扱い

このリポジトリは公開されています。マスター、共通・個別パスワード、APIトークン、名簿CSV、取り込みSQL、復号ページをコミットしません。暗号化HTMLを平文で上書きした状態で公開しないでください。

通常の資料はマスター・共通・個別の鍵で開きます。管理用ページの鍵は別運用で、共通鍵を勝手に追加しません。現在の鍵構成を `check_pw.py` と実装で確認します。

旧スクリプトの `OZAKEN_PW=マスター` という表記は実値をソースに書く指示ではありません。セッションの安全なシークレット入力を使うか、TTYで `getpass` から子プロセスへ渡します。例えば、ルートから次のように実行できます。

```python
import getpass
import os
import subprocess

env = os.environ.copy()
env["OZAKEN_PW"] = getpass.getpass("Master password: ")
subprocess.run([
    "python3", ".claude/skills/ozaken-shiryo/scripts/find.py", "調べたい概念"
], env=env, check=True)
```

入力値を表示・記録しないでください。既存スクリプトのCLIを使う際は環境変数名を確認します（多くは `OZAKEN_PW`、`lockbox.py` のCLIは `OZ_PW`）。`OZAKEN_ROOT` が設定されている場合は、現在のworktreeを指していることも確認します。

## ローカルで見る

Python 3を使います。暗号処理には `cryptography` が必要です。PDFや画像・ブラウザの検証は利用環境の既存ランタイムを優先し、OS固有の絶対パスを手順に固定しません。

プレビューはリポジトリ外の専用ディレクトリに生成します。トップへの移動や画像を確認する場合は、プレビューから参照する `index.html` と必要な `99_assets/` 等も同じ配置で参照できるようにしてください。復号ページを新しい公開URLへアップロードして確認しません。

```sh
python3 -m http.server 8878 --bind 127.0.0.1 \
  --directory /absolute/private-preview
```

`http://127.0.0.1:8878/template.html` または対象の資料パスを開きます。確認用サーバーはユーザーが見る間、実行中に保ちます。リンクを渡す前にHTTP応答と実表示を確認します。

資料が見えない場合は、サーバーが動いているか、ポート・公開ディレクトリ・URLが一致しているか、必要なファイルがあるか、暗号化ページなら鍵の入力が必要かを順に調べます。`127.0.0.1` のURLはその端末専用で、本番反映ではありません。

プレビューの出力先がシンボリックリンクなら、その実体を確認してから書きます。暗号化された本番用HTMLへのリンクを経由して平文を書き込まないでください。

## 隠しコマンドとプロフィール

トップの `index.html` がオーバーレイの実体とハッシュの受け口を持ちます。資料側の `apply_keynav.py` はトップへ移動するだけです。各資料にプロフィールや開始演出を複製しません。

| キー | 意味・行き先 |
|---|---|
| `pr` | 投影プロフィール（`#profile`） |
| `st` | 開始前の待機画面（`#standby`）。会話中に「開始エフェクト」と呼ばれる入口 |
| `go` | 開演の起動演出（`#boot`） |
| `en` | 終演演出からお礼画面（`#end`） |
| `th` / `ti` | お礼 / タイトル画面 |
| `qa` / `ma` | 質問箱 / 星座マップ |
| `ur` / `pw` / `mx` | 裏資料 / 台帳 / 資料マトリクスのゲート |
| `cs` / `in` | 道具の部屋 / 受信箱のゲート |
| `ck` | 会場チェック `stage.html` |
| `te` | トップからテンプレート便覧。**資料側keynavには追加しない** |
| `nl` | トップからメルマガ管理 |
| `qr` / `test` | 対応する資料内のQR / 確認テスト。共有keynavで横取りしない |

大文字入力にも対応する設計を保ちます。入力欄・編集中の要素・修飾キーの入力から誤発火させず、Escapeで閉じられることを確認します。`te` を資料側に追加すると `test` の途中で遷移してしまうため、追加禁止です。

スマートフォン用の長押し入口、`data-ozk` の順番タップ、既存ゲートも保持します。隠し操作は発見方法であってアクセス制御ではありません。

プロフィールの内容・本人確認済み数値は [デザイン規約](lecture-design.md#pr開始終了の扱い)、写真は [画像の運用](../99_assets/profile-media.md) を参照。トップのCSSは `#materials-home` に限定し、PR / ST / GO / ENの画面へ汎用セレクターで波及させないようにします。

### 公開トップのプロフィールと背景

2026-09-11の本人指定。トップ下部は、人物紹介（`#author`）、活動実績（`#author-record`）、AICXの3領域と認定資格（`#aicx`）の順で構成します。HTMLは `index.html`、専用の組版は `99_assets/author-profile.css`。既存のPR用HTML・CSSへこの構成を複製しません。

トップ全体の背景は `materials-home.js` が `#materials-home` 直下の全sectionとfooterへ `.mh-air` を挿入します。長い資料一覧も720px以下の `.mh-air-tile` に分け、各タイルの表示状態を監視します。`ResizeObserver` が改行・画像読み込み・内容量の変化に合わせて枚数と末尾の高さを更新します。要素は装飾専用で、JavaScriptが使えなくても本文は全て残ります。

- 1タイルは粒8個と光の筋2本。幅700px以下、または高さ320px未満の短い帯は半数に減らす。
- `IntersectionObserver` で画面内のタイルだけ `.is-active` にする。タブ非表示、動きを減らす設定、PR・ST等の `.thanks.show` とGO・ENの `.boot.is-on` 表示中は停止する。
- 色・透明度・周期は `materials-home.css` の `--air-*` と `mh-air-*`。白い面では青、紺の面では淡い光を使う。各面の背景の内側に置き、文字は動かさない。
- アーカイブの末尾、小画面で長くなったプロフィール、PRを閉じたあとの再開も確認する。ページ最上部のスクリーンショットだけで全体への適用を判断しない。
- `prefers-reduced-motion` では静止、印刷では `.mh-air` を非表示にする。既存の表紙・プロフィールの背景もそれぞれの停止規則を維持する。

更新後はアセットの内容ハッシュを再生成する。プロフィールの肩書き・実績・書籍名・発行予定日は既存の掲載値を基準とし、見た目の変更に合わせて数字を増やしたり集計日を推測したりしない。

初回のローカル検証（2026-09-11）：実測1422×800と390×844で人物紹介・3領域を確認し、横はみ出しなし。トップの全11面に背景があり、アーカイブ下部の光点の時間変化と画面外停止を確認。PR・ST・ENの起動と背景停止、全リンク先・既存インラインスクリプト・講演用オーバーレイの保持を確認した。印刷用・動きを減らすCSSを非公開の確認ページで適用し、文字の保持と装飾の停止を確認。実際のPDF出力・OS設定の変更・本番配信はこの検証に含まない。

## 検証と完了条件

- 生成元と生成HTMLが一致している。再生成しても手修正を失わない。
- 検査を通し、警告の意味を確認する。専用ビルダーと汎用ビルダーは検査範囲が異なるので、用途に合う入口を使う。
- 実表示で、対象の図・表・本文・リンク・背景を確認する。表示幅は実測値を記録し、CSSで隠れたままの文字や画面外のはみ出しを見落とさない。
- [デザイン規約の確認項目](lecture-design.md#完了前の確認) に沿って、投影、小画面、印刷、動きを減らす設定を検証する。
- 更新前後でラップ鍵 `W` が同じで、復号結果が生成プレビューと一致する。QRと関連リンクの保持を確認する。
- `git diff --check` と対象ファイルの差分を確認する。平文・鍵・名簿・確認用画像を不用意に含めない。

共通アセットを変更したときは次を実行し、参照URLの内容ハッシュを更新します。

```sh
python3 scripts/version-site-assets.py
python3 scripts/version-site-assets.py --check
```

便覧・講演版のインラインCSSだけを変えた場合、この操作だけでは生成HTMLは更新されません。各ビルダーで対象を再生成してください。

## Gitへの記録と本番反映

このサイトはCloudflare Pagesの `ozaken-materials` プロジェクトで、`main` の静的HTMLを配信する構成です。公開先は `https://content.ozaken.ai/`。`publish.py` の「公開」という出力、便覧の `--publish` は、ネットワークへの公開完了を意味しません。

1. 作業ブランチで生成元と必要な生成物を揃え、検証する。
2. 対象ファイルを明示してstageする。無関係なファイルも入る `git add .` を定型手順にしない。
3. コミットし、作業範囲に沿ってPR・統合を行う。ユーザーの本番反映指示が既にあるなら同じ許可を再度求めない。ローカル確認の依頼なら、その段階で止める。
4. `main` への統合・pushで本番配信が始まる。実際の配信状態を確認し、公開URLを開いて対象ページ・アセット・復号・隠しコマンドを確認する。
5. 「ローカル更新」「コミット済み」「本番反映済み」のどこまで終えたかを報告する。ビルド成功だけで本番反映済みとしない。

`.claude/` の生成元は通常の配信対象から外れる構成ですが、公開Gitリポジトリからは読めます。機密情報を置ける場所ではありません。

URL移転は `scripts/oz_site.py` と `retarget.py` を使う専用作業です。QRはSVGへ焼き込まれているため文字置換だけでは移転できません。パスを改名・移動した場合は `404.html` の旧URL対応も更新します。

## 不具合から戻す

まず範囲を確認し、別の作業を巻き込むリセットを避けます。再生成で古いデザインに戻った場合は、正しいビルダーと専用CSSの組み込みを確認します。鍵が開かない場合は、誤って新規作成したか、`W` が変わっていないかを確認します。

未公開なら対象の生成元を直して再生成します。公開済みなら原因を直すか、影響するコミットだけをrevertする変更を作り、検証して同じ配信手順で戻します。暗号化HTMLだけを戻して生成元と不一致にしないようにしてください。

## 週次・メルマガ・その他の運用

| 作業 | 読む手順 | 注意する境界 |
|---|---|---|
| 週次ニュース収集 | [スイープ手順](weekly-sweep-runbook.md) | 対象週・出来事の日付・一次情報を照合する |
| 週次資料の生成と更新 | [週次システム](weekly-system.md) | `weekly_publish.py`、定点JSON、鍵、最新号の掲載規則 |
| メルマガ原稿・名簿・配信 | [メルマガ運用](newsletter-system.md) | テスト送信も実際のメール。送信依頼を受けた範囲だけ実行する |
| 配信機能の修正 | [メルマガ検査](newsletter-system.md#7-直したら通すもの) | `node newsletter/selftest.mjs` は送信しない検査。D1のremote操作は本番データを変更する |
| プロフィール素材差し替え | [profile-media.md](../99_assets/profile-media.md) | 画像原本、alt、切り抜き位置、遅延読込、参照ハッシュ |
| 会場チェック・投影操作 | [stage.md](../.claude/skills/ozaken-shiryo/references/stage.md) | 本文の常時表示の指定を優先する |

メルマガ配信を資料公開のついでに行いません。配信停止者を勝手に再登録せず、名簿・投入SQLはGitに入れません。Cloudflare設定の詳細は既存手順を参照し、ルートに新しい `wrangler.toml` を置いて既存配信設定を上書きしないでください。

## 次の担当者に残すこと

変更対象、正しい生成コマンド、確認した画面幅・動作・印刷範囲、未確認点、コミット、公開の有無を記録します。ローカルの絶対パスや一時ポートを恒久的な本番設定として扱わないでください。

仕様を変えたら、生成元のREADME、[講演デザイン規約](lecture-design.md)、この手順の関係する箇所を同時に更新します。古い入口を残す場合は、現在使う入口と用途の違いを明示してください。
