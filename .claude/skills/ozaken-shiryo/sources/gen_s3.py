#!/usr/bin/env python3
"""AX Table セッション3（茶圓将裕さん）の進行資料。

AX Table の8本は「進行台本」の型で組んである（Takeaway / Agenda /
Context / Questions / Summary）。その型は保ったまま、図版を入れて、
問いを登壇者にしか答えられないものに寄せる。
"""
import sys

S = '/home/user/ozaken-materials/.claude/skills/ozaken-shiryo/scripts'
sys.path.insert(0, S)
from domain_fig import fig_issues, fig_flow, fig_ranges, fig_check

B = []
A = B.append

A('<!--META title=AX Table セッション3｜またPoCで終わった | '
  'desc=本番化できない組織に共通する5つのパターン。数多くの導入を伴走してきた'
  '茶圓将裕さんに、詰まり方の型と、PoCが要る領域・要らない領域の線引きを聞く。'
  'AI・人工知能EXPO NEO「AX Table」セッション3の投影資料。-->')

A('''<section class="hero" data-kabe>
  <div class="kabe-veil" aria-hidden="true"></div>
  <div class="inner" data-reveal>
    <span class="eyebrow">AX Table ─ Session 3 ／ AX2</span>
    <h1 class="hero-title">またPoCで終わった</h1>
    <p class="hero-copy">本番化できない組織に共通する5つのパターン</p>
    <p class="hero-meta">8/5（水）9:30–10:00　｜　30分<br>茶圓 将裕（株式会社デジライズ）　×　小澤健祐（おざけん）</p>
  </div>
</section>
''')

# ── Takeaway ────────────────────────────────────────────────
A('''<section class="sec-light">
  <div class="inner" data-reveal>
    <span class="eyebrow">Takeaway</span>
    <h2 class="sec-label">このセッションで持ち帰っていただくもの</h2>
    <p class="stmt">自社がどのパターンで止まるのかを先に特定して、PoCを始める前に潰しておくこと。</p>
    <p class="sec-note">この一点に絞って、30分お話しします。</p>
  </div>
</section>
''')

# ── Agenda ──────────────────────────────────────────────────
STEPS = [
    ('はじめに', '00:00–00:03', 'AX Table全体の趣旨と、このセッションで扱うことを。'),
    ('いま、現場で起きていること', '00:03–00:07',
     '「PoC沼」とは何か。毎日この景色を見ている立場から、いまの実感を。'),
    ('本番化できない5つのパターン', '00:07–00:17',
     '5つの型を、実際に起きた失敗とセットで。このセッションの中心です。'),
    ('抜けた企業がした順番と、PoCが要らない領域', '00:17–00:26',
     '何を、どの順で変えたのか。そして、そもそも検証が要らない領域の線引きを。'),
    ('明日からの一歩', '00:26–00:28', '自社を診断するためのチェックリストをお渡しします。'),
    ('おわりに', '00:28–00:30', '同日の次のセッションをご案内します。'),
]
A('<section class="sec-navy">\n  <div class="inner" data-reveal>\n'
  '    <span class="eyebrow">Agenda</span>\n'
  '    <h2 class="sec-label">進行</h2>\n'
  '    <p class="sec-note">30分。最後の数分で、持ち帰りポイントをまとめます。</p>\n'
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
  + fig_issues([
      ('目的がすり替わる', 'AIを使うこと自体が目的になる'),
      ('オーナーが不在', '情シスだけで走り、使う人が決まっていない'),
      ('合格ラインが無い', '終わってから基準を考えることになる'),
      ('運用が決まらない', '動いた後、誰が見るのか決まっていない'),
      ('経営が関心を失う', '判断が先送りされ、静かに消える'),
  ], 'Fig.1 ── 本番化が止まる、5つの場所',
     'どれか1つで止まると、残りが全部できていても本番には上がりません',
     uid='s3a')
  + fig_flow([
      ('対象を1つに絞る', '同時に走らせる本数を減らし、意思決定を速くする'),
      ('オーナーを立てる', '使う部門の側から責任者を出す。情シスは支える側へ'),
      ('合格ラインを文章に', '何がどこまでできたら本番か。判断者と時期も同時に'),
      ('運用の持ち主を決める', '監視・劣化対応・問い合わせを引き受ける人を先に'),
  ], 'Fig.2 ── 沼から抜けた企業が、動かした順番',
     '順番が逆になると、どれだけ手間をかけても本番には上がりません',
     uid='s3b', note='この順番そのものを、当日うかがいます')
  + '''    <div class="cards" data-wide>
      <div class="card"><span class="card-tag">1</span><h3>本番化できない5つのパターン</h3><p>①目的が「AIを使うこと」そのものにすり替わる ②情シス主導で、現場のオーナーが不在 ③検証に合格ラインがない ④運用を持つ人が決まっていない ⑤経営が途中で関心を失う。セッションでは、この5つを実際の失敗とセットで扱います。</p></div>
      <div class="card"><span class="card-tag">2</span><h3>合格ラインは、始める前に文章で決めておく</h3><p>検証が終わってから基準を考えると、必ず「もう少し様子を見よう」に着地します。何がどこまでできたら本番に上げるのか。開始前に文章で残しておくことが、最も効く一手です。判断者と判断の時期も、同時に決めておきます。</p></div>
      <div class="card"><span class="card-tag">3</span><h3>検証が終わる頃には、前提のツールが変わっている</h3><p>半年かけて検証すると、その間にモデルは何度も入れ替わります。「当時できなかったこと」を前提に設計した仕組みが、完成した時点で古い。<b>検証期間の長さそのものが、失敗の原因になる</b>という、この2〜3年で新しく現れた詰まり方です。</p></div>
      <div class="card"><span class="card-tag">4</span><h3>そもそもPoCが要らない領域が増えている</h3><p>汎用のツールを配って使わせたほうが速い領域と、業務に埋め込むために検証が要る領域は、本来まったく別のものです。<b>その線引きをしないまま全部をPoCにかけている</b>ことが、沼の入口になっています。</p></div>
    </div>
  </div>
</section>
''')

