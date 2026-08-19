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
from domain_fig import (fig_gap, fig_cycle, fig_ladder, fig_flow, fig_cols, fig_map, fig_check,
                        fig_dims, fig_tree, fig_versus, fig_issues, fig_sheet)

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
.eyebrow{display:inline-block;font-family:'OZ En',sans-serif;font-size:11pt;
  font-weight:700;letter-spacing:.13em;color:var(--azure);background:var(--azure-pale);
  padding:4px 11px;border-radius:4px;align-self:flex-start}
h2{font-family:'OZ Mincho',serif;font-size:24pt;font-weight:700;line-height:1.4;
  margin:7px 0 5px;letter-spacing:.01em}
.lead{font-size:13pt;line-height:1.8;color:var(--muted);max-width:270mm}
.page.navy h2{color:#fff}
.fig{flex:1;display:flex;align-items:center;justify-content:center;
  margin:6px 0 5px;min-height:0}
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
.tag{display:inline-block;font-family:'OZ En',sans-serif;font-size:9pt;font-weight:700;
  letter-spacing:.08em;color:var(--azure);background:var(--azure-pale);
  padding:2px 7px;border-radius:3px;margin-right:6px;vertical-align:2px}
.page.navy .tag{color:#fff;background:rgba(255,255,255,.18)}

.pnum{position:absolute;right:18mm;bottom:6mm;font-family:'OZ En',sans-serif;
  font-size:9.5pt;letter-spacing:.12em;color:var(--muted)}

.foot{position:absolute;left:18mm;bottom:6mm;font-size:9pt;color:var(--muted);
  letter-spacing:.02em}
.page.navy .foot{color:rgba(255,255,255,.5)}

/* 出典 */
.src{margin-top:4mm;font-size:9.5pt;line-height:1.7;color:var(--muted)}
.page.navy .src{color:rgba(255,255,255,.55)}

/* ── 詳細ページ（カードを1ページに独立させ、大きい文字で見せる） ── */
.page.detail h2{margin-bottom:6mm}
.cards-stack{display:flex;flex-direction:column;gap:6mm;flex:1;
  justify-content:center;min-height:0}
.cards-stack .card{padding:7mm 12mm}
.cards-stack .card h3{font-size:17pt;margin-bottom:3.5mm;line-height:1.5}
.cards-stack .card p{font-size:13pt;line-height:1.85}

/* ── 表紙・裏表紙 ── */
.cover{background:
  radial-gradient(ellipse 60% 46% at 50% 40%, rgba(46,84,150,.35) 0%, transparent 55%),
  radial-gradient(ellipse 70% 55% at 50% -5%, rgba(46,84,150,.60), transparent 62%),
  radial-gradient(ellipse 55% 45% at 88% 94%, rgba(255,93,106,.16), transparent 60%),
  linear-gradient(165deg,#1f3864 0%,#182a52 42%,#141d35 100%);
  color:#fff;justify-content:center;align-items:flex-start;padding:0 28mm}
.cover .bar{position:absolute;left:0;top:0;bottom:0;width:7mm;background:var(--red)}
.cover .tex{position:absolute;inset:0;opacity:.13}

.cover h1{font-family:'OZ Mincho',serif;font-size:38pt;font-weight:700;
  line-height:1.48;letter-spacing:.01em;position:relative}
.cover h1 .hl{color:var(--red-bright)}
.cover .sub{font-size:14.5pt;line-height:1.95;color:rgba(216,228,240,.86);
  margin-top:9mm;max-width:220mm;position:relative}

.cover .who{position:absolute;left:28mm;bottom:14mm;font-size:11pt;
  color:rgba(216,228,240,.75)}
.cover .who b{color:#fff;font-size:13pt;font-weight:700}
.cover .eyebrow{position:relative;margin-bottom:6mm}
.close{justify-content:center;align-items:center;text-align:center}
.close h2{font-size:30pt;line-height:1.6;max-width:250mm}
.close .lead{font-size:14pt;color:rgba(255,255,255,.85);margin-top:8mm;max-width:230mm}
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


FOOT = '放送大学 第11回「AIエージェント」 ─ AI技術を人・社会へとつなぐ'


def page(eyebrow, title, lead, figure, cards, navy=False, src=None):
    # 本文ページ（図版まで）と、カード解説の独立ページに分けて出す。
    # 文字を大きくした分、1ページに詰め込みすぎないための構成。
    N[0] += 1
    src_html = '<p class="src">%s</p>' % src if src else ''
    P.append(
        '<div class="page%s">'
        '<span class="eyebrow">%s</span><h2>%s</h2><p class="lead">%s</p>'
        '<div class="fig">%s</div>%s'
        '<div class="foot">%s</div>'
        '<div class="pnum">%02d</div></div>'
        % (' navy' if navy else '', eyebrow, title, lead,
           only_svg(figure), src_html, FOOT, N[0]))

    N[0] += 1
    cs = ''.join('<div class="card"><h3>%s</h3><p>%s</p></div>' % (h, b)
                 for h, b in cards)
    P.append(
        '<div class="page%s detail">'
        '<span class="eyebrow">%s ─ もっと詳しく</span><h2>%s</h2>'
        '<div class="cards-stack">%s</div>'
        '<div class="foot">%s</div>'
        '<div class="pnum">%02d</div></div>'
        % (' navy' if navy else '', eyebrow, title, cs, FOOT, N[0]))


# ── 01 表紙 ──────────────────────────────────────────────────
P.append(
    '<div class="page cover"><div class="bar"></div>' + TEX +
    '<span class="eyebrow">放送大学 第11回 ─ AI Agent</span>'
    '<h1>AI技術を、人と社会へつなぐ<br>「<span class="hl">AIエージェント</span>」の設計思想</h1>'
    '<p class="sub">これまでの生成AIは、人の指示を待って答えるだけだった。いま、与えられた目標を'
    '達成するために、状況を把握し、自律的に判断し、実行するAIエージェントへと変容している。'
    'その頭脳の仕組み（ReACT）、記憶の仕組み（状態管理）、知識の調達（RAG）を分解し、'
    'DX・AXの位置づけ、データ活用、組織論、そして人の仕事の変え方まで見渡したうえで、'
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
      ('<span class="tag">この講義の地図</span>仕組みから、社会・組織・人までを見る',
       'ReACT・状態管理・RAGという3つの仕組みを分解し、データ活用や組織論、キャリアへの影響'
       'まで見渡す。')],
     navy=True)

# ── 02b 実装の5レベル ────────────────────────────────────────
page('Chapter 11 ─ Five Levels',
     '実装は「点・線・面・立体」の5段階で進む',
     '単発のプロンプトから、完全自律型まで。レベル3と4のあいだで、段取りを決める主語が'
     '人からAIへ移る。',
     fig_dims([
         ('LV.1', 'dot', '単発の指示', 'その場のプロンプト', '都度の指示で、目の前を片づける', 0),
         ('LV.2', 'line', 'チャット構築', '前提を渡す', '前提を渡し、対話の中で答えさせる', 1),
         ('LV.3', 'chain', 'ワークフロー', '手順を渡す', '手順を組んで、決まった流れを走らせる', 1),
         ('LV.4', 'plane', '半自律', '目的を渡す', '目的を渡せば、ルートはAIが探す', 2),
         ('LV.5', 'cube', '完全自律', '複数の連携', '複数のエージェントが連携し、業務を回す', 3),
     ], '', '', split=4, uid='pdf-dims'),
     [('<span class="tag">見分け方</span>渡すものが「手順」か「目的」か',
       'レベル1〜3は<b>使うAI</b>。人が手順を渡す。レベル4〜5は<b>任せるAI</b>。人が渡すのは目的だけになる。'),
      ('<span class="tag">断絶ではない</span>ある日を境に切り替わるわけではない',
       'レベル2で前提を渡し始めた時点で「任せる」は芽生えている。<b>移っていくのは、手順を決める重心</b>。'),
      ('<span class="tag">注意</span>レベル2と3は、どちらも「線」',
       '2は前提を渡して答えさせる方向、3は手順を組んで走らせる方向。'
       '<b>3は2の発展形ではなく、別ルート</b>。')],
     src='出典: おざけん資料アーカイブ「AIエージェント実装の5レベル」にもとづく。')

# ── 03 DX vs AX ──────────────────────────────────────────────
page('Chapter 11 ─ DX vs AX',
     'DXが「データ」を、AXが「プロセス」を動かす',
     '二つは対立するものではなく、直交する。DXがもたらしたのは「見える」基盤だった。'
     'プロセスを回す主体は、人のまま残されていた。AIエージェントは、AXの体現だ。',
     fig_map('データの活用', 'プロセスの自律', [
         ('手作業・属人化', 14, 12, 1, '人が集め、人が回す'),
         ('データドリブン', 84, 18, 0, 'DXの到達点。見えるが、動かない'),
         ('部分的な自動化', 30, 58, 2, '渡すものが薄いまま、任せた状態'),
         ('AIエージェント', 80, 80, 3, '整ったデータの上を、AIが回す'),
     ], '', '', dark=True, corners=[(97, 97, 'ここが目的地')]),
     [('<span class="tag">DX</span>データの軸 ── アナログをデータに、データを価値に',
       '紙をデータに変え、バラバラだった記録をつなぎ、可視化して意思決定に活かす。'
       '<b>ここまでがDXの到達点</b>。'),
      ('<span class="tag">AX</span>プロセスの軸 ── AIが実行の主体に加わる',
       'これまで人が手を動かしていたプロセスそのものを、AIエージェントが実行・再設計・'
       '自律化していく。'),
      ('<span class="tag">役割の変化</span>「実行者」から「設計者」へ',
       '人の役割は、手を動かす実行者から、<b>プロセスを設計し監督する設計者へ書き換わる</b>。')],
     navy=True,
     src='出典: おざけん資料アーカイブ「AI Transformation・思想」にもとづく。')

# ── 04 ReACT ─────────────────────────────────────────────────
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

# ── 05 State Management ──────────────────────────────────────
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

# ── 06 構造化・非構造化データ ────────────────────────────────
page('Chapter 11 ─ Structured & Unstructured Data',
     '構造化データと非構造化データ、両方を横断して使う',
     '生成AIが、これまで活用できなかった非構造化データの壁を壊した。'
     'RAGが検索の対象にするのは、この2種類のデータだ。両方を横断して扱えることが、'
     'いまのAIエージェントの強みになる。',
     fig_cols([
         ('STRUCTURED', '構造化データ', 'テーブルに整理できる',
          'RDB・CSV・Excel。顧客マスタや取引履歴。従来のBIツールで分析できていた。', 0),
         ('UNSTRUCTURED', '非構造化データ', '規則性がなく、表にできない',
          'メール・議事録・社内文書、画像・音声。従来は活用に限度があった。', 1),
     ], '', ''),
     [('<span class="tag">壁が壊れた</span>これまでの技術では、非構造化データを扱いづらかった',
       'テキスト・画像・音声。生成AIがその壁を壊し、社内の議事録・問い合わせ・契約書まで'
       '<b>「使える資産」に変えた</b>。'),
      ('<span class="tag">RAGとの関係</span>RAGが検索するのは、主にこの非構造化データ',
       '見つかった断片を根拠にして答えさせる仕組みは、表にできない情報を扱えるように'
       'なったからこそ機能する。'),
      ('<span class="tag">質の3観点</span>Volume・Velocity・Variety',
       '量・速度・多様性。<b>質の高いデータをどれだけ揃えられるかが、エージェントの判断材料の'
       '質を決める</b>。')],
     src='出典: おざけん資料アーカイブ「DXとは何か」にもとづく。')

# ── 07 RAG ───────────────────────────────────────────────────
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

# ── 08 コンテキスト・ハーネス・ループ ─────────────────────────
page('Chapter 11 ─ Context & Data',
     'コンテキスト・ハーネス・ループ ── 3つのエンジニアリング',
     '何を渡すか、どう動かすか、いつ止めるか。RAGが検索する「知識」も、エージェントが認識する'
     '「状況」も、元をたどれば、この3つのエンジニアリングがどこまで設計されているかに行き着く。',
     fig_cols([
         ('CONTEXT', 'コンテキストエンジニアリング', '何を渡すか',
          'RAG・メモリ・社内データ接続。AIに前提を共有する設計。', 0),
         ('HARNESS', 'ハーネスエンジニアリング', 'どう動かすか',
          'ツール接続・評価と観測を含めた、AIを動かす環境ごとの設計。', 1),
         ('LOOP', 'ループエンジニアリング', 'いつ止めるか',
          '反復回数・停止条件・人の介入。ReACTの往復を制御する設計。', 2),
     ], '', ''),
     [('<span class="tag">コンテキスト</span>何を渡すかを設計する',
       'RAG・メモリ・社内データ接続。土台は「これが正しい」と決めた正本を1つに保つこと。'
       '<b>正本が複数あれば、AIは古い版を読むだけになる</b>。'),
      ('<span class="tag">ハーネス</span>どう動かすかを設計する',
       'ツール接続・評価と観測を含めた「環境ごと」の設計。'
       '<b>同じモデルでも、ハーネス次第で性能が数倍〜10倍変わる</b>。'),
      ('<span class="tag">ループ</span>いつ止めるかを設計する',
       'ReACTの往復に、反復回数の上限・停止条件・人の介入ポイント・ガードレールを組み込む。'
       '<b>ここが甘いと、エージェントは止まらなくなる</b>。')],
     src='出典: おざけん資料アーカイブ「コンテキスト＆ハーネスエンジニアリング」にもとづく。')

# ── 09 Anatomy ───────────────────────────────────────────────
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
     ], '', '', dark=True),
     [('<span class="tag">骨格</span>4部品は役割が違う。どれか一つでは動かない',
       '起点がなければ動き出さず、頭脳がなければ判断できず、記憶がなければ続かず、'
       '知識がなければ根拠を持てない。'),
      ('<span class="tag">設計の要</span>環境認識の質が、エージェントの価値を決める',
       '組織の暗黙知や業界の慣行をどれだけ「渡せる形」にできるかで、'
       '<b>同じ4部品でも働きの質は変わる</b>。'),
      ('<span class="tag">誤解しやすい点</span>賢いモデルを積めば済む話ではない',
       'モデルの性能ではなく、<b>4部品をどう組み合わせて設計するかが、実装の分かれ目になる</b>。')],
     navy=True)

# ── 09b トリガーの分類 ───────────────────────────────────────
page('Chapter 11 ─ Triggers',
     'トリガーは3種類。人の仕事の起動条件と、同じ形をしている',
     'レベルが「どこまで自律的か」を表す縦の軸なら、トリガーは「何をきっかけに動くか」という'
     '横の軸。AIの起動条件も、人の仕事とまったく同じ構造をしている。',
     fig_tree('AIが動き出す、3つのきっかけ', [
         ('指示型', ['人が依頼して、その場で動く']),
         ('定時型', ['決まった時刻に、自動で動く']),
         ('イベント型', ['出来事に反応して、自律的に動く']),
     ], '', '', uid='pdf-trig'),
     [('<span class="tag">対応関係</span>人間の仕事と、同じ3つに分かれる',
       '依頼を受けて動く、決まった時刻に動く、出来事に反応して動く。<b>AIの起動条件も、'
       '人の仕事とまったく同じ構造</b>をしている。'),
      ('<span class="tag">固定されない</span>トリガーは、レベルに固定されない',
       'どれが高度かではなく、<b>レベルが上がるほど主役のトリガーが移り変わる</b>のが要点。'),
      ('<span class="tag">注意</span>イベント型が、いちばん自律に近い',
       '人も時計も待たずに動く。だからこそ、<b>止め方と、越えてはいけない線を先に決めておく</b>'
       '必要がある。')],
     src='出典: おざけん資料アーカイブ「AIエージェント実装の5レベル」にもとづく。')

# ── 10 Social Implementation ─────────────────────────────────
page('Chapter 11 ─ Social Implementation',
     '社会実装は「AIが下書き、人が確認」まで。真のエージェント化はこれから',
     '自律的に動く「本当のAIエージェント」は、実務ではまだほとんど動いていない。'
     '医療・自治体・金融の現場で実際に動いているのは、AIが一次回答や下書きを用意し、'
     '必ず人が確認してから返す、という運用がほとんどだ。',
     fig_sheet(
         ['現場', '聞かれること（例）', 'AIが用意する一次回答', '人がすること'],
         [
             ['自治体', '「ゴミの分別ルールは？」', '例規を検索し、根拠つきの回答案を作成', '担当者が内容を確認して返信'],
             ['金融', '「この契約、途中解約できますか？」', '規程を検索し、回答案を作成', '担当者が確認し、正式回答として送付'],
             ['医療', '診察後の会話の記録から', 'カルテの下書きを自動生成', '医師が確認・修正して確定'],
         ],
         [0.12, 0.28, 0.33, 0.27], '', '', badge='現在の実装水準'),
     [('<span class="tag">共通点</span>すべて「AIが下書き、人が最終確認」という型',
       '自治体・金融・医療、いずれも人がループの外に出ることはない。'
       '<b>点・線・面・立体でいえば、まだレベル2〜3にとどまる</b>。'),
      ('<span class="tag">正直な現在地</span>「自律的に動くエージェント」は、まだほとんど動いていない',
       '目的だけを渡せば手順も判断もAIが担う、<b>レベル4〜5の実装は、実務ではまだ実証段階の'
       'ものが多い</b>。'),
      ('<span class="tag">それでも価値がある理由</span>「使うAI」だけでも、現場の時間は変わる',
       '一次回答の下書きがあるだけで、確認と修正で済む。地味だが、これが実装の第一歩に'
       'なっている。')],
     src='出典: おざけん資料アーカイブ「医療・自治体・金融のAI活用 完全ガイド」の活用事例にもとづく'
         '（2026年8月時点）。')

# ── 11 Pitfalls ──────────────────────────────────────────────
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
     ], '', '', dark=True),
     [('<span class="tag">落とし穴1</span>自律性は「全か無か」ではない',
       '反応型から自律型まで、自律性には段階がある。業務のリスクに応じて、'
       'どこまで任せるかを設計する。'),
      ('<span class="tag">落とし穴2</span>出典のない回答は、現場では使われない',
       '自治体・金融・医療、いずれも根拠を示せることが導入の条件だった。'
       '<b>技術より先に、ここでつまずく</b>。'),
      ('<span class="tag">これから</span>4つの部品を、業務にどう組むかが問われる',
       '技術としての部品はすでに出そろっている。<b>設計する側の理解が、次の分かれ目になる</b>。')],
     navy=True)

