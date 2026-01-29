"""
設定管理モジュール
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# プロジェクトルートディレクトリを取得
PROJECT_ROOT = Path(__file__).parent.parent

# .envファイルを読み込み
env_path = PROJECT_ROOT / '.env'
load_dotenv(env_path)

# API設定
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
TWITTER_API_KEY = os.getenv('TWITTER_API_KEY', '')
TWITTER_API_SECRET = os.getenv('TWITTER_API_SECRET', '')

# RSSフィードURL
NIKKEI_TECH_RSS = 'https://www.nikkei.com/technology/rss.xml'
TECHCRUNCH_RSS = 'https://techcrunch.com/feed/'

# Twitter収集対象アカウント
TWITTER_TARGETS = [
    'karpathy',  # Andrej Karpathy
    'jasonlk',   # Jason Lemkin
]

# 出力設定
OUTPUT_DIR = PROJECT_ROOT / 'daily_vibes'

# 収集設定
MAX_ARTICLES_PER_SOURCE = 10  # 各ソースから取得する最大記事数
MAX_TWEETS_PER_USER = 5       # 各ユーザーから取得する最大ツイート数

# Gemini API設定
GEMINI_MODEL = 'gemini-pro'
GEMINI_MAX_TOKENS = 500
GEMINI_TEMPERATURE = 0.7
