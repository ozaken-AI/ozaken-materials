#!/usr/bin/env python3
"""アーカイブの置き場所をさがす。

道具はスキルの中（.claude/skills/ozaken-shiryo/scripts/）に置いてあるが、
相手にする資料はリポジトリの直下にある。
「自分の何階層上」で数えると、道具を動かすたびに全部が壊れるので、
目印になるファイルを見つけるまで上へ辿る。

  OZAKEN_ROOT を設定すれば、それが優先される。
"""
import os

# ここに両方あれば、そこがアーカイブの根。
# index.html だけだと、どの階層にもあり得るので当てにならない
MARKS = ('index.html', 'ask.html')


def find(start):
    d = os.path.abspath(start)
    while True:
        if all(os.path.exists(os.path.join(d, m)) for m in MARKS):
            return d
        up = os.path.dirname(d)
        if up == d:
            raise SystemExit(
                'アーカイブの置き場所が見つかりません。'
                'OZAKEN_ROOT にリポジトリの場所を入れて実行してください。')
        d = up


def root(start=None):
    return os.environ.get('OZAKEN_ROOT') or find(start or os.path.dirname(
        os.path.abspath(__file__)))


# 裏資料の置き場。ここを増やすと、走査するすべての道具が追随する。
# 昔は8本のスクリプトに同じ2つ組を書いていて、
# Training を足したときに5本で for 文の中身を消す事故を起こした。
BACKSTAGE_DIRS = ('AX_Table', 'Training', 'Udemy')
