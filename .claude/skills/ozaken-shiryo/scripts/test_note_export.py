# -*- coding: utf-8 -*-
"""作り物の資料を1本でっち上げて、切り出しの全工程を通す。

鍵が要るのは復号だけなので、そこだけ差し替える。
並べ替え・カードの間引き・題の候補・見出し画像・台帳への記録は、これで本番と同じ道を通る。
"""
import io
import json
import os
import sys
import tempfile

S = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, S)
TMP = tempfile.mkdtemp()
os.environ['OZAKEN_NOTE_LEDGER'] = os.path.join(TMP, 'note_ledger.json')
os.environ['OZAKEN_PW'] = 'dummy'          # 復号を差し替えるので中身は使われない

import lockbox
import note_export
import note_ledger

DECK = '''<section class="hero">
<h1 class="hero-title">AGIとは何か<br>「来る日」ではなく、定義のほうが動く</h1>
<p class="hero-copy">この資料は、AGIという言葉の輪郭を、能力ではなく合意の側から見直します。</p>
</section>
<section class="sec-light" data-bg="1">
<span class="eyebrow">CONCEPT</span>
<h2 class="sec-title">言葉の来歴</h2>
<p class="sec-sub">どこから来た言葉か</p>
<p class="lede">だから、次の面で見るように、この資料ではまず来歴から入ります。</p>
<div class="cards">
<div class="card"><h3>1997年</h3><p>初出。</p></div>
<div class="card"><h3>2000年代</h3><p>定義が割れる。</p></div>
</div>
</section>
<section class="sec-navy" data-bg="2">
<span class="eyebrow">CONCEPT</span>
<h2 class="sec-title">定義は、能力ではなく合意で動く</h2>
<p class="lede">AGIが来る日を待つ議論は、いつまでも終わりません。線を引くのは能力ではなく、そのつど引き直される合意のほうだからです。</p>
<div class="figure"><p class="fig-title">Fig.3 ── 定義は、能力ではなく合意で動く</p>
<p class="figure-cap">出典：各社の技術報告（2026年3月確認）</p></div>
<div class="figure"><p class="fig-title">Fig.4 ── 引き直される線</p>
<p class="figure-cap">この整理は小澤健祐によるもの</p></div>
<div class="cards">
<div class="card"><h3>能力で引く線</h3><p>試験の点や作業の幅で引く線は、測るたびに動きます。去年の合格点が、今年は前提になっているからです。</p></div>
<div class="card"><h3>合意で引く線</h3><p>誰が、何をもってAGIと呼ぶかを決めているのか。線を引いているのは、技術ではなく人の側の合意です。</p></div>
<div class="card"><h3>短い</h3><p>ここは短い。</p></div>
</div>
<div class="take"><p class="take-text">AGIは、来る日ではない。引き直される線だ。</p></div>
</section>
<section class="sec-light" data-bg="3">
<span class="eyebrow">PRACTICE</span>
<h2 class="sec-title">仕事の側から見ると、何が変わるか</h2>
<p class="lede">定義が動くという前提に立つと、備え方も変わります。</p>
<div class="figure"><p class="fig-title">Fig.5 ── 備え方の三つ</p><p class="figure-cap">2026年4月確認</p></div>
<div class="bare"><p>待つのではなく、線が動く前提で仕組みを組む。それが実務の側の答えになります。</p></div>
</section>
<section class="sec-navy">
<h2 class="sec-title">おわりに</h2>
<p class="kicker">定義を追うのではなく、定義を引く側に回ること。</p>
</section>
<div class="oz-return">もどる</div>'''

lockbox.decrypt = lambda path, pw: DECK

ok = []


def check(name, cond, extra=''):
    ok.append(bool(cond))
    print('%s %s %s' % ('✓' if cond else '✗', name, extra if not cond else ''))


out = os.path.join(TMP, 'draft')
sys.argv = ['note_export.py', '01_concept/what-is-agi.html', '--sections', '1,2,3',
            '--no-figs', '--out', out]
note_export.main()
print('\n' + '=' * 70)

md = io.open(os.path.join(out, 'article.md'), encoding='utf-8').read()
meta = json.load(io.open(os.path.join(out, 'meta.json'), encoding='utf-8'))

# ── 並べ替え ──────────────────────────────────────────────
check('つかみの強い面（2）が先頭に出た', meta['sections'][0] == 2, str(meta['sections']))
check('残りは資料の順のまま', meta['sections'][1:] == [1, 3], str(meta['sections']))
check('台帳用の面は昇順で持っている', meta['sections_sorted'] == [1, 2, 3])
h = [l for l in md.split('\n') if l.startswith('## ')]
check('最初の見出しが面2', h and '合意で動く' in h[0], h[0] if h else '見出しなし')

# ── 冒頭 ──────────────────────────────────────────────────
check('冒頭は資料の表紙リードではなく、先頭の面の立ち上がり',
      md.startswith('AGIが来る日を待つ議論') and 'この資料は、AGIという言葉の輪郭' not in md)
