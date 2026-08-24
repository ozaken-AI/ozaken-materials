#!/usr/bin/env python3
"""労働組合向け講演『AIは、売場と厨房に何をしに来るのか』のワークシート（A4縦・4ページ）。

  python3 99_assets/pdf-src/york-worksheet.py
  node …/make_pdf.mjs /tmp/ozaken-ogp-fonts/york-worksheet.html    公開版.pdf a4p
  node …/make_pdf.mjs /tmp/ozaken-ogp-fonts/york-worksheet-pw.html 配布版.pdf a4p

**2種類を焼く。**
  公開版  資料ページから配る。**個別パスワードを刷らない**
  配布版  当日、会場で配る。パスワードを刷ってある

**16:9で焼かない。** 講演の投影物は16:9だが、これは印刷して手で書くもの。

中身は講演の図版と1対1で対応させている。
  ワーク1 → Fig.19 業務分解のワークシート（Section 11）
  ワーク2 → Fig.9  5レベル × スーパー／外食（Section 06）
  ワーク3 → Fig.24 明日からの5つの段（Section 13）
記入例は Fig.15（スーパー・惣菜）と Fig.17（外食・店舗）から取っている。
講演の言い回しをそのまま使うこと。言い換えると、どの場面のワークか分からなくなる。
"""
import os
import sys

URL = 'https://content.ozaken.ai/09_role/york-union.html'
PW = 'benimaru'

FONTS = '/tmp/ozaken-ogp-fonts'
OUT = os.path.join(FONTS, 'york-worksheet.html')
OUT_PW = os.path.join(FONTS, 'york-worksheet-pw.html')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from worksheet_style import CSS  # noqa: E402

FOOT = ('<div class="foot"><span>AIは、売場と厨房に何をしに来るのか ─ ワークシート</span>'
        '<span>OZAKEN / AICX %s</span></div>')


def cover(with_pw):
    key = (f'<p class="pw">PASSWORD　<b>{PW}</b></p>' if with_pw else
           '<p class="pw">PASSWORD　<b style="font-size:9pt;letter-spacing:.02em">'
           '講演の中でお伝えします</b></p>')
    return f'''<div class="page cover">
  <span class="tag">WORKSHEET ─ 4 PAGES</span>
  <h1>売場と厨房の仕事を、<br>「任せられる単位」まで割る</h1>
  <div class="rule"></div>
  <p class="sub">聴くだけでは、何も変わりません。この3枚を書き終えたとき、
    はじめてAIの話が自分の仕事の話になります。印刷して、手で書いてください。
    <b>記憶で書かないこと。</b>シフト表と日報を手元に置いて書くと、精度がまるで違います。</p>
  <ul class="howto">
    <li><b>01</b><span><b>ワーク1｜一日を、作業に割る。</b>自分の一日を7つの作業に割り、
      月の回数・1回の時間・見ているものを書きます。「見ているもの」の欄が、
      そのままAIに渡す材料の一覧になります。</span></li>
    <li><b>02</b><span><b>ワーク2｜上位ひとつに、任せ方を決める。</b>回数の多い順で
      いちばん上に来た作業を1つ選び、レベル1〜3のどれで任せるか、
      越えない線はどこかを書き切ります。</span></li>
    <li><b>03</b><span><b>ワーク3｜明日からの5段。</b>今日・今週・今月・3か月・組合として。
      考える紙ではなく、日付を書く紙です。</span></li>
  </ul>
  <div class="who">
    <b>記入例について</b>
    <p>3枚とも、<b>スーパーの惣菜担当</b>と<b>外食店の店長</b>という
      2つの記入例を載せています。職種が違っても、粒度の目安として使えます。
      <b>薄い青の帯が記入例です。</b>そこには書かず、下の線から書きはじめてください。</p>
  </div>
  <div class="promise">
    <div>
      <p><b>資料は更新されます。</b>AIと雇用のデータは数か月で景色が変わるので、
        新しい統計が出るたびに資料ページの数字を差し替えています。
        <b>URLは変わりません</b>ので、いつ開いても最新の数字になっています。
        このワークシートの設問は、数字が変わっても使えるように作ってあります。</p>
      <p class="url">{URL}</p>
      {key}
    </div>
  </div>
  {FOOT % 'COVER'}
</div>'''


