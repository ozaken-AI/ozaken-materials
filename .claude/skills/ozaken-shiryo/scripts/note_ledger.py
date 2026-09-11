#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""note に出した面の台帳。何をいつ出したかを覚えておき、重複を防ぐ。

  python3 note_ledger.py list [--status draft|posted] [--deck <slug>]
  python3 note_ledger.py posted <slug> --url https://note.com/… [--at 2026-09-11]
  python3 note_ledger.py reactions <slug> --likes 120 [--comments 3] [--at 2026-09-20]
  python3 note_ledger.py memo <slug> "書きたいこと"
  python3 note_ledger.py drop <slug> [--sections 2,7,8]

行は note_export.py が `--record`（既定ON）で作る。作られた時点では `draft`。
note で公開ボタンを押したら、手で `posted` に上げて URL を入れる。
公開は人が押すものなので、台帳が勝手に posted に変わることはない。

**台帳は公開リポジトリに入る。だから面の題も記事の本文も持たない。**
資料の題は index.html にすでに平文で載っているので持ってよい。
面の中身は暗号の内側なので、持つのは本文の SHA-256 の先頭8桁だけ。
ハッシュは中身を漏らさず、そのうえで2つの役に立つ:
  ・面の番号ではなく中身で重複を見るので、資料を直して面がずれても取り違えない
  ・出した当時と中身が変わった面を「出し直す候補」として拾える
