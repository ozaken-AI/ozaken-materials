#!/usr/bin/env python3
"""5レベルのCopilot編・Gemini編を同じ構成で改訂する

python3 gen_five_levels.py --preview-dir /absolute/private-preview
確認後に --update を追加する パスワードは非表示入力
レベル2を3章 レベル3を5章へ展開し Getting startedをAI-SECIの実践へ更新する
表紙・その他9章・既存スクリプト・関連資料リンクは現在の配信HTMLから保持する
"""
from practical_guides import chapter, figure, route, sheet, exchange, rows, srcs, replace_chapters, run

EDITIONS = {
 'copilot': {
  'bot':'Copilot Studioのエージェント', 'flow':'Power Automate',
  'bot_start':'Copilot Studioでエージェントを作成し 名前・説明・指示を設定する',
  'knowledge':'ナレッジに正式な規程のファイルやSharePointを追加する 参照範囲の設定も確認する',
  'share':'テスト後に公開し Teamsなどの利用先と利用者の権限を確認する',
  'mail':'Outlook', 'record':'SharePointリスト', 'chat':'Teams',
  'start':'［マイ フロー］から自動化したクラウドフローを作成 Outlookのメール受信トリガーで 対象のフォルダーと件名の条件を設定する',
  'ai':'AI Builderの［プロンプトを実行］を追加 先に作った抽出用プロンプトを選び 入力「問い合わせ本文」に受信メールの本文を渡す',
  'condition':'条件の処理を追加 必須項目が空なら担当者の確認へ回す 揃っている場合だけ記録と通常通知へ進める',
  'save':'SharePointの項目作成で各列に抽出結果を割り当てる 続くTeamsの投稿に要約・送信者・作成した記録へのリンクを渡す',
  'launch':'接続先と実行アカウントを確認して保存 テスト用メールを送り 実行履歴で各処理の入力と出力を確認する',
  'bot_source':('Microsoft：エージェントの作成・知識・公開','https://learn.microsoft.com/en-us/microsoft-copilot-studio/microsoft-365-copilot-extend-with-agents'),
  'flow_sources':[('Microsoft：クラウドフローの作成','https://learn.microsoft.com/en-us/power-automate/get-started-logic-flow'),
                  ('Microsoft：フロー内でプロンプトを実行','https://learn.microsoft.com/en-us/ai-builder/use-a-custom-prompt-in-flow')],
 },
 'gemini': {
  'bot':'GeminiのGem', 'flow':'Workspace Studio',
  'bot_start':'Geminiの［Gem］から［Gemを作成］を開き 名前とカスタム指示を入力する',
  'knowledge':'［知識］に正式な規程のファイルを追加する Googleドライブの資料を使う場合も参照先と共有範囲を確認する',
  'share':'プレビューで試して保存 Gemを共有し 利用者が開いて必要な知識を使えるか確認する',
  'mail':'Gmail', 'record':'Googleスプレッドシート', 'chat':'Google Chat',
  'start':'Workspace Studioでフローを新規作成 Gmailのメール受信スターターを選び 対象となる件名などの条件を設定する',
  'ai':'［抽出／Extract］を追加 抽出元に受信メールの本文を変数で指定し 欲しい項目名と説明を設定する',
  'condition':'先に担当へ受付通知を追加 続けて［条件を確認／Check if］で必須項目を確認する 条件を満たさなければ以降の処理は止まる',
  'save':'スプレッドシートへの行追加で各列に抽出結果の変数を割り当てる 続くChat通知に要約・送信者・記録先へのリンクを渡す',
  'launch':'［テスト実行］でスターターと各ステップの結果を確認する 接続先と通知先を確かめてからフローを有効にする',
  'bot_source':('Google：Gemの作成・知識・プレビュー','https://support.google.com/gemini/answer/15146780?hl=ja'),
  'flow_sources':[('Google：最初のフローを作成する','https://support.google.com/a/users/answer/16430397?hl=ja'),
                  ('Google：スターターとステップの一覧','https://support.google.com/workspace-studio/table/17176961?hl=en'),
                  ('Google：AIステップの使い方','https://support.google.com/workspace-studio/answer/16431105?hl=en')],
 },
}


