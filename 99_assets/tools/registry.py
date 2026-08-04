#!/usr/bin/env python3
"""個別パスワードの台帳をつくる・更新する。

台帳そのものを「マスターパスワードだけで開く暗号化ページ」として持つ。
リポジトリは公開なので、平文の一覧はどこにも置かない。
台帳の中身は HTML の中に JSON として埋めてあり、この道具が読み書きする。

  使い方（マスターは環境変数で渡す）:
    OZAKEN_PW=… python3 registry.py sync
        資料の一覧を取り込み、鍵の本数を最新にする（未記録はそのまま残す）

    OZAKEN_PW=… python3 registry.py set 05_推進/kiban-phase.html あいことば --to "みずほFG"
        パスワードを記録する。実際にその資料が開くかを確かめてから書き込む

    OZAKEN_PW=… python3 registry.py list
        いま記録されている内容を表示する

  必要なもの: pip install cryptography
"""
import base64
import datetime
import glob
import hashlib
import html
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get('OZAKEN_ROOT') or os.path.dirname(os.path.dirname(HERE))
LEDGER = os.path.join(ROOT, 'パスワード台帳.html')
ITER = 200000


def master():
    pw = os.environ.get('OZAKEN_PW', '')
    if not pw:
        sys.exit('OZAKEN_PW にマスターパスワードを入れて実行してください。')
    return pw


# ── 暗号まわり。lockbox.py と同じ形式を読み書きする ──────────────
def _aes():
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    return AESGCM


def wrappers(path):
    raw = open(path, encoding='utf-8').read()
    m = re.search(r'W=(\[.*?\]),ITER', raw, re.S)
    return json.loads(m.group(1)) if m else []


def opens(path, pw):
    """pw でこの資料が開くか。鍵の取り出しだけ試す"""
    AESGCM = _aes()
    for w in wrappers(path):
        key = hashlib.pbkdf2_hmac('sha256', pw.encode(), base64.b64decode(w['s']), ITER, 32)
        try:
            AESGCM(key).decrypt(base64.b64decode(w['iv']), base64.b64decode(w['ct']), None)
            return True
        except Exception:
            pass
    return False


def docs():
    out = []
    for d in sorted(glob.glob(os.path.join(ROOT, '0*_*'))):
        out += sorted(glob.glob(os.path.join(d, '*.html')))
    out += sorted(glob.glob(os.path.join(ROOT, 'AX_Table', '*.html')))
    out += [f for f in sorted(glob.glob(os.path.join(ROOT, '*.html')))
            if os.path.basename(f) not in ('index.html', 'ask.html',
                                           os.path.basename(LEDGER))]
    return [f for f in out if 'OZAKEN-LOCKED2' in open(f, encoding='utf-8').read(64)]


def title_of(path, pw):
    """資料の見出しを取り出す。失敗しても致命ではないので握りつぶす"""
    try:
        sys.path.insert(0, HERE)
        import lockbox
        m = re.search(r'<title>(.*?)</title>', lockbox.decrypt(path, pw), re.S)
        return html.unescape(m.group(1)).split('|')[0].strip() if m else ''
    except Exception:
        return ''


# ── 台帳の読み書き ────────────────────────────────────────
def load(pw):
    if not os.path.exists(LEDGER):
        return {}
    sys.path.insert(0, HERE)
    import lockbox
    inner = lockbox.decrypt(LEDGER, pw)
    m = re.search(r'<script type="application/json" id="registry">(.*?)</script>', inner, re.S)
    return json.loads(m.group(1)) if m else {}


def save(pw, data):
    sys.path.insert(0, HERE)
    import lockbox
    inner = render(data)
    if os.path.exists(LEDGER):
        lockbox.encrypt(LEDGER, pw, inner)
    else:
        tpl = os.path.join(ROOT, '裏資料置き場.html')
        lockbox.create(tpl, inner, LEDGER, [pw])
    assert lockbox.decrypt(LEDGER, pw) == inner, '書き戻しの確認に失敗しました'


