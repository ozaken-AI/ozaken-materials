"""演繹・帰納・非合理性と計画的偶発性を 既存本文を保って追加する"""
from practical_guides import chapter, figure, route, sheet, rows, srcs, sections, apply_styles, apply_body

LOGIC = 'https://plato.stanford.edu/entries/logic-inductive/'
REASON = 'https://plato.stanford.edu/entries/practical-reason/'
PREFIX = 'career11r--'
CHANCE_PREFIX = 'career12h--'
CHANCE_ORIGINAL = 'https://doi.org/10.1002/j.1556-6676.1999.tb02431.x'
CHANCE_RESEARCH = 'https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2022.899411/full'


def step(label, text):
    return f'<div class="cc-reason-step"><span>{label}</span><p>{text}</p></div>'


def build():
    comparison = ('<div class="cc-reason-compare">'
        '<article><p class="cc-reason-en">INDUCTION</p><h3>帰納 <small>きのう</small></h3>'
        '<p class="cc-reason-definition">事例から 傾向や仮説を見つける</p>'
        + step('観察した事例','相談した初心者のうち<br>何人もが 設定でつまずいていた')
        + '<span class="cc-reason-arrow" aria-hidden="true">↓</span>'
        + step('考えられる傾向','ほかの初心者も 設定で<br>つまずきやすいのではないか')
        + '<p class="cc-reason-check">別の人や条件では違うかもしれない<br>新しい事例で確かめる</p></article>'
        '<article><p class="cc-reason-en">DEDUCTION</p><h3>演繹 <small>えんえき</small></h3>'
        '<p class="cc-reason-definition">前提から 筋道を立てて結論を導く</p>'
        + step('前提にするルールと事実','未解決の相談は 人が対応する<br>この相談は まだ未解決だ')
        + '<span class="cc-reason-arrow" aria-hidden="true">↓</span>'
        + step('前提から導く結論','この相談には<br>人が対応する')
        + '<p class="cc-reason-check">前提が正しく 推論も妥当なら<br>結論は前提から必ず導かれる</p></article></div>')
    html = chapter(PREFIX+'logic','sec-navy','11A / 帰納と演繹',
        '帰納は 事例から傾向へ<br>演繹は 前提から結論へ',
        'キャリアを考えるときも 「何が起きているかを読むこと」と「方針から行動を導くこと」を使い分ける<br>初心者からの相談を受ける仕事で 2つの考え方を比べてみる',
        figure('THINKING GUIDE 01','同じ相談業務を 2つの考え方で見る',comparison,
            '説明用の架空例　帰納の結論は確定ではない　演繹は前提そのものの正しさを保証しない'),
        [('どちらが上かではなく どう組み合わせるか','事例から得た仮説を調べ 方針を決め その方針を個別の判断に使う<br>帰納だけをAI 演繹だけを人間の専売特許として分ける話ではない')],
        after=srcs([('用語の定義：Stanford Encyclopedia of Philosophy「Inductive Logic」',LOGIC)]))

    value = ('<div class="cc-value-origin"><p class="cc-reason-en">MY STARTING POINT</p>'
        '<p class="cc-origin-quote">効率がよくても<br><em>この人を置き去りにしたくない</em></p>'
        '<div class="cc-origin-path">'
        + step('体験・感情','自分も初心者のときに<br>相談できず 困った')
        + '<span aria-hidden="true">→</span>'
        + step('大切にする価値','困った人が<br>助けを求められること')
        + '<span aria-hidden="true">→</span>'
        + step('自分で選ぶ方針','未解決の相談には<br>人が対応する') + '</div></div>')
    html += chapter(PREFIX+'values','sec-light','11B / 人間の演繹を支えるもの',
        '人間の演繹の出発点に<br>「それでも こうしたい」を置く',
        '筆者が大切にしたいのは 損得だけでは割り切れない人間の「非合理性」<br>偏愛や悔しさ 美意識が 何を前提として選ぶかを支え キャリアの方向をつくる',
        figure('THINKING GUIDE 02','思いを 方針の出発点にする',value,
            '筆者のキャリア観を表した概念図　体験から価値を選ぶ部分は 演繹そのものではない'),
        [('「非合理性」は ここでは比喩として使う','効率や利益だけでは説明しきれない こだわりを指す<br>演繹は論理的な推論であり 価値を大切にする選択が不合理だという意味ではない'),
         ('正解率が高いだけでは 進む方向は決まらない','どの条件を優先するかで 選ぶ仕事や取り組む課題は変わる<br>なぜその方針で働きたいのかを 自分の体験から説明できることが大切になる')],
        after=srcs([('価値と行動を考える参考：Stanford Encyclopedia of Philosophy「Practical Reason」',REASON)]))

    html += chapter(PREFIX+'career','sec-navy','11C / 方針から仕事を選ぶ',
        '同じAIを使っても<br>人が選ぶ前提で 仕事は変わる',
        'たとえば 問い合わせ対応にAIを使うとき<br>「処理を速くする」に加えて「初心者が相談を諦めない」を 仕事の条件にする',
        figure('THINKING GUIDE 03','価値を 方針・判断・仕事へつなぐ',sheet([
            ('自分のWhy','初心者が 困ったまま諦める状況を減らしたい'),
            ('選ぶ方針','AIで未解決の相談には 人が対応する'),
            ('演繹で判断する','この相談はAIで未解決だ → 方針に従って 人が対応する'),
            ('形にする仕事','AIから人へつなぐ窓口と 引き継ぎの手順を設計する'),
            ('積みたい経験','相談者に話を聞く 引き継ぎの条件を決める 対応後の結果を確かめる'),
        ],'初心者向けサポートを設計する 架空のキャリア例'),
            '方針と事実から個別の判断を導く部分が演繹　仕事の設計やスキル選びには ほかの選択肢の比較も必要'),
        [('「こうしたい」から 育てるスキルを選ぶ','資料を速く作る力に加えて 困りごとの聞き取りや 部門間の調整を学ぶ<br>資格やツール名を先に並べるのではなく 自分の方針を実現するために必要な力を選ぶ')])

    html += chapter(PREFIX+'practice','sec-light','11D / 思いを仕事にする練習',
        '思いを起点に 論理で形にし<br>現実を見て 更新する',
        '「好きだから正しい」で終わらせず 大切にしたい価値と 実際の結果を照らし合わせる<br>自分の前提を見直すことが 続くメタ認知の話につながる',
        figure('THINKING GUIDE 04','人間のこだわりを 検証できる仕事へつなぐ',
            route([('価値を選ぶ','何を大切にするか','初心者が相談を<br>諦めないこと'),
                   ('演繹する','方針を判断に使う','未解決なら<br>人につなぐ'),
                   ('試す','小さく形にする','一つの窓口で<br>引き継ぎを試す'),
                   ('帰納する','結果から仮説を得る','つまずいた事例から<br>改善点を探す')])
            + '<p class="cc-reflection">↶ 仮説を確かめ 方針・手段・価値の優先順位を見直す</p>',
            '試行・観察には帰納の考え方を使う　方針があっても成果は保証されないため 実際の結果を確認する'),
        [('AIに相談しても 自分の選択を引き受ける','AIに事例の整理・方針の矛盾探し・実行案の比較を手伝ってもらう<br>そのうえで 何を優先して進むかを選び 関係する人と合意し 結果を確かめる'),
         ('まず 3行だけ書いてみる','①私は 誰のどんな困りごとを放っておけないか<br>②そのために どんな方針を置くか<br>③来週 何を小さく試し 何を見て判断するか')])
    return html


