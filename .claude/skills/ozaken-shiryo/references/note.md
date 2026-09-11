# 資料を切り出して、note に載せる

資料は鍵つきで、note は公開。だから「資料をそのまま載せる」のではなく、
**面を選んで切り出し、記事の形に組み直して、下書きとして置く**。

資料は111本、1本あたり10面前後。候補は1,000面を超えている。
**足りないのは供給ではなく「どれを出すか」**なので、選ぶところに道具を置いている。

## 流れ

```bash
cd .claude/skills/ozaken-shiryo/scripts

# 0) まだ出していない面を、出しやすい順に見る
OZAKEN_PW=マスター python3 note_pick.py --top 20 --why

# 1) 切り出す（面の番号は 1 始まり。deck_stats.py でも番号を確かめられる）
OZAKEN_PW=マスター python3 note_export.py 01_concept/what-is-agi.html --sections 2,7,8
# → note_drafts/what-is-agi/ に article.md / article.txt / figs/*.png / meta.json
#   同時に、台帳に「下書き」として1行つく

# 2) 読んで直す。meta.json の "check" と、画面に出る「要確認」を必ず見る
#    「次の面で」「姉妹資料」のように、資料の中だけで通じる言い回しがそのまま出ている

# 3) note に入れる。手で貼るのが基本。article.md を貼り、figs/ の画像を印の位置に
#    自動で下書きにするなら（未検証）:
NOTE_STATE=~/note-state.json node note_post.mjs ../../../../note_drafts/what-is-agi

# 4) 公開ボタンは人が押す。押したら、台帳に URL を入れる
python3 note_ledger.py posted what-is-agi --sections 2,7,8 --url https://note.com/…
```

## 決めていること

- **全部は出さない。** `--sections` で面を選ぶ。既定は最初の3面だけ。全部出すなら `--all` と明示する。
  鍵つき資料の中身が丸ごと外に出る形は、切り出しではなく複製
- **末尾は、3つのURLを並べるだけ。** ポートフォリオ（ozaken.ai）、AI資料アーカイブ
  （content.ozaken.ai）、X（@ozaken_AI）の順。**資料そのもののURLは書かない**。
  「この記事は資料から切り出したものです」のような断り書きも置かない
- **文は変えない。** 変えるのは形だけ。面の題→見出し、カードの見出し→小見出し、
  図版→画像、おざけんのワンポイント→引用、締め→最後の見出し
- **図版の出典行（「この整理は小澤健祐によるもの」）は外す。** 二次情報の確認日は残す
- **note_drafts/ はリポジトリに入れない。** 平文の中身と画像がそのまま置かれる。.gitignore 済み
- **自動投稿は「下書き保存」で止まる。** 公開ボタンには触らない。
  note に公式の投稿APIは無く、エディタの作りは予告なく変わるので、止まったら手で貼る
- **ログイン状態のファイル（NOTE_STATE）は鍵と同じ。** 手元のPCで `--login` で作り、共有もコミットもしない
- **裏資料（AX_Table / Training / Udemy / weekly）は候補に入れない。**
  相手先や受講者に向けたもの。`note_pick.py --backstage` で見えるが、出す前に一度考える

## 台帳（note_ledger.json）

置き場所は `.claude/skills/ozaken-shiryo/note_ledger.json`。
リポジトリ直下はそのまま content.ozaken.ai の公開ルートなので、道具の状態はサイトの中身と混ぜない。

**この台帳は公開リポジトリに入る。だから面の題も記事の本文も持たない。**
資料の題は index.html にすでに平文で載っているので持ってよい。
面の中身は暗号の内側なので、持つのは**本文の SHA-256 の先頭8桁**だけ。

指紋で持つ理由は2つある。

1. **面の番号は当てにならない。** 資料を直して面を1つ挿入すれば、「前に出した面2」と
   「いまの面2」は別物になる。中身で見れば取り違えない
2. **出した当時と変わった面を拾える。** 同じ番号なのに指紋が違う面には、
   `note_pick.py` が `改` の印をつける

1行の形:

```json
{
  "slug": "what-is-agi",
  "source": "01_concept/what-is-agi.html",
  "deck_title": "AGIとは何か ─ 「来る日」ではなく、定義のほうが動く",
  "sections": [2, 7, 8],
  "section_ids": ["a1b2c3d4", "5e6f7a8b", "9c0d1e2f"],
  "status": "draft",
  "recorded_at": "2026-09-11",
  "posted_at": null,
  "note_url": null,
  "hashtags": ["AI", "生成AI", "AGI"],
  "reactions": {"checked_at": null, "likes": null, "comments": null},
  "memo": ""
}
```

`status` は `draft` と `posted` の2つ。切り出した時点では `draft` で、
**公開ボタンを押すのは人**なので、台帳が勝手に `posted` に変わることはない。

```bash
python3 note_ledger.py list [--status draft] [--deck what-is-agi]
python3 note_ledger.py posted <slug> --url https://note.com/… [--at 2026-09-11]
python3 note_ledger.py reactions <slug> --likes 120 --comments 3
python3 note_ledger.py memo <slug> "続きを別の記事で"
python3 note_ledger.py drop <slug> [--sections 2,7,8]
```

同じ資料から2本以上出していると slug だけでは絞れない。そのときは `--sections` で選ぶ
（候補を見せて止まる）。

## 何を出すかを選ぶ（note_pick.py）

台帳を読み、**まだ出していない面**を3つの軸で並べる。点は目安で、順位は結論ではない。
決めるのは人のままにして、機械は並べるところまでをやる。

| 軸 | 数え方 |
|---|---|
| 図版がある | 2枚以上 +24 / 1枚 +18 / 無し 0。note は画像が1枚あるだけで読まれ方が変わる |
| 単独で読んで完結する | 立ち上がりが自前（lede か sub）+10 / カード2枚以上 +10 / 締めの一言 +8 / 地の文が700〜1800字 +14（450〜2600字 +7）/ 指示語で始まっていない +10 |
| 資料の中だけで通じる言い回しが少ない | 「次の面」「姉妹資料」「この資料」などの数×-12（3つで頭打ち） |

同じ資料から続けて出すと読む側には連載に見えて1本の強さが落ちるので、
すでに出した本数ぶんだけ軽く減点する（`--no-spread` で切れる）。

```bash
OZAKEN_PW=… python3 note_pick.py                      # 上位30面
OZAKEN_PW=… python3 note_pick.py --dir 01_concept --why  # 分類を絞り、点の内訳も見る
OZAKEN_PW=… python3 note_pick.py --deck what-is-agi --all  # 1本の中を、出したぶんも含めて見る
OZAKEN_PW=… python3 note_pick.py --json               # 別の道具に渡す
```

111本を毎回復号すると重いので、面ごとの数えた結果を `note_drafts/.pick_cache.json` に控える
（資料の更新時刻で作り直す。`--no-cache` で使わない）。
**控えには面の題が平文で入る**ので、note_drafts/ の外には出さない。.gitignore 済み。

## 記事にするときの直しどころ

切り出したままだと、次のところが記事として浮く。meta.json の `check` に拾ってあるので、
そこから直す。

- 「次の面」「前の面」「あとの面」 … 記事では「次の章」か、その場で言い切る
- 「姉妹資料〜」 … 記事では外すか、「別の記事で」に
- 「この資料では」 … 「この記事では」に
- 冒頭の1段落は資料のリード文そのまま。note では最初の2行で読むかが決まるので、
  切り出した面に合わせて書き直すことが多い
- ハッシュタグは meta.json の候補から。10個まで
