#!/usr/bin/env python3
"""ワークシートPDFの、共通の見た目。

A4縦・印刷して手で書く紙のための組み。
career-worksheet.py で作ったものを、2本目（ai-lead-worksheet.py）が出たときに
こちらへ寄せた。**片方だけ直して、並べたときに別物に見えるのを避けるため。**

紙ごとに違う部品（30日の日程・依頼文の欄など）は、各生成元の側に置く。
ここに置くのは、2枚以上の紙で使うものだけ。
"""

CSS = """
@font-face{font-family:'ZK';src:url('ZenKakuGothicNew-Medium.ttf')format('truetype');font-weight:500}
@font-face{font-family:'ZK';src:url('ZenKakuGothicNew-Bold.ttf')format('truetype');font-weight:700}
@font-face{font-family:'SM';src:url('ShipporiMinchoB1-Bold.ttf')format('truetype');font-weight:600}
@font-face{font-family:'HG';src:url('HankenGrotesk.ttf')format('truetype')}
:root{--ink:#1a1a2e;--navy:#1f3864;--navy-deep:#141d35;--azure:#2e5496;
  --azure-pale:#d8e4f0;--paper:#f8f7f4;--red:#e23744;--muted:#6b7a99}
*{box-sizing:border-box;margin:0;padding:0}
@page{size:A4;margin:0}
body{font-family:'ZK',sans-serif;color:var(--ink);-webkit-print-color-adjust:exact;print-color-adjust:exact}
.page{width:210mm;height:297mm;padding:16mm 15mm 13mm;page-break-after:always;
  position:relative;background:#fff;display:flex;flex-direction:column}
.page:last-child{page-break-after:auto}
.tag{display:inline-block;font-family:'HG';font-size:7.5pt;font-weight:700;letter-spacing:.16em;
  color:var(--navy-deep);background:var(--azure-pale);padding:3px 9px;border-radius:99px}
h1{font-family:'SM';font-weight:600;font-size:21pt;line-height:1.45;margin:6mm 0 3mm}
h2{font-family:'SM';font-weight:600;font-size:15pt;line-height:1.5;margin:4mm 0 1.5mm}
.sub{font-size:9pt;line-height:1.75;color:var(--muted);margin-bottom:5mm}
.rule{height:2px;background:linear-gradient(90deg,var(--azure),var(--azure-pale) 60%,transparent);margin:3mm 0 5mm}
.note{font-size:8pt;line-height:1.7;color:var(--muted)}
.foot{margin-top:auto;padding-top:4mm;border-top:1px solid var(--azure-pale);
  display:flex;justify-content:space-between;font-family:'HG';font-size:7.5pt;
  letter-spacing:.1em;color:var(--muted)}
/* 表紙 */
.cover{background:linear-gradient(168deg,#1f3864 0%,#182a52 46%,#141d35 100%);color:#fff}
.cover h1{font-size:26pt;margin-top:8mm}
.cover .sub{color:rgba(216,228,240,.78);font-size:10pt}
.cover .rule{background:linear-gradient(90deg,var(--red),rgba(226,55,68,0))}
.cover .foot{border-top-color:rgba(216,228,240,.28);color:rgba(216,228,240,.6)}
.howto{margin-top:6mm}
.howto li{list-style:none;display:flex;gap:4mm;padding:3.5mm 0;
  border-top:1px solid rgba(216,228,240,.22);font-size:9.5pt;line-height:1.8}
.howto b{font-family:'HG';font-size:9pt;color:var(--azure-pale);flex:none;width:8mm}
.howto span{color:rgba(255,255,255,.92)}
.promise{margin-top:5mm;padding:5mm;border-radius:4mm;
  background:rgba(255,255,255,.07);border:1px solid rgba(216,228,240,.26)}
.promise p{font-size:9pt;line-height:1.85;color:rgba(216,228,240,.92)}
.promise b{color:#fff}
.promise .url{font-family:'HG';font-size:9.5pt;font-weight:700;letter-spacing:.02em;
  color:#fff;margin-top:4mm;word-break:break-all}
.promise .pw{font-family:'HG';font-size:8pt;font-weight:700;letter-spacing:.14em;
  color:rgba(216,228,240,.7);margin-top:1.5mm}
.promise .pw b{font-size:12pt;letter-spacing:.06em;color:#fff}
/* 記入欄 */
.quad{display:grid;grid-template-columns:1fr 1fr;gap:3mm;margin-top:2mm}
.cell{border:1.2px solid var(--azure-pale);border-radius:3mm;padding:4mm;min-height:66mm}
.cell.hi{border-color:var(--azure);background:rgba(46,84,150,.045)}
.cell h3{font-family:'SM';font-size:11pt;font-weight:600;margin-bottom:1mm}
.cell .k{font-family:'HG';font-size:7pt;font-weight:700;letter-spacing:.14em;color:var(--azure)}
.cell p{font-size:7.5pt;line-height:1.65;color:var(--muted);margin-bottom:3mm}
.axis{display:flex;justify-content:space-between;font-family:'HG';font-size:7.5pt;
  font-weight:700;letter-spacing:.1em;color:var(--muted);margin:1mm 0}
.ylab{font-family:'HG';font-size:7.5pt;font-weight:700;letter-spacing:.1em;color:var(--muted)}
.line{border-bottom:1px dotted rgba(46,84,150,.45);height:7mm}
.rows{width:100%;border-collapse:collapse;margin-top:1mm}
.rows th{font-family:'HG';font-size:7.5pt;font-weight:700;letter-spacing:.12em;
  text-align:left;color:#fff;background:var(--navy);padding:2.5mm 3mm}
.rows td{border:1px solid var(--azure-pale);padding:2.6mm 3mm;vertical-align:top}
.rows td.q{width:42mm;background:rgba(46,84,150,.04)}
.rows td.q b{font-size:9.5pt;display:block;margin-bottom:1mm}
.rows td.q span{font-size:7.5pt;line-height:1.6;color:var(--muted)}
/* 記入例は、書く欄の隣に置いて、書いている間ずっと見えるようにする */
.rows td.e{width:52mm;background:rgba(46,84,150,.02);font-size:7.5pt;
  line-height:1.65;color:var(--muted)}
.rows td.a{height:19mm}
.plan{width:100%;border-collapse:collapse;margin-top:2mm}
.plan th{font-family:'HG';font-size:7.5pt;font-weight:700;letter-spacing:.12em;
  color:#fff;background:var(--navy);padding:2.5mm;text-align:center}
.plan th:first-child{text-align:left;width:44mm}
.plan td{border:1px solid var(--azure-pale);padding:2.4mm 3mm;height:12mm;vertical-align:top}
.plan td.n{background:rgba(46,84,150,.04);font-size:9pt;font-weight:700;vertical-align:middle}
.plan td.n span{display:block;font-weight:500;font-size:7.5pt;line-height:1.6;
  color:var(--muted);margin-top:1mm}
.checks{margin-top:2mm}
.checks li{list-style:none;display:flex;gap:3mm;align-items:flex-start;
  padding:2.3mm 0;border-bottom:1px solid rgba(46,84,150,.14);font-size:9pt;line-height:1.7}
.checks i{flex:none;width:4.5mm;height:4.5mm;border:1.4px solid var(--azure);
  border-radius:1mm;margin-top:1mm}
.checks em{font-style:normal;color:var(--muted);font-size:7.5pt;display:block;line-height:1.6}
/* 30日の日程（ワーク4）。日付と成果物を、行ごとに書き込ませる */
.pick{border:1.2px solid var(--azure);border-radius:3mm;padding:4mm 5mm;margin-top:1mm;
  background:rgba(46,84,150,.045)}
.pick .k{font-family:'HG';font-size:7pt;font-weight:700;letter-spacing:.14em;color:var(--azure)}
.pick .big{display:flex;align-items:flex-end;gap:3mm;margin-top:2mm}
.pick .big span{font-size:8.5pt;color:var(--muted);flex:none;padding-bottom:1mm}
.pick .big .line{flex:1;height:8mm;border-bottom:1.2px solid rgba(46,84,150,.5)}
.pick ul{display:flex;gap:5mm;margin-top:3mm}
.pick li{list-style:none;display:flex;gap:2mm;align-items:center;font-size:8pt;color:var(--muted)}
.pick i{flex:none;width:3.6mm;height:3.6mm;border:1.3px solid var(--azure);border-radius:.8mm}
.days{width:100%;border-collapse:collapse;margin-top:4mm}
.days th{font-family:'HG';font-size:7.5pt;font-weight:700;letter-spacing:.12em;
  text-align:left;color:#fff;background:var(--navy);padding:2.4mm 3mm}
.days td{border:1px solid var(--azure-pale);padding:2.4mm 3mm;vertical-align:middle;height:14.5mm}
.days td.d{width:20mm;background:rgba(46,84,150,.04);font-family:'HG';font-size:8.5pt;
  font-weight:700;text-align:center}
.days td.w{width:62mm;font-size:8.5pt;line-height:1.6}
.days td.w em{font-style:normal;display:block;font-size:7pt;color:var(--muted);margin-top:.6mm}
.days td.dt{width:24mm}
.days td.done{width:14mm;text-align:center}
.days td.done i{display:inline-block;width:4.2mm;height:4.2mm;
  border:1.3px solid var(--azure);border-radius:1mm}
/* 依頼文の記入欄（ワーク5） */
/* ①〜④の4点セットは2×2に組む。縦一列に6つ並べるとA4に収まらないうえ、
   4点セットと、その外側の⑤⑥という構造も見えなくなる */
.slots{display:grid;grid-template-columns:1fr 1fr;gap:2.5mm;margin-top:1mm}
.slots .slot{margin-bottom:0}
.slots2{margin-top:2.5mm}
.slot{border:1px solid var(--azure-pale);border-radius:2.5mm;padding:2.4mm 4mm;margin-bottom:2mm}
.slot.hi{border-color:var(--azure);background:rgba(46,84,150,.04)}
.slot h3{font-family:'SM';font-size:10pt;font-weight:600}
.slot p{font-size:7.5pt;line-height:1.6;color:var(--muted);margin:.5mm 0 1.6mm}
.slot .line{border-bottom:1px dotted rgba(46,84,150,.45);height:6mm}
/* 記入例。**書き込む線の上には置かない。** 手で書く場所と重なると、両方読めなくなる。
   薄い青の帯として、書きはじめる直前に置く */
.ex{border-left:2px solid rgba(46,84,150,.55);background:rgba(46,84,150,.05);
  padding:1.6mm 3mm;margin:0 0 2mm;border-radius:0 1.5mm 1.5mm 0}
.ex b{font-family:'HG';font-size:6.5pt;font-weight:700;letter-spacing:.14em;
  color:var(--azure);display:block;margin-bottom:.8mm}
.ex span{display:block;font-size:7.5pt;line-height:1.65;color:var(--muted)}
.ex span+span{margin-top:1mm}
.ex i{font-style:normal;font-weight:700;color:var(--azure)}
.ex .ng{color:rgba(226,55,68,.75)}
.ex .ng i{color:var(--red)}
/* 記入例の人物。表紙で一度だけ名乗らせる */
.who{margin-top:5mm;padding:4mm 5mm;border-radius:3mm;
  background:rgba(255,255,255,.05);border:1px solid rgba(216,228,240,.2)}
.who>b{font-family:'HG';font-size:7pt;font-weight:700;letter-spacing:.14em;
  color:var(--azure-pale);display:block;margin-bottom:1.5mm}
.who p{font-size:8.5pt;line-height:1.8;color:rgba(216,228,240,.85)}
.who p b{color:#fff}          /* 本文中の強調は行の中に置く。ラベルと同じ見た目にしない */
"""
