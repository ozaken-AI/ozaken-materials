#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""資料の中身を切り出して、note に載せられる記事の下書きにする。

  OZAKEN_PW=マスター python3 note_export.py 01_concept/what-is-agi.html
  OZAKEN_PW=マスター python3 note_export.py 01_concept/what-is-agi.html --sections 2,7,8
  OZAKEN_PW=マスター python3 note_export.py 01_concept/what-is-agi.html --no-figs --out /tmp/x

出るもの（既定は note_drafts/<資料名>/。**公開リポジトリには入れない**。.gitignore 済み）
  article.md    見出し・太字・画像つき。note のエディタに貼るときの正
  article.txt   装飾なし。画像は【画像: figs/fig_01.png】の印だけ
  figs/         図版のPNG（shot_figs.mjs で撮る）。記事に貼る画像
  meta.json     題・副題の候補・ハッシュタグ・切り出した面・元の資料

**資料は鍵つき、note は公開。** だから下書きに資料そのもののURLは書かず、
アーカイブの玄関（content.ozaken.ai）と ozaken.ai だけを書く。
切り出しで資料の中身が丸ごと外に出ないよう、既定では**本文の面を全部は出さない**。
`--sections` で面を選ぶのが基本。全部出したいときは `--all`。

**書き方は変えない。** 資料の文をそのまま使い、句読点も足さない。
note 向けに変えるのは形だけ：面の題を見出しに、カードの見出しを小見出しに、
図版を画像に、おざけんのワンポイントを引用に。
"""
import argparse
import html
import io
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lockbox
import oz_root

ROOT = oz_root.root(HERE)
ARCHIVE = 'https://content.ozaken.ai/'
PORTFOLIO = 'https://ozaken.ai/'
X_URL = 'https://x.com/ozaken_AI'
DEFAULT_TAGS = ['AI', '生成AI', 'AIエージェント', 'おざけん']


# ── HTML → 文 ──────────────────────────────────────────────
def text(s, md=True):
    """タグを落として文にする。太字だけ残す（md=True のとき ** で）"""
    s = re.sub(r'<br\s*/?>', '\n', s)
    s = re.sub(r'<span class="mth">(.*?)</span>', r'【\1】', s)
    if md:
        s = re.sub(r'<(b|strong)>(.*?)</\1>', r'**\2**', s, flags=re.S)
        s = re.sub(r'<span class="[^"]*fw-bold[^"]*">(.*?)</span>', r'**\1**', s, flags=re.S)
        s = re.sub(r'<span class="hot">(.*?)</span>', r'**\1**', s, flags=re.S)
    s = re.sub(r'<[^>]+>', '', s)
    s = html.unescape(s)
    s = re.sub(r'[ \t]+', ' ', s)
    s = re.sub(r' *\n *', '\n', s).strip()
    # ** の直後に句点が続くと note では崩れないが、** ** が隣り合うと消えるので離す
    s = s.replace('****', '** **')
    return s


def first(pat, s, flags=re.S):
    m = re.search(pat, s, flags)
    return m.group(1) if m else ''


# ── 面の解析 ────────────────────────────────────────────────
def parse(page):
    i0 = page.index('<section class="hero">')
    i1 = page.index('<div class="oz-return">') if '<div class="oz-return">' in page else len(page)
    body = page[i0:i1]
    spans = [m.start() for m in re.finditer(r'<section[^>]*>', body)] + [len(body)]
    parts = [body[spans[i]:spans[i + 1]] for i in range(len(spans) - 1)]
    hero, close, mid = parts[0], parts[-1], parts[1:-1]

    doc = {
        'title': text(first(r'<h1 class="hero-title">(.*?)</h1>', hero), md=False).replace('\n', ' ─ '),
        'copy': text(first(r'<p class="hero-copy">(.*?)</p>', hero)),
        'close_title': text(first(r'<h2 class="sec-title">(.*?)</h2>', close), md=False).replace('\n', ' '),
        'close_copy': text(first(r'<p class="kicker">(.*?)</p>', close)),
        'sections': [],
    }
    fig_i = 0
    for s in mid:
        sec = {
            'eyebrow': text(first(r'<span class="eyebrow">(.*?)</span>', s), md=False),
            'title': text(first(r'<h2 class="sec-title">(.*?)</h2>', s), md=False).replace('\n', ' '),
            'sub': text(first(r'<p class="sec-sub">(.*?)</p>', s)),
            'lede': text(first(r'<p class="(?:lede|kicker)">(.*?)</p>', s)),
            'figs': [], 'cards': [], 'paras': [], 'take': '',
        }
        for f in re.findall(r'<div class="figure">(.*?)</div>\s*(?:<p class="figure-cap">(.*?)</p>)?', s, re.S):
            pass
        for m in re.finditer(r'<div class="figure">(.*?)(?=<div class="figure">|<div class="cards"|<div class="take"|<p class="note"|<div class="bare"|</section>)', s, re.S):
            blk = m.group(1)
            t = text(first(r'<p class="fig-title">(.*?)</p>', blk), md=False)
            t = re.sub(r'^Fig\.\d+\s*(?:──|—)?\s*', '', t).strip()
            cap = text(first(r'<p class="figure-cap">(.*?)</p>', blk), md=False)
            sec['figs'].append({'n': fig_i, 'title': t, 'cap': cap})
            fig_i += 1
        for h3, p in re.findall(r'<div class="card">.*?<h3>(.*?)</h3>\s*<p>(.*?)</p>', s, re.S):
            sec['cards'].append((text(h3), text(p)))
        for p in re.findall(r'<div class="bare">(.*?)</div>', s, re.S):
            sec['paras'] += [text(x) for x in re.findall(r'<p>(.*?)</p>', p, re.S)]
        for p in re.findall(r'<p class="note">(.*?)</p>', s, re.S):
            sec['paras'].append(text(p))
        sec['take'] = text(first(r'<p class="take-text">(.*?)</p>', s))
        doc['sections'].append(sec)
    return doc


# ── 記事にする ──────────────────────────────────────────────
def render(doc, picks, rel, use_figs, intro, outro):
    md, tx = [], []

    def both(m, t=None):
        md.append(m)
        tx.append(m if t is None else t)

    if intro:
        both(doc['copy'])
        both('')
    for k in picks:
        s = doc['sections'][k - 1]
        both('## ' + s['title'], s['title'])
        if s['sub']:
            both(s['sub'])
        if s['lede']:
            both('')
            both(s['lede'])
        for f in s['figs']:
            both('')
            if use_figs:
                both('![%s](figs/fig_%02d.png)' % (f['title'], f['n']), '【画像: figs/fig_%02d.png】' % f['n'])
            both('図：' + f['title'])
            if f['cap'] and '小澤健祐' not in f['cap']:
                both('（%s）' % f['cap'])
        for h, p in s['cards']:
            both('')
            both('### ' + h, '■ ' + h)
            both(p)
        for p in s['paras']:
            both('')
            both(p)
        if s['take']:
            both('')
            q = s['take'].replace('\n', '\n> ')
            both('> ' + q, s['take'])
            both('> ── 小澤健祐（おざけん）', '── 小澤健祐（おざけん）')
        both('')
    if outro:
        both('## ' + doc['close_title'], doc['close_title'])
        both(doc['close_copy'])
        both('')
    # **末尾は、3つのURLを並べるだけ。** 資料そのもののURLは書かない。
    # note の読者がその先に行ける場所を、ポートフォリオ・資料サイト・X の順に置く
    both('---', '')
    both('ポートフォリオサイト')
    both(PORTFOLIO)
    both('')
    both('AI資料アーカイブ')
    both(ARCHIVE)
    both('')
    both('X（旧Twitter）')
    both(X_URL)
    return '\n'.join(md).strip() + '\n', re.sub(r'\*\*', '', '\n'.join(tx)).strip() + '\n'


def hashtags(rel):
    try:
        from crossref_data import CONCEPTS
    except Exception:
        return DEFAULT_TAGS
    tags = list(DEFAULT_TAGS)
    for name, (canon, words, _) in CONCEPTS.items():
        if canon == rel:
            for w in [name] + list(words):
                w = re.sub(r'[\s・/／]', '', w)
                if w and w not in tags and len(tags) < 10:
                    tags.append(w)
    return tags


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('rel')
    ap.add_argument('--sections', default='', help='切り出す面の番号（1始まり、カンマ区切り）')
    ap.add_argument('--all', action='store_true', help='本文の面を全部出す')
    ap.add_argument('--out', default='')
    ap.add_argument('--no-figs', action='store_true')
    ap.add_argument('--no-intro', action='store_true')
    ap.add_argument('--no-outro', action='store_true')
    a = ap.parse_args()

    pw = os.environ.get('OZAKEN_PW') or sys.exit('OZAKEN_PW を設定してください')
    path = os.path.join(ROOT, a.rel)
    page = lockbox.decrypt(path, pw)
    doc = parse(page)
    n = len(doc['sections'])
    if a.sections:
        picks = [int(x) for x in a.sections.split(',') if x.strip()]
        bad = [k for k in picks if not 1 <= k <= n]
        if bad:
            sys.exit('面の番号が範囲外です: %s（本文は %d 面）' % (bad, n))
    elif a.all:
        picks = list(range(1, n + 1))
    else:
        picks = list(range(1, min(3, n) + 1))
        print('※ --sections も --all も無いので、最初の %d 面だけを切り出します' % len(picks))

    slug = os.path.splitext(os.path.basename(a.rel))[0]
    out = a.out or os.path.join(ROOT, 'note_drafts', slug)
    os.makedirs(out, exist_ok=True)

    use_figs = not a.no_figs
    if use_figs:
        figdir = os.path.join(out, 'figs')
        os.makedirs(figdir, exist_ok=True)
        r = subprocess.run(['node', os.path.join(HERE, 'shot_figs.mjs'), a.rel, figdir],
                           cwd=ROOT, capture_output=True, text=True,
                           env=dict(os.environ, OZAKEN_PW=pw))
        if r.returncode:
            print('図版の撮影に失敗。画像なしで続けます:', (r.stdout + r.stderr)[-300:])
            use_figs = False

    md, tx = render(doc, picks, a.rel, use_figs, not a.no_intro, not a.no_outro)
    io.open(os.path.join(out, 'article.md'), 'w', encoding='utf-8').write(md)
    io.open(os.path.join(out, 'article.txt'), 'w', encoding='utf-8').write(tx)
    meta = {
        'source': a.rel,
        'deck_title': doc['title'],
        'title_candidates': [doc['title']] + [doc['sections'][k - 1]['title'] for k in picks[:3]],
        'sections': picks,
        'figs': sorted({f['n'] for k in picks for f in doc['sections'][k - 1]['figs']}),
        'hashtags': hashtags(a.rel),
        'chars': len(tx),
    }
    flags = sorted({m.group(0) for m in re.finditer(
        r'[^。\n]*(?:次の面|前の面|あとの面|この面|第\d+面|姉妹資料|この資料)[^。\n]*。?', tx)})
    meta['check'] = flags
    io.open(os.path.join(out, 'meta.json'), 'w', encoding='utf-8').write(
        json.dumps(meta, ensure_ascii=False, indent=2))
    print('書きました: %s' % out)
    print('  面 %s / 文字 %d / 画像 %d 点 / #%s' % (picks, len(tx), len(meta['figs']), ' #'.join(meta['hashtags'])))
    if use_figs:
        keep = {'fig_%02d.png' % i for i in meta['figs']}
        for f in os.listdir(figdir):
            if f.endswith('.png') and f not in keep:
                os.remove(os.path.join(figdir, f))
    if flags:
        print('  要確認（資料の中だけで通じる言い回し。記事では直す）:')
        for f in flags[:8]:
            print('    ・' + f[:70])
    print('  次: article.md を note のエディタに貼り、figs/ の画像を印の位置に入れる'
          '（自動投稿は note_post.mjs。未検証なので必ず下書きで止める）')


if __name__ == '__main__':
    main()
