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

REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0',
    'Accept': 'application/rss+xml, application/xml, text/xml, */*',
}


class TwitterCollector:
    """X（Twitter）から最新投稿を収集"""
    
    def __init__(self):
        self.targets = TWITTER_TARGETS
        self.max_tweets = MAX_TWEETS_PER_USER

    def _parse_rss_into_tweets(self, response_content: bytes, username: str) -> List[Dict]:
        """RSSレスポンスをパースしてツイートリストを返す。失敗時は空リスト。"""
        import feedparser
        feed = feedparser.parse(response_content)
        if feed.bozo:
            logger.warning(f"RSSフィードの解析エラー: {feed.bozo_exception}")
            return []
        tweets = []
        for entry in feed.entries[:self.max_tweets]:
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
                content = entry.get('title', entry.get('description', ''))
                url = entry.get('link', f"https://twitter.com/{username}/status/unknown")
                tweets.append({
                    'username': username,
                    'content': content,
                    'url': url,
                    'published': published,
                    'needs_translation': True,
                    'source': 'Twitter',
                })
            except Exception as e:
                logger.error(f"ツイートの処理中にエラー: {e}")
        return tweets

    def _try_fetch_rss(self, rss_url: str, username: str, out_tweets: List[Dict]) -> bool:
        """指定URLからRSSを取得しout_tweetsに追記。成功時True。"""
        try:
            logger.info(f"RSSを取得中: {rss_url}")
            response = requests.get(rss_url, headers=REQUEST_HEADERS, timeout=15, allow_redirects=True)
            if response.status_code != 200:
                return False
            parsed = self._parse_rss_into_tweets(response.content, username)
            if parsed:
                out_tweets.extend(parsed)
                logger.info(f"{username} から {len(parsed)} 件のツイートを取得しました")
                return True
        except Exception as e:
            logger.warning(f"RSS取得に失敗: {e}")
        return False
    
    def _get_tweets_via_rss(self, username: str) -> List[Dict]:
        """
        RSSフィード経由でツイートを取得（無料方法）
        
        Args:
            username: Twitterユーザー名
            
        Returns:
            List[Dict]: ツイート情報のリスト
        """
        tweets = []
        
        # Farside: 稼働中のNitterインスタンスへ自動リダイレクト（推奨）
        farside_url = f"https://farside.link/nitter/{username}/rss"
        if self._try_fetch_rss(farside_url, username, tweets):
            return tweets

        # Nitterインスタンスを直指定（Wiki・status.d420.deで稼働報告のあるもの）
        nitter_instances = [
            'https://nitter.privacydev.net',
            'https://nitter.kavin.rocks',
            'https://nitter.poast.org',
            'https://xcancel.com',
            'https://nitter.qwik.space',
            'https://bird.habedieeh.re',
            'https://t.com.sb',
            'https://nitter.lunar.icu',
            'https://nitter.tiekoetter.com',
            'https://nitter.privacyredirect.com',
            'https://nitter.net',
        ]
        
        for instance in nitter_instances:
            rss_url = f"{instance}/{username}/rss"
            if self._try_fetch_rss(rss_url, username, tweets):
                break
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
