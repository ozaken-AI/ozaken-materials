# 資料の生成元

資料の本文・図・専用デザインを組み立てる生成元です。
**資料を直すときは、暗号化HTMLの暗号文ではなく、生成元を直して作り直します。**
全体の作成・改訂・公開手順は [運用手順](../../../../docs/operations.md)、最新の本人指定は [講演・印刷のデザイン規約](../../../../docs/lecture-design.md) を参照してください。

## 現在使う生成入口

| 対象 | 生成入口 | 役割 |
|---|---|---|
| `template.html` | `build_template_gallery.py` | `gen_template.py` の見本データを読み、`template_gallery/lecture.py` で全34図・33本文パーツを常時表示 |
| `01_concept/use-to-delegate.html` | `delegation_pilot/build.py` | `gen_use_to_delegate.py` を参照し、講演用の構成・背景・印刷を適用 |
| その他の資料 | 対応する `gen_*.py` と `../scripts/publish.py` | 本文フラグメントの組版・検査・暗号化 |

両方の現行ビルダーは `lecture_effects.css` を埋め込みます。背景や列ホバーを変えたら、依頼された対象を再生成してください。便覧だけの修正で他の資料まで一括更新しません。

このディレクトリから実行する例：

```sh
python3 build_template_gallery.py --preview /absolute/private-preview/template.html
python3 build_template_gallery.py --preview /absolute/private-preview/template.html --publish
python3 delegation_pilot/build.py \
  --output /absolute/private-preview/01_concept/use-to-delegate.html --update
```

`--publish` / `--update` は既存鍵を保持してローカルの暗号化HTMLを書き戻します。本番へのpushは行いません。マスターは非表示入力で受け取り、ソースやREADMEには記録しません。

## 新しい資料を作る場合

`gen_template.py` は骨格・図の呼び出し・見本データの参考に使います。複製したら題・節・出力先を変更します。ただし、旧来の開閉・切り替え・段階表示まで流用しません。講演用の常時表示と背景・印刷は `template_gallery/lecture.py` と `delegation_pilot/` を参考に、専用ビルダーから再現できるように組み込みます。

汎用資料の更新は対応する生成元から本文フラグメントを作り、`publish.py --update` を通します。既存QR・関連リンク・独自の追加要素が保持されるか確認してください。詳しいコマンドと鍵の安全な渡し方は [運用手順](../../../../docs/operations.md#既存資料を直す) にあります。

## どの生成元が、どの資料を組むか

題（`<!--META title=...-->`）から突き合わせたもの。
空欄は、複数の資料をまとめて組む生成元か、題を変えたあとのもの。

- `build_template_gallery.py` ＋ `template_gallery/lecture.py` … template.html（現在の便覧）
- `gen_template.py` … 便覧の見本データ、作図関数・旧フラグメントの参考
- `gen_ai_drive.py` … 05_drive/ai-drive-handbook.html
- `gen_ai_lead.py` … （要確認）
- `gen_bizmodel.py` … 01_concept/business-model-shift.html
- `gen_bot.py` … 04_practice/build-a-bot.html
- `gen_bpt.py` … （要確認）
- `gen_budget.py` … 05_drive/ai-budget.html
- `gen_career_omote.py` … 06_people/career-in-agent-era.html
- `gen_china.py` … 02_models/china-ai-models.html
- `gen_coe.py` … 05_drive/ai-coe.html
- `gen_cxex.py` … 01_concept/cx-ex-hub.html
- `gen_data.py` … 01_concept/data-for-ai.html
- `gen_jinji.py` … 06_people/jinji-gyomu.html、06_people/jinji-seido.html
- `gen_kanadevia.py` … 09_role/kanadevia-ict.html
- `gen_keiei.py` … 05_drive/keiei-data-kiban.html
- `gen_meti_wg5.py` … 06_people/meti-ax-skill-wg5.html
- `gen_hatten.py` … 05_drive/growth-phase.html（発展フェーズ12施策）
- `gen_mcp_rag.py` … 02_models/mcp-and-rag.html
- `gen_msa.py` … Training/msa-life-training.html
- `gen_policy_japan.py` … 10_policy/japan-ai-strategy.html
- `gen_policy_usa.py` … 10_policy/usa-ai-strategy.html
- `gen_policy_china.py` … 10_policy/china-ai-strategy.html
- `gen_policy_eu.py` … 10_policy/eu-ai-strategy.html
- `gen_policy_compare.py` … 10_policy/ai-policy-compare.html
- `gen_stats_2026.py` … 11_stats/ai-stats-2026.html
- `gen_rag_ft.py` … 02_models/rag-finetuning.html
- `gen_role_docs.py` … （要確認）
- `gen_role_docs2.py` … （要確認）
- `gen_role_docs3.py` … （要確認）
- `gen_roles.py` … 06_people/roles-in-agent-era.html
- `gen_s1.py` … AX_Table/s1-nanimo-kawaranai.html
- `gen_s2.py` … AX_Table/s2-roadmap.html
- `gen_s3.py` … AX_Table/s3-poc.html
- `gen_s5.py` … AX_Table/s5-data-kiban.html
- `gen_s6.py` … AX_Table/s6-soshiki-saisekkei.html
- `gen_s8.py` … AX_Table/s8-copilot.html
- `gen_seci.py` … 01_concept/ai-seci.html
- `gen_skill.py` … 01_concept/agent-skills.html
- `gen_suishin.py` … 05_drive/drive-phase.html
- `gen_trend.py` … 02_models/three-axes.html
- `gen_udemy_career.py` … Udemy/career-strategy.html
- `gen_udemy_v2.py` … Udemy/career-strategy.html
- `delegation_pilot/build.py` … 01_concept/use-to-delegate.html（現在の講演版）
- `gen_use_to_delegate.py` … 上記ビルダーが参照する内容の生成元
- `gen_walls.py` … 05_drive/five-walls.html
- `gen_webtan2026.py` … 03_tools/ai-trend-and-tools-2026.html
- `gen_wf.py` … 04_practice/build-a-workflow.html
