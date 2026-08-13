#!/usr/bin/env python3
"""「読んだ人に通じるか」を機械で見る。

**色や書体は check_tokens が弾いてきたのに、
中身のわかりづらさは誰も見ていなかった。**
実際に出た事故は、どれも同じ形をしている。

  「6月の増加ペースは……」   ← 何の増加か書いていない
  「200名超が署名した」       ← 何の声明か書いていない
  「ダロン・アセモグルまで」   ← 誰なのか書いていない
  「BLSはソフト開発職を……」  ← 略語のまま置いた

共通しているのは、**書いた本人の頭の中にはある主語が、
紙の上に出ていない**こと。図やリードを読んでいれば分かる、
という前提が入り込んでいる。ところがカードは単独で読まれる。
投影中に1枚だけ写る場面もある。だからカードは、
それ単体で意味が通る状態にしておく必要がある。

ここでは、機械で確実に拾える形だけを検査する。
拾えないもの（比喩の飛躍、論理の飛び）は SKILL.md の
「わかりやすさのレギュレーション」で人が見る。

  python3 check_wakaru.py <資料のパス>       # 1本を見る
  OZAKEN_PW=マスター python3 lint_all.py --wakaru   # 全部を見る
"""
import re
import sys

# ── 説明しなくてよい略語 ─────────────────────────────
# 日本語のビジネス文書にそのまま出てきて、まず引っかからないものだけ。
# 迷ったら入れない。入れすぎると、この検査は何も言わなくなる
KNOWN = {
    'AI', 'IT', 'DX', 'PC', 'URL', 'QR', 'PDF', 'API', 'SNS', 'EC', 'HP',
    'CEO', 'CTO', 'CIO', 'COO', 'KPI', 'ROI', 'OK', 'NG', 'MTG', 'FAQ',
    'HTML', 'CSS', 'CSV', 'SVG', 'PNG', 'JPG', 'ID', 'OS', 'UI', 'UX',
    'RPA', 'SaaS', 'BI', 'CRM', 'ERP', 'MA', 'SFA', 'BPO', 'SI', 'PoC',
    'B2B', 'B2C', 'BtoB', 'BtoC', 'RAG', 'LLM', 'GPU', 'CPU', 'VPN',
    'IP', 'PII', 'GDPR', 'NDA', 'QA', 'AB', 'PM', 'PL', 'HR', 'CX', 'EX',
    'AX', 'CoE', 'OJT', 'SECI', 'JD', 'PDCA', 'SLA', 'MVP', 'ROIC',
    # 日本語の記事にそのまま出てくる、説明が要らない固有名詞
    'MIT', 'IBM', 'MBA', 'NY', 'AICX', 'GAFA', 'NPO', 'JR', 'NTT', 'ANA', 'JAL',
    'BLS', 'GPT', 'DB', 'SQL', 'MCP', 'NEC', 'PoC', 'SIer', 'LINE', 'HUB', 'CS',
}

# 図や見出しに英字のまま置く語。略語ではないので検査から外す
ENGLISH_WORDS = {
    'WHY', 'WHAT', 'HOW', 'WHO', 'WHEN', 'WHERE', 'VS', 'AND', 'OR', 'THE',
    'NEW', 'ALL', 'YES', 'NOW', 'ONE', 'TWO', 'FOR', 'YOU', 'WE', 'ACT',
    'BEFORE', 'AFTER', 'STEP', 'CASE', 'DATA', 'FREE', 'MORE', 'NEXT',
}

# 「AIエージェント・ストラテジスト」のような役割の名前は人名ではない。
# 片方にこの語が入っていたら、人名の検査から外す
ROLE_WORDS = ('ストラテジスト', 'エンジニア', 'アーキテクト', 'オペレーター',
              'マネージャー', 'マネジャー', 'デザイナー', 'ディレクター',
              'コンサルタント', 'プロデューサー', 'エージェント', 'リーダー',
              'サポート', 'スペシャリスト', 'アナリスト', 'プランナー',
              'リスク', 'コンプラ', 'セキュリティ', 'マーケ', 'データ',
              'クラウド', 'システム', 'ツール', 'サービス', 'プロセス')

# 人名の直前・直後に置かれていれば「誰か」が分かる語
TITLES = ('教授', '学者', '研究者', '博士', '氏', '創業', '社長', '会長',
          '記者', '作家', '思想家', '評論家', '受賞', 'CEO', 'CTO', '元',
          '所長', '代表', '大臣', '知事', '弁護士', '医師', '監督', '選手')

# カードの1文目に置くと、指す先が無くなる語
# 「ここでは」のような自分の面を指す語は外す。指す先が紙の上にあるので困らない
DEICTIC = ('この', 'その', 'これ', 'それ', 'こうした', 'そうした',
           '同社', '同氏', '同調査', '同じ調査')


def _text(html):
    """タグを落として本文だけにする。図の中の文字も対象に含める"""
    s = re.sub(r'<style[\s\S]*?</style>', ' ', html)
    s = re.sub(r'<script[\s\S]*?</script>', ' ', s)
    s = re.sub(r'<[^>]+>', ' ', s)
    return re.sub(r'\s+', ' ', s)


