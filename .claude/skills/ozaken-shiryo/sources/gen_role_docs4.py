#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""職種別ガイドの4層目。いまはマーケティング編だけに、ブランディングの軸を足す。

  cd .claude/skills/ozaken-shiryo/sources
  OZAKEN_PW=マスター python3 gen_role_docs4.py
  cd ../scripts
  OZAKEN_PW=マスター python3 publish.py /tmp/body_role4_marketing.html 09_role/marketing.html --update
  OZAKEN_PW=マスター python3 crossref.py apply

**足すのは、この主張。** 制作・配信・測定の実行がAIに移って安くなるほど、
差がつくのは「何者として、何を出さないか」を決める軸、つまりブランディングと
ポジショニングになる。AIエージェントが検索と推薦の窓口になると、選ばれる根拠は
指名と信頼に寄る。だからマーケティングの重心は、実行の腕からブランドの軸へ移る。

**入れる場所は Section 03（相手が先に変わった）の直後。** 相手の探し方が変わった、
という話の次に「だから重みが移る軸」を置き、そのあとの「目的は変わらない。時間の中身が変わる」へつなぐ。
面は2つ（紺・明）で、後ろの Section 番号と Fig 番号を +2 する。

**gen_role_docs3.py を流し直したら、このスクリプトも流し直す。** 3層目までは
ROLES → X → Y の上書きで組み立てているが、この層は公開済みページへの差し込み。
何度流しても同じ結果になるよう、前回入れた2面は data-brand の印で見分けて先に落とす。
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
from domain_fig import fig_gap, fig_cols

DOC = '09_role/marketing.html'
MINE = 'この整理は小澤健祐によるもの'
MARK = ' data-brand="1"'

HERO_COPY = ('<p class="hero-copy">生成AIで最初に変わるのは制作の速度ですが、'
             '効果が出るのは検証の回数が増えたときです。量ではなく、回転数で考えます。'
             'そして実行が安くなるほど、何者として何を出さないかを決める、'
             'ブランディングの軸が重くなります。</p>')

SWAPS = [
    ('作る腕が誰でも同じになる時代に、組織に残るのは、そちらのほうです。</p>',
     '作る腕が誰でも同じになる時代に、組織に残るのは、そちらのほうです。'
     'そして、何を出さないかを決める基準の正体は、ブランドです。'
     '<span class="fw-bold">実行が安くなるほど、マーケティングの重心は、'
     'ブランディングとポジショニングの軸へ移ります。</span></p>'),
]


def brand_axis_face(n):
    return sec('sec-navy', 'Section %02d' % n,
        '実行が安くなるほど、ブランディングの軸の重要性が上がります',
        '作る・配る・測るはAIに移ります。残るのは「何者として、何を出さないか」を決める軸です。',
        cattr=' data-figdark="1"' + MARK,
        lede='誰もが同じAIで、同じ水準のクリエイティブを、ほぼ無料で出せるようになりました。'
             '<span class="fw-bold">量でも速さでも、もう差はつきません</span>。'
             'さらに、AIエージェントが検索と推薦の窓口になると、'
             '選ばれる根拠は「知っている」「信頼している」、つまり指名とブランドに寄ります。'
             '<span class="fw-bold text-azure">だからマーケティングの重心は、実行の腕から、'
             'ブランディングとポジショニングの軸へ移ります。</span>'
             '前の面で見た「相手の探し方の変化」が、この移動を早めています。',
        fig=fig_gap([
            ('制作の速さと、出せる量', '出す・出さないを決める基準。ブランドの線'),
            ('媒体運用と入札の腕', 'ポジショニング。何者として選ばれるか'),
            ('A/Bテストの回数', '世界観とトーンの一貫性'),
            ('フォロワー数と、ページビュー', '指名検索の量と、一次情報の量'),
            ('AIで作れるものの多さ', 'AIに渡せるブランドガイドの質'),
        ], 'Fig.%d ── 重みが下がる軸と、上がる軸。上がる側は、どれもブランドの話' % (n + 1), MINE,
           uid='mktbrand', left_label='重みが下がる（AIに移る）', right_label='重みが上がる（人が決める軸）'),
        body=cards([
            ('<span class="mth">差</span>同じAIなら、同じ品質。差は「らしさ」にしか残りません',
             '生成の水準は、モデルが同じなら会社が違っても同じです。'
             '<b>読み手が見分けられるのは、何者が、どんな口調で、何を言わないか</b>。'
             '実行が均質になるほど、ブランドの輪郭が成果を分けます。'),
            ('<span class="mth">窓口</span>AIが選ぶ時代は、指名と信頼が根拠になります',
             '検索結果の一覧ではなく、AIの回答の中に載るかどうか。'
             '<b>載るのは、一次情報を持ち、名前で指名され、言うことが一貫している会社</b>です。'
             'ブランドは、気持ちの話ではなく、AIに選ばれる条件になりました。'),
            ('<span class="mth">順番</span>実行を任せて空いた時間を、ブランドの軸に使います',
             '草案や配信を型に任せると、担当者の時間が空きます。'
             '<b>その時間を、もっと作ることではなく、何者かを決めることに使う</b>。'
             'ここが、この職種で「任せる」意味のいちばん大きいところです。'),
        ]))