def level2(c):
    a = chapter('level2--design','sec-navy','Level 2 ─ Custom Bot / 1 of 3',
        'レベル2の作り方<br>まず1つの仕事に詳しい相談相手を作る',
        f'例：社内規程の問い合わせに答えるチャットボット<br>{c["bot"]}に 役割・知識・回答の型を持たせる',
        figure('L2 / BUILD','チャットボットを作る5つの手順',
            route([('01','役割を絞る','誰の どんな質問に答えるか'),
                   ('02','知識を用意','正本と更新担当を決める'),
                   ('03','指示を書く','答え方と答えない範囲を決める'),
                   ('04','実例で試す','質問と期待する回答を比べる'),
                   ('05','共有する','使う人と改善窓口を決める')]),
            '完成の目安：利用者が毎回長い前提を入力せずに 業務に沿った回答を得られる'),
        [('作成画面で行うこと',c['bot_start']),
         ('先に用意するもの','最新の規程と申請手順 よくある質問<br>古い版や矛盾があれば担当者に確かめる'),
         ('仕事の範囲を決める','最初は手順の案内まで<br>実際の申請登録や承認は別の処理として設計する')],
        after=srcs([c['bot_source']]))
    b = chapter('level2--instructions','sec-light','Level 2 ─ Custom Bot / 2 of 3',
        '指示には「知らないとき」まで書く',
        '「あなたは優秀な担当者です」だけでは 業務の判断基準が伝わらない<br>次の例を 自社の正本と連絡先に合わせて置き換える',
        figure('L2 / INSTRUCTIONS','そのまま設計のたたき台にできる指示例',
            sheet([
                ('役割','社内規程の問い合わせ窓口として 申請方法を案内する'),
                ('参照する知識','登録された正式な規程と申請手順を確認する 回答には文書名と該当箇所を示す'),
                ('回答の順番','結論 → 適用条件 → 根拠 → 次にすること の順に短く答える'),
                ('不明なとき','条件が足りなければ質問する 根拠がない場合や文書が矛盾する場合は断定せず担当窓口へ案内する'),
                ('対応の範囲','手順の案内までを行う 申請が完了したと回答しない')],label='EXAMPLE / 社内規程案内のカスタム指示'),
            '知識を付けるだけでは回答の正しさは保証されない 指示と実例による確認を組み合わせる'),
        [('知識を接続する',c['knowledge']),
         ('出力を確かめる','文書名を表示しただけで合格にしない<br>引用した箇所が回答を裏付けているか確認する')])
    d = chapter('level2--test','sec-navy','Level 2 ─ Custom Bot / 3 of 3',
        '公開前に 4種類の質問を通す',
        '正しく答えられるかと 適切に答えを留保できるかを一緒に見る',
        figure('L2 / TEST','質問と期待する動きを 先にペアで作る',
            rows(['試すこと','質問の例','期待する動き'],[
                ('普通の質問','休暇申請の手順は？','規程に沿った手順・根拠・申請先を示す'),
                ('条件が足りない','このケースは対象？','必要な条件を聞き返す'),
                ('知識にない質問','まだ公表されていない制度は？','未確認と伝え 担当窓口を示す'),
                ('知識が食い違う','旧版と新版で条件が違う','適用される正本を確認し 不明なら留保する')]),
            '質問の表現を変えて繰り返し試す 知識や指示を直したら同じ質問でも再確認する'),
        [('利用者へ渡す',c['share']),
         ('利用者の立場で試す','作成者以外のアカウントでも試す<br>見せてよい資料とアクセス権を確認する'),
         ('改善の入口を作る','困った質問・回答・期待との差を集める<br>指示と知識のどちらを直すか判断する')])
    return '\n'.join([a,b,d])


