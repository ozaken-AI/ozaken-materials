#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""まだ note に出していない面を、出しやすい順に並べる。

  OZAKEN_PW=マスター python3 note_pick.py
  OZAKEN_PW=マスター python3 note_pick.py --top 40 --dir 01_concept
  OZAKEN_PW=マスター python3 note_pick.py --deck what-is-agi --all
  OZAKEN_PW=マスター python3 note_pick.py --json > /tmp/pick.json

資料は111本、1本あたり10面前後。候補は1,000面を超える。
足りないのは供給ではなく「どれを出すか」なので、**決めるのは人のまま**にして、
機械は並べるところまでをやる。点は目安で、順位は結論ではない。

並べ方は3つの軸（`--why` で各面の内訳が出る）:
  図版がある            … note は画像が1枚あるだけで読まれ方が変わる
  単独で読んで完結する  … 立ち上がりが自前か、構造が自前か、量が記事の尺か、
                          指示語で始まっていないか
  資料の中だけで通じる  … 「次の面」「姉妹資料」などの数だけ減点。
  言い回しが少ない        切り出したあとに直す手間がそのまま残るので

すでに出した面は、番号ではなく**中身の指紋**で外す（note_ledger.py を見る）。
資料を直して面がずれても取り違えない。下書きのまま止まっている面も外す。

