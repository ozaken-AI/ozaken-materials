#!/usr/bin/env python3
"""AX Table セッション8（日本マイクロソフト 大森彩子さん）の進行資料。

題を「Copilotで現場はどう変わるか」から
「AIエージェントで現場はどう変わるか」へ変更。
主語が製品からエージェントに移るので、問いも
「機能はどこまで使えるか」から「どこまで任せられるか」へ寄せる。

アーカイブ『Copilot大全』の Section 04 と揃えたところ：
  「聞けば答える」（座席課金）→「任せると片付ける」（使用量課金）
  この段では費用の性質そのものが変わる
"""
import sys

S = '/home/user/ozaken-materials/.claude/skills/ozaken-shiryo/scripts'
sys.path.insert(0, S)
from domain_fig import fig_gap, fig_issues, fig_cols, fig_ranges, fig_check

B = []
A = B.append

A('<!--META title=AX Table セッション8｜AIエージェントで現場はどう変わるか | '
  'desc=Microsoft 365導入企業の活用リアル。「聞けば答える」で止まっている社内のCopilotを、'
  '「任せると片付ける」へどう進めるか。会議・資料作成・データのどこまで任せられるのか、'
  '定着した企業としなかった企業の差はどこにあったのかを、'
  '日本マイクロソフトの大森彩子さんと。'
  'AI・人工知能EXPO NEO「AX Table」セッション8の投影資料。-->')

A('''<section class="hero" data-kabe>
  <div class="kabe-veil" aria-hidden="true"></div>
  <div class="inner" data-reveal>
    <span class="eyebrow">AX Table ─ Session 8 ／ Copilot 活用</span>
    <h1 class="hero-title">AIエージェントで<br>現場はどう変わるか</h1>
    <p class="hero-copy">Microsoft 365導入企業の活用リアル</p>
    <p class="hero-meta">8/6（木）16:00–16:45　｜　45分<br>大森 彩子　エバンジェリスト／ソリューションエンジニア<br>日本マイクロソフト（株）クラウド &amp; AI ソリューション事業本部 Azure技術本部<br>×　小澤健祐（おざけん）</p>
  </div>
</section>
''')

# ── Takeaway ────────────────────────────────────────────────
A('''<section class="sec-light">
  <div class="inner" data-reveal>
    <span class="eyebrow">Takeaway</span>
    <h2 class="sec-label">このセッションで持ち帰っていただくもの</h2>
    <p class="stmt">「聞けば答える」で止まっている社内のAIを、「任せると片付ける」へ進める一歩を持ち帰ること。</p>
    <p class="sec-note">この一点に絞って、45分お話しします。</p>
  </div>
</section>
''')

