#!/usr/bin/env python3
"""本人提供の4象限図に沿って AI-SECIの8章を更新する

python3 gen_seci.py --preview-dir /absolute/private-preview
確認後に同じコマンドへ --update を付ける
現在の暗号化HTMLから対象章だけを更新し 共通表紙と既存スクリプトを保持する
"""
from practical_guides import chapter, figure, route, exchange, rows, srcs, replace_chapters, cover_lead, run

PAPER = 'https://doi.org/10.1016/S0024-6301(99)00115-6'
MCP = 'https://modelcontextprotocol.io/docs/getting-started/intro'
STAGES = [
    ('S', '共同化', 'Socialization', '暗黙知', '暗黙知',
     '自分の暗黙知に気づき<br>他者と共有する',
     ['業務プロセスのインタビュー', 'ワークショップ・ディスカッション'], 'AI活用も可能'),
    ('E', '表出化', 'Externalization', '暗黙知', '形式知',
     '暗黙知をプロンプトや<br>ワークフローに変える',
     ['コンテキストエンジニアリング', 'チャットボット化・ワークフロー化'], 'システムプロンプトが重要'),
    ('C', '結合化', 'Combination', '形式知', '形式知',
     'ワークフローやデータをつなぎ<br>仕組みとして体系化する',
     ['ワークフロー連携・チャットボット連携', 'RAGシステムの構築・MCP連携'], ''),
    ('I', '内面化', 'Internalization', '形式知', '暗黙知',
     '現場で使い 自分の暗黙知を更新する<br>新しい暗黙知として文句も生まれる',
     ['実業務への適用', '現場レビューによるエージェントの改善'], ''),
]


def knowledge(before, after):
    return f'<p class="pg-seci-knowledge"><span>{before}</span><span aria-hidden="true">→</span><span>{after}</span></p>'


def connector(key, direction, mobile=False):
    vertical = direction in ('down', 'up')
    path = {'right':'M2 10H54','down':'M10 2V54','left':'M58 10H6','up':'M10 58V6'}[direction]
    marker = f'seci-tip-{key}{"-mobile" if mobile else ""}'
    cls = 'pg-seci-mobile-arrow' if mobile else 'pg-seci-arrow pg-seci-arrow-'+direction
    view = '0 0 20 60' if vertical else '0 0 60 20'
    return (f'<svg class="{cls}" viewBox="{view}" aria-hidden="true">'
            f'<defs><marker id="{marker}" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
            '<path d="M0 0L8 4L0 8Z" fill="#2e5496"/></marker></defs>'
            f'<path class="a-flow" d="{path}" fill="none" stroke="#2e5496" stroke-width="1.5" marker-end="url(#{marker})"/></svg>')


def cycle():
    cells = []
    for i,(key,name,en,before,after,desc,examples,accent) in enumerate(STAGES):
        emphasis = f'<p class="pg-seci-emphasis{" pg-seci-important" if key=="E" else ""}">{accent}</p>' if accent else ''
        examples_html = ''.join(f'<li>{item}</li>' for item in examples)
        cells.append(f'<li class="pg-seci-stage pg-seci-{key.lower()}">'
            +f'<div class="pg-seci-heading"><h3>{name}<span>{en}</span></h3>'
            +knowledge(before,after)+f'</div><p class="pg-seci-desc">{desc}</p>'
             f'<ul class="pg-seci-examples">{examples_html}</ul>{emphasis}'
            +connector(key,('right','down','left','up')[i])
            +(connector(key,'down',True) if i<3 else '')+'</li>')
    return '<div class="pg-seci-cycle"><ol class="pg-seci-grid">'+''.join(cells)+'</ol>' \
           '<p class="pg-seci-return">↶　現場で生まれた新しい暗黙知を 次の共同化へ</p></div>'


