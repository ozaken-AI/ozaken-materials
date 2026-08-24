#!/usr/bin/env python3
"""道具の部屋（console.html）を組む。

**鍵の要るページが増えて、入口を覚えていられなくなった。**
裏資料置き場・パスワード台帳・資料マトリクス・テンプレート便覧・受信箱。
パソコンなら2文字のキーで飛べるが、スマートフォンでは打てない。

そこで、鍵の要るページだけを1枚に集めた。ここを開ければ、
あとは指で選ぶだけで全部に行ける。

**一度入れたパスワードは、そのまま次のページでも効く。**
解錠したパスワードは sessionStorage に残るので、
この部屋から先は、もう入力を求められない。だから入口は1つでよい。

  OZAKEN_PW=マスター python3 make_console.py

**道具のページに共通鍵は付けない。** 共通パスワードは資料を配るための鍵で、
これで道具の部屋が開くと、資料を渡した相手に台帳まで見えてしまう。
"""
import datetime
import html
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lockbox
import oz_root
import registry

ROOT = oz_root.root(HERE)
OUT = os.path.join(ROOT, 'console.html')

# 鍵の要るページ。**増やすときはここだけ直す。**
# index.html の隠しコマンドと、この部屋の両方に書くと、必ず片方が古くなる
DOORS = [
    ('backstage.html', 'UR', '裏資料置き場',
     'スポット講演・法人研修・Udemy講座・AX Table。渡す相手が決まっている資料。'),
    ('passwords.html', 'PW', 'パスワード台帳',
     '資料ごとの個別パスワードと、誰にいつ渡したか。共通パスワードもここ。'),
    ('matrix.html', 'MX', '資料マトリクス',
     'どの資料が、どの概念に触れているか。手薄なテーマを見つける道具。'),
    ('template.html', 'TE', 'テンプレート便覧',
     '資料の型・図版カタログ・レギュレーション・生成元の一覧。'),
    ('inbox.html', 'IN', '受信箱 ─ 質問とコメント',
     '届いたものを、期間を切らずに全部。投影のQ&Aは会場に映すので'
     '直近数時間しか出さない。読み返すのはこちら。'),
]


def counts(pw):
    """部屋に入ってすぐ分かるようにしておく数字。

    **道具のページは資料に数えない。** この部屋自身を数えてしまい、
    公開したわけでもないのに資料が1本増えて見えた。
    """
    from crossref_data import NOT_DOCS
    docs = [f for f in registry.docs() if os.path.basename(f) not in NOT_DOCS]
    cats = sorted({os.path.relpath(f, ROOT).split('/')[0]
                   for f in docs if re.match(r'^\d\d_', os.path.relpath(f, ROOT))})
    led = registry.load(pw)
    n_pw = sum(1 for k, v in led.items() if k != '_meta' and v.get('pw'))
    return len(docs), len(cats), n_pw


def build(pw):
    n_doc, n_cat, n_pw = counts(pw)
    doors = '\n'.join(
        '<a class="door" href="%s">'
        '<span class="k">%s</span>'
        '<span class="b"><b>%s</b><i>%s</i></span>'
        '<span class="go" aria-hidden="true">→</span></a>'
        % (html.escape(h), html.escape(k), html.escape(t), html.escape(d))
        for h, k, t, d in DOORS)
    out = TEMPLATE
    keys = '／'.join('<b>%s</b>' % k.lower() for _, k, _, _ in DOORS)
    for a, b in (('__DOORS__', doors), ('__NDOC__', str(n_doc)),
                 ('__NCAT__', str(n_cat)), ('__NPW__', str(n_pw)),
                 ('__NDOOR__', str(len(DOORS))), ('__KEYS__', keys),
                 ('__STAMP__', datetime.date.today().isoformat())):
        out = out.replace(a, b)
    return out


TEMPLATE = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<title>道具の部屋 | おざけん</title>
<meta name="robots" content="noindex">
<meta name="theme-color" content="#131c33">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Hanken+Grotesk:wght@400;600;700&family=Shippori+Mincho+B1:wght@500;600&family=Zen+Kaku+Gothic+New:wght@400;500;700;800&display=swap" rel="stylesheet">
<style>
:root{--navy:#1f3864;--navy-deep:#131c33;--azure:#2e5496;--azure-pale:#d8e4f0;
  --red:#e23744;--red-bright:#ff5d6a;--amber:#f0b429;--white:#fff;
  --font-ja-sans:'Zen Kaku Gothic New',sans-serif;
  --font-ja-serif:'Shippori Mincho B1',serif;
  --font-en:'Hanken Grotesk',sans-serif}
*{box-sizing:border-box}
/* **地の色は html にも敷く。** body の背景だけだと、
   本文が画面より長いときに、下のほうが白いまま残る */
