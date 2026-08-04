#!/usr/bin/env python3
"""既存の全資料を、いまの規定で点検する。

新しく作る資料は publish.py が公開前に弾くが、
規定を決める前に作った資料は、そのまま残っている。
どれがどれだけ外れているかを一覧にして、直す順番を決めるための道具。

  OZAKEN_PW=マスター python3 lint_all.py            # 要約だけ
  OZAKEN_PW=マスター python3 lint_all.py --detail   # 資料ごとの中身も出す
"""
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lockbox
import registry
from build_page import check, check_tokens

PW = os.environ.get('OZAKEN_PW') or sys.exit('OZAKEN_PW を設定してください')
DETAIL = '--detail' in sys.argv


def main():
    files = registry.docs()
    colors, issues, clean = Counter(), [], 0
    for f in files:
        rel = os.path.relpath(f, registry.ROOT)
        html = lockbox.decrypt(f, PW)
        try:
            errs, _ = check(html)
        except Exception as e:            # 構成が特殊で検査器が通らない資料もある
            errs = ['検査器が通らない: %s' % e]
        # 演出の注入で本文の並びは変わらないが、AX Tableなど構成が特殊な資料もある。
        # ここでは色と書体だけを見て、構成の指摘は参考に留める
        tok = check_tokens(html)
        if not tok:
            clean += 1
        else:
            issues.append((rel, tok, errs))
            for m in tok:
                if m.startswith('規定外の色'):
                    for c in m.split(': ', 1)[1].split('（')[0].split():
                        colors[c] += 1

    print('資料 %d 本 ／ 規定どおり %d 本 ／ 要修正 %d 本\n' % (len(files), clean, len(issues)))
    if colors:
        print('規定外の色（多い順）')
        for c, n in colors.most_common(20):
            print('  %-9s %2d 本' % (c, n))
    if DETAIL:
        print('\n資料ごとの指摘')
        for rel, tok, errs in issues:
            print('\n■ %s' % rel)
            for m in tok:
                print('   ', m)
            for m in errs:
                if m not in tok:
                    print('    （構成）', m)
    else:
        print('\n要修正の資料（先頭20本）')
        for rel, _, _ in issues[:20]:
            print('  ' + rel)
        print('\n中身を見るには --detail を付けて実行')


if __name__ == '__main__':
    main()