def work1():
    ex = [
        ('値引きの時間と幅を決める', '60回', '5分',
         '残数、時間帯、客数の推移、天気', 'レベル3（案を出す）'),
        ('翌週のシフトを組む', '4回', '90分',
         '予約状況、前年同週、希望シフト、資格と経験', 'レベル3（案＋人が確定）'),
    ]
    exrows = ''.join(
        f'''<tr class="exr"><td class="n">{a}</td><td>{b}</td><td>{c}</td>
        <td>{d}</td><td>{e}</td></tr>''' for a, b, c, d, e in ex)
    blank = '''<tr class="bl"><td class="n"></td><td></td><td></td>
        <td></td><td></td></tr>''' * 8
    return f'''<div class="page">
  <span class="tag">WORK 01 ─ SECTION 11</span>
  <h1>一日を、作業に割る</h1>
  <div class="rule"></div>
  <p class="sub">自分の一日を、7つ以上の作業に割ってください。ルールは3つだけ。
    <b>①必ず動詞で書く</b>（「発注」ではなく「発注数を決める」）、
    <b>②月の回数と1回の時間を分けて持つ</b>、
    <b>③「見ているもの」を必ず埋める</b>。③が埋まらない作業は、そもそも任せられません。</p>
  <div class="ex"><b>記入例</b><span>上の2行が記入例です。1行目がスーパーの惣菜担当、
    2行目が外食店の店長。この粒度で書いてください。</span></div>
  <table class="plan">
    <tr><th style="width:48mm">作業（動詞で書く）</th><th style="width:18mm">月の回数</th>
      <th style="width:13mm">1回</th><th style="width:53mm">見ているもの</th>
      <th style="width:36mm">任せ方</th></tr>
    {exrows}
    {blank}
  </table>
  <p class="note" style="margin-top:4mm">書き終えたら、<b>月の回数 × 1回の時間</b>を計算して、
    大きい順に並べ替えてください。月1回30分の仕事より、月60回5分の仕事のほうが先です。
    <b>「任せない（手作業）」と書ける行があることも、大事な発見です。</b></p>
  {FOOT % 'WORK 01'}
</div>'''


def work2():
    slots = [
        ('① いちばん回数の多い作業', 'ワーク1で並べ替えた、いちばん上の行を書き写します',
         '値引きの時間と幅を決める（月60回 × 5分 ＝ 月300分）'),
        ('② その作業で、見ているもの', 'AIに渡す材料の一覧になります。所在まで書けると、なお良い',
         '残数（レジの販売記録）、時間帯、客数の推移、天気予報。'
         'すべて画面で見られるが、判断の基準は自分の頭の中にしかない'),
        ('③ どのレベルで任せるか',
         'レベル1＝都度の指示／レベル2＝自店の前提を渡した相談窓口／'
         'レベル3＝手順を組んで自動で案を出す',
         'レベル3。毎日決まった時刻に、残数から値引き案を出してもらう。押すのは自分'),
        ('④ 越えない線', '<b>ここが無いと、事故が起きます。</b>'
         '取り返しがつくかどうかで決めてください',
         '値引きの確定はAIにやらせない。案を見て、自分が押す。'
         'お客様の個人情報と、未公開の数字は入力しない'),
        ('⑤ 判断の理由を、どこに残すか',
         'AIが賢くなるのは、外したときの理由が残っているときだけです',
         '外した日は、日報に一行だけ書く。「地区の運動会があった」で足りる'),
        ('⑥ 誰と一緒に進めるか', 'レベル3から先は、一人では動きません',
         '同じ売場の2人と、書いたシートを持ち寄る。'
         '重なった作業を、店長経由で本部に上げる'),
    ]

    def box(t, d, ex, n=3, hi=False):
        return (f'<div class="slot{" hi" if hi else ""}">'
                f'<h3>{t}</h3><p>{d}</p>'
                f'<div class="ex"><b>記入例</b><span>{ex}</span></div>'
                + '<div class="line"></div>' * n + '</div>')
    four = ''.join(box(*x) for x in slots[:4])
    two = ''.join(box(*x, 2, True) for x in slots[4:])
    return f'''<div class="page">
  <span class="tag">WORK 02 ─ SECTION 06</span>
  <h1>上位ひとつに、任せ方を決める</h1>
  <div class="rule"></div>
  <p class="sub">ワーク1でいちばん上に来た作業を1つ選び、6つの欄を埋めます。
    <b>①〜④が本体、⑤と⑥は続けるために必ず要る2つ</b>です。
    記入例はスーパーの惣菜担当で通しています。</p>
  <div class="slots">{four}</div>
  <div class="slots2">{two}</div>
  <p class="note" style="margin-top:3mm">1回で当てようとしないでください。
    まず1週間、AIが出した案と自分の判断を並べて見比べる。
    ずれた日だけ理由を書いて、渡し方を直す。この往復が型をつくります。
    <b>書き上げた紙は、そのまま新人への引き継ぎ資料になります。</b></p>
  {FOOT % 'WORK 02'}
</div>'''