"""
import argparse
import datetime
import hashlib
import io
import json
import os
import re
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
# 置き場所はスキルの直下（scripts/ の1つ上）。リポジトリ直下はそのまま
# content.ozaken.ai の公開ルートなので、道具の状態はサイトの中身と混ぜない
# OZAKEN_NOTE_LEDGER を設定すれば、そちらが優先される（試すとき用）
LEDGER = os.environ.get('OZAKEN_NOTE_LEDGER') or os.path.join(
    os.path.dirname(HERE), 'note_ledger.json')
VERSION = 1
STATUSES = ('draft', 'posted')


def today():
    return datetime.date.today().isoformat()


# ── 読み書き ────────────────────────────────────────────────
def load():
    if not os.path.exists(LEDGER):
        return {'version': VERSION, 'updated': today(), 'posts': []}
    with io.open(LEDGER, encoding='utf-8') as f:
        d = json.load(f)
    d.setdefault('posts', [])
    return d


def save(d):
    d['version'] = VERSION
    d['updated'] = today()
    # 並びは記録した日付の順に固定する。別の人と並行して push するので、
    # 行が動くと差分がむだに膨らみ、そのぶん衝突しやすくなる
    d['posts'].sort(key=lambda p: (p.get('recorded_at') or '', p.get('slug') or '',
                                   str(p.get('sections') or '')))
    io.open(LEDGER, 'w', encoding='utf-8').write(
        json.dumps(d, ensure_ascii=False, indent=2) + '\n')


def digest(sec):
    """面の中身の指紋。台帳に置けるのはこれだけ（面の題も本文も置かない）。

    note_export.parse() が出す面の辞書を、そのまま渡す。
    """
    parts = [sec.get('title', ''), sec.get('sub', ''), sec.get('lede', '')]
    parts += [f.get('title', '') for f in sec.get('figs', [])]
    parts += [h + p for h, p in sec.get('cards', [])]
    parts += list(sec.get('paras', []))
    parts.append(sec.get('take', ''))
    blob = re.sub(r'\s+', '', ''.join(parts))
    return hashlib.sha256(blob.encode('utf-8')).hexdigest()[:8]


# ── 引く ────────────────────────────────────────────────────
def match(posts, slug, sections=None):
    hit = [p for p in posts if p.get('slug') == slug]
    if sections is not None:
        hit = [p for p in hit if p.get('sections') == list(sections)]
    return hit


def taken(posts=None):
    """すでに手をつけた面の指紋。{(slug, digest), …}

    下書きのまま止まっている面も入れる。note の下書き箱に眠っているものを
    「まだ出していない」として並べ直すと、同じ面を二度書くことになる。
    """
    posts = load()['posts'] if posts is None else posts
    return {(p['slug'], sid) for p in posts for sid in (p.get('section_ids') or [])}


def deck_counts(posts=None):
    """資料ごとに、何本の記事を出した（下書きを含む）か"""
    posts = load()['posts'] if posts is None else posts
    return Counter(p['slug'] for p in posts)


# ── 書く ────────────────────────────────────────────────────
def record(slug, source, deck_title, sections, section_ids, hashtags, shape=None):
    """切り出した内容を下書きとして記録する。

    同じ資料・同じ面の組は1行にまとめて更新する。試しの切り出しを繰り返しても
    行は増えない。返すのは (行, 新しく作ったか)。

    shape は「どういう形で出したか」（題の型・並び・見出し画像の有無・長さ）。
    スキ数と突き合わせて、**どの型が効いたかを後から言えるようにする**ためのもの。
    公開済みの行では、実際に使った型を人が posted --title-kind で上書きする。
    """
    d = load()
    hit = match(d['posts'], slug, list(sections))
    if hit:
        p = hit[0]
        p['source'] = source
        p['deck_title'] = deck_title
        p['section_ids'] = list(section_ids)
        p['hashtags'] = list(hashtags)
        # 公開済みの行は status も日付も触らない。切り出し直しただけで
        # 「公開した」という記録を消してしまうと、台帳の意味がなくなる
        if p.get('status') != 'posted':
            p['recorded_at'] = today()
            if shape:
                p['shape'] = shape
        save(d)
        return p, False
    p = {
        'slug': slug,
        'source': source,
        'deck_title': deck_title,
        'sections': list(sections),
        'section_ids': list(section_ids),
        'status': 'draft',
        'recorded_at': today(),
        'posted_at': None,
        'note_url': None,
        'hashtags': list(hashtags),
        'reactions': {'checked_at': None, 'likes': None, 'comments': None},
        'shape': shape or {},
        'memo': '',
    }
    d['posts'].append(p)
    save(d)
    return p, True


def one(d, slug, sections):
    """slug で1行に絞る。絞れなければ、候補を見せて止まる"""
    hit = match(d['posts'], slug, sections)
    if not hit:
        sys.exit('台帳に %s の行がありません（list で確かめてください）' % slug)
    if len(hit) > 1:
        lines = ['%s は %d 行あります。--sections で選んでください:' % (slug, len(hit))]
        for p in hit:
            lines.append('  --sections %s  … %s / %s'
                         % (','.join(str(x) for x in p['sections']),
                            p['status'], p.get('note_url') or '(URL未記入)'))
        sys.exit('\n'.join(lines))
    return hit[0]


# ── CLI ─────────────────────────────────────────────────────
def parse_sections(s):
    return [int(x) for x in s.split(',') if x.strip()] if s else None


def cmd_list(a):
    d = load()
    posts = d['posts']
    if a.status:
        posts = [p for p in posts if p.get('status') == a.status]
    if a.deck:
        posts = [p for p in posts if p.get('slug') == a.deck]
    if not posts:
        print('該当なし（台帳: %s）' % LEDGER)
        return
    print('%-28s %-7s %-10s %-12s %s' % ('資料', '状態', '日付', '面', 'URL / 題'))
    print('-' * 100)
    for p in posts:
        when = p.get('posted_at') or p.get('recorded_at') or ''
        secs = ','.join(str(x) for x in p.get('sections') or [])
        tail = p.get('note_url') or ('（未公開）' + (p.get('deck_title') or ''))
        print('%-28s %-7s %-10s %-12s %s'
              % (p['slug'][:28], p.get('status', ''), when, secs, tail[:52]))
        r = p.get('reactions') or {}
        if r.get('likes') is not None:
            print('%s└ スキ %s / コメント %s（%s 時点）'
                  % (' ' * 30, r['likes'], r.get('comments'), r.get('checked_at')))
    n = Counter(p.get('status') for p in d['posts'])
    print('\n合計 %d 行（公開 %d / 下書き %d）。面の延べ %d'
          % (len(d['posts']), n['posted'], n['draft'],
             sum(len(p.get('sections') or []) for p in d['posts'])))


def cmd_posted(a):
    d = load()
    p = one(d, a.slug, parse_sections(a.sections))
    p['status'] = 'posted'
    p['note_url'] = a.url
    p['posted_at'] = a.at or today()
    if a.title_kind:
        # 実際に使った題の型。候補の1位をそのまま使うとは限らないので、ここで直す
        p.setdefault('shape', {})['title_kind'] = a.title_kind
    save(d)
    print('公開として記録しました: %s 面%s → %s'
          % (p['slug'], p['sections'], a.url))


def cmd_reactions(a):
    d = load()
    p = one(d, a.slug, parse_sections(a.sections))
    r = p.setdefault('reactions', {})
    r['checked_at'] = a.at or today()
    if a.likes is not None:
        r['likes'] = a.likes
    if a.comments is not None:
        r['comments'] = a.comments
    save(d)
    print('反応を記録しました: %s スキ %s / コメント %s（%s 時点）'
          % (p['slug'], r.get('likes'), r.get('comments'), r['checked_at']))


def cmd_memo(a):
    d = load()
    p = one(d, a.slug, parse_sections(a.sections))
    p['memo'] = a.text
    save(d)
    print('書きました: %s → %s' % (p['slug'], a.text))


def cmd_stats(a):
    """出した型ごとに、スキの平均を並べる。

    **ここが、この仕組みで唯一「効いた／効かない」を言える場所。**
    それ以外の採点は、すべて「効くとされている型」でしかない。
    行が少ないうちは平均を信じない。件数を必ず一緒に見る。
    """
    rows = [p for p in load()['posts']
            if p.get('status') == 'posted'
            and (p.get('reactions') or {}).get('likes') is not None]
    if not rows:
        print('スキ数の入った行がまだありません。\n'
              '  公開したら: note_ledger.py posted <slug> --url … --title-kind <型>\n'
              '  数えたら:   note_ledger.py reactions <slug> --likes N')
        return
    print('スキ数の入っている記事 %d 本\n' % len(rows))

    def group(name, key):
        buckets = {}
        for p in rows:
            buckets.setdefault(key(p), []).append(p['reactions']['likes'])
        print('── %s ──' % name)
        for k, v in sorted(buckets.items(), key=lambda kv: -sum(kv[1]) / len(kv[1])):
            print('  %-12s 平均 %6.1f （%d本: %s）'
                  % (k, sum(v) / len(v), len(v), ' '.join(str(x) for x in sorted(v, reverse=True)[:8])))
        print()

    group('題の型', lambda p: (p.get('shape') or {}).get('title_kind') or '(未記録)')
    group('見出し画像', lambda p: {True: 'あり', False: 'なし'}.get(
        (p.get('shape') or {}).get('cover'), '(未記録)'))
    group('面の並び', lambda p: (p.get('shape') or {}).get('order') or '(未記録)')

    n = [(p['reactions']['likes'], (p.get('shape') or {}).get('chars')) for p in rows
         if (p.get('shape') or {}).get('chars')]
    if len(n) >= 4:
        n.sort(key=lambda x: x[1])
        half = len(n) // 2
        lo = sum(x[0] for x in n[:half]) / half
        hi = sum(x[0] for x in n[half:]) / (len(n) - half)
        print('── 長さ ──')
        print('  短いほう半分（〜%d字）平均 %.1f / 長いほう半分（%d字〜）平均 %.1f'
              % (n[half - 1][1], lo, n[half][1], hi))
    if len(rows) < 8:
        print('\n※ %d本しかありません。型の差より、記事ごとのばらつきのほうが大きい段階です'
              % len(rows))


def cmd_drop(a):
    d = load()
    p = one(d, a.slug, parse_sections(a.sections))
    if p.get('status') == 'posted' and not a.force:
        sys.exit('%s は公開済みです。消すと「出していない」ことになり、'
                 'note_pick が同じ面をまた勧めます。本当に消すなら --force' % a.slug)
    d['posts'].remove(p)
    save(d)
    print('消しました: %s 面%s' % (p['slug'], p['sections']))


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd')

    q = sub.add_parser('list', help='台帳の中身を見る')
    q.add_argument('--status', choices=STATUSES)
    q.add_argument('--deck')
    q.set_defaults(fn=cmd_list)

    q = sub.add_parser('posted', help='公開したので URL を記録する')
    q.add_argument('slug')
    q.add_argument('--url', required=True)
    q.add_argument('--at', help='公開日（既定は今日）')
    q.add_argument('--title-kind', dest='title_kind',
                   help='実際に使った題の型（deck / deck-half / section / take / fig / custom）')
    q.add_argument('--sections', help='同じ資料の行が複数あるとき、どれかを選ぶ')
    q.set_defaults(fn=cmd_posted)

    q = sub.add_parser('reactions', help='反応を記録する')
    q.add_argument('slug')
    q.add_argument('--likes', type=int)
    q.add_argument('--comments', type=int)
    q.add_argument('--at', help='数えた日（既定は今日）')
    q.add_argument('--sections')
    q.set_defaults(fn=cmd_reactions)

    q = sub.add_parser('memo', help='覚え書きを残す')
    q.add_argument('slug')
    q.add_argument('text')
    q.add_argument('--sections')
    q.set_defaults(fn=cmd_memo)

    q = sub.add_parser('stats', help='型ごとのスキの平均を見る')
    q.set_defaults(fn=cmd_stats)

    q = sub.add_parser('drop', help='行を消す')
    q.add_argument('slug')
    q.add_argument('--sections')
    q.add_argument('--force', action='store_true')
    q.set_defaults(fn=cmd_drop)

    a = ap.parse_args()
    if not a.cmd:
        ap.print_help()
        return
    a.fn(a)


if __name__ == '__main__':
    main()
