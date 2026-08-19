#!/usr/bin/env python3
"""業務変革大全（配布用PDF）のHTMLを組む。

AX資料（01_概念・思想/ax-article.html）のプロセス論を土台にする。
  DX＝データの軸／AX＝プロセスの軸。直交する
  AXは3フェーズ 効率化 Optimize → 再構築 Redesign → 代替 Autonomy
  本当のAXは②再構築から始まる
この骨格を、実務に落とす手順として展開したものが本資料。

A4横・1ページ1テーマ。書体は資料と同じものを file:// で読ませるため、
書体フォルダの中にHTMLを書き出す（make_ogp.mjs と同じ理由）。
"""
import os
import sys

S = '/home/user/ozaken-materials/.claude/skills/ozaken-shiryo/scripts'
sys.path.insert(0, S)
from domain_fig import (fig_map, fig_stairs, fig_gap, fig_tree, fig_cols,
                        fig_matrix, fig_cycle, fig_issues, fig_check)

FONT_DIR = '/tmp/ozaken-ogp-fonts'

CSS = """
@font-face{font-family:'OZ Mincho';src:url('ShipporiMinchoB1-Bold.ttf');font-weight:700}
@font-face{font-family:'OZ Gothic';src:url('ZenKakuGothicNew-Medium.ttf');font-weight:500}
@font-face{font-family:'OZ Gothic';src:url('ZenKakuGothicNew-Bold.ttf');font-weight:700}
@font-face{font-family:'OZ En';src:url('HankenGrotesk.ttf')}
:root{
  --paper:#f8f7f4; --navy:#1f3864; --navy-deep:#141d35; --azure:#2e5496;
  --azure-pale:#d8e4f0; --ink:#1a1a2e; --muted:#6b7a99; --red:#e23744;
  --red-bright:#ff5d6a; --white:#ffffff; --pale:#eef3fa;
}
@page{size:A4 landscape;margin:0}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'OZ Gothic',sans-serif;color:var(--ink);
  -webkit-print-color-adjust:exact;print-color-adjust:exact}
.page{width:297mm;height:210mm;position:relative;overflow:hidden;
  page-break-after:always;background:var(--paper);
  padding:14mm 16mm 12mm;display:flex;flex-direction:column}
.page:last-child{page-break-after:auto}
.page.navy{background:linear-gradient(172deg,#1f3864 0%,#141d35 100%);color:#fff}
.page.navy .lead{color:rgba(255,255,255,.86)}
.page.navy .card{background:rgba(255,255,255,.06);border-color:rgba(255,255,255,.16)}
.page.navy .card h3{color:#fff}
.page.navy .card p{color:rgba(255,255,255,.76)}
.page.navy .eyebrow{background:rgba(255,255,255,.16);color:#fff}
.page.navy .pnum{color:rgba(255,255,255,.5)}
.eyebrow{display:inline-block;font-family:'OZ En',sans-serif;font-size:8.5pt;
  font-weight:700;letter-spacing:.14em;color:var(--azure);background:var(--azure-pale);
  padding:3px 9px;border-radius:4px;align-self:flex-start}
h2{font-family:'OZ Mincho',serif;font-size:19pt;font-weight:700;line-height:1.42;
  margin:6px 0 4px;letter-spacing:.01em}
.lead{font-size:9.5pt;line-height:1.75;color:var(--muted);max-width:230mm}
.page.navy h2{color:#fff}
.fig{flex:1;display:flex;align-items:center;justify-content:center;
  margin:5px 0 4px;min-height:0}
.fig svg{max-width:100%;max-height:100%;height:auto}
.cards{display:grid;grid-template-columns:repeat(3,1fr);gap:6mm}
.cards.two{grid-template-columns:repeat(2,1fr)}
.card{background:#fff;border:1px solid rgba(46,84,150,.18);border-radius:7px;
  padding:5mm 5.5mm;border-top:2.5px solid var(--azure)}
.card h3{font-family:'OZ Mincho',serif;font-size:10.5pt;font-weight:700;
  margin-bottom:2.5mm;line-height:1.5}
.card p{font-size:8.6pt;line-height:1.72;color:var(--muted)}
.card b{color:var(--ink);font-weight:700}
.page.navy .card b{color:#fff}
.tag{display:inline-block;font-family:'OZ En',sans-serif;font-size:7pt;font-weight:700;
  letter-spacing:.1em;color:var(--azure);background:var(--azure-pale);
  padding:1.5px 6px;border-radius:3px;margin-right:5px;vertical-align:2px}
.page.navy .tag{color:#fff;background:rgba(255,255,255,.18)}
.pnum{position:absolute;right:16mm;bottom:7mm;font-family:'OZ En',sans-serif;
  font-size:8pt;letter-spacing:.12em;color:var(--muted)}
.foot{position:absolute;left:16mm;bottom:7mm;font-size:7.6pt;color:var(--muted);
  letter-spacing:.02em}
.page.navy .foot{color:rgba(255,255,255,.5)}

/* ── 表紙・裏表紙 ── */
.cover{background:
  radial-gradient(ellipse 60% 46% at 50% 40%, rgba(46,84,150,.35) 0%, transparent 55%),
  radial-gradient(ellipse 70% 55% at 50% -5%, rgba(46,84,150,.60), transparent 62%),
  radial-gradient(ellipse 55% 45% at 88% 94%, rgba(255,93,106,.16), transparent 60%),
  linear-gradient(165deg,#1f3864 0%,#182a52 42%,#141d35 100%);
  color:#fff;justify-content:center;align-items:flex-start;padding:0 26mm}
.cover .bar{position:absolute;left:0;top:0;bottom:0;width:7mm;background:var(--red)}
.cover .tex{position:absolute;inset:0;opacity:.13}
.cover h1{font-family:'OZ Mincho',serif;font-size:34pt;font-weight:700;
  line-height:1.4;letter-spacing:.01em;position:relative}
.cover h1 .hl{color:var(--red-bright)}
.cover .sub{font-size:12pt;line-height:1.9;color:rgba(216,228,240,.82);
  margin-top:8mm;max-width:190mm;position:relative}
.cover .who{position:absolute;left:26mm;bottom:16mm;font-size:9.5pt;
  color:rgba(216,228,240,.72)}
.cover .who b{color:#fff;font-size:11pt;font-weight:700}
.cover .eyebrow{position:relative;margin-bottom:6mm}
.close{justify-content:center;align-items:center;text-align:center}
.close h2{font-size:24pt;line-height:1.55;max-width:220mm}
.close .lead{font-size:11pt;color:rgba(255,255,255,.8);margin-top:7mm;max-width:200mm}
"""