裏資料（AX_Table / Training / Udemy / weekly）は、相手先や受講者に向けたものなので
既定では候補に入れない。要るときだけ `--backstage`。
"""
import argparse
import io
import json
import os
import re
import sys
from glob import glob

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lockbox
import note_export
import note_ledger
import oz_root

ROOT = oz_root.root(HERE)
CACHE = os.path.join(ROOT, 'note_drafts', '.pick_cache.json')

# 資料の中でしか通じない言い回し。記事にするときは必ず直す場所
REF_RE = re.compile(
    r'次の面|前の面|あとの面|この面|最初の面|最後の面|第\d+面|次のページ|前のページ'
    r'|姉妹資料|この資料|本資料|後述|前述|先ほど|ここまで見て|冒頭で')

# 前の面を受けて始まっている合図。単独で読むと、何を受けたのか分からない
OPENER_RE = re.compile(
    r'^(だから|そのため|そこで|その結果|つまり|しかし|ところが|一方|いっぽう'
    r'|では|さて|逆に|同様に|同じように|こうした|こうして|以上の)')


# ── 面を数える ──────────────────────────────────────────────
def prose(sec):
    """面の地の文。面の題は見出しになるので、量には数えない"""
    parts = [sec['sub'], sec['lede']]
    for f in sec['figs']:
        parts += [f['title'], f['cap']]
    parts += ['%s。%s' % (h, p) for h, p in sec['cards']]
    parts += list(sec['paras']) + [sec['take']]
    return '\n'.join(x for x in parts if x)


def measure(sec):
    """点をつけるのに要るものだけを取り出す。面の題以外の本文は持ち歩かない"""
    body = prose(sec)
    head = (sec['lede'] or sec['sub']
            or (sec['paras'][0] if sec['paras'] else '')
            or (sec['cards'][0][1] if sec['cards'] else ''))
    return {
        'title': sec['title'],
        'chars': len(re.sub(r'\s', '', body)),
        'figs': len(sec['figs']),
        'refs': len(REF_RE.findall(body)),
        'cards': len(sec['cards']),
        'take': bool(sec['take']),
        'lede': bool(sec['lede'] or sec['sub']),
        'dep': bool(OPENER_RE.match(head.lstrip())),
        'digest': note_ledger.digest(sec),
    }


def score(m, seen_from_deck=0, spread=True):
    """3つの軸で点をつける。判断はしない、並べるだけ"""
    fig = 24 if m['figs'] >= 2 else 18 if m['figs'] == 1 else 0

    own = 0
    if m['lede']:
        own += 10                      # 立ち上がりが自前にある
    if m['cards'] >= 2:
        own += 10                      # 中の構造が自前にある
    if m['take']:
        own += 8                       # 締めの一言がある
    n = m['chars']
    if 700 <= n <= 1800:
        own += 14                      # note の記事として素直な尺
    elif 450 <= n < 700 or 1800 < n <= 2600:
        own += 7
    if not m['dep']:
        own += 10                      # 前の面を受けて始まっていない

    # 参照は3つで頭打ち。4つあっても8つあっても「けっこう直す」で同じ
    ref = -min(m['refs'], 3) * 12
    # 同じ資料ばかり続けて出すと、読む側からは連載に見えて、1本の強さが落ちる
    spr = -min(seen_from_deck, 3) * 6 if spread else 0
    return fig + own + ref + spr, {'図': fig, '独': own, '参': ref, '散': spr}


# ── 資料を読む ──────────────────────────────────────────────
def decks(backstage=False):
    """資料の一覧。registry.docs() と同じ数え方。

    **分類フォルダは2桁で、0 始まりとは限らない。**
    '0*_*' で拾うと、分類が10を超えた日に 10_policy と 11_stats が丸ごと落ちる。
    """
    out = []
    for d in sorted(glob(os.path.join(ROOT, '[0-9][0-9]_*'))):
        out += sorted(glob(os.path.join(d, '*.html')))
    if backstage:
        for d in oz_root.BACKSTAGE_DIRS:
            out += sorted(glob(os.path.join(ROOT, d, '*.html')))
    return [f for f in out
            if 'OZAKEN-LOCKED2' in io.open(f, encoding='utf-8').read(64)]


def read_deck(path, rel, pw, cache, use_cache):
    """資料を1本読んで、面ごとの目安を返す。中身が変わっていなければ控えから"""
    st = os.stat(path)
    key = '%d:%d' % (int(st.st_mtime), st.st_size)
    hit = cache.get(rel)
    if use_cache and hit and hit.get('key') == key:
        return hit['title'], hit['secs']
    doc = note_export.parse(lockbox.decrypt(path, pw))
    secs = [measure(s) for s in doc['sections']]
    cache[rel] = {'key': key, 'title': doc['title'], 'secs': secs}
    return doc['title'], secs


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--top', type=int, default=30, help='並べる本数（既定30、0で全部）')
    ap.add_argument('--deck', help='この資料だけを見る（slug）')
    ap.add_argument('--dir', help='この分類だけを見る（01_concept など）')
    ap.add_argument('--backstage', action='store_true', help='裏資料も候補に入れる')
    ap.add_argument('--all', action='store_true', help='すでに出した面も並べる（印がつく）')
    ap.add_argument('--no-spread', action='store_true', help='同じ資料への減点をやめる')
    ap.add_argument('--why', action='store_true', help='点の内訳を出す')
    ap.add_argument('--json', action='store_true')
    ap.add_argument('--no-cache', action='store_true')
    a = ap.parse_args()

    pw = os.environ.get('OZAKEN_PW') or sys.exit('OZAKEN_PW を設定してください')

    posts = note_ledger.load()['posts']
    done = note_ledger.taken(posts)
    counts = note_ledger.deck_counts(posts)
    # 「この番号の面は前に出したが、中身が変わっている」を見分けるための控え
    by_index = {}
    for p in posts:
        for k in p.get('sections') or []:
            by_index.setdefault((p['slug'], k), p.get('status'))

    use_cache = not a.no_cache
    cache = {}
    if use_cache and os.path.exists(CACHE):
        try:
            cache = json.load(io.open(CACHE, encoding='utf-8'))
        except Exception:
            cache = {}

    rows, n_deck, n_sec = [], 0, 0
    for path in decks(a.backstage):
        rel = os.path.relpath(path, ROOT)
        slug = os.path.splitext(os.path.basename(rel))[0]
        if a.deck and slug != a.deck:
            continue
        if a.dir and not rel.startswith(a.dir.rstrip('/') + os.sep):
            continue
        try:
            deck_title, secs = read_deck(path, rel, pw, cache, use_cache)
        except SystemExit as e:
            print('読めませんでした（別のパスワードの資料かもしれません）: %s — %s'
                  % (rel, e), file=sys.stderr)
            continue
        n_deck += 1
        n_sec += len(secs)
        for i, m in enumerate(secs, 1):
            seen = (slug, m['digest']) in done
            if seen and not a.all:
                continue
            pt, why = score(m, counts.get(slug, 0), not a.no_spread)
            rows.append({
                'score': pt, 'why': why, 'slug': slug, 'source': rel,
                'deck_title': deck_title, 'section': i, 'digest': m['digest'],
                'title': m['title'], 'chars': m['chars'], 'figs': m['figs'],
                'refs': m['refs'], 'seen': seen,
                # 同じ番号を前に出しているのに指紋が違う。資料を直したか、面がずれたか
                'moved': (not seen) and (slug, i) in by_index,
            })

    if use_cache:
        os.makedirs(os.path.dirname(CACHE), exist_ok=True)
        io.open(CACHE, 'w', encoding='utf-8').write(
            json.dumps(cache, ensure_ascii=False))

    rows.sort(key=lambda r: (-r['score'], r['slug'], r['section']))
    shown = rows if a.top <= 0 else rows[:a.top]

    if a.json:
        print(json.dumps(shown, ensure_ascii=False, indent=2))
        return

    print('資料 %d 本 / 面 %d 面。出していない面 %d（台帳: %d 行）'
          % (n_deck, n_sec, sum(1 for r in rows if not r['seen']), len(posts)))
    print()
    print('%-4s %-2s %-24s %-3s %-3s %-5s %-3s %s'
          % ('点', '', '資料', '面', '図', '字', '参', '見出し'))
    print('-' * 104)
    for r in shown:
        mark = '済' if r['seen'] else '改' if r['moved'] else ''
        print('%-4d %-2s %-24s %-3d %-3d %-5d %-3d %s'
              % (r['score'], mark, r['slug'][:24], r['section'], r['figs'],
                 r['chars'], r['refs'], r['title'][:38]))
        if a.why:
            print('%s└ %s' % (' ' * 5, ' '.join('%s%+d' % (k, v)
                                                for k, v in r['why'].items())))
    print()
    print('印  済=台帳にある（--all のときだけ出る）'
          ' / 改=同じ番号の面を前に出しているが中身が違う（資料を直したか、面がずれたか）')
    print('列  図=図版の数 / 字=地の文の字数 / 参=資料の中だけで通じる言い回しの数')
    if shown:
        r = shown[0]
        print('\n次: OZAKEN_PW=… python3 note_export.py %s --sections %d'
              % (r['source'], r['section']))


if __name__ == '__main__':
    main()
