---
marp: true
theme: default
paginate: true
header: "GitHub Copilotを使った既存リポジトリへの有効活用方法"
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

# GitHub Copilotを使った<br>既存リポジトリへの有効活用方法

**〜レガシーコードを段階的に改善する実践アプローチ〜**

---

## 本セミナーの流れ

| # | 内容 | ゴール |
|:--|:-----|:-------|
| 0 | プロンプトの書き方 | ワンショット・Fewショットの違いを理解する |
| 1 | テストの導入 | 既存コードを変えずにテストを追加できる |
| 2 | リンターの導入 | 決定論的ツールでAI出力のブレを補える |
| 3 | CI/CDの構築 | 変更のたびに自動検証が走る状態を作れる |
| 4 | Copilot指示書 | プロジェクト固有の文脈をAIに伝えられる |

**ゴール：** Copilotを使って既存リポジトリの品質基盤を段階的に構築できるようになる

---

## 効果的なプロンプトの書き方：ワンショットとFewショット

**ワンショット** — 指示だけを渡す。シンプルだが文脈不足になりやすい

```text
FlaskアプリのAPIテストをpytestで書いてください
```

**Fewショット（例示付き）** — 入出力の具体例を一緒に渡す。出力精度が上がる

```text
以下のテストを参考に、DELETEエンドポイントのテストを追加してください

【例】
def test_タスクを正常に作成(client):
    res = client.post("/tasks", json={"title": "テスト"})
    assert res.status_code == 201
```

例示があるほど、AIは期待する形式・命名・粒度を正確に再現できる

---

## 今回の手法：ブランチ差分をFewショットとして活用する

本セミナーでは **ブランチ間の差分** を「例示」として渡す：

```text
git@github.com:sotanengel/gitHub-copilot-first-try.git の
step/1-api → step/2-tests ブランチの差分を参考に、
同様の変更を段階的に実装してください
```

**なぜこの方法が効くのか？**
- 差分には「何を」「どこに」「どう」変更したかが全て含まれる
- ワンショットの手軽さで、Fewショット相当の精度が得られる
- 各ステップの差分が独立しているため、段階的に適用できる

---

## サンプルアプリの概要

**FlaskベースのタスクAPI** — シンプルなCRUDアプリケーション

| メソッド | パス | 説明 |
|:---------|:-----|:-----|
| GET | `/tasks` | 全タスク一覧取得 |
| POST | `/tasks` | タスク作成 |
| PUT | `/tasks/<id>` | タスク更新 |
| DELETE | `/tasks/<id>` | タスク削除 |
| PATCH | `/tasks/<id>/toggle` | 完了/未完了トグル |
| GET | `/tasks/search?q=` | タスク検索 |

技術スタック：Python 3.10+ / Flask / SQLite / uv

---

## ブランチ構成：各ステップが独立したブランチになっている

```text
main
  └─ step/1-api                    ← 素のFlask API（テスト・リンターなし）
       └─ step/2-tests             ← テスト追加（22テスト）
            └─ step/3-linter       ← リンター導入（ruff）
                 └─ step/4-cicd    ← CI/CD追加（GitHub Actions）
                      └─ step/5-copilot-instructions ← Copilot指示書
```

各ブランチの差分で「何が追加されたか」が一目瞭然
→ この差分をプロンプトの「例示」として使う

---

## 想定する状況：「よくあるレガシーリポジトリ」

```python
# app.py - FlaskベースのタスクAPIの例
from flask import Flask, request, jsonify
import sqlite3
import os   # ← 未使用のimport

app = Flask(__name__)

@app.route('/tasks', methods=['GET'])
def get_tasks():
    conn = sqlite3.connect('tasks.db')  # テストなし、CIなし
```

**問題点：** テストなし / リンターなし / CI/CDなし → 変更が不安

---

## Step 1：テストの導入 🧪

### Copilotにテスト生成を依頼

**やったこと：**
- `tests/conftest.py` — テストフィクスチャ（一時DB生成）
- `tests/test_api.py` — 各エンドポイントの結合テスト（18テスト）
- `tests/test_scenarios.py` — 複数操作の連結テスト（4テスト）

**ポイント：**
- 既存コード（`app.py`）は **一切変更しない**
- `tmp_path` を使い本番DBに影響しない
- 日本語のテスト名で可読性向上

---

## Step 1：テスト結果

