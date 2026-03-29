---
marp: true
theme: default
paginate: true
header: "GitHub Copilotで既存リポジトリを改善する"
footer: "© 2026"
style: |
  section {
    font-family: 'Hiragino Sans', 'Noto Sans JP', sans-serif;
  }
  h1 {
    color: #1a73e8;
  }
  h2 {
    color: #333;
  }
  code {
    background: #f0f0f0;
    padding: 2px 6px;
    border-radius: 3px;
  }
  table {
    font-size: 0.8em;
  }
---

# GitHub Copilotで<br>既存リポジトリを段階的に改善する

**テスト・リンター・CI/CDをCopilotで導入する実践手順**

---

## 既存コードは4ステップで安全に改善できる

1. テストの導入 — 既存コードを変えずに品質を担保
2. リンターの導入 — コードスタイルの自動統一
3. CI/CDの構築 — 変更の検証を自動化
4. Copilot指示書の作成 — AIにプロジェクト文脈を共有

---

## テストもリンターもないコードは変更が怖い

```python
# app.py - FlaskベースのタスクAPI
from flask import Flask, request, jsonify
import sqlite3
import os   # ← 未使用のimport

@app.route('/tasks', methods=['GET'])
def get_tasks():
    conn = sqlite3.connect('tasks.db')  # テストなし、CIなし
```

テストなし / リンターなし / CI/CDなし → **変更するたびに不安が生まれる**

---

## Step 1：既存コードを変えずにテストだけ追加する

Copilotにテスト生成を依頼し、3ファイルを追加：

- `conftest.py` — 一時DB生成のフィクスチャ
- `test_api.py` — 各エンドポイントの結合テスト（18件）
- `test_scenarios.py` — 複数操作の連結テスト（4件）

既存コード（`app.py`）は **一切変更しない** のがポイント

---

## 22テストが全てパス — 既存コード変更なし

```
test_api.py::test_タスクを正常に作成         PASSED
test_api.py::test_タスクを正常に削除         PASSED
test_api.py::test_タスクを検索              PASSED
test_scenarios.py::test_作成_更新_完了_削除フロー PASSED
======================== 22 passed in 0.21s ====
```

既存コードの変更なしにテストカバレッジを確保できた

---

## Step 2：Copilotがruff設定を生成し、コードを自動修正

```toml
[tool.ruff]
target-version = "py310"
line-length = 100

[tool.ruff.lint]
select = ["E", "F", "W", "I", "N", "UP", "B", "SIM"]

[tool.ruff.lint.per-file-ignores]
"tests/**" = ["N802"]  # 日本語テスト名を許可
```

未使用import削除 / importソート / フォーマット統一を自動で検出・修正

---

## Step 3：Copilotが最適なCI/CDワークフローを提案

```yaml
# .github/workflows/ci.yml
name: CI
on:
  push:
    branches: [main, "step/**"]
jobs:
  lint:     # ruff check + format check
  test:     # pytest（lintパス後に実行）
```

`setup-uv` + `uv sync --frozen` で再現可能な環境を自動構築

---

## Step 4：指示書でCopilotにプロジェクト文脈を共有する

```markdown
# Copilot Instructions
## プロジェクト概要
FlaskベースのタスクAPIです。
## コーディング規約
- ruffの設定に従うこと
- テスト関数名は日本語で記述してよい
## 開発時の注意事項
- エンドポイント追加時はtest_api.pyにテスト追加
- コミット前にruff check .を実行
```

Copilotがプロジェクト固有のルールを理解し、的確なコードを生成できるようになる

---

## 4ステップで品質基盤が整った

| 項目 | Before | After |
|:-----|:-------|:------|
| テスト | なし | 22テスト（結合＋連結） |
| リンター | なし | ruff（lint + format） |
| CI/CD | なし | GitHub Actions |
| Copilot指示書 | なし | copilot-instructions.md |
| 品質管理 | 手動 | 自動化 |

---

## Copilot活用の3原則

**既存コードを壊さない**
テスト追加時に既存コードは一切変更しなかった

**段階的に改善する**
テスト → リンター → CI/CD → 指示書の順で一歩ずつ導入

**指示書でCopilotにプロジェクト文脈を共有する**
`copilot-instructions.md` がCopilotの生成精度を上げる

---

## Copilotは「コードを書く」だけでなく「コードベースを良くする」ツール

- **テスト生成** — 既存APIの仕様を読み取り、包括的テストを自動生成
- **リンター導入** — 設定生成から自動修正まで一貫対応
- **CI/CD構築** — プロジェクトに最適なワークフローを提案
- **指示書作成** — Copilot自身への指示を自分で作れる

---

## 各ステップをブランチで分け、差分を可視化する

```
main
 └─ step/1-api          素のFlask API
  └─ step/2-tests       テスト追加
   └─ step/3-linter     リンター導入
    └─ step/4-cicd      CI/CD追加
     └─ step/5-copilot  指示書追加
      └─ step/6-slides  発表資料
       └─ step/7-pr     PRテンプレート
        └─ step/8-protection  ブランチ保護
         └─ step/9-security   サプライチェーン対策
          └─ step/10-contract 契約プログラミング
           └─ step/11-container コンテナ基盤
```

ブランチの差分を見れば「何が追加されたか」が一目瞭然

---

## CopilotはPR文も自動生成できる

1. PRテンプレートと指示書を用意しておく
2. 開発完了後にCopilotへ一言依頼する

> 「このブランチの変更内容を元に、PRテンプレートに沿ったPR文を作成して」

Copilotが差分を読み取り、概要・変更内容・テスト項目を自動で埋める

---

## ブランチ保護もコードで管理すれば変更履歴が残る

1. `branch-protection.json` に保護ルールをJSONで定義
2. mainマージ時にGitHub Actionsが自動適用
3. ルール変更はJSON編集 → PR → マージだけ

PRレビュー必須 / ステータスチェック必須 / Force Push禁止 / 管理者にも適用

---

## 契約プログラミングで関数の仕様を明示しAI精度を上げる

```python
@contract(
    pre(lambda task: task is not None),
    post(lambda result: "id" in result),
    pure(),
)
def task_to_dict(task):
    return {"id": task["id"], "title": task["title"], ...}
```

- `pre()` / `post()` / `pure()` で関数の意図をコードで宣言
- Copilotが仕様を正確に理解し、生成コードの品質が向上

---

## サプライチェーン攻撃を3層で防ぐ

**GitHub Actions SHA pinning** — ActionをコミットSHAで固定
```yaml
- uses: actions/checkout@34e1148...  # v4
```

**uv exclude-newer** — 公開3日未満のパッケージを除外

**Dependabot + cooldown** — 依存更新自動化 + 3日の検疫期間

---

## AIエージェントはセキュアなサンドボックスで動かす

```yaml
# compose.yaml
services:
  sandbox:
    read_only: true       # root FSは読み取り専用
    network_mode: none    # オフライン既定
    cap_drop: [ALL]       # 全権限をdrop
```

- オフライン既定 → 依存取得時のみ `--online` で明示許可
- 書き込みは `/workspace` と `.sandbox/home` のみ
- 監査ログをhost側に記録

---

# ご清聴ありがとうございました

リポジトリをクローンして各ブランチの差分を確認してみてください

**質問はありますか？**
