#!/usr/bin/env python3
"""One-material motion pilot. Original explanations stay available as reading notes.

python3 build.py --output /absolute/local-preview/01_concept/use-to-delegate.html
Add --update only to replace this material's encrypted HTML, preserving its keys.
The master is requested without echo; no credential is written to the source.
"""
import argparse
import contextlib
import getpass
import inspect
import io
import os
from pathlib import Path
import re
import runpy
import sys
import tempfile

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent.parent / 'scripts'
ROOT = HERE.parents[4]
sys.path.insert(0, str(SCRIPTS))
import page_parts


def choices(name, items):
    return '<div class="dp-choices" role="group" aria-label="%s">%s</div>' % (name, ''.join(
        '<button type="button" data-choice="%d" aria-pressed="%s">%s</button>' %
        (i, str(i == 0).lower(), label) for i, label in enumerate(items)))


def wrap(kind, content, caption, controls=''):
    return ('<figure class="dp-figure" data-scene="%s">%s<div class="dp-canvas">%s</div>'
            '<figcaption>%s</figcaption><button type="button" class="dp-replay" '
            'aria-label="この図の動きを再生">↻ 動きを見る</button></figure>') % (kind, controls, content, caption)


def figures():
    result = []
    rows = [('起動', '毎回、自分で開く', '条件・時刻で動かす'), ('単位', '1回の作業', '範囲を決めた業務'),
            ('技能', 'うまく聞く', '材料と許可を設計する'), ('確認', 'その都度、読む', 'リスクに応じて確認する')]
    result.append(wrap('shift', '<div class="dp-shift-head"><span>人とAIの関わり方</span><b data-shift-title>使う</b></div>'
        + '<div class="dp-shift-rows">' + ''.join('<div class="dp-shift-row dp-stagger"><span>%s</span>'
          '<div><b data-before="%s" data-after="%s">%s</b><i aria-hidden="true"></i></div></div>' % (a,b,c,b) for a,b,c in rows) + '</div>',
        '自動化の量だけでなく、仕事の渡し方を変える。4つは段階的に設計できます。', choices('関わり方を比較', ['使う', '任せる'])))
    checks = [('起動', 'いつ動くか', '条件・時刻・受信'), ('手順', '何を渡すか', '材料と出力の型'),
              ('確認', '何を確かめるか', '基準と確認範囲'), ('境界', 'どこで止めるか', '金額・対象・例外'),
              ('記録', '何を残すか', '判断の根拠と結果')]
    result.append(wrap('checks', '<div class="dp-checks">' + ''.join(
        '<div class="dp-check dp-stagger"><span class="dp-index">0%d</span><i aria-hidden="true"></i><h3>%s</h3><p>%s</p><small>%s</small></div>' % (i+1,*v)
        for i,v in enumerate(checks)) + '</div>', '起動・手順・確認に、越えない線と記録を加える。製品名では判定しない。'))
    result.append(wrap('gate', '<div class="dp-gate-input"><span>依頼</span><strong data-gate-request>社内メモの下書き</strong></div>'
        '<div class="dp-gate-line" aria-hidden="true"><i></i><b></b></div>'
        '<div class="dp-gate-boundary"><span class="dp-label">BOUNDARY</span><strong>範囲・基準</strong><small>外部への送信は承認が必要</small></div>'
        '<div class="dp-gate-out"><div class="dp-route dp-route-ai"><span>範囲内</span><strong>AIが進める</strong></div>'
        '<div class="dp-route dp-route-human"><span>線を越える</span><strong>人が判断する</strong></div></div>',
        '「何を任せるか」と「どこで戻すか」。両方を決めて、丸投げを防ぐ。', choices('依頼の例を切り替え', ['社内の下書き', '社外への送信'])))
    layers = [('01', 'PROMPT', 'どう頼むか', '目的・指示・出力の形'), ('02', 'CONTEXT', '何を渡すか', '資料・履歴・判断の前提'),
              ('03', 'HARNESS', 'どこまで許すか', 'ツール・権限・止める条件')]
    result.append(wrap('layers', '<div class="dp-layers">' + ''.join(
        '<div class="dp-layer dp-stagger"><span class="dp-index">%s</span><span><small>%s</small><strong>%s</strong></span><p>%s</p></div>' % v for v in layers)
        + '</div>', '聞き方を整え、その下にある材料と実行範囲まで設計する。', choices('設計の層を切り替え', ['聞き方', '材料を加える', '実行範囲まで'])))
    decisions = [('01', '渡す材料', '判断の前提をつくる', '参照資料・過去の事例'), ('02', '見る割合', '確認の範囲を決める', '高リスクは全件確認も'),
                 ('03', '止める条件', '介入の線を引く', '例外・誤り・権限の境界')]
    result.append(wrap('decisions', '<div class="dp-decisions">' + ''.join(
        '<div class="dp-decision dp-stagger"><span class="dp-orbit" aria-hidden="true"></span><span class="dp-index">%s</span><h3>%s</h3><p>%s</p><small>%s</small></div>' % v for v in decisions)
        + '</div>', '任せたあとも、判断基準をつくり、見直す仕事は人に残る。'))
    tasks = [('日程の候補出し', 'ai'), ('一次返信の下書き', 'ai'), ('書類の形式確認', 'ai'),
             ('求人票の下書き', 'with'), ('面接メモの整理', 'with'), ('採否・条件の決定', 'human')]
    result.append(wrap('tasks', '<div class="dp-task-heading"><strong>採用業務</strong><span data-task-note>大きな名前のままでは、任せる境界が見えない</span></div>'
        '<div class="dp-task-board"><div class="dp-task-labels"><span>AIに任せる範囲</span><span>人が確認する</span><span>人が決める</span></div>'
        '<div class="dp-tasks">' + ''.join('<div class="dp-task" data-owner="%s"><span>%s</span><small>%s</small></div>' % (owner,label, {'ai':'定めた範囲で実行','with':'下書き・整理を支援','human':'判断は人が担う'}[owner]) for label,owner in tasks)
        + '</div></div>', '「採用を任せる」では大きすぎる。動詞まで分けると、渡せる範囲が見える。', choices('業務の粒度を切り替え', ['業務のまま', '動詞まで分解'])))
    result.append(wrap('myths', '<div class="dp-myth"><div><span class="dp-label">BEFORE</span><p data-myth-before>精度が上がったら任せる</p></div>'
        '<i aria-hidden="true">→</i><div><span class="dp-label">REFRAME</span><p data-myth-after>外れたときの戻し方から決める</p></div></div>'
        '<p class="dp-myth-note" data-myth-note>精度だけを待たず、限定した範囲と確認方法を先に設計する。</p>',
        '技術の進歩を待つだけでなく、自分たちが置いている前提を見直す。', choices('5つの思い込みを選ぶ', ['01 精度', '02 全社導入', '03 楽になる', '04 完璧なルール', '05 仕事の変化'])))
    result.append(wrap('return', '<div class="dp-return"><div class="dp-station"><span class="dp-index">01</span><strong>任せる</strong><p>範囲内で実行</p></div>'
        '<div class="dp-station"><span class="dp-index">02</span><strong>人に戻す</strong><p>例外を確認・判断</p></div>'
        '<div class="dp-station"><span class="dp-index">03</span><strong>任せ直す</strong><p>基準を更新して再開</p></div>'
        '<div class="dp-return-track" aria-hidden="true"><i></i></div></div>',
        '前例がない・影響が大きい・状況が荒れている。戻す条件と担当者を決めておく。', choices('運用の状態を切り替え', ['範囲内で実行', '例外が発生', '基準を更新'])))
    result.append(wrap('plan', '<div class="dp-plan">' + ''.join(
        '<div class="dp-plan-step dp-stagger"><span>%s</span><h3>%s</h3><p>%s</p><small>残すもの：%s</small></div>' % v for v in [
          ('WEEK 1', 'ほどく', '業務を動詞に分ける', '作業の一覧'), ('WEEK 2', '型にする', '過去の事例で試す', '材料と出力の型'),
          ('WEEK 3–4', '線を引く', '境界と確認方法を決める', '判断基準とログ')]) + '</div>'
        '<div class="dp-conditions"><span>毎週やる</span><span>社内で完結</span><span>自分が当事者</span><span>取り消せる</span></div>',
        '最初の1か月の進め方の例。必要な期間と工数は、業務の複雑さによって変わります。'))
    return result


