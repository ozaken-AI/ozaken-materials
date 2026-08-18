#!/usr/bin/env python3
"""放送大学 第11回「AIエージェント」講義資料（配布用PDF）のHTMLを組む。

01_concept/ai-agent-mechanics.html の本文を、16:9の配布用PDFに焼き直したもの。
内容はスライド資料と一対一対応。図版は domain_fig の <svg> だけを抜いて使う。

16:9（338.67mm × 190.5mm）。書体は資料と同じものを file:// で読ませるため、
書体フォルダの中にHTMLを書き出す（make_ogp.mjs と同じ理由）。
"""
import os
import sys

S = '/home/user/ozaken-materials/.claude/skills/ozaken-shiryo/scripts'
sys.path.insert(0, S)
from domain_fig import fig_gap, fig_cycle, fig_ladder, fig_flow, fig_cols, fig_map, fig_check

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
@page{size:338.67mm 190.5mm;margin:0}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'OZ Gothic',sans-serif;color:var(--ink);
  -webkit-print-color-adjust:exact;print-color-adjust:exact}
.page{width:338.67mm;height:190.5mm;position:relative;overflow:hidden;
  page-break-after:always;background:var(--paper);
  padding:11mm 18mm 10mm;display:flex;flex-direction:column}
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
h2{font-family:'OZ Mincho',serif;font-size:18pt;font-weight:700;line-height:1.4;
  margin:5px 0 3px;letter-spacing:.01em}
