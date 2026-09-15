#!/usr/bin/env python3
"""キャリア資料の雇用統計を 初見でも読める常時表示の解説へ改訂する

現行HTMLを入力として 旧Section 01〜07と表紙リード・説明メタデータを更新
後半7章・既存スクリプト・関連リンク・Wを保持する
旧フラグメント生成版はGit履歴にある 現行デザインへ再適用しない

python3 gen_career_omote.py --preview-dir /absolute/private-preview
確認後に --update を追加 --input-dir は現行の非公開復号HTMLの控え
数値・対象・比較期間・改訂理由は docs/verification/2026-09-15-career-clarity.md
"""
from pathlib import Path
import re
from practical_guides import (chapter, figure, route, rows, sheet, exchange,
    replace_chapters, cover_lead, srcs, run)

NY = 'https://www.newyorkfed.org/research/college-labor-market'
BLS = 'https://www.bls.gov/news.release/archives/empsit_08072026.htm'
DEFS = 'https://www.bls.gov/cps/definitions.htm'
REMOTE = 'https://libertystreeteconomics.newyorkfed.org/2026/06/remote-work-leaves-younger-workers-sidelined/'
HAI = 'https://hai.stanford.edu/assets/files/ai_index_report_2026_chapter_4_economy.pdf#page=51'
PWC = 'https://www.pwc.com/gx/en/1/services/ai/ai-jobs-barometer.html'
PWC_NEWS = 'https://www.pwc.com/gx/en/news-room/press-releases/2026/pwc-2026-ai-jobs-barometer.html'
IBM = 'https://www.ibm.com/think/news/entry-level-roles-get-reset-ai'
OOH = 'https://www.bls.gov/ooh/computer-and-information-technology/software-developers.htm'
KYODO = 'https://www.oanda.jp/lab-education/market_news/kn_2026041901000813/'
COVER_COPY = ('消えたのは仕事ではなく梯子の一段目です<br>'
    'この「梯子」は 新人が実務を通して経験を積む道筋のたとえです<br>'
    '雇用統計の読み方から始め AI時代に育てたい力を考えます')
DESCRIPTION = '雇用統計を100人の例で読み解き AI時代のキャリアを考える 失業率と不完全雇用率の違い 若手の雇用・求人の変化 日本企業の採用計画から 経験を積む入口を見直す'
STYLE_RE = re.compile(r'<style id="oz-career-clarity-style">[\s\S]*?</style>\n')


def metadata(page):
    return re.sub(r'<meta (name="description"|property="og:description") content="[^"]*">',
        lambda m: f'<meta {m[1]} content="{DESCRIPTION}">', page)


def metric(value, unit, title, population, reading):
    return (f'<div class="cc-metric"><p class="cc-value">{value}<span>{unit}</span></p>'
            f'<h3>{title}</h3><p class="cc-population">{population}</p><p>{reading}</p></div>')


def metrics(*items):
    return '<div class="cc-metrics">'+''.join(items)+'</div>'


