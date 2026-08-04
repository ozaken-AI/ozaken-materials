#!/usr/bin/env python3
"""全資料を、同じものさしで並べる。

資料が増えると「どれが弱いか」が分からなくなる。
1本ずつ見て回ると、見た順に印象が引きずられて、判断が揃わない。
だから機械で測れるところだけを先に測って、直す順番を決める。

  OZAKEN_PW=… python3 audit_all.py             # 弱い順に並べる
  OZAKEN_PW=… python3 audit_all.py --detail    # 資料ごとの内訳も出す
  OZAKEN_PW=… python3 audit_all.py --csv       # 表計算に貼れる形

ここで測れるのは「かたち」だけ。
メッセージが強いか、独自の見方があるかは測れないので、
ここで下位に来た資料から順に ozaken-hyoka スキルで人が見る。
"""
import html as H
import os
import re
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lockbox
import oz_root
import registry
from build_page import check_tokens
from crossref_data import NOT_DOCS

PW = os.environ.get('OZAKEN_PW') or sys.exit('OZAKEN_PW を設定してください')
ROOT = oz_root.root(HERE)
DETAIL = '--detail' in sys.argv
CSV = '--csv' in sys.argv

SECTION = re.compile(r'<section class="sec-(light|navy)"([^>]*)>([\s\S]*?)</section>')
RED = ('#e23744', '#ff5d6a', 'text-red', 'var(--red')
# 一般論の匂い。これだけで断じないが、多い資料は本文が薄い傾向がある
VAGUE = ('重要です', '重要性', '求められています', '注目されて', '期待されて',
         '課題となって', 'と言われて', '必要があります', 'ではないでしょうか')


def text_of(x):
    x = re.sub(r'<svg[\s\S]*?</svg>', ' ', x)
    return re.sub(r'\s+', ' ', H.unescape(re.sub(r'<[^>]+>', ' ', x))).strip()


def shape(svg):
    c = {t: len(re.findall(r'<%s[\s>]' % t, svg))
         for t in ('rect', 'circle', 'path', 'line', 'text')}
    k = []
    if c['rect'] >= 4:
        k.append('箱')
    if c['circle'] >= 3:
        k.append('丸')
    if c['path'] >= 3 or c['line'] >= 3:
        k.append('線')
    if 'marker-end' in svg:
        k.append('矢')
    return '+'.join(k) or '—'