# ── 12 「個人最適」の罠 ─────────────────────────────────────
page('Chapter 11 ─ The Trap',
     '「個人最適」の罠 ── それだけで、満足していませんか？',
     '個人がどれだけAIを使いこなしても、その成功体験は組織のプロセスに接続されない。'
     '要約する、校正する、翻訳する。便利だが、いままでの手順を変えないまま、'
     'その中の一工程だけを速くしている状態にすぎない。',
     fig_issues([
         ('ツール導入≠再設計', '配っただけでは、業務は変わらない'),
         ('成功体験が非共有', 'サイロ化し、個人の中に閉じる'),
         ('評価制度が未整備', 'うまく使う人が、報われない'),
     ], '', '', uid='pdf-trap'),
     [('<span class="tag">表層の罠</span>要約・校正・翻訳は、いちばん浅い活用',
       '手順そのものには、まだ指一本触れていない。<b>前提を疑わないから、いくら積み上げても'
       '手順は変わらない</b>。'),
      ('<span class="tag">問うべきこと</span>「誰が一番うまいか」ではない',
       '問うべきは「誰がやっても同じ品質になるか」。AIを使える人を増やすだけでは、'
       '組織は変わらない。'),
      ('<span class="tag">現場感覚</span>現場でいちばんよく聞く使い方が、この罠にはまる',
       '要約・校正・翻訳が速くなったかどうかではなく、<b>その工程自体が要るかどうかを'
       '問い直す</b>。')],
     src='出典: おざけん資料アーカイブ「生成AI時代の組織論」にもとづく。生成AI時代、属人化はむしろ加速する。')

