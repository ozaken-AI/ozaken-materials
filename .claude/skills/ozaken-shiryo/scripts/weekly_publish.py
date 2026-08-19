#!/usr/bin/env python3
"""週次トレンドの号を公開する。

資料アーカイブ（publish.py）とは、鍵のかけ方と載せ先だけが違う。
組版・スタイル検査・演出の注入は publish.compose をそのまま通すので、
資料と週次で見た目が割れることはない。

  OZAKEN_PW=マスター python3 weekly_publish.py \\
      /tmp/body.html 2026-08-18 --pw nikyoku \\
      --title "使っているのに、不安は増えている" \\
      --lead "今週は7領域から7本。…（3行ぶん）"

鍵は3本。
  マスター        … おざけん本人
  週次購読キー    … 全号に共通（_meta.weekly）。四半期ごとに付け替える
  その週の1語     … 号ごと。会場で読み上げる前提の小文字英字4〜10文字

**資料の共通パスワードは付けない。** 資料をまとめて渡した相手に
週次まで渡ってしまうため（逆も同じ）。
"""
import argparse
import datetime
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import oz_root
ROOT = oz_root.root(HERE)

import lockbox
import registry
from publish import compose, check_pw_word, TPL

INDEX = os.path.join(ROOT, 'index.html')
START, END = '<!--WEEKLY:START-->', '<!--WEEKLY:END-->'
ANCHOR = '<span class="eyebrow">Section 01</span>'
SHOW = 4          # トップページに出す号数。古い号は一覧ページへ送る


def master():
    pw = os.environ.get('OZAKEN_PW', '')
    if not pw:
        sys.exit('OZAKEN_PW にマスターパスワードを入れて実行してください。')
    return pw


def weekly_key(m):
    """週次購読キー。無ければ作って台帳に記録する"""
    data = registry.load(m)
    meta = data.setdefault('_meta', {})
    if not meta.get('weekly'):
        q = (datetime.date.today().month - 1) // 3 + 1
        meta['weekly'] = 'O29trend%02dq%d' % (datetime.date.today().year % 100, q)
        registry.save(m, data)
        print('週次購読キーを作りました: %s' % meta['weekly'])
    return meta['weekly']


