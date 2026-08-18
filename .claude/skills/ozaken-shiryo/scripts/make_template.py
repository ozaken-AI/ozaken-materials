#!/usr/bin/env python3
"""テンプレート便覧のページを組む。トップページから te で開く。

**資料が92本あるのに、型がどこにも一覧されていなかった。**
図版が何種類あるのか、面の並びにどんな決まりがあるのか、
どの資料がどの生成元から組まれているのか。
知っているのは書いた本人だけで、しばらく経つと本人も忘れる。
だから同じ形を作り直したり、規約から外れた資料が混ざったりしていた。

このページは、その台帳。**見本は実物のCSSと実物の部品で描く。**
説明文だけの一覧にすると、部品を直したときにここだけ古くなる。

  OZAKEN_PW=マスター python3 make_template.py

道具のページなので、資料の規約（奇数セクション等）は当てはめない。
パスワード台帳・資料マトリクスと同じ扱いで、**マスターだけで開く**。
"""
import html as H
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import oz_root
ROOT = oz_root.root(HERE)

import lockbox
import build_page
import page_parts
import domain_fig as D

PW = os.environ.get('OZAKEN_PW') or sys.exit('OZAKEN_PW を設定してください')
OUT = os.path.join(ROOT, 'template.html')
SRC = os.path.join(HERE, '..', 'sources')

STYLE = open(os.path.join(HERE, 'tpl_style.html'), encoding='utf-8').read()


def esc(s):
    return H.escape(str(s))


# ==================================================================
# 01  デザイントークン
# ==================================================================
TOKENS = [
    ('地', [('--paper', '#f8f7f4', '明るい面の地'),
            ('--navy', '#1f3864', '濃い面の地'),
            ('--navy-deep', '#141d35', 'いちばん濃いところ'),
            ('#ffffff', '#ffffff', '箱の地')]),
    ('文字', [('--ink', '#1a1a2e', '本文'),
              ('--muted', '#6b7a99', '補足'),
              ('--azure-pale', '#d8e4f0', '濃い面の上の文字')]),
    ('意味を持つ色', [('--azure', '#2e5496', '基準・肯定・数字'),
                      ('--red', '#e23744', '警告・否定・強調'),
                      ('--red-bright', '#ff5d6a', '濃い面の上の警告'),
                      ('AMBER', '#c9762f', '注意・中間'),
                      ('TEAL', '#2f8f8a', '良い・達成')]),
]

FONTS = [('--font-ja-serif', '游明朝 / Shippori Mincho B1', '見出し・リード文'),
         ('--font-ja-sans', '游ゴシック / Noto Sans JP', '本文・図版の中'),
         ('--font-en', 'Barlow / Jost', '英字・数字・ラベル')]


def sec_tokens():
    sw = []
    for group, items in TOKENS:
        cells = ''.join(
            '<div class="tk"><span class="tk-chip" style="background:%s"></span>'
            '<b>%s</b><code>%s</code><span>%s</span></div>' % (hexv, esc(name), esc(hexv), esc(note))
            for name, hexv, note in items)
        sw.append('<h3 class="tp-h3">%s</h3><div class="tk-row">%s</div>' % (esc(group), cells))
    fonts = ''.join(
        '<div class="tk"><b>%s</b><code>%s</code><span>%s</span></div>'
        % (esc(v), esc(n), esc(u)) for n, v, u in FONTS)
    return ('<h3 class="tp-h3">書体は3つだけ</h3><div class="tk-row">%s</div>' % fonts
            + ''.join(sw)
            + '<p class="note">この表にない色と書体は、機械検査（build_page.check_tokens）で'
              '弾かれる。<b>足したいときは PALETTE に登録してから使う。</b>'
              '登録せずに使うと公開が止まる。</p>')


# ==================================================================
# 02  面の型と、並びの決まり
# ==================================================================
ORDER = [('hero', '表紙', '題・ひとこと・リード文。ここだけ別の型'),
         ('sec-light', '明るい面', '本文。奇数番目'),
         ('sec-navy', '濃い面', '本文。偶数番目'),
         ('sec-light', '明るい面', '…以下、交互に'),
         ('sec-navy', '締め', 'close()。必ず濃い面で終える'),
         ('sec-download', '配布資料', '締めのあと。明暗の数には入らない')]