TEX = """<svg class="tex" viewBox="0 0 1200 600" preserveAspectRatio="none">
<defs><pattern id="pg" width="46" height="46" patternUnits="userSpaceOnUse">
<path d="M46 0H0V46" fill="none" stroke="#fff" stroke-width="0.7"/></pattern></defs>
<rect width="1200" height="600" fill="url(#pg)"/>
<circle cx="240" cy="120" r="4" fill="#fff"/><circle cx="560" cy="300" r="4" fill="#fff"/>
<circle cx="880" cy="160" r="4" fill="#fff"/><circle cx="1060" cy="430" r="4" fill="#fff"/>
<path d="M240 120L560 300L880 160L1060 430" stroke="#fff" stroke-width="1" fill="none"/>
</svg>"""

P = []


def only_svg(figure_html):
    """domain_fig の返り値から <svg> だけを抜く。PDFでは図の枠が二重になるため"""
    i = figure_html.find('<svg')
    j = figure_html.rfind('</svg>') + 6
    return figure_html[i:j]


def cap_of(figure_html):
    import re
    m = re.search(r'<p class="fig-cap">([\s\S]*?)</p>', figure_html)
    return re.sub(r'<[^>]+>', '', m.group(1)).strip() if m else ''


def page(n, eyebrow, title, lead, figure, cards, navy=False):
    cs = ''.join('<div class="card"><h3>%s</h3><p>%s</p></div>' % (h, b)
                 for h, b in cards)
    P.append(
        '<div class="page%s">'
        '<span class="eyebrow">%s</span><h2>%s</h2><p class="lead">%s</p>'
        '<div class="fig">%s</div>'
        '<div class="cards%s">%s</div>'
        '<div class="foot">業務変革大全 ─ AXは、プロセスを動かす</div>'
        '<div class="pnum">%02d</div></div>'
        % (' navy' if navy else '', eyebrow, title, lead,
           only_svg(figure), ' two' if len(cards) == 2 else '', cs, n))


