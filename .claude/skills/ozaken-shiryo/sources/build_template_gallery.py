#!/usr/bin/env python3
# coding: utf-8
"""Build only the template catalogue. --publish preserves its existing lockbox keys.

python3 build_template_gallery.py --preview /absolute/work/preview/template.html
OZAKEN_PW=... python3 build_template_gallery.py --publish

gen_template.py remains the ordinary article skeleton. Its real function calls
supply examples here. The catalogue is an interactive tool, so article-only
section/CTA checks do not apply; shared colour/font and SVG checks still apply.
No other material, registry, profile, or shared renderer is written.
"""
from pathlib import Path
import argparse, functools, inspect, json, os, re, runpy, sys
HERE=Path(__file__).resolve().parent
SCRIPTS=HERE.parent/'scripts';sys.path.insert(0,str(SCRIPTS))
from template_gallery.catalog import CATALOG,CATEGORIES,BLOCKS
from template_gallery.scenes import scene,e
import domain_fig,blocks,build_page
# The shared keynav module requires an environment variable at import time, even
# though its JS export never reads a key or touches encrypted files.
_keynav_preview = "OZAKEN_PW" not in os.environ
if _keynav_preview: os.environ["OZAKEN_PW"] = "template-preview"
import apply_keynav
if _keynav_preview: os.environ.pop("OZAKEN_PW")

def examples():
    figures={};parts={};originals=[]
    def wrap(mod,name,store):
        fn=getattr(mod,name);originals.append((mod,name,fn))
        signature_fn=inspect.getclosurevars(fn).nonlocals.get('fn',fn) if mod is domain_fig else fn
        @functools.wraps(fn)
        def call(*args,**kwargs):
            bound=inspect.signature(signature_fn).bind(*args,**kwargs);bound.apply_defaults()
            data=dict(bound.arguments);html=fn(*args,**kwargs)
            if mod is blocks or name in data.get('title',''):
                if name not in store: store[name]={'args':data,'html':html}
            return html
        setattr(mod,name,call)
    try:
        for item in CATALOG:wrap(domain_fig,'fig_'+item['id'],figures)
        for key in BLOCKS:wrap(blocks,key,parts)
        runpy.run_path(str(HERE/'gen_template.py'),run_name='template_examples')
    finally:
        for mod,name,fn in originals:setattr(mod,name,fn)
    assert len(figures)==30,figures.keys()
    assert len(parts)==24,parts.keys()
    return figures,parts

def mini(kind):
    # Deliberately text-free silhouettes: labels stay readable outside thumbnails.
    def rect(x,y,w,h,c=''):
        return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="3" class="{c}"/>'
    def line(d,c=''):return f'<path d="{d}" class="{c}"/>'
    if kind=='dims':art=line('M100 10 135 30 135 68 100 88 65 68 65 30 Z M65 30 100 50 135 30 M100 50 V88')+line('M25 50 H50 M148 50 H177','faint')
    elif kind in ('cycle','issues','loop4'):
        art='<circle cx="100" cy="50" r="32"/>'+''.join(rect(x,y,22,14,'filled' if i==1 else '') for i,(x,y) in enumerate([(89,11),(123,43),(89,75),(55,43)]))
    elif kind in ('tree','kpi'):
        art=line('M100 25 V45 M45 45 H155 M45 45 V66 M100 45 V66 M155 45 V66')+rect(80,10,40,17,'filled')+''.join(rect(x,65,36,20) for x in [27,82,137])
    elif kind in ('pyramid','context'):
        art=''.join(rect(100-w/2,12+i*27,w,20,'filled' if i==0 else '') for i,w in enumerate([58,94,134]))
    elif kind=='waterline':
        art=''.join(rect(35,10+i*27,130,22) for i in range(3))+line('M25 47 Q50 37 75 47 T125 47 T175 47','accent')
    elif kind in ('bars','ranges','orgs'):
        art=''.join(rect(30,12+i*26,w,15,'filled' if i==1 else '') for i,w in enumerate([135,88,48]))+line('M25 7 V92','faint')
    elif kind=='donut':art='<circle cx="100" cy="50" r="33" stroke-width="15"/><circle cx="100" cy="50" r="33" stroke-width="15" stroke-dasharray="84 124" class="accent"/>'
    elif kind=='stack':art=''.join(rect(30+i*45,22+j*34,40,23,'filled' if i==j else '') for j in range(2) for i in range(3))
    elif kind in ('stairs','ladder','timeline'):
        art=line('M22 80 H67 V57 H112 V34 H160 V15')+''.join(rect(25+i*45,50-i*20,30,18,'filled' if i==2 else '') for i in range(3))
    elif kind in ('flow','roles','cols','stats'):
        art=line('M35 50 H165','faint')+''.join(rect(18+i*58,27,45,46,'filled' if i==1 else '') for i in range(3))
    elif kind in ('quad','map','katagata'):
        art=line('M100 8 V92 M18 50 H182','faint')+''.join(rect(x,y,55,28,'filled' if i==1 else '') for i,(x,y) in enumerate([(34,14),(112,14),(34,59),(112,59)]))
    elif kind in ('sheet','matrix','check'):
        art=''.join(rect(28+i*49,12+j*27,43,20,'filled' if i==1 and j==1 else '') for j in range(3) for i in range(3))
    else:
        art=''.join(rect(x,17+j*38,60,25,'filled' if x==114 else '') for j in range(2) for x in [26,114])+line('M90 49 H110')
    return f'<svg viewBox="0 0 200 100" class="tl-mini" aria-hidden="true">{art}</svg>'

