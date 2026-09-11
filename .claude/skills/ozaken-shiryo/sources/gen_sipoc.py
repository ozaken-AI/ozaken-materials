#!/usr/bin/env python3
"""業務分解大全のSIPOCを本人指定の記入例・判断基準で具体化する

python3 gen_sipoc.py --preview-dir /absolute/private-preview
確認後は --update を追加 現在の資料へSIPOC・エージェント設計・標準化の11章を追記
講演構成の14〜22を含む 自身の追加章だけを置換し 他の本文と図を保持する
"""
from practical_guides import chapter, figure, route, rows, sheet, srcs, sections, apply_styles, run
import apply_body
from qrgen import svg as qr_svg

PROCESSES = ['データを抽出', '数字を集計', 'メンバーのコメントを集める', '資料にまとめる', 'マネージャーが確認']
NUMBERS = '①②③④⑤'
RATINGS = ['◎', '◎', '○', '◎', '×']
ORIGINAL_INTRO = '実際に使っている2枚です。請求書処理を例に、記入した状態で載せます。埋める順番は、上から下です。'
UPDATED_INTRO = '請求書処理を例に SIPOCと業務分解シートの2枚を記入した状態で載せます<br>SIPOCは「業務名 → P → O・C → S・I」の順で書き そのあと作業の単位まで割ります'


def rating(mark):
    cls = {'◎':'agent','○':'assist','×':'human'}[mark]
    return f'<span class="pg-sipoc-rating pg-sipoc-{cls}">{mark}</span>'


