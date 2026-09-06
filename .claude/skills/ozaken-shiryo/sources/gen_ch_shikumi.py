#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""コンテキスト＆ハーネスエンジニアリング（04_practice/context-harness-engineering.html）を、
「仕組みづくり」を主題にした形に組み替える。

  cd .claude/skills/ozaken-shiryo/sources
  OZAKEN_PW=マスター python3 gen_ch_shikumi.py
  cd ../scripts
  OZAKEN_PW=マスター python3 publish.py /tmp/body_ch.html \\
      04_practice/context-harness-engineering.html --update
  OZAKEN_PW=マスター python3 crossref.py apply

**変えるのは背骨で、中身ではない。** 元の資料はすでに正本・台帳・虎の巻・周期・承認と、
仕組みの部品を全部持っている。ただ、表紙と締めが「設計力」と言っていたので、
個人のスキルの話に読めた。表紙・導入・各章の見出し・締めを「仕組みづくり」で貫き、
第1章の直後に「仕組みの全体像」と「仕組みになっているかを見分ける問い」の2面を足す。

**面は2つ足す。** 本文の面は奇数本という規約なので、1面では締めの直前で紺が続く。
全体像（明）と診断（紺）を対で入れる。図版番号は、挿入位置より後ろを +2 する。

**何度流しても同じ結果になる。** 前回入れた2面は eyebrow で見分けて先に落とす。
見出しの差し替えは「元の文 → 新しい文」の対で持ち、元の文が無ければ（すでに
差し替え済みなら）何もしない。
"""
import io
import os
import re
import sys

S = '/home/user/ozaken-materials/.claude/skills/ozaken-shiryo/scripts'
ROOT = '/home/user/ozaken-materials'
sys.path.insert(0, S)
import lockbox
from page_parts import sec, cards
from domain_fig import fig_flow, fig_check

DOC = '04_practice/context-harness-engineering.html'
MINE = 'この整理は小澤健祐によるもの'
NEW = ('Chapter 1.5 ─ The System', 'Chapter 1.6 ─ Is It a System Yet')

TITLE = 'コンテキスト＆ハーネスエンジニアリング ─ 個人の腕ではなく、仕組みをつくる'
DESC = ('コンテキストエンジニアリングとハーネスエンジニアリングを、「仕組みづくり」として図解。'
        'プロンプト→コンテキスト→ハーネスの変遷、正本・台帳・虎の巻・周期・承認がつながる仕組みの全体像、'
        '仕組みになっているかを見分ける6つの問い、コンテキスト4種と5レイヤー、ハーネス4部品、'
        '台帳を見て動く半自律エージェント、現場と情シスの協働までを解説。')

HERO_H1 = ('<h1 class="hero-title">コンテキスト＆ハーネスエンジニアリング<br>'
           '個人の腕ではなく、<span class="hl">仕組み</span>をつくる</h1>')
HERO_COPY = ('<p class="hero-copy">「うまいプロンプト」を書く時代は終わりました。'
             '同じモデルでも、渡す文脈と動かす環境で成果は10倍変わります。'
             'それは個人の腕ではなく、仕組みの話です。'
             'AIを組織の戦力にする仕組みづくりを、2つの技術で解きほぐします。</p>')

# 見出しと導入の差し替え。左が元の文、右が新しい文
SWAPS = [
    ('<h2 class="sec-title">脱プロンプト時代へ</h2>',
     '<h2 class="sec-title">脱プロンプト ── 磨く対象が、文章から仕組みへ移った</h2>'),
    ('エージェント時代の中核能力は、ここにある。</p>',
     'これは、個人の腕から組織の仕組みへの移り変わりでもある。</p>'),
    ('<h2 class="sec-title">コンテキストエンジニアリングとは</h2>',
     '<h2 class="sec-title">コンテキストエンジニアリング ── 前提を「そろえる」仕組み</h2>'),
    ('<h2 class="sec-title">ハーネスエンジニアリングとは</h2>',
     '<h2 class="sec-title">ハーネスエンジニアリング ── AIを「動かす」仕組み</h2>'),
    ('<p class="sec-sub">2つの技術は、担い手が違う。分担と協働の設計そのものが、成否を分ける。</p>',
     '<p class="sec-sub">仕組みは、一人では作れない。現場と情シスの分担そのものが、仕組みの一部だ。</p>'),
    ('<h2 class="sec-title">差を生むのは、モデルではなく「設計力」</h2>',
     '<h2 class="sec-title">差を生むのは、モデルではなく「仕組み」</h2>'),
    ('<p class="kicker">同じClaude / GPTでも、コンテキストとハーネスの設計で成果は数倍〜10倍変わる。'
     '<span class="fw-bold">"AIを信じる"のではなく、"AIに渡す情報と、動かす環境を整える"</span>。'
     'プロンプトの先にある、この2つの設計力こそが、エージェント時代の組織の競争力になる。</p>',
     '<p class="kicker">同じClaude / GPTでも、コンテキストとハーネスの仕組みで成果は数倍〜10倍変わる。'
     'プロンプトを磨くのは、個人の腕。'
     '<span class="fw-bold">正本を決め、台帳で回し、周期で書き直し、承認を人に返す。'
     'この仕組みをつくった組織だけが、AIを戦力にできる。</span>'
     '"AIを信じる"のではなく、"渡す情報と動かす環境を、仕組みで整える"。'
     '<span class="fw-bold text-red">プロンプトの先にあるのは、設計力という個人の技ではなく、'
     '仕組みづくりだ。</span></p>'),
]


def system_face():
    return sec('sec-light', NEW[0],
        '仕組みづくりの全体像 ── 5つの段が、1本につながる',
        'この資料で扱うのは、個人の腕ではなく、人が変わっても回る仕組みです。',
        lede='コンテキストもハーネスも、突き詰めれば'
             '<span class="fw-bold">同じ1つの仕組みの、前半と後半</span>です。'
             '正本を1つに決め、台帳に載せ、チームの前提を虎の巻にまとめる。ここまでがコンテキストの仕組み。'
             '周期が来たらエージェントが書き直し、人が承認する。ここからがハーネスの仕組み。'
             '<span class="fw-bold text-azure">プロンプトを磨いても、この5段のどこかが欠けていれば、'
             '成果は個人の腕に戻ります。</span>',
        fig=fig_flow([
            ('正本を決める', '正しい版を1つに'),
            ('台帳に載せる', '所在と担当と周期'),
            ('虎の巻にする', '前提を1枚に'),
            ('周期で更新', '鮮度を周期で守る'),
            ('人が承認する', '戻せる形で公開'),
        ], 'Fig.3 ── 5段で1つの仕組み。前の3段がコンテキスト、後の2段がハーネス', MINE,
           uid='chsys',
           note='以降の章は、この順に進む。どこから読んでも、いま自分の組織で欠けている段が見つかる'),
        body=cards([
            ('<span class="mth">個人技</span>個人の腕は、その人と一緒に異動します',
             'プロンプトが上手い人の成果は、その人のチャット履歴の中にあります。'
             '<b>異動した日に、組織の成果はゼロに戻る</b>。'
             'どれだけ上手くても、それは仕組みではありません。'),
            ('<span class="mth">仕組み</span>仕組みとは、人が変わっても回る状態のことです',
             '印は3つ。<b>担当者が休んでもAIが正本を読める。'
             '鮮度を意志ではなく周期が守っている。任せる範囲が列で決まっている</b>。'
             '3つそろって、はじめて仕組みと呼べます。'),
            ('<span class="mth">読み方</span>この資料は、5段の順に進みます',
             '第2〜3章が正本・台帳・虎の巻、第4章以降が周期と承認です。'
             '<b>次の面の6つの問いで、自分の組織の欠けている段を先に見つけてから</b>読むと、'
             '読む場所が決まります。'),
        ]))


def check_face():
    return sec('sec-navy', NEW[1],
        '「仕組みになっているか」を見分ける、6つの問い',
        '「詳しい人に聞けば分かる」は、仕組みではありません。',
        cattr=' data-figdark="1"',
        lede='「うちはもう仕組み化できている」と言う組織ほど、聞いてみると'
             '<span class="fw-bold">特定の人の頭の中で回っている</span>ことがあります。'
             '仕組みかどうかは、気持ちではなく問いで見分けられます。'
             '<span class="fw-bold text-azure">6つのうち1つでも外れていれば、'
             'その段からが、この資料の読みどころです。</span>',
        fig=fig_check([
            (True, '担当者が休んだ日も、AIは正本を読めるか',
             '正本がURLで一意に指せる場所にあり、個人のPCやメール添付の中にない'),
            (True, '更新の周期が、人の意志ではなく台帳に書いてあるか',
             '「気づいた人が直す」は周期ではない。列に書かれた周期だけが守られる'),
            (True, '新人に最初に渡す文書と、AIに最初に渡す文書が同じか',
             '虎の巻が両方に効いていれば仕組み。別々なら、どちらかが古くなっている'),
            (True, '任せる範囲と、人に返す範囲が、列で決まっているか',
             '判断基準は人が書き、進捗はエージェントが書く。境界が文章ではなく列にある'),
            (False, 'プロンプト集を配って、仕組み化と呼んでいる',
             '配った瞬間から古くなる。更新の担当と周期がなければ、それは資料集'),
            (False, '「詳しい人に聞けば分かる」を、仕組みと呼んでいる',
             'その人が異動した日に、組織の記憶は消える。属人化の別の名前'),
        ], 'Fig.4 ── 4つの問いに○、2つの習慣に×が付けば、仕組みになっている', MINE,
           note='×が付いた段から読み始める。上の段から直す。飛ばすと、下の段が持たない'),
        body=cards([
            ('<span class="mth">診断</span>外れた問いの段から、読み始めてください',
             '正本で外れたなら第2章、周期で外れたなら第4章です。'
             '<b>全部を最初から整えようとすると、どれも中途半端で止まります</b>。'
             '外れた段を1つ直すだけで、AIの出力は目に見えて変わります。'),
            ('<span class="mth">順番</span>上の段から直します。飛ばすと、下が持ちません',
             '正本が決まっていないのに台帳を作っても、台帳が嘘を並べます。'
             '<b>周期を決める前に、何を回すかが決まっている必要があります</b>。'
             '5段の順番は、そのまま直す順番です。'),
            ('<span class="mth">経営</span>仕組みづくりは、情シスだけの仕事ではありません',
             '正本を決めるのも、周期を決めるのも、業務を知る側の判断です。'
             '<b>情シスは、その判断を回る形にする側</b>。'
             '誰が何を持つかは、第5章の分担で扱います。'),
        ]))


def main():
    pw = os.environ.get('OZAKEN_PW') or sys.exit('OZAKEN_PW を設定してください')
    page = lockbox.decrypt(os.path.join(ROOT, DOC), pw)
    i0 = page.index('<section class="hero">')
    i1 = page.index('<div class="oz-return">')
    body = page[i0:i1]
    spans = [m.start() for m in re.finditer(r'<section[^>]*>', body)]
    spans.append(len(body))
    parts = [body[spans[i]:spans[i + 1]] for i in range(len(spans) - 1)]
    hero, close, mid = parts[0], parts[-1], parts[1:-1]

    mid = [s for s in mid if not any(e in s for e in NEW)]
    if len(mid) != 13:
        sys.exit('外したあとの面の数が想定と違います: %d' % len(mid))

    # 表紙
    hero = re.sub(r'<h1 class="hero-title">.*?</h1>', HERO_H1, hero, flags=re.S)
    hero = re.sub(r'<p class="hero-copy">.*?</p>', HERO_COPY, hero, flags=re.S)

    # 見出しと導入の差し替え（無ければ何もしない）
    def swap(s):
        for a, b in SWAPS:
            s = s.replace(a, b)
        return s
    mid = [swap(s) for s in mid]
    close = swap(close)

    at = next(i for i, s in enumerate(mid) if '>Chapter 1 ─ The Shift<' in s) + 1
    later = [re.sub(r'Fig\.(\d+)', lambda m: 'Fig.%d' % (int(m.group(1)) + 2), s)
             for s in mid[at:]]
    mid = mid[:at] + [system_face(), check_face()] + later

    out = []
    for s in [hero] + mid + [close]:
        s = re.sub(r'\s+data-bg="\d+"', '', s)
        s = re.sub(r'\n?<a class="oz-home"[^>]*>.*?</a>', '', s)
        s = re.sub(r'\n?\s*<p class="xr-chips">.*?</p>', '', s, flags=re.S)
        out.append(s)

    txt = '<!--META title=%s | desc=%s-->\n' % (TITLE, DESC) + '\n'.join(out)
    io.open('/tmp/body_ch.html', 'w', encoding='utf-8').write(txt)
    print('%d 文字 / 面 %d 枚 / 図版 %d 点' % (len(txt), len(out) - 1, txt.count('class="figure"')))


if __name__ == '__main__':
    main()
