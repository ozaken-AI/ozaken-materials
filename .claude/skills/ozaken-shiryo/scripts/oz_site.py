#!/usr/bin/env python3
"""公開しているURLを、1か所に持つ。

**以前は apply_qr.py と apply_ogp.py の両方に同じURLを書いていた。**
QRの升目にも、共有カードの og:url にも、資料の本文にも焼き込まれるので、
引っ越すときに片方だけ直すと、会場のスクリーンに古いURLが出る。

引っ越すときは、ここを直してから `retarget.py` を通す。
"""

# 配信しているところ。**末尾のスラッシュを落とさない**
SITE = 'https://content.ozaken.ai/'

# 画面に出すときの見せ方（httpsを外した形）。資料の本文やQRの下に出る
def bare(url=None):
    return (url or SITE).replace('https://', '').replace('http://', '').rstrip('/')


if __name__ == '__main__':
    print(SITE)
    print(bare())
