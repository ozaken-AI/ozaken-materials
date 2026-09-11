#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""記事の「読まれる形」を作る。題・つかみ・ハッシュタグ。

note で読まれるかは、本文より先に**題と見出し画像**で決まる。
ここはその2つを作るところ。本文の文には触れない。

**候補はすべて、おざけん自身が資料に書いた文から採る。**
題をゼロから作文すると、資料に書いていないことを言い出す。そうではなく、
資料の中にすでにある強い一文を見つけて、note の作法で採点して並べる。
選ぶのは人。

## 長さの根拠（note公式ヘルプと、表示の実測記事）

- note公式のすすめは **15〜25字**
- スマホの note トップの一覧は **26字**で切れる。検索結果は31字、
  クリエイターページは36字。いちばん狭い26字に合わせるのが安全
- 切れた題はクリックされにくい

資料の題は「◯◯とは何か ─ ……」の二部構成が多く、たいてい29〜34字ある。
**そのまま note に出すと一覧で切れる。** だから面の題やワンポイントから、
短くて強い候補を作る。
"""
import re

SAFE = 26          # note トップの一覧で切れない長さ
IDEAL = (15, 25)   # note公式のすすめ
CUT = 31           # 検索結果でも切れ始める

# 対比・逆接。おざけんの資料の題はこの型が多く、note でも強い
TURN = re.compile(r'ではなく|ではない|じゃない|よりも|より先|の前に|だけ|ほど|むしろ'
                  r'|しかし| but|から.+へ|は、?.*ない')
# 問いかけ
ASK = re.compile(r'とは|なぜ|どこまで|どうやって|何が|何を|どちら|のか|ですか|\?|？')
NUM = re.compile(r'[0-9０-９]')
# 二部構成の区切り。資料の題はここで割れている
SPLIT = re.compile(r'\s*[─―—]\s*|\s+[-–]\s+')
NOISE = re.compile(r'[！!？?【】★☆…]')


def score_title(t):
    """note の題としての点。数えられるものだけで見る"""
    n = len(t)
    why = {}

    if n < 12:
        why['長さ'] = 10          # 短すぎて、何の記事なのかが分からない
    elif n < IDEAL[0]:
        why['長さ'] = 22
    elif n <= IDEAL[1]:
        why['長さ'] = 30
    elif n <= SAFE:
        why['長さ'] = 24
    elif n <= CUT:
        why['長さ'] = 8           # note トップの一覧では切れる
    else:
        why['長さ'] = -14         # どこでも切れる

    # 二部構成は、前半だけで意味が通るかが分かれ目。
    # 一覧で後半が落ちたとき、前半が名前だけだと何の記事か分からなくなる
    parts = SPLIT.split(t)
    if len(parts) > 1:
        head = parts[0]
        why['二部'] = 4 if len(head) >= 10 else -8

    why['対比'] = 12 if TURN.search(t) else 0
    why['問い'] = 8 if ASK.search(t) else 0
    why['具体'] = 8 if NUM.search(t) else 0
    # かぎ括弧ひと組は、引用として目が留まる。多すぎると散らかる
    q = t.count('「')
    why['括弧'] = 5 if q == 1 else (-5 if q >= 3 else 0)
    # 記号を盛ると煽りに見える。おざけんは本名で出しているので、そこは割に合わない
    noise = len(NOISE.findall(t))
    why['記号'] = -6 * noise if noise else 0

    return sum(why.values()), {k: v for k, v in why.items() if v}


def _clean(s):
    """前後の空白を詰め、**全体がかぎ括弧で囲まれているときだけ**外す。

    「来る日」ではなく… のように、頭が括弧で始まるだけの文から開き括弧を外すと、
    閉じ括弧だけが残って壊れる。囲みかどうかは、両端で見る。
    """
    s = re.sub(r'\s+', ' ', (s or '')).strip()
    for a, b in (('「', '」'), ('『', '』')):
        if s.startswith(a) and s.endswith(b) and s.count(a) == 1:
            return s[1:-1]
    return s


def title_candidates(doc, picks):
    """題の候補を、資料の中の文から集めて並べる。

    kind は台帳に残す。どの型が効いたかを、あとでスキ数と突き合わせるため。
    """
    seen, out = set(), []

    def add(text, kind):
        t = _clean(text)
        if not t or len(t) < 8 or t in seen:
            return
        seen.add(t)
        pt, why = score_title(t)
        out.append({'text': t, 'kind': kind, 'score': pt, 'why': why, 'chars': len(t)})

    add(doc['title'], 'deck')                    # 資料の題。たいてい長い
    # 二部構成の資料の題は、後半だけのほうが短くて強いことがある
    for part in SPLIT.split(doc['title']):
        add(part, 'deck-half')
    for k in picks:
        s = doc['sections'][k - 1]
        add(s['title'], 'section')
        add(s['take'], 'take')                   # ワンポイントは断定が多く、強い
        for f in s['figs']:
            add(f['title'], 'fig')               # 図版の題も断定が多い
    out.sort(key=lambda c: (-c['score'], c['chars']))
    return out


def phrase_candidates(doc, picks, limit=20):
    """見出し画像に載せるつかみ。**一覧では小さく出るので、短いほど効く**"""
    seen, out = set(), []
    for k in picks:
        s = doc['sections'][k - 1]
        for text, kind in [(s['take'], 'take'), (s['title'], 'section')] + \
                          [(f['title'], 'fig') for f in s['figs']]:
            t = _clean(text)
            # 長いものは、最初の句で切ると一文の言い切りになることが多い
            if t and len(t) > limit and '。' in t:
                t = t.split('。')[0] + '。'
            if not t or not (6 <= len(t) <= limit) or t in seen:
                continue
            seen.add(t)
            # 言い切りで終わるものを上に。体言止めより目が留まる
            end = 10 if re.search(r'(。|ない|動く|変わる|終わる|始まる|だ|である)$', t) else 0
            out.append({'text': t, 'kind': kind, 'score': end + (20 - abs(14 - len(t))),
                        'chars': len(t)})
    out.sort(key=lambda c: -c['score'])
    return out


def report(cands, n=8, label='題'):
    lines = ['%s の候補（note公式のすすめは15〜25字、スマホの一覧は26字で切れる）:' % label]
    for c in cands[:n]:
        why = ' '.join('%s%+d' % kv for kv in c.get('why', {}).items())
        lines.append('  %3d [%-10s %2d字] %s' % (c['score'], c['kind'], c['chars'], c['text']))
        if why:
            lines.append('        %s' % why)
    return '\n'.join(lines)
