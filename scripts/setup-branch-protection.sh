#!/usr/bin/env bash
set -euo pipefail

# ブランチ保護ルールを .github/branch-protection.json から適用するスクリプト
# 前提: gh CLI がインストール済み & 認証済み

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
CONFIG_FILE="$REPO_ROOT/.github/branch-protection.json"

if [[ ! -f "$CONFIG_FILE" ]]; then
  echo "❌ 設定ファイルが見つかりません: $CONFIG_FILE"
  exit 1
fi

# リポジトリのオーナー/名前を自動取得
REPO=$(gh repo view --json nameWithOwner -q '.nameWithOwner')
BRANCH=$(jq -r '.branch' "$CONFIG_FILE")

echo "📋 ブランチ保護ルールを適用します"
echo "   リポジトリ: $REPO"
echo "   ブランチ:   $BRANCH"
echo ""

# branch-protection.json から branch キーを除いた内容を API に送信
jq 'del(.branch)' "$CONFIG_FILE" | \
  gh api \
    --method PUT \
    "repos/$REPO/branches/$BRANCH/protection" \
    --input -

echo ""
echo "✅ ブランチ保護ルールを適用しました"
echo ""
echo "設定内容:"
echo "  - PRレビュー必須（1名以上の承認）"
echo "  - 古いレビューの自動却下"
echo "  - ステータスチェック必須（Lint, Test）"
echo "  - 管理者にも適用"
echo "  - Force Push 禁止"
echo "  - ブランチ削除禁止"
