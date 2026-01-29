#!/usr/bin/env python3
"""
実行スクリプト（エントリーポイント）
"""
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.main import main

if __name__ == '__main__':
    sys.exit(main())