check('冒頭の文が本文で重複していない', md.count('AGIが来る日を待つ議論') == 1)

# ── カードの間引き ────────────────────────────────────────
check('短いカードが落ちた', '### 短い' not in md and 'ここは短い' not in md)
check('中身のあるカードは残っている', '### 能力で引く線' in md and '### 合意で引く線' in md)
check('落としたカードが meta に残っている',
      any(d['head'] == '短い' for d in meta['dropped_cards']), str(meta['dropped_cards']))
check('面1の一行カードも落ちた（1997年など）',
      '### 1997年' not in md and len(meta['dropped_cards']) == 3, str(len(meta['dropped_cards'])))

# ── 図版と出典 ────────────────────────────────────────────
check('図版の題から Fig.N が外れている', '図：定義は、能力ではなく合意で動く' in md)
check('「小澤健祐による」の出典行は外れる', 'この整理は小澤健祐によるもの' not in md)
check('二次情報の確認日は残る', '2026年3月確認' in md)

# ── 題の候補 ──────────────────────────────────────────────
titles = meta['title_candidates']
check('題の候補が出ている', len(titles) >= 4, str(len(titles)))
top = titles[0]
check('1位が26字以内（note の一覧で切れない）', top['chars'] <= 26,
      '%d字 %s' % (top['chars'], top['text']))
check('資料の題そのまま（34字）は1位ではない', titles[0]['kind'] != 'deck')
deck_row = [t for t in titles if t['kind'] == 'deck']
check('資料の題は候補には入っているが、長さで沈んでいる',
      deck_row and deck_row[0]['score'] < top['score'],
      str(deck_row[:1]))
check('型が記録されている', all(t['kind'] in
      ('deck', 'deck-half', 'section', 'take', 'fig') for t in titles))

# ── つかみ（見出し画像用） ────────────────────────────────
ph = meta['phrase_candidates']
check('つかみの候補が20字以内', ph and all(p['chars'] <= 20 for p in ph), str(ph[:2]))
check('ワンポイントがつかみに拾われている',
      any('来る日ではない' in p['text'] for p in ph), str([p['text'] for p in ph]))

# ── 見出し画像 ────────────────────────────────────────────
cov = os.path.join(out, 'cover.png')
check('見出し画像ができた', meta['cover'] == 'cover.png' and os.path.exists(cov))
if os.path.exists(cov):
    check('見出し画像に中身がある（10KB超）', os.path.getsize(cov) > 10000,
          '%dB' % os.path.getsize(cov))

# ── 末尾の決めごと ────────────────────────────────────────
check('末尾は3つのURLだけ', md.rstrip().endswith('https://x.com/ozaken_AI'))
check('資料そのもののURLは書かない', 'what-is-agi.html' not in md)
check('切り出した旨の断り書きは無い', '切り出' not in md and 'この記事は' not in md)

# ── 要確認 ────────────────────────────────────────────────
check('資料の中だけで通じる言い回しを拾っている',
      any('次の面' in f for f in meta['check']), str(meta['check']))

# ── 台帳 ──────────────────────────────────────────────────
posts = note_ledger.load()['posts']
check('台帳に1行ついた', len(posts) == 1)
row = posts[0]
check('台帳の面は昇順（並べ替えても同じ記事）', row['sections'] == [1, 2, 3])
check('型が台帳に残っている', row['shape'].get('title_kind') == top['kind']
      and row['shape'].get('cover') is True and row['shape'].get('order') == 'strong',
      str(row['shape']))
raw = io.open(note_ledger.LEDGER, encoding='utf-8').read()
check('台帳に面の中身は入っていない',
      not any(w in raw for w in ('合意で動く', '来る日ではない', '能力で引く線', '引き直される線')))

check('中身が無くなった面を拾っている', meta['stub_sections'] == [1],
      str(meta['stub_sections']))
check('中身のある面は抜け殻にならない', 2 not in meta['stub_sections'] and 3 not in meta['stub_sections'])

# ── 並べ替えを切ったとき ──────────────────────────────────
out2 = os.path.join(TMP, 'draft2')
sys.argv = ['note_export.py', '01_concept/what-is-agi.html', '--sections', '1,2,3',
            '--no-figs', '--no-cover', '--order', 'deck', '--min-card-chars', '0',
            '--out', out2, '--no-record']
note_export.main()
meta2 = json.load(io.open(os.path.join(out2, 'meta.json'), encoding='utf-8'))
md2 = io.open(os.path.join(out2, 'article.md'), encoding='utf-8').read()
check('--order deck で資料の順のまま', meta2['sections'] == [1, 2, 3])
check('--min-card-chars 0 で短いカードも残る', '### 短い' in md2)
check('--no-record で台帳は増えない', len(note_ledger.load()['posts']) == 1)
check('--no-cover で見出し画像を作らない', meta2['cover'] is None)
check('カードを残せば抜け殻も消える', meta2['stub_sections'] == [], str(meta2['stub_sections']))

print('\n%d / %d' % (sum(ok), len(ok)))
print('下書き:', out)
sys.exit(0 if all(ok) else 1)
