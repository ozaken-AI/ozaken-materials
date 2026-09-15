#!/usr/bin/env python3
"""Add the DCAP practice to the current tacit-knowledge document only.

Retains the complete cover, original sections, links, scripts and wrapped keys.
Use --preview-dir outside the repository; add --update after visual review.
"""
from pathlib import Path
import re
from practical_guides import chapter, figure, srcs, sections, apply_styles, apply_body, run

PREFIX = 'tacit-dcap--'
STYLE = re.compile(r'<style id="oz-tacit-dcap-style">[\s\S]*?</style>\n?')
PDCA = 'https://asq.org/quality-resources/pdca-cycle'
CONTEXT = 'https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents'


def build():
    steps = [
        ('D', 'DO', 'まず使う', '一つの業務に<br>AIエージェントを入れる'),
        ('C', 'CHECK', '文句を集める', '出力を現場で見て<br>「何が違うか」を確かめる'),
        ('A', 'ACT', 'コンテキストを直す', '足りない前提や判断基準を<br>指示・情報・例に加える'),
        ('P', 'PLAN', '次の試し方を決める', '次に任せる範囲と<br>確かめる点を決める'),
    ]
    cycle = '<div class="td-cycle"><ol>' + ''.join(
        f'<li><div class="td-step-top"><b>{letter}</b><span>{english}</span></div><h3>{title}</h3><p>{copy}</p></li>'
        for letter,english,title,copy in steps) + '</ol>'
    cycle += ('<div class="td-loop"><svg viewBox="0 0 1000 44" preserveAspectRatio="none" aria-hidden="true">'
              '<path class="a-flow" d="M880 2V22Q880 34 868 34H132Q120 34 120 22V2" fill="none" stroke="#2e5496" stroke-width="1.5"/>'
              '<path d="M114 9L120 2L126 9" fill="none" stroke="#2e5496" stroke-width="1.5"/></svg>'
              '<p>次のDへ　使うたびに コンテキストが育つ</p></div></div>')
    first = chapter(PREFIX+'cycle','sec-navy','Section 06 — DCAP',
        'AI導入は PDCAよりDCAP<br>まず使って 文句を集める',
        'AIに渡す前提や情報＝コンテキストを 完璧に整えるまで待たない<br>先に小さく使うと 現場の「ここが違う」に 埋もれていた判断基準が表れる',
        figure('DCAP GUIDE 01','計画の完成を待たず 実行から学習を回す',cycle,
               '本資料では PDCAの入口をDoに置く AI導入の進め方をDCAPと呼ぶ　計画をなくすという意味ではない'),
        after='<p class="td-note"><strong>最初は 小さな下書き業務から</strong>用途・使ってよい情報・人が確認する場所を決めて始める<br>記録を残す箱は最小限用意し コンテキストの中身は使いながら整える</p>'
              + srcs([('PDCAの定義：ASQ',PDCA),('反復的なコンテキスト整備：Anthropic',CONTEXT)]))
    examples = [
        ('「この数字 いつもの数字と違う」','対象期間や集計条件が<br>現場の前提と違う','対象期間・集計元<br>キャンセル案件の除外条件'),
        ('「部長には この順番で見せない」','読み手が優先するのは<br>結論と 判断が必要なこと','結論 → 要判断事項 → 根拠<br>の順に並べた 良い見本'),
        ('「この案件は 普通の対応じゃダメ」','例外扱いになる条件や<br>確認先が 共有されていない','特別対応になる条件<br>担当者に確認するタイミング'),
    ]
    headings = ['現場の文句','言葉にすると見えてくる前提','AIに渡すコンテキスト']
    grid = '<table class="td-table"><thead><tr>' + ''.join(f'<th scope="col">{h}</th>' for h in headings) + '</tr></thead><tbody>'
    for row in examples:
        grid += '<tr>'
        for i,value in enumerate(row):
            tag = 'th' if i == 0 else 'td'
            scope = ' scope="row"' if i == 0 else ''
            grid += f'<{tag}{scope}><span class="td-cell-label">{headings[i]}</span>{value}</{tag}>'
        grid += '</tr>'
    grid += '</tbody></table>'
    second = chapter(PREFIX+'context','sec-light','Section 07 — Feedback to context',
        '現場の文句は<br>コンテキストを育てる材料になる',
        '例：週次の定例会議資料を AIエージェントに下書きさせる<br>「使えない」で終わらせず どこが違うのかを聞くと 言葉になっていなかった前提が見えてくる',
        figure('DCAP GUIDE 02','文句を 判断基準と具体例へ変える',grid,
               '説明用の架空例　文句をそのまま指示に足さず 原因を確かめて 共通のルールや具体例にする'),
        after='<div class="td-check"><span>確かめ方</span><p>同じ入力で もう一度使う → 人が結果を確認する → 直った条件を残す</p></div>'
              '<p class="td-note">データや接続先の不具合なら その原因を直す<br>現場の「違う」を記録へ戻すことが 暗黙知をコンテキストに変える仕事になる</p>')
    return first + second


def transform(page):
    source = STYLE.sub('', apply_body.strip(page))
    owned = [n for n in sections(source) if n.attrs.get('data-practical-guide','').startswith(PREFIX)]
    if owned:
        nodes = sections(source)
        positions = [nodes.index(n) for n in owned]
        assert positions == list(range(positions[0],positions[-1]+1)), 'DCAP chapters must remain adjacent'
        source = source[:owned[0].start].rstrip() + '\n' + source[owned[-1].end:].lstrip()
    original = [n.outer(source) for n in sections(source)]
    anchors = [n for n in sections(source) if '>Summary<' in n.outer(source)]
    assert len(anchors) == 1, 'Cannot find the original summary'
    pos = anchors[0].start
    source = source[:pos].rstrip() + '\n' + build().rstrip() + '\n' + source[pos:]
    for section in original:
        assert section in source, 'Original chapter changed'
    result = apply_styles(source)
    css = Path(__file__).with_name('tacit_dcap.css').read_text()
    return result.replace('</head>', f'<style id="oz-tacit-dcap-style">\n{css}\n</style>\n</head>', 1)


if __name__ == '__main__':
    run({'01_concept/tacit-knowledge-and-data-box.html':transform}, '暗黙知の資料にDCAPとコンテキストの実践例を追加')
