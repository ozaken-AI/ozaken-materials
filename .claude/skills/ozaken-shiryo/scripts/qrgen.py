#!/usr/bin/env python3
"""QRコードを作る。標準ライブラリだけで動く。

会場で「このページを開いてください」と言うために使う。URLを読み上げるのは
無理があるし、短縮URLは外のサービスに依存する。**画面に出せば、それで済む。**

外の部品を持ち込まないのは、資料が暗号化されて配られるから。
実行時に何かを取りに行く作りにすると、鍵の中で外部通信が起きる。
ここで作った升目をビルド時にSVGへ焼いて、資料の中に置く。

対応は **バージョン1〜10・誤り訂正レベルM**（8ビットバイトモード）。
URLは長くても100文字ほどなので、これで足りる。
`segno` が入っている環境では `python3 qrgen.py --verify` で総当たり突き合わせができる。

  from qrgen import svg
  svg('https://example.com/')      # → <svg …> の文字列
"""

# 版ごとの (総コード語数, ブロックあたりの誤り訂正コード語数, [(ブロック数, データ語数), …])
# 誤り訂正レベル M。ISO/IEC 18004 の表9より
SPEC = {
    1:  (26,  10, [(1, 16)]),
    2:  (44,  16, [(1, 28)]),
    3:  (70,  26, [(1, 44)]),
    4:  (100, 18, [(2, 32)]),
    5:  (134, 24, [(2, 43)]),
    6:  (172, 16, [(4, 27)]),
    7:  (196, 18, [(4, 31)]),
    8:  (242, 22, [(2, 38), (2, 39)]),
    9:  (292, 22, [(3, 36), (2, 37)]),
    10: (346, 26, [(4, 43), (1, 44)]),
}

# 位置合わせパターンの中心座標
ALIGN = {
    1: [], 2: [6, 18], 3: [6, 22], 4: [6, 26], 5: [6, 30],
    6: [6, 34], 7: [6, 22, 38], 8: [6, 24, 42], 9: [6, 26, 46], 10: [6, 28, 50],
}

ECL_M = 0b00                      # 形式情報に載る誤り訂正レベルの符号


# ── ガロア体 GF(256) ────────────────────────────────────────
EXP = [0] * 512
LOG = [0] * 256
_x = 1
for _i in range(255):
    EXP[_i] = _x
    LOG[_x] = _i
    _x <<= 1
    if _x & 0x100:
        _x ^= 0x11d                # x^8 + x^4 + x^3 + x^2 + 1
for _i in range(255, 512):
    EXP[_i] = EXP[_i - 255]


def _mul(a, b):
    return 0 if a == 0 or b == 0 else EXP[LOG[a] + LOG[b]]


def _gen_poly(n):
    """誤り訂正用の生成多項式 (x-α^0)(x-α^1)…(x-α^(n-1))"""
    g = [1]
    for i in range(n):
        g = [0] + g
        for j in range(len(g) - 1):
            g[j] ^= _mul(g[j + 1], EXP[i])
    return g[::-1]      # 次数の高いほうを先頭にして返す（_ecc がその順で割る）


def _ecc(data, n):
    """データ語から誤り訂正語を作る（多項式の剰余）"""
    g = _gen_poly(n)
    rem = list(data) + [0] * n
    for i in range(len(data)):
        c = rem[i]
        if c:
            for j in range(len(g)):
                rem[i + j] ^= _mul(g[j], c)
    return rem[len(data):]


# ── 符号化 ──────────────────────────────────────────────────
def _pick(nbytes):
    """入るいちばん小さい版を選ぶ"""
    for v in sorted(SPEC):
        total, ec, blocks = SPEC[v]
        data = sum(n * k for n, k in blocks)
        head = 4 + (8 if v < 10 else 16)          # モード指示子＋文字数指示子
        if data * 8 >= head + nbytes * 8:
            return v
    raise ValueError('この実装で扱える長さを超えています: %d バイト' % nbytes)