```
tests/test_api.py::TestCreateTask::test_タスクを正常に作成 PASSED
tests/test_api.py::TestDeleteTask::test_タスクを正常に削除 PASSED
tests/test_api.py::TestSearchTasks::test_タスクを検索 PASSED
tests/test_api.py::TestToggleTask::test_タスクの完了状態をトグル PASSED
tests/test_scenarios.py::TestTaskLifecycle::test_タスクの作成_更新_完了_削除フロー PASSED
...
======================== 22 passed in 0.21s ========================
```

✅ **22テスト 全てパス** — 既存コードの変更なしにテストカバレッジを確保

---

## 「決定論」と「確率論」— このスライドでの意味

**決定論（deterministic）**
辞書的意味：同じ条件なら必ず同じ結果になるという考え方
このスライドでは：リンターやCIのように **同じ入力に対して毎回同じ結果** を返すツール

**確率論（probabilistic）**
辞書的意味：結果が確率的に変動するという考え方
このスライドでは：Copilotのように **同じプロンプトでも出力が毎回異なりうる** AI

AIの出力ブレを決定論的ツールで検証する — これがStep 2以降のテーマ

---

## Step 2：リンターの導入 📏

### Copilotにruff設定を依頼 → `pyproject.toml` を自動生成

```toml
[tool.ruff]
target-version = "py310"
line-length = 100

[tool.ruff.lint]
select = ["E", "F", "W", "I", "N", "UP", "B", "SIM"]

[tool.ruff.lint.per-file-ignores]
"tests/**" = ["N802"]  # 日本語テスト名を許可
```

**検出・修正：** 未使用import削除 / importソート / フォーマット統一

---

## Step 3：CI/CDの構築 🔄

### Copilotにワークフローを依頼

```yaml
# .github/workflows/ci.yml
name: CI
on:
  push:
    branches: [main, "step/**"]
jobs:
  lint:     # uv run ruff check + format check
  test:     # uv run pytest（lintパス後に実行）
```

**ポイント：** `astral-sh/setup-uv` で環境非依存にセットアップ
`uv sync --frozen` でロックファイルから再現可能な環境を構築

---

## Step 4：Copilot指示書の作成 📝

### `.github/copilot-instructions.md`

```markdown
# Copilot Instructions
## プロジェクト概要
FlaskベースのタスクAPIです。
## コーディング規約
- ruffの設定(pyproject.toml)に従うこと
- テストの関数名は日本語で記述してよい
## 開発時の注意事項
- 新規エンドポイント追加時はtest_api.pyにテスト追加
- コミット前にuv run ruff check .を実行
- 依存追加はuv addで行う
```

**効果：** Copilotがプロジェクト固有のルールを理解し、的確なコード生成が可能に

---

## 作業のビフォー・アフター

| 項目 | Before | After |
|:-----|:-------|:------|
| テスト | ❌ なし | ✅ 22テスト（結合＋連結） |
| リンター | ❌ なし | ✅ ruff（lint + format） |
| CI/CD | ❌ なし | ✅ GitHub Actions |
| Copilot指示書 | ❌ なし | ✅ copilot-instructions.md |
| コード品質管理 | 🙋 手動 | 🤖 自動化 |

---

## Copilot活用のポイント

### 1. **既存コードを壊さない**
テスト追加時に既存コードは一切変更しなかった

### 2. **段階的に改善する**
テスト → リンター → CI/CD → 指示書の順で段階的に導入

### 3. **指示書でCopilotを「育てる」**
`copilot-instructions.md` でプロジェクト固有の文脈を共有

### 4. **ブランチで変更を可視化**
各改善ステップをブランチで分け、差分を明確にする

---

## まとめ

### GitHub Copilotは「新規開発」だけでなく<br>「既存改善」にも強力なツール

1. **テスト生成** — 既存APIの仕様を読み取り、包括的テストを生成
2. **リンター導入** — 設定ファイルの生成から自動修正まで
3. **CI/CD構築** — プロジェクトに最適なワークフローを提案
4. **指示書作成** — 自身への指示を自分で作れる

> 💡 **「コードを書く」だけでなく「コードベースを良くする」ためにCopilotを使おう**

---

# ご清聴ありがとうございました 🙏

**リポジトリ：** このリポジトリをクローンして各ブランチを確認してください

**質問はありますか？**
