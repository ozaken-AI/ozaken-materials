#!/usr/bin/env python3
"""組版を通さない1枚もの（板）を、鍵を保ったまま資料の中へ入れる。

**資料の型に合わないものが、たまにある。**
9面18図・明暗の交互・図版主導という型は、投影して話す資料のためのもので、
ダッシュボードのように「開いた瞬間に現在地が分かる」ことを求められる
1枚ものには当てはまらない。導入文もカードも要らないし、
面を交互に並べる意味もない。

そういう1枚ものは publish.py（build_page → check → 演出）を通さず、
出来上がったHTMLをそのまま鍵の中へ入れる。

  python3 ../sources/gen_jobs_board.py
  OZAKEN_PW=マスター python3 put_board.py /tmp/board_jobs.html 12_jobs/us-jp-employment.html

**鍵は作り直さない。** lockbox.encrypt なので、配布済みのパスワードは生きたまま。
入れたあと apply_ogp を通して、SNSに貼ったときの題と概要も更新する。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lockbox
import oz_root

ROOT = oz_root.root(HERE)


def main():
    pw = os.environ.get('OZAKEN_PW') or sys.exit('OZAKEN_PW を設定してください')
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    src, rel = sys.argv[1], sys.argv[2]
    dst = os.path.join(ROOT, rel)
    if not os.path.exists(dst):
        sys.exit('%s がありません。新規なら publish.py で1度作ってください' % rel)

    page = open(src, encoding='utf-8').read()
    if '<!DOCTYPE' not in page[:200]:
        sys.exit('1枚もののHTMLを渡してください（本文フラグメントではなく）')

    lockbox.encrypt(dst, pw, page)
    assert lockbox.decrypt(dst, pw) == page
    print('差し替えました: %s（%d 文字・鍵はそのまま）' % (rel, len(page)))

    import apply_ogp
    apply_ogp.manifest(pw)
    apply_ogp.patch(rel, pw)
    print('OGPを更新しました。画像は: OZAKEN_PW=… python3 apply_ogp.py cards')


if __name__ == '__main__':
    main()
