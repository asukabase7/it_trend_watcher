"""
TechCrunch記事収集モジュール
"""
import feedparser
import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from config.settings import TECHCRUNCH_RSS, MAX_ARTICLES_PER_SOURCE

logger = logging.getLogger(__name__)


class TechCrunchCollector:
    """TechCrunchから最新記事を収集"""
    
    def __init__(self):
        self.rss_url = TECHCRUNCH_RSS
        self.max_articles = MAX_ARTICLES_PER_SOURCE
    
    def collect(self) -> List[Dict]:
        """
        TechCrunchのRSSフィードから記事を収集
        
        Returns:
            List[Dict]: 記事情報のリスト
                - title: タイトル
                - url: URL
                - published: 公開日時（datetime）
                - summary: 概要
                - needs_translation: 要約が必要か（常にTrue）
        """
        articles = []
        
        try:
            logger.info(f"TechCrunch RSSフィードを取得中: {self.rss_url}")
            feed = feedparser.parse(self.rss_url)
            
            if feed.bozo:
                logger.warning(f"RSSフィードの解析エラー: {feed.bozo_exception}")
            
            entries = feed.entries[:self.max_articles]
            
            for entry in entries:
                try:
                    # 公開日時のパース
                    published = None
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        published = datetime(*entry.published_parsed[:6])
                    elif hasattr(entry, 'published'):
                        # フォールバック: 文字列からパースを試みる
                        try:
                            from dateutil import parser as date_parser
                            published = date_parser.parse(entry.published)
                        except:
                            published = datetime.now()
                    else:
                        published = datetime.now()
                    
                    article = {
                        'title': entry.get('title', 'No Title'),
                        'url': entry.get('link', ''),
                        'published': published,
                        'summary': entry.get('summary', entry.get('description', '')),
                        'needs_translation': True,  # TechCrunchは英語なので常に要約が必要
                        'source': 'TechCrunch'
                    }
                    
                    articles.append(article)
                    
                except Exception as e:
                    logger.error(f"記事の処理中にエラー: {e}")
                    continue
            
            logger.info(f"TechCrunchから {len(articles)} 件の記事を収集しました")
            
        except Exception as e:
            logger.error(f"TechCrunchの収集中にエラーが発生: {e}")
        
        return articles