def render(data):
    rows = []
    for rel in sorted(data):
        e = data[rel]
        pwv = e.get('pw') or ''
        keys = e.get('keys', 1)
        if pwv:
            cell = '<b>%s</b>' % html.escape(pwv)
            cls = 'ok'
        elif keys > 1:
            cell = '未記録'
            cls = 'ng'
        else:
            cell = 'マスターのみ'
            cls = 'na'
        rows.append(
            '<tr class="%s"><td class="d"><span class="t">%s</span><span class="p">%s</span></td>'
            '<td class="k">%s</td><td class="s">%s</td><td class="w">%s</td></tr>'
            % (cls, html.escape(e.get('title', '') or rel), html.escape(rel),
               cell, html.escape(e.get('to', '') or '—'), html.escape(e.get('at', '') or '—')))

    n_pw = sum(1 for e in data.values() if e.get('pw'))
    n_ng = sum(1 for e in data.values() if not e.get('pw') and e.get('keys', 1) > 1)
    n_na = sum(1 for e in data.values() if e.get('keys', 1) == 1)
    stamp = datetime.date.today().isoformat()

    out = TEMPLATE
    for k, v in (('__ROWS__', '\n'.join(rows)), ('__NPW__', str(n_pw)),
                 ('__NNG__', str(n_ng)), ('__NNA__', str(n_na)),
                 ('__TOTAL__', str(len(data))), ('__STAMP__', stamp),
                 ('__JSON__', json.dumps(data, ensure_ascii=False, indent=1))):
        out = out.replace(k, v)
    return out


TEMPLATE = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>パスワード台帳 | おざけん</title>
<meta name="robots" content="noindex">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Hanken+Grotesk:wght@400;600;700&family=Shippori+Mincho+B1:wght@500;600&family=Zen+Kaku+Gothic+New:wght@400;500;700&display=swap" rel="stylesheet">
<style>
:root{--navy:#1f3864;--navy-deep:#141d35;--azure:#2e5496;--azure-pale:#d8e4f0;
  --red:#e23744;--red-bright:#ff5d6a;--muted:#6b7a99;
  --fs:'Zen Kaku Gothic New',sans-serif;--fm:'Shippori Mincho B1',serif;--fe:'Hanken Grotesk',sans-serif}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html{background:var(--navy-deep)}
