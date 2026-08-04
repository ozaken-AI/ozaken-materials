#!/usr/bin/env python3
"""資料と資料を、概念でつなぐ。

同じ概念が複数の資料に出てくる。そのままだと、資料ごとに少しずつ違う説明が
書かれてしまい、どれが正しいのか分からなくなる。

そこで概念ごとに「正典となる資料」を決め（crossref_data.py）、
他の資料からはそこへリンクを張る。リンクが張られていれば、
説明を書き直すときに「どこを直せば全体の整合が取れるか」が分かる。

  OZAKEN_PW=… python3 crossref.py map        # どの資料がどの概念に触れているか
  OZAKEN_PW=… python3 crossref.py check      # 整合を疑うべき箇所を洗い出す
  OZAKEN_PW=… python3 crossref.py apply      # 各資料の末尾に「関連する資料」を挿入
  OZAKEN_PW=… python3 crossref.py graph      # 資料間の辺をJSONで出す（マップ用）
"""
import html as H
import json
import os
import re
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lockbox
import registry
from crossref_data import CONCEPTS, STOP

PW = os.environ.get('OZAKEN_PW') or sys.exit('OZAKEN_PW を設定してください')
ROOT = registry.ROOT
MARK = '<!-- OZ-XREF v1 -->'
MAXLINK = 6                      # 1資料に並べる関連資料の上限


def text_of(html):
    t = re.sub(r'<script[\s\S]*?</script>|<style[\s\S]*?</style>', '', html)
    return re.sub(r'\s+', ' ', H.unescape(re.sub(r'<[^>]+>', ' ', t)))


def scan():
    """資料 → 言及している概念、の対応を作る"""
    led = registry.load(PW)
    hits, titles, bodies = {}, {}, {}
    for f in registry.docs():
        rel = os.path.relpath(f, ROOT)
        html = lockbox.decrypt(f, PW)
        txt = text_of(html)
        bodies[rel] = txt
        titles[rel] = (led.get(rel, {}).get('title') or rel).split('｜')[0].strip()
        found = []
        for name, (canon, words, _) in CONCEPTS.items():
            if rel == canon:
                continue                       # 自分が正典なら数えない
            n = sum(txt.count(w) for w in words if w not in STOP)
            if n:
                found.append((name, n))
        hits[rel] = sorted(found, key=lambda x: -x[1])
    return hits, titles, bodies


def cmd_map(hits, titles, bodies):
    used = defaultdict(list)
    for rel, found in hits.items():
        for name, n in found:
            used[name].append((rel, n))
    print('概念 %d 個 / 資料 %d 本\n' % (len(CONCEPTS), len(hits)))
    print('%-24s %s' % ('概念', '言及している資料'))
    print('-' * 62)
    for name, (canon, _, _) in CONCEPTS.items():
        rs = used.get(name, [])
        exists = os.path.exists(os.path.join(ROOT, canon))
        print('%-24s %2d本 %s' % (name, len(rs), '' if exists else '← 正典が見つからない'))
    print('\n言及が0本の概念（ほかの資料から参照されていない）')
    for name in CONCEPTS:
        if not used.get(name):
            print('  ' + name)


def cmd_check(hits, titles, bodies):
    """整合を疑うべき箇所を出す。判断は人がやる。ここは材料を並べるだけ"""
    print('■ 正典に触れずに、概念を厚く説明している資料')
    print('  （正典へのリンクを張るか、説明をそちらへ寄せるべき候補）\n')
    for rel, found in sorted(hits.items()):
        heavy = [(n, c) for n, c in found if c >= 8]
        if not heavy:
            continue
        print('  %s' % titles[rel][:46])
        for name, c in heavy[:4]:
            canon = CONCEPTS[name][0]
            print('      %-22s %2d回  → 正典: %s' % (name, c, canon))
    print('\n■ 同じ概念について、数字が資料ごとに違う可能性のある箇所')
    print('  （同じ概念の周辺に出る数値を並べる。食い違っていたら直す）\n')
    NUM = re.compile(r'[\d,]+(?:\.\d+)?\s*(?:%|％|円|ドル|\$|倍|本|件|人|社|割)')
    for name, (canon, words, _) in CONCEPTS.items():
        seen = defaultdict(set)
        for rel, txt in bodies.items():
            for w in words:
                if w in STOP:
                    continue
                for m in re.finditer(re.escape(w), txt):
                    around = txt[max(0, m.start() - 60):m.end() + 60]
                    for num in NUM.findall(around):
                        seen[num].add(rel)
        multi = {k: v for k, v in seen.items() if len(v) >= 2}
        if len(multi) >= 3:
            print('  %s' % name)
            for num, rs in sorted(multi.items(), key=lambda kv: -len(kv[1]))[:4]:
                print('      %-12s %d本の資料に出る' % (num, len(rs)))