def sec_layout():
    band = ''.join(
        '<div class="ly %s"><b>%s</b><span>%s</span><code>%s</code></div>'
        % ('ly-navy' if k in ('sec-navy',) else ('ly-dl' if k == 'sec-download' else 'ly-light'),
           esc(ja), esc(note), esc(k))
        for k, ja, note in ORDER)
    return (('<div class="ly-row">%s</div>' % band)
            + '<p class="note"><b>本文の面は奇数本。</b>明るい面から始めて交互に置き、'
              '締めは必ず濃い面。だから<b>節を足すときは2本ずつ</b>足す。'
              '1本だけ足すと、そのうしろの明暗が全部ひっくり返る。'
              '確認テストと配布資料の節は、この数には入らない。</p>')


# ==================================================================
# 03  図版カタログ
# ==================================================================
def catalogue():
    """29種類を、実物で描く。**説明だけの一覧にはしない。**"""
    figs = []

    def add(kind, why, html):
        figs.append('<div class="cat"><div class="cat-h"><code>%s</code><span>%s</span></div>%s</div>'
                    % (esc(kind), esc(why), html))

    add('fig_gap', 'いま → これから。左右の対比', D.fig_gap(
        [('探す・集める時間', '決める・確かめる時間'),
         ('一次案を、人が書く', '一次案を、人が却下する')],
        'Fig. ── 総量は減らず、中身が入れ替わる', '左が消えるぶん、右が中心になる',
        uid='tgap', left_label='いまの1週間', right_label='2〜3年後の1週間'))

    add('fig_versus', '2つを、観点ごとに並べて比べる', D.fig_versus(
        ('使うAI', 'レベル1〜3。主語は人'), ('任せるAI', 'レベル4〜5。主語はAI'),
        [('渡すもの', '手順を渡す', '目的を渡す'),
         ('確認するもの', '出てきた成果物', '決めておいた基準')],
        'Fig. ── またいだ瞬間に、同時に入れ替わる', '観点は4つまでが読みやすい'))

    add('fig_check', '守ること・避けること。○×で示す', D.fig_check(
        [(True, '範囲を、具体的な名前で言えるか', '言えないうちは、渡した先が決まっていない'),
         (False, '1つでも欠けていれば、それは丸投げ', 'AIは困っても聞き返さず、最後まで進む')],
        'Fig. ── 3つ揃って、はじめて成り立つ', '○と×を混ぜると、順番と落とし穴が同時に出せる'))

    add('fig_cols', '3つを、並べて説明する', D.fig_cols(
        [('RULE', '制度', '労働時間と、要員計画', '勤務時間と要員の考え方が変わる', 0),
         ('EVAL', '評価', '手を動かした量では測れない', '何を止め、何を通したかで測る', 1),
         ('GROW', '育成', '覚える場を、作り直す', '見て覚える場を、誰も引き受けていない', 3)],
        'Fig. ── 3つを、同じ重さで並べる', '4つ以上になると、1枚が狭くなって読めない'))

    add('fig_context', '層。下ほど土台、上ほど成果に近い', D.fig_context(
        [('仕事', '何のためにいるか。職種の目的'),
         ('業務', '繰り返す、始まりと終わりのある活動'),
         ('作業', '動詞で書ける、最小の単位。渡せるのはここ')],
        'Fig. ── 3層に分ける', '「どの粒度の話をしているか」を揃えるときに効く'))

    add('fig_ladder', '段。順番があるものを、上下に積む', D.fig_ladder(
        [('壁1・目的の壁', '「使うこと」が目的にすり替わる'),
         ('壁2・業務の壁', '任せられる単位に、ほどけていない'),
         ('壁3・データの壁', '渡せるものが、手元に無い')],
        'Fig. ── 越える順番が決まっている', '6個以上を横に並べたいときも、これを使う', asc=False))

    add('fig_flow', '横一列の流れ。**5個まで**', D.fig_flow(
        [('① 選ぶ', '記録がある業務を1つ'), ('② ほどく', '動詞で書ける作業まで'),
         ('③ 書く', '範囲・基準・戻し方')],
        'Fig. ── 手順を、矢印でつなぐ', '6個以上は文字が右へはみ出す。fig_ladder に替える',
        uid='tflow'))

    add('fig_issues', '4つが1本の輪になっていることを示す', D.fig_issues(
        [('矛盾', '推進と統制を、同じ部門が担っている'),
         ('実態', '把握できていない利用が増えている'),
         ('負荷', '問い合わせが本来の業務を圧迫する'),
         ('期待', '要員も予算も増えないまま期待が上がる')],
        'Fig. ── 別々の問題ではなく、1本の輪', '因果が巡っているときに使う', uid='tiss'))

    add('fig_sheet', '表。**tableタグは使えないのでこれ**', D.fig_sheet(
        ['立場', 'やること', '見るもの'],
        [['決める人', '投資する工程を絞る', '工程の数字が動いたか'],
         ['組む人', '渡せる形に直す', '他部門が真似できるか']],
        [0.24, 0.46, 0.30], 'Fig. ── 役割ごとに、持ち場を分ける',
        '資料の中で <table> は禁止。表が要るときは必ずこれ', badge='3者'))

    add('fig_matrix', '格子。当てはまる・当てはまらないを一覧', D.fig_matrix(
        ['レベル1', 'レベル2', 'レベル3'],
        [('社内文書', ['○', '○', '△']), ('個人情報', ['×', '△', '×'])],
        'Fig. ── どこまで許すかの一覧', '○△×か、短い文字列だけを入れる'))

    add('fig_quad', '2軸4象限。どこから手を付けるか', D.fig_quad(
        '判断の記録', '判断の回数',
        [('まず、記録から', '判断は多いのに理由が残っていない', 1),
         ('ここから始めます', '判断が多く、記録もある', 0),
         ('当面は置いておく', '判断も記録も少ない', 2),
         ('効きますが、後で', '記録はあるが回数が少ない', 1)],
        'Fig. ── 2つの軸で、置き場所を決める',
        '**xpoles / ypoles を必ず渡す。**軸名だけだと左右どちらが是か読めない',
        xpoles=('残っていない', '残っている'), ypoles=('少ない', '多い')))

    add('fig_map', '2軸の散布。位置関係を見せる', D.fig_map(
        '機密性', '難しさ',
        [('社内文書の検索', 24, 30, 0, '低リスク'), ('顧客対応', 70, 62, 2, '要確認')],
        'Fig. ── どこに置くかを、点で示す', '象限で語るときは fig_quad、点の散らばりを見るときはこれ'))

    add('fig_dims', '点・線・面・立体。成熟度の5段', D.fig_dims(
        [('レベル1', 'dot', '単発プロンプト', '対話型AIの利用', '人が毎回、聞き方を工夫する', 0),
         ('レベル2', 'line', '特化型ボット', '社内FAQ', '前提を先に書いて保存する', 0),
         ('レベル3', 'chain', 'ワークフロー', '定型業務の自動処理', '決まった順に進む', 1),
         ('レベル4', 'plane', '自律エージェント', '目的を渡す', 'AIが手順を決める', 2),
         ('レベル5', 'cube', '完全自律', 'エージェント協働', '複数が連携して動く', 3)],
        'Fig. ── 実装の5レベル', '形は dot / line / chain / plane / cube', uid='tdim'))

    add('fig_stairs', '階段。製品を段に置く', D.fig_stairs(
        [('L1', '点', '単発', 'ChatGPT', '都度の指示', 0),
         ('L2', '線', 'ボット', 'Copilot Studio', '前提を渡す', 1),
         ('L3', '面', 'フロー', 'Power Automate', '手順を組む', 2)],
        'Fig. ── 段ごとに、製品を置く', '製品名まで出すときはこちら'))

    add('fig_pyramid', '希少さ。上ほど少ない', D.fig_pyramid(
        [('ストラテジスト', 'どこに置くと事業が変わるかを決める', 2),
         ('アーキテクト', '任せられる状態をつくる', 1),
         ('オペレーター', '動いているものを見て判断する', 0)],
        'Fig. ── 上ほど席が少ない', '人数の話をするときに使う',
        left_label='少ない', right_label='多い'))

    add('fig_roles', '3つの役。持ち場を書き分ける', D.fig_roles(
        ['どこに置くと事業が変わるかを見極め、投資を配る',
         '任せられる状態をつくる。データと権限を整える',
         '動いているものを見て、良し悪しを判断する'],
        'Fig. ── 肩書きではなく「いまの立場」',
        '同じ人が、業務によって別の役になる'))

    add('fig_loop4', '4工程の環。一周して戻る', D.fig_loop4(
        [('共同化', 'Socialization', '一緒にやって、見て覚える', ['現場に同席する']),
         ('表出化', 'Externalization', '言葉にして形式知へ', ['判断の根拠を書く']),
         ('連結化', 'Combination', '組み合わせて体系にする', ['標準書に束ねる']),
         ('内面化', 'Internalization', '実践して、また身体に落とす', ['型を使って動く'])],
        'Fig. ── 一周するたび、知が一段上がる', 'SECIのような4工程の循環に', uid='tloop'))

    add('fig_cycle', '円環。4〜6個の繰り返し', D.fig_cycle(
        [('計画', '対象を決める'), ('実行', '渡してみる'),
         ('確認', '基準で判定する'), ('改善', '線を引き直す')],
        'Fig. ── 回り続けるもの', '始まりと終わりが無いときはこちら',
        center='90日', uid='tcyc'))

    add('fig_tree', '階層。分類・組織を2段で', D.fig_tree(
        'AI推進の施策', [('基盤', ['戦略', '体制']), ('推進', ['育成', '共有']),
                         ('発展', ['事業化'])],
        'Fig. ── 上位と下位を、枝で結ぶ', '枝は4本まで', uid='ttree'))

    add('fig_kpi', '指標の分解。上位から下位へ', D.fig_kpi(
        '工程の数字が動いたか',
        [('突発停止の比率', ['予兆検知の件数']), ('対応までの日数', ['一次判定の時間'])],
        'Fig. ── 何で測るかを、分解する', '成果指標を具体に落とすときに'))

    add('fig_bars', '横棒。大小を比べる', D.fig_bars(
        [('レベル1で止まっている', 62, '62%', '多くの企業がここ', 2),
         ('レベル2まで来た', 26, '26%', '前提を渡し始めた', 1),
         ('レベル3以上', 12, '12%', 'まだ少ない', 0)],
        'Fig. ── 割合を、長さで見せる', '数字は必ず出典とセットで', unit='%'))

    add('fig_stack', '積み上げ棒。内訳を比べる', D.fig_stack(
        [('A社', [40, 35, 25]), ('B社', [70, 20, 10])],
        ['基盤', '推進', '発展'], 'Fig. ── 内訳の比を、並べて見る',
        '合計が同じものを比べるときに', unit='%'))

    add('fig_donut', '円。全体に対する割合', D.fig_donut(
        [('システム実装', 8, '思ったより少ない'), ('人と組織', 24, 'ここが本体'),
         ('その他', 19, '')],
        'Fig. ── 全体のうち、どれだけか', '3〜5項目まで。多いと読めない', center='51施策'))

    add('fig_stats', '数字を、大きく置く', D.fig_stats(
        [('90', '日', '1本を通しきる期間', '検証を延ばさないための区切り', 0),
         ('3', 'つ', '任せるための問い', '範囲・基準・戻し方', 1)],
        'Fig. ── 覚えて帰ってもらう数字', '丸数字と単位が重なるので、単位は短く'))

    add('fig_timeline', '時系列。出来事を並べる', D.fig_timeline(
        [('05.13', 'OpenAI', 'Codex を一般提供', '手順ではなく目的を渡す形へ', 0),
         ('05.20', 'Google', 'Gemini の新版', 'ドメイン特化が進む', 1)],
        'Fig. ── いつ、何が起きたか', '日付は資料の中で揃える', axis='2026年5月'))

    add('fig_ranges', '工程表。期間の帯で示す', D.fig_ranges(
        ['Day 1-30', 'Day 31-60', 'Day 61-90'],
        [('対象を決める', 0, 0, 0, '記録がある業務から'),
         ('記録を、止めない', 0, 2, 2, '判断とその理由を毎回残す')],
        'Fig. ── 何を、いつやるか', '帯の中の補足は1行に収まる長さで'))

    add('fig_orgs', '組織の比較。規模と中身', D.fig_orgs(
        [('CoE', 4, '3〜5名', ['設計する場', '可否を決める場'], '全社横断', 0),
         ('運営委員会', 8, '8名前後', ['方針を決める'], '経営直下', 1)],
        'Fig. ── 置き方ごとに、何が違うか', '人数の目安まで出すときに', unit='名'))

    add('fig_waterline', '水位。下から満ちてくるもの', D.fig_waterline(
        [('WHY', '目的を決める', 'なぜやるかは人が決める', '当面は人', '代わりが効かない'),
         ('WHAT', '何をやるか決める', '選択肢を並べて選ぶ', '半分は移った', '判断は残る'),
         ('HOW', 'どうやるか決める', '手順を組んで動かす', 'ほぼ移った', 'AIのほうが速い')],
        'Fig. ── AIの水位は、下から上がってくる',
        '「いつまで残るか」を語るときに', water_at=1))

    return ''.join(figs)


