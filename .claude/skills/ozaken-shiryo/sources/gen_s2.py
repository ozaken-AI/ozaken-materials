#!/usr/bin/env python3
"""AX Table セッション2（朝比奈さん）の進行資料。

進行台本の型（Takeaway / Agenda / Context / Questions / Summary）は保ったまま、
図版を4点入れ、問いを「実際に3年計画を書いて経営を通した人」にしか
答えられないものへ寄せる。

登壇者の経歴は公開情報から確認できなかったため、
経歴にもとづく記述は置いていない。問いの側で引き出す組み立てにしている。
"""
import sys

S = '/home/user/ozaken-materials/.claude/skills/ozaken-shiryo/scripts'
sys.path.insert(0, S)
from domain_fig import fig_gap, fig_ladder, fig_ranges, fig_check

B = []
A = B.append

A('<!--META title=AX Table セッション2｜AI推進ロードマップのつくり方 | '
  'desc=「なんとなくAI」から脱却する3年計画の設計。積み上げではなく逆算で描く方法、'
  '年次ごとに置くもの、経営に通る計画との差、そして計画がずれたときの直し方を聞く。'
  'AI・人工知能EXPO NEO「AX Table」セッション2の投影資料。-->')

A('''<section class="hero" data-kabe>
  <div class="kabe-veil" aria-hidden="true"></div>
  <div class="inner" data-reveal>
    <span class="eyebrow">AX Table ─ Session 2 ／ AX1</span>
    <h1 class="hero-title">AI推進ロードマップのつくり方</h1>
    <p class="hero-copy">「なんとなくAI」から脱却する3年計画の設計</p>
    <p class="hero-meta">8/5（水）12:45–13:30　｜　45分<br>朝比奈さん　×　小澤健祐（おざけん）</p>
  </div>
</section>
''')

# ── Takeaway ────────────────────────────────────────────────
A('''<section class="sec-light">
  <div class="inner" data-reveal>
    <span class="eyebrow">Takeaway</span>
    <h2 class="sec-label">このセッションで持ち帰っていただくもの</h2>
    <p class="stmt">3年目の到達像を1文で書き、そこから「今年やらないこと」を決めて帰ること。</p>
    <p class="sec-note">この一点に絞って、45分お話しします。</p>
  </div>
</section>
''')

