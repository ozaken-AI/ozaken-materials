#!/usr/bin/env python3
"""Udemy講座『AIエージェント時代のキャリア戦略』のワークシート（A4縦・4ページ）。

  python3 99_assets/pdf-src/career-worksheet.py
  node …/make_pdf.mjs /tmp/ozaken-ogp-fonts/career-worksheet.html      公開版.pdf a4p
  node …/make_pdf.mjs /tmp/ozaken-ogp-fonts/career-worksheet-pw.html   配布版.pdf a4p

**2種類を焼く。**
  公開版  資料ページのダウンロードボタンから配る。**個別パスワードを刷らない。**
          リンク先は暗号の外に置かれるので、誰でも取れる。パスワードを載せると鍵が漏れる
  配布版  Udemyの教材リソースや、研修の当日配布に使う。パスワードを刷ってある

**16:9で焼かない。** 講座のPDFは投影物なので16:9だが、これは印刷して手で書くもの。
横長の紙に手書きの欄を並べても、実際には使われない。

**書体は file:// で読ませるので、HTMLは書体フォルダの中に書き出す。**
書体は apply_ogp.py の fonts() が /tmp/ozaken-ogp-fonts に用意する。

中身は講座の3つの図版と1対1で対応させている。
  ワーク1 → Fig.7  目的の四象限
  ワーク2 → Fig.11 総合職の職務内容6つ
  ワーク3 → Fig.20 90日の実行計画
講座を観ながら書けるように、図版の言い回しをそのまま使うこと。
言い換えると、受講者が「どの回のワークか」を見失う。
"""
import os

URL = 'https://ozaken-ai.github.io/ozaken-materials/Udemy/career-strategy.html'
PW = 'yoroi'

FONTS = '/tmp/ozaken-ogp-fonts'
OUT = os.path.join(FONTS, 'career-worksheet.html')          # 公開版
OUT_PW = os.path.join(FONTS, 'career-worksheet-pw.html')    # 配布版（パスワードあり）

