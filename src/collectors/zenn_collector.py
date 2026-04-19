"""
Zenn Techトピック記事収集モジュール
"""
import feedparser
import requests
import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from config.settings import ZENN_TOPICS_TECH_RSS, MAX_ARTICLES_PER_SOURCE

logger = logging.getLogger(__name__)

REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0',
    'Accept': 'application/rss+xml, application/xml, text/xml, */*',
}


class ZennCollector:
    """ZennのTechトピックから最新記事を収集（日本語ソースのため要約不要）"""

    def __init__(self):
        self.rss_url = ZENN_TOPICS_TECH_RSS
        self.max_articles = MAX_ARTICLES_PER_SOURCE

    def collect(self) -> List[Dict]:
        """
        Zenn TechトピックのRSSフィードから記事を収集

        Returns:
            List[Dict]: 記事情報のリスト
                - title: タイトル
                - url: URL
                - published: 公開日時（datetime）
                - summary: 概要
                - needs_translation: 要約が必要か（Zennは日本語のためFalse）
        """
        articles = []

        try:
            logger.info(f"Zenn RSSフィードを取得中: {self.rss_url}")
            resp = requests.get(self.rss_url, headers=REQUEST_HEADERS, timeout=15)
            resp.raise_for_status()
            feed = feedparser.parse(resp.content)

            if feed.bozo:
                logger.warning(f"RSSフィードの解析エラー: {feed.bozo_exception}")

            entries = feed.entries[:self.max_articles]

            for entry in entries:
                try:
                    published = None
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        published = datetime(*entry.published_parsed[:6])
                    elif hasattr(entry, 'published'):
                        try:
                            from dateutil import parser as date_parser
                            published = date_parser.parse(entry.published)
                        except Exception:
                            published = datetime.now()
                    else:
                        published = datetime.now()

                    article = {
                        'title': entry.get('title', 'No Title'),
                        'url': entry.get('link', ''),
                        'published': published,
                        'summary': entry.get('summary', entry.get('description', '')),
                        'needs_translation': False,  # Zennは日本語ソースのため要約不要
                        'source': 'Zenn',
                    }
                    articles.append(article)

                except Exception as e:
                    logger.error(f"記事の処理中にエラー: {e}")
                    continue

            logger.info(f"Zennから {len(articles)} 件の記事を収集しました")

        except Exception as e:
            logger.error(f"Zennの収集中にエラーが発生: {e}")

        return articles
