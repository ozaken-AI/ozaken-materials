# 資料整理済みフォルダ

「資料」フォルダの中身をテーマ別に整理したものです。GitHubリポジトリ `ozaken-materials` としてアップロードする想定の構成です。

## フォルダ構成

- `01_AIエージェント_5段階レベル/` — AIエージェント実装の5レベルに関する記事・資料（Copilot/Gemini比較、PDF資料など）
- `02_AIエージェント_資格制度/` — AIエージェント・ストラテジスト等、資格制度関連
- `03_AIエージェント_予算/` — AIエージェント導入の予算・コストに関する記事
- `04_AIエージェント_キャリア/` — AIエージェント時代のキャリアに関する記事（HTML/PDF）
- `05_AI活用施策まとめ/` — AI活用施策50/51選などのまとめ記事
- `06_AX解説/` — AXとは何か、を解説するPDF資料
- `07_業界動向_解説記事/` — ChatGPT Work、Google I/O、OpenAI FDE、Human-in/on-the-loop、パーパス論、AI音声、モデル使い分けなど業界動向・解説記事
- `08_Cowork関連/` — Cowork解説資料
- `09_Mythos/` — Mythosプロジェクト関連資料
- `10_人事_法務/` — 人事関連資料、個人情報保護法解説
- `11_登壇資料_スライド/` — 登壇用スライド（pptx）
- `12_画像素材/` — 画像素材
- `13_その他/` — 分類外の資料

## GitHubへのアップロード手順（ご自身のPCで実行）

```bash
cd ~/Documents/資料_整理済み
git init
git add .
git commit -m "資料を整理してアップロード"
gh repo create ozaken-materials --public --source=. --remote=origin
git push -u origin main
```

`gh` コマンドが未インストールの場合は `brew install gh` の後 `gh auth login` でログインしてから上記を実行してください。