# ==================================================================
# 04  部品
# ==================================================================
def parts():
    quiz = ('<div class="quiz-demo"><span class="qd-tag">確認テスト</span>'
            '<p><b>画面を3回たたく／<code>test</code> と打つ／<code>#test</code> で開く。</b>'
            '5〜7問。難易度は「知っているか」ではなく「見分けられるか」で作る。'
            '本文の最後の <code>&lt;/section&gt;</code> より後ろに '
            '<code>&lt;div class="quiz"&gt;</code> を置く。</p></div>')
    return ('<h3 class="tp-h3">カード（cards）</h3>'
            '<div class="cards">'
            + page_parts.cards([
                ('<span class="mth">見出し</span>3枚が既定。多くて4枚',
                 '1枚を読んだ人にそれだけで通じるように書く。'
                 '<b>指示語で始めない。</b>「この」「その」で始めると、'
                 'その箱だけを読んだ人に通じない。'),
                ('<span class="mth">強調</span><b>タグ</b>は本文の中だけ',
                 '図版のキャプションは <code>esc()</code> を通るので、'
                 '<b>タグを書くと文字のまま出る。</b>SVGの中も同じ。'),
                ('<span class="mth">出典</span>抜粋なら、出どころを書く',
                 '他の資料から持ってきた話は、末尾に'
                 '「出典：資料アーカイブ「◯◯」」を付ける。'),
            ]) + '</div>'
            + '<h3 class="tp-h3">Ozaken\'s One Point（take）</h3>'
            + '<p class="note">1本の資料に<b>2つまで</b>。3つ以上は機械検査で弾かれる。'
              'カードの格子の外（<code>sec(after=...)</code>）に置く。</p>'
            + page_parts.take(
                '現場でいちばんもったいないと感じるのは、'
                '「守る部門だから推進は自分の仕事ではない」と線を引いてしまうことです。'
                '実際には逆で、<span class="hot">安全な道を用意できるのは、'
                'その部門しかいません</span>。')
            + '<h3 class="tp-h3">注記（note）・導入文（lede）・見出しチップ（mth）</h3>'
            + '<p class="lede">導入文。<span class="fw-bold text-azure">節のはじめに置く</span>。'
              '明朝で大きく、そこだけ読んでも節の主張が分かるように書く。</p>'
            + '<p class="note">注記。図版のあとに置く補足。'
              '<b>本文より小さく、色を落とす。</b></p>'
            + '<h3 class="tp-h3">関連資料チップ（xr-chips）</h3>'
            + '<p class="xr-chips"><span class="xr-lb">関連資料</span>'
              '<a href="01_concept/what-is-ai-agent.html">AIエージェントとは何か</a>'
              '<a href="01_concept/use-to-delegate.html">「使うAI」から「任せるAI」へ</a></p>'
            + '<p class="note"><code>crossref.py apply</code> が、話の重なる節の末尾に自動で置く。'
              '行き先は <code>crossref_data.py</code> の概念表で決まる。'
              '顧客名を冠した資料は <code>NO_CHIP_TO</code> に入れて、行き先にしない。</p>'
            + '<h3 class="tp-h3">確認テスト（quiz）</h3>' + quiz
            + '<h3 class="tp-h3">配布資料（download）</h3>'
            + '<p class="note">締めのあとに <code>page_parts.download(depth=N)</code>。'
              'トップページと同じリード獲得ゲートが付く。'
              '<b>参加者にページごと共有する資料に置く。</b></p>')