# ── Agenda ──────────────────────────────────────────────────
STEPS = [
    ('はじめに', '00:00–00:04',
     '2日間の最後のセッションです。「導入したのに、業務は同じ」を今日で解きます。'),
    ('いま、現場で起きていること', '00:04–00:10',
     '導入企業からいちばん多く寄せられる相談と、止まってしまう典型のかたち。'),
    ('アシスタントから、エージェントへ', '00:10–00:20',
     '「聞けば答える」と「任せると片付ける」の境目。このセッションの中心です。'),
    ('どの業務なら、任せられるのか', '00:20–00:30',
     '会議・資料作成・データ。実務で使える水準はどこまで来ているのか。'),
    ('定着を、どう設計するか', '00:30–00:38',
     '成果が出た企業と、出なかった企業の差。打ち手の違いでうかがいます。'),
    ('明日からの一歩', '00:38–00:43', '持ち帰っていただく3点をまとめ、ご質問にお答えします。'),
    ('おわりに', '00:43–00:45', '2日間の総括と、AICX協会のご案内。'),
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
      ('人が開いて、その都度たずねる', '条件が揃うと、人を待たずに動き出す'),
      ('速くなるのは、たずねた人の手元だけ', '工程そのものが、人の手を離れる'),
      ('席の数で費用が決まる。使わなくても満額', '動かした量で費用が決まる'),
      ('個人の時短で終わりやすい', '誰が作った何が動いているか、統制が要る'),
  ], 'Fig.1 ── 「聞けば答える」と「任せると片付ける」は、別のもの',
     '座席で買う世界から、動かした量で払う世界へ。この段を越えると費用の性質が変わります',
     uid='s8gap',
     left_label='アシスタント ── 聞けば答える',
     right_label='エージェント ── 任せると片付ける')
  + fig_issues([
      ('教える場がない', '使い方を知る機会が無い'),
      ('上手い人がいない', '真似する相手が見つからない'),
      ('成果が出てこない', '続ける理由が社内に残らない'),
      ('3ヶ月で落ちる', '意欲ではなく、仕組みの問題'),
  ], 'Fig.2 ── 定着しない組織には、同じ欠落が同じ順で並ぶ',
     '導入から3ヶ月ほどで利用が落ちるとき、原因は現場の意欲ではありません',
     uid='s8b')
  + fig_cols([
      ('MEETING', '会議', '要約と、欠席者の追いつき',
       '最も利用の多い領域。ただし共有する前に人がどこを直しているかで、実務で使える水準かどうかが分かれます', 0),
      ('DOCUMENT', '資料作成', '効くのは、書く前と直したあと',
       '白紙から書かせるより、構成案づくりと体裁直しに効きます。素材が散らかっていると、そこで空回りします', 2),
      ('DATA', 'データ', '既存ファイルの整い方で決まる',
       '表が整っていれば任せられます。結合セルと注記だらけの表なら、まず表を直すほうが早い', 3),
  ], 'Fig.3 ── 同じ製品でも、業務によって効き方がまったく違う',
     'どこから使わせるかを決めるとき、この違いを踏まえていないと順番を間違えます')
  + '''    <div class="cards" data-wide>
      <div class="card"><span class="card-tag">1</span><h3>「聞けば答える」と「任せると片付ける」は、費用の性質まで違う</h3><p>Microsoft 365 Copilotは、既存の業務アプリの中で「聞けば答える」存在です。ここから一段進んで「任せると片付ける」にすると、<b>座席課金の世界から、動かした量で決まる世界へ移ります</b>。同じ製品名の中に、性質の違う2つの段があります。<span class="fw-bold">（アーカイブ『Copilot大全』より）</span></p></div>
      <div class="card"><span class="card-tag">2</span><h3>定着は、利用率では測れない</h3><p>月に一度触った人を数えても、定着しているかは分かりません。見るべきは、<b>同じ業務のなかで繰り返し使われているかどうか</b>です。リピートが起きていない機能は、どれだけ利用者数が多くても定着していません。</p></div>
      <div class="card"><span class="card-tag">3</span><h3>配布の順番が、成果を分ける</h3><p>全社一斉配布は、効く業務と効かない業務を同時に走らせることになります。効く部署から順に広げ、そこでの使い方を持って次へ移るほうが、<b>結果的に全社へ届くのは早くなります</b>。</p></div>
      <div class="card"><span class="card-tag">4</span><h3>前日のGeminiセッションと、対になる構成です</h3><p>同じ質問の構造で、前日は Google Workspace を扱いました。両方をお聞きいただいた方は、<b>自社の環境ではどちらがどの業務に効くのかを、同じ物差しで比べられます</b>。</p></div>
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
      ['00:04', '00:12', '00:20', '00:28', '00:36'],
      [('エージェントへ進む', 0, 1, 0, 'いま現場はどこまで来たか'),
       ('どの業務なら任せられるか', 1, 3, 1, '会議・資料・データの実際'),
       ('定着を、どう設計するか', 3, 4, 2, '出た企業と、出なかった企業'),
       ], 'Fig.4 ── 45分を、3つの塊に割る',
      '45分あっても、扱えるのは3つまでです',
      dark=True, note='押したら真ん中の塊を1問落とします。3つ目は必ず残します')
  + '''    <div class="two-col">
      <div class="two-col-item"><h3>アシスタントから、エージェントへ</h3><p class="tp-lead">導入企業の現在地を、いちばん多い使われ方からうかがいます。</p><p class="tp-q">Microsoft 365を入れた企業で、いま実際にいちばん多い使われ方は何ですか？</p><p class="tp-q">「聞けば答える」から「任せると片付ける」へ進んだ現場は、何がきっかけでしたか？</p><p class="tp-q">エージェントを作り始める組織と、そうでない組織の差はどこにありますか？</p></div>
      <div class="two-col-item"><h3>どの業務なら、任せられるのか</h3><p class="tp-lead">効く工程と、そうでない工程を切り分けます。</p><p class="tp-q">会議の要約は、どこまで実務で使えますか。共有する前に、人はどこを直していますか？</p><p class="tp-q">資料作成では、どの工程にいちばん効きますか？</p><p class="tp-q">既存のファイルが整っていない場合、何から直すべきですか？</p></div>
      <div class="two-col-item"><h3>定着を、どう設計するか</h3><p class="tp-lead">多くの現場をご覧になってきた立場から、打ち手の違いをうかがいます。</p><p class="tp-q">「どの業務から使わせるか」の順番に、正解はありますか？</p><p class="tp-q">定着した企業と、しなかった企業の差はどこにありましたか？</p><p class="tp-q">エバンジェリストとして現場を見てこられて、この1年でいちばん変わったのは何ですか？</p></div>
    </div>
  </div>
</section>
''')

# ── Summary ─────────────────────────────────────────────────
A('<section class="sec-light">\n  <div class="inner" data-reveal>\n'
  '    <span class="eyebrow">Summary</span>\n'
  '    <h2 class="sec-label">持ち帰りは、この3点</h2>\n'
  + fig_check([
      (False, '成果の報告が、利用率と利用者数になっている',
       '触った人の数は、業務が変わっていなくても増えます。判断材料になりません'),
      (False, '全社に一斉配布して、そこで終わっている',
       '効く業務と効かない業務を同時に走らせることになり、平均が動きません'),
      (False, '使い方を共有する場が、社内にひとつも無い',
       '導入から3ヶ月ほどで利用が落ちます。意欲ではなく、仕組みの問題です'),
      (True, '同じ業務の中で、繰り返し使われているかを見ている',
       'リピートが起きていない機能は、利用者数が多くても定着していません'),
      (True, '「任せる」へ進む前に、渡す先の資料と表を整えてある',
       '素材が散らかったままエージェントを作ると、必ず作り直しになります'),
  ], 'Fig.5 ── 自社診断：上の3つが当てはまったら、まだ「聞けば答える」の段です',
     '会場で1つ選んで、月曜からの一歩として持ち帰ってください')
  + '''    <div class="cards" data-take>
      <div class="card"><span class="card-tag">1</span><h3>全社一斉配布ではなく、効く業務・効く部署から順に広げる</h3></div>
      <div class="card"><span class="card-tag">2</span><h3>定着の指標は利用率ではなく、業務の中でのリピート利用</h3></div>
      <div class="card"><span class="card-tag">3</span><h3>「任せる」へ進む前に、渡す先を整える（ここを飛ばす組織が非常に多い）</h3></div>
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
open('/tmp/body_s8.html', 'w', encoding='utf-8').write(body)
print('本文フラグメントを書き出しました（%d文字）' % len(body))