html{background:var(--navy-deep)}
body{margin:0;min-height:100vh;
  background:linear-gradient(172deg,#1f3864 0%,#131c33 100%);color:var(--azure-pale);
  font-family:var(--font-ja-sans);line-height:1.9;
  padding:clamp(1.3rem,5vw,3rem) clamp(1.1rem,5vw,2rem) calc(3rem + env(safe-area-inset-bottom));
  -webkit-text-size-adjust:100%}
.wrap{max-width:660px;margin:0 auto}
.eyebrow{display:flex;align-items:center;gap:.7em;font-family:var(--font-en);
  font-size:.6rem;font-weight:700;letter-spacing:.34em;color:var(--amber);margin-bottom:.9rem}
.eyebrow::before{content:"";width:24px;height:1px;background:currentColor;opacity:.7}
h1{font-family:var(--font-ja-sans);font-weight:800;line-height:1.34;
  font-size:clamp(1.5rem,6vw,2.1rem);color:#fff;margin:0 0 .5rem}
.lead{font-size:.86rem;color:rgba(216,228,240,.66);margin:0 0 1.8rem}

.nums{display:grid;grid-template-columns:repeat(3,1fr);gap:.5rem;margin-bottom:1.8rem}
.num{border:1px solid rgba(159,198,245,.18);border-radius:10px;
  background:rgba(159,198,245,.06);padding:.7rem .5rem;text-align:center}
.num b{display:block;font-family:var(--font-en);font-size:1.5rem;font-weight:700;
  line-height:1;color:#fff}
.num i{display:block;font-style:normal;font-size:.62rem;letter-spacing:.04em;
  color:rgba(216,228,240,.55);margin-top:.35rem}

.doors{display:flex;flex-direction:column;gap:.6rem}
.door{display:flex;align-items:center;gap:.85rem;text-decoration:none;
  border:1px solid rgba(159,198,245,.2);border-radius:12px;
  background:rgba(159,198,245,.07);padding:.95rem 1rem;color:#fff;
  -webkit-tap-highlight-color:transparent;transition:background .18s,transform .18s}
.door:active{background:rgba(159,198,245,.18);transform:scale(.99)}
@media(hover:hover){.door:hover{background:rgba(159,198,245,.13)}}
.door .k{flex:none;min-width:2.4em;padding:.3em .45em;border-radius:5px;text-align:center;
  background:rgba(240,180,41,.16);color:var(--amber);
  font-family:var(--font-en);font-size:.62rem;font-weight:700;letter-spacing:.12em}
.door .b{flex:1;min-width:0}
.door .b b{display:block;font-size:.98rem;font-weight:700;line-height:1.5}
.door .b i{display:block;font-style:normal;font-size:.72rem;line-height:1.7;
  color:rgba(216,228,240,.58)}
.door .go{flex:none;font-family:var(--font-en);color:rgba(159,198,245,.5)}

.note{margin-top:1.8rem;padding-top:1.2rem;border-top:1px solid rgba(159,198,245,.14);
  font-size:.74rem;line-height:1.9;color:rgba(216,228,240,.5)}
.note b{color:rgba(216,228,240,.78)}
.back{display:inline-flex;align-items:center;gap:.5em;margin-top:1.4rem;
  font-family:var(--font-en);font-size:.66rem;font-weight:700;letter-spacing:.18em;
  color:rgba(159,198,245,.7);text-decoration:none}
.stamp{font-family:var(--font-en);font-size:.58rem;letter-spacing:.2em;
  color:rgba(159,198,245,.35);margin-top:2rem}
</style>
</head>
<body>
<div class="wrap">
  <span class="eyebrow">OZAKEN CMS ／ RESTRICTED</span>
  <h1>道具の部屋</h1>
  <p class="lead">鍵の要るページを、ここに集めています。<br>
    <b>一度解錠していれば、この先はもうパスワードを聞かれません。</b></p>

  <div class="nums">
    <div class="num"><b>__NDOC__</b><i>資料</i></div>
    <div class="num"><b>__NCAT__</b><i>分類</i></div>
    <div class="num"><b>__NPW__</b><i>鍵を記録済み</i></div>
  </div>

  <div class="doors">
__DOORS__
  </div>

  <p class="note">パソコンでは、この__NDOOR__枚に<b>2文字のキー</b>（__KEYS__）でも飛べます。
    スマートフォンでは、玄関の<b>3つの要素を順にタップ</b>すると、この部屋が開きます。</p>

  <a class="back" href="index.html">← ARCHIVE TOP</a>
  <p class="stamp">GENERATED __STAMP__</p>
</div>
</body>
</html>
"""


def main():
    pw = os.environ.get('OZAKEN_PW') or sys.exit('OZAKEN_PW を設定してください')
    page = build(pw)
    if os.path.exists(OUT):
        # 鍵は作り直さない。配ってあるものが死ぬので
        lockbox.encrypt(OUT, pw, page)
        how = '更新'
    else:
        lockbox.create(os.path.join(ROOT, 'backstage.html'), page, OUT, [pw])
        how = '新規作成'
    assert lockbox.decrypt(OUT, pw) == page
    print('道具の部屋を%sしました（扉 %d 枚）' % (how, len(DOORS)))


if __name__ == '__main__':
    main()