# ── Agenda ──────────────────────────────────────────────────
STEPS = [
    ('はじめに', '00:00–00:04', '計画の「型」を持ち帰っていただくセッションです。'),
    ('いま、現場で起きていること', '00:04–00:12',
     '「なんとなくAI」の三つの症状。自社に当てはまるものがあるかを、その場で確かめていただきます。'),
    ('逆算で描くという考え方', '00:12–00:22',
     '積み上げでは計画にならない理由と、3年目の到達像から逆に引く思考法。'),
    ('1年目・2年目・3年目に置くもの', '00:22–00:32',
     '年次ごとの中身と、その境界の引き方。「やらないこと」の決め方も含めて。'),
    ('経営に通す、そして計画を直す', '00:32–00:38',
     '承認される計画との差と、現実に合わなくなったときの修正のしかた。'),
    ('明日からの一歩', '00:38–00:43', '持ち帰り3点をまとめ、ご質問にお答えします。'),
    ('おわりに', '00:43–00:45', '次のセッションへの流れをご案内します。'),
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
  + fig_gap([
      ('課題を並べて、できることから足していく', '3年目の到達像を、先に1文で書く'),
      ('全部が「やる」に見えてしまう', '「今年やらないこと」が決まる'),
      ('投資額の根拠が、どこからも出てこない', '到達像との差が、そのまま根拠になる'),
      ('遅れていても、遅れていると気づけない', 'どこが遅れているかが、一目で分かる'),
  ], 'Fig.1 ── 同じ3年計画でも、書き方でまったく別物になります',
     '積み上げは網羅的に見えますが、優先順位も投資の根拠も出てきません',
     uid='s2a', left_label='積み上げで書いた計画', right_label='逆算で書いた計画')
  + fig_ladder([
      ('1年目 ── 足場をつくる',
       '測るのは成果ではなく整備度。データ・体制・ルールがどこまで揃ったかで見る'),
      ('2年目 ── 型を横に配る',
       '1年目に通した1業務の型を、他部門へ。ここで初めて削減時間を成果として測る'),
      ('3年目 ── 事業の側へ出す',
       '社内の効率化から、顧客に届く価値へ。売上や提供価値の指標に切り替える'),
  ], 'Fig.2 ── 年次で置くものと、測るものを変える',
     '3年とも同じ指標で測ろうとすると、1年目に無理が出ます', asc=False)
  + '''    <div class="cards" data-wide>
      <div class="card"><span class="card-tag">1</span><h3>「なんとなくAI」には、三つの症状がある</h3><p>予算の根拠を説明できない。成果の測り方が決まっていない。施策が単発で終わり、次につながらない。この三つが揃うと、活動量はあるのに翌年の予算が取れません。まず自社に当てはまるものがないかを確かめてください。</p></div>
      <div class="card"><span class="card-tag">2</span><h3>積み上げ式では、計画になりません</h3><p>現状の課題を並べて足していくやり方は、一見網羅的に見えますが、優先順位も投資の根拠も出てきません。3年目の到達像を先に置き、そこから逆に引く。<b>この順序ではじめて、「今年やらないこと」が決まります</b>。</p></div>
      <div class="card"><span class="card-tag">3</span><h3>1年目のKPIは、成果ではなく基盤の整備度で置く</h3><p>初年度から売上や削減額のKPIを置くと、達成しやすい小さな施策ばかりを選ぶことになり、土台が育ちません。データがどこまで揃ったか、推進の体制ができたか、社内ルールが定まったか。1年目はこの整備度で測るほうが現実的です。</p></div>
      <div class="card"><span class="card-tag">4</span><h3>計画は必ず陳腐化する。それを前提に組み込む</h3><p>モデルも製品構成も1年で変わります。固定した瞬間に古くなるため、<b>「いつ、誰が、何を見て見直すか」を計画そのものに書き込んで</b>おきます。見直しは失敗の証拠ではなく、計画の一部です。</p></div>
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
      [('計画が無いと、何が起きるか', 0, 1, 0, '積み上げと逆算の、決定的な違い'),
       ('年次に、何を置くか', 2, 2, 1, '足場の中身と、やらないと決めたこと'),
       ('経営に通す、そして直す', 3, 4, 2, '承認の差と、ずれたときの直し方'),
       ], 'Fig.3 ── 45分を、3つの塊に割る',
      '45分あっても、扱えるのは3つまでです',
      dark=True, note='押したら真ん中の塊を1問落とします。3つ目は必ず残します')
  + '''    <div class="two-col">
      <div class="two-col-item"><h3>ロードマップがない組織で、起きること</h3><p class="tp-lead">計画を持たないまま進めた組織が1年後にどうなるかを、実際の景色として共有します。</p><p class="tp-q">ロードマップがない組織では、1年後に何が起きていましたか？</p><p class="tp-q">積み上げで書いた計画と、逆算で書いた計画は、どこが決定的に違いましたか？</p><p class="tp-q">3年目の到達像は、どのくらいの粒度で書くべきですか？</p></div>
      <div class="two-col-item"><h3>1年目・2年目・3年目に、何を置くか</h3><p class="tp-lead">年次ごとの中身を、具体的な打ち手のレベルまで下ろします。</p><p class="tp-q">1年目に置くべき「足場」の中身は、具体的に何ですか？</p><p class="tp-q">1年目に、あえて「やらない」と決めたことは何でしたか？</p><p class="tp-q">2年目と3年目の境界は、どこで引きますか？</p></div>
      <div class="two-col-item"><h3>経営に通る計画と、通らない計画</h3><p class="tp-lead">承認を得るための書き方と、途中で修正するときの作法をうかがいます。</p><p class="tp-q">経営に承認される計画と、されない計画の差は何ですか？</p><p class="tp-q">投資額の根拠は、何をもって説明しましたか？</p><p class="tp-q">計画のうち、実際にそのとおりになったのはどのくらいでしたか。ずれたのはどこですか？</p></div>
    </div>
  </div>
</section>
''')

# ── Summary ─────────────────────────────────────────────────
A('<section class="sec-light">\n  <div class="inner" data-reveal>\n'
  '    <span class="eyebrow">Summary</span>\n'
  '    <h2 class="sec-label">持ち帰りは、この3点</h2>\n'
  + fig_check([
      (False, '3年目の到達像が、1文で書けない',
       '書けないのであれば、それは計画ではなく願望です'),
      (False, '1年目のKPIが、削減額や売上になっている',
       '達成しやすい小さな施策ばかりを選ぶことになり、土台が育ちません'),
      (False, '「今年やらないこと」が、どこにも書いていない',
       'すべてが「やる」の計画は、優先順位が無いのと同じです'),
      (True, '見直しの時期と、見る人が計画に書いてある',
       '見直しは失敗の証拠ではなく、計画の一部です'),
      (True, '投資額の根拠を、到達像との差で説明できる',
       '差が根拠になっていれば、経営は判断できます'),
  ], 'Fig.4 ── 計画の健康診断：上の3つが当てはまったら、書き直しです',
     '自社の計画を思い浮かべながら、1つ選んで持ち帰ってください')
  + '''    <div class="cards" data-take>
      <div class="card"><span class="card-tag">1</span><h3>3年目の到達像を1文で書けるか。書けないなら計画ではなく願望</h3></div>
      <div class="card"><span class="card-tag">2</span><h3>1年目のKPIは「成果」ではなく「基盤の整備度」で置く</h3></div>
      <div class="card"><span class="card-tag">3</span><h3>ロードマップは年1回の見直し前提で設計する（固定した瞬間に陳腐化する）</h3></div>
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
open('/tmp/body_s2.html', 'w', encoding='utf-8').write(body)
print('本文フラグメントを書き出しました（%d文字）' % len(body))
