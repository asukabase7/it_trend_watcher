"""
X（Twitter）投稿収集モジュール
"""
import requests
import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from config.settings import TWITTER_TARGETS, MAX_TWEETS_PER_USER

logger = logging.getLogger(__name__)


class TwitterCollector:
    """X（Twitter）から最新投稿を収集"""
    
    def __init__(self):
        self.targets = TWITTER_TARGETS
        self.max_tweets = MAX_TWEETS_PER_USER
    
    def _get_tweets_via_rss(self, username: str) -> List[Dict]:
        """
        RSSフィード経由でツイートを取得（無料方法）
        
        Args:
            username: Twitterユーザー名
            
        Returns:
            List[Dict]: ツイート情報のリスト
        """
        tweets = []
        
        # Nitterインスタンス経由でRSSを取得
        # 複数のNitterインスタンスを試行
        nitter_instances = [
            'https://nitter.net',
            'https://nitter.it',
            'https://nitter.pussthecat.org',
        ]
        
        for instance in nitter_instances:
            try:
                rss_url = f"{instance}/{username}/rss"
                logger.info(f"Nitter経由でRSSを取得中: {rss_url}")
                
                response = requests.get(rss_url, timeout=10)
                if response.status_code == 200:
                    import feedparser
                    feed = feedparser.parse(response.content)
                    
                    if feed.bozo:
                        logger.warning(f"RSSフィードの解析エラー: {feed.bozo_exception}")
                        continue
                    
                    entries = feed.entries[:self.max_tweets]
                    
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
                            
                            # ツイート本文を取得（RSSのタイトルまたは説明から）
                            content = entry.get('title', entry.get('description', ''))
                            
                            # URLを取得
                            url = entry.get('link', f"https://twitter.com/{username}/status/unknown")
                            
                            tweet = {
                                'username': username,
                                'content': content,
                                'url': url,
                                'published': published,
                                'needs_translation': True,  # Twitterは英語が多いので要約が必要
                                'source': 'Twitter'
                            }
                            
                            tweets.append(tweet)
                            
                        except Exception as e:
                            logger.error(f"ツイートの処理中にエラー: {e}")
                            continue
                    
                    logger.info(f"{username} から {len(tweets)} 件のツイートを取得しました")
                    break  # 成功したらループを抜ける
                    
            except Exception as e:
                logger.warning(f"Nitterインスタンス {instance} での取得に失敗: {e}")
                continue
        
        return tweets
    
    def collect(self) -> List[Dict]:
        """
        対象ユーザーから最新ツイートを収集
        
        Returns:
            List[Dict]: ツイート情報のリスト
                - username: ユーザー名
                - content: ツイート内容
                - url: ツイートURL
                - published: 投稿日時（datetime）
                - needs_translation: 要約が必要か（常にTrue）
        """
        all_tweets = []
        
        for username in self.targets:
            try:
                logger.info(f"Twitterユーザー @{username} のツイートを収集中...")
                tweets = self._get_tweets_via_rss(username)
                all_tweets.extend(tweets)
                
            except Exception as e:
                logger.error(f"@{username} の収集中にエラーが発生: {e}")
                continue
        
        logger.info(f"合計 {len(all_tweets)} 件のツイートを収集しました")
        return all_tweets
