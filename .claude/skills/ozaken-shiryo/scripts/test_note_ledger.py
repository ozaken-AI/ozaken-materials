# -*- coding: utf-8 -*-
"""台帳と採点を、鍵なしで確かめる。作り物の面を渡して動きを見る。"""
import json
import os
import subprocess
import sys
import tempfile

S = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, S)
import note_ledger
import note_pick

TMP = tempfile.mkdtemp()
note_ledger.LEDGER = os.path.join(TMP, 'note_ledger.json')


def sec(title, sub='', lede='', figs=0, cards=0, take='', paras=()):
    return {'eyebrow': '', 'title': title, 'sub': sub, 'lede': lede,
            'figs': [{'n': i, 'title': '図%d' % i, 'cap': ''} for i in range(figs)],
            'cards': [('見出し%d' % i, 'カードの本文。' * 12) for i in range(cards)],
            'paras': list(paras), 'take': take}


ok = []


def check(name, cond, extra=''):
    ok.append(cond)
    print('%s %s %s' % ('✓' if cond else '✗', name, extra if not cond else ''))


# ── 指紋 ───────────────────────────────────────────────────
a = sec('AGIとは何か', lede='定義のほうが動く。', figs=1, cards=2, take='一言')
b = sec('AGIとは何か', lede='定義のほうが動く。', figs=1, cards=2, take='一言')
c = sec('AGIとは何か', lede='定義のほうが動く。ここを直した。', figs=1, cards=2, take='一言')
check('同じ中身は同じ指紋', note_ledger.digest(a) == note_ledger.digest(b))
check('1文字直すと指紋が変わる', note_ledger.digest(a) != note_ledger.digest(c))
check('指紋は8桁', len(note_ledger.digest(a)) == 8, note_ledger.digest(a))
check('指紋から中身は読めない（題を含まない文字列）',
      'AGI' not in note_ledger.digest(a))

# ── 記録 ───────────────────────────────────────────────────
ids = [note_ledger.digest(a)]
row, new = note_ledger.record('what-is-agi', '01_concept/what-is-agi.html',
                              '公開ずみの資料タイトル', [2], ids, ['AI'])
check('新しい行ができる', new and row['status'] == 'draft')
row, new = note_ledger.record('what-is-agi', '01_concept/what-is-agi.html',
                              '公開ずみの資料タイトル', [2], ids, ['AI'])
check('同じ資料・同じ面は1行にまとまる', (not new) and len(note_ledger.load()['posts']) == 1)
note_ledger.record('what-is-agi', '01_concept/what-is-agi.html', 'x', [5, 6],
                   ['aaaa1111', 'bbbb2222'], ['AI'])
check('面の組が違えば別の行', len(note_ledger.load()['posts']) == 2)

# ── 台帳に平文の中身が入っていないこと ────────────────────
raw = open(note_ledger.LEDGER, encoding='utf-8').read()
check('資料の題は持つ（index.html で公開ずみ）', '公開ずみの資料タイトル' in raw)
check('面の中身は持たない', not any(w in raw for w in
      ('AGIとは何か', '定義のほうが動く', '見出し0', 'カードの本文', '一言')))

# ── 公開として記録 ─────────────────────────────────────────
d = note_ledger.load()
p = note_ledger.one(d, 'what-is-agi', [2])
p['status'] = 'posted'
p['note_url'] = 'https://note.com/ozaken_ai/n/nTEST'
p['posted_at'] = '2026-09-11'
note_ledger.save(d)
# 公開済みの行を切り出し直しても、公開の記録は消えない
row, new = note_ledger.record('what-is-agi', '01_concept/what-is-agi.html', 'x',
                              [2], ids, ['AI'])
check('公開済みの行は切り出し直しても posted のまま',
      row['status'] == 'posted' and row['note_url'].endswith('nTEST'))

try:
    note_ledger.one(note_ledger.load(), 'what-is-agi', None)
    check('絞れないときは止まる', False, '止まらなかった')
except SystemExit as e:
    check('絞れないときは候補を見せて止まる', '--sections' in str(e))

# ── 出した面の集合 ─────────────────────────────────────────
t = note_ledger.taken()
check('指紋で引ける', ('what-is-agi', ids[0]) in t and ('what-is-agi', 'aaaa1111') in t)
check('資料ごとの本数', note_ledger.deck_counts()['what-is-agi'] == 2)

# ── 採点 ───────────────────────────────────────────────────
good = sec('単独で読める面', lede='ここから始まる話。', figs=2, cards=3,
           take='締めの一言', paras=['本文。' * 120])
bad = sec('前を受ける面', lede='だから、次の面で見るように、この資料の要点はここにある。',
          figs=0, cards=0, paras=['短い。'])
mg, mb = note_pick.measure(good), note_pick.measure(bad)
sg, wg = note_pick.score(mg)
sb, wb = note_pick.score(mb)
check('良い面のほうが高い', sg > sb, '%d vs %d' % (sg, sb))
check('図版が点になる', wg['図'] == 24 and wb['図'] == 0)
check('指示語で始まる面は独立点が下がる', mb['dep'] and not mg['dep'])
check('資料内参照を数えている', mb['refs'] >= 2 and wb['参'] < 0, str(mb['refs']))
check('参照の減点は3つで頭打ち', note_pick.score(dict(mb, refs=9))[1]['参'] == -36)
check('同じ資料への減点が効く', note_pick.score(mg, 2)[0] == sg - 12)
check('--no-spread で減点が消える', note_pick.score(mg, 2, spread=False)[0] == sg)

# ── CLI ────────────────────────────────────────────────────
env = dict(os.environ, PYTHONPATH=S, OZAKEN_NOTE_LEDGER=note_ledger.LEDGER)
run = lambda *a: subprocess.run([sys.executable, os.path.join(S, 'note_ledger.py')] + list(a),
                                capture_output=True, text=True, env=env)
r = run('list')
check('CLI list が動く', r.returncode == 0, r.stderr[-300:])
r = run('drop', 'what-is-agi', '--sections', '2')
check('公開済みは --force なしで消せない',
      r.returncode != 0 and '公開済み' in (r.stdout + r.stderr), r.stdout + r.stderr)

print('\n%d / %d' % (sum(ok), len(ok)))
sys.exit(0 if all(ok) else 1)
