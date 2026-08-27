#!/usr/bin/env python3
"""資料に注入した塊が、全部そろっているかを見張る。

**この道具は、事故のあとに作った。**
`crossref.py strip` が「印から </style> まで」を切っていたせいで、
あとから積まれた OZ-BODYSTYLE や OZ-HEROFX まで巻き添えで消え、
**92本の資料から表紙の演出と本文の体裁が丸ごと失われた**。
1本あたり32,000字が消えていたのに、検査は全部通っていた。
`build_page.check()` は「本文が何本あるか」しか見ないので、
CSSが消えても気づけない。

そこで、いまの状態を控えとして保存しておき、
**一括で書き換えたあとに「減っていないか」だけを見る**。
何が正しいかを決めるのではなく、**減ったことに気づく**のが仕事。
資料ごとに持っている塊は違う（図版の無い資料には FIGFLOW が無い）ので、
あるべき一覧を決め打ちにはしない。

  OZAKEN_PW=… python3 check_blocks.py         # 控えと突き合わせる
  OZAKEN_PW=… python3 check_blocks.py save    # いまの状態を控えにする

**一括で書き換える道具を走らせる前に控えを取り、走らせた後に見る。**
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lockbox
import oz_root
import registry

ROOT = oz_root.root(HERE)
SNAP = os.path.join(HERE, 'blocks_snapshot.json')

# 注入される塊の印。増やしたらここに足す
BLOCKS = ('OZ-SPACING', 'OZ-BG', 'OZ-HEROFX', 'OZ-FIGFLOW', 'OZ-HOME',
          'OZ-BODYSTYLE', 'OZ-HEROSIZE', 'OZ-XREFCSS', 'OZ-QR', 'OZ-KIT')


def survey(pw):
    """いま、どの資料がどの塊を持っていて、本文が何字あるか"""
    out = {}
    for f in registry.docs():
        rel = os.path.relpath(f, ROOT)
        try:
            html = lockbox.decrypt(f, pw)
        except SystemExit:
            continue
        out[rel] = {'blocks': sorted(b for b in BLOCKS if b in html),
                    'chars': len(html)}
    return out


def main():
    pw = os.environ.get('OZAKEN_PW') or sys.exit('OZAKEN_PW を設定してください')
    now = survey(pw)

    if len(sys.argv) > 1 and sys.argv[1] == 'save':
        json.dump(now, open(SNAP, 'w', encoding='utf-8'),
                  ensure_ascii=False, indent=1, sort_keys=True)
        print('控えを取りました: %d 本' % len(now))
        return

    if not os.path.exists(SNAP):
        sys.exit('控えがありません。先に `check_blocks.py save` を実行してください。')
    old = json.load(open(SNAP, encoding='utf-8'))

    lost, shrunk, gone = [], [], []
    for rel, was in old.items():
        if rel not in now:
            gone.append(rel)
            continue
        missing = sorted(set(was['blocks']) - set(now[rel]['blocks']))
        if missing:
            lost.append((rel, missing))
        # **1割以上縮んだら疑う。** 節を1本消しただけでも1割は減らない
        if now[rel]['chars'] < was['chars'] * 0.9:
            shrunk.append((rel, was['chars'], now[rel]['chars']))

    added = sorted(set(now) - set(old))
    print('資料 %d 本（控え %d 本）' % (len(now), len(old)))
    if added:
        print('  新しく増えた: %s' % ' '.join(added))
    if gone:
        print('\n✗ 控えにあった資料が見当たらない %d 本' % len(gone))
        for r in gone[:20]:
            print('   ', r)
    if lost:
        print('\n✗ 塊が消えた %d 本' % len(lost))
        for r, m in lost[:20]:
            print('    %-44s %s' % (r, ' '.join(m)))
    if shrunk:
        print('\n✗ 本文が1割以上縮んだ %d 本' % len(shrunk))
        for r, a, b in shrunk[:20]:
            print('    %-44s %d字 → %d字' % (r, a, b))
    if not (lost or shrunk or gone):
        print('\n減ったものはありません。')
    else:
        print('\n**一括で書き換える道具が、余分に消していないかを疑ってください。**')
        sys.exit(1)


if __name__ == '__main__':
    main()
