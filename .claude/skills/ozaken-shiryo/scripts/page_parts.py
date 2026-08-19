#!/usr/bin/env python3
"""本文フラグメントを組み立てる部品。

資料の骨組み（表紙・セクション・カード・締め）はどの資料でも同じ形なので、
ここに置いて使い回す。以前はこの部品が作業用の一時ディレクトリにあり、
セッションが変わると失われて、資料ごとに書き直す羽目になっていた。

  from page_parts import hero, sec, cards, close, EXTRA_CSS

図版は domain_fig の fig_* が返すHTMLを、そのまま sec(fig=...) に渡す。
複数枚を重ねたいときは '+' で連結する。
"""
from domain_fig import esc

# セクション共通の追加CSS。publish.py の --extra-css に渡す
EXTRA_CSS = """
.lede{font-family:var(--font-ja-serif);font-size:clamp(1.15rem,2.6vw,1.5rem);
  line-height:1.9;margin:.4rem 0 1.6rem}
.sec-navy .lede{color:rgba(255,255,255,.95)}
.cards[data-two]{grid-template-columns:repeat(auto-fit,minmax(300px,1fr))}
.mth{display:inline-block;font-family:var(--font-en);font-size:.62rem;font-weight:700;
  letter-spacing:.14em;color:var(--azure);background:var(--azure-pale);
  padding:2px 8px;border-radius:4px;margin-right:.5em;vertical-align:middle}
.sec-navy .mth{color:#fff;background:rgba(255,255,255,.18)}
.num{font-family:var(--font-en);font-weight:700;font-size:1.06em;letter-spacing:.02em}
/* 配布物のダウンロード。CTAボタンではなく「資料に挟まれた配り物」として置く */
.dl{display:flex;flex-wrap:wrap;align-items:center;gap:1.1rem;
  margin:2.2rem 0 0;padding:1.4rem 1.5rem;border-radius:16px;
  border:1px solid var(--azure-pale);background:rgba(46,84,150,.05)}
.sec-navy .dl{border-color:rgba(255,255,255,.2);background:rgba(255,255,255,.06)}
.dl-body{flex:1 1 300px}
.dl-tag{display:inline-block;font-family:var(--font-en);font-size:.6rem;font-weight:700;
  letter-spacing:.16em;color:var(--navy-deep);background:var(--azure-pale);
  padding:3px 9px;border-radius:999px;margin-bottom:.5rem}
.dl h3{font-family:var(--font-ja-serif);font-size:1.08rem;font-weight:600;
  color:var(--ink);margin-bottom:.25rem}
.sec-navy .dl h3{color:#fff}
.dl p{font-size:.82rem;line-height:1.85;color:var(--muted)}
.sec-navy .dl p{color:rgba(255,255,255,.72)}
.dl-go{flex:none;font-family:var(--font-ja-sans);font-size:.86rem;font-weight:700;
  text-decoration:none;color:var(--azure);border:1px solid var(--azure);
  border-radius:999px;padding:.72em 1.5em;transition:background .2s ease,color .2s ease}
.dl-go:hover{background:var(--azure);color:#fff}
.sec-navy .dl-go{color:var(--azure-pale);border-color:var(--azure-pale)}
.sec-navy .dl-go:hover{background:var(--azure-pale);color:var(--navy-deep)}
@media print{.dl-go{display:none}}
/* ══ 配布資料ダウンロード（トップページと同じ形） ══ */
.sec-download{background:var(--paper);padding:3.5rem 1.5rem}
.dl-feature{max-width:var(--max-w);margin:0 auto;
  background:linear-gradient(140deg,#24446f 0%,var(--navy) 46%,var(--navy-deep) 100%);
  border:1px solid rgba(216,228,240,.10);border-radius:16px;padding:2.9rem 2.6rem;
  color:#fff;position:relative;overflow:hidden;
  box-shadow:0 24px 60px -24px rgba(20,29,53,.65)}
.dl-feature::before{content:"";position:absolute;inset:0;pointer-events:none;
  background:radial-gradient(58% 78% at 90% 4%,rgba(46,84,150,.55),transparent 62%),
             radial-gradient(46% 66% at 8% 106%,rgba(159,198,245,.18),transparent 58%)}
.dl-feature>*{position:relative}
.dl-badge{display:inline-block;font-family:var(--font-en);font-size:.7rem;
  letter-spacing:.14em;text-transform:uppercase;font-weight:700;
  background:var(--red);color:#fff;padding:.35rem .75rem;border-radius:100px}
.dl-title{font-family:var(--font-ja-serif);font-size:1.75rem;line-height:1.42;
  margin:1.05rem 0 .65rem;font-weight:600}
.dl-title span{color:var(--azure-pale)}
.dl-copy{font-size:.9rem;line-height:1.9;color:rgba(255,255,255,.82);
  max-width:560px;margin-bottom:1.85rem}
.dl-items{display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin-top:1.5rem}
.dl-item{background:rgba(255,255,255,.06);border:1px solid rgba(216,228,240,.16);
  border-radius:8px;padding:1.15rem 1.2rem;display:flex;flex-direction:column}
.dl-item h3{font-family:var(--font-ja-serif);font-size:1.02rem;color:#fff;
  margin-bottom:.35rem;font-weight:600}
.dl-item p{font-size:.8rem;color:rgba(255,255,255,.72);line-height:1.7;
  margin-bottom:1rem;flex-grow:1}
.dl-btn{display:inline-flex;align-items:center;justify-content:center;gap:.65rem;
  width:100%;background:var(--red);color:#fff;font-weight:700;font-size:.98rem;
  padding:.95rem 1.6rem;border-radius:8px;text-decoration:none;
  transition:transform .15s ease,background .2s ease;
  box-shadow:0 10px 24px -10px rgba(226,55,68,.7)}
.dl-btn:hover{background:var(--red-bright);transform:translateY(-2px)}
.dl-btn-meta{font-family:var(--font-en);font-weight:500;font-size:.75rem;opacity:.9}
@media (max-width:640px){
  .dl-feature{padding:2.1rem 1.5rem}
  .dl-title{font-size:1.4rem}
  .dl-btn{flex-wrap:wrap;row-gap:.3rem}
  .dl-items{grid-template-columns:1fr}
}
/* リード獲得ゲート */
.gate-overlay{position:fixed;inset:0;z-index:9990;display:none;
  align-items:center;justify-content:center;padding:1.5rem;
  background:rgba(20,29,53,.72)}
.gate-overlay.open{display:flex}
.gate-modal{position:relative;width:min(430px,100%);background:#fff;
  border-radius:16px;padding:2rem 1.9rem;box-shadow:0 30px 70px -20px rgba(20,29,53,.6)}
.gate-modal .gate-eyebrow{font-family:var(--font-en);font-size:.7rem;
  letter-spacing:.12em;text-transform:uppercase;color:var(--azure);font-weight:700}
.gate-modal h3{font-family:var(--font-ja-serif);font-size:1.32rem;color:var(--ink);
  margin:.5rem 0}
.gate-lead{font-size:.84rem;color:var(--muted);line-height:1.85;margin-bottom:1.3rem}
.gate-field{margin-bottom:.85rem}
.gate-field label{display:block;font-size:.76rem;font-weight:700;color:var(--navy);
  margin-bottom:.3rem}
.gate-field input{width:100%;padding:.7rem .85rem;border:1px solid var(--azure-pale);
  border-radius:8px;font-family:var(--font-ja-sans);font-size:.9rem;color:var(--ink)}
.gate-field input:focus{outline:none;border-color:var(--azure);
  box-shadow:0 0 0 3px rgba(46,84,150,.12)}
.gate-err{color:var(--red);font-size:.76rem;margin:.2rem 0;min-height:1em}
.gate-submit{width:100%;background:var(--red);color:#fff;border:none;border-radius:8px;
  padding:.9rem;font-family:var(--font-ja-sans);font-weight:700;font-size:.95rem;
  cursor:pointer}
.gate-submit:hover{background:var(--red-bright)}
.gate-submit:disabled{opacity:.6;cursor:default}
.gate-note{font-size:.72rem;color:var(--muted);margin-top:.9rem;line-height:1.65}
.gate-close{position:absolute;top:.7rem;right:1rem;background:none;border:none;
  font-size:1.5rem;color:var(--muted);cursor:pointer;line-height:1}
"""