.lead{font-size:9.3pt;line-height:1.7;color:var(--muted);max-width:270mm}
.page.navy h2{color:#fff}
.fig{flex:1;display:flex;align-items:center;justify-content:center;
  margin:5px 0 4px;min-height:0}
.fig svg{max-width:100%;max-height:100%;height:auto}
.cards{display:grid;grid-template-columns:repeat(3,1fr);gap:7mm}
.cards.two{grid-template-columns:repeat(2,1fr)}
.card{background:#fff;border:1px solid rgba(46,84,150,.18);border-radius:7px;
  padding:4mm 4.6mm;border-top:2.5px solid var(--azure)}
.card h3{font-family:'OZ Mincho',serif;font-size:10pt;font-weight:700;
  margin-bottom:2.2mm;line-height:1.5}
.card p{font-size:8.2pt;line-height:1.68;color:var(--muted)}
.card b{color:var(--ink);font-weight:700}
.page.navy .card b{color:#fff}
.tag{display:inline-block;font-family:'OZ En',sans-serif;font-size:7pt;font-weight:700;
  letter-spacing:.1em;color:var(--azure);background:var(--azure-pale);
  padding:1.5px 6px;border-radius:3px;margin-right:5px;vertical-align:2px}
.page.navy .tag{color:#fff;background:rgba(255,255,255,.18)}

.pnum{position:absolute;right:18mm;bottom:6mm;font-family:'OZ En',sans-serif;
  font-size:8pt;letter-spacing:.12em;color:var(--muted)}

.foot{position:absolute;left:18mm;bottom:6mm;font-size:7.6pt;color:var(--muted);
  letter-spacing:.02em}
.page.navy .foot{color:rgba(255,255,255,.5)}

/* 出典 */
.src{margin-top:3mm;font-size:7.4pt;line-height:1.6;color:var(--muted)}
.page.navy .src{color:rgba(255,255,255,.55)}

/* ── 表紙・裏表紙 ── */
.cover{background:
  radial-gradient(ellipse 60% 46% at 50% 40%, rgba(46,84,150,.35) 0%, transparent 55%),
  radial-gradient(ellipse 70% 55% at 50% -5%, rgba(46,84,150,.60), transparent 62%),
  radial-gradient(ellipse 55% 45% at 88% 94%, rgba(255,93,106,.16), transparent 60%),
  linear-gradient(165deg,#1f3864 0%,#182a52 42%,#141d35 100%);
  color:#fff;justify-content:center;align-items:flex-start;padding:0 28mm}
.cover .bar{position:absolute;left:0;top:0;bottom:0;width:7mm;background:var(--red)}
.cover .tex{position:absolute;inset:0;opacity:.13}

.cover h1{font-family:'OZ Mincho',serif;font-size:33pt;font-weight:700;
  line-height:1.45;letter-spacing:.01em;position:relative}
.cover h1 .hl{color:var(--red-bright)}
.cover .sub{font-size:11.5pt;line-height:1.9;color:rgba(216,228,240,.82);
  margin-top:8mm;max-width:220mm;position:relative}

.cover .who{position:absolute;left:28mm;bottom:14mm;font-size:9.5pt;
  color:rgba(216,228,240,.72)}
.cover .who b{color:#fff;font-size:11pt;font-weight:700}
.cover .eyebrow{position:relative;margin-bottom:6mm}
.close{justify-content:center;align-items:center;text-align:center}
.close h2{font-size:24pt;line-height:1.55;max-width:250mm}
.close .lead{font-size:11pt;color:rgba(255,255,255,.8);margin-top:7mm;max-width:230mm}
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
    i = figure_html.find('<svg')
    j = figure_html.rfind('</svg>') + 6
    return figure_html[i:j]


N = [1]  # 表紙が1ページ目


def page(eyebrow, title, lead, figure, cards, navy=False, src=None):
    N[0] += 1
    cs = ''.join('<div class="card"><h3>%s</h3><p>%s</p></div>' % (h, b)
                 for h, b in cards)
    src_html = '<p class="src">%s</p>' % src if src else ''
    P.append(
        '<div class="page%s">'
        '<span class="eyebrow">%s</span><h2>%s</h2><p class="lead">%s</p>'
        '<div class="fig">%s</div>%s'
        '<div class="cards%s">%s</div>'
        '<div class="foot">放送大学 第11回「AIエージェント」 ─ AI技術を人・社会へとつなぐ</div>'
        '<div class="pnum">%02d</div></div>'
        % (' navy' if navy else '', eyebrow, title, lead,
           only_svg(figure), src_html, ' two' if len(cards) == 2 else '', cs, N[0]))


# ── 01 表紙 ──────────────────────────────────────────────────
P.append(
    '<div class="page cover"><div class="bar"></div>' + TEX +
    '<span class="eyebrow">放送大学 第11回 ─ AI Agent</span>'
    '<h1>AI技術を、人と社会へつなぐ<br>「<span class="hl">AIエージェント</span>」の設計思想</h1>'
    '<p class="sub">これまでの生成AIは、人の指示を待って答えるだけだった。いま、与えられた目標を'
    '達成するために、状況を把握し、自律的に判断し、実行するAIエージェントへと変容している。'
    'その頭脳の仕組み（ReACT）、記憶の仕組み（状態管理）、知識の調達（RAG）を分解し、'
    '医療・自治体・金融での実装例から、人と社会にどうつながるかを考える。</p>'
    '<div class="who"><b>小澤健祐（おざけん）</b>　一般社団法人AICX協会<br>'
    'ozaken-ai.github.io/ozaken-materials</div></div>')

# ── 02 Why Now ───────────────────────────────────────────────
page('Chapter 11 ─ Why Now',
     'AIの「主語」が、人からAIへ移りはじめている',
     '生成AI技術は、人間の指示を待つだけの存在ではなくなった。'
     '与えられた目標を達成するために、状況を把握し、自律的に判断して実行する。'
     'この主語の転換が、AIエージェントという言葉の正体だ。',
     fig_gap([
         ('聞かれたことに、一問一答で答える', '目標だけを渡せば、手順は自分で組み立てる'),
         ('1回のやり取りで、そこで完結する', '状況を見ながら、必要な行動を続けて取る'),
         ('次に何をするかは、そのつど人が決める', '観察した結果をもとに、次の一手を自分で選ぶ'),
     ], '', '', dark=True, uid='pdf-intro',
        left_label='指示を待つ生成AI', right_label='状況を把握し、自ら動くAIエージェント'),
     [('<span class="tag">定義</span>状況を把握し自律的に動くプログラム',
       '生成AIが「頭脳」だとすれば、AIエージェントはその頭脳に、環境を認識する目と、'
       '実行する手足が備わった存在。<b>目標だけを渡せば、状況判断から実行までを自律的にこなす</b>。'),
      ('<span class="tag">転換点</span>「使う」から「任せる」へ',
       '人が都度指示を出すのではなく、目標達成までの手順そのものをAIが設計し、実行していく。'
       '<b>関係そのものが変わる</b>。'),
      ('<span class="tag">この講義の地図</span>3つの仕組みと、社会実装を見る',
       'ReACT（考えて動く頭脳）・状態管理（記憶の装置）・RAG（知識の調達）という3つの仕組みを'
       '分解し、最後に医療・自治体・金融の実装例を見る。')],
     navy=True)

# ── 03 ReACT ─────────────────────────────────────────────────
page('Chapter 11 ─ ReACT',
     'エージェントの頭脳は、考えると動くを交互に回す',
     '一つの技術の名前というより、いまのAIエージェントがほぼ例外なく内蔵している基本原理。'
     '最初の一手がうまくいかなくても、観察した結果を踏まえてまた考え直せる。'
     '一発勝負で終わらないことが、この仕組みの値打ちだ。',
     fig_cycle([
         ('思考する', '次に何をすべきかを、言葉にして考える'),
         ('行動する', 'ツールを呼ぶ・検索する・操作を実行する'),
         ('観察する', '行動の結果が、どうなったかを確認する'),
         ('また考える', '結果を踏まえて、思考の一歩へ戻る'),
     ], '', '', dark=True, center='ReACT', uid='pdf-react'),
     [('<span class="tag">由来</span>Reasoning + Acting',
       '2022年、「ReACT」という名前で提案された。「考える」だけでも「動く」だけでもなく、'
       'この2つを1ステップずつ交互に繰り返すのが特徴。'),
      ('<span class="tag">何が変わるか</span>結果を見て、考え直せる',
       '最初の判断が外れても、観察を踏まえて思考をやり直せる。'
       '<b>軌道修正しながら目標に近づいていく</b>。'),
      ('<span class="tag">大枠でとらえると</span>名前の注目度は下がり、原理は残った',
       'ReACTという固有名詞が話題に上る頻度はいまや下がっている。だが理由は廃れたからではなく、'
       '<b>大半のエージェント基盤に、名前を意識されないまま組み込まれ「当たり前」になったから</b>。')],
     navy=True,
     src='出典: Yao et al.「ReAct: Synergizing Reasoning and Acting in Language Models」'
         '（2022年, arXiv:2210.03629）。')

# ── 04 State Management ──────────────────────────────────────
page('Chapter 11 ─ State Management',
     '状態管理は、「覚えている」を成り立たせる装置',
     '考える・動く・確かめるのループを回し続けるには、それまでの経緯を覚えておく必要がある。'
     '一手ごとに記憶を失えば、エージェントはゴールに辿りつけない。',
     fig_ladder([
         ('実行ログ', 'この一連の行動で、何をどう行ったか'),
         ('作業中の一時変数', '検索結果・計算の途中経過など、いまだけ使う値'),
         ('長期記憶', 'これまでのやり取りや、好みの傾向を保存する'),
         ('外部の記憶装置', 'ベクトルDB・ファイル・データベースに保存する'),
     ], '', '', asc=True),
     [('<span class="tag">なぜ要るか</span>覚えていなければ、次の一手が選べない',
       '思考・行動・観察を繰り返すには、それまでの経緯を踏まえる必要がある。'
       'これを支えるのが状態管理。'),
      ('<span class="tag">2つの記憶</span>短期はその場限り、長期は次回に持ち越す',
       '実行中の一時的なメモと、セッションをまたいで残す記憶は、別の仕組みで管理されている。'),
      ('<span class="tag">限界</span>覚えられる量には、上限がある',
       'コンテキストウィンドウという「机の広さ」を超えた分は、要約するか、'
       '<b>外部の記憶装置に逃がすほかない</b>。')])

# ── 05 RAG ───────────────────────────────────────────────────
page('Chapter 11 ─ RAG',
     'RAGは、答える前に外の知識を検索しにいく仕組み',
     'Retrieval-Augmented Generation ── 検索で拡張された生成。'
     '知識をモデルに覚え込ませるのではなく、答える直前に外部を検索し、'
     '見つかった断片だけを根拠にして答えさせる。学習ではなく、調達だ。',
     fig_flow([
         ('質問・状況を受け取る', 'エージェントが、いま何を知る必要があるかを把握する'),
         ('関連する文書を検索する', '社内文書やWeb上から、根拠になりそうな断片を探す'),
         ('断片を根拠として渡す', '見つかった断片だけを、回答の材料として渡す'),
         ('根拠にもとづいて答える', 'モデルが働くのは、この最後の1工程だけ'),
     ], '', '', dark=True, uid='pdf-rag'),
     [('<span class="tag">正体</span>覚えさせるのではなく、その場で調べて答える',
       '答える前に外部知識を検索し、見つかった断片だけを根拠にして答えさせる仕組み。'
       'モデルの中に知識を蓄えるファインチューニングとは、<b>狙いが違う</b>。'),
      ('<span class="tag">エージェントでの役割</span>状況認識の材料を、外から取ってくる',
       'エージェントが環境を認識するには、最新かつ固有の情報が要る。'
       'RAGは、その情報取得を担うスキルの一つとして働く。'),
      ('<span class="tag">利点</span>出典が示せて、差し替えがきく',
       '参照する文書を更新すれば翌日から反映され、「どの文書に基づく回答か」を示せる。'
       '<b>学習させる手法にはない強みだ</b>。')],
     navy=True)

# ── 06 Anatomy ───────────────────────────────────────────────
page('Chapter 11 ─ Anatomy',
     '4つの部品が揃って、初めて「エージェント」になる',
     'トリガー・ReACT・状態管理・RAG。役割はそれぞれ違う。'
     '考えて動く頭脳だけがあっても、記憶と知識の調達が欠ければ、状況を把握し続けることはできない。',
     fig_cols([
         ('TRIGGER', 'トリガー', '何が動かすか',
          'メール受信・スケジュール・指示の3種類。ここから最初の思考が始まる。', 0),
         ('REASON & ACT', '頭脳', 'どう考え、動くか',
          '考える・動く・確かめるのループで、繰り返す。', 1),
         ('MEMORY', '記憶', '何を覚えておくか',
          '状態管理が、実行ログと長期の記憶を支える。', 2),
         ('KNOWLEDGE', '知識', '何を根拠にするか',
          'RAGが、最新かつ固有の情報を検索して渡す。', 3),
     ], '', ''),
     [('<span class="tag">骨格</span>4部品は役割が違う。どれか一つでは動かない',
       '起点がなければ動き出さず、頭脳がなければ判断できず、記憶がなければ続かず、'
       '知識がなければ根拠を持てない。'),
      ('<span class="tag">設計の要</span>環境認識の質が、エージェントの価値を決める',
       '組織の暗黙知や業界の慣行をどれだけ「渡せる形」にできるかで、'
       '<b>同じ4部品でも働きの質は変わる</b>。'),
      ('<span class="tag">誤解しやすい点</span>賢いモデルを積めば済む話ではない',
       'モデルの性能ではなく、<b>4部品をどう組み合わせて設計するかが、実装の分かれ目になる</b>。')])

# ── 07 Social Implementation ─────────────────────────────────
page('Chapter 11 ─ Social Implementation',
     '社会実装は、どこまで来ているか',
     '医療・自治体・金融。それぞれの現場で、AIエージェントはすでに動きはじめている。'
     '派手な自動運転より先に、「照会に一次回答を用意し、人が確認して返す」という'
     '地味な現場から実装は進んでいる。',
     fig_map('導入のしやすさ', '現場への効果の大きさ', [
         ('自治体：例規の照会支援', 22, 40, 0, '公開情報の範囲から、根拠つきの一次回答を用意'),
         ('金融：照会対応の一次回答', 55, 62, 1, '規程に基づく回答案をAIが用意し、担当者が確認'),
         ('医療：診療記録の下書き', 78, 88, 2, '会話から下書きを作り、医療者が確認・修正する'),
     ], '', '', dark=True,
        corners=[(15, 90, '効果は大きいが、着手のハードルは高い'), (85, 90, '効果も大きく、着手しやすい'),
                 (15, 10, 'まずは様子を見てよい'), (85, 10, '着手しやすいが、効果は小さい')]),
     [('<span class="tag">共通点</span>どの例も「根拠を示す」形で使われている',
       '自治体は例規の条文、金融は規程、医療は出典。RAGが支える「答えの裏付け」が、'
       '現場で使われる条件になっている。'),
      ('<span class="tag">役割で見え方が変わる</span>決める人・組む人・回す人',
       'どこに置くかを決める人、閉域環境や監査証跡を設計する人、日々の照会や記録作成で'
       '実際に回す人。役割ごとに求められる理解が違う。'),
      ('<span class="tag">共通の失敗</span>出典を示せない設計は、現場で使われない',
       '住民・顧客・患者に関わる場面ほど、<b>「なぜその答えなのか」を示せないエージェントは'
       '定着しない</b>。')],
     navy=True,
     src='出典: おざけん資料アーカイブ「医療・自治体・金融のAI活用 完全ガイド」の活用事例にもとづく'
         '（2026年8月時点）。')

# ── 08 Pitfalls ──────────────────────────────────────────────
page('Chapter 11 ─ Pitfalls',
     '「賢くなった」のではなく、「任せられる範囲が増えた」',
     'AIエージェントという言葉には、誤解も多く積み重なっている。'
     '進化しているのは、モデルの知能そのものというより、状況を把握し、任せられる作業の範囲だ。',
     fig_check([
         (False, '完全自律で、何でも人抜きに任せられる',
          '権限とリスクに応じて、確認をどこに挟むかを線引きする設計がまだ必要になる'),
         (False, '会話を続ければ、AIが勝手に賢くなる',
          '実際は状態管理という設計があって初めて、その場の記憶が保たれているにすぎない'),
         (False, 'RAGは、AIに知識を覚え込ませる技術だ',
          '覚えさせるのではなく、答える前に外部を検索し、断片を根拠にする技術'),
         (True, 'ReACTは、結果を見てから考え直せる仕組みだ',
          '一度の判断で終わらず、観察した結果を踏まえてまた考え直せる'),
     ], '', ''),
     [('<span class="tag">落とし穴1</span>自律性は「全か無か」ではない',
       '反応型から自律型まで、自律性には段階がある。業務のリスクに応じて、'
       'どこまで任せるかを設計する。'),
      ('<span class="tag">落とし穴2</span>出典のない回答は、現場では使われない',
       '自治体・金融・医療、いずれも根拠を示せることが導入の条件だった。'
       '<b>技術より先に、ここでつまずく</b>。'),
      ('<span class="tag">これから</span>4つの部品を、業務にどう組むかが問われる',
       '技術としての部品はすでに出そろっている。<b>設計する側の理解が、次の分かれ目になる</b>。')])

# ── 09 締め ──────────────────────────────────────────────────
P.append(
    '<div class="page navy close">' +
    '<span class="eyebrow">Summary</span>'
    '<h2>AIエージェントは、人の代わりではなく、<br>考え直せる相手になる</h2>'
    '<p class="lead">AI技術の主語がAIに移ったことは、人が要らなくなることを意味しない。'
    'ReACTが考え直す力を、状態管理が記憶を、RAGが最新の根拠を支える——'
    'この3つが揃って初めて、エージェントは安心して任せられる相手になる。<br><br>'
    '人と社会がAIエージェントとどう向き合うかは、技術の性能ではなく、'
    '<b style="color:#fff">この仕組みをどこまで理解し、どこに線を引くか</b>で決まる。</p>'
    '<div class="foot">放送大学 第11回「AIエージェント」 ─ AI技術を人・社会へとつなぐ　'
    '｜　小澤健祐（おざけん）／ 一般社団法人AICX協会</div>'
    '<div class="pnum">%02d</div></div>' % (N[0] + 1))

html = ('<!DOCTYPE html><html lang="ja"><head><meta charset="utf-8">'
        '<title>AIエージェントとは何か</title><style>%s</style></head><body>%s</body></html>'
        % (CSS, ''.join(P)))
out = os.path.join(FONT_DIR, 'ai-agent-lecture.html')
open(out, 'w', encoding='utf-8').write(html)
print('%s に書き出しました（%dページ / %d文字）' % (out, len(P), len(html)))
