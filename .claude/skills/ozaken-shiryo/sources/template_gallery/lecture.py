"""Projection/print catalogue. All information is server-rendered; no content controls."""
import re
from .scenes import e, scene, svg, node, grid
from .next import curtain, parts as next_parts

# Familiar identities remain stable for existing links; their presentations are now static.
PART_LABELS = {
 'copyable': ('依頼文の見本', '目的・条件・出力を、そのまま読める形に。', 'ことば'),
 'flip': ('問いと答えの対', '問いから答えへ、視線でつなぐ。', '構成'),
 'toggle_pair': ('前後の対比', '同じ観点の変化を、同時に見せる。', '構成'),
 'tabs': ('観点の並列', '異なる立場の説明を、一枚で見渡す。', '構成'),
 'accordion': ('説明の一覧', '見出しと説明を、ひと続きで読む。', '構成'),
 'wave': ('波のアクセント', '固定した言葉に、波打つ光を添える。', '強調'),
 'counter': ('数字の余韻', '完成した数値に、光のアクセントを添える。', '数字'),
 'poll': ('問い・選択肢・理由', '選択肢と判断の根拠を、同じ面に置く。', '構成'),
 'reactive_sentence': ('計算が伝わる一文', '条件・計算・結果を、一つの流れで見せる。', '数字'),
 'focus_note': ('工程と注釈', '全体の流れと、それぞれの意味を結ぶ。', '強調'),
 'wipe': ('整理前後の対比', '同じ内容の見せ方を、左右で比べる。', '構成'),
 'decision': ('判断とその理由', '選択肢と、その後の進め方を並べる。', '構成'),
 'chapter': ('次章へつながる言葉', '共通する言葉を残し、論点をつなぐ。', 'ことば'),
}

def pairs(items, cls=''):
    return '<div class="lt-pairs '+cls+'">'+''.join('<div><span>%s</span><div>%s</div></div>' % (e(a),b) for a,b in items)+'</div>'

