"""Semantic, responsive scenes used only by template.html."""
from html import escape
import math

def e(x): return escape(str(x), quote=True)
def motion(beat=0,kind='rise'): return f'data-beat="{beat}" data-motion="{kind}"'
def node(title,sub='',beat=0,kind='rise',extra='',cls=''):
    return f'<div class="lab-node {cls}" {motion(beat,kind)} {extra}><strong>{e(title)}</strong>{f"<p>{e(sub)}</p>" if sub else ""}</div>'
def grid(items,cls=''): return f'<div class="lab-grid {cls}">{"".join(items)}</div>'
def path(d,beat=0,cls='',travel=False):
    return f'<path d="{d}" pathLength="1" class="lab-line {cls}" {motion(beat,"draw")}/>'+(f'<circle r="1.3" class="lab-packet" data-travel="{e(d)}" data-beat="{beat}"/>' if travel else '')
def svg(content,view='0 0 100 100',cls='lab-wires'):
    fit = 'none' if cls in ('lab-wires', 'lab-branches') else 'xMidYMid meet'
    return f'<svg viewBox="{view}" preserveAspectRatio="{fit}" class="{cls}" aria-hidden="true">{content}</svg>'
def head(label): return f'<p class="lab-axis-label">{e(label)}</p>'
def tree(a,kpi=False):
    top=a['top'] if kpi else a['root'];branches=a['branches'];n=len(branches)
    roots=node(top,beat=0,cls='lab-tree-root')
    wires=svg(''.join(path(f'M50 0 V26 H{(i+.5)*100/n} V100',1) for i in range(n)),cls='lab-branches')
    return '<div class="lab-tree">'+roots+wires+grid([f'<div class="lab-branch">{node(h,beat=1)}<span class="lab-stem" {motion(2,"growy")}></span>'+''.join(node(v,beat=2,cls='lab-leaf') for v in rows)+'</div>' for h,rows in branches],f'cols-{n}')+'</div>'
def circular(items,center,kind):
    n=len(items);parts=[]
    for i,item in enumerate(items):
        angle=-math.pi/2+i*2*math.pi/n
        x=50+34*math.cos(angle);y=50+34*math.sin(angle)
        parts.append(node(item[0],item[1],i,extra=f'style="--x:{x}%;--y:{y}%"',cls='lab-orbit-node'))
    route='M50 16 A34 34 0 1 1 49.99 16'
    return '<div class="lab-orbit">'+svg(path(route,0,travel=True))+''.join(parts)+f'<div class="lab-orbit-center">{e(center)}<small>{"IMPROVE" if kind=="cycle" else "CONNECTION"}</small></div></div>'