def brand_context_face(n):
    return sec('sec-light', 'Section %02d' % n,
        'ブランドを、AIに渡せる形にします',
        '抽象的なブランドガイドは、人にもAIにも効きません。何者か・語り口・出さないもの・根拠の4つで書きます。',
        cattr=MARK,
        lede='ブランディングの軸が重くなるほど、'
             '<span class="fw-bold">その軸を、AIに渡せる形に言葉にする仕事</span>が増えます。'
             '「上質で親しみやすく」のような形容詞では、人も迷い、AIは平均を返します。'
             '<span class="fw-bold text-azure">何者か、語り口、出さないもの、根拠。'
             'この4つを、良い例より「直した例」と「却下した例」で書く。</span>'
             'そうして書かれたブランドガイドは、草案ボットの前提になり、'
             '公開前の関門の基準になり、新しい担当者の教材になります。',
        fig=fig_cols([
            ('WHY', '何者か', '存在理由と、約束',
             '誰の、どんな困りごとに、何者として応えるか。1文で書く。迷ったら、ここに戻る', 0),
            ('TONE', '語り口', '言葉づかいの型',
             '使う言葉と使わない言葉。直す前と後の例を3組。良い例だけより伝わる', 0),
            ('NO', '出さないもの', '禁止表現と、却下した例',
             '最上級表現、根拠の無い数字、他社との比較。却下ログがそのまま基準の実体になる', 3),
            ('PROOF', '根拠', '一次情報の置き場',
             '自社にしかない数字と事例。AIの回答に引用として残るのは、ここだけ', 1),
        ], 'Fig.%d ── ブランドガイドの4つの欄。形容詞ではなく、例と却下で書く' % (n + 1), MINE),
        body=cards([
            ('<span class="mth">一貫性</span>一貫して守ることは、AIの得意分野です',
             '人は疲れると表現がぶれますが、型は疲れません。'
             '<b>ブランドガイドを渡した草案ボットは、誰が使っても同じ輪郭で返します</b>。'
             '速度を上げてもぶれないのは、人の確認ではなく、渡した前提の力です。'),
            ('<span class="mth">更新</span>「らしさ」を動かすのは、人の仕事のままです',
             '市場と顧客が変われば、何者かの定義も少しずつ動きます。'
             '<b>守るのはAI、動かすのは人</b>。'
             '四半期に一度、却下ログを読み返して欄を書き換えるのが、ブランドを育てる工程です。'),
            ('<span class="mth">測る</span>指名検索と、逸脱の件数と、一次情報の割合で見ます',
             'ブランドの効き目は、指名検索の量、公開前に差し戻した逸脱の件数、'
             '出したものに含まれる一次情報の割合で追えます。'
             '<b>3つとも、いまの運用の中で数えられる数字</b>です。'),
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

    mid = [s for s in mid if MARK.strip() not in s]
    if len(mid) != 15:
        sys.exit('外したあとの面の数が想定と違います: %d' % len(mid))

    hero = re.sub(r'<p class="hero-copy">.*?</p>', HERO_COPY, hero, flags=re.S)
    for a, b in SWAPS:
        close = close.replace(a, b)

    at = next(i for i, s in enumerate(mid) if '>Section 03<' in s) + 1
    # **番号は足し算ではなく、振り直す。** 公開済みページを読み直す作りなので、
    # 「後ろを +2」だと2回目に流したとき +4 になる（実際になった）。
    # 挿入位置より後ろの面は、Section も Fig も、続き番号で振り直す。
    later = mid[at:]
    TITLE = re.compile(r'(fig-no">Fig\.|<p class="fig-title">Fig\.)(\d+)')
    figmap, nxt = {}, 7                        # 新しい2面が Fig.5 / Fig.6
    for s in later:
        for m in TITLE.finditer(s):
            figmap.setdefault(int(m.group(2)), nxt)
            if figmap[int(m.group(2))] == nxt:
                nxt += 1
    out_later = []
    for i, s in enumerate(later):
        s = re.sub(r'Fig\.(\d+)', lambda m: 'Fig.%d' % figmap.get(int(m.group(1)), int(m.group(1))), s)
        s = re.sub(r'>Section (\d+)<', '>Section %02d<' % (6 + i), s)
        out_later.append(s)
    mid = mid[:at] + [brand_axis_face(4), brand_context_face(5)] + out_later

    out = []
    for s in [hero] + mid + [close]:
        s = re.sub(r'\s+data-bg="\d+"', '', s)
        s = re.sub(r'\n?<a class="oz-home"[^>]*>.*?</a>', '', s)
        s = re.sub(r'\n?\s*<p class="xr-chips">.*?</p>', '', s, flags=re.S)
        out.append(s)

    title = re.search(r'<title>(.*?)</title>', page).group(1).split(' | ')[0]
    desc = re.search(r'name="description" content="(.*?)"', page).group(1)
    if 'ブランディング' not in desc:
        desc = desc.rstrip('。') + '。実行が安くなるほど重みが増すブランディングの軸と、ブランドをAIに渡せる形にする4つの欄も。'
    txt = '<!--META title=%s | desc=%s-->\n' % (title, desc) + '\n'.join(out)
    io.open('/tmp/body_role4_marketing.html', 'w', encoding='utf-8').write(txt)
    print('%d 文字 / 面 %d 枚 / 図版 %d 点' % (len(txt), len(out) - 1, txt.count('class="figure"')))


if __name__ == '__main__':
    main()
