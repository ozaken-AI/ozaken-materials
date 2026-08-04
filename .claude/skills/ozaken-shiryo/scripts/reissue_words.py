#!/usr/bin/env python3
"""個別パスワードを、やさしい英単語3つのつなぎに付け替える。

例: honey-panda-moon

各資料の鍵を「マスター／共通／新しい個別」の3本に張り直す。本文は触らない。
綴りに迷わない短い語だけを選んである（同音・紛らわしい語は入れていない）。
"""
import html as H
import os
import re
import secrets
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lockbox
import registry

ROOT = registry.ROOT
MASTER = os.environ.get('OZAKEN_PW', '')   # 実行時のみ必要。読み込みでは落とさない
COMMON = os.environ.get('OZAKEN_COMMON', 'O29daisuki')

WORDS = """
apple bagel bamboo banana bear berry bird bloom blue boat bread bubble bunny
butter candy cat cherry chick cloud clover cocoa coco comet cookie coral cosmos
cotton cozy cream daisy dango deer donut dove dream drop duck feather fern fig
flower fluffy forest fox frog garden ginger glow grape green happy hazel heart
hill honey hop ice ivy jam jelly juice kite koala lake lamb latte leaf lemon
lily lime linen lotus lucky maple marble melon milk mint mochi moon moss muffin
nest night ocean olive orange otter owl panda peach pear pebble petal piano
pine pink plum pocket polar pond poppy puddle puffin pumpkin rabbit rain
rainbow ribbon rice river robin rose sail sakura salt sand seed sesame shell
shine silver sky sleepy smile snow socks soda soft spark spring sprout star
stone sugar summer sun sunny sweet tea teddy tiny toast tulip turtle twig
velvet violet waffle walnut warm water wave whale wheat willow wind wing
winter wish wolf wonder wool yarn yuzu zebra
""".split()


def gen(used):
    while True:
        pw = '-'.join(secrets.choice(WORDS) for _ in range(3))
        w = pw.split('-')
        if len(set(w)) == 3 and pw not in used:      # 同じ語の重複は避ける
            used.add(pw)
            return pw


def main():
    if not MASTER:
        sys.exit('OZAKEN_PW を設定してください')
    print('語彙 %d 語 → 組み合わせ %s 通り' % (len(WORDS), format(len(WORDS) ** 3, ',')))
    files = registry.docs()
    data = registry.load(MASTER)
    used = set()
    for f in files:
        rel = os.path.relpath(f, ROOT)
        inner = lockbox.decrypt(f, MASTER)
        m = re.search(r'<title>(.*?)</title>', inner, re.S)
        title = H.unescape(m.group(1)).split('|')[0].strip() if m else rel

        pw = gen(used)
        lockbox.create(f, inner, f, [MASTER, COMMON, pw])
        for k in (MASTER, COMMON, pw):
            assert lockbox.decrypt(f, k) == inner, (rel, k)

        e = data.setdefault(rel, {})
        e.update({'pw': pw, 'title': title, 'keys': 3,
                  'at': registry.datetime.date.today().isoformat()})
        e.setdefault('to', '')
        print('  %-44s %s' % (rel[:44], pw))

    data['_meta'] = {'common': COMMON}
    registry.save(MASTER, data)
    print('\n%d 本を付け替えて、台帳に記録しました' % len(files))


if __name__ == '__main__':
    main()