# ── 13 答えは「標準化」 ─────────────────────────────────────
page('Chapter 11 ─ Standardization',
     '答えは「標準化」 ── サイゼリヤに、天才シェフはいない',
     'サイゼリヤは、誰が厨房に立っても同じ味が出る。天才シェフに依存しない。'
     'あるのは、徹底的に磨かれた型（標準オペレーション）だ。AIエージェントは、'
     'この型を組織にインストールする装置になる。',
     fig_flow([
         ('個人の暗黙知', 'その人の頭の中にしかないノウハウ'),
         ('型に落とし込む', '優れたやり方を、標準オペレーションに変換する'),
         ('AIエージェントに搭載', '型を組織にインストールする装置として働く'),
         ('組織の資産になる', '誰でも同じ品質で動ける状態に反転する'),
     ], '', '', dark=True, uid='pdf-std'),
     [('<span class="tag">型とは何か</span>徹底的に磨かれた標準オペレーション',
       'サイゼリヤは全国1,000店舗で同じ品質を再現する。<b>あるのは名人芸ではなく型</b>。'),
      ('<span class="tag">反転</span>「使える人だけ得をする」から「誰でも同じ品質で動ける」へ',
       '個人の暗黙知を型化し、AIエージェントに載せると、成功体験が組織全体で再利用できる'
       '資産に変わる。'),
      ('<span class="tag">本質</span>エージェントは、時短ツールではなく"配管"',
       '個人の判断ロジックを形式知として組織に配る。<b>名人芸を標準オペレーションへ翻訳する'
       'ことが、組織づくりの本質になる</b>。')],
     navy=True,
     src='出典: おざけん資料アーカイブ「生成AI時代の組織論」にもとづく。')