# ── 01 表紙 ──────────────────────────────────────────────────
P.append(
    '<div class="page cover"><div class="bar"></div>' + TEX +
    '<span class="eyebrow">Business Process Transformation</span>'
    '<h1>業務変革大全<br>AXは、<span class="hl">プロセス</span>を動かす</h1>'
    '<p class="sub">DXが整えたのは「見える」基盤でした。'
    'プロセスを回す主体は、人のまま残されています。'
    'AIエージェントが加わったいま、変革の主語はデータからプロセスへ移りました。'
    '本資料は、その変革を実務の手順に落としたものです。</p>'
    '<div class="who"><b>小澤健祐（おざけん）</b>　一般社団法人AICX協会 代表理事<br>'
    'ozaken-ai.github.io/ozaken-materials</div></div>')

# ── 02 DXとAX ────────────────────────────────────────────────
page(2, 'Section 01 ─ Two Axes',
     'DXは「見える」をつくり、AXは「動く」をつくる',
     'DXは横の軸、AXは縦の軸。二つは対立するものではなく、直交します。'
     'データがどれだけ整っても、回すのが人のままなら、それはDXの完成にすぎません。',
     fig_map('データの活用', 'プロセスの自律', [
         ('手作業・属人化', 14, 12, 1, '人が集め、人が回す'),
         ('データドリブン', 84, 18, 0, 'DXの到達点。見えるが、動かない'),
         ('部分的な自動化', 30, 58, 2, '渡すものが薄いまま、任せた状態'),
         ('AIネイティブ', 86, 88, 3, '整ったデータの上を、AIが回す'),
     ], '', '', dark=True,
        corners=[(86, 92, 'ここが目的地')]),
     [('<span class="tag">DX</span>データの軸',
       '紙をデータに、バラバラの記録をつなぎ、可視化して意思決定に活かす。'
       '<b>右へ進むほど、判断の材料が整います</b>。'),
      ('<span class="tag">AX</span>プロセスの軸',
       'AIが業務を実行し、やがて自律する。'
       '<b>上へ昇るほど、人がプロセスから手を離せます</b>。'),
      ('<span class="tag">注意</span>右だけ進んでも動かない',
       'データを貯めて見せるところで止まると、'
       '判断も実行も人のままです。<b>縦の軸を足して初めて、'
       '整えたデータが「動く力」になります</b>。')],
     navy=True)

# ── 03 3フェーズ ─────────────────────────────────────────────
page(3, 'Section 02 ─ Three Phases',
     '業務変革は、3つのフェーズで進む',
     'AXは一足飛びには進みません。既存のプロセスとAIの関わり方が深まるにつれて、'
     '変革は段階を踏みます。自社がいまどこにいて、次にどこへ進むのか。'
     'AXを語るとは、煎じ詰めればこの問いに答えることです。',
     fig_stairs([
         ('PHASE 01', '効率化', '人が主導する', 'Optimize',
          'プロセスの形は変えず、AIを道具として乗せる', 0),
         ('PHASE 02', '再構築', '人が設計する', 'Redesign',
          'AIが動くことを前提に、手順そのものを組み直す', 1),
         ('PHASE 03', '代替', '人は監督する', 'Autonomy',
          'AIが端から端まで自走し、人は例外と設計へ移る', 3),
     ], '', '', note=''),
     [('<span class="tag">01</span>効率化 ── AXの入口',
       '下書き・要約・定型作業をAIが肩代わりし、スピードと量が上がる。'
       '価値はありますが、<b>プロセスの形は何ひとつ変わっていません</b>。'),
      ('<span class="tag">02</span>再構築 ── ここから本当のAX',
       '人のために最適化されてきた手順を、AI前提で組み直す。'
       '<b>効率化から変革へ、質が変わるのはこのフェーズから</b>です。'),
      ('<span class="tag">03</span>代替 ── 主役が入れ替わる',
       '人は個別の実行から退き、例外対応と監督、そして次の設計へ。'
       'プロセスの主役が、人からAIへ移ります。')])

