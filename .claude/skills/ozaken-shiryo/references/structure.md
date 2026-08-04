# 本文フラグメントの書き方

## 全体の形

Pythonで組み立てて、HTMLフラグメントを吐く。手書きしない。
既存の生成スクリプトを雛形にすると早い（`gen_credits.py` が最新かつ素直な例）。

```python
import os, sys
sys.path.insert(0, '/home/user/ozaken-materials/99_assets/tools')
from domain_fig import fig_cols, fig_bars, fig_sheet, fig_ladder, fig_gap, fig_quad

BODY = []
A = BODY.append

A('<!--META title=タイトル ─ 副題 | desc=検索結果に出る一文。-->')
A(hero('Eyebrow ─ 分類', 'タイトル<br>2行目', 'リード文。3〜5行。'))
A(sec('sec-light', 'Section 01', '見出し', 'サブ', lede='…', fig=…, body=cards([...])))
...
A(close('締めの見出し', '締めの文章。'))

open('/tmp/body_foo.html', 'w', encoding='utf-8').write('\n'.join(BODY))
```

`hero()` `sec()` `close()` `cards()` は各生成スクリプトが持っている小さな関数。
新しく作るときは `gen_credits.py` からコピーして使う。

## セクションの部品

```python
sec(tone, eyebrow, title, sub=None, lede=None, fig=None, body=None)
```

| 部品 | 役割 | 長さの目安 |
|---|---|---|
| `eyebrow` | 「Section 01」など小さなラベル | 短く |
| `title` | セクションの主張。**述語で言い切る** | 25文字前後 |
| `sub` | 見出しを1段かみ砕く | 40文字前後 |
| `lede` | 明朝体の大きめ導入文。要点を語る | 2〜4行。全セクションには置かない |
| `fig` | 図版。**毎セクション必ず1つ以上** | — |
| `body` | カード3枚 | 各2〜4行 |

`fig` には複数の図版を `+` で連結して渡せる。
情報量が多いセクションでは、棒グラフ＋表のように2枚重ねると理解が早い。

## カードの書き方

```python
cards([
    ('<span class="mth">短いラベル</span>見出しになる一文',
     '本文。2〜4行。数字と固有名詞を入れる。'),
    ...
])
```

`mth` ラベルは、聴講者が話の位置を見失わないための目印。
「前提条件」「落とし穴」「判断軸」「試算」のように、**そのカードの役割**を書く。
内容の要約ではない。

カードの本文には `<b>` が使える（SVGの中では使えない）。
効かせどころは1セクションに1箇所まで。

## 構成の型

### 解説型（製品・技術・制度の理解）
1. なぜ今それが問題か（`fig_gap` で対比）
2. 全体像・分類（`fig_cols`）
3. 中核の数値（`fig_sheet` / `fig_bars`）
4. 仕組みの分解（`fig_cols` / `fig_context`）
5. 実例・シナリオ（`fig_bars` + `fig_sheet`）
6. 見積り・手順（`fig_ladder`）
7. 境界線・誤解（`fig_quad`）
8. 周辺領域（`fig_cols`）
9. 落とし穴と行動（`fig_ladder`）
→ 締め

### 実践型（業務での使い方）
1. 現場で起きていること
2. そもそも何か（定義の整理）
3. 3つの型（`fig_cols`）
4. 型ごとの詳細 ×3
5. 使い分けの判断（`fig_quad`）
6. 導入の順序（`fig_stairs`）
7. つまずきどころ
→ 締め

### 講演セッション型（AX Table のような1コマ用）
本文は5〜7本と短くする。1セッション30分なら、
図版7点・カード15枚が上限。それ以上は喋りきれない。

## 締めのセクション

`close(title, copy)` は navy 一色。図版は置かない。
**事実の要約をしない。** 資料全体を1段上から言い直す。

良い例（Copilot Credits の資料より）:

> この変化の本質は、値上げでも値下げでもない。
> **AIの使い方が、はじめて金額として見えるようになった**ということだ。
> 重い仕事を1本回せば$7、軽い要約なら$1。
> この感覚が現場に共有されると、「とりあえず全部AIに」という発想は自然に消え、
> 「ここは人がやったほうが速い」「この仕事は$7払う価値がある」という判断が生まれる。

事実（$7と$1）を、判断の話に翻訳している。ここが資料の価値になる。

## 出典の扱い

外部資料を元にしたときは、**図版のキャプションに出典を書く**。

```
'出典: Microsoft Copilot Credits Guide（2026年8月）。金額は $0.01/クレジットで換算'
```

原典の数値と、自分で計算した値を必ず区別する。
「〜と明記されている」「〜は参考値」といった書き分けを本文でも行う。
壇上で「ここは私の試算です」と言えることが、資料の信用を支える。

## 既存資料を直すとき

本文だけ差し替えれば、外側のロック画面と鍵はそのまま使える。

```python
import lockbox
inner = lockbox.decrypt(path, MASTER)
# inner を編集
lockbox.encrypt(path, MASTER, inner)      # 鍵はすべて維持される
assert lockbox.decrypt(path, MASTER) == inner
```

`lockbox.create()` は鍵を作り直すので、**パスワードを変える意図がないときは使わない**。
図版だけ作り直す場合も、生成スクリプトから組み直して `encrypt` で戻すのが安全。
