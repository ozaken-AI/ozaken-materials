#!/usr/bin/env python3
"""AX Table セッション6（鳥潟幸志さん・グロービス）の進行資料。

進行台本の型は保ったまま図版を5点入れ、
表に置いてある組織系の資料から、この回に効くセクションを持ってくる。

  06_キャリア・人材/人事.html            作業・業務・仕事の3層／人事が握る3つの転換
  06_キャリア・人材/生成AI時代の組織論.html  AI型化モデル／名人芸を組織の型に／正本を決める

登壇者は『AIが答えを出せない 問いの設定力』の著者であり、
グロービス・デジタル・プラットフォーム部門の責任者として、
自社の事業と組織をAIで作り変えている当事者でもある
（各社の公表情報・報道より／2026年8月確認）。
「人間に残るのは、問いを立てる領域」という表の資料の主張と、
著者としての立場が正面から重なるので、そこを背骨に置く。
"""
import sys

S = '/home/user/ozaken-materials/.claude/skills/ozaken-shiryo/scripts'
sys.path.insert(0, S)
from domain_fig import fig_context, fig_versus, fig_cols, fig_ranges, fig_check

B = []
A = B.append

A('<!--META title=AX Table セッション6｜AIが増えると、組織はどう変わるか | '
  'desc=職種・役割・意思決定の再設計。一人が複数のエージェントを扱う前提に立つと、'
  '職務記述書も等級も評価も同時に揺らぐ。作業・業務・仕事の3層、'
  'Human in / on the Loop の境界、そして人事が握る3つの転換を、'
  '鳥潟幸志さんと。AI・人工知能EXPO NEO「AX Table」セッション6の投影資料。-->')

A('''<section class="hero" data-kabe>
  <div class="kabe-veil" aria-hidden="true"></div>
  <div class="inner" data-reveal>
    <span class="eyebrow">AX Table ─ Session 6 ／ AX4</span>
    <h1 class="hero-title">AIが増えると、組織はどう変わるか</h1>
    <p class="hero-copy">職種・役割・意思決定の再設計</p>
    <p class="hero-meta">8/6（木）11:00–11:45　｜　45分<br>鳥潟 幸志　マネジング・ディレクター<br>株式会社グロービス／グロービス経営大学院 教員　×　小澤健祐（おざけん）</p>
  </div>
</section>
''')

# ── Takeaway ────────────────────────────────────────────────
A('''<section class="sec-light">
  <div class="inner" data-reveal>
    <span class="eyebrow">Takeaway</span>
    <h2 class="sec-label">このセッションで持ち帰っていただくもの</h2>
    <p class="stmt">人とAIの役割分担を、自社の職種名で1つ描いて帰ること。</p>
    <p class="sec-note">この一点に絞って、45分お話しします。</p>
  </div>
</section>
''')

# ── Agenda ──────────────────────────────────────────────────
STEPS = [
    ('はじめに', '00:00–00:04', 'AX Tableの到達点として、組織のかたちそのものを扱います。'),
    ('いま、現場で起きていること', '00:04–00:12',
     '一人が複数のエージェントを扱う前提に立つと、最初に何が壊れるのか。'),
    ('職種は、どう変質するか', '00:12–00:22',
     'なくなる仕事ではなく、変質する仕事。具体的な職種名で見ていきます。'),
    ('意思決定を、どう引き直すか', '00:22–00:32',
     '人が判断する範囲の決め方を、Human in the Loop と on the Loop の違いから。'),
    ('誰が、いつ着手するか', '00:32–00:38', '主導する部門と、始めるタイミング。'),
    ('明日からの一歩', '00:38–00:43', '持ち帰り3点をまとめ、ご質問にお答えします。'),
    ('おわりに', '00:43–00:45', '2日間の総括と、AICX協会の資格制度のご案内。'),
]
A('<section class="sec-navy">\n  <div class="inner" data-reveal>\n'
  '    <span class="eyebrow">Agenda</span>\n'
  '    <h2 class="sec-label">進行</h2>\n'
  '    <p class="sec-note">45分。最後の数分で、持ち帰りポイントをまとめます。</p>\n'
  '    <div class="stepper">\n' +
  '\n'.join('      <div class="step"><div class="step-num">%d</div>'
            '<div class="step-body"><h3>%s<span class="step-time">%s</span></h3>'
            '<p>%s</p></div></div>' % (i + 1, h, t, p)
            for i, (h, t, p) in enumerate(STEPS)) +
  '\n    </div>\n  </div>\n</section>\n')

