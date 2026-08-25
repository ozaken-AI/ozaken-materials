#!/usr/bin/env python3
"""既存の全資料を、いまの規定で点検する。

新しく作る資料は publish.py が公開前に弾くが、
規定を決める前に作った資料は、そのまま残っている。
どれがどれだけ外れているかを一覧にして、直す順番を決めるための道具。

  OZAKEN_PW=マスター python3 lint_all.py            # 要約だけ
  OZAKEN_PW=マスター python3 lint_all.py --detail   # 資料ごとの中身も出す
  OZAKEN_PW=マスター python3 lint_all.py --wakaru   # わかりにくさだけを一覧にする
"""
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lockbox
import registry
from build_page import check, check_tokens
from check_wakaru import check_wakaru
from crossref_data import NOT_DOCS, NOT_DECKS

PW = os.environ.get('OZAKEN_PW') or sys.exit('OZAKEN_PW を設定してください')
DETAIL = '--detail' in sys.argv
WAKARU = '--wakaru' in sys.argv


def wakaru():
    """**わかりにくさは、色の乱れと同じくらい資料を壊す。**
    色は check_tokens が弾いてきたが、中身は誰も見ていなかった。
    直す順番を決めるために、指摘の多い順に並べる"""
    files = [f for f in registry.docs() if os.path.basename(f) not in NOT_DOCS]
    rows, total = [], 0
    for f in files:
        rel = os.path.relpath(f, registry.ROOT)
        got = check_wakaru(lockbox.decrypt(f, PW))
        total += len(got)
        if got:
            rows.append((len(got), rel, got))
    rows.sort(reverse=True)
    print('資料 %d 本 ／ 指摘のある資料 %d 本 ／ 指摘 %d 件\n'
          % (len(files), len(rows), total))
    kinds = Counter(g.split('「')[0] for _, _, got in rows for g in got)
    for k, n in kinds.most_common():
        print('  %-28s %3d 件' % (k.strip(), n))
    print()
    for n, rel, got in rows:
        print('■ %s（%d件）' % (rel, n))
        for g in got:
            print('   ・' + g)


def main():
    if WAKARU:
        return wakaru()
    # 置き場・索引・台帳は資料ではない。道具としてのページなので規定の外
    # **板（ダッシュボード）は、投影して話す資料ではない。**
    # 面の交互も図版主導も当てはまらないので、型の検査からは外す
    files = [f for f in registry.docs()
             if os.path.basename(f) not in NOT_DOCS
             and os.path.relpath(f, registry.ROOT) not in NOT_DECKS]
    colors, issues, clean = Counter(), [], 0
    kinds = Counter()
    for f in files:
        rel = os.path.relpath(f, registry.ROOT)
        html = lockbox.decrypt(f, PW)
        try:
            errs, _ = check(html)
        except Exception as e:            # 構成が特殊で検査器が通らない資料もある
            errs = ['検査器が通らない: %s' % e]
        tok = check_tokens(html)
        # **色と書体の指摘は、check() の戻りにも入っている。**
        # 両方を足すと同じものを二度数えるので、ここで落とす
        errs = [m for m in errs if m not in tok]
        if not tok and not errs:
            clean += 1
        else:
            issues.append((rel, tok, errs))
            for m in tok:
                if m.startswith('規定外の色'):
                    for c in m.split(': ', 1)[1].split('（')[0].split():
                        colors[c] += 1
            for m in errs:
                kinds[m.split(':')[0].split('（')[0].strip()[:28]] += 1

    # **「規定どおり」は、色と書体だけの話ではない。**
    # 以前はここで check() の結果を捨てていて、色さえ合っていれば
    # 「104本すべて規定どおり」と出ていた。図のキャプションに残った
    # マークダウンも、扉の長すぎる題も、この数には出てこなかった。
    # 出ない指摘は、無いのと同じ
    print('資料 %d 本 ／ 規定どおり %d 本 ／ 要修正 %d 本\n' % (len(files), clean, len(issues)))
    if colors:
        print('規定外の色（多い順）')
        for c, n in colors.most_common(20):
            print('  %-9s %2d 本' % (c, n))
        print()
    if kinds:
        print('型の指摘（多い順）')
        for k, n in kinds.most_common(20):
            print('  %-42s %3d 本' % (k, n))
    if DETAIL:
        print('\n資料ごとの指摘')
        for rel, tok, errs in issues:
            print('\n■ %s' % rel)
            for m in tok:
                print('    （色・書体）', m)
            for m in errs:
                print('    （型）    ', m)
    else:
        print('\n要修正の資料（先頭20本）')
        for rel, _, _ in issues[:20]:
            print('  ' + rel)
        print('\n中身を見るには --detail を付けて実行')


if __name__ == '__main__':
    main()
