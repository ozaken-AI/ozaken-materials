#!/usr/bin/env python3
"""資料の一番上と一番下に、トップページへ戻る動線を置く。

**資料は、単体で共有される。**
登壇のあとに1本のURLだけを渡すことが多く、受け取った人は
その資料しか知らないまま読み終える。ほかにも並んでいることも、
誰が書いたものかも、そこからは辿れない。

だから、扉の左上と、締めの直後の2か所に置く。
上は「いま何を開いているのか」の名札で、下は「読み終わったあとの行き先」。
役割が違うので、見た目も分けてある。

  OZAKEN_PW=… python3 apply_home.py            # まだ入っていない資料に入れる
  OZAKEN_PW=… python3 apply_home.py refresh    # 剥がして、いまの版を入れ直す
  OZAKEN_PW=… python3 apply_home.py strip      # 剥がす

行き先は **/index.html**（サイトの根から）。
資料は 09_role/ の下にも AX_Table/ の下にも、根の直下にもある。
`../index.html` と書くと根の直下の資料が親を辿ってしまい、
実際に template.html のフッターが行き止まりになっていた。
"""
import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lockbox
import oz_root

ROOT = oz_root.root(HERE)
HOME = '/index.html'

MARK = '/* /OZ-HOME */'
HEAD = '/* ══ OZ-HOME v3'
HEAD_ANY = '/* ══ OZ-HOME v'