def block(rel, found, titles):
    """末尾に差し込む「関連する資料」"""
    items = []
    for name, n in found[:MAXLINK]:
        canon, _, desc = CONCEPTS[name]
        if not os.path.exists(os.path.join(ROOT, canon)):
            continue
        depth = rel.count('/')
        href = ('../' * depth) + canon
        items.append(
            '      <li><a href="%s"><span class="xr-t">%s</span>'
            '<span class="xr-d">%s</span></a></li>'
            % (H.escape(href), H.escape(name), H.escape(desc)))
    if not items:
        return ''
    # 本文セクション（sec-light / sec-navy）としては数えない。
    # これは講演で話す面ではなく、資料の付録だから。
    # sec-* を名乗ると、奇数本・交互・末尾navy という並びの規約を壊してしまう
    return ('\n<section class="xref">\n  <div class="inner" data-reveal>\n'
            '    <span class="eyebrow">Related</span>\n'
            '    <h2 class="sec-title">この資料が触れた概念は、こちらで詳しく</h2>\n'
            '    <p class="sec-sub">同じ概念を別々に説明すると食い違うので、'
            '深掘りは正典となる資料に寄せている。</p>\n'
            '    <ul class="xr-list">\n%s\n    </ul>\n  </div>\n</section>\n'
            % '\n'.join(items))


CSS = """
/* ══ 関連する資料（付録。本文の面としては数えない） ══ */
.xref{padding:clamp(3rem,7vh,4.5rem) 1.5rem;
  background:linear-gradient(178deg,#eef3fa 0%,#e7eef8 100%);color:var(--ink);
  border-top:2px solid rgba(46,84,150,.16)}
.xref .eyebrow{color:var(--azure);background:var(--azure-pale)}
.xref .sec-title{font-family:var(--font-ja-serif);
  font-size:clamp(1.4rem,3.4vw,1.9rem);font-weight:500;line-height:1.4;margin-bottom:.6rem}
.xref .sec-sub{font-size:.94rem;color:var(--muted);margin-bottom:2rem;line-height:1.7}
.xr-list{list-style:none;margin:0;padding:0;display:grid;gap:.7rem;
  grid-template-columns:repeat(auto-fit,minmax(300px,1fr))}
.xr-list a{display:block;padding:1rem 1.2rem;border-radius:12px;
  background:var(--white);border:1px solid rgba(46,84,150,.18);
  transition:transform .2s ease,box-shadow .2s ease,border-color .2s ease}
.xr-list a:hover{transform:translateY(-2px);border-color:var(--azure);
  box-shadow:0 14px 30px -18px rgba(46,84,150,.5)}
.xr-list .xr-t{display:block;font-weight:700;color:var(--ink);margin-bottom:.2rem}
.xr-list .xr-t::after{content:" →";color:var(--azure);font-family:var(--font-en)}
.xr-list .xr-d{display:block;font-size:.8rem;line-height:1.7;color:var(--muted)}
"""


def cmd_apply(hits, titles, bodies):
    done = skip = 0
    for f in registry.docs():
        rel = os.path.relpath(f, ROOT)
        html = lockbox.decrypt(f, PW)
        if MARK in html:
            skip += 1
            continue
        b = block(rel, hits.get(rel, []), titles)
        if not b:
            skip += 1
            continue
        i = html.rfind('<footer>')
        if i < 0:
            skip += 1
            continue
        html = html[:i] + b + html[i:]
        j = html.rfind('</style>')
        html = html[:j] + CSS + html[j:]
        k = html.rfind('</body>')
        html = html[:k] + MARK + '\n' + html[k:]
        lockbox.encrypt(f, PW, html)
        assert lockbox.decrypt(f, PW) == html
        done += 1
    print('関連する資料を挿入 %d 本 / 対象外・適用済み %d 本' % (done, skip))


def cmd_graph(hits, titles, bodies):
    """資料どうしの辺を出す。星座マップで使う"""
    edges = defaultdict(int)
    for rel, found in hits.items():
        for name, n in found:
            canon = CONCEPTS[name][0]
            if canon in hits:
                a, b = sorted([rel, canon])
                edges[(a, b)] += n
    out = [{'a': a, 'b': b, 'w': w, 'concept': ''} for (a, b), w in edges.items() if w >= 3]
    print(json.dumps(out, ensure_ascii=False, indent=1))


def cmd_strip(hits, titles, bodies):
    """挿入した付録を全部外す。作り直すとき用"""
    n = 0
    for f in registry.docs():
        html = lockbox.decrypt(f, PW)
        if MARK not in html:
            continue
        # 旧版（sec-light xref）も含めて外す
        html = re.sub(r'\n<section class="(?:sec-light )?xref"[^>]*>[\s\S]*?</section>\n',
                      '', html)
        i = html.find('/* ══ 関連する資料')
        if i >= 0:
            j = html.find('</style>', i)
            html = html[:i] + html[j:]
        html = html.replace(MARK + '\n', '').replace(MARK, '')
        lockbox.encrypt(f, PW, html)
        assert lockbox.decrypt(f, PW) == html
        n += 1
    print('付録を外した %d 本' % n)


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'map'
    fn = {'map': cmd_map, 'check': cmd_check, 'apply': cmd_apply,
           'graph': cmd_graph, 'strip': cmd_strip}.get(cmd)
    if not fn:
        sys.exit(__doc__)
    fn(*scan())
