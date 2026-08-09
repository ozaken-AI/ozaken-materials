#!/usr/bin/env python3
"""資料と資料を、概念でつなぐ。

同じ概念が複数の資料に出てくる。そのままだと、資料ごとに少しずつ違う説明が
書かれてしまい、どれが正しいのか分からなくなる。

そこで概念ごとに「正典となる資料」を決め（crossref_data.py）、
他の資料からはそこへリンクを張る。リンクが張られていれば、
説明を書き直すときに「どこを直せば全体の整合が取れるか」が分かる。

  OZAKEN_PW=… python3 crossref.py map        # どの資料がどの概念に触れているか
  OZAKEN_PW=… python3 crossref.py check      # 整合を疑うべき箇所を洗い出す
  OZAKEN_PW=… python3 crossref.py preview    # どのセクションに何が並ぶかを見る
  OZAKEN_PW=… python3 crossref.py apply      # 重なるセクションの末尾にチップを挿入
  OZAKEN_PW=… python3 crossref.py matrix     # 資料×概念の一覧ページを作り直す
  OZAKEN_PW=… python3 crossref.py graph      # 資料間の辺をJSONで出す（マップ用）
"""
import datetime
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
from crossref_data import CONCEPTS, NOT_DOCS, STOP

PW = os.environ.get('OZAKEN_PW') or sys.exit('OZAKEN_PW を設定してください')
ROOT = registry.ROOT
MARK = '<!-- OZ-XREF v2 -->'
CSS_HEAD = '/* ══ 関連資料チップ'
CSS_END = '/* /OZ-XREFCSS */'


def text_of(html):
    t = re.sub(r'<script[\s\S]*?</script>|<style[\s\S]*?</style>', '', html)
    # 自分で入れたチップは数えない。資料名が概念語と重なるので、
    # 数えると「張ったから関係が強い」という循環になってしまう
    t = re.sub(r'<p class="xr-chips">[\s\S]*?</p>', '', t)
    return re.sub(r'\s+', ' ', H.unescape(re.sub(r'<[^>]+>', ' ', t)))


def scan():
    """資料 → 言及している概念、の対応を作る"""
    led = registry.load(PW)
    hits, titles, bodies = {}, {}, {}
    for f in registry.docs():
        rel = os.path.relpath(f, ROOT)
        if os.path.basename(f) in NOT_DOCS:
            continue                           # 置き場・索引のページは資料ではない
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


SECTION = re.compile(r'<section class="sec-(?:light|navy)"[^>]*>[\s\S]*?</section>')
TERM = re.compile(r'[ァ-ヴー]{3,}|[一-龥々]{2,}|[A-Za-z][A-Za-z0-9./+#-]{2,}')
# 語が広すぎても狭すぎても手がかりにならない。全68本のうち、
# 2〜14本に出てくる語だけを「その資料らしい語」として扱う
DF_LO, DF_HI = 2, 14
CHIP_MIN = 20.0                  # 概念で結びついたとき、これ未満は出さない
CHIP_LOOSE = 24.0                # 概念に頼らず、語の重なりだけで結ぶときの敷居
CHIP_MAX = 2                     # 1セクションに並べる上限。多いと本文が負ける


def terms_of(txt):
    c = defaultdict(int)
    for t in TERM.findall(txt):
        c[t] += 1
    return c


def relate(bodies):
    """資料ごとの語と、語の重み（珍しい語ほど重い）を用意する"""
    import math
    docs = {rel: terms_of(txt) for rel, txt in bodies.items()}
    df = defaultdict(int)
    for c in docs.values():
        for t in c:
            df[t] += 1
    n = len(docs)
    w = {t: math.log(n / d) for t, d in df.items() if DF_LO <= d <= DF_HI}
    return docs, w


