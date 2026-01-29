#!/bin/bash
# ITトレンド・ウォッチャー セットアップスクリプト

set -e

echo "=========================================="
echo "ITトレンド・ウォッチャー セットアップ"
echo "=========================================="
echo ""

# プロジェクトディレクトリに移動
cd "$(dirname "$0")"

# 仮想環境のパス（ホームディレクトリに作成）
VENV_DIR="$HOME/.venv_it_trend_watcher"

echo "[Step 1] 仮想環境を作成中..."
if [ -d "$VENV_DIR" ]; then
    echo "仮想環境は既に存在します: $VENV_DIR"
else
    python3 -m venv "$VENV_DIR"
    echo "✓ 仮想環境を作成しました: $VENV_DIR"
fi

echo ""
echo "[Step 2] 仮想環境をアクティベート中..."
source "$VENV_DIR/bin/activate"

echo ""
echo "[Step 3] pipをアップグレード中..."
pip install --upgrade pip

echo ""
echo "[Step 4] 依存パッケージをインストール中..."
pip install -r requirements.txt

echo ""
echo "=========================================="
echo "セットアップが完了しました！"
echo "=========================================="
echo ""
echo "仮想環境をアクティベートするには:"
echo "  source $VENV_DIR/bin/activate"
echo ""
echo "実行するには:"
echo "  source $VENV_DIR/bin/activate"
echo "  python3 run.py"
echo ""