# ── 04 断層 ──────────────────────────────────────────────────
page(4, 'Section 03 ─ The Gap',
     'ほとんどの会社は、①効率化で止まっている',
     '議事録が速くなった、メールを下書きさせた。それも価値です。'
     'ただし<b>手順が変わっていない限り、成果は個人の時短にとどまります</b>。'
     '効率化で満足した会社と、再構築まで行った会社の差は、'
     'これから数年で取り返しのつかない開きになります。',
     fig_gap([
         ('AIで下書きを作らせる', '下書きを前提に、確認の工程を減らす'),
         ('議事録を自動で書く', '議事録を書く前提で、会議の持ち方を変える'),
         ('問い合わせに一次回答する', '一次回答を前提に、担当の配置を組み直す'),
         ('個人の作業時間が減る', '業務の総量と、通し方そのものが変わる'),
     ], '', '', uid='bpt4',
        left_label='① 効率化 ── 形は変えない',
        right_label='② 再構築 ── 形を組み直す'),
     [('<span class="tag">見分け方</span>手順書が書き換わったか',
       '効率化で止まっている組織は、<b>手順書が以前のまま</b>です。'
       '再構築に入った組織は、工程の数と順番そのものが変わります。'),
      ('<span class="tag">よくある誤解</span>①を積み上げれば②になる',
       'なりません。<b>①は同じ手順を速くする営み、'
       '②は手順を捨てて組み直す営み</b>で、向きが違います。'),
      ('<span class="tag">分かれ目</span>誰が手順を決めるか',
       '①は現場が各自で工夫します。'
       '②は<b>誰かが手順を設計し直さないと始まりません</b>。'
       'ここに人を置けるかが、実質的な分岐点です。')],
     navy=True)

# ── 05 単位 ──────────────────────────────────────────────────
page(5, 'Section 04 ─ The Unit',
     '変革の単位は「業務」ではなく、「工程」',
     '「この業務をAIに」と言っている限り、どこにも入りません。'
     '一つの業務は複数の工程でできていて、AIが強い工程と、'
     '人が持つべき工程が混ざっています。'
     '<b>ほどいてから当てる</b>。順番はこちらです。',
     fig_tree('ひとつの業務', [
         ('調べる', ['社内の前例を探す', '外部の情報を集める', '条件を確認する']),
         ('決める', ['選択肢を並べる', '基準に照らす', '責任者が承認する']),
         ('作る', ['下書きを書く', '体裁を整える', '数字を差し込む']),
         ('通す', ['関係者に回す', '指摘を反映する', '記録を残す']),
     ], '', '', uid='bpt5'),
     [('<span class="tag">配分</span>AIが強いのは「調べる」と「作る」',
       '「決める」と「通す」は人が持ちます。'
       '<b>この配分を先に決めてから、道具を選びます</b>。'),
      ('<span class="tag">目安</span>新人に口頭で説明できるか',
       'ほどけているかどうかの判定です。'
       '<b>説明できない工程は、AIにも渡せません</b>。'),
      ('<span class="tag">選び方</span>回数の多い工程から',
       '削減時間は「1回あたり×年間回数」で決まります。'
       '効くのは地味で回数の多い工程。'
       '派手な業務から選ぶと、たいてい外します。')])

# ── 06 組み替え ──────────────────────────────────────────────
page(6, 'Section 05 ─ Redesign',
     'AI前提で組み替える、4つの型',
     '再構築とは、工程を消す・移す・分ける・順番を変えるという、'
     '4つの操作の組み合わせです。'
     '<b>新しい工程を足すのではなく、いまある工程をどう扱うか</b>で考えると、'
     '現場でも議論できる形になります。',
     fig_cols([
         ('REMOVE', '消す', 'そもそも要らなくなる工程',
          '「あとで確認できるように」だけを目的にした転記や集計。'
          'AIがその場で引けるなら、工程ごと消えます。', 1),
         ('SHIFT', '移す', '人からAIへ、工程を移す',
          '調べる・作るを移し、決める・通すは残す。'
          '移した先で品質が落ちないかは、差し戻しの数で見ます。', 0),
         ('SPLIT', '分ける', '一括の工程を、判断で割る',
          '「確認する」を、機械的な確認と判断を伴う確認に割る。'
          '前者だけを任せると、後者に時間を使えます。', 2),
         ('REORDER', '並べ替える', '順番そのものを変える',
          '人が待つ前提で組まれた順番を崩す。'
          '並行して走らせられる工程は、AIなら同時に回せます。', 3),
     ], '', '', dark=True),
     [('<span class="tag">最初にやる</span>「消す」から入る',
       '移す・分けるの前に、<b>そもそも要らない工程を落とす</b>。'
       'AIに移してから消すと、二度手間になります。'),
      ('<span class="tag">効きが大きい</span>並べ替え',
       '人が待つ前提の順番は、想像以上に多い。'
       '<b>順番を変えるだけで、期間が半分になることがあります</b>。'),
      ('<span class="tag">やらないこと</span>全工程を一度に触る',
       '1業務・4工程くらいが、一度に扱える上限です。'
       '広げると、どこが効いたのか分からなくなります。')],
     navy=True)