def transform(page):
    built = []
    built.append(chapter('seci-overview','sec-light','AI-SECI ─ Overview',
        'AI-SECIモデル<br>暗黙知を形式知化する4プロセス',
        '経験や判断を共有し AIが使える形にして 現場へ戻す<br>共同化 → 表出化 → 結合化 → 内面化を回すたびに 次の知が生まれる',
        figure('01 / CYCLE','知の形を変えながら 時計回りに一周する',cycle(),
               '暗黙知＝人の中にある経験・コツ・判断　形式知＝共有できる言葉・手順・設定'),
        after='<p class="note">野中郁次郎らのSECIモデルを 小澤健祐がAI活用の実務へ応用した整理<br>知の変換は 共同化＝暗黙知から暗黙知　表出化＝暗黙知から形式知<br>結合化＝形式知から形式知　内面化＝形式知から暗黙知</p>'
              +srcs([('理論の参照：Nonaka・Toyama・Konno（2000）',PAPER)])))
    built.append(chapter('seci-socialization','sec-navy','S ─ 共同化 / Socialization',
        '共同化<br>自分の暗黙知に気づき 他者と共有する',
        '業務の棚卸しやインタビューで 自分が無意識にしていた判断を見つける<br>ワークショップで実例を持ち寄り その経験を他者と共有する',
        figure('02 / SOCIALIZATION','個人の中にある判断を 対話の場へ持ち出す',
            knowledge('暗黙知','暗黙知')
            +exchange('自分の中にある判断','「この問い合わせは<br>先に担当へ確認する」',
                     '他者と共有する経験','どこを見て判断したか<br>同じ実例で一緒に確かめる'),
            '次に渡すもの：共有した判断の着眼点・業務の流れ・例外・実例'),
        [('インタビュー','暗黙知を持つ社員に仕事の流れを聞く<br>「何を見た？」「なぜそうした？」で理由を掘る'),
         ('ワークショップ','同じ業務の実例を持ち寄り<br>判断が分かれる場面をディスカッションする'),
         ('AI活用も可能','質問案・文字起こし・整理をAIが支援する<br>経験の意味や判断の妥当性は現場の人が確かめる')],
        after='<p class="note">ここでの中心は 経験の自己認識と共有<br>共有した知をAIが使う指示や手順として定めるのが 次の表出化</p>'))
    built.append(chapter('seci-externalization','sec-light','E ─ 表出化 / Externalization',
        '表出化<br>暗黙知をプロンプトやワークフローに変える',
        '共有した判断を AIに渡せる言葉・参照情報・処理の順番に落とし込む<br>チャットボットやワークフローとして動かせる形式知にする',
        figure('03 / EXTERNALIZATION','何を渡すかを設計し どう動かすかを決める',
            knowledge('暗黙知','形式知')
            +'<div class="pg-pair"><div><span class="pg-label">DESIGN / AIに何を渡すか</span>'
             '<h3>判断の土台を揃える</h3>'
             '<div class="pg-seci-item"><h4>コンテキストエンジニアリング</h4><p>背景・参照資料・実例など<br>AIが判断するために必要な情報を揃える</p></div>'
             '<div class="pg-seci-item"><h4>システムプロンプト</h4><p>役割・判断基準・例外への対応・出力の形<br>毎回守ってほしい土台の指示を定める</p></div></div>'
             '<div><span class="pg-label">IMPLEMENT / どう動かすか</span><h3>使える形にする</h3>'
             '<div class="pg-seci-item"><h4>チャットボット化</h4><p>質問に答える役割と参照する知識を設定<br>例：規程を根拠に 申請先まで案内する</p></div>'
             '<div class="pg-seci-item"><h4>ワークフロー化</h4><p>入力・処理・条件・出力を順番に設定<br>例：問い合わせを分類して 担当へ通知する</p></div></div></div>'
             '<p class="pg-seci-emphasis pg-seci-important">システムプロンプトが重要　「何をするか」と「迷ったときの判断」を明記する</p>',
            '次に渡すもの：プロンプト・参照情報・ワークフロー・試せるAIエージェント'),
        [('レベル2につながる','まずは1業務に詳しいチャットボット<br>よい回答の型と根拠を揃えて試す'),
         ('レベル3につながる','受付から記録・通知までのワークフロー<br>各処理の受け渡し項目と条件を決めて試す'),
         ('現場の判断で確かめる','もっともらしい文章だけでは判定しない<br>実例と例外を使い 判断の順序まで確かめる')],
        after=srcs([('レベル2・3の作り方：Copilot編','../01_concept/five-levels-copilot.html#level2--design'),
                    ('レベル2・3の作り方：Gemini編','../01_concept/five-levels-gemini.html#level2--design')])))
    built.append(chapter('seci-combination','sec-navy','C ─ 結合化 / Combination',
        '結合化<br>作った型とデータをつなぎ 仕組みにする',
        'ワークフローを組み合わせたり データベースと連携したりして システムを体系化する<br>マルチAIエージェントやRAGなどを 必要な役割に合わせて組み込む',
        figure('04 / COMBINATION','連携は つなぐ相手と目的で選ぶ',
            knowledge('形式知','形式知')
            +'<div class="pg-seci-options">'
             '<div><span class="pg-label">01 / PROCESS</span><h3>ワークフロー連携</h3><p>前の処理の結果を 次の処理へ渡す<br>例：受付 → 分類 → 台帳への記録 → 通知</p></div>'
             '<div><span class="pg-label">02 / AGENTS</span><h3>チャットボット連携</h3><p>得意な役割を分けて結果をまとめる<br>例：規程を調べる役 → 回答を確認する役<br>複数の役を組み合わせるマルチAIエージェント</p></div>'
             '<div><span class="pg-label">03 / KNOWLEDGE</span><h3>RAGシステムの構築</h3><p>必要な資料を検索し その内容を材料に回答する<br>例：就業規則と申請手順から根拠を取り出す</p></div>'
             '<div><span class="pg-label">04 / CONNECTION</span><h3>MCP連携</h3><p>AIと外部ツール・データを共通の接続方式でつなぐ<br>例：必要な情報を業務データベースから取得する</p></div></div>'
             '<p class="pg-band">これらは併用できる すべてを使うのではなく 足りない機能に合わせて選ぶ</p>',
            '次に渡すもの：参照先・役割・受け渡す情報・接続先が決まった仕組み'),
        [('根拠を揃える','正本と更新担当を決める<br>検索した根拠が質問に合うかも確かめる'),
         ('受け渡しを揃える','質問・根拠・判断結果を次の処理や役へ渡す<br>最終回答をまとめる役も決めておく'),
         ('連携した効果を見る','つなぐ前と後で比べる<br>正確さ・時間・手間が改善したかを確かめる')],
        after=srcs([('MCPの参照：公式ドキュメント',MCP)])))
    built.append(chapter('seci-internalization','sec-light','I ─ 内面化 / Internalization',
        '内面化<br>現場で使うと 自分の暗黙知が更新される',
        '人がエージェントなどを実業務で使い 新しいコツや判断を身につける<br>その過程で生まれる文句や改善点も 新しい暗黙知の手がかりになる',
        figure('05 / INTERNALIZATION','使う前には分からなかったことが見えてくる',
            knowledge('形式知','暗黙知')
            +exchange('現場で出た文句','「答えは合っているけど<br>結局どこに申請するの？」',
                     '使って更新された判断','「回答には根拠だけでなく<br>次の行動も必要だ」'),
            '次に渡すもの：新しく得たコツ・違和感・困った場面・期待していた動き'),
        [('実業務に適用する','試作した本人だけでなく<br>普段その仕事をする人が実例で使う'),
         ('現場でレビューする','どの場面で何が足りなかったかを振り返る<br>現場の声をエージェントなどの改善につなげる'),
         ('次の共同化に戻す','人の中に生まれた気づきを他者と共有する<br>使うだけでAIの設定が自動改善されるわけではない')]))
    built.append(chapter('seci-feedback','sec-navy','Feedback ─ 改善の受け渡し',
        '文句を そのまま次の仕様に変える',
        '内面化で生まれた違和感を 共同化で共有し 表出化や結合化で直す',
        figure('06 / FEEDBACK','同じ問い合わせ業務で 一周をもう一度回す',
            rows(['現場の声','共同化で確かめること','次に直すもの'],[
                ('申請先が分からない','完了するには何が必要か','表出化：回答の型に申請先を追加'),
                ('古い規程で案内された','正本はどれか 更新日はいつか','結合化：参照先と更新方法を修正'),
                ('例外をそのまま断定された','どの条件なら担当へ確認するか','表出化：確認へ回す条件を追加')]),
            '改善したら同じ質問で再確認する 直した理由も残す'),
        [('記録する3点','入力・実際の出力・期待との差<br>その場の状況が分かる形で残す'),
         ('もう一度使う','設定を変えて終わりにしない<br>前の困りごとが解消したか現場で確かめる')]))
    built.append(chapter('seci-first-cycle','sec-light','Practice ─ 最小の一周',
        'まず1つの業務で 小さく一周させる',
        '例：社内規程の問い合わせ対応<br>詳しい人・作る人・使う人で 同じ実例を見ながら進める',
        figure('07 / FIRST CYCLE','共有した判断が 現場で更新されるまで',
            route([('S','共有する','質問と例外の判断を持ち寄る'),
                   ('E','型にする','プロンプトやフローに落とす'),
                   ('C','つなぐ','必要な規程や処理と連携する'),
                   ('I','使って学ぶ','新しいコツや文句を得る')],loop=True),
            'RAG・MCP・複数エージェントなどは 必要性が分かったところから加える'),
        [('完成の目安','現場の人が使えて<br>次に直す理由が1つ具体的に言えること'),
         ('継続の決め方','誰が改善点を集め 誰が設定を直すか<br>次に確かめる場を決めてから一周を終える')]))
    built.append(chapter('seci-summary','sec-navy','Summary',
        '形式知を動かすことで<br>現場の暗黙知が更新される',
        '共有する → プロンプトやフローにする → 仕組みをつなぐ → 現場で使う',
        figure('TAKEAWAY','一周の終わりが 次の知識創造の入口になる',
            exchange('表出化・結合化で整えるもの','現場の知を使える<br>プロンプト・手順・仕組み',
                     '内面化で人の中に生まれるもの','新しいコツや判断<br>次に共有したい文句や改善点'),
            '共同化・表出化・結合化・内面化を 1業務で回し続ける')))
    updated = replace_chapters(page,[(f'Section {i:02d}' if i<8 else 'Summary',s) for i,s in enumerate(built,1)])
    return cover_lead(updated,transform.cover_copy)


transform.cover_copy = ('野中郁次郎のSECIモデルを AI活用の実務へ落とし込む<br>'
                        '現場の暗黙知を共有し プロンプトやワークフローへ変える<br>'
                        '仕組みをつなぎ 現場で使い 次の知へ戻す')


if __name__ == '__main__':
    run({'01_concept/ai-seci.html': transform}, __doc__)
