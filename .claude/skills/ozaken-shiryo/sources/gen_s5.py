#!/usr/bin/env python3
"""AX Table セッション5（中林紀彦さん・ライオン）の進行資料。

進行台本の型（Takeaway / Agenda / Context / Questions / Summary）は保ったまま、
図版を入れ、問いを登壇者にしか答えられないものに寄せる。

登壇者は、IT・広告・保険・物流、そして消費財と、業界を越えてデータ基盤の
立ち上げに携わってきた稀な経歴を持つ（各社の公表情報・報道より／2026年8月確認）。
「業種が変わっても同じだったこと」を実体験で語れる人は、そう多くない。
"""
import sys

S = '/home/user/ozaken-materials/.claude/skills/ozaken-shiryo/scripts'
sys.path.insert(0, S)
from domain_fig import fig_versus, fig_ladder, fig_ranges, fig_timeline

B = []
A = B.append

A('<!--META title=AX Table セッション5｜データ基盤、業務をどう設計するか | '
  'desc=AIエージェント時代に向けて、何から整えるか。業界を越えてデータ基盤の'
  '立ち上げに携わってきた中林紀彦さんに、優先順位のつけ方、判断根拠の言語化、'
  'そして業種が変わっても同じだったことを聞く。'
  'AI・人工知能EXPO NEO「AX Table」セッション5の投影資料。-->')

A('''<section class="hero" data-kabe>
  <div class="kabe-veil" aria-hidden="true"></div>
  <div class="inner" data-reveal>
    <span class="eyebrow">AX Table ─ Session 5 ／ AX3</span>
    <h1 class="hero-title">データ基盤、業務をどう設計するか</h1>
    <p class="hero-copy">AIエージェント時代に向けて</p>
    <p class="hero-meta">8/5（水）11:00–11:45　｜　45分<br>中林さん（ライオン株式会社）　×　小澤健祐（おざけん）</p>
  </div>
</section>
''')

# ── Takeaway ────────────────────────────────────────────────
A('''<section class="sec-light">
  <div class="inner" data-reveal>
    <span class="eyebrow">Takeaway</span>
    <h2 class="sec-label">このセッションで持ち帰っていただくもの</h2>
    <p class="stmt">自社が最初に整える1領域を、用途から逆に引いて決めて帰ること。</p>
    <p class="sec-note">この一点に絞って、45分お話しします。</p>
  </div>
</section>
''')

# ── Agenda ──────────────────────────────────────────────────
STEPS = [
    ('はじめに', '00:00–00:04', 'エージェントを入れる「前」の話です。'),
    ('いま、現場で起きていること', '00:04–00:12',
     'エージェントが力を出せない二つの理由。どちらがより根深いのか。'),
    ('データ基盤：どこから整えるか', '00:12–00:22',
     '全部は無理ななかでの優先順位と、「整った」をどう定義したか。'),
    ('業務設計：棚卸しと、言語化', '00:22–00:32',
     '業務の棚卸しの進め方と、判断の根拠を言葉にしていく作業。'),
    ('業界を越えて、共通すること', '00:32–00:38',
     '業種が変わっても同じだったことと、変わったこと。ここが本セッションの山です。'),
    ('明日からの一歩', '00:38–00:43', '持ち帰り3点をまとめ、ご質問にお答えします。'),
    ('おわりに', '00:43–00:45', '翌日のセッションへの流れをご案内します。'),
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
  '    <p class="sec-note">この4つを共有できていると、このあとの話が具体的に聞こえます。</p>\n'
  + fig_versus(
      ('使いたい業務から、逆に引く', '用途を1つ決めてから、必要なデータを引く'),
      ('全体最適から、整える', 'まず基盤を作ってから、と考える'),
      [('着手の単位', 'エージェントに任せたい業務を、1つだけ',
        '全社のデータを、横断で統合する'),
       ('「整った」の定義', 'その用途に足りる水準を、先に言葉にする',
        '決めないまま進み、準備段階が終わらない'),
       ('かかる時間', '数か月で1周まわして、次を決められる',
        '年単位。途中で前提のほうが変わる'),
       ('失敗のしかた', '対象を選び間違える。選び直せばよい',
        '完成しても、使われないまま残る')],
      'Fig.1 ── どちらも「基盤を整える」と呼ばれますが、着手の単位が違います',
      '赤い側は、終わりが自分では決められない進め方です')
  + fig_ladder([
      ('用途を1つ決める',
       'どの業務のどの判断を渡すのか。ここが決まらないと、必要なデータも決まらない'),
      ('必要なデータを逆に引く',
       'その判断のために、人はいま何を見ているか。見ているものが、必要なデータ'),
      ('正本を1つ決める',
       '同じ数字が複数の場所にある状態をやめる。決めるだけで、答えの精度が上がる'),
      ('判断の理由を残す',
       '結果ではなく「なぜそう決めたか」。いちばん薄く、いちばん時間がかかる層'),
      ('「整った」を定義する',
       'その用途に足りる水準を、先に言葉にしておく。完璧なデータは目指さない'),
  ], 'Fig.2 ── 整える順番。上から下へ、この順で決めます',
     '順番を逆にすると、範囲が広がり続けて着地しません', asc=False)
  + '''    <div class="cards" data-wide>
      <div class="card"><span class="card-tag">1</span><h3>エージェントが力を出せない、二つの理由</h3><p>ひとつは、データが部署ごとに分断されていること。もうひとつは、判断の根拠が人の頭の中にしかないことです。前者はシステムの問題ですが、後者は業務そのものの問題で、解くのに時間がかかります。<b>多くの組織で足を止めるのは後者</b>です。</p></div>
      <div class="card"><span class="card-tag">2</span><h3>暗黙知の形式知化が、最大の山になる</h3><p>「なぜその判断をしたのか」を言葉にする作業は、システム構築ではなく業務の棚卸しそのものです。人手を最も割くべき場所であり、<b>ここを飛ばすと、必ずあとで戻ってくる</b>ことになります。</p></div>
      <div class="card"><span class="card-tag">3</span><h3>業種が変わっても、順番は同じなのか</h3><p>本日の登壇者は、IT・広告・保険・物流、そして消費財と、<b>業界を越えてデータ基盤の立ち上げに携わってきた</b>稀な経歴をお持ちです。「同じだったこと」と「変わったこと」を実体験で切り分けられる方は、そう多くありません。<span class="fw-bold">本セッションの山は、ここです。</span></p></div>
      <div class="card"><span class="card-tag">4</span><h3>扱うデータの性質が違えば、整え方も変わる</h3><p>消費財で見たいのは、買った記録そのものではなく、その手前にある暮らしの行動です。物流の実績データや保険の契約データとは、粒度も鮮度も揃え方も違う。<b>「データ基盤」という一語で括ると、この違いが消えます</b>。</p></div>
    </div>
  </div>
</section>
''')