def esc(t):
    return (t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'))


def weekly_rows(m):
    """台帳から週次の号を新しい順に取り出す"""
    data = registry.load(m)
    rows = []
    for rel, e in data.items():
        if rel == '_meta' or not rel.startswith('weekly/'):
            continue
        date = os.path.basename(rel)[:-5]
        rows.append((date, rel, e.get('title', '') or rel, e.get('lead', '')))
    return sorted(rows, reverse=True)


def index_section(m):
    rows = weekly_rows(m)
    cards = []
    for date, rel, title, lead in rows[:SHOW]:
        y, mo, d = date.split('-')
        cards.append(
            '        <div class="card">\n'
            '          <span class="card-tag">%s/%s</span>\n'
            '          <h3>%s</h3>\n'
            '          <p>%s</p>\n'
            '          <a class="wk-open" href="%s">%s年%s月%s日号を開く →</a>\n'
            '        </div>' % (mo, d, esc(title), esc(lead), rel, y, int(mo), int(d)))
    more = ''
    if len(rows) > SHOW:
        more = ('        <p class="sec-sub" style="margin-top:1.4rem">'
                'これより前の号は %d 本あります。購読キーでまとめてお渡しします。</p>\n'
                % (len(rows) - SHOW))
    return (START + '\n'
            '<section class="sec-navy">\n'
            '  <div class="inner" data-reveal>\n'
            '    <span class="eyebrow">Weekly Trend</span>\n'
            '    <h2 class="sec-title">今週のトレンド ── '
            '毎週、一次情報だけでまとめています</h2>\n'
            '    <p class="sec-sub">技術・法規制・人材・組織・社会・産業・スタートアップの7領域を定点で追い、'
            '数字と仕組みまで確かめたものだけを載せています。'
            '裏の取れなかった話は「今週は載せなかったもの」として理由ごと残しています。</p>\n'
            '    <div class="arc-lock">\n'
            '      <span class="arc-lock-i" aria-hidden="true">🔒</span>\n'
            '      <div class="arc-lock-b">\n'
            '        <p class="arc-lock-t">本文の閲覧には購読キーが必要です</p>\n'
            '        <p class="arc-lock-d">顧問先・研修先の方にお渡ししています。'
            '資料アーカイブとは別の鍵です。</p>\n'
            '        <div class="arc-lock-a">\n'
            '          <a href="https://ozaken-ai.studio.site/#contact" target="_blank" rel="noopener">フォームから問い合わせる →</a>\n'
            '          <a href="https://x.com/ozaken_AI" target="_blank" rel="noopener">X（@ozaken_AI）のDMへ →</a>\n'
            '        </div>\n'
            '      </div>\n'
            '    </div>\n\n'
            '      <div class="cards">\n' + '\n'.join(cards) + '\n      </div>\n'
            + more +
            '  </div>\n'
            '</section>\n' + END + '\n\n')


def add_to_index(m):
    s = open(INDEX, encoding='utf-8').read()
    sec = index_section(m)
    if START in s:
        s = s[:s.index(START)] + sec + s[s.index(END) + len(END) + 1:].lstrip('\n')
    else:
        i = s.index(ANCHOR)
        i = s.rfind('<section class="sec-light">', 0, i)
        s = s[:i] + sec + s[i:]
    open(INDEX, 'w', encoding='utf-8').write(s)
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('body')
    ap.add_argument('date', help='YYYY-MM-DD')
    ap.add_argument('--pw', required=True, help='その週の1語（小文字英字4〜10文字）')
    ap.add_argument('--title', required=True)
    ap.add_argument('--lead', required=True, help='トップページに平文で出る3行ぶん')
    ap.add_argument('--update', action='store_true', help='本文だけ差し替える（鍵は維持）')
    a = ap.parse_args()

    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', a.date):
        sys.exit('日付は YYYY-MM-DD で渡してください')
    m = master()
    rel = 'weekly/%s.html' % a.date
    out = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(out), exist_ok=True)

    page, summary = compose(a.body)
    print('検査:', summary)

    if a.update:
        if not os.path.exists(out):
            sys.exit('%s がありません。新規なら --update を外してください。' % rel)
        lockbox.encrypt(out, m, page)
        assert lockbox.decrypt(out, m) == page
        print('更新: %s（鍵はそのまま）' % rel)
    else:
        wk = weekly_key(m)
        pw = check_pw_word(a.pw, m)
        lockbox.create(TPL, page, out, [m, wk, pw])
        for k in (m, wk, pw):
            assert lockbox.decrypt(out, k) == page, '鍵の確認に失敗: ' + k
        print('公開: %s\n購読キー: %s / その週の1語: %s' % (rel, wk, pw))

    data = registry.load(m)
    row = data.get(rel, {})
    row.update({'pw': a.pw, 'keys': 3, 'to': '週次購読者',
                'title': a.title, 'lead': a.lead,
                'at': datetime.date.today().isoformat()})
    data[rel] = row
    registry.save(m, data)

    # 会場で見せるQR画面（登壇の最後に「今週のトレンド」を出せる）
    import apply_qr
    inner = lockbox.decrypt(out, m)
    got = apply_qr.patch(inner, rel, a.title, a.pw)
    if got:
        lockbox.encrypt(out, m, got)

    # 鍵がかかった外側の題と概要。ここを忘れると、テンプレに借りた資料の題が出る
    import apply_ogp
    apply_ogp.manifest(m)
    apply_ogp.patch(rel, m)

    add_to_index(m)
    print('トップページの「今週のトレンド」を更新しました（最新%d号を表示）' % SHOW)


if __name__ == '__main__':
    main()
