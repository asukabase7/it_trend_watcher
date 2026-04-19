#!/usr/bin/env python3
"""
.env と API 設定の確認スクリプト
（APIキーの値は表示しません）
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv(project_root / '.env')

import os

def main():
    env_path = project_root / '.env'
    
    print("=" * 50)
    print("環境・API 設定の確認")
    print("=" * 50)
    print(f"\n読み込み元: {env_path}")
    print(f".env の存在: {'あり' if env_path.exists() else 'なし（作成してください）'}")
    
    # Gemini API（値は表示せず長さのみ）
    key = os.getenv('GEMINI_API_KEY', '')
    key = key.strip() if key else ''
    key_len = len(key)
    
    PLACEHOLDER = 'your_api_key_here'
    if key_len and key != PLACEHOLDER:
        print(f"GEMINI_API_KEY: 設定済み（{key_len} 文字）→ 要約が有効になります")
    else:
        print("GEMINI_API_KEY: 未設定 または プレースホルダーのまま")
        if key == PLACEHOLDER or (key_len == 17 and key == PLACEHOLDER):
            print("  → .env の「your_api_key_here」を、Google AI Studio で取得した実際のキーに置き換えてください")
        print("  → 形式（余計なスペース・クォートなし）: GEMINI_API_KEY=AIzaで始まるキー")
        print("  → 取得: https://aistudio.google.com/ → Get API key")
    
    # Twitter は Nitter RSS のため API 不要
    print("\nTwitter（X）: APIキーは使用していません（無料の Nitter RSS で取得）")
    
    print("\n" + "=" * 50)
    print("0件になる主な理由")
    print("=" * 50)
    print("・日経: RSS の XML が不正でパースに失敗している場合があります")
    print("・Twitter: Nitter のサーバーが応答していない／ブロックされている場合があります")
    print("・TechCrunch が 10 件取れていれば、プログラム自体は正常に動いています")
    print("=" * 50)

if __name__ == '__main__':
    main()
