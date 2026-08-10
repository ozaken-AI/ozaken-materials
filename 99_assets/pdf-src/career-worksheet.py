#!/usr/bin/env python3
"""Udemy講座『AIエージェント時代のキャリア戦略』のワークシート（A4縦・6ページ）。

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

中身は講座の図版と1対1で対応させている。
  ワーク1 → Fig.7  目的の四象限          （第1部・長期の投資判断）
  ワーク2 → Fig.11 総合職の職務内容6つ    （第1部・長期の投資判断）
  ワーク3 → Fig.29 90日の実行計画        （第2部・締め）
  ワーク4 → Fig.25 30日で1業務を線に上げる（第2部・実務）
  ワーク5 → Fig.26 依頼文の4点セット      （第2部・実務）
講座を観ながら書けるように、図版の言い回しをそのまま使うこと。
言い換えると、受講者が「どの回のワークか」を見失う。

**紙面での並びは 1 → 2 → 4 → 5 → 3。** 講座の進行と同じ順にする。
ワーク3（90日）は最後のセクションなので、いちばん後ろに来る。
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
.promise{margin-top:5mm;padding:5mm;border-radius:4mm;
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
.rows td.q{width:42mm;background:rgba(46,84,150,.04)}
.rows td.q b{font-size:9.5pt;display:block;margin-bottom:1mm}
.rows td.q span{font-size:7.5pt;line-height:1.6;color:var(--muted)}
/* 記入例は、書く欄の隣に置いて、書いている間ずっと見えるようにする */
.rows td.e{width:52mm;background:rgba(46,84,150,.02);font-size:7.5pt;
  line-height:1.65;color:var(--muted)}
.rows td.a{height:19mm}
.plan{width:100%;border-collapse:collapse;margin-top:2mm}
.plan th{font-family:'HG';font-size:7.5pt;font-weight:700;letter-spacing:.12em;
  color:#fff;background:var(--navy);padding:2.5mm;text-align:center}
.plan th:first-child{text-align:left;width:44mm}
.plan td{border:1px solid var(--azure-pale);padding:2.4mm 3mm;height:12mm;vertical-align:top}
.plan td.n{background:rgba(46,84,150,.04);font-size:9pt;font-weight:700;vertical-align:middle}
.plan td.n span{display:block;font-weight:500;font-size:7.5pt;line-height:1.6;
  color:var(--muted);margin-top:1mm}
.checks{margin-top:2mm}
.checks li{list-style:none;display:flex;gap:3mm;align-items:flex-start;
  padding:2.3mm 0;border-bottom:1px solid rgba(46,84,150,.14);font-size:9pt;line-height:1.7}
.checks i{flex:none;width:4.5mm;height:4.5mm;border:1.4px solid var(--azure);
  border-radius:1mm;margin-top:1mm}
.checks em{font-style:normal;color:var(--muted);font-size:7.5pt;display:block;line-height:1.6}
/* 30日の日程（ワーク4）。日付と成果物を、行ごとに書き込ませる */
.pick{border:1.2px solid var(--azure);border-radius:3mm;padding:4mm 5mm;margin-top:1mm;
  background:rgba(46,84,150,.045)}
.pick .k{font-family:'HG';font-size:7pt;font-weight:700;letter-spacing:.14em;color:var(--azure)}
.pick .big{display:flex;align-items:flex-end;gap:3mm;margin-top:2mm}
.pick .big span{font-size:8.5pt;color:var(--muted);flex:none;padding-bottom:1mm}
.pick .big .line{flex:1;height:8mm;border-bottom:1.2px solid rgba(46,84,150,.5)}
.pick ul{display:flex;gap:5mm;margin-top:3mm}
.pick li{list-style:none;display:flex;gap:2mm;align-items:center;font-size:8pt;color:var(--muted)}
.pick i{flex:none;width:3.6mm;height:3.6mm;border:1.3px solid var(--azure);border-radius:.8mm}
.days{width:100%;border-collapse:collapse;margin-top:4mm}
.days th{font-family:'HG';font-size:7.5pt;font-weight:700;letter-spacing:.12em;
  text-align:left;color:#fff;background:var(--navy);padding:2.4mm 3mm}
.days td{border:1px solid var(--azure-pale);padding:2.4mm 3mm;vertical-align:middle;height:14.5mm}
.days td.d{width:20mm;background:rgba(46,84,150,.04);font-family:'HG';font-size:8.5pt;
  font-weight:700;text-align:center}
.days td.w{width:62mm;font-size:8.5pt;line-height:1.6}
.days td.w em{font-style:normal;display:block;font-size:7pt;color:var(--muted);margin-top:.6mm}
.days td.dt{width:24mm}
.days td.done{width:14mm;text-align:center}
.days td.done i{display:inline-block;width:4.2mm;height:4.2mm;
  border:1.3px solid var(--azure);border-radius:1mm}
/* 依頼文の記入欄（ワーク5） */
/* ①〜④の4点セットは2×2に組む。縦一列に6つ並べるとA4に収まらないうえ、
   4点セットと、その外側の⑤⑥という構造も見えなくなる */
.slots{display:grid;grid-template-columns:1fr 1fr;gap:2.5mm;margin-top:1mm}
.slots .slot{margin-bottom:0}
.slots2{margin-top:2.5mm}
.slot{border:1px solid var(--azure-pale);border-radius:2.5mm;padding:2.4mm 4mm;margin-bottom:2mm}
.slot.hi{border-color:var(--azure);background:rgba(46,84,150,.04)}
.slot h3{font-family:'SM';font-size:10pt;font-weight:600}
.slot p{font-size:7.5pt;line-height:1.6;color:var(--muted);margin:.5mm 0 1.6mm}
.slot .line{border-bottom:1px dotted rgba(46,84,150,.45);height:6mm}
/* 記入例。**書き込む線の上には置かない。** 手で書く場所と重なると、両方読めなくなる。
   薄い青の帯として、書きはじめる直前に置く */
.ex{border-left:2px solid rgba(46,84,150,.55);background:rgba(46,84,150,.05);
  padding:1.6mm 3mm;margin:0 0 2mm;border-radius:0 1.5mm 1.5mm 0}
.ex b{font-family:'HG';font-size:6.5pt;font-weight:700;letter-spacing:.14em;
  color:var(--azure);display:block;margin-bottom:.8mm}
.ex span{display:block;font-size:7.5pt;line-height:1.65;color:var(--muted)}
.ex span+span{margin-top:1mm}
.ex i{font-style:normal;font-weight:700;color:var(--azure)}
.ex .ng{color:rgba(226,55,68,.75)}
.ex .ng i{color:var(--red)}
/* 記入例の人物。表紙で一度だけ名乗らせる */
.who{margin-top:5mm;padding:4mm 5mm;border-radius:3mm;
  background:rgba(255,255,255,.05);border:1px solid rgba(216,228,240,.2)}
.who>b{font-family:'HG';font-size:7pt;font-weight:700;letter-spacing:.14em;
  color:var(--azure-pale);display:block;margin-bottom:1.5mm}
.who p{font-size:8.5pt;line-height:1.8;color:rgba(216,228,240,.85)}
.who p b{color:#fff}          /* 本文中の強調は行の中に置く。ラベルと同じ見た目にしない */
"""