# ==================================================================
# 05  レギュレーション
# ==================================================================
RULES = [
    ('本文の面は奇数本', '明るい面から始めて交互、締めは濃い面。節は2本ずつ足す'),
    ('&lt;table&gt; は使わない', '表が要るときは fig_sheet か fig_matrix'),
    ('CTAボタンを置かない', 'btn-primary / btn-secondary は資料には入れない'),
    ('take は2つまで', '3つ以上は「ここぞ」が消える'),
    ('規定外の色・書体を使わない', 'PALETTE と3書体の変数だけ'),
    ('SVGは妥当なXML', 'marker の id が重複しないよう uid を渡す'),
    ('回転テキストに矢印を入れない', '向きが読めなくなる'),
    ('数量には主語を付ける', '「前年比◯%」だけでは、何の数字か分からない'),
    ('固有名詞は正体とセット', 'カタカナ人名には肩書き、略語には日本語名'),
    ('カードを指示語で始めない', 'その箱だけを読んだ人に通じるか'),
    ('図の参照を数え直す', '節を足したら Fig.N がずれる'),
]


def rules():
    li = ''.join('<div class="rl"><b>%s</b><span>%s</span></div>' % (k, esc(v))
                 for k, v in RULES)
    return ('<div class="rl-row">%s</div>' % li
            + '<p class="note">上の7つは <code>build_page.check</code> が、'
              '下の4つは <code>check_wakaru.py</code> が見る。'
              '<b>前者は公開を止め、後者は警告だけ出して止めない。</b>'
              'うるさいだけの検査は、誰も見なくなるので。<br>'
              'まとめて見るときは <code>OZAKEN_PW=… python3 lint_all.py --wakaru</code>。</p>')