def level3(c):
    copilot = c['flow'] == 'Power Automate'
    a = chapter('level3--design','sec-light','Level 3 ─ Workflow / 1 of 5',
        'レベル3の作り方<br>問い合わせを受けて 担当へ渡すまでつなぐ',
        f'例：{c["mail"]}で受信 → 要点を抽出 → {c["record"]}に記録 → {c["chat"]}で担当へ通知<br>誰が何をするかと 次へ渡す情報を あらかじめ決める',
        figure('L3 / FLOW','処理の順番と 進む条件を設計する',
            route([('01','受信する','対象のメールだけを拾う'),
                   ('02','AIで抽出','要件・希望日を取り出す'),
                   ('03','条件を確認','必要な情報が揃ったか'),
                   ('04','記録する','受付内容を台帳へ追加'),
                   ('05','通知する','要点と記録先を担当へ渡す')]),
            '条件が揃わないメールは担当者の確認へ回す ここでは申請者への自動回答までは行わない'),
        [('AIに任せる処理','自由な文章から要点を取り出す<br>曖昧な言葉を扱う部分にAIを使う'),
         ('決めた処理で進める','条件分岐・記録・通知は設定した順で行う<br>フローのすべての工程にAIを置く必要はない'),
         ('レベル2との違い','回答に加え 複数の処理をつなぐ<br>レベル3は手順を事前に決めることが軸で 起動方法だけでは決まらない')])
    data = chapter('level3--data','sec-navy','Level 3 ─ Workflow / 2 of 5',
        '次へ渡す項目を決めると<br>フローのつなぎ方が見えてくる',
        '架空のテストメール：「2026年9月18日に休暇を取りたいです 申請手順を教えてください」<br>受信データとAIの抽出結果を分けて 次の処理に渡す',
        figure('L3 / DATA','文章を 業務で使える項目に分ける',
            rows(['受け渡す項目','取り出し元','テストデータの例'],[
                ('メールID・送信者','受信トリガーの変数','test-001 / staff@example.com'),
                ('要件','AIによる本文の抽出','休暇申請の手順を確認したい'),
                ('希望日','AIによる本文の抽出','2026-09-18'),
                ('記録先','作成した台帳・保存処理','担当者が受付内容を確認するリンク')]),
            '要件と希望日を必須とする練習例 記載がなければ推測せず 未記載として扱う'),
        [('抽出結果の形を設定する',
          'AI Builderのプロンプトで出力をJSONに変更<br>「要件」「希望日」の文字列項目を定義してテストし 保存した項目を後の処理で選ぶ'
          if copilot else
          'Extractで「要件」「希望日」をカスタム項目に追加<br>項目の説明に 未記載時の扱いと日付の形式を指定する'),
         ('保存先の列を先に作る',
          'メールID・送信者・要件・希望日を用意<br>練習では希望日も文字列で揃える 日付型にする場合は未記載と形式の検査を追加する')],
        after=srcs([('Microsoft：JSON出力の設定','https://learn.microsoft.com/en-us/microsoft-copilot-studio/process-responses-json-output')]) if copilot else srcs(c['flow_sources'][1:2]))
    b = chapter('level3--configure','sec-light','Level 3 ─ Workflow / 3 of 5',
        '画面で部品を置き 変数で情報をつなぐ',
        f'{c["flow"]}で 前の処理の出力を 次の処理の入力へ割り当てる<br>「メール本文」と文字を打つだけでは本文は渡らない 画面の変数・動的コンテンツから選ぶ',
        figure('L3 / CONFIGURE',f'{c["flow"]}で設定する5か所',
            sheet([('01 起動',c['start']),('02 AI処理',c['ai']),
                   ('03 分岐',c['condition']),('04 記録と通知',c['save']),('05 テスト',c['launch'])],
                  label='SETUP / 問い合わせ受付フロー'),
            '利用できる機能や画面名は契約・管理者設定で異なる 接続先への権限とAI処理の利用条件を確認する'),
        [('変数をつなぐ例','受信本文 → AI処理の入力<br>抽出した要件 → 台帳の「要件」列<br>台帳の記録先 → 担当への通知'),
         ('AI処理に渡す指示の例','「本文から要件と希望日を抽出<br>書かれていない項目は未記載とする」<br>送信者とメールIDは受信データから直接渡す')],
        after='<p class="note">「未記載」と空欄のどちらを返すかを揃え 分岐条件も同じ値で設定する<br>希望日が不要な業務なら必須にしない 項目と条件は業務に合わせて決める</p>'+srcs(c['flow_sources']))
    condition = chapter('level3--conditions','sec-navy','Level 3 ─ Workflow / 4 of 5',
        '条件を満たさないときの行き先を作る',
        'この練習では「要件」と「希望日」が必要<br>空欄や未記載を除外し 両方が揃ったときだけ通常処理へ進める',
        figure('L3 / CONDITIONS','同じ抽出結果から 進む先を分ける',
            '<div class="pg-pair"><div><span class="pg-label">READY / 必須項目あり</span><h3>記録して担当へ渡す</h3>'
            '<p>要件あり AND 希望日あり<br><br>台帳へ記録 → 担当へ完了通知</p></div>'
            '<div><span class="pg-label">REVIEW / 必須項目なし</span><h3>人が不足を確認する</h3>'
            '<p>要件なし OR 希望日なし<br><br>通常処理を止める → 担当が情報を確認</p></div></div>',
            '値があることと 内容が正しいことは別 テストで抽出精度も確かめる'),
        [('画面で設定すること',
          'Power Automateの条件で AND を設定<br>真の側に記録と完了通知 偽の側に担当への確認依頼を置く'
          if copilot else
          'Check ifは条件を満たすときだけ後続へ進む<br>この例ではその前に全件の受付通知を送り 不足で止まった案件も担当が確認できるようにする'),
         ('元の問い合わせも渡す',
          '担当者には抽出結果だけでなく 元メールを特定できる情報も渡す<br>何が足りないかを本文に戻って確認できるようにする')],
        after='' if copilot else srcs(c['flow_sources'][1:2]))
    d = chapter('level3--test','sec-light','Level 3 ─ Workflow / 5 of 5',
        '1件を最後まで流し<br>途中で困ったときの戻り先も確かめる',
        '各処理の入力と出力を確認すると どこで情報が切れたのかが分かる',
        figure('L3 / TEST','普通に流れるケースと 止まるケースを試す',
            rows(['テスト入力','見る場所','期待する結果'],[
                ('必要な項目があるメール','抽出結果 → 台帳 → 通知','同じ内容がつながり 正しい担当へ届く'),
                ('要件や必須の希望日がない','抽出結果と条件分岐','通常処理へ進まず 担当の確認へ回る'),
                ('同じメールを再処理','メールIDと既存の記録','重複を検出し 二重登録を防ぐ'),
                ('接続先やAI処理が失敗','実行履歴と失敗通知','停止箇所が分かり 担当が再実行を判断できる')]),
            '重複検査や失敗時の通知は 必要な処理として追加する 自動で備わるとは限らない'),
        [('公開前の到達点','テスト用の記録先と通知先で確認する<br>正常・不足・重複・失敗の結果を残す'),
         ('運用で決めること','止める人・直す人・再実行する人を決める<br>試行後に本番の接続先へ切り替える'),
         ('改善の見つけ方','「通知の要点が足りない」はAI指示<br>「違う人に届く」は分岐や通知先を見直す')])
    return '\n'.join([a,data,b,condition,d])