def audit(rel, html):
    """減点方式。0が満点で、大きいほど直すところが多い"""
    bad, pts = [], 0
    secs = list(SECTION.finditer(html))
    if not secs:
        return 99, ['本文セクションが見つからない（構成が特殊）'], {}

    faces = [m.group(1) for m in secs]
    bodies = [m.group(3) for m in secs]
    lens = [len(text_of(b)) for b in bodies]
    figs = [len(re.findall(r'<svg[\s\S]*?</svg>', b)) for b in bodies]
    shapes = [' '.join(shape(s) for s in re.findall(r'<svg[\s\S]*?</svg>', b)) or '—'
              for b in bodies]

    # 1. 規定外の色・書体。見た目のばらつきの最大の原因
    tok = check_tokens(html)
    if tok:
        n = len(re.findall(r'#[0-9a-f]{3,6}', ' '.join(tok)))
        pts += min(n * 2, 14)
        bad.append('規定外の色・書体 %d 種' % n)

    # 2. 図版が無い面。投影すると文字の壁になる
    nofig = [i + 1 for i, n in enumerate(figs) if n == 0]
    if nofig:
        # 締めの1本は図が無くてもよい
        real = [i for i in nofig if i != len(secs)]
        if real:
            pts += len(real) * 4
            bad.append('図版が無い面 %s' % real)

    # 3. 同じかたちの図が続く。送っても景色が変わらない
    run = best = 1
    for i in range(1, len(shapes)):
        run = run + 1 if shapes[i] == shapes[i - 1] and shapes[i] != '—' else 1
        best = max(best, run)
    if best >= 3:
        pts += (best - 2) * 3
        bad.append('同じかたちの図が %d 面続く' % best)

    # 4. かたちの偏り
    c = Counter(s for s in shapes if s != '—')
    if c:
        top, n = c.most_common(1)[0]
        if len(secs) >= 5 and n >= len(secs) * 0.6:
            pts += 4
            bad.append('図の %d/%d が「%s」に寄っている' % (n, len(secs), top))

    # 5. 文字量の偏り
    if lens and min(lens) and max(lens) / max(min(lens), 1) >= 4:
        pts += 3
        bad.append('文字量の差が %.1f 倍' % (max(lens) / max(min(lens), 1)))

    # 6. 赤の撒きすぎ
    red = sum(sum(b.count(r) for r in RED) for b in bodies)
    if red > len(secs) * 1.6:
        pts += 3
        bad.append('赤が %d 箇所（面は %d）' % (red, len(secs)))

    # 7. 一般論の匂い
    whole = text_of(html)
    vague = sum(whole.count(v) for v in VAGUE)
    if vague >= 6:
        pts += min((vague - 4), 6)
        bad.append('一般論めいた言い回し %d 箇所' % vague)

    # 8. 締めが要約になっていないか（「以上」「まとめ」で始まる締め）
    if re.search(r'(以上、|まとめると|本資料では)', text_of(bodies[-1])):
        pts += 3
        bad.append('締めが要約になっている')

    # 9. 見出しが体言止めばかり
    heads = [re.search(r'<h2 class="sec-title">([\s\S]*?)</h2>', b) for b in bodies]
    heads = [text_of(h.group(1)) for h in heads if h]
    taigen = sum(1 for h in heads if not re.search(r'[るいたずぬんかよねだ]$|。|\?|？', h))
    if heads and taigen >= len(heads) * 0.6:
        pts += 3
        bad.append('見出しの %d/%d が体言止め' % (taigen, len(heads)))

    # 10. 関連資料チップが無い＝アーカイブから孤立
    if 'xr-chips"' not in html:
        pts += 2
        bad.append('関連資料チップが無い')

    return pts, bad, {'secs': len(secs), 'figs': sum(figs),
                      'chars': sum(lens), 'red': red}


def main():
    led = registry.load(PW)
    rows = []
    for f in registry.docs():
        rel = os.path.relpath(f, ROOT)
        if os.path.basename(f) in NOT_DOCS:
            continue
        html = lockbox.decrypt(f, PW)
        pts, bad, st = audit(rel, html)
        title = (led.get(rel, {}).get('title') or rel).split('｜')[0].strip()
        rows.append((pts, rel, title, bad, st))
    rows.sort(key=lambda r: -r[0])

    if CSV:
        print('点,パス,題名,指摘')
        for pts, rel, title, bad, st in rows:
            print('%d,"%s","%s","%s"' % (pts, rel, title, ' / '.join(bad)))
        return

    print('資料 %d 本を、直すところが多い順に並べた\n' % len(rows))
    print('%-4s %-46s %s' % ('点', '資料', '内訳'))
    print('-' * 100)
    for pts, rel, title, bad, st in rows:
        print('%-4d %-46s %s' % (pts, title[:44], '面%d 図%d 字%d' %
                                 (st.get('secs', 0), st.get('figs', 0), st.get('chars', 0))))
        if DETAIL or pts >= 8:
            for b in bad:
                print('     ・%s' % b)
    n_bad = sum(1 for r in rows if r[0] >= 8)
    print('\n手当てが要る（8点以上） %d 本 / 軽微（1〜7点） %d 本 / 無傷 %d 本'
          % (n_bad, sum(1 for r in rows if 0 < r[0] < 8),
             sum(1 for r in rows if r[0] == 0)))
    print('\n※ ここで測れるのは「かたち」だけ。')
    print('  メッセージの強さと独自の視点は測れないので、上から順に人が見る。')


if __name__ == '__main__':
    main()
