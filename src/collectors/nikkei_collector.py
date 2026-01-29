"""
日経電子版テック面記事収集モジュール
"""
import feedparser
import requests
from bs4 import BeautifulSoup
import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from config.settings import NIKKEI_TECH_RSS, MAX_ARTICLES_PER_SOURCE

logger = logging.getLogger(__name__)


class NikkeiCollector:
    """日経電子版テック面から記事を収集"""
    
    def __init__(self):
        self.rss_url = NIKKEI_TECH_RSS
        self.max_articles = MAX_ARTICLES_PER_SOURCE
    
    def _detect_language(self, text: str) -> bool:
        """
        テキストが英語かどうかを簡易判定
        
        Args:
            text: 判定するテキスト
            
        Returns:
            bool: 英語の場合True、日本語の場合False
        """
        if not text:
            return False
        
        # 英語文字（A-Z, a-z）の割合を計算
        english_chars = sum(1 for c in text if c.isascii() and c.isalpha())
        total_chars = sum(1 for c in text if c.isalpha())
        
        if total_chars == 0:
            return False
        
        # 50%以上が英語文字なら英語と判定
        return (english_chars / total_chars) > 0.5
    
    def collect(self) -> List[Dict]:
        """
        日経電子版テック面のRSSフィードから記事を収集
        
        Returns:
            List[Dict]: 記事情報のリスト
                - title: タイトル
                - url: URL
                - published: 公開日時（datetime）
                - summary: 概要
                - needs_translation: 要約が必要か（英語記事の場合True）
        """
        articles = []
        
        try:
            logger.info(f"日経電子版RSSフィードを取得中: {self.rss_url}")
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
                        try:
                            from dateutil import parser as date_parser
                            published = date_parser.parse(entry.published)
                        except:
                            published = datetime.now()
                    else:
                        published = datetime.now()
                    
                    title = entry.get('title', 'No Title')
                    summary = entry.get('summary', entry.get('description', ''))
                    
                    # タイトルと概要から言語を判定
                    is_english = self._detect_language(title + ' ' + summary)
                    
                    article = {
                        'title': title,
                        'url': entry.get('link', ''),
                        'published': published,
                        'summary': summary,
                        'needs_translation': is_english,
                        'source': '日経電子版'
                    }
                    
                    articles.append(article)
                    
                except Exception as e:
                    logger.error(f"記事の処理中にエラー: {e}")
                    continue
            
            logger.info(f"日経電子版から {len(articles)} 件の記事を収集しました")
            
        except Exception as e:
            logger.error(f"日経電子版の収集中にエラーが発生: {e}")
        
        return articles
