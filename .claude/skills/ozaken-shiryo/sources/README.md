# 資料の生成元

公開されている資料の本文フラグメントを組み立てるスクリプト。
**資料を直すときは、公開済みのHTMLではなく、ここを直して作り直す。**

```bash
cd .claude/skills/ozaken-shiryo/sources
python3 gen_xxx.py                       # /tmp/body_xxx.html を書き出す
cd ../scripts
OZAKEN_PW=マスター python3 publish.py \
    /tmp/body_xxx.html 01_concept/xxx.html --update
```

`--update` は鍵を作り直さないので、配布済みのパスワードはそのまま使える。

## どの生成元が、どの資料を組むか

題（`<!--META title=...-->`）から突き合わせたもの。
空欄は、複数の資料をまとめて組む生成元か、題を変えたあとのもの。

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
- `gen_msa.py` … Training/msa-life-training.html
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
- `gen_use_to_delegate.py` … 01_concept/use-to-delegate.html
- `gen_walls.py` … 05_drive/five-walls.html
- `gen_webtan2026.py` … 03_tools/ai-trend-and-tools-2026.html
- `gen_wf.py` … 04_practice/build-a-workflow.html
