#!/usr/bin/env python3
"""全資料を復号して、1つのフォルダへ並べる。

描画して確かめる道具（check_overflow.mjs / shot_secs.mjs）に渡すための下ごしらえ。
**中身は平文なので、作業が終わったら消す。**

  OZAKEN_PW=マスター python3 dump_all.py /tmp/oz
"""
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lockbox
import oz_root
import registry

ROOT = oz_root.root(HERE)


def main():
    pw = os.environ.get('OZAKEN_PW') or sys.exit('OZAKEN_PW を設定してください')
    out = sys.argv[1] if len(sys.argv) > 1 else sys.exit(__doc__)
    os.makedirs(out, exist_ok=True)
    n = 0
    for f in registry.docs():
        rel = os.path.relpath(f, ROOT)
        # フォルダの区切りは __ に畳む。file:// で開くときに階層が要らない
        io.open(os.path.join(out, rel.replace('/', '__')), 'w',
                encoding='utf-8').write(lockbox.decrypt(f, pw))
        n += 1
    print('%d 本を %s へ並べました。**終わったら消してください**' % (n, out))


if __name__ == '__main__':
    main()