FOOT = ('<div class="foot"><span>AIエージェント時代のキャリア戦略 ─ ワークシート</span>'
        '<span>OZAKEN / AICX %s</span></div>')


def cover(with_pw):
    key = (f'<p class="pw">PASSWORD　<b>{PW}</b></p>' if with_pw else
           '<p class="pw">PASSWORD　<b style="font-size:9pt;letter-spacing:.02em">'
           '講座の中でお伝えします</b></p>')
    return f'''<div class="page cover">
  <span class="tag">WORKSHEET ─ 6 PAGES</span>
  <h1>AIエージェント時代の<br>キャリア戦略 ワークシート</h1>
  <div class="rule"></div>
  <p class="sub">観るだけでは残りません。この5枚を書き終えたとき、はじめて講座が
    自分のキャリアの話になります。印刷して、手で書いてください。
    前半2枚が長期の投資判断、後半3枚が来週から動かす実務です。</p>
  <ul class="howto">
    <li><b>01</b><span><b>ワーク1｜目的の四象限。</b>いま抱えている仕事を5つ書き出し、
      4つの枠のどこに入るかを置きます。左下が3つ以上なら、時間の使い方から変えます。</span></li>
    <li><b>02</b><span><b>ワーク2｜職務内容の棚卸し。</b>「なんでもやってきました」は市場で0点。
      6つの項目に分けて、実績を具体名詞で紐づけます。</span></li>
    <li><b>03</b><span><b>ワーク4｜30日の実務。</b>業務を1つ選び、7つの行に日付を入れます。
      考える紙ではなく、予定を書く紙です。週3〜4時間で足ります。</span></li>
    <li><b>04</b><span><b>ワーク5｜依頼文の実物。</b>6日目に書く文を、ここで書き切ります。
      ⑤越えない線と⑥渡す材料まで書けて、ようやく実務で使えます。</span></li>
    <li><b>05</b><span><b>ワーク3｜90日の実行計画。</b>5つの投資先に日付を入れます。
      同時に全部は動きません。1か月目は導線づくりだけで十分です。</span></li>
  </ul>
  <div class="who">
    <b>記入例について</b>
    <p>5枚とも、<b>保険代理店のサポート担当（中小の代理店を30社担当）</b>という
      ひとりの記入例を通しで載せています。業種が違っても、粒度の目安として使えます。
      <b>薄い青の帯が記入例です。</b>そこには書かず、下の線から書きはじめてください。</p>
  </div>
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
         '内側から出ているが、まだ言葉になっていない。ここを言葉にすると、右上へ移ります',
         '新人が毎回同じところで詰まるのが、ずっと気になっている。'
         'なぜ気になるのかは、まだ説明できない', False),
        ('B', 'ここを増やす',
         '内側から出ていて、かつ人に説明できる。委譲もでき、枯れない。増やすのはここだけ',
         '代理店の事務担当が、手続きで消耗している。'
         'そこを軽くするのが自分の仕事だと、人に言える', True),
        ('C', 'まだ目的になっていない',
         '外から与えられ、言葉にもなっていない。最初に捨ててよい領域です',
         '上期の売上目標。なぜこの数字なのかを知らないまま追っている', False),
        ('D', '渡せるが、枯れやすい',
         '言葉になった、外から与えられた課題。AIに委譲できるが、解くほど速く消費されます',
         '月次レポートの作成。フォーマットも締切も決まっている', False),
    ]
    grid = ''.join(
        f'''<div class="cell{' hi' if hi else ''}">
      <span class="k">{k}</span><h3>{t}</h3><p>{d}</p>
      <div class="ex"><b>記入例</b><span>{ex}</span></div>
      {'<div class="line"></div>' * 4}
    </div>''' for k, t, d, ex, hi in cells)
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
        ('① 状況の解像度',
         '組織の政治、予算の出所、決裁者の関心。書かれていない一次情報を、どれだけ持っているか',
         '担当30社の、どの代理店がどの手続きで詰まるかを社名で言える。'
         '規程に書かれていない「例外扱いの3社」も把握している'),
        ('② 目的の設定',
         '解ける問題ではなく、解くべき問題を選んだ経験。「やらない」と決めたこと',
         '問い合わせ件数の削減ではなく、事務担当の残業を減らすことを目的に置き直した。'
         '件数が増える施策も通した'),
        ('③ 検証の基準',
         'AIや部下の出力を却下した経験。何を根拠に却下したかまで',
         'AIの回答案を、引いている条番号が改訂前のものだという理由で12件却下し、'
         '却下理由を一覧に残した'),
        ('④ 文脈翻訳',
         '営業の言葉を開発の言葉に。同じ日本語なのに通じない場所に、意味を通した仕事',
         '代理店が言う「手続きが面倒」を、システム部門に'
         '「入力項目が3つ多く、うち2つは既存データから引ける」と翻訳して伝えた'),
        ('⑤ 合意形成',
         '利害の違う人間を、ひとつの目的に束ねた経験。誰が何を諦めたかまで',
         '締切をめぐる営業と事務の対立を、月末3日前で合意させた。'
         '営業は駆け込み受付を、事務は当日対応を諦めた'),
        ('⑥ 全体設計',
         '部分最適の総和を、ひとつの成果に統合した経験',
         '問い合わせ・入力・確認をひとつの導線にまとめ、'
         '1件あたりの手続き時間を平均40分から24分にした'),
    ]
    tr = ''.join(f'''<tr><td class="q"><b>{n}</b><span>{d}</span></td>
      <td class="e">{ex}</td><td class="a"></td></tr>''' for n, d, ex in rows)
    return f'''<div class="page">
  <span class="tag">WORK 02 ─ SECTION 06</span>
  <h1>職務内容に、名前をつける</h1>
  <div class="rule"></div>
  <p class="sub">「なんでもやってきました」は市場で0点です。6つに分けて、
    <b>具体名詞で</b>書いてください。真ん中の列は、保険代理店のサポート担当の場合の記入例です。
    <b>この粒度まで書けて、はじめて名乗れます。</b></p>
  <table class="rows">
    <tr><th>職務内容</th><th>記入例</th><th>あなたの実績</th></tr>
    {tr}
  </table>
  <p class="note" style="margin-top:4mm">空欄が3つ以上あるなら、そこが次の90日の投資先です。
    埋まっている項目は、職務経歴書にその言葉のまま書けます。
    <b>数字と固有名詞が1つも入っていない行は、まだ書けていません。</b></p>
  {FOOT % 'WORK 02'}