# 表紙の奥に薄く敷く格子と星座。地の色そのものは apply_herofx が当てる
HERO_TEXTURE = """  <div class="texture" aria-hidden="true">
    <svg viewBox="0 0 1200 600" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg">
      <defs><pattern id="pgr" width="46" height="46" patternUnits="userSpaceOnUse"><path d="M46 0H0V46" fill="none" stroke="#fff" stroke-width="0.7"/></pattern></defs>
      <rect width="1200" height="600" fill="url(#pgr)"/>
      <circle cx="240" cy="180" r="4" fill="#fff"/><circle cx="560" cy="350" r="4" fill="#fff"/><circle cx="880" cy="210" r="4" fill="#fff"/><circle cx="1040" cy="430" r="4" fill="#fff"/>
      <path d="M240 180L560 350L880 210L1040 430" stroke="#fff" stroke-width="1" fill="none"/>
    </svg>
  </div>
"""


def dl(href, title, note, label='PDFをダウンロード', tag='FREE DOWNLOAD'):
    """配布物のダウンロード。書き込むワークシートのように、
    資料を見ながら手を動かすものを渡すときに置く。

    **リンク先は暗号の外に置かれる。** 資料そのものは鍵で守られるが、
    ここに置くPDFは公開URLで誰でも取れる。パスワードを刷り込んだ紙は置かない。
    """
    return ('<div class="dl">\n  <div class="dl-body">\n'
            '    <span class="dl-tag">%s</span>\n'
            '    <h3>%s</h3>\n    <p>%s</p>\n  </div>\n'
            '  <a class="dl-go" href="%s" download>%s</a>\n</div>\n'
            % (tag, esc(title), note, href, esc(label)))