def static_part(k, data):
    a=data.get('args',{}); html=data['html']
    if k=='flip':
        front=a['front'].replace('いちばん先に見るべき条件はどれでしょうか。','候補を見つける手がかりの一つは何でしょうか。').replace('難しさでも、時間の長さでもありません。','回数だけで決めず、確認のしやすさや失敗時の影響も見ます。')
        back=a['back'].replace('難しさでも、時間の長さでもありません。','回数だけで決めず、確認のしやすさや失敗時の影響も見ます。').replace('効きが大きく、失敗しても取り返しがつきます。','効果を積み重ねられます。')
        return pairs([('問い',front),('答え',back)])
    if k=='toggle_pair': return pairs([(a['a_label'],a['a_body']),(a['b_label'],a['b_body'])])
    if k=='tabs': return pairs(a['items'],'lt-columns')
    if k=='accordion': return pairs([
        ('図版と本文パーツの使い分け','関係・順番・割合を一目で伝えるなら図版。言葉の意味や根拠を伝えるなら本文パーツ。'),
        ('講演と印刷で、同じ内容を','すべての情報は最初から表示。図の動きが止まっていても、比較と結論を読めます。'),
        ('小さな画面では、縦に読む','比較や工程は縦並びへ組み替えます。端末の「動きを減らす」設定にも対応します。')],'lt-rows')
    if k=='poll':
        opts=[x.replace('手順を決めて渡し、AIが順に実行して結果を返す','目的と制約を渡し、AIが手順を組み立てて実行・確認する') for x in a['options']]
        why=(a.get('why') or '').replace('手順をAI自身が回している','手順の組み立てと実行・確認をAIが担っている')
        return '<div class="lt-question"><h4>'+e(a['question'])+'</h4>'+pairs([(('%02d / 正解' if i==a['answer'] else '%02d')%(i+1),e(x)) for i,x in enumerate(opts)],'lt-rows')+'<p class="lt-reason">'+why+'</p></div>'
    if k=='copyable': return '<div class="lt-script"><span>依頼文</span><pre>'+e(a['text'])+'</pre>'+'<p>目的・条件・出力の形を添えた依頼文の見本です。</p>'+'</div>'
    if k=='reactive_sentence': return '<div class="lt-equation"><p>週 <b>3</b> 回 × <b>20</b> 分 × <b>4</b> 週間</p><i aria-hidden="true">↓</i><p>短縮時間 <strong>4</strong> 時間</p><small>4週間として単純計算した仮想例。</small></div>'
    if k=='evidence': return '<div class="lt-evidence"><h4>待ち時間は、<br><em>全体の40%。</em></h4>'+pairs([('対象','直列に進む提案業務の仮想例'),('計算','承認待ち12時間 ÷ 全体30時間'),('出典','この便覧の説明用データ'),('留意点','実際の業務に一般化しません。')],'lt-rows')+'</div>'
    if k=='focus_note': return pairs([('01 / 準備','目的・対象・使える情報を揃える。'),('02 / 判断','任せる範囲と、人が確認する条件を決める。'),('03 / 実行','合意した条件に沿って進め、結果を確認する。')],'lt-columns lt-route')
    if k=='wipe': return pairs([('整理前','<p>提案書は、目的を揃え、条件を決め、確認する人を決めてから作り始める。</p>'),('整理後','<h4>作り始める前に、3つを決める。</h4><ol><li>目的を揃える</li><li>条件を決める</li><li>確認する人を決める</li></ol>')])
    if k=='decision': return '<div class="lt-question"><h4>初めての業務を、どう任せる？</h4>'+pairs([('小さく試す','1件の低い影響範囲で試し、結果を確認。条件を具体化できます。'),('草案まで任せる','草案作成を任せ、公開・送信の前に人が確認。作成と最終判断を分担できます。')])+'</div>'
    if k=='trace': return pairs([('01 / 00:00 入力を受け取る','対象期間と集計条件を受け取った、という記録の見本。'),('02 / 00:02 対象を検索する','指定範囲のデータを検索。参照先と実行結果を残します。'),('03 / 00:05 草案を作る','確認できた内容から草案を作成。出力への参照を残します。'),('04 / 00:10 人が確認する','確認者が根拠と出力を照合。修正内容と承認結果を残します。')],'lt-rows')+'<p class="lt-note">架空の実行記録。AIの内的な思考を示すものではありません。</p>'
    if k=='units':
        return '<div class="nx-units is-grouped">'+re.sub(r'<button\b[\s\S]*?</button>','',html.split('<div class="nx-units">',1)[1])
    if k=='chapter': return '<div class="lt-chapter"><span>CHAPTER 01 → CHAPTER 02</span><h4>目的</h4><div><p>を、言葉にする。</p><i aria-hidden="true">→</i><p>を、AIと共有する。</p></div></div>'
    if k=='marquee': return '<div class="lt-keywords">'+''.join('<span>'+e(x)+'</span>' for x in ['比較','流れ','構造','数量','目的','材料','判断','記録'])+'</div>'
    if k=='split': return pairs([('図版','関係・順番・割合を、一目で伝える。比較や工程のつながりを見せたいときに。'),('本文パーツ','言葉の意味や根拠を、まとまりで伝える。説明の長さに合わせて自然に並べたいときに。')])
    if k=='faq': return pairs([('図版と本文パーツ、どちらを使う？','関係を見せるなら図版。説明を読み進めるなら本文パーツ。同じ面に詰め込まず、伝えたいことから選びます。'),('静止画でも、伝わる？','比較の両側、工程の全段階、数字の前提を同じ面に置きます。動きが止まっても、意味と結論は残ります。')],'lt-rows')
    # Noninteractive blocks keep their original semantics and example content.
    html=re.sub(r'(<b data-to="(\d+)">)0',lambda m:m[1]+format(int(m[2]),','),html)
    html=html.replace('oz-press','').replace('data-count','data-static-count')
    html=html.replace('押すと、もう一度回ります','数字・単位・何を数えた値かを、ひとまとまりで見せます。')
    html=html.replace('17個は多いように見えますが、','それぞれのパーツは、')
    html=html.replace('印は線を2本引いて作ります。書体に左右されません','条件を満たす項目と、整える必要がある項目を分けて示します。')
    if k=='counter': html=html.replace('>30<','>34<').replace('>24<','>33<').replace('図版の作図関数','便覧の図版').replace('本文ブロック','便覧の本文パーツ')
    if k=='statgrid': html=html.replace('>30<','>34<').replace('図版の作図関数','便覧の図版')
    return html