CSS = """
@font-face{font-family:'ZK';src:url('ZenKakuGothicNew-Medium.ttf')format('truetype');font-weight:500}
@font-face{font-family:'ZK';src:url('ZenKakuGothicNew-Bold.ttf')format('truetype');font-weight:700}
@font-face{font-family:'SM';src:url('ShipporiMinchoB1-Bold.ttf')format('truetype');font-weight:600}
@font-face{font-family:'HG';src:url('HankenGrotesk.ttf')format('truetype')}
:root{--ink:#1a1a2e;--navy:#1f3864;--navy-deep:#141d35;--azure:#2e5496;
  --azure-pale:#d8e4f0;--paper:#f8f7f4;--red:#e23744;--muted:#6b7a99}
*{box-sizing:border-box;margin:0;padding:0}
@page{size:A4;margin:0}
body{font-family:'ZK',sans-serif;color:var(--ink);-webkit-print-color-adjust:exact;print-color-adjust:exact}
.page{width:210mm;height:297mm;padding:16mm 15mm 13mm;page-break-after:always;
  position:relative;background:#fff;display:flex;flex-direction:column}
.page:last-child{page-break-after:auto}
.tag{display:inline-block;font-family:'HG';font-size:7.5pt;font-weight:700;letter-spacing:.16em;
  color:var(--navy-deep);background:var(--azure-pale);padding:3px 9px;border-radius:99px}
h1{font-family:'SM';font-weight:600;font-size:21pt;line-height:1.45;margin:6mm 0 3mm}
h2{font-family:'SM';font-weight:600;font-size:15pt;line-height:1.5;margin:4mm 0 1.5mm}
.sub{font-size:9pt;line-height:1.75;color:var(--muted);margin-bottom:5mm}
.rule{height:2px;background:linear-gradient(90deg,var(--azure),var(--azure-pale) 60%,transparent);margin:3mm 0 5mm}
.note{font-size:8pt;line-height:1.7;color:var(--muted)}
.foot{margin-top:auto;padding-top:4mm;border-top:1px solid var(--azure-pale);
  display:flex;justify-content:space-between;font-family:'HG';font-size:7.5pt;
  letter-spacing:.1em;color:var(--muted)}
/* 表紙 */
.cover{background:linear-gradient(168deg,#1f3864 0%,#182a52 46%,#141d35 100%);color:#fff}
.cover h1{font-size:26pt;margin-top:8mm}
.cover .sub{color:rgba(216,228,240,.78);font-size:10pt}
.cover .rule{background:linear-gradient(90deg,var(--red),rgba(226,55,68,0))}
.cover .foot{border-top-color:rgba(216,228,240,.28);color:rgba(216,228,240,.6)}
.howto{margin-top:6mm}
.howto li{list-style:none;display:flex;gap:4mm;padding:3.5mm 0;
  border-top:1px solid rgba(216,228,240,.22);font-size:9.5pt;line-height:1.8}
.howto b{font-family:'HG';font-size:9pt;color:var(--azure-pale);flex:none;width:8mm}
.howto span{color:rgba(255,255,255,.92)}
.promise{margin-top:8mm;padding:6mm;border-radius:4mm;
  background:rgba(255,255,255,.07);border:1px solid rgba(216,228,240,.26)}
.promise p{font-size:9pt;line-height:1.85;color:rgba(216,228,240,.92)}
.promise b{color:#fff}
.promise .url{font-family:'HG';font-size:9.5pt;font-weight:700;letter-spacing:.02em;
  color:#fff;margin-top:4mm;word-break:break-all}
.promise .pw{font-family:'HG';font-size:8pt;font-weight:700;letter-spacing:.14em;
  color:rgba(216,228,240,.7);margin-top:1.5mm}
.promise .pw b{font-size:12pt;letter-spacing:.06em;color:#fff}
/* 記入欄 */
.quad{display:grid;grid-template-columns:1fr 1fr;gap:3mm;margin-top:2mm}
.cell{border:1.2px solid var(--azure-pale);border-radius:3mm;padding:4mm;min-height:66mm}
.cell.hi{border-color:var(--azure);background:rgba(46,84,150,.045)}
.cell h3{font-family:'SM';font-size:11pt;font-weight:600;margin-bottom:1mm}
.cell .k{font-family:'HG';font-size:7pt;font-weight:700;letter-spacing:.14em;color:var(--azure)}
.cell p{font-size:7.5pt;line-height:1.65;color:var(--muted);margin-bottom:3mm}
.axis{display:flex;justify-content:space-between;font-family:'HG';font-size:7.5pt;
  font-weight:700;letter-spacing:.1em;color:var(--muted);margin:1mm 0}
.ylab{font-family:'HG';font-size:7.5pt;font-weight:700;letter-spacing:.1em;color:var(--muted)}
.line{border-bottom:1px dotted rgba(46,84,150,.45);height:7mm}
.rows{width:100%;border-collapse:collapse;margin-top:1mm}
.rows th{font-family:'HG';font-size:7.5pt;font-weight:700;letter-spacing:.12em;
  text-align:left;color:#fff;background:var(--navy);padding:2.5mm 3mm}
.rows td{border:1px solid var(--azure-pale);padding:2.6mm 3mm;vertical-align:top}
.rows td.q{width:52mm;background:rgba(46,84,150,.04)}
.rows td.q b{font-size:9.5pt;display:block;margin-bottom:1mm}
.rows td.q span{font-size:7.5pt;line-height:1.6;color:var(--muted)}
.rows td.a{height:19mm}
.plan{width:100%;border-collapse:collapse;margin-top:2mm}
.plan th{font-family:'HG';font-size:7.5pt;font-weight:700;letter-spacing:.12em;
  color:#fff;background:var(--navy);padding:2.5mm;text-align:center}
.plan th:first-child{text-align:left;width:44mm}
.plan td{border:1px solid var(--azure-pale);padding:3mm;height:17mm;vertical-align:top}
.plan td.n{background:rgba(46,84,150,.04);font-size:9pt;font-weight:700;vertical-align:middle}
.plan td.n span{display:block;font-weight:500;font-size:7.5pt;line-height:1.6;
  color:var(--muted);margin-top:1mm}
.checks{margin-top:4mm}
.checks li{list-style:none;display:flex;gap:3mm;align-items:flex-start;
  padding:2.8mm 0;border-bottom:1px solid rgba(46,84,150,.14);font-size:9pt;line-height:1.7}
.checks i{flex:none;width:4.5mm;height:4.5mm;border:1.4px solid var(--azure);
  border-radius:1mm;margin-top:1mm}
.checks em{font-style:normal;color:var(--muted);font-size:7.5pt;display:block;line-height:1.6}
"""

FOOT = ('<div class="foot"><span>AIエージェント時代のキャリア戦略 ─ ワークシート</span>'
        '<span>OZAKEN / AICX %s</span></div>')