# ── 14 キャリアへの影響 ─────────────────────────────────────
page('Chapter 11 ─ Careers',
     'AIエージェント時代、人の仕事の変え方',
     '道具が変われば、育てるべきスキルも変わる。マニュアルになり、学習データになり、'
     '再現されるものから順に価値を失っていく。技術の話は、最後は人の話に還る。',
     fig_versus(
         ('ハードスキル（鎧）', 'What・Howを担う'), ('Whyを持つ力', '目的を設計する'),
         [('AIとの関係', '手順を覚え、道具を使いこなす', '目的を渡し、Howを引き出す'),
          ('価値の変化', '希少だった鎧が、誰でも持てる前提になった', '記述できないぶん、水面上に残り続ける'),
          ('鍛え方', '資格やツールの習熟を積み重ねる', '課題を自分で見つけ、始める経験を積む')],
         '', ''),
     [('<span class="tag">何が沈むか</span>記述できる仕事から、順に代替されていく',
       '難しさの順ではない。<b>手順として書き出せるかどうか</b>が、順番を決めている。'),
      ('<span class="tag">現場で問われる力</span>技術が主役になるのは、6工程のうち1つだけ',
       '残りの5つは、業務理解・組織理解・対人の仕事。<b>このスキルの希少性は、技術力に'
       '由来しない</b>。'),
      ('<span class="tag">残るもの</span>目的を持つ人から、順に代替されない',
       '「始めること」だけは、AIに渡した瞬間に誰のものでもなくなる。日本でも同じ順番の'
       '変化が数字に出はじめている。')],
     src='出典: おざけん資料アーカイブ「AIエージェント時代のキャリア」にもとづく。')