body{font-family:var(--fs);color:#fff;line-height:1.8;
  background:radial-gradient(ellipse 70% 50% at 50% -6%,rgba(46,84,150,.55),transparent 62%),
    linear-gradient(168deg,#1f3864 0%,#182a52 44%,#141d35 100%);
  background-attachment:fixed;min-height:100vh;padding:clamp(2rem,6vh,4rem) 1.2rem}
.wrap{width:min(1080px,100%);margin:0 auto}
.badge{display:inline-flex;align-items:center;gap:.5rem;padding:.45em .9em;border-radius:999px;
  background:rgba(20,29,53,.5);border:1px solid rgba(216,228,240,.22);
  font-family:var(--fe);font-size:.62rem;font-weight:600;letter-spacing:.16em;
  color:rgba(216,228,240,.9);margin-bottom:1.4rem}
.badge .dot{width:6px;height:6px;border-radius:50%;background:var(--red-bright);box-shadow:0 0 8px var(--red-bright)}
.badge .ja{font-family:var(--fs);letter-spacing:.06em;font-size:.66rem;color:#fff}
h1{font-family:var(--fm);font-weight:600;font-size:clamp(1.6rem,4.6vw,2.2rem);margin-bottom:.6rem}
.lead{font-size:.88rem;color:rgba(216,228,240,.75);margin-bottom:1.8rem}
.stats{display:flex;flex-wrap:wrap;gap:.7rem;margin-bottom:1.6rem}
.stat{flex:1;min-width:150px;padding:.9rem 1.1rem;border-radius:12px;
  background:rgba(255,255,255,.06);border:1px solid rgba(216,228,240,.16)}
.stat b{display:block;font-family:var(--fe);font-size:1.6rem;font-weight:700;line-height:1.2}
.stat span{font-size:.74rem;color:rgba(216,228,240,.7)}
.stat.ok b{color:#46c98a}.stat.ng b{color:var(--red-bright)}.stat.na b{color:#9fc6f5}
table{width:100%;border-collapse:collapse;font-size:.84rem}
th,td{text-align:left;padding:.7rem .8rem;border-bottom:1px solid rgba(216,228,240,.12);vertical-align:top}
th{font-family:var(--fe);font-size:.62rem;font-weight:700;letter-spacing:.16em;
  color:rgba(159,198,245,.7);border-bottom-color:rgba(216,228,240,.24);white-space:nowrap}
td.d .t{display:block;font-weight:700}
td.d .p{display:block;font-family:var(--fe);font-size:.66rem;color:rgba(216,228,240,.5);word-break:break-all}
td.k{font-family:var(--fe);white-space:nowrap}
tr.ok td.k b{color:#7ee2b0;font-size:.95rem;letter-spacing:.03em}
tr.ng td.k{color:var(--red-bright);font-family:var(--fs);font-size:.78rem}
tr.na td.k{color:rgba(216,228,240,.4);font-family:var(--fs);font-size:.78rem}
td.s,td.w{color:rgba(216,228,240,.7);font-size:.78rem;white-space:nowrap}
.note{margin-top:1.8rem;padding-top:1.4rem;border-top:1px solid rgba(216,228,240,.14);
  font-size:.76rem;line-height:1.9;color:rgba(216,228,240,.55)}
.note code{font-family:var(--fe);background:rgba(255,255,255,.08);padding:.1em .45em;border-radius:4px;color:#fff}
.note a{color:var(--azure-pale)}
@media(max-width:640px){td.s,td.w,th.s,th.w{display:none}}
</style>
</head>
<body>
<div class="wrap">
  <div class="badge"><span class="dot"></span><span class="ja">おざけん コンテンツ管理システム</span></div>
  <h1>パスワード台帳</h1>
  <p class="lead">個別パスワードの記録。マスターパスワードでのみ開きます。最終更新 __STAMP__</p>

  <div class="stats">
    <div class="stat ok"><b>__NPW__</b><span>記録済み</span></div>
    <div class="stat ng"><b>__NNG__</b><span>個別ありだが未記録</span></div>
    <div class="stat na"><b>__NNA__</b><span>マスターのみ</span></div>
    <div class="stat"><b>__TOTAL__</b><span>資料の総数</span></div>
  </div>

  <table>
    <thead><tr><th>資料</th><th>個別パスワード</th><th class="s">共有先</th><th class="w">記録日</th></tr></thead>
    <tbody>
__ROWS__
    </tbody>
  </table>

  <p class="note">
    この台帳は <code>99_assets/tools/registry.py</code> が読み書きします。手で書き換えないでください。<br>
    記録する：<code>OZAKEN_PW=… python3 registry.py set 05_推進/kiban-phase.html 合言葉 --to "共有先"</code><br>
    資料を足したら：<code>OZAKEN_PW=… python3 registry.py sync</code><br>
    <a href="index.html">← AI資料アーカイブに戻る</a>
  </p>
</div>
<script type="application/json" id="registry">
__JSON__
</script>
</body>
</html>
"""


# ── コマンド ────────────────────────────────────────────
def cmd_sync(pw, args):
    data = load(pw)
    for f in docs():
        rel = os.path.relpath(f, ROOT)
        e = data.setdefault(rel, {})
        e['keys'] = len(wrappers(f))
        if not e.get('title'):
            e['title'] = title_of(f, pw)
    for rel in list(data):
        if not os.path.exists(os.path.join(ROOT, rel)):
            del data[rel]           # 消えた資料は台帳からも外す
    save(pw, data)
    print('台帳を更新しました（%d 本）' % len(data))


def cmd_set(pw, args):
    if len(args) < 2:
        sys.exit('使い方: registry.py set <資料のパス> <パスワード> [--to 共有先]')
    rel, val = args[0], args[1]
    to = ''
    if '--to' in args:
        to = args[args.index('--to') + 1]
    path = os.path.join(ROOT, rel)
    if not os.path.exists(path):
        sys.exit('見つかりません: ' + rel)
    if not opens(path, val):
        sys.exit('その文字列ではこの資料は開きません。記録を中止しました。')
    data = load(pw)
    e = data.setdefault(rel, {})
    e.update({'pw': val, 'to': to, 'at': datetime.date.today().isoformat(),
              'keys': len(wrappers(path))})
    if not e.get('title'):
        e['title'] = title_of(path, pw)
    save(pw, data)
    print('記録しました: %s → %s' % (rel, val))


def cmd_list(pw, args):
    data = load(pw)
    if not data:
        print('台帳がまだありません。sync から始めてください。')
        return
    for rel in sorted(data):
        e = data[rel]
        v = e.get('pw') or ('未記録' if e.get('keys', 1) > 1 else '－')
        print('%-46s %-16s %s' % (rel[:46], v, e.get('to', '')))


if __name__ == '__main__':
    cmds = {'sync': cmd_sync, 'set': cmd_set, 'list': cmd_list}
    if len(sys.argv) < 2 or sys.argv[1] not in cmds:
        sys.exit(__doc__)
    cmds[sys.argv[1]](master(), sys.argv[2:])
