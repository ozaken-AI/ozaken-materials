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
import note_hooks
import note_ledger
import note_pick
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
def strength(doc, k):
    """つかみの強さ。note_pick と同じ数え方で、面ひとつを見る"""
    return note_pick.score(note_pick.measure(doc['sections'][k - 1]))[0]


def order_picks(doc, picks, how):
    """note 向きに並べ替える。

    **いちばん強い面だけを先頭に出し、残りは資料の順のまま。**
    全部を点の順に並べ替えると、資料が積み上げてきた筋が崩れる。
    いっぽう note は最初の面で読むかが決まるので、先頭だけは入れ替える値打ちがある。
    """
    if how == 'deck' or len(picks) < 2:
        return list(picks), None
    top = max(picks, key=lambda k: strength(doc, k))
    if top == picks[0]:
        return list(picks), None
    return [top] + [k for k in picks if k != top], top


def render(doc, picks, use_figs, intro, outro, min_card=0):
    md, tx, dropped = [], [], []

    def both(m, t=None):
        md.append(m)
        tx.append(m if t is None else t)

    # note は最初の2〜3行で読むかどうかが決まる。
    # **資料の表紙のリードは資料全体の話**なので、3面だけ切り出した記事には合わない。
    # 先頭の面の立ち上がりを、そのまま記事の入り口にする（文は変えない。置き場所を変える）
    opening = ''
    if intro:
        s0 = doc['sections'][picks[0] - 1]
        opening = s0['lede'] or s0['sub'] or doc['copy']
        both(opening)
        both('')
    for k in picks:
        s = doc['sections'][k - 1]
        both('## ' + s['title'], s['title'])
        if s['sub'] and s['sub'] != opening:
            both(s['sub'])
        if s['lede'] and s['lede'] != opening:
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
            # 投影では1行の見出しでも成立するが、記事に並ぶと切れ端に見える。
            # 落としたものは必ず画面に出す。おざけんの文を黙って消さない
            if min_card and len(re.sub(r'\s', '', p)) < min_card:
                dropped.append((k, h, p))
                continue
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
    return ('\n'.join(md).strip() + '\n',
            re.sub(r'\*\*', '', '\n'.join(tx)).strip() + '\n',
            dropped)


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
    ap.add_argument('--no-record', action='store_true',
                    help='台帳に記録しない（既定は記録する）')
    ap.add_argument('--order', choices=('strong', 'deck'), default='strong',
                    help='strong=いちばん強い面を先頭に（既定） / deck=資料の順のまま')
    ap.add_argument('--min-card-chars', type=int, default=30,
                    help='これより短いカードは記事から落とす（既定30、0で落とさない）')
    ap.add_argument('--no-cover', action='store_true', help='見出し画像を作らない')
    ap.add_argument('--phrase', default='', help='見出し画像に載せるつかみ（既定は候補の1位）')
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

    # note 向きに並べ替える。台帳には並べ替える前の順（昇順）で残すので、
    # 並びを変えて切り出し直しても、同じ記事の行として1本にまとまる
    ledger_secs = sorted(picks)
    picks, moved = order_picks(doc, picks, a.order)
    if moved:
        print('面 %d を先頭に出しました（つかみが強い面。--order deck で資料の順のまま）' % moved)

    md, tx, dropped = render(doc, picks, use_figs, not a.no_intro, not a.no_outro,
                             a.min_card_chars)
    io.open(os.path.join(out, 'article.md'), 'w', encoding='utf-8').write(md)
    io.open(os.path.join(out, 'article.txt'), 'w', encoding='utf-8').write(tx)
    # カードを落とした結果、見出しとリードしか残らなかった面
    stubs = [k for k in picks
             if not any(True for h, p in doc['sections'][k - 1]['cards']
                        if not (a.min_card_chars
                                and len(re.sub(r'\s', '', p)) < a.min_card_chars))
             and not doc['sections'][k - 1]['figs']
             and not doc['sections'][k - 1]['paras']
             and not doc['sections'][k - 1]['take']]

    titles = note_hooks.title_candidates(doc, picks)
    phrases = note_hooks.phrase_candidates(doc, picks)
    meta = {
        'source': a.rel,
        'deck_title': doc['title'],
        'title_candidates': titles,
        'phrase_candidates': phrases,
        'sections': picks,
        'sections_sorted': ledger_secs,
        'order': a.order,
        'figs': sorted({f['n'] for k in picks for f in doc['sections'][k - 1]['figs']}),
        'hashtags': hashtags(a.rel),
        'chars': len(tx),
        'dropped_cards': [{'section': k, 'head': h, 'text': t} for k, h, t in dropped],
        'stub_sections': stubs,
    }
    flags = sorted({m.group(0) for m in re.finditer(
        r'[^。\n]*(?:次の面|前の面|あとの面|この面|第\d+面|姉妹資料|この資料)[^。\n]*。?', tx)})
    meta['check'] = flags

    print('書きました: %s' % out)
    print('  面 %s / 文字 %d / 画像 %d 点 / #%s'
          % (picks, len(tx), len(meta['figs']), ' #'.join(meta['hashtags'])))
    if use_figs:
        keep = {'fig_%02d.png' % i for i in meta['figs']}
        for f in os.listdir(figdir):
            if f.endswith('.png') and f not in keep:
                os.remove(os.path.join(figdir, f))

    # ── 見出し画像 ────────────────────────────────────────
    # note公式が「見出し画像の有無で、ビュー数やスキ数に数十パーセントの差がつく」と
    # 言っている。記事の中で、効き方がいちばんはっきり分かっている場所
    cover = None
    if not a.no_cover:
        phrase = a.phrase or (phrases[0]['text'] if phrases else '')
        cat = (doc['sections'][picks[0] - 1]['eyebrow'] or 'OZAKEN ARCHIVE')[:24]
        fig0 = doc['sections'][picks[0] - 1]['figs']
        figarg = (os.path.join(out, 'figs', 'fig_%02d.png' % fig0[0]['n'])
                  if use_figs and fig0 else '')
        cmd = ['node', os.path.join(HERE, 'note_cover.mjs'),
               '--out', os.path.join(out, 'cover.png'),
               '--title', titles[0]['text'] if titles else doc['title'], '--cat', cat]
        if phrase:
            cmd += ['--phrase', phrase]
        if figarg and os.path.exists(figarg):
            cmd += ['--fig', figarg]
        r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
        if r.returncode:
            print('  見出し画像は作れませんでした:', (r.stdout + r.stderr)[-300:])
        else:
            cover = 'cover.png'
            print('  ' + r.stdout.strip().replace('\n', '\n  '))
    meta['cover'] = cover

    io.open(os.path.join(out, 'article.md'), 'w', encoding='utf-8').write(md)
    io.open(os.path.join(out, 'article.txt'), 'w', encoding='utf-8').write(tx)
    io.open(os.path.join(out, 'meta.json'), 'w', encoding='utf-8').write(
        json.dumps(meta, ensure_ascii=False, indent=2))

    # ── 人が決めるための材料 ──────────────────────────────
    print()
    print(note_hooks.report(titles, 8, '題'))
    print('  ※ 選んだら NOTE_TITLE で note_post.mjs に渡すか、note で手で入れる')
    if dropped:
        print('\n  短いので記事から落としたカード（%d枚。--min-card-chars 0 で残す）:' % len(dropped))
        for k, h, t in dropped[:6]:
            print('    ・面%d「%s」%s' % (k, h[:24], t[:34]))
    # カードが全部落ちると、見出しとリードだけの抜け殻が残る。
    # 投影なら口で埋まるが、記事では「見出しの下に何も無い」ようにしか見えない
    if stubs:
        print('\n  ⚠ 中身が無くなった面: %s' % ' '.join('面%d' % k for k in stubs))
        print('    見出しとリードだけになっています。この面は --sections から外すか、'
              '--min-card-chars を下げてください')
    if flags:
        print('\n  要確認（資料の中だけで通じる言い回し。記事では直す）:')
        for f in flags[:8]:
            print('    ・' + f[:70])

    # 台帳に「下書きとして切り出した」ことを残す。次に note_pick.py を走らせたとき、
    # この面がもう一度勧められないようにするため。**公開したことにはしない。**
    # 公開ボタンは人が押すものなので、URL は押したあとに手で入れる
    if not a.no_record:
        ids = [note_ledger.digest(doc['sections'][k - 1]) for k in ledger_secs]
        row, new = note_ledger.record(slug, a.rel, doc['title'], ledger_secs, ids,
                                      meta['hashtags'],
                                      shape={'title_kind': titles[0]['kind'] if titles else None,
                                             'order': a.order, 'cover': bool(cover),
                                             'chars': len(tx)})
        print('\n  台帳: %s（%s）' % ('新しい行' if new else '既にある行を更新',
                                      note_ledger.LEDGER))
        if row['status'] == 'posted':
            print('  ※ この面は %s に公開済みとして記録されています: %s'
                  % (row['posted_at'], row['note_url']))

    print('\n  次: article.md を note のエディタに貼り、figs/ の画像を印の位置に入れる。'
          '見出し画像に cover.png を設定する'
          '（自動投稿は note_post.mjs。未検証なので必ず下書きで止める）')
    if not a.no_record:
        print('  公開したら: python3 note_ledger.py posted %s --sections %s --url <note のURL>'
              % (slug, ','.join(str(k) for k in ledger_secs)))


if __name__ == '__main__':
    main()