def getting_started():
    return chapter('levels-practice','sec-navy','Getting started',
        '作ったあとを AI-SECIで回す',
        'レベル2は回答の型 レベル3は仕事の流れ<br>どちらも現場で使い 改善点を次の仕様へ戻して育てる',
        figure('PRACTICE / AI-SECI','最初の1体を 1業務の循環に置く',
            route([('S','共同化','棚卸しで暗黙知を言葉にする'),
                   ('E','表出化','チャットボットやフローを作る'),
                   ('C','連結化','RAGや別の役割とつなぐ'),
                   ('I','内面化','使って新しい文句や気づきを得る')],loop=True),
            '小澤健祐によるAI活用の実務モデル 原典の用語との対応はAI-SECI資料を参照'),
        [('今日やること','実際に困った問い合わせを1件選ぶ<br>よい回答と 完了までの手順を書き出す'),
         ('次に確かめること','作った人以外に使ってもらう<br>文句を1件持ち帰り 指示・知識・手順を直す')],
        after=srcs([('4工程を個別に読む：AI-SECIモデル','../01_concept/ai-seci.html#seci-overview')]))


def transform(page, edition):
    c = EDITIONS[edition]
    return replace_chapters(page,[('Level 2 ─ Custom Bot',level2(c)),
                                   ('Level 3 ─ Workflow',level3(c)),
                                   ('Getting started',getting_started())])


if __name__ == '__main__':
    run({f'01_concept/five-levels-{edition}.html':lambda page,e=edition:transform(page,e)
         for edition in EDITIONS}, __doc__)
