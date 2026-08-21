#!/usr/bin/env python3
"""濃い面の図版のうち、**暗い地の上に描かれたもの**に印を付ける。

いまの規約では、図版の箱は濃い面の上でも白い。だから図の中身は
常に明るい組み（濃い字・薄い塗り）で描く。`domain_fig` は
`_always_light` で dark= を捨てているので、これから作る資料は必ずそうなる。

ところが**手で組んだ古い資料の図版は、暗い地の上に白い字で描かれている**。
そこへ「箱は白」を一律に当てると、白い箱に白い字が乗って図が消える。
実際、暗黙知の資料の Fig.2 は、木構造の枝も見出しもほとんど読めなくなった。

そこで、濃い面の図版のSVGを見て、
**白や淡い青で字を描いているもの**が入っている面に `data-figdark="1"` を付ける。
`normalize_style.py` の塊は、この印が無い面にだけ白い箱を当てる。

  ・印がある面 …… 箱は従来どおり濃いまま。図はそのまま読める
  ・印が無い面 …… 箱が白になり、いまの規約の見た目になる

**古い図を描き直すまでの橋渡しであって、直したことにはならない。**
生成元から作り直せる資料は、`publish.py --update` で通したほうがよい。

  OZAKEN_PW=マスター python3 mark_figdark.py         # 印を付け直す（冪等）
  OZAKEN_PW=マスター python3 mark_figdark.py list    # どの資料に付くかを見るだけ
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lockbox
import oz_root
import registry

ROOT = oz_root.root(HERE)

# 暗い地の上に置くために使われる字の色。
#
# **真っ白（#ffffff）は目印にならない。** 明るい組みの図でも、
# 紺で塗った帯の中の字は白で描く（「ここまで揃って、はじめて…」の帯など）。
# 実際これを目印にすると、いま作ったばかりの資料まで暗い組みと判定された。
#
# 目印になるのは**半透明の白と淡い青**のほう。これは暗い地の上でだけ使う、
# 補足や副題の色で、明るい組みの図には出てこない。
#
# **同じ色でも、書き方が2通りある。** 以前は淡い青を #d8e4f0 の形でしか
# 見ていなかったが、手で組んだ古い図は半透明にするために
# rgba(216,228,240,0.5) と書いている。同じ色なのに拾えず、
# コンテキストの資料の Fig.4 は白い箱に白い字が乗って中身が消えていた。
# 16進と rgba の両方を見る。
LIGHT_INK = re.compile(
    r'fill="(?:rgba\(\s*255,\s*255,\s*255\s*,'          # 半透明の白
    r'|rgba\(\s*216,\s*228,\s*240\s*,'                   # 淡い青（#d8e4f0）
    r'|rgba\(\s*159,\s*198,\s*245\s*,'                   # 明るい青（#9fc6f5）
    r'|#d8e4f0|#8fb0e0|#9fc6f5)', re.I)

SEC = re.compile(r'<section class="sec-navy"([^>]*)>')


def figs_are_dark(section_html):
    """その面の図版が、暗い地の上に描かれているか"""
    for fig in re.finditer(r'<div class="figure"[\s\S]*?</div>\s*(?=<)', section_html):
        for svg in re.finditer(r'<svg[\s\S]*?</svg>', fig.group(0)):
            for t in re.finditer(r'<text[^>]*>', svg.group(0)):
                if LIGHT_INK.search(t.group(0)):
                    return True
    return False


def patch(html):
    """濃い面を順に見て、印を付け直す。既にある印はいったん外す"""
    html = html.replace(' data-figdark="1"', '')
    out, pos, hit = [], 0, 0
    for m in SEC.finditer(html):
        end = html.find('<section', m.end())
        body = html[m.end():end if end > 0 else len(html)]
        out.append(html[pos:m.start()])
        if figs_are_dark(body):
            out.append('<section class="sec-navy" data-figdark="1"%s>' % m.group(1))
            hit += 1
        else:
            out.append(m.group(0))
        pos = m.end()
    out.append(html[pos:])
    return ''.join(out), hit


def main():
    pw = os.environ.get('OZAKEN_PW') or sys.exit('OZAKEN_PW を設定してください')
    show = len(sys.argv) > 1 and sys.argv[1] == 'list'
    n = m = 0
    for f in registry.docs():
        rel = os.path.relpath(f, ROOT)
        h = lockbox.decrypt(f, pw)
        new, hit = patch(h)
        if hit:
            print('  %-52s 濃い面 %d 枚' % (rel, hit))
            m += 1
        if show or new == h:
            continue
        lockbox.encrypt(f, pw, new)
        assert lockbox.decrypt(f, pw) == new
        n += 1
    print('印が付く資料 %d 本 / 書き換えた資料 %d 本' % (m, n))


if __name__ == '__main__':
    main()
