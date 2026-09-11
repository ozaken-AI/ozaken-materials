#!/usr/bin/env python3
"""業務分解大全のSIPOCを本人指定の記入例・判断基準で具体化する

python3 gen_sipoc.py --preview-dir /absolute/private-preview
確認後は --update を追加 現在の資料へ4章を追記し 他の本文と図を保持する
"""
from practical_guides import chapter, figure, route, rows, srcs, sections, apply_styles, run
import apply_body

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
    criteria = '<div class="pg-sipoc-checks">'+''.join(
        f'<div><span class="pg-index">0{i}</span><h3>{title}</h3><p>{question}</p></div>'
        for i,(title,question) in enumerate([
            ('繰り返し発生するか','毎週・毎月など<br>同じ仕事が繰り返されるか'),
            ('入出力が決まっているか','インプットとアウトプットが<br>決まっているか'),
            ('最後に人が確認できるか','結果を人が確認できる<br>流れになっているか'),
        ],1))+'</div>'
    verdicts = '<div class="pg-sipoc-verdicts">'+''.join(
        '<div>'+rating(mark)+f'<p>{condition}<strong>{action}</strong></p></div>'
        for mark,condition,action in [('◎','3つともYES','エージェントに任せる'),
                                      ('○','一部YES','AIに手伝わせる'),
                                      ('×','','人がやる')])+'</div>'
    c = chapter('sipoc--criteria','sec-light','SIPOC ─ エージェント化の判断基準',
        '任せ方は プロセスごとに<br>3つだけ確認する',
        '業務全体に1つの判定をつけず Pに書いたプロセスを1つずつ見る',
        figure('SIPOC / CHECK','繰り返し・入出力・人の確認',criteria+verdicts,
            '◎＝エージェントに任せる　○＝AIに手伝わせる　×＝人がやる'))
    jobs = ['必要な案件データを取り出す',
            '決めた集計ルールで数字をまとめる',
            'AIが整理を支援し メンバーが内容を補足・確認する',
            '決めた構成に データとコメントをまとめる',
            '最終確認はマネージャーが担う']
    judgments = rows(['プロセス','判定','この例での分担'],[
        (NUMBERS[i]+' '+name,rating(RATINGS[i]),jobs[i]) for i,name in enumerate(PROCESSES)
    ]).replace('class="pg-table"','class="pg-table pg-sipoc-decisions"')
    d = chapter('sipoc--decisions','sec-navy','SIPOC ─ 記入例の判定',
        '①②④は任せる ③は手伝わせる<br>⑤の最終確認は人が持つ',
        '業務：週次の定例会議資料の作成<br>5つのプロセスに分けると エージェント・AIの補助・人の役割が見える',
        figure('SIPOC / DECISIONS','同じ業務の中でも 任せ方を分ける',judgments,
            'この記入例の判定：①②④＝◎　③＝○　⑤＝×　最終確認の工程を人に残す'),
        after=srcs([('ワークフローの作り方：Copilot編','../01_concept/five-levels-copilot.html#level3--design'),
                    ('ワークフローの作り方：Gemini編','../01_concept/five-levels-gemini.html#level3--design')]))
    return '\n'.join([a,b,c,d]).strip()


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