def cards(items, raw_head=True):
    """items: [(見出し, 本文)]。見出しに <span class="mth"> を入れたいときが多いので、
    既定では見出しをエスケープしない。素の文字列を入れたいときは raw_head=False"""
    return '\n'.join(
        '      <div class="card"><span class="card-tag">%02d</span><h3>%s</h3><p>%s</p></div>'
        % (i + 1, h if raw_head else esc(h), p) for i, (h, p) in enumerate(items))


def take(text, name='小澤健祐（おざけん）'):
    """おざけんのワンポイント。

    **毎回このHTMLを手で書いていたので、事故が繰り返された。**
    body（カードの格子）に混ぜてしまい、1列ぶんの幅に潰れる。
    sec(..., after=take('…')) の形で、カードの外に置く。

    アイコンは実物の顔写真を使う。頭文字の丸だと、
    誰の一言なのかが投影中に伝わらない。
    """
    return ('    <div class="take">\n'
            '      <img class="take-avatar" src="../99_assets/ozaken-avatar.jpg" '
            'alt="%s" loading="lazy">\n'
            '      <div class="take-body">\n'
            '        <div class="take-label">Ozaken\'s One Point</div>\n'
            '        <div class="take-author">%s</div>\n'
            '        <p class="take-text">%s</p>\n'
            '      </div>\n    </div>\n' % (name, name, text))


def sec(tone, eyebrow, title, sub=None, lede=None, fig=None, body=None, cattr='',
        after=None):
    """tone: 'sec-light' か 'sec-navy'。fig は必ず1つ以上入れる。

    **after はカードの外に置く。** ここを用意していなかったので、
    「おざけんのワンポイント」や注記を body に混ぜてしまい、
    カードの格子の中に入って1列ぶんの幅に潰れていた（実際に出た）。
    """
    out = ['<section class="%s">' % tone, '  <div class="inner" data-reveal>',
           '    <span class="eyebrow">%s</span>' % eyebrow,
           '    <h2 class="sec-title">%s</h2>' % title]
    if sub:
        out.append('    <p class="sec-sub">%s</p>' % sub)
    if lede:
        out.append('    <p class="lede">%s</p>' % lede)
    if fig:
        out.append(fig)
    if body:
        out.append('    <div class="cards"%s>' % cattr)
        out.append(body)
        out.append('    </div>')
    if after:
        out.append(after)
    out += ['  </div>', '</section>', '']
    return '\n'.join(out)