def cover(with_pw):
    key = (f'<p class="pw">PASSWORD　<b>{PW}</b></p>' if with_pw else
           '<p class="pw">PASSWORD　<b style="font-size:9pt;letter-spacing:.02em">'
           '講座の中でお伝えします</b></p>')
    return f'''<div class="page cover">
  <span class="tag">WORKSHEET ─ 4 PAGES</span>
  <h1>AIエージェント時代の<br>キャリア戦略 ワークシート</h1>
  <div class="rule"></div>
  <p class="sub">観るだけでは残りません。この3枚を書き終えたとき、はじめて講座が
    自分のキャリアの話になります。印刷して、手で書いてください。</p>
  <ul class="howto">
    <li><b>01</b><span><b>ワーク1｜目的の四象限。</b>いま抱えている仕事を5つ書き出し、
      4つの枠のどこに入るかを置きます。左下が3つ以上なら、時間の使い方から変えます。</span></li>
    <li><b>02</b><span><b>ワーク2｜職務内容の棚卸し。</b>「なんでもやってきました」は市場で0点。
      6つの項目に分けて、実績を具体名詞で紐づけます。</span></li>
    <li><b>03</b><span><b>ワーク3｜90日の実行計画。</b>5つの投資先に日付を入れます。
      同時に全部は動きません。1か月目は導線づくりだけで十分です。</span></li>
  </ul>
  <div class="promise">
    <div>
      <p><b>この教材は更新されます。</b>AIと雇用のデータは数か月で景色が変わるので、
        新しい統計が出るたびに講座ページの数字を差し替えています。
        <b>URLは変わりません</b>ので、ブックマークしておけば、いつ開いても最新の数字になっています。
        このワークシートの設問は、数字が変わっても使えるように作ってあります。</p>
      <p class="url">{URL}</p>
      {key}
    </div>
  </div>
  {FOOT % 'COVER'}
</div>'''


def work1():
    cells = [
        ('A', '言語化すれば、資産になる',
         '内側から出ているが、まだ言葉になっていない。ここを言葉にすると、右上へ移ります', False),
        ('B', 'ここを増やす',
         '内側から出ていて、かつ人に説明できる。委譲もでき、枯れない。増やすのはここだけ', True),
        ('C', 'まだ目的になっていない',
         '外から与えられ、言葉にもなっていない。最初に捨ててよい領域です', False),
        ('D', '渡せるが、枯れやすい',
         '言葉になった、外から与えられた課題。AIに委譲できるが、解くほど速く消費されます', False),
    ]
    grid = ''.join(
        f'''<div class="cell{' hi' if hi else ''}">
      <span class="k">{k}</span><h3>{t}</h3><p>{d}</p>
      {'<div class="line"></div>' * 5}
    </div>''' for k, t, d, hi in cells)
    return f'''<div class="page">
  <span class="tag">WORK 01 ─ SECTION 04</span>
  <h1>いまの仕事を、4つの枠に置く</h1>
  <div class="rule"></div>
  <p class="sub">直近で担当している仕事を5つ書き出し、それぞれがどの枠に入るかを書き込んでください。
    判定の軸は2つだけ ── <b>自分の内側から出ているか</b>と、<b>人に説明できる言葉になっているか</b>。</p>
  <div class="ylab">↑ 内発性が高い</div>
  <div class="quad">{grid}</div>
  <div class="axis"><span>言語化されていない</span><span>言語化されている →</span></div>
  <p class="note" style="margin-top:4mm">書き終えたら、C（左下）に入った数を数えてください。
    3つ以上なら、新しいことを始める前に、まず時間の使い方を変える必要があります。
    A（左上）に入ったものは、次のワーク2で言葉にしていきます。</p>
  {FOOT % 'WORK 01'}
</div>'''