# ── Context ─────────────────────────────────────────────────
A('<section class="sec-light">\n  <div class="inner" data-reveal>\n'
  '    <span class="eyebrow">Context</span>\n'
  '    <h2 class="sec-label">前提として、押さえておきたいこと</h2>\n'
  '    <p class="sec-note">この4つを共有できていると、このあとの話が具体的に聞こえます。'
  '図はいずれも、アーカイブの組織系の資料から持ってきています。</p>\n'
  + fig_context([
      ('仕事', '問いを立て、意味を見出し、判断する。人に残る層'),
      ('業務', '複数の作業からなる一連のプロセス。エージェントが代替し始めた層'),
      ('作業', '定型的・反復的な個別のアクション。AIが代替する層'),
  ], 'Fig.1 ── 作業・業務・仕事。人間に残るのは「仕事」の層',
     'アーカイブ資料『AIエージェント時代の人事』より。'
     '職種を「なくなる／残る」で捉えず、どの層が移るかで見ます')
  + fig_versus(
      ('Human on the Loop', '監督者として全体を見て、例外だけを引き取る'),
      ('Human in the Loop', '一件ごとに、人が判断に入る'),
      [('人の立ち位置', '処理の上に立ち、基準と例外を持つ',
        '処理の中に立ち、すべてを通す'),
       ('必要な人数', '委譲を広げるほど、少なくて済む',
        '件数に比例して増える'),
       ('求められるスキル', '基準を書く力、例外を見抜く力',
        '正確に速く処理する力'),
       ('評価の観点', '任せた範囲と、止めた回数',
        '処理した件数と、その正確さ')],
      'Fig.2 ── どちらを採るかで、人数もスキルも評価も変わる',
      '判断の境界線は、この選択から決まります。'
      'どちらが優れているかではなく、業務ごとに選ぶものです')
  + fig_cols([
      ('EVALUATION', '評価', '時間から、成果へ',
       'これまでの評価は労働時間を暗黙の前提にしてきました。'
       'AIが作業を肩代わりすれば、その前提は崩れます。'
       '生み出した価値で測る形へ。', 0),
      ('REWARD', '報酬', '価値が2倍なら、報酬も',
       '最も難しく、最も重要な転換。'
       '生産性向上の果実をすべて会社が回収すれば、'
       '従業員はAIを使う動機を失います。', 1),
      ('ROLE', '役割', '作業者から、考える人へ',
       'AIに作業を委ねた先で人に残るのは、考え抜く役割。'
       'それを評価し処遇しキャリアとして用意する仕組みが要ります。', 2),
  ], 'Fig.3 ── 人事が握る、3つの転換',
     'アーカイブ資料『AIエージェント時代の人事』より。'
     'どれか1つだけ動かしても、現場では噛み合いません')
  + '''    <div class="cards" data-wide>
      <div class="card"><span class="card-tag">1</span><h3>一人が、複数のエージェントを扱う前提に立つ</h3><p>一人の担当者が何体ものエージェントに仕事を渡す状態を前提に置くと、職務記述書、等級の定義、評価の単位といった人事の土台が同時に揺らぎます。まず、<b>何が先に壊れるのか</b>を見立てておく必要があります。</p></div>
      <div class="card"><span class="card-tag">2</span><h3>Human in the Loop と Human on the Loop</h3><p>前者は一件ごとに人が判断に入る形、後者は人が監督者として全体を見て、例外だけを引き取る形です。どちらを採るかで、必要な人数も、求められるスキルも、評価の観点も変わります。<b>判断の境界線は、この選択から決まります</b>。</p></div>
      <div class="card"><span class="card-tag">3</span><h3>人間に残るのは「仕事」── 作業・業務・仕事の3層</h3><p>作業はAIが代替し、業務はエージェントが代替し始めています。人に残るのは、<b>問いを立て、意味を見出し、判断する領域</b>です。職種を「なくなる／残る」の二分法で語らず、どの層が移るかで捉えると、そのまま育成の設計につながります。<span class="fw-bold">（アーカイブ『AIエージェント時代の人事』より）</span></p></div>
      <div class="card"><span class="card-tag">4</span><h3>名人芸を、組織の「型」に変える ── AI型化モデル</h3><p>優れた個人のやり方を、エージェントという形で書き出して配る。<b>属人化した名人芸が、組織の型として横に渡る</b>という考え方です。役割の再設計は、この「型を作る人」を職務として置けるかどうかにかかっています。<span class="fw-bold">（アーカイブ『生成AI時代の組織論』より）</span></p></div>
    </div>
  </div>
</section>
''')