def build():
    process_list = '<ol class="pg-sipoc-processes">'+''.join(
        f'<li><span>{NUMBERS[i]}</span>{name}</li>' for i,name in enumerate(PROCESSES))+'</ol>'
    example = rows(['項目','記入例'],[
        ('<span class="pg-sipoc-letter">S</span>供給者','チームメンバー<br>営業管理システム'),
        ('<span class="pg-sipoc-letter">I</span>インプット','案件データ<br>各メンバーの進捗メモ'),
        ('<span class="pg-sipoc-letter">P</span>プロセス',process_list),
        ('<span class="pg-sipoc-letter">O</span>アウトプット','定例会議の資料'),
        ('<span class="pg-sipoc-letter">C</span>顧客','部長<br>チームメンバー'),
    ]).replace('class="pg-table"','class="pg-table pg-sipoc-table"')
    a = chapter('sipoc--example','sec-light','SIPOC ─ 記入例',
        'SIPOCで 仕事の外枠を1枚にする',
        '何を受け取り どんな順序で進め 誰に何を渡すか<br>まずは身近な1業務を選び 記入した完成形を見てみる',
        figure('SIPOC / EXAMPLE','業務：週次の定例会議資料の作成',example,
               'S＝供給者　I＝インプット　P＝プロセス　O＝アウトプット　C＝顧客'))
    b = chapter('sipoc--order','sec-navy','SIPOC ─ 書く順番',
        '書きやすいプロセスから始めると<br>手が止まりにくくなる',
        '業務名を決めたら Pを5つ前後のプロセスに分ける<br>書く順番は「業務名 → P → O・C → S・I」がおすすめ',
        figure('SIPOC / ORDER','項目の並びと 書く順番は別でよい',
            route([('01','業務名','週次の定例会議資料の作成'),
                   ('02','P / プロセス','何をするかを5つ前後に分ける'),
                   ('03','O・C / 成果と相手','何を仕上げ 誰が使うかを決める'),
                   ('04','S・I / 供給元と材料','必要な材料と その供給元を確認する')]),
            '順番にすべて埋めようとせず まず実際の仕事の流れから書き始める'),
        [('Pは動詞で書く','抽出する・集計する・集める・まとめる・確認する<br>実際にしている行動を5つ前後に分ける'),
         ('O・Cはセットで考える','何を作るかだけでなく 誰が使うかまで書く<br>この例では定例会議の資料を 部長とチームメンバーが使う'),
         ('S・Iは材料からたどる','必要な案件データと進捗メモを確認する<br>営業管理システムとチームメンバーが供給元になる')])
    jobs = ['必要な案件データを取り出す',
            '決めた集計ルールで数字をまとめる',
            'AIが整理を支援し メンバーが内容を補足・確認する',
            '決めた構成に データとコメントをまとめる',
            '最終確認はマネージャーが担う']
    judgments = rows(['プロセス','判定','この例での分担'],[
        (NUMBERS[i]+' '+name,rating(RATINGS[i]),jobs[i]) for i,name in enumerate(PROCESSES)
    ]).replace('class="pg-table"','class="pg-table pg-sipoc-decisions"')
    mapping = '<dl class="pg-sipoc-map">'+''.join(
        f'<div><dt><span>{letter}</span>{name}</dt><dd><span class="pg-map-example">{example}</span>'
        f'<span class="pg-map-arrow" aria-hidden="true">↓</span><strong>{design}</strong><p>{detail}</p></dd></div>'
        for letter,name,example,design,detail in [
            ('S','供給者','メンバー・営業管理システム','接続先','誰から・どこから取得するか'),
            ('I','インプット','案件データ・進捗メモ','渡す情報','何を材料として読むか'),
            ('P','プロセス','抽出・集計など5工程','手順とルール','どんな順で進めるか'),
            ('O','アウトプット','定例会議の資料','出力の仕様','何をどの形で仕上げるか'),
            ('C','顧客','部長・チームメンバー','受け手と確認点','誰が使い どこで人が確認するか'),
        ])+'</dl>'
    c = chapter('sipoc--blueprint','sec-light','14 / SIPOC → AGENT',
        'SIPOCは そのまま<br>エージェントの設計図になる',
        '仕事の外枠を書いた1枚を 「AIに何を渡し どう動かすか」の設計へつなげる',
        figure('SIPOC / BLUEPRINT','同じ仕事を エージェント設計の言葉で読み替える',mapping,
            'Cは成果物の利用者　最終確認者は別に決める　この例の最終確認者はマネージャー'))
    d = chapter('sipoc--context','sec-navy','15 / S・I ─ コンテキストエンジニアリング',
        '何を渡し どこにつなぐかを決める',
        'コンテキストエンジニアリングは AIが仕事を理解するための情報を整えること<br>必要な材料に加え 目的・対象期間・用語も一緒に渡す',
        figure('S・I / CONTEXT','週次会議の資料を作るAIに渡す情報',
            sheet([('接続先 S','営業管理システムと メンバーの進捗メモの保管先'),
                   ('材料 I','今週の案件データと進捗メモ<br>前週の集計結果と資料のひな形も用意する'),
                   ('前提','対象チーム・集計期間・売上や受注の定義<br>部長が会議で何を判断したいか'),
                   ('取得ルール','必要な範囲だけ読み取る権限を設定<br>データが古い・足りない場合は人に知らせる')],label='この業務の入力設計例'),
            '資料を大量に渡す前に 使う情報・使わない情報・更新元を決める'),
        after=srcs([('コンテキストとハーネスの全体像','context-harness-engineering.html')]))
    e = chapter('sipoc--rules','sec-light','16 / P ─ 手順と判断ルール',
        '手順と判断ルールを<br>言葉にできてから任せる',
        '「いい感じにまとめて」だけでは 期待した処理が決まらない<br>通常の手順と 迷ったときの扱いを一緒に書く',
        figure('P / RULES','週次資料のPを 実行できる指示にする',
            rows(['プロセス','手順の例','判断ルールの例'],[
                ('① データを抽出','対象期間とチームで絞り込む','対象期間が不明なら処理を止めて確認'),
                ('② 数字を集計','決めた項目を案件単位で集計','同じ案件IDが重複したら人に確認'),
                ('④ 資料にまとめる','ひな形の所定の欄に配置','不明な数値やコメントを推測で埋めない'),
            ]),
            'まだ人によって答えが違う箇所は 標準化する論点として残す'),
        [('次は標準化','言葉にできない部分を無理にAIへ渡さず<br>担当者どうしで「いつもの判断」をすり合わせる')])
    f = chapter('sipoc--harness','sec-navy','17 / O・C ─ ハーネスエンジニアリング',
        '出力の形と 人が確認する場所を決める',
        'ハーネスエンジニアリングは AIを業務で動かす周辺の仕組みを整えること<br>ここでは出力形式・検査・承認・記録を具体化する',
        figure('O・C / HARNESS','作成できたところで終わらず 確認してから渡す',
            route([('O','資料案を出す','会議用スライドと元データへの参照<br>対象期間・集計値・進捗を指定の欄へ'),
                   ('CHECK','マネージャーが確認','数値・対象期間・不足項目を確認<br>不備があれば差し戻し 承認まで配布しない'),
                   ('C','部長とチームが使う','承認した版を会議で使用<br>誰がいつ確認したかも記録する')]),
            'C＝利用者と 確認者は同じとは限らない　この例では⑤が人の確認の工程'),
        [('出す形を固定する','必要な項目とファイル形式を先に決める<br>抜け漏れをチェックできる出力にする'),
         ('止め方も設計する','確認で不備が出たら自動配布を止める<br>直す担当者と再確認の流れを決める')])
    # Keep the three criteria and all five judgments together without duplicating earlier pages.
    criteria_compact = '<ol class="pg-sipoc-criteria-line"><li>くり返し発生する</li><li>インプットとアウトプットが決まっている</li><li>最後に人が確認できる</li></ol>'
    g = chapter('sipoc--decisions','sec-light','18 / 任せられるプロセスの見分け方',
        '①②④は任せる ③は手伝わせる<br>⑤の最終確認は人が持つ',
        '業務全体を一括で判定せず Pのプロセスを1つずつ3つの基準で見る',
        figure('SIPOC / DECISIONS','業務：週次の定例会議資料の作成',criteria_compact+judgments,
            '◎ 3つともYES＝任せる　○ 一部YES＝AIに手伝わせる　×＝人がやる'),
        [('会場で試してみる','時間があれば お一人の業務を聞いて5つ前後に分ける<br>どこを任せ どこを手伝わせ どこを人が持つかを一緒に仕分ける')],
        after=srcs([('ワークフローの作り方：Copilot編','../01_concept/five-levels-copilot.html#level3--design'),
                    ('ワークフローの作り方：Gemini編','../01_concept/five-levels-gemini.html#level3--design')]))
    h = chapter('sipoc--standardize-door','sec-navy','19 / おざけんトーク② ─ 18:17–18:23 / 6分',
        'エージェント化の前に<br>標準化',
        'AIに渡す手順は チームの中で揃っているだろうか',
        figure('STANDARDIZE','次の問い',
            '<div class="pg-sipoc-door"><span aria-hidden="true">P</span><p>その仕事のやり方を<br><strong>誰でも同じように説明できるか</strong></p></div>',
            '人による違いを見つける → 共通の型を作る → 現場で直す'))
    lanes = '<div class="pg-sipoc-lanes">'+''.join(
        f'<div><strong>{who}</strong><ol>'+''.join(f'<li>{step}</li>' for step in steps)+'</ol></div>'
        for who,steps in [
            ('AさんのP',['金曜に抽出','受注日で集計','数値から資料化']),
            ('BさんのP',['月曜に抽出','売上日で集計','コメントから資料化']),
            ('共通のP',['対象期間を統一','集計基準を統一','ひな形と確認を統一']),
        ])+'</div>'
    i = chapter('sipoc--different-processes','sec-light','20 / 標準化 ─ 担当者ごとの違いを見る',
        '人によってやり方が違うと<br>AIに渡す手順が決まらない',
        '同じ「週次資料の作成」でも 抽出日・集計の意味・まとめ方が違うことがある<br>どちらが正しいかを決めつけず 仕事の目的に合う共通ルールを話し合う',
        figure('STANDARDIZE / PROCESS','担当者ごとに違うPを 1つの型へそろえる',lanes,
            '違いを見つけるための説明例　必要な違いは 例外条件として型に書き込む'))
    j = chapter('sipoc--eighty','sec-navy','21 / 標準化 ─ 人の時間を取り戻す',
        '標準化は 人を縛るためのものではない',
        '業務を言葉にして型にすることが AI時代のマネージャーの仕事になる<br>目的は 判断や対話など 人が担う仕事に時間を回すこと',
        figure('STANDARDIZE / IMPROVE','80点で型を作り 現場で直していく',
            route([('01','まず型を作る','いつもの手順と判断基準を書き出す<br>最初から完璧を目指さない'),
                   ('02','現場で使って直す','担当者が実際の仕事で試す<br>迷う場面や例外を型に戻す'),
                   ('03','人の仕事へ時間を回す','定型処理を任せる範囲を広げる<br>顧客との対話や改善に使う')]),
            '80点はたたき台の完成度のたとえ　必要な品質基準や人の確認を省く意味ではない'))
    contacts = '<div class="pg-sipoc-contacts">'+''.join(
        f'<a href="{url}" target="_blank" rel="noopener"><span class="pg-sipoc-qr">{qr_svg(url, quiet=4)}</span><span><strong>{label}</strong><small>{display}</small></span></a>'
        for label,display,url in [('Xでつながる','@ozaken_AI','https://x.com/ozaken_AI'),
                                  ('お問い合わせ','ozaken.ai/contact/','https://ozaken.ai/contact/')])+'</div>'
    k = chapter('sipoc--next-week','sec-light','22 / まとめ ─ 18:23–18:25 / 2分',
        '来週 チームとSIPOCを見直そう',
        '今日書いたSIPOCを チームのメンバーと一緒に見直す<br>この後の交流会で 同じ業務に悩む人と話してみてください',
        figure('NEXT WEEK','まず1つの業務から',
            route([('01','メンバーと見直す','Pの手順と判断に<br>人による違いがないか確認する'),
                   ('02','任せ方を仕分ける','①くり返し ②入出力<br>③人の確認で見分ける'),
                   ('03','1つの型を試す','任せる工程と確認者を決める<br>使って分かった改善点を戻す')])+contacts,
            '小澤健祐（おざけん）　質問や実践後の気づきも ぜひ教えてください'))
    return '\n'.join([a,b,c,d,e,f,g,h,i,j,k]).strip()


def transform(page):
    source=apply_body.strip(page)
    # Replace only this generator's additions. Existing methods and invoice examples stay intact.
    owned=[n for n in sections(source) if n.attrs.get('data-practical-guide','').startswith('sipoc--')]
    if owned:
        all_nodes=sections(source)
        positions=[all_nodes.index(n) for n in owned]
        assert positions==list(range(positions[0],positions[-1]+1)), 'SIPOC chapters must stay adjacent'
        source=source[:owned[0].start]+source[owned[-1].end:]
    methods=[n for n in sections(source) if '>Methods<' in n.outer(source)]
    assert len(methods)==1, 'SIPOC insertion point must be unique'
    point=methods[0].end
    # Keep separators owned with the new block, making regeneration byte-stable.
    source=source[:point]+build()+source[point:]
    if ORIGINAL_INTRO in source:
        assert source.count(ORIGINAL_INTRO)==1
        source=source.replace(ORIGINAL_INTRO,UPDATED_INTRO,1)
    else:
        assert UPDATED_INTRO in source, 'Unexpected worksheet introduction'
    return apply_styles(source)


if __name__ == '__main__':
    run({'04_practice/gyomu-bunkai.html': transform}, __doc__)
