#!/bin/bash
# 仮想環境を使用して実行するスクリプト

VENV_DIR="$HOME/.venv_it_trend_watcher"

if [ ! -d "$VENV_DIR" ]; then
    echo "エラー: 仮想環境が見つかりません。"
    echo "まず setup.sh を実行してください:"
    echo "  bash setup.sh"
    exit 1
fi

# 仮想環境をアクティベート
source "$VENV_DIR/bin/activate"

# プロジェクトディレクトリに移動
cd "$(dirname "$0")"

# 実行
python3 run.py