# ==================================================================
# 06  生成元
# ==================================================================
def sources():
    p = os.path.join(SRC, 'README.md')
    if not os.path.exists(p):
        return '<p class="note">生成元の一覧がまだありません。</p>'
    rows = []
    for line in open(p, encoding='utf-8'):
        if line.startswith('- `'):
            name = line.split('`')[1]
            dest = line.split('…', 1)[1].strip() if '…' in line else ''
            rows.append('<div class="sr"><code>%s</code><span>%s</span></div>'
                        % (esc(name), esc(dest)))
    return ('<div class="sr-row">%s</div>' % ''.join(rows)
            + '<p class="note"><b>資料を直すときは、公開済みのHTMLではなく生成元を直す。</b>'
              '置き場所は <code>.claude/skills/ozaken-shiryo/sources/</code>。<br>'
              '<code>python3 gen_xxx.py</code> で本文を書き出し、'
              '<code>publish.py … --update</code> で焼き直す。'
              '<code>--update</code> は鍵を作り直さないので、'
              '配ってあるパスワードはそのまま使える。</p>')


# ==================================================================
# 組む
# ==================================================================
EXTRA = """
<style>
body{background:var(--paper)}
.tp-wrap{max-width:1180px;margin:0 auto;padding:0 1.5rem}
.tp-head{background:linear-gradient(140deg,#24446f 0%,var(--navy) 46%,var(--navy-deep) 100%);
  color:#fff;padding:3.4rem 1.5rem 3rem;margin-bottom:0}
.tp-head .tp-wrap{padding:0 1.5rem}
.tp-tag{display:inline-block;font-family:var(--font-en);font-size:.64rem;font-weight:700;
  letter-spacing:.18em;background:var(--red);padding:.3rem .7rem;border-radius:100px}
.tp-head h1{font-family:var(--font-ja-serif);font-size:clamp(1.7rem,4vw,2.4rem);
  font-weight:600;margin:1rem 0 .6rem;line-height:1.4}
.tp-head p{font-size:.92rem;line-height:1.9;color:rgba(255,255,255,.8);max-width:640px}
.tp-nav{display:flex;flex-wrap:wrap;gap:.5rem;margin-top:1.6rem}
.tp-nav a{font-size:.78rem;color:var(--azure-pale);text-decoration:none;
  border:1px solid rgba(216,228,240,.28);border-radius:100px;padding:.28em .9em}
.tp-nav a:hover{background:#fff;color:var(--navy);border-color:#fff}
.tp-sec{padding:3.2rem 0 1rem}
.tp-sec>.tp-wrap>h2{font-family:var(--font-ja-serif);font-size:1.5rem;font-weight:600;
  margin-bottom:.4rem}
.tp-sec>.tp-wrap>h2 em{font-style:normal;font-family:var(--font-en);font-size:.66rem;
  font-weight:700;letter-spacing:.16em;color:var(--azure);display:block;margin-bottom:.4rem}
.tp-lead{font-size:.9rem;line-height:1.95;color:var(--muted);max-width:720px;margin-bottom:1.6rem}
.tp-h3{font-family:var(--font-ja-serif);font-size:1.06rem;font-weight:600;
  margin:2.2rem 0 .8rem;padding-left:.7rem;border-left:3px solid var(--azure)}
.tk-row{display:grid;grid-template-columns:repeat(auto-fill,minmax(210px,1fr));gap:.7rem}
.tk{background:#fff;border:1px solid var(--azure-pale);border-radius:10px;padding:.85rem .95rem}
.tk-chip{display:block;height:26px;border-radius:5px;margin-bottom:.55rem;
  border:1px solid rgba(46,84,150,.18)}
.tk b{display:block;font-size:.84rem;color:var(--ink)}
.tk code{display:block;font-family:var(--font-en);font-size:.72rem;color:var(--azure);margin:.15rem 0}
.tk span{font-size:.75rem;color:var(--muted);line-height:1.6}
.ly-row{display:flex;flex-wrap:wrap;gap:.6rem}
.ly{flex:1 1 160px;border-radius:10px;padding:.9rem 1rem;border:1px solid var(--azure-pale)}
.ly-light{background:#fff}
.ly-navy{background:var(--navy);border-color:var(--navy)}
.ly-navy b,.ly-navy span{color:#fff}
.ly-navy code{color:var(--azure-pale)}
.ly-dl{background:var(--azure-pale)}
.ly b{display:block;font-size:.9rem;margin-bottom:.2rem}
.ly span{display:block;font-size:.76rem;color:var(--muted);line-height:1.6}
.ly code{font-family:var(--font-en);font-size:.68rem;color:var(--azure)}
.cat{margin-bottom:2.2rem}
.cat-h{display:flex;align-items:baseline;gap:.7rem;margin-bottom:.5rem;flex-wrap:wrap}
.cat-h code{font-family:var(--font-en);font-size:.86rem;font-weight:700;color:var(--azure);
  background:var(--azure-pale);padding:.16em .6em;border-radius:5px}
.cat-h span{font-size:.82rem;color:var(--muted)}
.rl-row{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:.6rem}
.rl{background:#fff;border:1px solid var(--azure-pale);border-radius:9px;padding:.8rem .95rem}
.rl b{display:block;font-size:.86rem;margin-bottom:.2rem}
.rl span{font-size:.76rem;color:var(--muted);line-height:1.65}
.sr-row{display:grid;grid-template-columns:repeat(auto-fill,minmax(330px,1fr));gap:.4rem}
.sr{display:flex;gap:.6rem;align-items:baseline;background:#fff;border-radius:7px;
  padding:.5rem .75rem;border:1px solid var(--azure-pale)}
.sr code{font-family:var(--font-en);font-size:.74rem;color:var(--azure);white-space:nowrap}
.sr span{font-size:.74rem;color:var(--muted);word-break:break-all}
.quiz-demo{background:#fff;border:1px solid var(--azure-pale);border-radius:10px;padding:1.1rem 1.2rem}
.qd-tag{display:inline-block;font-family:var(--font-en);font-size:.62rem;font-weight:700;
  letter-spacing:.14em;color:var(--azure);background:var(--azure-pale);
  padding:.2em .6em;border-radius:4px;margin-bottom:.5rem}
.quiz-demo p{font-size:.84rem;line-height:1.9;color:var(--muted)}
code{font-family:var(--font-en);font-size:.86em}
.tp-foot{background:var(--navy-deep);color:rgba(255,255,255,.55);font-size:.76rem;
  text-align:center;padding:2.4rem 1.5rem;margin-top:3rem}
</style>
"""