def body():
    captured = []
    original = page_parts.sec
    def capture(*args, **kwargs):
        b = inspect.signature(original).bind(*args, **kwargs)
        b.apply_defaults()
        captured.append(b.arguments)
        return original(*args, **kwargs)
    page_parts.sec = capture
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            data = runpy.run_path(str(HERE.parent / 'gen_use_to_delegate.py'))
    finally:
        page_parts.sec = original
    assert len(captured) == 9
    lines = [data['B'][0]]
    curtain = '<div class="dp-curtain" aria-hidden="true"><div>' + ''.join('<i style="--rib:%d"></i>' % i for i in range(20)) + '</div></div>'
    lines.append('<section class="hero" id="cover">' + curtain + '<div class="inner">'
        '<span class="eyebrow">CONCEPT / FROM USING TO DELEGATING</span>'
        '<h1 class="hero-title"><span>「使うAI」から</span><br><span>「任せるAI」へ。</span></h1>'
        '<p class="hero-copy">変えるのは、聞き方だけではない。<br>仕事の渡し方を、設計し直す。</p>'
        '<p class="hero-meta">' + page_parts.BYLINE + '</p>'
        '<a class="dp-start" href="#chapter-1">関わり方の境目を見にいく <span aria-hidden="true">↓</span></a></div>'
        '<div class="dp-cover-foot"><span>OZAKEN / CONCEPT SERIES</span><span>9 CHAPTERS · INTERACTIVE EDITION</span></div></section>')
    titles = ['変えるのは、<em>仕事の渡し方。</em>', '「任せる」を、<em>5つの問いで点検する。</em>',
              '任せることは、<em>線を引くこと。</em>', '聞き方から、<em>実行の設計へ。</em>',
              '人に残るのは、<em>3つの決めごと。</em>', '仕事をほどくと、<em>任せる範囲が見える。</em>',
              '止まる理由は、<em>前提にあるかもしれない。</em>', '戻せるから、<em>任せられる。</em>',
              '最初の一歩は、<em>小さな1業務。</em>']
    subtitles = ['人が毎回動かす状態から、範囲と基準を決めて渡す状態へ。', '起動・手順・確認、そして境界と記録。',
        '社内の下書きと、社外への送信。同じ文章でも、許す範囲は違う。', 'プロンプト、コンテキスト、ハーネス。設計する対象が広がる。',
        '作業を減らすだけで終わらせない。何を判断するかを決めておく。', '「業務の名前」から「具体的な動詞」へ、粒度を下げる。',
        '5つの思い込みを、次の行動が決まる言葉に置き直す。', '全部を任せ続けることがゴールではない。', '派手さより、繰り返せること。自分の仕事から始める。']
    for i, (old, fig) in enumerate(zip(captured, figures()), 1):
        notes = '<details class="dp-notes"><summary>この章の解説と元の図を読む<span aria-hidden="true">＋</span></summary><div class="dp-notes-inner">'
        notes += '<h3>' + old['title'] + '</h3>'
        if old['lede']: notes += '<p class="lede">' + old['lede'] + '</p>'
        original_figures = re.sub(r'<svg[\s\S]*?</svg>', lambda m:
            '<div class="dp-reference-canvas" tabindex="0" role="region" aria-label="参考図。狭い画面では左右にスクロールできます">'
            + m[0] + '</div>', old['fig'] or '')
        notes += original_figures + '<div class="cards">' + (old['body'] or '') + '</div>' + (old['after'] or '') + '</div></details>'
        lines.append('<section class="%s" id="chapter-%d" data-chapter="%d"><div class="dp-air" aria-hidden="true"></div><div class="inner">'
            '<span class="eyebrow">CHAPTER %02d / 09</span><h2 class="sec-title">%s</h2><p class="sec-sub">%s</p>%s%s</div></section>' %
            (old['tone'], i, i, i, titles[i-1], subtitles[i-1], fig, notes))
    lines.append('<section class="sec-navy" id="closing"><div class="inner"><span class="eyebrow">TAKE IT WITH YOU</span>'
        '<h2 class="sec-title">任せるとは、<br><em>仕事を説明できる形にすること。</em></h2>'
        '<p class="dp-close-copy">仕事をほどく。範囲を決める。基準を言葉にする。<br>この力は、道具が変わっても持っていける。</p>'
        '<div class="dp-closing-words"><span>ほどく</span><i>→</i><span>範囲</span><i>→</i><span>基準</span></div>'
        '<details class="dp-notes"><summary>おわりに<span aria-hidden="true">＋</span></summary><div class="dp-notes-inner">'
        + re.search(r'<p class="kicker">(.*?)</p>', data['B'][-1], re.S).group(0) + '</div></details></div></section>')
    lines.append('<nav class="dp-dock" aria-label="資料の操作"><button type="button" data-prev aria-label="前の章">←</button>'
        '<span class="dp-page" aria-live="polite">表紙 / 11</span><button type="button" data-next aria-label="次の章">→</button>'
        '<button type="button" data-motion aria-pressed="false">動きを止める</button></nav>')
    return '\n'.join(lines)