# ── Questions ───────────────────────────────────────────────
A('<section class="sec-navy">\n  <div class="inner" data-reveal>\n'
  '    <span class="eyebrow">Questions</span>\n'
  '    <h2 class="sec-label">今日、うかがうこと</h2>\n'
  '    <p class="sec-note">この8問を、この順番でお聞きします。</p>\n'
  + fig_ranges(
      ['00:04', '00:12', '00:22', '00:32', '00:38'],
      [('データ基盤：どこから', 0, 1, 0, '優先順位のつけ方と「整った」の定義'),
       ('業務設計：言語化', 2, 2, 1, '誰が、どの単位で、どう協力を得たか'),
       ('業界を越えた共通項', 3, 4, 2, '同じだったことと、変わったこと'),
       ], 'Fig.3 ── 45分を、3つの塊に割る',
      '45分あっても、扱えるのは3つまでです',
      dark=True, note='押したら真ん中の塊を1問落とします。3つ目は必ず残します')
  + '''    <div class="two-col">
      <div class="two-col-item"><h3>データ基盤：どこから手をつけたか</h3><p class="tp-lead">限られた資源のなかでの、優先順位のつけ方をうかがいます。</p><p class="tp-q">最初に着手したのはどの領域で、なぜそこだったのですか？</p><p class="tp-q">全部を整えるのは無理ななかで、優先順位はどうつけましたか？</p><p class="tp-q">「整った」の水準を、経営にはどう説明して投資を通しましたか？</p></div>
      <div class="two-col-item"><h3>業務設計：棚卸しと、判断根拠の言語化</h3><p class="tp-lead">業務側の作業を、誰がどう動いたかまで具体的にうかがいます。</p><p class="tp-q">業務の棚卸しは、誰が、どんな単位で進めましたか？</p><p class="tp-q">判断の根拠を言葉にする作業に、現場はどう協力してくれましたか？</p><p class="tp-q">研究開発のデータと、日々の業務のデータでは、整え方は違いましたか？</p></div>
      <div class="two-col-item"><h3>業界を越えて、共通すること</h3><p class="tp-lead">複数の業界でデータ基盤を立ち上げてこられた経験から、一般化します。</p><p class="tp-q">業種が変わっても同じだったことと、変わったことは何ですか？</p><p class="tp-q">外から入って、最初の90日で何を見て、何から手を付けましたか？</p></div>
    </div>
  </div>
</section>
''')

# ── Summary ─────────────────────────────────────────────────
A('<section class="sec-light">\n  <div class="inner" data-reveal>\n'
  '    <span class="eyebrow">Summary</span>\n'
  '    <h2 class="sec-label">持ち帰りは、この3点</h2>\n'
  + fig_timeline([
      ('MONTH 1', '推進役', '使いたい業務を1つ決める',
       '判断が多く、記録がある業務を選ぶ', 0),
      ('MONTH 2', '現場', 'その業務の正本を1つ決める',
       '同じ数字が複数ある状態をなくす', 0),
      ('MONTH 3', '現場', '判断の理由を、その場で残す',
       '結果ではなく、判断の理由を書き足す', 2),
  ], 'Fig.4 ── 最初の3か月で、ここまでは進められます',
     '新しい投資は要りません。決めることと、残すことだけです',
     axis='最初の3か月')
  + '''    <div class="cards" data-take>
      <div class="card"><span class="card-tag">1</span><h3>基盤整備は全体最適から入らない。エージェントを使いたい業務から逆に引く</h3></div>
      <div class="card"><span class="card-tag">2</span><h3>判断根拠の言語化が最大のボトルネック。ここに人的リソースを割く</h3></div>
      <div class="card"><span class="card-tag">3</span><h3>業務プロセスの再設計は、AI導入プロジェクトではなく業務改善として立てる</h3></div>
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
open('/tmp/body_s5.html', 'w', encoding='utf-8').write(body)
print('本文フラグメントを書き出しました（%d文字）' % len(body))