def build_happenstance():
    html = chapter(CHANCE_PREFIX+'theory','sec-light','12A / プランド・ハップンスタンス理論',
        '偶然を待つだけでなく<br>機会につながる行動を増やす',
        'プランド・ハップンスタンス理論は 日本語で「計画的偶発性理論」<br>予期しない出会いや出来事を 学びやキャリアの機会として生かすための考え方',
        figure('CHANCE GUIDE 01','偶然を機会に変える 5つのスキル',
            rows(['スキル','意味','来週できる行動の例'],[
                ('好奇心<br><small>Curiosity</small>','新しい学びを探す','気になる他部署の仕事を 一つ聞く'),
                ('持続性<br><small>Persistence</small>','つまずいても 工夫して続ける','相談への反応が薄ければ 聞き方を変える'),
                ('柔軟性<br><small>Flexibility</small>','考えや行動を 状況に合わせて変える','想定外の依頼も 自分の関心との接点を探す'),
                ('楽観性<br><small>Optimism</small>','新しい機会は実現できると捉える','「自分には無理」と閉じず 小さな参加方法を探す'),
                ('冒険心<br><small>Risk taking</small>','結果が不確かでも 行動する','時間の上限を決め 未経験の役割を一度試す'),
            ]),
            'Mitchell・Levin・Krumboltzが1999年に提唱　5スキルの意味を平易に言い換え 行動例は本資料で作成'),
        [('「計画する」のは 偶然そのものではない','新しい人・現場・課題に触れる行動を増やし 予定外の出来事から学ぶ<br>楽観性は成功の保証ではなく 冒険心も無謀な挑戦を勧める意味ではない')],
        after=srcs([('原論文：Planned Happenstance（1999）',CHANCE_ORIGINAL),
                    ('5スキルの説明：Frontiers in Psychology（2022）',CHANCE_RESEARCH)]))
    html += chapter(CHANCE_PREFIX+'action','sec-navy','12B / 偶然と 自分の軸をつなぐ',
        '大切にしたい軸は持ち<br>行き先は 固定しすぎない',
        '「初心者を支えたい」という思いがあっても 実現する職種は一つとは限らない<br>やってみて出会った課題から 自分が担いたい仕事を見つけ直していく',
        figure('CHANCE GUIDE 02','予定していなかった役割に出会う 架空例',
            route([('行動','勉強会を手伝う','初心者の質問に<br>触れる機会をつくる'),
                   ('偶然','別の困りごとを知る','教材より 相談の<br>窓口が足りなかった'),
                   ('試行','窓口づくりを試す','AIから人への<br>引き継ぎを考える'),
                   ('選択','次に学ぶことを決める','教材制作に加え<br>相談の設計を学ぶ')])
            + '<p class="cc-reflection">自分のWhyを仮の軸にする → 現場へ出る → 偶然から学ぶ → 軸と進路を更新する</p>',
            '理論をキャリアへ応用した本資料の例　出会いや成果を保証するものではない'),
        [('来週は 一つだけ接点を増やす','普段話さない人に話を聞く 勉強会を一度手伝う 小さな企画を見せる<br>一つ選んで予定に入れ 終わったら「予想外だったこと」と「次に試すこと」を残す'),
         ('AIとの壁打ちを 現場での一歩につなげる','AIに質問案やたたき台を作ってもらい 実際の相手に見せて反応を聞く<br>自分が何に惹かれ 何を変えたくなったかを 振り返りの材料にする')])
    return html


def insert_group(source, prefix, eyebrow, built):
    owned = [n for n in sections(source) if n.attrs.get('data-practical-guide','').startswith(prefix)]
    nodes = sections(source)
    if owned:
        positions = [nodes.index(n) for n in owned]
        assert positions == list(range(positions[0],positions[-1]+1)), 'Reasoning chapters are not adjacent'
        source = source[:owned[0].start] + source[owned[-1].end:]
    anchor = [n for n in sections(source) if f'>{eyebrow}<' in n.outer(source)]
    assert len(anchor) == 1, 'Cannot locate original chapter: '+eyebrow
    pos = anchor[0].start
    # Normalize only whitespace owned by this insertion, for idempotent generation.
    return source[:pos].rstrip() + '\n' + built.rstrip() + '\n' + source[pos:]


def insert(page):
    """Own only the six added sections. Original chapters stay byte-identical."""
    source = apply_body.strip(page)
    source = insert_group(source,PREFIX,'Section 12',build())
    source = insert_group(source,CHANCE_PREFIX,'Section 13',build_happenstance())
    return apply_styles(source)