# ── 07 委譲範囲 ──────────────────────────────────────────────
page(7, 'Section 06 ─ Delegation',
     'どこまで任せ、どこで止めるか',
     '機能名で仕分けると必ず迷います。'
     '<b>やり直しがきくか、件数が多いか</b>。'
     'この2つで切ると、着手の順番はほぼ自動的に決まります。',
     fig_matrix(
         ['件数が多い', '件数が少ない'],
         [('やり直しがきく', ['今週から任せる', 'あとで任せる']),
          ('取り消しにくい', ['下書きまで任せ、人が通す', 'まだ人が持つ']),
          ('渡すもの', ['手順と判断基準', '目的と制約']),
          ('止め方', ['出す前に人が通す', '実行前に承認を挟む']),
          ('効果の出方', ['回数が効く。すぐ数字になる', '一件が重い。質で効く'])],
         '', '', note=''),
     [('<span class="tag">最初の対象</span>社外に直接出ないもの',
       '部内で完結する工程から始めます。'
       '<b>失敗しても、部内で吸収できる範囲に留まります</b>。'),
      ('<span class="tag">境界</span>取り消せないものは渡さない',
       '取引の最終決定、人の処遇、対外的な確約。'
       'ここを急ぐと、<b>取り返しがつかないうえに信頼ごと失います</b>。'),
      ('<span class="tag">同時に決める</span>越えてよい線と、止める人',
       '任せる範囲を決めるときに、必ずセットで決めます。'
       '<b>あとから決めようとすると、決まりません</b>。')])

# ── 08 定着 ──────────────────────────────────────────────────
page(8, 'Section 07 ─ Adoption',
     '定着は、回し続けるループとして設計する',
     '一度決めて終わりの委譲は、半年で実態と乖離して誰も見なくなります。'
     '<b>範囲を決め、止め方を用意し、差し戻しの理由を貯め、'
     'それを使って範囲を広げる</b>。'
     'この4つが回り続けて、はじめて定着します。',
     fig_cycle([
         ('範囲を決める', '何を、どこまで任せるか'),
         ('止め方を置く', '逸脱の止め方を先に用意する'),
         ('理由を残す', '差し戻した理由を捨てない'),
         ('範囲を広げる', '貯まった理由で基準を更新する'),
     ], '', '', center='定着ループ', uid='bpt8'),
     [('<span class="tag">いちばん落ちる</span>3つ目の「理由を残す」',
       '修正してそのまま出してしまう。'
       '<b>ここが抜けている組織は、1年経っても全件確認から抜けられません</b>。'),
      ('<span class="tag">量</span>一行で足ります',
       '「前提条件が抜けていたため」程度の一行で十分です。'
       '<b>3か月貯まると、それが判断基準になります</b>。'),
      ('<span class="tag">切り替え</span>条件を数字で先に決める',
       '「差し戻しが2週続けて5%を下回ったら抜き取りへ」。'
       '決めておかないと、永久に全件確認が続きます。')],
     navy=True)