def picks(rel, sec_txt, docs, w, titles):
    """このセクションと関係の深い資料を返す。

    人が決めた概念（CONCEPTS）は確かな手がかりなので低い敷居で通し、
    語の重なりだけで拾ったものは高い敷居を課す。
    後者はどうしても外れが混じるので、確信が持てるものだけを残す。
    """
    con, gen = defaultdict(float), defaultdict(float)

    for name, (canon, words, _) in CONCEPTS.items():
        if canon == rel or canon not in docs:
            continue
        hit = sum(sec_txt.count(x) for x in words if x not in STOP)
        if hit:
            con[canon] += 14.0 + 3.0 * min(hit, 4)

    for t, k in terms_of(sec_txt).items():
        weight = w.get(t)
        if not weight:
            continue
        for other, c in docs.items():
            if other == rel or c.get(t, 0) < 3:
                continue
            gen[other] += weight * min(k, 4)

    out = []
    for r in set(con) | set(gen):
        a, b = con.get(r, 0.0), gen.get(r, 0.0)
        if (a and a + b >= CHIP_MIN) or b >= CHIP_LOOSE:
            out.append((r, a + b))
    out.sort(key=lambda x: -x[1])
    return [r for r, _ in out[:CHIP_MAX]]


def chips(rel, rels, titles):
    if not rels:
        return ''
    depth = rel.count('/')
    items = []
    for r in rels:
        t = titles.get(r, r).split('─')[0].split('—')[0].strip() or r
        items.append('<a href="%s%s">%s</a>' % ('../' * depth, H.escape(r), H.escape(t[:26])))
    return ('\n      <p class="xr-chips"><span class="xr-lb">関連資料</span>%s</p>'
            % ''.join(items))


CSS = """
/* ══ 関連資料チップ（話が重なるセクションの末尾に小さく置く） ══ */
.xr-chips{display:flex;flex-wrap:wrap;align-items:center;gap:.4rem .5rem;
  margin-top:1.6rem;padding-top:1rem;border-top:1px solid rgba(46,84,150,.14)}
.xr-chips .xr-lb{font-family:var(--font-en);font-size:.62rem;font-weight:700;
  letter-spacing:.14em;color:var(--muted);margin-right:.2rem}
.xr-chips a{display:inline-block;padding:.24em .8em;border-radius:999px;
  font-size:.76rem;line-height:1.6;color:var(--azure);text-decoration:none;
  background:rgba(46,84,150,.07);border:1px solid rgba(46,84,150,.2);
  transition:background .2s ease,border-color .2s ease,color .2s ease}
.xr-chips a::after{content:" ↗";font-family:var(--font-en);font-size:.7em;opacity:.6}
.xr-chips a:hover{background:var(--azure);border-color:var(--azure);color:#fff}
.sec-navy .xr-chips{border-top-color:rgba(216,228,240,.18)}
.sec-navy .xr-chips .xr-lb{color:rgba(216,228,240,.6)}
.sec-navy .xr-chips a{color:var(--azure-pale);background:rgba(255,255,255,.07);
  border-color:rgba(216,228,240,.24)}
.sec-navy .xr-chips a:hover{background:#fff;border-color:#fff;color:var(--navy)}
/* /OZ-XREFCSS */
"""


def cmd_apply(hits, titles, bodies):
    """話が重なるセクションの末尾に、小さな関連資料チップを置く。

    資料の最後にまとめて並べても、そこまで送られることは少ない。
    「この話は、あの資料でも扱っている」を、その話をしている場所に置く。
    """
    docs, w = relate(bodies)
    done = skip = n_chip = 0
    for f in registry.docs():
        rel = os.path.relpath(f, ROOT)
        if os.path.basename(f) in NOT_DOCS:
            skip += 1
            continue
        html = lockbox.decrypt(f, PW)
        if MARK in html:
            skip += 1
            continue

        got = [0]

        def one(m):
            sec = m.group(0)
            if 'xr-chips' in sec:
                return sec
            rels = picks(rel, text_of(sec), docs, w, titles)
            c = chips(rel, rels, titles)
            if not c:
                return sec
            got[0] += len(rels)
            i = sec.rfind('</div>')          # .inner の閉じ。図版の入れ子より後ろ
            return sec[:i] + c + '\n    ' + sec[i:] if i > 0 else sec

        out = SECTION.sub(one, html)
        if not got[0]:
            skip += 1
            continue
        j = out.rfind('</style>')
        out = out[:j] + CSS + out[j:]
        k = out.rfind('</body>')
        out = out[:k] + MARK + '\n' + out[k:]
        lockbox.encrypt(f, PW, out)
        assert lockbox.decrypt(f, PW) == out
        n_chip += got[0]
        done += 1
    print('関連資料チップを挿入 %d 本 / 対象外・適用済み %d 本 ／ チップ %d 個'
          % (done, skip, n_chip))