def work2():
    rows = [
        ('① 状況の解像度', 'Whyの入力',
         '組織の政治、予算の出所、決裁者の関心。書かれていない一次情報を、どれだけ持っているか'),
        ('② 目的の設定', 'Whyの本体',
         '解ける問題ではなく、解くべき問題を選んだ経験。「やらない」と決めたこと'),
        ('③ 検証の基準', 'Whyの出力管理',
         'AIや部下の出力を却下した経験。何を根拠に却下したかまで'),
        ('④ 文脈翻訳', '越境',
         '営業の言葉を開発の言葉に。同じ日本語なのに通じない場所に、意味を通した仕事'),
        ('⑤ 合意形成', '越境',
         '利害の違う人間を、ひとつの目的に束ねた経験。誰が何を諦めたかまで'),
        ('⑥ 全体設計', '統合',
         '部分最適の総和を、ひとつの成果に統合した経験'),
    ]
    tr = ''.join(f'''<tr><td class="q"><b>{n}</b><span>{d}</span></td>
      <td class="a"></td></tr>''' for n, _, d in rows)
    return f'''<div class="page">
  <span class="tag">WORK 02 ─ SECTION 06</span>
  <h1>職務内容に、名前をつける</h1>
  <div class="rule"></div>
  <p class="sub">「なんでもやってきました」は市場で0点です。6つに分けて、
    <b>具体名詞で</b>書いてください。「部門間を翻訳した」ではなく
    「営業の要望を開発の仕様に翻訳し、3か月で合意まで持っていった」まで書けると、はじめて名乗れます。</p>
  <table class="rows">
    <tr><th>職務内容</th><th>あなたの実績（具体名詞で）</th></tr>
    {tr}
  </table>
  <p class="note" style="margin-top:4mm">空欄が3つ以上あるなら、そこが次の90日の投資先です。
    埋まっている項目は、職務経歴書にその言葉のまま書けます。</p>
  {FOOT % 'WORK 02'}
</div>'''


def work3():
    rows = [
        ('Howを満たす', '要求水準を淡々とクリアする。ここに人生を賭けない'),
        ('一次情報の導線', '社内異動でも副業でもいい。生身の困りごとに触れる場を1つ'),
        ('下積みを自己発注', '小さく企画し、自分で決め、自分で刈り取る'),
        ('週15分のループ', '外した判断を1つ選び、前提を書き出す。予定に固定する'),
        ('職務内容の棚卸し', 'ワーク2の6項目に、実績を紐づけて名前をつける'),
    ]
    tr = ''.join(f'''<tr><td class="n">{n}<span>{d}</span></td>
      <td></td><td></td><td></td></tr>''' for n, d in rows)
    checks = [
        ('直近1か月で、AIの出力を根拠つきで却下した',
         'ゼロなら、検証基準を持っていません。AIを使っているのではなく、AIに承認印を押しています'),
        ('自分の仕事のWhyを、自分で決めていると言える',
         '与えられた目的を高速に処理しているだけなら、AIと同じ職務記述書の上に立っています'),
        ('いちばん外した判断を、前提つきで言葉にできる',
         '「運が悪かった」で処理した失敗は、何回繰り返しても基準になりません'),
        ('自分の「不均一さ」を1つ挙げられる',
         '経歴の変わり者ポイント、偏愛、劣等感。均一な基準で減点されてきたものが、非代替の資産になります'),
    ]
    ck = ''.join(f'<li><i></i><span>{t}<em>{d}</em></span></li>' for t, d in checks)
    return f'''<div class="page">
  <span class="tag">WORK 03 ─ SECTION 11</span>
  <h1>90日の計画に、日付を入れる</h1>
  <div class="rule"></div>
  <p class="sub">やることではなく、<b>いつやるか</b>を書きます。
    同時に全部は動きません。1か月目は導線づくりだけで十分です。</p>
  <table class="plan">
    <tr><th>投資先</th><th>1〜30日</th><th>31〜60日</th><th>61〜90日</th></tr>
    {tr}
  </table>
  <h2 style="margin-top:7mm">90日後に、この4つで自分を点検する</h2>
  <ul class="checks">{ck}</ul>
  <p class="note" style="margin-top:5mm">4つとも具体名詞で答えられるなら、市場がどう荒れてもポジションは残ります。
    答えられなかった項目は、次の90日の投資先です。もう一度この紙を印刷してください。</p>
  {FOOT % 'WORK 03'}
</div>'''


def build(with_pw):
    return ('<!DOCTYPE html><html lang="ja"><head><meta charset="utf-8">'
            '<title>AIエージェント時代のキャリア戦略 ワークシート</title>'
            '<style>%s</style></head><body>%s</body></html>'
            % (CSS, cover(with_pw) + work1() + work2() + work3()))


os.makedirs(FONTS, exist_ok=True)
open(OUT, 'w', encoding='utf-8').write(build(False))
open(OUT_PW, 'w', encoding='utf-8').write(build(True))
print('書きました:\n  公開版 %s\n  配布版 %s' % (OUT, OUT_PW))