BYLINE = ('<b>小澤健祐（おざけん）</b>'
          '<span>一般社団法人AICX協会 代表理事</span>')


def hero(eyebrow, title, copy, cat=None, meta=BYLINE):
    """資料の扉。**中央揃えではなく左揃え。**

    投影したときも、あとから読んだときも、視線は左上から始まる。
    中央に置くと、題・リード文・署名の行頭がそれぞれ違う位置に来るので、
    読み手は毎回その行の始まりを探すことになる。

      eyebrow  助走の小さなラベル。罫線が自動で付く
      title    <br> で2行に割る。<span class="hl"> で一部を淡い青＋下線に
      copy     リード文。3〜4行で収める
      cat      右上に置く区分（「AI Transformation ／ 解説」など）。省略可
      meta     著者と所属の行。既定でおざけんの署名が入る。None で消せる

    稼働の読み出しとスクロール誘導は apply_herofx が入れるので、ここでは書かない。
    """
    top = '  <span class="hero-cat">%s</span>\n' % esc(cat) if cat else ''
    mt = '    <p class="hero-meta">%s</p>\n' % meta if meta else ''
    return ('<section class="hero">\n%s%s  <div class="inner" data-reveal>\n'
            '    <span class="eyebrow">%s</span>\n'
            '    <h1 class="hero-title">%s</h1>\n'
            '    <p class="hero-copy">%s</p>\n%s  </div>\n</section>\n'
            % (HERO_TEXTURE, top, eyebrow, title, esc(copy), mt))


def close(title, copy):
    """締め。図版は置かない。事実の要約ではなく、1段上から言い直す"""
    return ('<section class="sec-navy">\n  <div class="inner" data-reveal>\n'
            '    <span class="eyebrow">Summary</span>\n'
            '    <h2 class="sec-title">%s</h2>\n'
            '    <p class="kicker">%s</p>\n  </div>\n</section>\n' % (title, copy))


def replace_figure(html, fig_no, new_html):
    """既存の図版を差し替える。fig_no は 'Fig.3' のような見出しの先頭。

    `<div class="figure">` から `</div>` までを正規表現で取ろうとすると、
    中の `<div class="figure-scroll">` を数え損ねて、
    **後ろにあるカードまで巻き込んで消す**。実際に2本の資料でカードが消えた。
    開きタグと閉じタグを数えて、対応する `</div>` を見つける。
    """
    import re
    m = re.search(r'<div class="figure">\s*<p class="fig-title">%s' % re.escape(fig_no), html)
    if not m:
        raise ValueError('%s が見つかりません' % fig_no)
    i = m.start()
    depth, j = 0, i
    for tag in re.finditer(r'<div\b|</div>', html[i:]):
        depth += 1 if tag.group(0).startswith('<div') else -1
        if depth == 0:
            j = i + tag.end()
            break
    else:
        raise ValueError('%s の閉じタグが見つかりません' % fig_no)
    return html[:i] + new_html + html[j:]


# ── 配布資料のダウンロード（トップページと同じ形） ────────────
#
# **登壇のあと、参加者にページごと共有する資料に置く。**
# 会場では投影するだけだが、あとから開いた人には「持ち帰れるもの」が要る。
# トップページに置いてある配布物を、同じ見た目・同じリード獲得ゲートのまま、
# 資料の末尾に出す。
#
# **CSSは本文ではなく EXTRA_CSS（head）に置く。**
# 資料はパスワードのあと document.write で書き戻されるので、
# スタイルは head にまとまっているほうが、読み込みの順番が素直になる。
#
# なお、ネットワークの無いところで手元のファイルを開くと、head の Webフォントの
# 読み込みが終わらず、本文の <script> の手前でページが止まって見える。
# 資料が途中で切れて見えても、たいていはこれ。公開先では起きない。
#
# 締め（close）の**あと**に置く。本文の明暗の並びには入らない
# （build_page.check は hero / sec-light / sec-navy しか数えない）ので、
# 節を足すときのような数合わせは要らない。