# ── Questions ───────────────────────────────────────────────
A('<section class="sec-navy">\n  <div class="inner" data-reveal>\n'
  '    <span class="eyebrow">Questions</span>\n'
  '    <h2 class="sec-label">今日、うかがうこと</h2>\n'
  '    <p class="sec-note">この9問を、この順番でお聞きします。</p>\n'
  + fig_ranges(
      ['00:04', '00:12', '00:22', '00:32', '00:38'],
      [('職種は、どう変質するか', 0, 1, 0, '何が残り、何が移るか'),
       ('判断の境界線を引き直す', 1, 3, 1, 'どこまで明文化するか'),
       ('誰が、いつ着手するか', 3, 4, 2, '主導する部門と、着手の時期'),
       ], 'Fig.4 ── 45分を、3つの塊に割る',
      '45分あっても、扱えるのは3つまでです',
      dark=True, note='押したら真ん中の塊を1問落とします。3つ目は必ず残します')
  + '''    <div class="two-col">
      <div class="two-col-item"><h3>職種は、どう変質するか</h3><p class="tp-lead">「なくなる／残る」の二分法から降りて、具体的な職種名で扱います。</p><p class="tp-q">業務が再配分されると、職種の定義はどう変わりますか？</p><p class="tp-q">たとえば営業企画や購買では、何が残り、何が移りますか？</p><p class="tp-q">人に残るのが「問いを立てること」だとして、それを職務記述書や評価に、どう書けますか？</p></div>
      <div class="two-col-item"><h3>判断の境界線を、どう引き直すか</h3><p class="tp-lead">Human in the Loop と on the Loop の選び方を、基準まで降ろします。</p><p class="tp-q">「誰が何を判断し、AIに何を任せるか」を曖昧にすると、どうなりますか？</p><p class="tp-q">判断の境界線は、どんな基準で引くべきですか。どこまで明文化しますか？</p><p class="tp-q">ご自身の事業部門でAIを入れたとき、最初に見直したのは何でしたか？</p></div>
      <div class="two-col-item"><h3>誰が、いつ着手するか</h3><p class="tp-lead">経営大学院で多くの管理職を見てこられた立場からも、うかがいます。</p><p class="tp-q">この再設計は、誰が主導すべきですか（人事・経営・現場）。着手はどの段階が適切ですか？</p><p class="tp-q">評価制度の見直しは、どこまで先送りできますか？</p><p class="tp-q">役割を引き直せる管理職と、そうでない管理職の差は、どこにありますか？</p></div>
    </div>
  </div>
</section>
''')

# ── Summary ─────────────────────────────────────────────────
A('<section class="sec-light">\n  <div class="inner" data-reveal>\n'
  '    <span class="eyebrow">Summary</span>\n'
  '    <h2 class="sec-label">持ち帰りは、この3点</h2>\n'
  + fig_check([
      (False, '職種の話を「なくなる／残る」で議論している',
       '二分法では現場の納得が得られず、育成の設計にもつながりません'),
      (False, '判断の境界線が、どこにも文章になっていない',
       '曖昧なまま進めると、現場は誰が何を決めるのか分からないまま働き続けます'),
      (False, '組織の再設計を、導入が終わってから始めるつもりでいる',
       '業務が変わり始めてから直すと、その間ずっと摩擦が続きます。並行して着手します'),
      (True, '1つの職種について、何が残り何が移るかを書き出してある',
       '具体的な職種名まで降りていれば、そのまま育成と評価の設計に使えます'),
      (True, '評価・報酬・役割の3つを、同時に動かす計画になっている',
       'どれか1つだけ変えても、現場では噛み合いません'),
  ], 'Fig.5 ── 自社診断：上の3つが当てはまったら、再設計はまだ始まっていません',
     '会場で1つ選んで、月曜からの一歩として持ち帰ってください')
  + '''    <div class="cards" data-take>
      <div class="card"><span class="card-tag">1</span><h3>職種は「なくなる／残る」ではなく、どの層が移るかで捉える</h3></div>
      <div class="card"><span class="card-tag">2</span><h3>判断の境界線を文章にする。in the Loop と on the Loop を業務ごとに選ぶ</h3></div>
      <div class="card"><span class="card-tag">3</span><h3>組織の再設計は、導入と並行して着手する（終わってからでは遅い）</h3></div>
    </div>
  </div>
</section>
''')

# ── 締め ────────────────────────────────────────────────────
A('''<section class="sec-navy">
  <div class="inner" data-reveal>
    <span class="eyebrow">AX Table</span>
    <h2 class="sec-title">現場の壁は、<br>越えた人の言葉でしか越えられない</h2>
    <p class="kicker">正論では、壁は崩れません。<span class="fw-bold">同じ壁の前に立ち、実際に越えた人が、どこに手をかけたかを話す</span>。AX Tableは、そのための場です。</p>
  </div>
</section>
''')

body = '\n'.join(B)
open('/tmp/body_s6.html', 'w', encoding='utf-8').write(body)
print('本文フラグメントを書き出しました（%d文字）' % len(body))