CSS = """
/* ══ OZ-HOME v3 ── 資料からトップページへの動線 ══════════════
   上は扉に置く戻りボタン。下は締めのあとに置く行き先。 */
/* 左上には、herofx が入れる稼働バッジ（OZAKEN CMS）がもう居る。
   同じ高さに置くと重なるので、その1段下に、同じ左の軸で置く。
   扉は左そろえなので、名札・題・署名が同じ縦線から始まる。

   **絶対配置ではなく、バッジと同じくフローの2段目に置く。**
   以前は position:absolute で、バッジの下の高さを指定するだけの
   決め打ちだった。扉の中身（.inner）はバッジとこの名札の存在を知らずに
   縦中央寄せされていたので、タイトルが短い・ウィンドウが低いなどで
   中央寄せの結果がここまで浮き上がると、扉のeyebrow（節ラベル）と
   文字が重なっていた。ノートPCの高さでは珍しくなかった。
   flexアイテムにしておけば、.inner はバッジとこの名札を除いた
   残りの領域でしか中央寄せされないので、重なりが構造的に起きない */
/* **名札ではなく、押せるボタンとして置く。**
   v2 までは細い罫線1本と薄い字だけだったので、
   「いま何を開いているか」の表示に見えて、**押せることに気づかれなかった**。
   輪郭と矢印を付け、字を白にして、一目で戻り口だと分かる形にする。
   それでも扉の主役は題字なので、地は控えめな青のままにしてある */
.oz-home{position:relative;z-index:4;align-self:flex-start;flex:0 0 auto;
  margin:.85rem 0 0 1.6rem;
  display:inline-flex;align-items:center;gap:.5rem;
  padding:.5em 1.1em .5em .9em;border-radius:999px;
  background:rgba(46,84,150,.42);border:1px solid rgba(159,198,245,.5);
  backdrop-filter:blur(6px);-webkit-backdrop-filter:blur(6px);
  font-family:var(--font-ja-sans);font-weight:600;font-size:.8rem;
  letter-spacing:.04em;color:#ffffff;text-decoration:none;white-space:nowrap;
  transition:background .25s ease,border-color .25s ease,box-shadow .25s ease}
/* 矢印は文字で置く。締めのカードの「→」と同じ扱い */
.oz-home::before{content:'←';font-family:var(--font-en);font-weight:700;
  font-size:1em;line-height:1;transition:transform .25s ease}
.oz-home:hover{background:rgba(46,84,150,.72);border-color:#9fc6f5;
  box-shadow:0 8px 22px -12px rgba(10,15,28,.8)}
.oz-home:hover::before{transform:translateX(-3px)}
.oz-home:focus-visible{outline:2px solid #9fc6f5;outline-offset:3px}
@media (max-width:640px){
  .oz-home{margin:.65rem 0 0 1.05rem;font-size:.74rem;gap:.4rem;
    padding:.45em .95em .45em .8em}
}

/* 扉を持たないページ（記事の体裁・一覧・ダッシュボード）には、
   重ねる先が無い。いちばん上に細い帯として置く。
   これらのページは自前のCSSを持っていて、変数が揃っているとは限らないので、
   色は変数に頼らず、規定の色そのままで書く */
:root{--oz-bar-h:3.6rem}
.oz-homebar{position:relative;z-index:120;background:#141d35;padding:0 1.5rem;
  min-height:var(--oz-bar-h);display:flex;align-items:center}
/* 帯の中では横並びなので、上端そろえ（扉の縦並び用）を打ち消して中央へ */
.oz-homebar .oz-home{position:static;margin:0;align-self:center}
/* 記事のページは、自前の固定ヘッダーを持っている。
   帯を上に置くと、そのヘッダーが帯の下に潜って題字と重なるので、
   帯のぶんだけ下げる。帯を持つページだけに効く書き方にしてある。
   **下げ幅は帯の高さと同じ変数で持つ。** 別々の数字にしていたので、
   ボタンを大きくしたときに下げ幅だけ古いままずれていた */
body:has(> .oz-homebar) > header{top:var(--oz-bar-h)}
@media (max-width:640px){:root{--oz-bar-h:3.3rem}.oz-homebar{padding:0 1rem}}

/* 締めの直後。フッターと地続きの濃い面に、行き先を1つだけ置く */
.oz-return{background:var(--navy-deep);padding:3.4rem 1.5rem}
.oz-return-link{display:block;max-width:var(--max-w);margin:0 auto;
  padding:1.9rem 2rem;border:1px solid rgba(216,228,240,.16);border-radius:10px;
  transition:border-color .25s ease,background .25s ease}
.oz-return-link:hover{border-color:rgba(216,228,240,.34);
  background:rgba(216,228,240,.04)}
.oz-return-eb{display:block;font-family:var(--font-en);font-size:.66rem;
  font-weight:600;letter-spacing:.18em;text-transform:uppercase;
  color:rgba(216,228,240,.5)}
.oz-return-ttl{display:block;margin:.55rem 0 .4rem;
  font-family:var(--font-ja-serif);font-weight:600;
  font-size:clamp(1.05rem,2.4vw,1.3rem);line-height:1.55;color:#ffffff}
.oz-return-ttl::after{content:' →';font-family:var(--font-en);
  color:rgba(216,228,240,.55)}
.oz-return-sub{display:block;font-size:.82rem;line-height:1.8;
  color:rgba(216,228,240,.55)}
@media (max-width:640px){
  .oz-return{padding:2.6rem 1rem}
  .oz-return-link{padding:1.4rem 1.2rem}
}
/* /OZ-HOME */
"""

# 文言は「AI資料アーカイブ」から「AI資料アーカイブに戻る」へ。
# 名前だけだと、いま開いているものの表示に読める。フッターの言い方に揃えた
TOP = ('<a class="oz-home" href="%s">AI資料アーカイブに戻る</a>\n' % HOME)

BAR = ('<div class="oz-homebar">'
       '<a class="oz-home" href="%s">AI資料アーカイブに戻る</a></div>\n'
       % HOME)

BOTTOM = """<div class="oz-return">
  <a class="oz-return-link" href="%s">
    <span class="oz-return-eb">Ozaken Archive</span>
    <span class="oz-return-ttl">ほかの資料も、ここに並んでいます</span>
    <span class="oz-return-sub">生成AIとAX（AI Transformation）の解説資料が、分野ごとに置いてあります。content.ozaken.ai</span>
  </a>
</div>
""" % HOME

FOOTER = ('<footer>\n  <p>&copy; 2026 小澤健祐（おざけん）/ 一般社団法人AICX協会 '
          '&nbsp;｜&nbsp; <a href="%s">← AI資料アーカイブに戻る</a></p>\n</footer>\n' % HOME)


