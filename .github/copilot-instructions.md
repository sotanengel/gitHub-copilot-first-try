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
