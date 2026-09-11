"""New examples owned by the catalogue; existing article renderers stay independent."""

FIGURES = [
    dict(id='cutaway', category='structure', name='分解断面図', purpose='全体をひらくと、役割の関係が見える。', best='内部の構成と、各層が担う役割を説明。', caution='6つの役割に分けた構成例です。すべてのAIの実装を表すものではありません。', beats=['ひとつの全体', '役割ごとにひらく', 'モデルを支える構成を見る']),
    dict(id='rebuild', category='structure', name='分解・再構成図', purpose='同じ作業が、分かれ、つながり直す。', best='人とAIの分担、業務の組み替えを説明。', caution='作業の名前と識別形を保ち、どこへ移ったか追えるようにします。', beats=['ひとつの業務', '6つの作業へ分解', '人とAIに分担', '仕事の流れへ再接続']),
    dict(id='gate', category='sequence', name='判断ゲート', purpose='任せる範囲を、見える境界にする。', best='条件に応じた実行と、人への確認の分岐。', caution='判定は事前に合意した条件に基づく見本です。条件と責任を明示します。', beats=['依頼を受け取る', '合意した条件と照合', '実行か承認待ちへ分岐']),
    dict(id='waiting', category='quantity', name='待ち時間とボトルネック', purpose='作業が速くなっても、待ちは残る。', best='一部の作業の高速化が全体に及ぼす影響。', caution='直列に進む業務の仮想例です。並列処理や実測効果を示していません。', beats=['30時間の内訳', '草案の作業を速くする', '全体の変化を見る']),
]

PARTS = {
    'cover': ('光のあるファーストビュー', '言葉を主役に、光と面で空気をつくる。', '強調'),
    'reactive_sentence': ('条件を変えられる一文', '自分の条件に置き換えて、規模をつかむ。', '操作'),
    'evidence': ('主張と根拠の接続', '要点から、数値の前提と出典へつなぐ。', 'ことば'),
    'focus_note': ('焦点を動かす注釈', '全体を残しながら、説明する場所を選ぶ。', '強調'),
    'wipe': ('同じ面の前後ワイプ', '同じ内容の整理前後を、重ねて比べる。', '操作'),
    'decision': ('判断の選択肢', '選んだ後の展開と、選択理由を見せる。', '操作'),
    'trace': ('実行の記録', '入力から確認まで、実際の行動を追う。', '構成'),
    'units': ('数量のまとまり', '単位と分母を添え、数を実感できる形に。', '数字'),
    'chapter': ('次章へつながる言葉', 'ひとつの言葉を残し、次の論点へ渡す。', 'ことば'),
}

def curtain():
    return '<div class="tl-curtain" aria-hidden="true"><div class="tl-curtain-sheet">'+''.join(f'<i style="--rib:{i}"></i>' for i in range(20))+'</div><div class="tl-curtain-glow"></div><span class="tl-curtain-line"></span></div>'

def cover_air():
    """Sparse decorative light; deterministic positions keep rebuilds reproducible."""
    points = [(18,18),(32,76),(43,12),(48,58),(54,87),(60,29),(65,69),
              (70,10),(74,48),(78,83),(83,24),(87,61),(91,40),(95,77)]
    particles = ''.join(
        f'<i style="--x:{x}%;--y:{y}%;--drift:{24+i%4*14}px;--duration:{12+i%5*2}s;--delay:{-i*1.7}s;--size:{2+i%3}px"></i>'
        for i,(x,y) in enumerate(points))
    return '<div class="tl-cover-air" aria-hidden="true">'+particles+'<span class="tl-cover-ray"></span><span class="tl-cover-ray"></span></div>'

def scene(kind):
    control = ''
    if kind == 'gate':
        control = '<div class="nx-options" role="group" aria-label="依頼の条件"><button type="button" data-gate="normal" aria-pressed="false">合意した範囲内</button><button type="button" data-gate="exception" aria-pressed="true">上限を超える</button></div>'
    if kind == 'waiting':
        control = '<label class="nx-slider" for="nx-speed">草案をつくる速度 <output id="nx-speed-value" for="nx-speed">4倍</output><input id="nx-speed" type="range" min="1" max="4" step="0.5" value="4"></label><div class="nx-legend"><span><i class="nx-blue"></i>調査</span><span><i class="nx-teal"></i>草案</span><span><i class="nx-warm"></i>承認待ち</span><span><i class="nx-muted"></i>確認</span></div>'
    return f'<div class="nx-scene" data-kinetic="{kind}">{control}<div class="nx-drawing"></div><p class="nx-summary" aria-live="polite"></p></div>'