def scene(kind,a):
    if kind=='gap':
        pairs=a['pairs'];out=head(a.get('left_label','いま')+' → '+a.get('right_label','これから'))
        for i,(left,right) in enumerate(pairs):
            origin = f'data-from=".gap-source-{i}"'
            out+=f'<div class="lab-pair">{node(left,beat=0,cls=f"gap-source-{i} lab-before")}<span class="lab-arrow" {motion(1,"growx")}>→</span>{node(right,beat=i+1,kind="transfer",extra=origin,cls="lab-after")}</div>'
        return out
    if kind=='sides':
        return grid([f'<div class="lab-side"><h4>{e(a.get(label,""))}</h4>'+''.join(node(v,beat=i,kind='fromleft' if i==0 else 'fromright') for v in a[key])+'</div>' for i,(label,key) in enumerate([('left_label','lefts'),('right_label','rights')])], 'cols-2')
    if kind=='versus':
        return '<div class="lab-versus">'+grid([head('比較する観点'),node(*a['left'],beat=0),node(*a['right'],beat=0)],'cols-3')+''.join(f'<div class="lab-compare-row" {motion(i+1,"fromleft")}><h4>{e(row[0])}</h4><p>{e(row[1])}</p><p>{e(row[2])}</p></div>' for i,row in enumerate(a['rows']))+'</div>'
    if kind=='check':
        return '<div class="lab-checks">'+''.join(f'<div class="lab-check" {motion(i+1,"fromleft")}><b class="check-{str(ok).lower()}">{"○" if ok is True else "×" if ok is False else "−"}</b><div><strong>{e(h)}</strong><p>{e(t)}</p></div></div>' for i,(ok,h,t) in enumerate(a['items']))+'</div>'
    if kind=='matrix':
        return '<div class="lab-matrix" role="table" aria-label="条件ごとの判定"><div class="lab-matrix-row" role="row">'+head('条件')+''.join(f'<b role="columnheader">{e(c)}</b>' for c in a['cols'])+'</div>'+''.join('<div class="lab-matrix-row" role="row">'+f'<strong role="rowheader">{e(h)}</strong>'+''.join(f'<span role="cell" class="lab-verdict verdict-{e(v)}" {motion(j+1,"scale")}>{e(v)}</span>' for j,v in enumerate(vals))+'</div>' for h,vals in a['rows'])+'<p class="lab-footnote">○ 適用可能　△ 条件付き　× 適用不可</p></div>'
    if kind=='quad':
        x=a['xpoles'];y=a['ypoles']
        cells=''.join(node(c[0],c[1],2 if c[2]==0 else 1,kind='scale',cls='lab-quad-cell'+(' lab-priority' if c[2]==0 else '')) for c in a['cells'])
        return f'<div class="lab-quadrant"><p class="axis-top">{e(a["ylab"])}：{e(y[1])}</p>{grid([cells],"quad-cells")}<p class="axis-bottom">{e(y[0])}</p><div class="axis-x"><span>{e(x[0])}</span><b>{e(a["xlab"])}</b><span>{e(x[1])}</span></div></div>'
    if kind=='katagata':
        cells=[('ビルダー',['AIエージェントの技術的な高い知見','組織変革／業務変革の視点も必要（現場に入る技術者に近い）','業務の理解は浅い／限定的']),('AIエージェント・アーキテクト',['自分のロジックをAIに落とし込み、設計・構築できる','AIエージェントの思考の道筋を誘導できる','会社の理念や文化まで理解している','高い言語化力を持っている']),('オペレーター',['AIエージェントで定型業務を行う','作る指示は具体さに欠けがち','単純な検索や文章作成に利用','AIの力を限定的にしか引き出せない']),('プロフェッショナル',['豊富な業務知識と地頭でAIを高度に使う','個人の業務効率・思考力を最大化','仕組み化の技がなく、効果は属人的','抜本的な変革は生み出せない'])]
        return '<div class="lab-katagata">'+head('↑ AIエージェントをつくる ／ ↓ AIエージェントをつかう')+grid([f'<div class="lab-node kg-{i}" {motion(3 if i==1 else 0,"scale")}><strong>{e(h)}</strong><ul>'+''.join(f'<li>{e(t)}</li>' for t in rows)+'</ul></div>' for i,(h,rows) in enumerate(cells)],'cols-2')+f'<div class="lab-pathways"><span {motion(1,"fromleft")}>プロフェッショナル → <b>生成AI教育</b> → アーキテクト</span><span {motion(2,"fromleft")}>オペレーター → <b>型の提供</b> → アーキテクト</span></div>'+head('← 業務知識 少ない ／ 業務知識 多い →')+'</div>'
    if kind=='map':
        pts=a['points'];inner=svg(path('M12 87 C33 87 54 87 64 86 S84 62 88 15',1,travel=True))
        for i,(h,x,y,*rest) in enumerate(pts):
            px=12+x*.8;py=87-y*.8
            inner+=f'<div class="lab-map-point" style="left:{px}%;top:{py}%" {motion(i+1,"scale")}><i></i><strong>{e(h)}</strong></div>'
        return f'<div class="lab-map"><p class="lab-map-y">{e(a["ylab"])} ↑</p>{inner}<p class="lab-map-x">{e(a["xlab"])} →</p></div>'
    if kind=='ladder':
        return '<div class="lab-ladder">'+''.join(f'<div class="lab-rung" {motion(i,"fromleft")}><b>{i+1:02}</b><div><strong>{e(h)}</strong><p>{e(t)}</p></div><i>↓</i></div>' for i,(h,t) in enumerate(a['items']))+'</div>'
    if kind in ('flow','roles'):
        items=a['steps'] if kind=='flow' else list(zip(['決める人','組む人','回す人'],a['who']))
        return '<div class="lab-process">'+grid([node(h,t,i,extra=f'data-station="{i}"',cls='lab-process-node') for i,(h,t) in enumerate(items)],'cols-3')+'<div class="lab-transfer-track">'+svg(path('M16 50 H84',0,travel=True),view='0 0 100 100')+'<span>対象を受け渡す</span></div>'+('' if kind=='flow' else '<p class="lab-footnote">方針・投資 → データ・権限・設計 → 運用・判断の記録</p>')+'</div>'
    if kind=='stairs':
        return '<div class="lab-stairs">'+''.join(f'<div class="lab-stair" style="--height:{(i+1)*22+12}%"><div {motion(i,"rise")}><span>{e(row[0])}</span><h4>{e(row[2])}</h4><p>{e(row[3])}</p><small>{e(row[4])}</small></div><i {motion(i,"growy")}></i></div>' for i,row in enumerate(a['steps']))+'</div>'
    if kind=='dims':
        return '<div class="lab-dimensions"><div class="lab-dimension-art">'+svg('<g data-dimension=""><polygon class="dimension-face"/><polyline class="dimension-wire"/><polyline class="dimension-inner"/></g>','0 0 600 250','dimension-svg')+'<span class="dimension-label" data-dimension-label>立体 / 協働</span></div>'+grid([f'<div class="lab-dim-step" data-beat="{i}"><span>0{i+1}</span><strong>{e(s[2])}</strong><p>{e(s[4])}</p></div>' for i,s in enumerate(a['steps'])],'cols-5')+'<div class="lab-dim-bands"><span>人が使う</span><span>目的を任せる</span></div></div>'
    if kind=='ranges':
        labels=a['phases'];n=len(labels)
        return '<div class="lab-ranges">'+grid([head(v) for v in labels],'cols-3')+''.join(f'<div class="lab-range-row"><strong>{e(h)}</strong><div class="lab-range-track"><i style="left:{start*100/n}%;width:{(end-start+1)*100/n}%" {motion(i+1,"growx")}></i><span>{e(note)}</span></div></div>' for i,(h,start,end,tone,note) in enumerate(a['rows']))+'</div>'
    if kind=='timeline':
        events=[('04.01','企画','対象を1つ選ぶ','範囲と目的を揃える'),('05.01','検証','小さく試す','結果から次の判断へ')]
        return '<div class="lab-timeline"><div class="lab-time-spine" '+motion(0,'growy')+'></div>'+''.join(f'<div class="lab-time-event" {motion(i+1,"fromleft")}><b>{date}</b><div><span>{team}</span><h4>{h}</h4><p>{sub}</p></div></div>' for i,(date,team,h,sub) in enumerate(events))+'<p class="lab-footnote">日付・出来事は構造を示すための架空の例</p></div>'
    if kind=='cycle':return circular(a['steps'],a.get('center','改善'),'cycle')
    if kind in ('context','pyramid'):
        rows=a['layers'];n=len(rows)
        return f'<div class="lab-layers {kind}">'+''.join(f'<div class="lab-layer" style="--layer:{i};--span:{60+i*20}%" {motion(n-1-i,"rise")}><span>0{n-i}</span><div><strong>{e(row[0])}</strong><p>{e(row[1])}</p></div></div>' for i,row in enumerate(rows))+'</div>'
    if kind in ('tree','kpi'):return tree(a,kind=='kpi')
    if kind in ('loop4','issues'):
        items=a['items'];cells=[]
        for i,item in enumerate(items):
            sub=(item[2]+' / '+'・'.join(item[3])) if kind=='loop4' else item[1]
            cells.append(node(item[0],sub,i,extra=f'style="order:{[0,1,3,2][i]}"',cls='lab-loop-node'))
        return '<div class="lab-loop">'+svg(path('M25 20 H75 V80 H25 V20',0,travel=True))+grid(cells,'cols-2')+'<span class="lab-loop-center">'+('知識の循環' if kind=='loop4' else '課題の連鎖')+'</span></div>'
    if kind=='waterline':
        return '<div class="lab-water"><div class="lab-water-fill" data-water></div><div class="lab-water-wave" data-water-wave></div>'+''.join(f'<div class="lab-water-row" data-beat="{2-i}"><b>{e(r[0])}</b><div><strong>{e(r[1])}</strong><p>{e(r[2])}</p></div><span>{e(r[3])}<small>{e(r[4])}</small></span></div>' for i,r in enumerate(a['layers']))+'<p class="lab-footnote">水位は分担の範囲を示す概念図</p></div>'
    if kind=='cols':
        return grid([f'<div class="lab-column" {motion(i,"rise")}><span>{e(row[0])}</span><h4>{e(row[1])}</h4><strong>{e(row[2])}</strong><p>{e(row[3])}</p></div>' for i,row in enumerate(a['items'])],'cols-3')
    if kind=='sheet':
        return '<div class="lab-sheet" role="table" aria-label="立場ごとの比較"><div class="lab-sheet-head" role="row">'+''.join(f'<b role="columnheader">{e(h)}</b>' for h in a['headers'])+'</div>'+''.join(f'<div class="lab-sheet-row" role="row" {motion(i+1,"fromleft")}>'+''.join(f'<div role="cell" data-label="{e(a["headers"][j])}">{e(c)}</div>' for j,c in enumerate(row))+'</div>' for i,row in enumerate(a['rows']))+'</div>'
    if kind=='bars':
        maximum=max(100,max(row[1] for row in a['items']))
        return '<div class="lab-bars"><div class="lab-bar-axis"><span>0</span><span>50</span><span>100%</span></div>'+''.join(f'<div class="lab-bar-row"><div><strong>{e(h)}</strong><b>{e(label)}</b></div><div class="lab-bar-track"><i style="width:{v/maximum*100}%" {motion(i+1,"growx")}></i></div><p>{e(note)}</p></div>' for i,(h,v,label,note,*_) in enumerate(a['items']))+'</div>'
    if kind=='stack':
        colors=['#2e5496','#2f8f8a','#9fc6f5'];out='<div class="lab-stacks">'
        for title,vals in a['rows']:
            total=sum(vals);out+=f'<h4>{e(title)}<span>合計 {total}%</span></h4><div class="lab-stack-track">'
            for i,v in enumerate(vals):out+=f'<div style="width:{v/total*100}%;--seg:{colors[i]}" {motion(i+1,"growy")}><b>{v}%</b></div>'
            out+='</div>'
        return out+'<div class="lab-legend">'+''.join(f'<span><i style="background:{colors[i]}"></i>{e(k)}</span>' for i,k in enumerate(a['keys']))+'</div></div>'
    if kind=='donut':
        total=sum(row[1] for row in a['items']);colors=['#2e5496','#2f8f8a','#9fc6f5'];offset=0;arcs=[];legend=[];circ=2*math.pi*78
        for i,(h,v,note) in enumerate(a['items']):
            length=v/total*circ
            arcs.append(f'<circle cx="120" cy="120" r="78" fill="none" stroke="{colors[i]}" stroke-width="30" stroke-dasharray="{length} {circ-length}" stroke-dashoffset="{-offset}" data-arc="{length}" data-circ="{circ}" data-beat="{i+1}"/>');offset+=length
            legend.append(f'<div {motion(i+1,"fromright")}><i style="background:{colors[i]}"></i><span>{e(h)}<small>{e(note)}</small></span><b>{v}<small>{v/total*100:.1f}%</small></b></div>')
        return '<div class="lab-donut"><div class="lab-donut-art">'+svg('<circle cx="120" cy="120" r="78" fill="none" stroke="#e7eef8" stroke-width="30"/>'+''.join(arcs),'0 0 240 240','donut-svg')+f'<strong>{total}<small>施策 / TOTAL</small></strong></div><div class="lab-donut-key">'+''.join(legend)+'</div></div>'
    if kind=='stats':
        return grid([f'<div class="lab-stat" {motion(i+1,"rise")}><div><b>{e(v)}</b><i>{e(u)}</i></div><h4>{e(h)}</h4><p>{e(note)}</p><span {motion(i+1,"growx")}></span></div>' for i,(v,u,h,note,*_) in enumerate(a['items'])],'cols-2')
    if kind=='orgs':
        return grid([f'<div class="lab-org" {motion(i+1,"rise")}><h4>{e(h)}</h4><b>{e(label)}</b><div class="lab-people">'+''.join(f'<i {motion(i+1,"scale")}></i>' for _ in range(n))+'</div><p>'+e(' / '.join(items))+f'</p><small>{e(note)}</small></div>' for i,(h,n,label,items,note,*_) in enumerate(a['items'])],'cols-2')
    raise ValueError(kind)