SECS = [
    ('tokens', 'Design Tokens', 'デザイントークン',
     'この表にある色と書体だけを使う。増やすときは PALETTE に登録してから。', sec_tokens),
    ('layout', 'Section Order', '面の型と、並びの決まり',
     '明るい面と濃い面を交互に置く。**節を足すときは2本ずつ。**', sec_layout),
    ('figs', 'Figure Catalogue', '図版カタログ ── 28種類',
     '同じ形が続くと、内容の違いが見えなくなる。'
     '形が変わること自体が、聴いている人にとっての区切りになる。', catalogue),
    ('parts', 'Parts', '部品',
     'カード・Ozaken\'s One Point・注記・関連資料チップ・確認テスト・配布資料。', parts),
    ('rules', 'Regulation', 'レギュレーション',
     '機械で見ているもの。守れているかは lint_all.py で一度に確かめられる。', rules),
    ('sources', 'Sources', '生成元 ── どの資料が、どこから組まれるか',
     '資料を直すときは、公開済みのHTMLではなく生成元を直して焼き直す。', sources),
]


def build():
    nav = ''.join('<a href="#%s">%s</a>' % (k, esc(ja)) for k, _, ja, _, _ in SECS)
    body = []
    for key, en, ja, lead, fn in SECS:
        body.append(
            '<section class="tp-sec" id="%s"><div class="tp-wrap">'
            '<h2><em>%s</em>%s</h2><p class="tp-lead">%s</p>%s</div></section>'
            % (key, esc(en), esc(ja), lead.replace('**', ''), fn()))
    return (
        '<!doctype html><html lang="ja"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>テンプレート便覧｜おざけん</title>'
        '<link rel="preconnect" href="https://fonts.googleapis.com">'
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
        '<link href="https://fonts.googleapis.com/css2?'
        'family=Barlow:wght@400;500;600;700&family=Jost:wght@400;500;600;700&'
        'family=Noto+Sans+JP:wght@400;500;700&family=Shippori+Mincho+B1:wght@500;600;700&'
        'display=swap" rel="stylesheet">'
        + STYLE + EXTRA +
        '</head><body>'
        '<header class="tp-head"><div class="tp-wrap">'
        '<span class="tp-tag">OZAKEN TEMPLATE ／ 便覧</span>'
        '<h1>資料の型は、ここにまとめてある</h1>'
        '<p>図版が何種類あるのか、面の並びにどんな決まりがあるのか、'
        'どの資料がどの生成元から組まれているのか。'
        '知っているのが書いた本人だけだと、同じ形を作り直したり、'
        '規約から外れた資料が混ざったりする。'
        '<b>見本は説明文ではなく、実物の部品で描いてある。</b>'
        '部品を直せば、このページの見本も一緒に変わる。</p>'
        '<div class="tp-nav">%s</div></div></header>%s'
        '<footer class="tp-foot">おざけん 資料アーカイブ ／ テンプレート便覧'
        '<br>トップページで <b>te</b> と打つと、ここへ来られる</footer>'
        '</body></html>' % (nav, ''.join(body)))


if __name__ == '__main__':
    page = build()
    if os.path.exists(OUT):
        lockbox.encrypt(OUT, PW, page)          # 鍵は作り直さない
    else:
        # **道具のページに共通鍵は付けない。**マスターだけで開く
        lockbox.create(os.path.join(ROOT, 'backstage.html'), page, OUT, [PW])
    assert lockbox.decrypt(OUT, PW) == page
    print('テンプレート便覧を更新しました（図版 %d 種 / 節 %d 本 / %d 文字）'
          % (page.count('class="figure"'), len(SECS), len(page)))