def dimensions(args):
    shapes=[
      '<circle cx="100" cy="62" r="5" fill="currentColor"/>',
      '<path d="M35 62 H165"/><circle cx="35" cy="62" r="3"/><circle cx="165" cy="62" r="3"/>',
      '<path d="M30 83 L70 43 L125 83 L168 43"/><circle cx="30" cy="83" r="4"/><circle cx="70" cy="43" r="4"/><circle cx="125" cy="83" r="4"/><circle cx="168" cy="43" r="4"/>',
      '<path d="M35 31 H165 V96 H35 Z"/><path d="M35 31 L165 96 M165 31 L35 96" opacity=".3"/>',
      '<path d="M100 8 L153 37 V96 L100 125 L47 96 V37 Z M47 37 L100 66 L153 37 M100 66 V125"/>'
    ]
    names=['点 / 単発','線 / 前提','連鎖 / 手順','面 / 目的','立体 / 協働']
    return '<div class="lt-dimensions">'+''.join('<div><span>0%d</span><svg viewBox="0 0 200 140" aria-hidden="true">%s</svg><h4>%s</h4><strong>%s</strong><p>%s</p></div>'%(i+1,art,names[i],e(args['steps'][i][2]),e(args['steps'][i][4])) for i,art in enumerate(shapes))+'</div><p class="lt-dim-axis">人が使う <span aria-hidden="true">⟶</span> 目的を任せる</p>'

def new_figure(k):
    if k=='cutaway':
        rows=[('目的','何を実現するか'),('計画','どう進めるか'),('モデル','推論と生成を担う'),('知識','参照する材料'),('道具','外部へ働きかける'),('評価','結果を確かめる')]
        art=''
        for i,(h,p) in enumerate(rows):
            y=25+i*55
            art+=f'<g class="lt-plane"><path d="M40 {y+20} L130 {y} L280 {y+35} L190 {y+60} Z"/><path d="M280 {y+35} H330" class="lt-leader"/><text x="345" y="{y+35}">{h}</text><text class="lt-plane-note" x="345" y="{y+55}">{p}</text></g>'
        return '<div class="lt-cutaway"><svg viewBox="0 0 610 380" role="img" aria-label="AIエージェントの6つの役割：目的、計画、モデル、知識、道具、評価">'+art+'</svg><p>モデルを中心に、<br><strong>目的・知識・道具・評価が支える。</strong></p></div>'
    if k=='rebuild': return '<div class="lt-rebuild"><p class="lt-job">見積り・提案書を作る</p><p class="lt-note">仕事を6つの動詞へ分解し、担当を決める</p>'+pairs([('AIが担う','<div class="lt-task-lane">'+''.join('<span><b>%02d</b>%s</span>'%(i+1,v) for i,v in enumerate(['調査','要約','構成','草案']))+'</div>'),('人が担う','<div class="lt-task-lane">'+''.join('<span><b>%02d</b>%s</span>'%(i+5,v) for i,v in enumerate(['判断','合意']))+'</div>')])+'<p class="lt-flowline">調査 → 要約 → 構成 → 草案 → 判断 → 合意</p></div>'
    if k=='gate': return '<div class="lt-gate"><div><span>依頼</span><h4>条件と照合する</h4><p>事前に合意した<br>範囲・上限・権限</p></div><div class="lt-gate-line" aria-hidden="true"><i></i></div>'+pairs([('合意した範囲内','<strong>実行へ進む</strong>'),('上限を超える','<strong>人の承認を待つ</strong>')],'lt-rows')+'</div>'
    if k=='waiting':
        labels=['調査','草案','承認待ち','確認'];out='<div class="lt-waiting">'
        for h,values in [('従来',[6,8,12,4]),('草案が4倍の速度',[6,2,12,4])]:
            out+='<div class="lt-wait-row"><h4>'+h+'<b>'+str(sum(values))+'<small>時間</small></b></h4><div class="lt-timebar">'+''.join(f'<span style="--width:{v/30*100}%;--seg:{i}"><b>{v}h</b></span>' for i,v in enumerate(values))+'</div></div>'
        return out+'<div class="lt-timeaxis"><span>0</span><span>10</span><span>20</span><span>30時間</span></div><div class="lt-legend">'+''.join(f'<span style="--seg:{i}"><i></i>{name}</span>' for i,name in enumerate(labels))+'</div><p class="lt-wait-conclusion">草案 <b>8 → 2</b> 時間。<br>承認待ちは <b>12</b> 時間のまま。</p></div>'
    raise ValueError(k)