# ── 14b 6つの工程 ────────────────────────────────────────────
page('Chapter 11 ─ Six Steps',
     '現場でAIを動かす仕事は、6つの工程に割れる',
     'スキル名だけでは像が結びません。1つの案件で、何をどの順にやるのかを並べる。'
     '技術が中心になるのは、6工程のうち④だけ。残りは業務理解・組織理解・対人の仕事だ。',
     fig_ladder([
         ('① 現場に入り、業務を観る', '会議に出て、作業を見て、話を聞く。数日はシステムに触らない'),
         ('② AIが効く箇所を診断する', '業務を作業まで割り、任せられる作業を特定する'),
         ('③ 権限と責任の線を引き直す', '「誰の権限で何を変えられるか」を確定させる。最も案件が止まる工程'),
         ('④ コンテキストを渡せる形にする', '規程・過去の判断例・暗黙のルールを集める。技術が主役になるのはここだけ'),
         ('⑤ 動かして、抵抗をほぐす', '反対する人が何を守りたいのかを理解する'),
         ('⑥ 定着させ、引き継ぐ', '運用の担い手を立て、判断基準を文書に残す'),
     ], '', '', dark=True, asc=False),
     [('<span class="tag">現場から始まる</span>最初の数日はシステムに触らない',
       '会議に出て、作業を見て、話を聞く。<b>診断より先に、まず現場を観る</b>。'),
      ('<span class="tag">最も止まる工程</span>③ 権限と責任の線引き',
       '「誰の権限で何を変えられるか」が決まっていないと、動くものを作っても本番では'
       '使えない。'),
      ('<span class="tag">技術は1/6だけ</span>④以外は、業務理解・組織理解・対人の仕事',
       '<b>このスキルの希少性が技術力に由来しないのは、このため</b>。')],
     navy=True,
     src='出典: おざけん資料アーカイブ「AIエージェント時代のキャリア戦略」にもとづく。')

# ── 15 締め ──────────────────────────────────────────────────
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