DL_ITEMS = [
    ('AIエージェント実装の5レベル 完全版',
     '「使うAI」から「任せるAI」へ。実装の成熟度を5段階で整理した、決定版スライド。',
     '01_concept/five-levels-of-delegation.pdf', 'PDF · 約3.5MB'),
    ('業務変革大全',
     'AXは「プロセス」を動かす。効率化・再構築・代替の3フェーズ、'
     '業務分解の5つの道具、そして組み直すまでの実務手順。',
     '04_practice/business-transformation-guide.pdf', 'PDF · 16:9 14ページ'),
    ('AI推進 51施策マスター',
     '経営戦略から事業化まで、社内会議でそのまま使える打ち手を9カテゴリ×51施策で一覧化。',
     '05_drive/ai-51-measures.pdf', 'PDF · A4 1枚'),
    ('AIエージェント人材基準 v0.5',
     'AICX協会が策定した、AIエージェント時代に求められる人材の定義・スキル基準。'
     '組織の人材設計の土台に。',
     '99_assets/aicx-agent-talent-standard-v0.5.pdf', 'PDF · 26ページ'),
    ('人事白書 2026',
     'AIエージェント時代の「人事白書」。「管理」から「価値創造」へ。'
     'AIと共に進化する組織と人事の未来図をまとめた公式白書。',
     '99_assets/aicx-whitepaper-2026.pdf', 'PDF · 47ページ'),
]

# リード獲得の送り先。トップページと同じ窓口に集める
DL_ENDPOINT = ('https://script.google.com/macros/s/'
               'AKfycbwvf6VRQsjfiXulHOPAQ_Uren7ewTS3LTp9sp7XMf3H4yDsMhQIO1f41NPs1FfaTz1P/exec')


GATE_HTML = """
<div class="gate-overlay" id="leadGate" aria-hidden="true">
  <div class="gate-modal" role="dialog" aria-modal="true" aria-labelledby="gateTitle">
    <button class="gate-close" id="gateClose" type="button" aria-label="閉じる">&#215;</button>
    <span class="gate-eyebrow">Download</span>
    <h3 id="gateTitle">資料をご覧いただくには</h3>
    <p class="gate-lead">かんたんなご登録で、資料をダウンロード・閲覧いただけます。
      いただいた情報は、講演・顧問のご案内や資料のお届けに利用させていただく場合があります。</p>
    <form id="gateForm" novalidate>
      <div class="gate-field"><label for="gName">お名前</label>
        <input id="gName" name="name" type="text" autocomplete="name" required></div>
      <div class="gate-field"><label for="gCompany">会社名・所属</label>
        <input id="gCompany" name="company" type="text" autocomplete="organization" required></div>
      <div class="gate-field"><label for="gEmail">メールアドレス</label>
        <input id="gEmail" name="email" type="email" autocomplete="email" required></div>
      <div class="gate-err" id="gateErr" aria-live="polite"></div>
      <button class="gate-submit" type="submit" id="gateSubmit">送信して資料を見る &#8594;</button>
      <p class="gate-note">送信をもってAICX協会からの資料・イベント案内の受け取りに
        同意いただいたものとします。配信はいつでも停止できます。</p>
    </form>
  </div>
</div>
"""

