#!/usr/bin/env python3
"""『AI推進の教科書』のワークシート（A4縦・表紙＋6ワークの7ページ）。

  python3 99_assets/pdf-src/ai-drive-worksheet.py
  node …/make_pdf.mjs /tmp/ozaken-ogp-fonts/ai-drive-worksheet.html    99_assets/ai-drive-worksheet.pdf a4p
  node …/make_pdf.mjs /tmp/ozaken-ogp-fonts/ai-drive-worksheet-pw.html 05_drive/ai-drive-worksheet-pw.pdf a4p

**2種類を焼く。**
  公開版  資料ページのダウンロードから配る。**個別パスワードを刷らない。**
          リンク先は暗号の外に置かれるので、誰でも取れる
  配布版  研修や講演の当日配布に使う。パスワードを刷ってある

**16:9で焼かない。** 印刷して手で書く紙なので A4縦（a4p）。

資料の図版と1対1で対応させている。受講者が「どの節のワークか」を
見失わないよう、図版の言い回しをそのまま使うこと。

  ワーク1 → Fig.2  3ヶ月で寄っていく3つの形   （Section 01）
  ワーク2 → Fig.6  1業務目を、この2軸で選ぶ    （Section 03）
  ワーク3 → Fig.8  期ごとの、終わったと言える条件（Section 04）
  ワーク4 → Fig.12 誰に、何を、どう持っていくか （Section 06）
  ワーク5 → Fig.16 1本目にする5条件           （Section 08）
  ワーク6 → Fig.27 折れる5つの瞬間            （Section 14）

**紙面の並びは 1 → 4 → 2 → 5 → 3 → 6。**
資料の進行そのままだと、味方づくり（ワーク4）が真ん中に来て、
「1業務を選ぶ」の前に手が止まる。実際に動く順に並べ替えている。

記入例は、**製造業の情シス兼務でAI推進を任された人**を通しで使う。
専任の担当者は実際には多くないので、兼務の人を置いている。
業種が違っても、粒度の目安になる。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from worksheet_style import CSS  # noqa: E402

URL = 'https://ozaken-ai.github.io/ozaken-materials/05_drive/ai-drive-handbook.html'
PW = 'tebanasu'

FONTS = '/tmp/ozaken-ogp-fonts'
OUT = os.path.join(FONTS, 'ai-drive-worksheet.html')
OUT_PW = os.path.join(FONTS, 'ai-drive-worksheet-pw.html')

FOOT = ('<div class="foot"><span>AI推進の教科書 ─ ワークシート</span>'
        '<span>OZAKEN / AICX %s</span></div>')


def cover(with_pw):
    key = (f'<p class="pw">PASSWORD　<b>{PW}</b></p>' if with_pw else
           '<p class="pw">PASSWORD　<b style="font-size:9pt;letter-spacing:.02em">'
           '資料の中でお伝えします</b></p>')
    return f'''<div class="page cover">
  <span class="tag">WORKSHEET ─ 7 PAGES</span>
  <h1>AI推進の教科書<br>ワークシート</h1>
  <div class="rule"></div>
  <p class="sub">読むだけでは、月曜に手が動きません。この6枚を書き終えたとき、
    はじめて自分の会社の話になります。印刷して、手で書いてください。
    前半3枚がいまの立ち位置と味方づくり、後半3枚が着手と、折れないための備えです。</p>
  <ul class="howto">
    <li><b>01</b><span><b>ワーク1｜いまの立ち位置。</b>直近1ヶ月の予定表を見て、
      何に時間を使ったかを数えます。便利屋・研修係・選定係のどれに寄っているかが出ます。</span></li>
    <li><b>02</b><span><b>ワーク4｜味方を3人。</b>経営・情シス・現場に1人ずつ。
      役職ではなく<b>名前で書けるか</b>。書けないなら、それがいまの最優先です。</span></li>
    <li><b>03</b><span><b>ワーク2｜1業務目を選ぶ。</b>候補を3つ書いて、四象限に置きます。
      右上が1つに絞れなければ、まだ条件を満たしていません。</span></li>
    <li><b>04</b><span><b>ワーク5｜5条件で落とす。</b>選んだ1業務が、5つとも満たすか。
      4つしか満たさないなら、それは2本目以降です。</span></li>
    <li><b>05</b><span><b>ワーク3｜12ヶ月の地図。</b>3つの期に、終わったと言える条件を
      自分の会社の言葉で書きます。そのまま上司との合意文になります。</span></li>
    <li><b>06</b><span><b>ワーク6｜折れる前に。</b>5つの瞬間のうち、自分に来そうなものは
      いまでも分かります。来る前に、右の手を1つだけ打っておきます。</span></li>
  </ul>
  <div class="who">
    <b>記入例について</b>
    <p>6枚とも、<b>製造業の情シス兼務で、AI推進を任された人</b>という
      ひとりの記入例を通しで載せています。業種が違っても、粒度の目安として使えます。
      <b>薄い青の帯が記入例です。</b>そこには書かず、下の線から書きはじめてください。</p>
  </div>
  <div class="promise">
    <div>
      <p><b>この資料は更新されます。</b>製品名も相場も数か月で変わるので、
        新しい情報が出るたびに資料ページを差し替えています。
        <b>URLは変わりません</b>ので、ブックマークしておけば、いつ開いても最新になっています。
        このワークシートの設問は、製品が変わっても使えるように作ってあります。</p>
      <p class="url">{URL}</p>
      {key}
    </div>
  </div>
  {FOOT % 'COVER'}
</div>'''


# ── ワーク1 ── いまの立ち位置 ─────────────────────────────────
def work1():
    rows = [
        ('便利屋', 'プロンプトの相談、ツールの設定、資料の清書。頼まれごとを受けている時間',
         '週に6時間ほど。Teamsで来る個別の相談が大半'),
        ('研修係', '研修の企画・準備・登壇。教えている時間',
         '月に4時間。全社研修を2回やったが、その後の実例はゼロ'),
        ('選定係', '製品比較、見積取得、稟議の往復。選んでいる時間',
         '週に4時間。3社の比較表を作って、まだ決まっていない'),
        ('土台づくり', '測る・線を引く・1業務を動かす。残るものを作っている時間',
         '週に1時間。ほぼ手が回っていない。ここを増やすのが今期の課題'),
    ]
    body = ''.join(f'''<tr>
      <td class="q"><b>{n}</b><span>{d}</span></td>
      <td class="e">{ex}</td>
      <td class="a"></td></tr>''' for n, d, ex in rows)
    return f'''<div class="page">
  <span class="tag">WORK 01 ─ SECTION 01</span>
  <h1>いまの自分は、どの形に寄っているか</h1>
  <div class="rule"></div>
  <p class="sub">直近1ヶ月の予定表とチャットの履歴を見て、
    <b>実際に使った時間</b>を書き出します。ありたい姿ではなく、事実を書いてください。
    4つ目が週1時間を切っているなら、いまは推進ではなく対応をしています。</p>
  <table class="rows"><tr><th>形</th><th>記入例</th><th>あなたの場合（時間と、その中身）</th></tr>
  {body}</table>
  <div class="pick">
    <span class="k">いちばん多かったのは</span>
    <div class="big"><span>形の名前</span><div class="line"></div></div>
    <div class="big"><span>そこを減らすために、今週やめること</span><div class="line"></div></div>
  </div>
  <p class="note" style="margin-top:3mm">3つとも悪気なくそうなります。
    頼まれたことに誠実に応えた結果なので、自分では気づけません。
    <b>共通しているのは、自分が動いた分しか進まない形になっていること</b>です。</p>
  {FOOT % 'WORK 01'}
</div>'''


# ── ワーク4 ── 味方を3人 ─────────────────────────────────────
def work4():
    rows = [
        ('経営', '効果と、いつ止められるか', '着手前の測定結果と、撤退条件を書いた1枚',
         '製造本部長。前に工場のIoT案件で一緒だった。数字で話すと早い'),
        ('情シス', '事故が起きない保証', '入れてよいデータと、だめなデータの分類案',
         '情シスの課長。自分も兼務なので、上司にあたる。分類案は自分から出す'),
        ('現場', '自分の仕事が軽くなること', 'その人の業務が、何分減るかの見込み',
         '生産管理の主任。毎週の実績集計に3時間かけている。まずここから'),
    ]
    body = ''.join(f'''<tr>
      <td class="q"><b>{n}</b><span>欲しがっているもの：{w}</span></td>
      <td class="e"><b style="font-family:'HG';font-size:6.5pt;letter-spacing:.14em;
        color:#2e5496;display:block;margin-bottom:.8mm">記入例</b>{ex}</td>
      <td class="a"></td></tr>''' for n, w, _t, ex in rows)
    return f'''<div class="page">
  <span class="tag">WORK 04 ─ SECTION 06</span>
  <h1>味方を3人。名前で書けるか</h1>
  <div class="rule"></div>
  <p class="sub">この仕事がいちばん多く失敗するのは、技術でも予算でもなく<b>孤立</b>です。
    経営に1人、情シスに1人、現場に1人。<b>役職ではなく、名前で書いてください。</b>
    書けないなら、それがいまいちばんの課題です。</p>
  <table class="rows"><tr><th>相手</th><th>記入例</th><th>名前と、その人の事情</th></tr>
  {body}</table>
  <div class="pick">
    <span class="k">この3人に、来週それぞれ渡すもの</span>
    <div class="big"><span>経営へ</span><div class="line"></div></div>
    <div class="big"><span>情シスへ</span><div class="line"></div></div>
    <div class="big"><span>現場へ</span><div class="line"></div></div>
  </div>
  <p class="note" style="margin-top:3mm">同じ資料を3人に見せて全員に刺さることは、まずありません。
    <b>「まずやってみましょう」「そこは大丈夫です」「全社的な取り組みです」</b>は、
    それぞれ経営・情シス・現場に言ってはいけない一言です。善意で言ってしまい、取り消しにくい。</p>
  {FOOT % 'WORK 04'}
</div>'''


# ── ワーク2 ── 1業務目の四象限 ────────────────────────────────
def work2():
    cells = [
        ('A', '慎重に進む', '型はあるが、取り消せない。速く作れますが、必ず人を挟みます',
         '請求書の突合。効果は大きいが、間違えると社外に出る。2本目以降', False),
        ('B', 'ここから始める', '型があり、取り消せる。1業務目は、必ずここから選びます',
         '生産会議の議事録と次アクション。毎週あり、社内で完結し、直せる', True),
        ('C', '当面はやらない', '型も無く、取り消せない。人の仕事のまま置きます',
         'クレーム対応の一次回答。相手に届いたら戻せない', False),
        ('D', '型を作るところから', '型は無いが、取り消せる。まず様式を決める作業から',
         '不具合報告の分類。まず分類の軸を決めるところから', False),
    ]
    grid = ''.join(
        f'''<div class="cell{' hi' if hi else ''}">
      <span class="k">{k}</span><h3>{t}</h3><p>{d}</p>
      <div class="ex"><b>記入例</b><span>{ex}</span></div>
      <div class="line"></div><div class="line"></div><div class="line"></div>
    </div>''' for k, t, d, ex, hi in cells)
    return f'''<div class="page">
  <span class="tag">WORK 02 ─ SECTION 03</span>
  <h1>1業務目を、2軸で選ぶ</h1>
  <div class="rule"></div>
  <p class="sub">頭の中で選ぶと、必ず「いちばん大変な業務」を選んでしまいます。
    <b>候補を3つ書き出して、4つの枠に置いてください。</b>
    右上（B）に入ったものが1本目です。Bが空なら、まだ着手する業務が見つかっていません。</p>
  <p class="ylab">↑ 縦：仕事の型が決まっている／下は型がない</p>
  <div class="quad">{grid}</div>
  <div class="axis"><span>← 取り消せない</span><span>取り消せる →</span></div>
  <p class="note">1業務目は、成果を出すためではなく
    <b>「うちでもできる」と思わせるため</b>に選びます。地味な業務のほうが、この目的には合っています。</p>
  {FOOT % 'WORK 02'}
</div>'''


# ── ワーク5 ── 5条件で落とす ─────────────────────────────────
def work5():
    rows = [
        ('毎週来る', '直近1ヶ月の予定表で、4回以上あるか',
         '毎週水曜の生産会議。月4回。○'),
        ('社内で完結する', '出力が社外の人の目に触れるか',
         '議事録は社内のみ。社外には出ない。○'),
        ('間違えても戻せる', '出したあとに訂正できるか',
         '配布後でも差し替えられる。○'),
        ('渡す材料が手元にある', '過去10件を、いま出せるか',
         '過去の議事録は共有フォルダに2年分。○'),
        ('自分が中身を分かっている', '出た結果の良し悪しを、自分で言えるか',
         '会議には毎回出ている。抜けに気づける。○'),
    ]
    body = ''.join(f'''<tr>
      <td class="q"><b>{n}</b><span>{h}</span></td>
      <td class="e"><b style="font-family:'HG';font-size:6.5pt;letter-spacing:.14em;
        color:#2e5496;display:block;margin-bottom:.8mm">記入例</b>{ex}</td>
      <td class="a"></td></tr>''' for n, h, ex in rows)
    return f'''<div class="page">
  <span class="tag">WORK 05 ─ SECTION 08</span>
  <h1>5条件で、1本目を確定させる</h1>
  <div class="rule"></div>
  <p class="sub">ワーク2で右上に置いた業務を、ここで確かめます。
    <b>5つとも満たすものだけが1本目です。</b>
    4つしか満たさないなら、それは2本目以降に回してください。1本目でつまずくと、次の提案が通らなくなります。</p>
  <div class="pick" style="margin-bottom:3mm">
    <span class="k">確かめる業務</span>
    <div class="big"><span>業務名</span><div class="line"></div></div>
  </div>
  <table class="rows"><tr><th>条件</th><th>記入例</th><th>あなたの場合（○か×と、その根拠）</th></tr>
  {body}</table>
  <p class="note" style="margin-top:3mm">4つ目で×が付くことが、いちばん多くあります。
    <b>過去10件が出せないなら、それを集めるところが1本目の仕事</b>です。
    材料が無い状態で型を作っても、平均的な出力しか返りません。</p>
  {FOOT % 'WORK 05'}
</div>'''


# ── ワーク3 ── 12ヶ月の地図 ──────────────────────────────────
def work3():
    rows = [
        ('0〜90日', '土台',
         '規程が1枚あり、着手前の数字が手元にあり、1業務が動きはじめている',
         '入れてよいデータの表がA4で1枚できている。生産会議の議事録に'
         '週3時間かかっていると測れている。議事録の型を1本作りはじめている'),
        ('91〜180日', '定着',
         '動いた1業務が型になり、自分以外の3人が使っている',
         '議事録の型を、生産管理の3人が自分で使っている。'
         '週3時間が1時間になった。外した回の理由が10件ぶん残っている'),
        ('181〜365日', '拡大',
         '自分以外に型を作れる人が2人以上いて、部署をまたいで動いている',
         '生産管理の主任が、自分で品質報告の型を作った。'
         '調達部からも相談が来ている。自分は相談を受けるだけ'),
    ]
    body = ''.join(f'''<tr>
      <td class="q" style="width:30mm"><b>{p}</b><span>{k}</span></td>
      <td><div class="ex" style="margin-bottom:1.5mm"><b>一般形</b><span>{g}</span></div>
        <div class="ex"><b>記入例</b><span>{ex}</span></div>
        <div class="line"></div><div class="line"></div><div class="line"></div></td>
      </tr>''' for p, k, g, ex in rows)
    return f'''<div class="page">
  <span class="tag">WORK 03 ─ SECTION 04</span>
  <h1>12ヶ月を、3つの期に割る</h1>
  <div class="rule"></div>
  <p class="sub">12ヶ月を1本で考えると、何から手を付けるか毎週ぶれます。
    <b>期ごとに「終わったと言える条件」を、自分の会社の言葉で書いてください。</b>
    ここで書いた文が、そのまま上司との合意文になります。</p>
  <table class="rows" style="table-layout:fixed">
  <tr><th style="width:30mm">期</th><th>終わったと言える条件（自分の会社の言葉で）</th></tr>
  {body}</table>
  <div class="pick" style="margin-top:3mm">
    <span class="k">この3つを、いつ誰と合意するか</span>
    <div class="big"><span>相手</span><div class="line"></div></div>
    <div class="big"><span>いつまでに</span><div class="line"></div></div>
  </div>
  <p class="note" style="margin-top:3mm">土台に1年かけると、先に周りの熱が冷めます。
    <b>90日で粗くても埋めきって、動くものを見せるほうが続きます。</b>
    ただし「1業務を動かす」だけは、期をまたいで構いません。</p>
  {FOOT % 'WORK 03'}
</div>'''


# ── ワーク6 ── 折れる前に ────────────────────────────────────
def work6():
    rows = [
        ('ひとりでやっている', '相談する相手が社内にいない',
         '3人の味方を、最初の90日で作る。名前で書けるまで'),
        ('成果を聞かれて答えられない', '着手前の数字が無い',
         '着手前の1ヶ月を測っておく。粗くていい'),
        ('正論で止められる', '「セキュリティが」「前例が」',
         'よくある反論と答えを、先に紙に書いておく'),
        ('熱が冷める', '半年たつと、周りの関心が落ちる',
         '冷めたあとに残るもの（型と規程）を、熱いうちに作る'),
        ('異動・離任', '担当が変わった日に、全部止まる',
         '自分が作らない。作れる人を増やすことを、最初から目標にする'),
    ]
    body = ''.join(f'''<tr>
      <td class="q"><b>{n}</b><span>{w}</span></td>
      <td class="e">{h}</td>
      <td style="width:14mm;text-align:center"><i style="display:inline-block;width:4.6mm;height:4.6mm;border:1.3px solid #2e5496;border-radius:1mm"></i></td>
      <td class="a" style="height:14mm"></td></tr>''' for n, w, h in rows)
    return f'''<div class="page">
  <span class="tag">WORK 06 ─ SECTION 14</span>
  <h1>折れる前に、先に打っておく</h1>
  <div class="rule"></div>
  <p class="sub">この5つのうち、自分に来そうなものは今でも分かるはずです。
    <b>来る前に、右の手を1つだけ実行してください。</b>
    どれも「うまくいっているうちにしかできないこと」で、折れてからでは手が回りません。</p>
  <table class="rows"><tr><th>折れる瞬間</th><th>先に打っておく手</th>
  <th style="width:14mm">済</th><th>いつ、何をするか</th></tr>
  {body}</table>
  <div class="pick" style="margin-top:3mm">
    <span class="k">よくある反論と、こちらの答え（3つ書いておく）</span>
    <div class="big"><span>言われること</span><div class="line"></div></div>
    <div class="big"><span>返す言葉</span><div class="line"></div></div>
    <div class="big"><span>言われること</span><div class="line"></div></div>
    <div class="big"><span>返す言葉</span><div class="line"></div></div>
  </div>
  <p class="note" style="margin-top:3mm">返ってくる言葉は、3つか4つしかありません。
    <b>その場で考えると、たいてい言い負けます。</b>
    紙に書いておくだけで、次の会議の通り方が変わります。</p>
  {FOOT % 'WORK 06'}
</div>'''


def build(with_pw):
    return ('<!DOCTYPE html><html lang="ja"><head><meta charset="utf-8">'
            '<title>AI推進の教科書 ワークシート</title>'
            '<style>%s</style></head><body>%s</body></html>'
            % (CSS, cover(with_pw) + work1() + work4() + work2()
               + work5() + work3() + work6()))


os.makedirs(FONTS, exist_ok=True)
open(OUT, 'w', encoding='utf-8').write(build(False))
open(OUT_PW, 'w', encoding='utf-8').write(build(True))
print('書きました:\n  公開版 %s\n  配布版 %s' % (OUT, OUT_PW))
