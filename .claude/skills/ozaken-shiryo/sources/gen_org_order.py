#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成AI時代の組織論（06_people/org-theory.html）に、2面を足す。

  cd .claude/skills/ozaken-shiryo/sources
  OZAKEN_PW=マスター python3 gen_org_order.py
  cd ../scripts
  OZAKEN_PW=マスター python3 publish.py /tmp/body_org_theory.html \\
      06_people/org-theory.html --update
  OZAKEN_PW=マスター python3 crossref.py apply

**足すのは、この主張。**
  業務命令にできないなら、生成AIもAIエージェントも使わせないほうがいい。
  「使っていい」（許可）は自由に見えて、使い方の設計を個人に丸投げしている。
  それは個人最適の罠の入口であり、属人化をむしろ加速させる。

**入れる場所は「個人最適の罠」の直後。** 罠の出口は「もっと使わせる」ではなく
「命令にできる形にする」であり、その形にする作業が次の面の「標準化」につながる。

**面は2つ。** 本文の面は奇数本で、明暗が交互で、締めが紺、という規約があるので、
1面だけ足すと締めの直前で紺が2つ続く。主張の面（紺）と、命令にするための
4条件の面（明）を対で入れる。

**何度流しても同じ結果になる。** 公開済みのページを読んで差し替える作りなので、
前回入れた2面（eyebrow で見分ける）を先に落としてから入れ直す。
図版番号は、挿入位置より後ろの Fig.N を +2 して振り直す。
"""
import io
import os
import re
import sys

S = '/home/user/ozaken-materials/.claude/skills/ozaken-shiryo/scripts'
ROOT = '/home/user/ozaken-materials'
sys.path.insert(0, S)
import lockbox
from page_parts import sec, cards, take
from domain_fig import fig_versus, fig_cols

DOC = '06_people/org-theory.html'
MINE = 'この整理は小澤健祐によるもの'
NEW = ('Chapter 6 ─ The Order', 'Chapter 6 ─ Four Conditions')


def order_face():
    return sec('sec-navy', NEW[0],
        '業務命令にできないなら、使わせないほうがいい',
        '「使っていい」と「使え」は違います。裁量に任せたAI利用は、属人化を加速させます。',
        cattr=' data-figdark="1"',
        lede='個人最適の罠の出口は、「もっと使わせる」ではありません。'
             '<span class="fw-bold">「使っていいよ」と裁量に任せた瞬間、'
             'AIの使い方は個人の名人芸になり、成果はその人の中に閉じます</span>。'
             'だから、逆説に聞こえますが、'
             '<span class="fw-bold text-azure">業務命令にできないなら、'
             '生成AIもAIエージェントも、使わせないほうがいい。</span>'
             '何の業務で、どの道具で、どの型で、誰の責任で。'
             'これを会社が言えるようになった業務から、順に使わせます。',
        fig=fig_versus(
            ('使え（業務命令）', '会社が業務・道具・型・責任を決めている'),
            ('使っていい（許可だけ）', '使い方は、個人の裁量に任されている'),
            [('決めるのは誰か', '会社が業務・道具・型を決める', '使い方は個人の裁量に任される'),
             ('成果の行き先', '型として組織に残る', '個人の中に閉じ、異動で消える'),
             ('品質', '誰がやっても同じ品質に寄る', '使える人と使えない人で差が開く'),
             ('責任', '会社が結果に責任を持つ', '「勝手に使った」個人に落ちる'),
             ('情報の扱い', '入れていい情報が決まっている', '判断が人任せで、事故が起きる')],
            'Fig.3 ── 「使え」と「使っていい」は、正反対の結果を生む', MINE, dark=True),
        body=cards([
            ('<span class="mth">逆説</span>「許可」は、属人化の入口です',
             '「使っていい」は自由に見えて、'
             '<b>使い方の設計を個人に丸投げしています</b>。'
             'うまい人はもっとうまく、使わない人は使わないまま。'
             '個人最適の罠は、禁止からではなく、許可から始まります。'),
            ('<span class="mth">責任</span>命令にできないのは、会社が説明できていないからです',
             '何の業務で、どの道具で、どの型で、誰が結果に責任を持つか。'
             'これを言えないまま使わせると、'
             '<b>事故が起きたとき、責任は「勝手に使った個人」に落ちます</b>。'
             'それは、会社の仕事の放棄です。'),
            ('<span class="mth">順番</span>使わせるのは、命令にできる業務からです',
             '全面禁止でも、全面解禁でもありません。'
             '<b>命令にできる形にした業務から、順に使わせる</b>。'
             'その「形にする」作業こそが、次の面で話す標準化です。'),
        ]),
        after=take('「AIを使わせない」と言うと、遅れた会社に聞こえるかもしれません。'
                   'でも私が見てきた限り、'
                   '<span class="fw-bold text-red">「使っていいよ」だけの会社ほど、'
                   '1年後に名人と素人の差だけが残っています</span>。'
                   '命令にできる形にすることを、会社がサボらない。'
                   '<span class="fw-bold text-red">それが、AIを本気で使う会社の、'
                   '最初の仕事です。</span>'))


def conditions_face():
    return sec('sec-light', NEW[1],
        '「業務命令」にするための、4つの条件',
        '業務・道具・型・責任。4つが言えたら命令にでき、言えないなら型化が先です。',
        lede='業務命令にするとは、'
             '<span class="fw-bold">「この業務は、この道具で、この型で、この責任のもとで'
             'やってください」と会社が言えること</span>です。'
             '<span class="fw-bold text-azure">4つのうち1つでも欠けていれば、'
             'それは命令ではなく許可です。</span>'
             '欠けている欄が、その組織の型化の宿題になります。',
        fig=fig_cols([
            ('01', '業務', 'どの仕事で使うか',
             '「議事録の作成」「一次回答の下書き」のように、工程の名前で言える', 0),
            ('02', '道具', '何を使わせるか',
             '会社が契約し、入れていい情報の範囲を決めた道具に限る', 0),
            ('03', '型', 'どう使うか',
             'プロンプト・手順・確認の仕方を配る。個人の工夫は型に戻す', 1),
            ('04', '責任', '誰が結果を負うか',
             '出力の確認者と最終責任者を、先に決めておく。「AIがやった」は通らない', 3),
        ], 'Fig.4 ── 4つが言えたら業務命令にできる。言えない欄が、型化の宿題', MINE),
        body=cards([
            ('<span class="mth">診断</span>いま使っている用途で、4つを埋めてみます',
             '社内で使われているAIの用途を1つ取り、4つの欄を埋めてみてください。'
             '<b>埋まらない欄が、必ず出ます</b>。'
             'それが「許可のまま放置されている」印です。'),
            ('<span class="mth">工夫</span>命令にしても、工夫は止まりません',
             '「命令にすると現場の工夫が止まる」と言われます。逆です。'
             '<b>工夫は、型に戻して初めて組織のものになります</b>。'
             '戻す口の作り方は、あとの面のAI-SECIモデルで扱います。'),
            ('<span class="mth">経営</span>人に命令できない業務は、AIにも任せられません',
             'AIエージェントに任せる範囲が広がるほど、'
             '業務が命令の形になっていることが前提になります。'
             '<b>命令にできる会社が、任せられる会社になる</b>。順番はこれだけです。'),
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
    if len(mid) != 7:
        sys.exit('外したあとの面の数が想定と違います: %d' % len(mid))

    at = next(i for i, s in enumerate(mid) if '>Chapter 6 ─ The Trap<' in s) + 1
    # 後ろの面の図版番号を先に +2 しておく（Fig.3〜7 → Fig.5〜9）
    later = [re.sub(r'Fig\.(\d+)', lambda m: 'Fig.%d' % (int(m.group(1)) + 2), s)
             for s in mid[at:]]
    mid = mid[:at] + [order_face(), conditions_face()] + later

    out = []
    for s in [hero] + mid + [close]:
        s = re.sub(r'\s+data-bg="\d+"', '', s)                       # 背景の印は publish が振り直す
        s = re.sub(r'\n?<a class="oz-home"[^>]*>.*?</a>', '', s)      # 戻るボタンは apply_home が足す
        s = re.sub(r'\n?\s*<p class="xr-chips">.*?</p>', '', s, flags=re.S)  # 関連資料は crossref が足す
        out.append(s)

    title = re.search(r'<title>(.*?)</title>', page).group(1).split(' | ')[0]
    desc = re.search(r'name="description" content="(.*?)"', page).group(1)
    desc = desc.replace('サイゼリヤに学ぶ標準化', '「業務命令にできないなら使わせない」という原則、サイゼリヤに学ぶ標準化')
    txt = '<!--META title=%s | desc=%s-->\n' % (title, desc) + '\n'.join(out)
    io.open('/tmp/body_org_theory.html', 'w', encoding='utf-8').write(txt)
    print('%d 文字 / 面 %d 枚 / 図版 %d 点' % (len(txt), len(out) - 1, txt.count('class="figure"')))


if __name__ == '__main__':
    main()