def parts():
    return {
        'cover': '<div class="nx-cover" data-ambient-zone>'+cover_air()+curtain()+'<span class="nx-overline">A QUESTION WORTH ASKING</span><h4><span>問いを、</span><span>未来につなぐ。</span></h4><p>言葉から始まる、次の一歩。</p></div>',
        'reactive_sentence': '<div class="nx-reactive"><p class="nx-sentence">週 <label><span class="nx-sr">1週間の回数</span><input type="number" min="1" max="20" value="3" data-frequency></label> 回、<br>1回 <label><span class="nx-sr">1回あたりの分数</span><input type="number" min="1" max="120" value="20" data-minutes></label> 分を短縮すると。</p><div class="nx-reactive-line"><i></i></div><p class="nx-result" aria-live="polite">4週間で <strong data-saving>4</strong> 時間</p><small>4週間として単純計算した仮想例。</small></div>',
        'evidence': '<div class="nx-evidence"><p class="nx-big-statement">待ち時間は、<br><em>全体の40%。</em></p><div class="nx-source-line"></div><details><summary>数字の根拠をひらく <span>＋</span></summary><dl><div><dt>対象</dt><dd>直列に進む提案業務の仮想例</dd></div><div><dt>計算</dt><dd>承認待ち12時間 ÷ 全体30時間</dd></div><div><dt>出典</dt><dd>この便覧の説明用データ</dd></div><div><dt>留意点</dt><dd>実際の業務に一般化しません。</dd></div></dl></details></div>',
        'focus_note': '<div class="nx-focus"><div class="nx-focus-path" role="group" aria-label="説明する工程">'+''.join(f'<button type="button" data-focus="{i}" aria-pressed="{str(i==1).lower()}"><span>0{i+1}</span>{name}</button>' for i,name in enumerate(['準備','判断','実行']))+'</div><div class="nx-focus-pointer"></div><p aria-live="polite">判断：任せる範囲と、人が確認する条件を決める。</p></div>',
        'wipe': '<div class="nx-wipe"><div class="nx-wipe-window"><div class="nx-wipe-before"><span>整理前</span><p>提案書は、目的を揃え、条件を決め、確認する人を決めてから作り始める。</p></div><div class="nx-wipe-after"><span>整理後</span><h4>作り始める前に、<br>3つを決める。</h4><ol><li>目的を揃える</li><li>条件を決める</li><li>確認する人を決める</li></ol></div><i class="nx-wipe-edge"></i></div><label>同じ内容の見せ方 <output>50%</output><input type="range" min="0" max="100" value="50" aria-label="整理後の表示割合"></label></div>',
        'decision': '<div class="nx-decision"><p class="nx-big-statement">初めての業務を、<br>どう任せる？</p><div class="nx-choice-row"><button type="button" data-decision="small" aria-pressed="true">小さく試す</button><button type="button" data-decision="draft" aria-pressed="false">草案まで任せる</button></div><p class="nx-decision-answer" aria-live="polite">1件の低い影響範囲で試し、結果を確認。条件を具体化できます。</p></div>',
        'trace': '<div class="nx-trace">'+''.join(f'<details><summary><span>0{i+1}</span><b>{name}</b><small>{time}</small></summary><p>{detail}</p></details>' for i,(name,time,detail) in enumerate([('入力を受け取る','00:00','対象期間と集計条件を受け取った、という記録の見本。'),('対象を検索する','00:02','指定した範囲のデータを検索。参照先と実行結果をここに記録します。'),('草案を作る','00:05','確認できた内容から草案を作成。出力への参照を残します。'),('人が確認する','00:10','確認者が根拠と出力を照合。修正内容と承認結果を記録します。')]))+'<p class="nx-small">架空の実行記録。AIの内的な思考を示すものではありません。</p></div>',
        'units': '<div class="nx-units"><div class="nx-units-title"><strong>40<span> / 100件</span></strong><button type="button" data-unit-group aria-pressed="false">10件ずつにまとめる</button></div><div class="nx-unit-field" aria-hidden="true">'+''.join(f'<i class="{"is-lit" if i<40 else ""}" style="--ux:{i%10};--uy:{i//10};--gx:{(i//10)%2*6+i%5};--gy:{i//20*3+(i%10)//5}"></i>' for i in range(100))+'</div><p>1つの点が1件。100件のうち40件を強調した見本。</p></div>',
        'chapter': '<div class="nx-chapter"><span class="nx-overline" data-chapter-label>CHAPTER 01 / 決める</span><div class="nx-chapter-word"><b>目的</b><span data-chapter-text>を、言葉にする。</span></div><button type="button" data-chapter-next>次の章へ →</button><p class="nx-sr" aria-live="polite" data-chapter-live>第1章：目的を、言葉にする。</p></div>',
    }
