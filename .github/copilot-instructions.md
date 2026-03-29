# Copilot Instructions

## プロジェクト概要

このリポジトリはFlaskベースのタスク管理APIです。SQLiteをデータベースとして使用し、タスクのCRUD操作および検索・トグル機能を提供します。

## 技術スタック

- **言語**: Python 3.10+
- **フレームワーク**: Flask
- **データベース**: SQLite
- **パッケージ管理**: uv
- **テスト**: pytest
- **リンター/フォーマッター**: ruff
- **CI/CD**: GitHub Actions

## コーディング規約

- ruffの設定(`pyproject.toml`)に従うこと
- 行の最大長: 100文字
- importの整列にはruffのisortルールを使用
- テストの関数名は日本語で記述してよい（`test_タスクを作成` 等）

## プロジェクト構成

```
app.py              # メインアプリケーション（Flask API）
pyproject.toml      # プロジェクト設定・依存関係・ruff設定
uv.lock             # 依存関係のロックファイル
.python-version     # Pythonバージョン指定
tests/
  conftest.py       # テストのフィクスチャ定義
  test_api.py       # 各エンドポイントの結合テスト
  test_scenarios.py # 複数操作の連結テスト
.github/
  workflows/
    ci.yml          # CI/CDワークフロー
    branch-protection.yml  # ブランチ保護自動適用ワークフロー
  branch-protection.json  # ブランチ保護ルール定義
scripts/
  setup-branch-protection.sh  # ブランチ保護適用スクリプト
```

## API仕様

| メソッド | パス | 説明 |
|---------|------|------|
| GET | `/tasks` | 全タスク一覧取得 |
| GET | `/tasks/<id>` | タスク詳細取得 |
| POST | `/tasks` | タスク作成 |
| PUT | `/tasks/<id>` | タスク更新 |
| DELETE | `/tasks/<id>` | タスク削除 |
| GET | `/tasks/search?q=` | タスク検索 |
| PATCH | `/tasks/<id>/toggle` | 完了/未完了トグル |

## セットアップ

```bash
uv sync
```

## テストの実行

```bash
uv run pytest tests/ -v
```

## リントの実行

```bash
uv run ruff check .
uv run ruff format --check .
```

## 開発時の注意事項

- データベースはファイルベース（`tasks.db`）。テスト時は`tmp_path`で一時DBを使用する
- 新しいエンドポイントを追加した場合は、`tests/test_api.py`に結合テストを追加すること
- 複数エンドポイントを跨ぐシナリオテストは`tests/test_scenarios.py`に追加すること
- コミット前に`uv run ruff check .`と`uv run ruff format --check .`を実行すること
- 依存関係の追加は`uv add <パッケージ名>`で行うこと（requirements.txtは使用しない）

## スライドデザインの確認サイクル

`slides/slides.md`（Marp形式）を編集した後は、以下のサイクルで文字はみ出し等のデザイン崩れを確認・修正すること。

### 手順

1. **画像エクスポート**: `marp slides/slides.md --images png -o slides_images/slide.png` で全スライドをPNG画像に書き出す
2. **画像確認**: `slides_images/` 内の各画像を1枚ずつ目視確認する（Copilotに画像を見せて確認させてもOK）
3. **問題の特定**: 以下の観点でチェックする
   - テキストがスライド下部やフッターにはみ出していないか
   - コードブロックが横に切れていないか
   - 表やリストがスライド領域を超えていないか
4. **修正**: 問題があれば`slides/slides.md`を修正（コンテンツ量削減、1行にまとめる等）
5. **再確認**: 手順1に戻り、問題がなくなるまで繰り返す

### 修正のコツ

- 箇条書き（`-`）をインラインの `/` 区切りにまとめると縦スペースを節約できる
- `###` よりも `##` の見出し＋インライン説明の方がコンパクト
- コードブロックの空行を減らす
- `slides_images/` は`.gitignore`に追加済みのためコミットされない

## ブランチ保護の適用

`main`ブランチの保護ルールはコードベースで管理している。

### 設定ファイル

- `.github/branch-protection.json` — 保護ルールの定義（レビュー必須、ステータスチェック必須等）
- `.github/workflows/branch-protection.yml` — mainへのマージ時に自動適用するワークフロー
- `scripts/setup-branch-protection.sh` — `gh` CLIで手動適用するスクリプト（初回セットアップ用）

### 自動適用

`.github/branch-protection.json` を変更するPRがmainにマージされると、GitHub Actionsが自動的に保護ルールを適用する。

**前提条件:** リポジトリの Settings > Secrets に `BRANCH_PROTECTION_TOKEN`（`admin` 権限付きPersonal Access Token）を設定すること。

### 手動適用（初回セットアップ）

```bash
./scripts/setup-branch-protection.sh
```

前提条件: `gh` CLI がインストール済み＆認証済み、`jq` がインストール済みであること。

### 保護ルールの内容

- PRレビュー必須（1名以上の承認）
- 古いレビューの自動却下
- ステータスチェック必須（Lint, Test）
- 管理者にも適用
- Force Push 禁止
- ブランチ削除禁止

## PR作成ガイド

開発作業が完了したら、`.github/pull_request_template.md`のテンプレートに従ってPR文を作成すること。

### Copilotへの依頼方法

作業完了後に以下のように依頼すると、Copilotがブランチの差分を読み取りPR文を自動生成する：

> 「このブランチの変更内容を元に、PRテンプレートに沿ったPR文を作成してください」

### PR文作成の手順

1. `git diff <ベースブランチ>..HEAD --stat` で変更ファイル一覧を確認
2. 各変更ファイルの差分内容を読み取る
3. `.github/pull_request_template.md` のテンプレートに沿って以下を埋める：
   - **概要**: 変更の目的を1〜2文で要約
   - **変更内容**: 具体的な変更点をリストアップ
   - **変更の種類**: 該当するチェックボックスにチェック
   - **テスト**: 実行すべきテストコマンドと確認事項
4. 生成されたPR文をクリップボードにコピーまたはファイル出力する