def _cards(html):
    """カード1枚ごとの (見出し, 本文) を返す。カードは単独で読まれる"""
    out = []
    for blk in re.findall(r'<div class="card"[^>]*>([\s\S]*?)</div>', html):
        h = re.search(r'<h3[^>]*>([\s\S]*?)</h3>', blk)
        p = re.search(r'<p[^>]*>([\s\S]*?)</p>', blk)
        if h and p:
            out.append((re.sub(r'<[^>]+>', '', h.group(1)).strip(),
                        re.sub(r'<[^>]+>', '', p.group(1)).strip()))
    return out


def r_acronym(html, text):
    """**略語を、日本語の名前なしで置かない。**
    初出は「日本語名（略語）」か「略語（日本語名）」のどちらかにする"""
    errs = []
    seen = set()
    # **見るのは、日本語の文に混ざって出てくる大文字だけ。**
    # 図の飾りや小見出しの英字（SCROLL, LEVEL, BEFORE …）まで拾いはじめると、
    # この検査は「うるさいだけの検査」になって、誰も見なくなる
    JA = 'ぁ-んァ-ヶ一-龠、。・「」（）ー'
    for m in re.finditer(r'(?<![A-Za-z0-9])[A-Z]{2,6}(?![A-Za-z0-9])', text):
        a = m.group(0)
        if a in KNOWN or a in ENGLISH_WORDS or a in seen:
            continue
        before, after = text[max(0, m.start() - 1):m.start()], text[m.end():m.end() + 1]
        if not (re.match('[%s]' % JA, before or ' ') or re.match('[%s]' % JA, after or ' ')):
            continue                    # 英字だけの中に置かれた語。飾りとみなす
        seen.add(a)
        seen.add(a)
        # 資料のどこかで、日本語の名前と並んでいれば良い。
        # 「日本語名（略語）」「略語（日本語名）」「略語＝日本語名」の3つを認める
        e = re.escape(a)
        near = (re.search(r'[ぁ-んァ-ヶ一-龠][^（(]{1,24}[（(][^）)]{0,12}%s[^）)]{0,12}[）)]' % e, text)
                or re.search(r'%s\s*[（(][^）)]{1,30}[）)]' % e, text)
                or re.search(r'%s\s*[＝=：:][ぁ-んァ-ヶ一-龠]' % e, text))
        if not near:
            errs.append('略語「%s」に日本語の説明がない' % a)
    return errs


def r_person(html, text):
    """**人名は、肩書きとセットで出す。**
    「ダロン・アセモグルまで名を連ねた」は、知っている人にしか効かない"""
    errs = []
    # 「情シス・サポート」のような並びを人名と取り違えないよう、
    # 前後に「・」が続かない、3字以上どうしの組だけを人名とみなす
    for m in re.finditer(r'(?<![ァ-ヶー・])[ァ-ヶー]{3,}・[ァ-ヶー]{3,}(?![ァ-ヶー・])', text):
        name = m.group(0)
        if any(w in name for w in ROLE_WORDS):
            continue
        around = text[max(0, m.start() - 40):m.end() + 30]
        if not any(t in around for t in TITLES):
            errs.append('人名「%s」に肩書きがない' % name)
    return errs


def r_deictic(html, text):
    """**カードを指示語で始めない。**
    カードは単独で読まれるので、「この」の指す先が紙の上に無い"""
    errs = []
    for head, body in _cards(html):
        if body.startswith(DEICTIC):
            errs.append('カード「%s」の本文が指示語で始まる' % head[:22])
    return errs


def r_subject(html, text):
    """**数量の主語を落とさない。**
    「6月の増加ペースは」だけでは、何が増えたのか分からない"""
    errs = []
    bad = re.compile(r'^(?:\d+月の|\d+年の|前年比|同\d|前回比)')
    for head, body in _cards(html):
        first = re.split(r'[。]', body)[0]
        if bad.match(first):
            errs.append('カード「%s」の1文目に主語がない: %s' % (head[:16], first[:26]))
    return errs


def r_figref(html, text):
    """**存在しない図を指さない。** 節を足し引きすると、参照だけが残る"""
    # 図の題は資料の代によって「Fig.1 ──」「Fig.1 —」と形が違う。
    # 区切り記号のどれかが続いていれば、その図はここにあるとみなす
    DEF = r'Fig\.(\d+)\s*[──—–‐\-:：]'
    have = set(re.findall(DEF, text))
    errs = []
    for n in set(re.findall(r'Fig\.(\d+)(?!\s*[──—–‐\-:：])', text)):
        if n not in have:
            errs.append('Fig.%s を参照しているが、その図が無い' % n)
    return errs


RULES = (r_acronym, r_person, r_deictic, r_subject, r_figref)


def check_wakaru(html):
    """わかりにくさの指摘を返す。公開は止めないが、必ず目に入るところに出す"""
    text = _text(html)
    errs = []
    for rule in RULES:
        errs += rule(html, text)
    return errs


if __name__ == '__main__':
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    src = open(sys.argv[1], encoding='utf-8').read()
    if src.startswith('<!--OZAKEN-LOCKED2-->'):
        import lockbox
        src = lockbox.decrypt(sys.argv[1], os.environ['OZAKEN_PW'])
    got = check_wakaru(src)
    print('\n'.join('  ・' + e for e in got) if got else 'わかりにくさの指摘なし')