# ── Questions ───────────────────────────────────────────────
A('<section class="sec-navy">\n  <div class="inner" data-reveal>\n'
  '    <span class="eyebrow">Questions</span>\n'
  '    <h2 class="sec-label">今日、うかがうこと</h2>\n'
  '    <p class="sec-note">この6問を、この順番でお聞きします。</p>\n'
  + fig_ranges(
      ['00:03', '00:07', '00:12', '00:17', '00:22', '00:26'],
      [('詰まり方の型', 0, 2, 1, '5つのパターンを、失敗とセットで'),
       ('抜けた企業の順番', 3, 4, 0, '何を、どの順で変えたのか'),
       ('検証の要否の線引き', 4, 5, 2, 'PoCが要る領域と、要らない領域'),
       ], 'Fig.3 ── どの問いを、どの時間に置くか',
      '30分は短い。問いが後ろにずれると、いちばん聞きたい話が入りません',
      dark=True, note='進行が押したら、真ん中の塊を1問落として最後を守ります')
  + '''    <div class="two-col">
      <div class="two-col-item"><h3>数多くの現場から見た、詰まり方の型</h3><p class="tp-lead">何社も伴走してきた立場から、止まる企業と上がる企業の違いを、具体で示していただきます。</p><p class="tp-q">これまで伴走してきた中で、PoCで止まる企業と本番に上がる企業は、最初の一手が何か違いましたか？</p><p class="tp-q">5つのうち、いま最も多いのはどのパターンですか。業種や規模で偏りはありますか？</p><p class="tp-q">「これは本番に上がらないな」と、着手の時点で分かってしまう瞬間はありますか？</p></div>
      <div class="two-col-item"><h3>ツールの進化が速すぎる時代の、検証のしかた</h3><p class="tp-lead">毎日この分野の変化を追い続けている立場から、検証の設計そのものを問い直します。</p><p class="tp-q">半年かけたPoCは、いま何が起きますか。検証している間に前提が変わることを、どう設計に織り込みますか？</p><p class="tp-q">そもそもPoCが要らない領域と、要る領域の線引きはどこですか？</p><p class="tp-q">研修とツール提供を一体で入れる進め方は、PoCと何が決定的に違いますか？</p></div>
    </div>
  </div>
</section>
''')

# ── Summary ─────────────────────────────────────────────────
A('<section class="sec-light">\n  <div class="inner" data-reveal>\n'
  '    <span class="eyebrow">Summary</span>\n'
  '    <h2 class="sec-label">持ち帰りは、この3点</h2>\n'
  + fig_check([
      (False, 'PoCの企画書に、運用体制の欄が無い', '動いた後に誰が持つのかが空欄なら、その時点で本番には上がりません'),
      (False, '合格ラインが「様子を見て判断」になっている', '基準を後から考えると、必ず先送りに着地します'),
      (False, '走っているPoCの本数を、成熟度として数えている', '本数は指標になりません。同時に走るほど、一件あたりの判断が遅くなります'),
      (True, '対象を1つに絞り、現場のオーナーを先に立てている', 'この2つが揃っている案件は、止まっても原因がすぐ分かります'),
      (True, '配れば済む領域と、検証が要る領域を分けている', '全部をPoCにかけないだけで、進む速さが変わります'),
  ], 'Fig.4 ── 自社診断：3つ当てはまったら、いまのPoCは止まります',
     '会場で1つ選んで、持ち帰っていただくためのチェックです')
  + '''    <div class="cards" data-take>
      <div class="card"><span class="card-tag">1</span><h3>5パターンのうち、自社が該当するものを1つ特定して帰る</h3></div>
      <div class="card"><span class="card-tag">2</span><h3>PoC開始前に「本番化の判断基準」と判断者を、文章で決めておく</h3></div>
      <div class="card"><span class="card-tag">3</span><h3>配れば済む領域と、検証が要る領域を分ける。全部をPoCにかけない</h3></div>
    </div>\n  </div>\n</section>\n''')

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
open('/tmp/body_s3.html', 'w', encoding='utf-8').write(body)
print('本文フラグメントを書き出しました（%d文字）' % len(body))