def work3():
    rows = [
        ('今日 ── 7行、埋める', 'ワーク1を、シフト表と日報を見ながら'),
        ('今週 ── レベル1を1つ試す', '手書きのメモを整える／長い通達を3行にする'),
        ('今月 ── 職場で1枚、持ち寄る', '同じ売場・厨房の人と、シートを見せ合う'),
        ('3か月 ── レベル2を1つ作る', '自店の手順書を読ませた「相談窓口」を1つ'),
        ('組合として ── 3つを議題に', '導入の順番／負荷の寄り方／浮いた時間の行き先'),
    ]
    tr = ''.join(f'''<tr><td class="n">{n}<span>{d}</span></td>
      <td></td><td></td></tr>''' for n, d in rows)
    checks = [
        ('自分の一日を、動詞で7つ以上書き出せた',
         '書けないなら、まだ「業務」の塊のままです。塊のままでは、渡す部分が決まりません'),
        ('「見ているもの」の欄が、全部埋まっている',
         '空欄の行は、任せられない行です。埋められないこと自体が、いちばん大事な発見になります'),
        ('「任せない」と書いた行が、1つ以上ある',
         '全部を任せる話ではありません。手を使う非定型な作業は、機械にいちばん難しい領域です'),
        ('AIが出した案を、断れる材料を持っている',
         '来週この地区で何があるかを知っているのは、AIではなく自分です。'
         'その一行が、これからいちばん価値のある情報になります'),
    ]
    ck = ''.join(f'<li><i></i><span>{t}<em>{d}</em></span></li>' for t, d in checks)
    return f'''<div class="page">
  <span class="tag">WORK 03 ─ SECTION 13</span>
  <h1>明日からの、5つの段</h1>
  <div class="rule"></div>
  <p class="sub">考える紙ではなく、<b>日付を書く紙</b>です。同時に全部は動きません。
    いちばん下の段は、今日この場で終わります。</p>
  <table class="plan tall">
    <tr><th>やること</th><th style="width:34mm">いつまでに</th>
      <th style="width:52mm">一緒にやる人・相談する人</th></tr>
    {tr}
  </table>
  <h2 style="font-family:'SM';font-size:11pt;font-weight:600;margin:6mm 0 0">
    帰る前に、4つだけ確かめてください</h2>
  <ul class="checks">{ck}</ul>
  <p class="note" style="margin-top:4mm">AIができるのは、記録に残っていることを
    速く正確に処理することだけです。傷んだ野菜を見分けること、
    「今週は地区の運動会がある」と気づくこと。ここは当分、人の領域として残ります。
    <b>書いた分だけ、任せられるものが増え、書いた人にしかできないことがはっきりします。</b></p>
  {FOOT % 'WORK 03'}
</div>'''


def build(with_pw):
    return ('<!DOCTYPE html><html lang="ja"><head><meta charset="utf-8">'
            '<title>AIは、売場と厨房に何をしに来るのか ワークシート</title>'
            '<style>%s\n.plan td.n span{display:block;font-size:7pt;'
            'font-weight:400;color:var(--muted);line-height:1.5;margin-top:.6mm}\n'
            '.plan tr.exr td{background:rgba(46,84,150,.05);font-size:7.5pt;'
            'color:var(--muted);height:auto}\n'
            '.plan tr.exr td.n{font-size:8pt;font-weight:600}\n'
            '.plan tr.bl td{height:16.5mm}\n'
            '.plan.tall td{height:15mm}</style>'
            '</head><body>%s</body></html>'
            % (CSS, cover(with_pw) + work1() + work2() + work3()))


os.makedirs(FONTS, exist_ok=True)
open(OUT, 'w', encoding='utf-8').write(build(False))
open(OUT_PW, 'w', encoding='utf-8').write(build(True))
print('書きました:\n  公開版 %s\n  配布版 %s' % (OUT, OUT_PW))