GATE_JS = """
<script>
/* 配布資料のリード獲得ゲート。トップページと同じ窓口・同じ鍵なので、
   トップで登録済みの人には、ここでは出ない */
(function(){
  var ENDPOINT = "%s";
  var KEY = "ozaken_lead_unlocked";
  var gate = document.getElementById('leadGate');
  if (!gate) return;
  var form = document.getElementById('gateForm');
  var errEl = document.getElementById('gateErr');
  var submitBtn = document.getElementById('gateSubmit');
  var pending = null;

  function unlocked(){ try { return localStorage.getItem(KEY) === "1"; } catch(e){ return false; } }
  function openGate(){ gate.classList.add('open'); gate.setAttribute('aria-hidden','false');
    setTimeout(function(){ document.getElementById('gName').focus(); }, 50); }
  function closeGate(){ gate.classList.remove('open'); gate.setAttribute('aria-hidden','true');
    pending = null; }
  function proceed(a){
    if (!a) return;
    var t = document.createElement('a'); t.href = a.getAttribute('href');
    t.setAttribute('download',''); document.body.appendChild(t); t.click(); t.remove();
  }

  document.querySelectorAll('a[data-gate]').forEach(function(a){
    a.addEventListener('click', function(ev){
      if (!ENDPOINT || unlocked()) return;
      ev.preventDefault(); pending = a; errEl.textContent = ''; openGate();
    });
  });

  document.getElementById('gateClose').addEventListener('click', closeGate);
  gate.addEventListener('click', function(e){ if (e.target === gate) closeGate(); });
  document.addEventListener('keydown', function(e){
    if (e.key === 'Escape' && gate.classList.contains('open')) closeGate(); });

  form.addEventListener('submit', function(ev){
    ev.preventDefault();
    var name = document.getElementById('gName').value.trim();
    var company = document.getElementById('gCompany').value.trim();
    var email = document.getElementById('gEmail').value.trim();
    if (!name || !company || !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) {
      errEl.textContent = 'お名前・会社名・正しいメールアドレスをご入力ください。'; return;
    }
    submitBtn.disabled = true; submitBtn.textContent = '送信中…';
    var asset = pending ? (pending.getAttribute('href') || '') : '';
    fetch(ENDPOINT, { method:'POST', mode:'no-cors',
        headers:{ 'Content-Type':'text/plain;charset=utf-8' },
        body: JSON.stringify({ name:name, company:company, email:email,
                               asset:asset, ua:navigator.userAgent }) })
      .catch(function(){})
      .finally(function(){
        try { localStorage.setItem(KEY, "1");
          localStorage.setItem("ozaken_lead_info",
            JSON.stringify({name:name, company:company, email:email})); } catch(e){}
        submitBtn.disabled = false; submitBtn.textContent = '送信して資料を見る →';
        var a = pending; closeGate(); proceed(a);
      });
  });
})();
</script>
"""


def download(items=None, depth=1,
             title='実務でそのまま使える資料を、<br>'
                   '<span>無料でプレゼントしています。</span>',
             copy='本日の内容の予習・復習、社内での共有、研修の教材として、'
                  'どうぞご自由にお使いください。'):
    """配布資料のダウンロード。**締め（close）のあとに置く。**

    depth はこの資料の階層の深さ。09_role/foo.html なら 1、
    ルート直下なら 0。PDFは暗号の外に置いてあるので、ここで '../' を足す。
    """
    up = '../' * depth
    cells = []
    for h, note, href, meta in (items or DL_ITEMS):
        cells.append(
            '        <div class="dl-item">\n'
            '          <h3>%s</h3>\n          <p>%s</p>\n'
            '          <a class="dl-btn" href="%s%s" download data-gate>'
            '<span>&#11015;</span> ダウンロード '
            '<span class="dl-btn-meta">%s</span></a>\n'
            '        </div>' % (esc(h), esc(note), up, href, esc(meta)))
    return ('\n<section class="sec-download">\n  <div class="inner" data-reveal>\n'
              '    <div class="dl-feature">\n'
              '      <span class="dl-badge">無料配布資料 / Download</span>\n'
              '      <h2 class="dl-title">%s</h2>\n'
              '      <p class="dl-copy">%s</p>\n'
              '      <div class="dl-items">\n%s\n      </div>\n'
              '    </div>\n  </div>\n</section>\n' % (title, copy, '\n'.join(cells))
            + GATE_HTML + (GATE_JS % DL_ENDPOINT))