def _bits(payload, v):
    total, ec, blocks = SPEC[v]
    cap = sum(n * k for n, k in blocks)
    bits = [0, 1, 0, 0]                            # 8ビットバイトモード
    cnt = 8 if v < 10 else 16
    for i in range(cnt - 1, -1, -1):
        bits.append((len(payload) >> i) & 1)
    for b in payload:
        for i in range(7, -1, -1):
            bits.append((b >> i) & 1)
    bits += [0] * min(4, cap * 8 - len(bits))      # 終端子
    bits += [0] * (-len(bits) % 8)                 # バイト境界まで
    words = [int(''.join(map(str, bits[i:i + 8])), 2) for i in range(0, len(bits), 8)]
    pad = [0xEC, 0x11]
    while len(words) < cap:
        words.append(pad[(len(words) - len(bits) // 8) % 2])
    return words


def _interleave(words, v):
    """ブロックに割ってから、決められた順に組み直す"""
    total, ecn, blocks = SPEC[v]
    data_blocks, ec_blocks, at = [], [], 0
    for n, k in blocks:
        for _ in range(n):
            d = words[at:at + k]
            at += k
            data_blocks.append(d)
            ec_blocks.append(_ecc(d, ecn))
    out = []
    for i in range(max(len(b) for b in data_blocks)):
        for b in data_blocks:
            if i < len(b):
                out.append(b[i])
    for i in range(ecn):
        for b in ec_blocks:
            out.append(b[i])
    return out


# ── 升目に置く ──────────────────────────────────────────────
def _finder(m, res, r, c):
    for i in range(-1, 8):
        for j in range(-1, 8):
            y, x = r + i, c + j
            if not (0 <= y < len(m) and 0 <= x < len(m)):
                continue
            on = (0 <= i <= 6 and j in (0, 6)) or (0 <= j <= 6 and i in (0, 6)) \
                or (2 <= i <= 4 and 2 <= j <= 4)
            m[y][x] = 1 if on else 0
            res[y][x] = 1


def _bch(value, poly, deg):
    v = value << deg
    for i in range(len(bin(v)) - 2 - 1, deg - 1, -1):
        if v & (1 << i):
            v ^= poly << (i - deg)
    return (value << deg) | v


def _place_format(m, res, mask):
    bits = _bch((ECL_M << 3) | mask, 0b10100110111, 10) ^ 0b101010000010010
    n = len(m)
    seq = [(bits >> (14 - i)) & 1 for i in range(15)]   # 上の桁から順に置く
    # 左上
    pos = [(8, 0), (8, 1), (8, 2), (8, 3), (8, 4), (8, 5), (8, 7), (8, 8),
           (7, 8), (5, 8), (4, 8), (3, 8), (2, 8), (1, 8), (0, 8)]
    for b, (r, c) in zip(seq, pos):
        m[r][c] = b
        res[r][c] = 1
    # 右上・左下
    pos2 = [(n - 1, 8), (n - 2, 8), (n - 3, 8), (n - 4, 8), (n - 5, 8), (n - 6, 8), (n - 7, 8),
            (8, n - 8), (8, n - 7), (8, n - 6), (8, n - 5), (8, n - 4), (8, n - 3),
            (8, n - 2), (8, n - 1)]
    for b, (r, c) in zip(seq, pos2):
        m[r][c] = b
        res[r][c] = 1
    m[n - 8][8] = 1                                 # 常に黒い升
    res[n - 8][8] = 1


def _skeleton(v):
    n = v * 4 + 17
    m = [[0] * n for _ in range(n)]
    res = [[0] * n for _ in range(n)]

    _finder(m, res, 0, 0)
    _finder(m, res, 0, n - 7)
    _finder(m, res, n - 7, 0)

    for i in range(8, n - 8):                       # タイミングパターン
        m[6][i] = m[i][6] = 1 - (i % 2)
        res[6][i] = res[i][6] = 1

    centers = ALIGN[v]
    for r in centers:
        for c in centers:
            if (r < 8 and c < 8) or (r < 8 and c > n - 9) or (r > n - 9 and c < 8):
                continue
            for i in range(-2, 3):
                for j in range(-2, 3):
                    m[r + i][c + j] = 1 if max(abs(i), abs(j)) != 1 else 0
                    res[r + i][c + j] = 1

    if v >= 7:                                      # 版情報
        bits = _bch(v, 0b1111100100101, 12)
        for i in range(18):
            b = (bits >> i) & 1
            m[i // 3][n - 11 + i % 3] = b
            res[i // 3][n - 11 + i % 3] = 1
            m[n - 11 + i % 3][i // 3] = b
            res[n - 11 + i % 3][i // 3] = 1

    for i in range(9):                              # 形式情報の席を先に取る
        for r, c in ((8, i), (i, 8)):
            if r < n and c < n:
                res[r][c] = 1
    for i in range(8):
        res[8][n - 1 - i] = 1
        res[n - 1 - i][8] = 1
    res[n - 8][8] = 1
    return m, res


def _fill(m, res, words):
    n = len(m)
    bits = [(w >> i) & 1 for w in words for i in range(7, -1, -1)]
    at, up, col = 0, True, n - 1
    while col > 0:
        if col == 6:
            col -= 1                                # 縦のタイミングパターンは飛ばす
        rows = range(n - 1, -1, -1) if up else range(n)
        for r in rows:
            for c in (col, col - 1):
                if res[r][c]:
                    continue
                m[r][c] = bits[at] if at < len(bits) else 0
                at += 1
        up = not up
        col -= 2


def _masked(m, res, mask):
    f = [
        lambda r, c: (r + c) % 2 == 0,
        lambda r, c: r % 2 == 0,
        lambda r, c: c % 3 == 0,
        lambda r, c: (r + c) % 3 == 0,
        lambda r, c: (r // 2 + c // 3) % 2 == 0,
        lambda r, c: (r * c) % 2 + (r * c) % 3 == 0,
        lambda r, c: ((r * c) % 2 + (r * c) % 3) % 2 == 0,
        lambda r, c: ((r + c) % 2 + (r * c) % 3) % 2 == 0,
    ][mask]
    n = len(m)
    return [[m[r][c] ^ (1 if (not res[r][c] and f(r, c)) else 0)
             for c in range(n)] for r in range(n)]


def _penalty(m):
    n = len(m)
    p = 0
    lines = [list(row) for row in m] + [[m[r][c] for r in range(n)] for c in range(n)]
    for line in lines:                              # 規則1：同じ色の連続
        run, prev = 1, line[0]
        for v in line[1:]:
            if v == prev:
                run += 1
            else:
                if run >= 5:
                    p += 3 + run - 5
                run, prev = 1, v
        if run >= 5:
            p += 3 + run - 5
    for r in range(n - 1):                          # 規則2：2×2の同色
        for c in range(n - 1):
            if m[r][c] == m[r][c + 1] == m[r + 1][c] == m[r + 1][c + 1]:
                p += 3
    pat = [1, 0, 1, 1, 1, 0, 1, 0, 0, 0, 0]
    for line in lines:                              # 規則3：紛らわしい並び
        for i in range(len(line) - 10):
            if line[i:i + 11] == pat or line[i:i + 11] == pat[::-1]:
                p += 40
    dark = sum(sum(row) for row in m)               # 規則4：白黒の偏り
    p += abs(dark * 100 // (n * n) - 50) // 5 * 10
    return p


def matrix(text):
    """QRの升目（1が黒）を返す"""
    payload = text.encode('utf-8')
    v = _pick(len(payload))
    words = _interleave(_bits(payload, v), v)
    m, res = _skeleton(v)
    _fill(m, res, words)
    best, score = None, None
    for mask in range(8):
        cand = _masked(m, res, mask)
        c2 = [row[:] for row in cand]
        _place_format(c2, [row[:] for row in res], mask)
        s = _penalty(c2)
        if score is None or s < score:
            best, score = c2, s
    return best


def svg(text, quiet=3):
    """QRをSVGの文字列にする。色は指定せず、currentColor で描く"""
    m = matrix(text)
    n = len(m)
    size = n + quiet * 2
    d = []
    for r, row in enumerate(m):
        c = 0
        while c < n:
            if row[c]:
                w = 1
                while c + w < n and row[c + w]:
                    w += 1
                d.append('M%d %dh%dv1h-%dz' % (c + quiet, r + quiet, w, w))
                c += w
            else:
                c += 1
    return ('<svg viewBox="0 0 %d %d" xmlns="http://www.w3.org/2000/svg" '
            'shape-rendering="crispEdges" role="img" aria-label="QRコード">'
            '<rect width="%d" height="%d" fill="#fff"/>'
            '<path d="%s" fill="#141d35"/></svg>'
            % (size, size, size, size, ''.join(d)))


if __name__ == '__main__':
    import sys
    if '--verify' in sys.argv:
        # 実際に読み取れるかで確かめる。他の実装と升目を突き合わせても、
        # 詰め物の付け方が実装ごとに違うので一致しない（規格上はどちらも正しい）
        import cv2                                  # 検証用。実行時には要らない
        import numpy as np
        samples = [
            'https://ozaken-ai.github.io/ozaken-materials/',
            'https://ozaken-ai.github.io/ozaken-materials/Training/msa-life-training.html',
            'https://ozaken-ai.github.io/ozaken-materials/AX_Table/s4-setsumei-dekiru-seika.html',
            'https://ozaken-ai.github.io/ozaken-materials/05_drive/keiei-data-kiban.html',
            'a', 'x' * 60, 'y' * 120, 'z' * 200,
            'https://example.com/?q=' + 'ab' * 40,
        ]
        ng = 0
        for s in samples:
            m = matrix(s)
            n = len(m)
            q, z = 4, 8                             # 余白4升、1升8ピクセル
            img = np.full(((n + q * 2) * z,) * 2, 255, dtype=np.uint8)
            for r in range(n):
                for c in range(n):
                    if m[r][c]:
                        img[(r + q) * z:(r + q + 1) * z, (c + q) * z:(c + q + 1) * z] = 0
            got, _, _ = cv2.QRCodeDetector().detectAndDecode(img)
            ok = got == s
            ng += 0 if ok else 1
            print('%s  %3d文字 版%-2d %s' % ('読めた ' if ok else 'NG!  ', len(s),
                                             (n - 17) // 4, s[:44]))
        sys.exit(ng and '読み取れないものがあります')
    print(svg(sys.argv[1] if len(sys.argv) > 1 else 'https://example.com/'))
