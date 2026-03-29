# GitHub Copilotを使った既存リポジトリへの有効活用方法

テスト・リンター・CIが一切ない素のFlask APIに対して、GitHub Copilotを活用しながら段階的にコード品質を改善していくデモリポジトリです。

## 概要

「既存のレガシーコードにどうやってCopilotを活かすか？」をテーマに、以下の改善プロセスをブランチごとに記録しています。

## ブランチ構成

各ブランチは前のブランチから分岐しており、差分を見ることで何が追加されたかを確認できます。

```
main
  └─ step/1-api                    ← 素のFlask API（テスト・リンターなし）
       └─ step/2-tests             ← テスト追加（22テスト）
            └─ step/3-linter       ← リンター導入（ruff）
                 └─ step/4-cicd    ← CI/CD追加（GitHub Actions）
                      └─ step/5-copilot-instructions ← Copilot指示書
                           └─ step/6-slides          ← 発表スライド
```

| ブランチ | 内容 | ポイント |
|---------|------|---------|
| `step/1-api` | Flask製タスク管理API | テストなし・リンターなし・CIなし |
| `step/2-tests` | pytest結合テスト＋連結テスト | 既存コード（app.py）を一切変更せずにテスト追加 |
| `step/3-linter` | ruffリンター導入＋コード整形 | pyproject.toml設定、未使用importの削除等 |
| `step/4-cicd` | GitHub Actions CI/CD | lint → testの2ステージパイプライン |
| `step/5-copilot-instructions` | Copilot指示書 | プロジェクト固有のルールをCopilotに伝える |
| `step/6-slides` | Marp形式の発表スライド | 10分のプレゼン用 |

## 技術スタック

- **言語**: Python 3.10+
- **フレームワーク**: Flask
- **データベース**: SQLite
- **パッケージ管理**: uv
- **テスト**: pytest
- **リンター/フォーマッター**: ruff
- **CI/CD**: GitHub Actions
- **スライド**: Marp

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
uv run python app.py
```

## テスト・リントの実行

```bash
# テスト
uv run pytest tests/ -v

# リント
uv run ruff check .
uv run ruff format --check .
```

## ライセンス

[MIT](LICENSE)