def build(figures, parts, catalog, blocks, categories, base_style, keynav, assets, mini):
    parts.update({k:{'html':v} for k,v in next_parts().items()})
    figurecards=[];index=[]
    for i,item in enumerate(catalog):
        k=item['id']
        content=dimensions(figures['fig_dims']['args']) if k=='dims' else scene(k,figures['fig_'+k]['args']) if 'fig_'+k in figures else new_figure(k)
        best=item['best'].replace('一つの形の変化で伝える','形の違いで見渡す')
        figurecards.append(f'<article class="lt-figure" id="figure-{k}" data-ambient-zone><header><span>{i+1:02} / {e(categories[item["category"]])}</span><h3>{e(item["name"])}</h3><p>{e(item["purpose"])}</p></header><div class="tl-canvas"><div class="lab-scene scene-{k}">{content}</div></div><footer><p><b>向いている場面</b>{e(best)}</p><p><b>使うときの注意</b>{e(item["caution"])}</p></footer></article>')
        index.append(f'<a href="#figure-{k}" class="lt-index-item">{mini(k)}<span>{i+1:02}</span><b>{e(item["name"])}</b></a>')
    partcards=[]
    for i,(k,meta) in enumerate(blocks.items()):
        name,purpose,group=PART_LABELS.get(k,meta)
        html=static_part(k,parts[k]).replace(' data-reveal', '')
        assert not re.search(r'<(?:button|input|select|details)\b|role="(?:button|tab)"',html), k
        partcards.append(f'<article class="tl-part" id="part-{k}" data-part="{k}" data-ambient-zone><header><span>{i+1:02} / {e(group)}</span><h3>{e(name)}</h3><p>{e(purpose)}</p></header><div class="tl-part-example">{html}</div></article>')
    guide=[('一つの面に、一つの主張。','導入で問いを置き、図で理解し、短い補足で結論を持ち帰る。話の単位で面を分けます。'),
       ('すべてを、最初から。','説明・比較・答えを開閉や切り替えの裏に置きません。静止した一枚で意味が通る構成にします。'),
       ('動くのは、視線の道筋。','光、接続線、背景にゆっくりした動きを添えます。単位・ラベル・出典は動かさず、読む時間を確保します。'),
       ('画面から、そのまま紙へ。','印刷では動きを止め、図版・本文パーツごとに改ページ。必要な内容が欠けない完成形を残します。'),
       ('書体と色に、役割を。','見出しは明朝、本文はゴシック、数字は欧文書体。紺・紙色・青を軸に、注意と区分にだけ差し色を使います。'),
       ('小さくする前に、組み替える。','小さな画面では比較を縦へ、表を行ごとのカードへ。文字を縮めすぎず、読む順番を保ちます。')]
    styles='\n'.join((assets/n).read_text() for n in ['style.css','atmosphere.css','next.css','lecture.css'])
    return f'''<!DOCTYPE html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>テンプレート便覧 — 講演と印刷に、伝わる形を。 | おざけん</title><meta name="description" content="34の図版と33の本文パーツ。完成形を見渡せる、講演と印刷のためのテンプレート便覧。"><link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Hanken+Grotesk:wght@400;500;600;700&family=Shippori+Mincho+B1:wght@400;500;600&family=Zen+Kaku+Gothic+New:wght@400;500;700&display=swap" rel="stylesheet">{base_style}<style>{styles}</style></head>
<body class="tl-body tl-lecture"><div class="tl-atmosphere" aria-hidden="true"><i></i><i></i></div><header class="tl-header"><a class="tl-brand" href="index.html">OZAKEN<span>DESIGN LIBRARY</span></a><nav class="lt-nav" aria-label="便覧の目次"><a href="#figures">図版 34</a><a href="#parts">本文パーツ 33</a><a href="#guide">設計ガイド</a></nav><a class="tl-back" href="index.html">資料アーカイブ ↗</a></header>
<main><div class="tl-hero" data-ambient-zone><div class="tl-hero-copy"><span class="tl-eyebrow">OZAKEN TEMPLATE COLLECTION / LECTURE EDITION</span><h1><span><b>伝わる資料に、</b></span><span><b><em>動きを。</em></b></span></h1><p>言葉も、数字も、物語も。<br>一枚で届く。動きで、心に残る。</p><a href="#figures" class="tl-hero-link">テンプレートを見る <span>↓</span></a></div><div class="tl-hero-art" aria-hidden="true">{curtain()}<span class="tl-hero-art-caption">WORDS INTO EXPERIENCE</span></div><div class="tl-hero-bottom"><span>言葉が届く。理解が、つながる。</span><span>34 FIGURES ／ 33 BUILDING BLOCKS</span></div></div>
<div class="tl-shell"><section id="figures"><div class="lt-section-heading"><span class="tl-eyebrow">01 / FIGURES</span><h2>何を、伝えたい？</h2><p>比較、流れ、構造、数量。伝える内容から、形を見つける。</p></div><nav class="lt-index" aria-label="図版の目次">{''.join(index)}</nav><p class="lt-library-note">図と数値は構造を示すための見本です。実際の資料では、文言・数値・出典を内容に合わせます。</p><div class="lt-figure-list">{''.join(figurecards)}</div></section>
<section id="parts"><div class="lt-section-heading"><span class="tl-eyebrow">02 / WORDS & NUMBERS</span><h2>図のまわりにも、<br>伝わる形を。</h2><p>数字をつかむ。言葉を届ける。理由まで見渡す。</p></div><div class="tl-part-grid">{''.join(partcards)}</div></section>
<section id="guide"><div class="lt-section-heading"><span class="tl-eyebrow">03 / DESIGN NOTES</span><h2>見せる形と、<br>持ち帰る形を、ひとつに。</h2></div><div class="tl-guide-grid">{''.join(f'<article><span>0{i+1}</span><h3>{h}</h3><p>{t}</p></article>' for i,(h,t) in enumerate(guide))}</div></section></div></main>
<footer class="tl-footer"><div><b>OZAKEN</b><span>型があるから、伝えることに時間を使える。</span></div><a href="index.html">資料アーカイブに戻る ↗</a></footer>{keynav}<script>{(assets/'lecture.js').read_text()}</script></body></html>'''