def cmd_preview(hits, titles, bodies):
    """当てる前に、どのセクションに何が並ぶかを見る"""
    docs, w = relate(bodies)
    want = sys.argv[2] if len(sys.argv) > 2 else ''
    for f in registry.docs():
        rel = os.path.relpath(f, ROOT)
        if os.path.basename(f) in NOT_DOCS or (want and want not in rel):
            continue
        html = lockbox.decrypt(f, PW)
        print('\n■ %s' % titles.get(rel, rel)[:52])
        for m in SECTION.finditer(html):
            sec = m.group(0)
            h = re.search(r'<h2 class="sec-title">([\s\S]*?)</h2>', sec)
            head = re.sub(r'<[^>]+>', '', h.group(1)) if h else '(見出し無し)'
            rels = picks(rel, text_of(sec), docs, w, titles)
            print('   %-34s → %s' % (head[:34],
                  ' / '.join(titles.get(r, r)[:22] for r in rels) or '—'))


def edges_of(hits):
    """資料どうしの辺。同じ概念を厚く扱っているほど重い"""
    e = defaultdict(int)
    for rel, found in hits.items():
        for name, n in found:
            canon = CONCEPTS[name][0]
            if canon in hits:
                a, b = sorted([rel, canon])
                e[(a, b)] += n
    return sorted(((a, b, w) for (a, b), w in e.items() if w >= 3),
                  key=lambda t: -t[2])


def cmd_matrix(hits, titles, bodies):
    """資料マトリクスのページを作り直す。マスターと共通パスワードで開く"""
    import crossref_page
    led = registry.load(PW)
    common = led.get('_meta', {}).get('common') or ''

    rows = [(rel, titles[rel], dict(hits[rel])) for rel in sorted(hits)]
    ed = [(a, b, w, titles.get(a, a), titles.get(b, b)) for a, b, w in edges_of(hits)]
    page = crossref_page.build(rows, ed, datetime.date.today().isoformat())

    out = os.path.join(ROOT, 'matrix.html')
    if os.path.exists(out):
        # 鍵は作り直さない。配ってあるものが死ぬので
        lockbox.encrypt(out, PW, page)
    else:
        # **道具のページに共通鍵は付けない。** 共通パスワードは資料を配るためのもので、
        # 全資料の一覧が共通鍵で開くと、渡した相手にアーカイブの中身が全部見える
        lockbox.create(os.path.join(ROOT, 'backstage.html'), page, out, [PW])
    assert lockbox.decrypt(out, PW) == page
    print('資料マトリクスを更新しました（資料 %d 本 / 概念 %d 個 / つながり %d 本）'
          % (len(rows), len(CONCEPTS), len(ed)))


def cmd_graph(hits, titles, bodies):
    """資料どうしの辺を出す。星座マップで使う"""
    out = [{'a': a, 'b': b, 'w': w} for a, b, w in edges_of(hits)]
    print(json.dumps(out, ensure_ascii=False, indent=1))


def cmd_strip(hits, titles, bodies):
    """挿入したものを全部外す。作り直すとき用"""
    n = 0
    for f in registry.docs():
        html = lockbox.decrypt(f, PW)
        marks = [m for m in ('<!-- OZ-XREF v1 -->', MARK) if m in html]
        if not marks:
            continue
        # 末尾に付録を置いていた頃のもの（sec-light xref を名乗る版も含む）
        html = re.sub(r'\n<section class="(?:sec-light )?xref"[^>]*>[\s\S]*?</section>\n',
                      '', html)
        html = re.sub(r'\n\s*<p class="xr-chips">[\s\S]*?</p>', '', html)
        for head in ('/* ══ 関連する資料', '/* ══ 関連資料チップ'):
            i = html.find(head)
            if i >= 0:
                j = html.find('</style>', i)
                html = html[:i] + html[j:]
        for m in marks:
            html = html.replace(m + '\n', '').replace(m, '')
        lockbox.encrypt(f, PW, html)
        assert lockbox.decrypt(f, PW) == html
        n += 1
    print('付録を外した %d 本' % n)


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'map'
    fn = {'map': cmd_map, 'check': cmd_check, 'apply': cmd_apply,
           'preview': cmd_preview, 'matrix': cmd_matrix,
           'graph': cmd_graph, 'strip': cmd_strip}.get(cmd)
    if not fn:
        sys.exit(__doc__)
    fn(*scan())