</div>'''


def work3():
    rows = [
        ('Howを満たす', '要求水準を淡々とクリアする。ここに人生を賭けない'),
        ('一次情報の導線', '生身の困りごとに触れる場を1つ'),
        ('下積みを自己発注', '小さく企画し、自分で刈り取る'),
        ('週15分のループ', '外した判断の前提を書き出す'),
        ('職務内容の棚卸し', 'ワーク2の6項目に紐づける'),
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
  <span class="tag">WORK 03 ─ SECTION 15</span>
  <h1>90日の計画に、日付を入れる</h1>
  <div class="rule"></div>
  <p class="sub">やることではなく、<b>いつやるか</b>を書きます。
    同時に全部は動きません。1か月目は導線づくりだけで十分です。</p>
  <div class="ex">
    <b>記入例 ─ 一次情報の導線</b>
    <span><i>1〜30日：</i>代理店3社に同行を申し込む（4/15までに連絡）</span>
    <span><i>31〜60日：</i>月2回の同行を固定。困りごとをその場でメモに起こす</span>
    <span><i>61〜90日：</i>拾った困りごとを1つ選び、社内に企画として出す</span>
    <span class="ng"><i>書けていない例：</i>「一次情報に触れる機会を増やす」──
      いつ・誰に・何をするかが無いものは、90日後にそのまま残ります</span>
  </div>
  <table class="plan">
    <tr><th>投資先</th><th>1〜30日</th><th>31〜60日</th><th>61〜90日</th></tr>
    {tr}
  </table>
  <h2 style="margin-top:4mm">90日後に、この4つで自分を点検する</h2>
  <ul class="checks">{ck}</ul>
  <p class="note" style="margin-top:3mm">4つとも具体名詞で答えられるなら、市場がどう荒れてもポジションは残ります。
    答えられなかった項目は、次の90日の投資先です。もう一度この紙を印刷してください。</p>
  {FOOT % 'WORK 03'}
</div>'''