# ── 09 失敗 ──────────────────────────────────────────────────
page(9, 'Section 08 ─ Pitfalls',
     'よくある失敗は、だいたいこの5つ',
     'どれも技術の問題ではありません。'
     '<b>変革の単位、順番、そして誰が手順を決めるか</b>。'
     'この3つのどこかを取り違えたときに起きます。',
     fig_issues([
         ('道具から入る', 'どのツールかの議論で止まる'),
         ('業務単位で考える', '工程にほどかず、入口が見つからない'),
         ('効率化で満足する', '手順が変わらず、総量が減らない'),
         ('設計者がいない', '各自の工夫のまま、横に伝わらない'),
         ('理由を残さない', '全件確認から抜けられない'),
     ], '', '', uid='bpt9'),
     [('<span class="tag">最多</span>効率化で満足してしまう',
       '個人の時短は出ているので、成功に見えます。'
       '<b>総量と手順が変わっていないことに、しばらく気づけません</b>。'),
      ('<span class="tag">構造</span>設計者がいないと、②に入れない',
       '再構築は、誰かが手順を引き直さないと始まりません。'
       '<b>使う人でも作る人でもない、第三の役割が要ります</b>。'),
      ('<span class="tag">回避</span>1業務・4工程・90日',
       '範囲を先に区切ると、5つの失敗はほとんど起きません。'
       '広げるのは、1周まわしてからです。')])

# ── 10 90日と診断 ────────────────────────────────────────────
page(10, 'Section 09 ─ First 90 Days',
     '最初の90日と、自社診断',
     '大きな構想は要りません。'
     '<b>1つの業務を選び、工程にほどき、1つの工程を任せて、'
     '差し戻しの理由を残す</b>。'
     'この一周を90日で終えると、次に何をすべきかが自社の言葉で言えるようになります。',
     fig_check([
         (False, '「どのツールを入れるか」から議論が始まっている',
          '道具の議論は、任せる工程が決まってからです'),
         (False, '成果の報告が、利用率と時短時間になっている',
          '手順が変わっていなくても、その数字は上がります'),
         (False, '手順を引き直す担当が、誰も決まっていない',
          '再構築は、設計する人がいないと始まりません'),
         (True, '1業務を工程にほどき、任せる工程を1つ決めてある',
          'ここまで決まっていれば、90日で一周できます'),
         (True, '差し戻した理由を、その場で一行残す運用になっている',
          '3か月後に、それが判断基準として使えるようになります'),
     ], '', '', note=''),
     [('<span class="tag">Day 1-30</span>選んで、ほどく',
       '判断が多く、記録がある業務を1つ。'
       '工程まで分解して、任せる工程を1つ決めます。'),
      ('<span class="tag">Day 31-60</span>任せて、理由を残す',
       '80点で動かし、差し戻した理由を一行ずつ残す。'
       '<b>完璧な設計を待たないほうが、結果として速い</b>。'),
      ('<span class="tag">Day 61-90</span>測って、次を決める',
       '工程の所要時間×年間回数で金額に換算する。'
       'この2つの数字が、次の投資判断をそのまま決めます。')])

# ── 11 締め ──────────────────────────────────────────────────
P.append(
    '<div class="page navy close">' +
    '<span class="eyebrow">Conclusion</span>'
    '<h2>変革の主語が、<br>データからプロセスへ移った</h2>'
    '<p class="lead">DXがデータの土台を整え、その上でAXがプロセスを動かす。'
    '両者は競合ではなく、接続する関係にあります。'
    'いま問われているのは、自社のデータをどこまで「動く力」に変えられるか。'
    'その一点に尽きます。<br><br>'
    'そして動く力に変える作業は、システムの導入ではありません。'
    '<b style="color:#fff">いまある手順を、工程にほどいて、組み直す</b>という、'
    'きわめて地道な仕事です。'
    'だからこそ、外から買うことができません。</p>'
    '<div class="foot">業務変革大全 ─ AXは、プロセスを動かす　'
    '｜　小澤健祐（おざけん）／ 一般社団法人AICX協会</div>'
    '<div class="pnum">11</div></div>')

html = ('<!DOCTYPE html><html lang="ja"><head><meta charset="utf-8">'
        '<title>業務変革大全</title><style>%s</style></head><body>%s</body></html>'
        % (CSS, ''.join(P)))
out = os.path.join(FONT_DIR, 'bpt.html')
open(out, 'w', encoding='utf-8').write(html)
print('%s に書き出しました（%dページ / %d文字）' % (out, len(P), len(html)))