def build():
    figures,parts=examples()
    style=(HERE/'template_gallery/style.css').read_text();runtime=(HERE/'template_gallery/runtime.js').read_text()
    cards=[];templates=[]
    for i,item in enumerate(CATALOG):
        k=item['id'];rendered=scene(k,figures['fig_'+k]['args'])
        templates.append(f'<template id="scene-{k}"><div class="lab-scene scene-{k}">{rendered}</div></template>')
        cards.append(f'''<button type="button" class="tl-card" data-select="{k}" data-category="{item['category']}">
<span class="tl-card-top"><span>{i+1:02} / {e(CATEGORIES[item['category']])}</span><span aria-hidden="true">↗</span></span>
<div class="tl-card-art">{mini(k)}</div><h3>{e(item['name'])}</h3><p>{e(item['purpose'])}</p><span class="tl-card-link">動きを試す <span aria-hidden="true">→</span></span></button>''')
    partcards=[]
    for i,(k,(name,purpose,group)) in enumerate(BLOCKS.items()):
        html=parts[k]['html']
        if k=='poll':
            html=html.replace('手順を決めて渡し、AIが順に実行して結果を返す','目的と制約を渡し、AIが手順を組み立てて実行・確認する').replace('手順をAI自身が回している','手順の組み立てと実行・確認をAIが担っている')
        if k=='flip':
            html=html.replace('いちばん先に見るべき条件はどれでしょうか。','候補を見つける手がかりの一つは何でしょうか。').replace('難しさでも、時間の長さでもありません。','回数だけで決めず、確認のしやすさや失敗時の影響も見ます。').replace('効きが大きく、失敗しても取り返しがつきます。','効果を積み重ねられます。')
        if k=='accordion':
            html=blocks.accordion([
                ('図版と本文パーツは、どう使い分けますか','<p>関係・順番・割合を一目で伝えるなら図版。文章を読み進める、詳しく開く、その場で試すなら本文パーツが向いています。</p>'),
                ('動きを止めて、説明できますか','<p>図版は再生・一時停止・段階送りに対応しています。段階の札を押すと、その状態を止めて見せられます。「全体を見る」で完成形に戻れます。</p>'),
                ('スマートフォンでも見られますか','<p>小さな画面では、表をカードに、長い比較を縦並びに組み替えます。端末の「動きを減らす」設定にも対応しています。</p>')
            ],note='読み手が必要な情報を開くための見本です。')
        # Counter is readable in print/no-JS; runtime can still replay it.
        html=re.sub(r'(<b data-to="(\d+)">)0',lambda m:m[1]+format(int(m[2]),','),html)
        partcards.append(f'<article class="tl-part" data-part="{k}" data-part-group="{group}"><header><span>{i+1:02} / {e(group)}</span><h3>{e(name)}</h3><p>{e(purpose)}</p></header><div class="tl-part-example">{html}</div><footer><code>{k}()</code><button type="button" data-replay-part aria-label="{e(name)}を再生">再生 ↻</button></footer></article>')
    guide='''<div class="tl-guide-intro"><span class="tl-eyebrow">DESIGN NOTES</span><h2>形を整える。<br>伝えることに、集中する。</h2><p>色・書体・余白・動きに共通の役割を持たせる。<br>図が変わっても、読み方は迷わせない。</p></div>
<div class="tl-guide-grid"><article><span>01 / COMPOSITION</span><h3>一つの面に、一つの主張。</h3><div class="tl-page-demo"><i>主張</i><b>図版</b><span>補足　／　補足　／　補足</span></div><p>導入で問いを置き、図で理解し、短い補足で結論を持ち帰る。図を詰め込むより、話の単位で面を分けます。</p></article>
<article><span>02 / CONTRAST</span><h3>明るい面と、濃い面。</h3><div class="tl-tone-demo"><i>表紙</i><i>本文</i><i>本文</i><i>締め</i></div><p>通常の資料は、表紙 → 明暗の交互 → 濃い締め。色の切り替わりを、話の切り替わりと揃えます。</p></article>
<article><span>03 / TYPOGRAPHY</span><h3>書体に、役割を持たせる。</h3><div class="tl-type-demo"><b>伝わる。</b><span>本文は、素直に読みやすく。</span><i>0123456789</i></div><p>見出しは明朝、本文はゴシック、数字と英字は欧文書体。文字の役割を形の違いで伝えます。</p></article>
<article><span>04 / COLOUR</span><h3>色を、意味のために使う。</h3><div class="tl-swatches"><i style="--sw:#141d35">地</i><i style="--sw:#2e5496">基準</i><i style="--sw:#2f8f8a">達成</i><i style="--sw:#e23744">注意</i></div><p>紺・紙色・青を軸に、赤と青緑を要点へ。数字の内訳には凡例を添え、色だけで意味を伝えません。</p></article>
<article><span>05 / MOTION</span><h3>動きは、説明の順番。</h3><div class="tl-motion-demo"><i></i><span></span><i></i><span></span><i></i></div><p>最初は完成形を見せ、必要に応じて再生。話し手は途中で止め、段階を選び、何度でも見せ直せます。</p></article>
<article><span>06 / LEGIBILITY</span><h3>小さくする前に、組み替える。</h3><div class="tl-size-demo"><i>図</i><span>図<br>説明<br>補足</span></div><p>スマートフォンでは表をカードへ、比較を縦へ。単位・ラベル・出典は動かさず、読む時間を確保します。</p></article></div>
<details class="tl-maker"><summary>作り手向け：生成と運用</summary><p>この便覧は、既存の30図版・24本文ブロックの呼び出し例を読み取り、便覧専用の表示と動きを組み立てています。今回のデザイン変更はテンプレートだけに適用しています。</p><pre>python3 .claude/skills/ozaken-shiryo/sources/build_template_gallery.py --preview /absolute/work/template.html</pre><p>本番の再生成は環境変数 OZAKEN_PW を設定して --publish。既存の暗号鍵を維持し、template.html だけを更新します。既存の個別資料と、共有の描画関数には新しい演出を適用しません。</p></details>'''
    default=next(x for x in CATALOG if x['id']=='dims')
    catalogue_json=json.dumps(CATALOG,ensure_ascii=False).replace('<','\\u003c')
    block_runtime=build_page.TAIL[build_page.TAIL.index('<script>\n/* ══ 押せる部品'):]
    html=f'''<!DOCTYPE html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>テンプレート便覧 — 伝わる図に、動きを。 | おざけん</title><meta name="description" content="30種類の図版と24種類の本文パーツ。用途から選び、動きと説明の順番を試せるテンプレート便覧。"><link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Hanken+Grotesk:wght@400;500;600;700&family=Shippori+Mincho+B1:wght@400;500;600&family=Zen+Kaku+Gothic+New:wght@400;500;700&display=swap" rel="stylesheet">{build_page.STYLE}<style>{style}</style></head>
<body class="tl-body"><a class="tl-skip" href="#tl-explorer">図版の操作へ移動</a><header class="tl-header"><a class="tl-brand" href="index.html">OZAKEN<span>DESIGN LIBRARY</span></a><nav class="tl-tabs" role="tablist" aria-label="便覧の表示"><button type="button" role="tab" id="tab-figures" aria-controls="panel-figures" aria-selected="true" data-panel="figures">図版 <span>30</span></button><button type="button" role="tab" id="tab-parts" aria-controls="panel-parts" aria-selected="false" tabindex="-1" data-panel="parts">本文パーツ <span>24</span></button><button type="button" role="tab" id="tab-guide" aria-controls="panel-guide" aria-selected="false" tabindex="-1" data-panel="guide">設計ガイド</button></nav><a class="tl-back" href="index.html">資料アーカイブ ↗</a></header>
<main id="tl-main"><section id="panel-figures" role="tabpanel" aria-labelledby="tab-figures"><div class="tl-hero"><div class="tl-hero-copy"><span class="tl-eyebrow">OZAKEN TEMPLATE COLLECTION / 2026</span><h1>伝わる図に、<br><em>動きを。</em></h1><p>比較する。つなぐ。ほどく。<br>伝えたいことから、図の形と動きを選ぶ。</p><a href="#tl-explorer" class="tl-hero-link">図版を試す <span>↓</span></a></div><div class="tl-hero-art" aria-hidden="true"><div class="hero-orbit orbit-a"></div><div class="hero-orbit orbit-b"></div><div class="hero-orbit orbit-c"></div><div class="hero-cube">{mini('dims')}</div><span class="hero-label label-a">FORM</span><span class="hero-label label-b">MEANING</span><span class="hero-label label-c">MOTION</span></div><div class="tl-hero-bottom"><span>形が変わる。理解が、つながる。</span><span>30 FIGURES <i>／</i> 24 BUILDING BLOCKS</span></div></div>
<div class="tl-shell"><div class="tl-section-head" id="tl-explorer"><div><span class="tl-eyebrow">01 / MOTION STUDIO</span><h2>動かして、伝わり方を試す。</h2></div><p>完成形から、説明の順番へ。</p></div><div id="tl-studio-anchor"></div><section class="tl-studio" aria-label="図版のプレビュー"><div class="tl-stage-top"><div><span id="tl-stage-category">流れを伝える</span><h3 id="tl-stage-title" tabindex="-1">次元の変化</h3></div><button type="button" id="tl-expand">大きく表示 ⤢</button></div><div class="tl-workspace"><div class="tl-canvas" id="tl-canvas" role="region" aria-label="図版の見本">{scene('dims',figures['fig_dims']['args'])}</div><aside class="tl-inspector"><span class="tl-eyebrow">WHAT IT TELLS</span><h4 id="tl-purpose">{e(default['purpose'])}</h4><div><span>向いている場面</span><p id="tl-best">{e(default['best'])}</p></div><div><span>使うときの注意</span><p id="tl-caution">{e(default['caution'])}</p></div><p class="tl-example-note">図は型を示すための見本です。実際の数値・出典・文言に置き換えて使います。</p></aside></div><div class="tl-player"><div class="tl-controls"><button type="button" id="tl-play" class="tl-primary">▶ 再生</button><button type="button" id="tl-replay" aria-label="最初から再生">↻ 最初から</button><button type="button" id="tl-next">次の段階 →</button><button type="button" id="tl-all">全体を見る</button><label class="tl-speed">速度<select id="tl-speed" aria-label="再生速度"><option value="0.7">ゆっくり</option><option value="1" selected>標準</option><option value="1.4">速く</option></select></label></div><label class="tl-range-label" for="tl-progress">再生位置 <span id="tl-time">完成形</span></label><input type="range" id="tl-progress" min="0" max="1000" value="1000" aria-label="再生位置"><div class="tl-beats" id="tl-beats" aria-label="説明の段階"></div><p class="tl-caption" id="tl-caption" aria-live="polite">完成形を表示しています。再生すると、説明の順に変化します。</p></div></section>
<div class="tl-section-head tl-catalog-head" id="tl-catalog"><div><span class="tl-eyebrow">02 / FIND YOUR FORM</span><h2>何を、伝えたい？</h2></div><label class="tl-search"><span>図版を検索</span><input id="tl-search" type="search" placeholder="例：比較、手順、比率" autocomplete="off"></label></div><div class="tl-filterbar"><div class="tl-filters" role="group" aria-label="図版の用途"><button type="button" data-filter="all" aria-pressed="true">すべて <span>30</span></button>{''.join(f'<button type="button" data-filter="{k}" aria-pressed="false">{v} <span>{sum(x["category"]==k for x in CATALOG)}</span></button>' for k,v in CATEGORIES.items())}</div><span id="tl-results" role="status">30種類</span></div><div class="tl-catalog-grid">{''.join(cards)}</div><p id="tl-empty" hidden>一致する図版がありません。別の言葉で探してみてください。</p></div></section>
<section id="panel-parts" role="tabpanel" aria-labelledby="tab-parts" hidden><div class="tl-shell"><div class="tl-parts-intro"><span class="tl-eyebrow">BUILDING BLOCKS / 17 + 7</span><h2>図のまわりにも、<br>伝わる形を。</h2><p>数字・ことば・構成・強調の17種類と、触って試せる7種類。<br>本文の役割に合わせて選ぶ、24のパーツ。</p></div><div class="tl-part-filters" role="group" aria-label="本文パーツの用途">{''.join(f'<button type="button" data-part-filter="{v}" aria-pressed="{str(i==0).lower()}">{v}</button>' for i,v in enumerate(['すべて','数字','ことば','構成','強調','操作']))}</div><div class="tl-part-grid">{''.join(partcards)}</div></div></section>
<section id="panel-guide" role="tabpanel" aria-labelledby="tab-guide" hidden><div class="tl-shell">{guide}</div></section></main>
<footer class="tl-footer"><div><b>OZAKEN</b><span>型があるから、伝えることに時間を使える。</span></div><a href="index.html">資料アーカイブに戻る ↗</a></footer><dialog id="tl-dialog" aria-label="図版を大きく表示"><form method="dialog"><button class="tl-dialog-close" aria-label="拡大表示を閉じる">閉じる ×</button></form><div id="tl-dialog-mount"></div></dialog>{''.join(templates)}<script type="application/json" id="tl-data">{catalogue_json}</script>
{block_runtime}{apply_keynav.JS}<script>{runtime}</script></body></html>'''
    # The catalogue has its own accessible controls and layout. Shared tokens still apply.
    errors=build_page.check_tokens(html)
    if errors:raise ValueError(errors)
    return html

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--preview',type=Path);ap.add_argument('--publish',action='store_true');args=ap.parse_args()
    page=build()
    if args.preview:
        args.preview.parent.mkdir(parents=True,exist_ok=True);args.preview.write_text(page)
        print('Preview written:',args.preview)
    if args.publish:
        import lockbox,oz_root
        pw=os.environ.get('OZAKEN_PW')
        if not pw:raise SystemExit('Set OZAKEN_PW before publishing.')
        target=Path(oz_root.root(str(HERE)))/'template.html'
        before=lockbox.parse(target.read_text()).group('w')
        lockbox.encrypt(str(target),pw,page)
        assert lockbox.parse(target.read_text()).group('w')==before
        assert lockbox.decrypt(str(target),pw)==page
        print('Updated template.html; existing keys preserved.')
    if not args.preview and not args.publish:ap.error('Choose --preview or --publish')
if __name__=='__main__':main()