def work4():
    """Fig.24 と同じ7行。ここだけは「考える紙」ではなく「予定を書く紙」にする。

    抽象的な設問ばかりだと、書き終えても月曜に手が動かない。
    日付欄と済チェックを置いて、机上の計画を実行の記録に変える。
    """
    days = [
        ('1〜3日', '直近30件の問い合わせを書き出す', '問い合わせ一覧（表1枚）'),
        ('4〜5日', 'ベテランに「どう見分けているか」を聞く', '判断の分かれ目メモ'),
        ('6〜10日', '依頼文を1本書き、過去10件で試す', '依頼文（4点セット＝ワーク5）'),
        ('11〜15日', '外した回だけ、理由を書いて依頼文を直す', '却下ログ（外した理由）'),
        ('16〜20日', '固まった依頼文を、型として保存する', '業務ボット1つ'),
        ('21〜25日', '同僚2人に使ってもらい、横で見る', '使い方メモ（A4半分）'),
        ('26〜30日', '抜き取りの基準と、止める線を決める', '監督手順書（A4半分）'),
    ]
    tr = ''.join(f'''<tr><td class="d">{d}</td>
      <td class="w">{w}<em>作るもの：{o}</em></td>
      <td class="dt"></td><td class="done"><i></i></td></tr>''' for d, w, o in days)
    return f'''<div class="page">
  <span class="tag">WORK 04 ─ SECTION 13</span>
  <h1>1つの業務を、30日で「線」に上げる</h1>
  <div class="rule"></div>
  <p class="sub">ここから先は、考える紙ではなく<b>予定を書く紙</b>です。
    業務を1つだけ選び、7つの行に日付を入れてください。週3〜4時間で足ります。</p>
  <div class="pick">
    <span class="k">STEP 0 ─ 選ぶ</span>
    <div class="big"><span>取り上げる業務</span><div class="line"></div></div>
    <ul>
      <li><i></i>毎週やっている</li>
      <li><i></i>社内で完結する</li>
      <li><i></i>自分が当事者である</li>
    </ul>
  </div>
  <div class="ex" style="margin-top:3mm">
    <b>記入例</b>
    <span><i>取り上げる業務：</i>契約変更手続きの問い合わせ対応（週に10件ほど・社内で完結・自分が一次窓口）</span>
    <span><i>やる日：</i>4/7 → 4/10 → 4/13 → 4/20 → 4/27 → 5/2 → 5/7。
      週に1コマ（3〜4時間）を先に予定へ入れると、ちょうど30日に収まります</span>
    <span class="ng"><i>選ばないほうがいい例：</i>年に1回の契約更改（頻度が低い）／
      顧客へ直接出す書類（社内で完結しない）／他部署から頼まれた集計（当事者でない）</span>
  </div>
  <table class="days">
    <tr><th>日</th><th>やること／作るもの</th><th>やる日</th><th>済</th></tr>
    {tr}
  </table>
  <p class="note" style="margin-top:4mm">3つのチェックが揃わない業務を選ぶと、
    たいてい2週目で止まります。人に頼まれた業務では、外した理由を書く手が動きません。
    30日後に手元に残るのは、ボットではなく上の<b>5枚の紙</b>のほうです。</p>
  {FOOT % 'WORK 04'}
</div>'''