def preserve_extensions(page, old):
    """Keep the existing QR credentials, links, and material-specific additions in memory."""
    from apply_qr import CSS_HEAD, CSS_TAIL, MARK
    if MARK in old:
        start = old.rfind('<div class="qrv">', 0, old.index(MARK))
        assert start >= 0
        qr = old[start:old.index(MARK) + len(MARK)]
        css = old[old.index(CSS_HEAD):old.index(CSS_TAIL) + len(CSS_TAIL)]
        page = page.replace('</head>', '<style>' + css + '</style></head>')
        page = page.replace('</body>', qr + '\n</body>')
    # Existing chapter references follow their matching chapter inside its reading notes.
    sections = re.findall(r'<section\b[\s\S]*?</section>', old)
    for i, section in enumerate(sections[1:10], 1):
        refs = re.findall(r'<p class="xr-chips">[\s\S]*?</p>', section)
        if refs:
            pattern = r'(<section\b[^>]*\bid="chapter-%d"[\s\S]*?)(</div></details>)' % i
            page, count = re.subn(pattern, lambda m: m[1] + ''.join(refs) + m[2], page, count=1)
            assert count == 1, 'Could not preserve chapter references'
    if 'xr-chips' in old:
        from crossref import CSS
        page = page.replace('</head>', '<style>' + CSS + '</style></head>')
    return page


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--update', action='store_true')
    parser.add_argument('--preserve', action='store_true', help='Preserve the current page QR in preview; asks for master')
    parser.add_argument('--baseline', type=Path, help='Optional encrypted original for recovering existing references')
    args = parser.parse_args()
    master = getpass.getpass('Master password: ') if args.update or args.preserve else None
    os.environ['OZAKEN_PW'] = master or 'local-preview-only'
    from publish import compose
    from build_page import check
    import lockbox
    with tempfile.TemporaryDirectory(prefix='ozaken-pilot-') as tmp:
        fragment = Path(tmp) / 'body.html'
        fragment.write_text(body(), encoding='utf-8')
        page, summary = compose(str(fragment))
    # The new atmosphere replaces only decorative scripts; navigation stays intact.
    import apply_herofx
    page = apply_herofx.strip(page)
    page = re.sub(r'<script>\s*/\* パーティクル・ネットワーク背景[\s\S]*?</script>', '', page)
    page = page.replace('<body>', '<body class="delegation-pilot">')
    page = page.replace('</head>', '<style>\n' + (HERE / 'pilot.css').read_text() + '\n</style>\n</head>')
    page = page.replace('</body>', '<script>\n' + (HERE / 'pilot.js').read_text() + '\n</script>\n</body>')
    target = ROOT / '01_concept/use-to-delegate.html'
    if master:
        old = lockbox.decrypt(str(args.baseline or target), master)
        page = preserve_extensions(page, old)
        assert page.count('class="xr-chips"') == old.count('class="xr-chips"')
        assert ('<!-- OZ-QR v1 -->' in page) == ('<!-- OZ-QR v1 -->' in old)
    errors, _ = check(page)
    if errors: raise SystemExit('\n'.join(errors))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(page, encoding='utf-8')
    if args.update:
        before = lockbox.parse(target.read_text()).group('w')
        lockbox.encrypt(str(target), master, page)
        assert lockbox.parse(target.read_text()).group('w') == before
        assert lockbox.decrypt(str(target), master) == page
    print('OK:', summary, '/ 9 interactive scenes /', args.output)


if __name__ == '__main__':
    main()