def strip(html):
    """入れ直せるようにしておく。

    **印があるだけで諦める作りにすると、直した版が二度と既存資料に届かない。**
    ファーストビューの演出で実際にそうなっていた。
    """
    i = html.find(HEAD_ANY)
    if i >= 0:
        j = html.find(MARK, i)
        if j >= 0:
            html = html[:i] + html[j + len(MARK) + 1:]
    html = re.sub(r'<div class="oz-homebar">[\s\S]*?</div>\n?', '', html)
    html = re.sub(r'[ \t]*<a class="oz-home"[\s\S]*?</a>\n?', '', html)
    html = re.sub(r'<div class="oz-return">[\s\S]*?</div>\n?', '', html)
    return html


def patch(html):
    if MARK in html:
        return None
    html = strip(html)

    # 本文の中にも「← AI資料アーカイブに戻る」を持っている資料がある。
    # 行き先がばらばらだと、置き場所を変えた資料だけが行き止まりになるので、
    # ページの中の玄関への行き先は、ここで1つに揃える
    html = re.sub(r'href="(?:\.\./)?index\.html"', 'href="%s"' % HOME, html)

    # ── 上 ── 扉に重ねる。扉は position:relative なので、そのまま浮く
    m = re.search(r'<section class="hero"[^>]*>\n?', html)
    if m:
        html = html[:m.end()] + TOP + html[m.end():]
    else:
        # 扉を持たないページには、重ねる先が無い。帯として最初に置く
        b = re.search(r'<body[^>]*>\n?', html)
        if b:
            html = html[:b.end()] + BAR + html[b.end():]

    # ── 下 ── 締めのあと、フッターの手前。
    # フッターは資料によって行き先が違っていた（無い資料が20本あり、
    # 根の直下の資料は ../index.html で行き止まりだった）ので、丸ごと揃える
    if re.search(r'<footer[\s\S]*?</footer>\s*', html):
        html = re.sub(r'<footer[\s\S]*?</footer>\s*', BOTTOM + FOOTER, html, count=1)
    else:
        i = html.rfind('</body>')
        if i < 0:
            return None
        html = html[:i] + BOTTOM + FOOTER + html[i:]

    i = html.rfind('</style>')
    if i < 0:
        return None
    return html[:i] + CSS + html[i:]


def targets():
    for d in sorted(glob.glob(os.path.join(ROOT, '[0-9][0-9]_*'))):
        for f in sorted(glob.glob(os.path.join(d, '*.html'))):
            yield f
    for d in oz_root.BACKSTAGE_DIRS:
        for f in sorted(glob.glob(os.path.join(ROOT, d, '*.html'))):
            yield f
    for f in sorted(glob.glob(os.path.join(ROOT, '*.html'))):
        # 玄関と質問箱は自前で持っている。道具のページは資料ではない
        if os.path.basename(f) not in ('index.html', 'ask.html',
                                       'passwords.html', 'backstage.html',
                                       'matrix.html', 'console.html',
                                       'inbox.html', 'stage.html',
                                       '404.html'):
            yield f


def main():
    pw = os.environ.get('OZAKEN_PW') or sys.exit('OZAKEN_PW を設定してください')
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'apply'
    off = cmd == 'strip'
    done = skip = nohero = 0
    for f in targets():
        raw = open(f, encoding='utf-8').read()
        enc = 'OZAKEN-LOCKED2' in raw
        inner = lockbox.decrypt(f, pw) if enc else raw
        # refresh は、入っている版を剥がしてから入れ直す。
        # 印があるだけで諦める作りだと、直した版が既存資料に届かない
        new = strip(inner) if off else patch(strip(inner) if cmd == 'refresh' else inner)
        if new is None or new == inner:
            skip += 1
            continue
        if not off and '<a class="oz-home"' not in new:
            nohero += 1        # 扉を持たないページ。下だけ入る
        if enc:
            lockbox.encrypt(f, pw, new)
            assert lockbox.decrypt(f, pw) == new
        else:
            open(f, 'w', encoding='utf-8').write(new)
        done += 1
    print('%s: %d 本／据え置き %d 本' % ('剥がした' if off else '入れた', done, skip))
    if nohero:
        print('扉が無く、下だけ入れた資料: %d 本' % nohero)


if __name__ == '__main__':
    main()