def work5():
    slots = [
        ('① あなたは誰か', '肩書きではなく、立場と担当範囲',
         '保険代理店のサポート担当。中小の代理店を30社ほど担当している', 2, False),
        ('② 相手は誰か', '誰が、何に、どのくらいの頻度で困っているか',
         '代理店の事務担当者。契約変更の手続きで、月に2〜3回問い合わせてくる', 2, False),
        ('③ 何をしてほしいか', '出力の中身を1つに絞る。2つ以上頼むと、どちらも浅くなる',
         '下に貼る問い合わせに対する、一次回答の案を1つ', 2, False),
        ('④ どういう形で欲しいか', '長さ・体裁・根拠の出し方まで指定する',
         '300字以内。根拠にした規程の条番号を、最後に並べる', 2, False),
        ('⑤ 越えない線', '<b>ここが無いと、平気で作文します。</b>規程の外に出たときの振る舞いを、先に決める',
         '規程に書かれていないことは推測せず「確認が必要」と書く', 2, True),
        ('⑥ 渡す材料', '<b>ここが無いと、一般論しか返ってきません。</b>要約せず、そのまま貼るのが要点',
         '過去の類似回答を3件、原文のまま貼る（要約した時点で、判断の分かれ目が消える）', 2, True),
    ]
    def box(t, d, ex, n, hi):
        return (f'<div class="slot{" hi" if hi else ""}">'
                f'<h3>{t}</h3><p>{d}</p>'
                f'<div class="ex"><b>記入例</b><span>{ex}</span></div>'
                + '<div class="line"></div>' * n + '</div>')
    four = ''.join(box(*x) for x in slots[:4])
    two = ''.join(box(*x) for x in slots[4:])
    return f'''<div class="page">
  <span class="tag">WORK 05 ─ SECTION 13</span>
  <h1>6日目に書く、依頼文の実物</h1>
  <div class="rule"></div>
  <p class="sub">ワーク4の6〜10日で書くものです。ここで書いた文が、そのまま型の原型になります。
    <b>①〜④が4点セット、⑤と⑥は実務で必ず要る2つ</b>です。</p>
  <div class="slots">{four}</div>
  <div class="slots2">{two}</div>
  <p class="note" style="margin-top:3mm">1発で当てようとしないでください。
    過去10件で試して、外した回だけ理由を書いて直す。この往復が型をつくります。
    却下した理由を書き残した紙が、そのまま「検証の基準」の証拠になります。</p>
  {FOOT % 'WORK 05'}
</div>'''


def build(with_pw):
    return ('<!DOCTYPE html><html lang="ja"><head><meta charset="utf-8">'
            '<title>AIエージェント時代のキャリア戦略 ワークシート</title>'
            '<style>%s</style></head><body>%s</body></html>'
            % (CSS, cover(with_pw) + work1() + work2() + work4() + work5() + work3()))


os.makedirs(FONTS, exist_ok=True)
open(OUT, 'w', encoding='utf-8').write(build(False))
open(OUT_PW, 'w', encoding='utf-8').write(build(True))
print('書きました:\n  公開版 %s\n  配布版 %s' % (OUT, OUT_PW))