def build():
    groups = []
    figure_titles = {'01A':'実務を通して経験を積む3段階', '01B':'架空の大卒者100人で 分母を比べる',
        '01C':'若年大卒者の2つの指標', '02A':'22〜25歳のソフトウェア開発者の雇用',
        '02B':'求人の要件と件数は 別の比較', '03A':'失業率の上昇分に対する説明割合',
        '03B':'AI時代に学ぶ機会を残す設計例', '04':'作業と判断の役割分担',
        '05':'入口・給与・長期見通しを分けて読む', '06':'3つの身近な仕事で考える',
        '07':'2027年度入社の新卒採用計画'}
    def part(key, label, title, sub, diagram, caption, notes=(), sources=()):
        # Tones alternate within the added introduction; original later tones remain.
        tone = 'sec-navy' if label in ('01B','02A','03A','04','06') else 'sec-light'
        return chapter(key,tone,label+' / 雇用とキャリア',title,sub,
            figure('DATA GUIDE '+label, figure_titles[label],diagram,caption),notes,
            after=srcs(sources) if sources else '')

    intro = part('career01--ladder','01A',
        '「梯子の一段目」は<br>新人が経験を積む仕事のこと',
        'たとえば 資料の下書きを作り 先輩の修正から判断の基準を学ぶ<br>AIが下書きを作るようになったら その学びをどこで得るかが課題になる',
        route([('01','まず作ってみる','調べる・集計する<br>下書きを作る'),
               ('02','直してもらう','先輩と見直し<br>修正の理由を知る'),
               ('03','自分で判断する','目的に合う案を選び<br>結果に責任を持つ')]),
        'キャリアの育ち方を表した概念図　統計の出典確認：2026年9月15日　すべての仕事や新人の席が消えたという意味ではない',
        [('この資料で確かめること','①若手の就職はどう変わったか → ②原因をどう読むか → ③どんな力と経験を積むか<br>前半の統計と 後半の筆者のキャリア観をつないで考える')])

    people = ('<div class="cc-population-bar" aria-label="架空の大卒者100人 働く60人 求職中4人 働かず求職もしない36人">'
        '<span style="flex:60" class="cc-employed"></span><span style="flex:4" class="cc-seeking"></span>'
        '<span style="flex:36" class="cc-inactive"></span></div>'
        '<div class="cc-people"><div><b>60人</b><strong>働いている</strong><p>うち20人は 大卒資格を<br>通常必要としない職に就く</p></div>'
        '<div><b>4人</b><strong>仕事を探している</strong><p>仕事がなく 就業可能で<br>実際に求職している</p></div>'
        '<div><b>36人</b><strong>求職していない</strong><p>働いておらず<br>進学・育児などで求職もしていない</p></div></div>'
        '<div class="cc-equations"><p><strong>失業率</strong><span>4 ÷（60＋4）＝ <b>6.25％</b></span></p>'
        '<p><strong>就業者比率</strong><span>60 ÷ 100 ＝ <b>60％</b></span></p>'
        '<p><strong>不完全雇用率</strong><span>20 ÷ 60 ≒ <b>33.3％</b></span></p></div>')
    intro += part('career01--denominators','01B',
        '同じ100人でも<br>分母が変わると 数字は変わる',
        '以下は計算を理解するための架空の大卒者100人の例<br>失業率は「働く人＋失業者」 不完全雇用率は「働く人」を分母にする',
        people,
        '実際の米国の比率ではない　不完全雇用はNY連銀の「通常は大卒資格を必要としない職」の定義を使用',
        [('失業者には数え方がある','米国では原則として 仕事がない・就業可能・直近4週間に積極的に求職した人<br>一時解雇で復職待ちの人には求職要件の例外がある'),
         ('働き始めた人の状況も見る','就職が決まっても どんな仕事に就いたかは別の問い<br>ここでの「不完全雇用」は 短時間勤務や低賃金を直接測る指標ではない')],
        [('BLS：雇用・失業の定義',DEFS),('NY連銀：不完全雇用の定義',NY)])

    intro += part('career01--rates','01C',
        '若年大卒者は<br>就職の有無と 就職先を分けて見る',
        '米国の「recent college graduates」は 22〜27歳の大卒以上の人を年齢で区切った層<br>今年卒業した人だけの調査でも 日本の新卒内定率でもない',
        metrics(
            metric('5.6','％','仕事がなく 求職している割合','若年大卒者の失業率<br>2026年4〜6月期 約5.6％','働く人＋失業者を100人とすると<br>約6人が失業中'),
            metric('42','％','就職先が大卒資格を通常必要としない割合','働く若年大卒者の不完全雇用率<br>2026年4〜6月期 42％','働く人だけを100人とすると<br>42人が該当する')),
        '出典：NY連銀 2026年第2四半期の公表値　2つは分母が異なるので足さない　42％が失業中という意味でもない',
        [('全体の平均だけでは 若手の状況は分からない','米国全体の失業率は4.1％（16歳以上 2026年7月 季節調整済み）<br>若年大卒者とは年齢・学歴・期間が異なるため この差だけで「大卒の価値が消えた」とは判断できない'),
         ('数字を見たら 対象と時点も見る','ここでは公表時点の数字を使って読み方を説明する<br>5.6％と42％は四半期 4.1％は月次の値であり 同じ月の比較ではない')],
        [('NY連銀：2026年4〜6月期',NY),('BLS：2026年7月分 8月7日公表',BLS)])
    groups.append(('Section 01',intro))

    jobs = part('career02--headcount','02A',
        '若手の雇用が減ることと<br>失業率が上がることは 別の数字',
        'AI Index 2026では 米国の22〜25歳のソフトウェア開発者について<br>2025年9月の雇用が 2022年のピークから約20％減ったと報告している',
        '<div class="cc-index-chart"><p class="cc-axis">雇用人数の変化を指数に置き換えた説明図</p>'
        '<div><strong>2022年のピーク</strong><span><i style="width:100%"></i></span><b>100</b></div>'
        '<div><strong>2025年9月</strong><span><i style="width:80%"></i></span><b>約80</b></div></div>',
        '出典：Stanford HAI AI Index 2026 本文p.221・図4.4.29　元データ：Brynjolfssonほか（2025）　指数100は実人数100人ではない',
        [('分かったこと','調査データ上で この年齢層・職種の雇用人数が減った<br>若手の入口を点検する理由になる'),
         ('この図だけでは分からないこと','20％の人がAIに解雇されたという意味ではない<br>採用減・退職・年齢層の入れ替わりなどを含む人数の変化であり 原因は別に調べる')],
        [('Stanford：原報告書 p.221–222',HAI)])
    jobs += part('career02--requirements','02B',
        '「7倍」は 新人向け求人が<br>経験者向けの力を求める傾向の差',
        'PwCは米国の初級職向け求人240万件を分析<br>AIの影響を受けやすい仕事と 受けにくい仕事で 求人票に書かれる要件を比較した',
        metrics(metric('7','倍','経験者向けの力を求める傾向','AIの影響が最も大きい初級職<br>／最も小さい初級職','リーダーシップや戦略的思考など<br>仕事の難しさや必要経験年数が7倍という意味ではない'),
                metric('＋35','％','経験者向けの力を求める初級職の求人','2019年からの変化<br>PwC 2026年報告','それ以外の初級職求人は−10％<br>同じ「新人向け」でも動きが分かれる')),
        '出典：PwC 2026年6月15日公表　7倍はグループ間の比較　＋35％・−10％は2019年との時点比較',
        [('求人票の どこを見るか','「未経験可」だけでなく 何を判断し 誰と調整する仕事かを見る<br>AIから受ける影響の大きさは仕事の性質の指標であり その会社のAI導入済み割合ではない')],
        [('PwC：2026 AI Jobs Barometer',PWC),('PwC：調査対象と初級職の分析',PWC_NEWS)])
    groups.append(('Section 02',jobs))

    causes = part('career03--remote','03A',
        '「64％」は 失業した人の割合ではなく<br>失業率の上昇を説明する推計',
        'NY連銀の研究者は 在宅でできる職と できない職で 若手と経験者の差を分析<br>リモートワークの広がりが 若手を育てる機会に影響した可能性を示した',
        '<div class="cc-share"><div><span class="pg-label">失業率の「上昇分」を100としたとき</span>'
        '<div class="cc-share-bar" aria-hidden="true"><i style="width:64%"></i></div>'
        '<p><b>約64％</b>を リモートワークの広がりで説明できると推計</p></div>'
        '<p class="cc-share-note">失業者100人のうち64人が<br>在宅勤務のせいで失業した という意味ではない</p></div>',
        '出典：NY連銀 2026年6月1日　18〜28歳の大卒者　2017〜19年と2022〜24年の比較に基づく概算　5.6％の指標とは対象・期間が異なる',
        [('この研究の読み方','AIの影響だけでは 若手の状況を説明しきれない<br>残りの36％がすべてAIの影響だと計算することもできない'),
         ('キャリアへのヒント','出社か在宅かだけでなく 誰から どの頻度で具体的な助言をもらえるかを確認する<br>仕事の進め方を学べる仕組みを選ぶ')],
        [('NY連銀：Remote Work Leaves Younger Workers Sidelined',REMOTE)])
    causes += part('career03--training','03B',
        '新人の仕事と 学ぶ機会は<br>企業の設計で変えられる',
        'IBMは2026年の米国の初級職採用を3倍にする計画を公表<br>AI時代に合わせて仕事内容を組み替え 将来の経験者を育てる入口を確保しようとしている',
        route([('作業','AIが下準備を助ける','調査や下書きの<br>時間を短くする'),
               ('学習','人が判断を説明する','何を直したかだけでなく<br>なぜ直したかを振り返る'),
               ('成長','任せる範囲を広げる','小さな仕事を一つ持ち<br>結果まで確かめる')]),
        '図は本資料の育成設計例　IBMの採用3倍は計画であり 達成済み人数ではない　同社の公表：2026年3月2日',
        [('本人と会社の両方にできることがある','本人は添削や振り返りを求める 会社は教える担当者と時間を用意する<br>「若手は自分で何とかするしかない」で終わらせない')],
        [('IBM：初級職の採用計画と仕事の再設計',IBM)])
    groups.append(('Section 03',causes))

    groups.append(('Section 04',part('career04--experience','04',
        '職位が上がっても<br>仕事の中身は見直し続ける',
        'ここからは統計を踏まえた筆者の考え方<br>新人・中堅・ベテランという肩書きより 自分が何を判断し どの責任を担うかを見る',
        rows(['仕事の場面','AIに助けてもらう例','人が確かめること'],[
            ('下書きを作る','資料やコードの一次案を作る','必要な条件と根拠を満たすか'),
            ('案を比べる','選択肢や論点を整理する','顧客や現場に合う選択はどれか'),
            ('方針を決める','影響やリスクを洗い出す','何を優先し 誰が結果を引き受けるか')]),
        '役割分担の例　特定の職位が何年後に消えるという予測ではない',
        [('経験の積み方を変える','AIの出力を直すだけでなく なぜその案を採ったかを説明する<br>仕事の目的と判断理由を言葉にする練習が 後半のWhyの話につながる')])) )

    groups.append(('Section 05',part('career05--reading','05',
        '就職の難しさと 給与の高さは<br>別々に確かめる',
        '「就職できるか」「就職後にいくら得られるか」「今後どれだけ仕事が増えるか」<br>この3つは異なる問い 一つの数字で専攻や職種の将来を決めない',
        rows(['知りたいこと','見る数字の例','読み取るときの注意'],[
            ('入口に入りやすいか','若年層の失業率<br>未経験者向けの求人と要件','同じ国・年齢・調査年で比較する'),
            ('働いた人の給与はどうか','米国ソフトウェア開発者<br>年収中央値 135,980ドル','2025年5月 全年齢の就業者<br>新卒の初任給でも全卒業生の所得でもない'),
            ('長期の仕事量はどうか','開発者・品質保証担当・テスター<br>2025〜35年の雇用見通し ＋10％','3職種合計の予測<br>来年の新卒採用数を保証しない')]),
        '出典：BLS Occupational Outlook Handbook　中央値は金額順に並べた中央の値　失業率は学歴の価値や働く人の能力を直接測る指標ではない',
        [('高い失業率の理由を 決めつけない','就職先が少ないのか 条件が合わないのか ほかの要因なのかは追加の調査が必要<br>低い失業率だけで「条件を妥協した」と推測することもできない')],
        [('BLS：職種別の賃金と2025〜35年の見通し',OOH)])))

    groups.append(('Section 06',part('career06--tasks','06',
        '自分の職種でも<br>経験を積む入口がどこにあるかを見る',
        'AIエージェントは 決めた範囲で複数の作業を進めるAI<br>職種名を丸ごと比べるより 普段の作業と そこから学ぶことを分けて考える',
        rows(['身近な仕事','AIが助ける作業の例','人が経験として積みたいこと'],[
            ('営業資料を作る','顧客情報の整理と下書き','相手の困りごとを聞き 提案の理由を説明する'),
            ('問い合わせに答える','FAQを探し 回答案を作る','根拠を確認し 例外や難しい相談を判断する'),
            ('月次報告を作る','数字の集計と異常値の抽出','数字が動いた理由を調べ 次の行動を決める')]),
        '職種を越えて考えるための例　各職種の雇用減少を示す実測データではない',
        [('まず 一つの作業で試す','AIで短くできる作業を一つ選ぶ<br>空いた時間で 誰に何を教わり どんな判断を練習するかまで決める')])) )

    company_rows=[('減らす','25社','23％'),('増やす','18社','16％'),('前年度並み','39社','35％'),('未定','24社','22％'),('無回答','5社','5％')]
    japan = part('career07--japan','07',
        '日本の「23％」は<br>採用を減らすと答えた企業の割合',
        '共同通信が主要企業111社に 2027年度入社の新卒採用計画を聞いた調査<br>採用人数が全国で23％減る という意味ではない',
        rows(['前年度実績に比べた計画','回答企業数','111社に占める割合'],company_rows),
        '2026年3月中旬〜4月上旬に回答　2027年度入社＝2027年4月〜2028年3月　割合は公表時の丸め値のため合計101％',
        [('理由の分母は さらに小さい','採用を減らす25社のうち 4社がデジタル対応による省人化を理由に挙げた（16％）<br>主要企業111社すべての16％でも 日本企業全体の16％でもない'),
         ('日本で確かめたいこと','計画の回答であり 実際に採用した人数ではない<br>日本全体へ一般化せず 志望先・自社の採用要件と 若手を育てる仕事の変化を確認する')],
        [('共同通信：111社調査 2026年4月20日配信',KYODO)])
    groups.append(('Section 07',japan))
    return groups


def transform(page):
    page = STYLE_RE.sub('',page)
    page = replace_chapters(page,build())
    page = metadata(cover_lead(page,COVER_COPY))
    css = Path(__file__).with_name('career_clarity.css').read_text()
    return page.replace('</head>',f'<style id="oz-career-clarity-style">\n{css}\n</style>\n</head>',1)

transform.cover_copy = COVER_COPY
transform.public_metadata = metadata

if __name__ == '__main__':
    run({'06_people/career-in-agent-era.html':transform},'キャリア資料の雇用統計を分かりやすく改訂')
