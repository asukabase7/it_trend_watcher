"""
Markdown形式で出力するモジュール
"""
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from config.settings import OUTPUT_DIR

logger = logging.getLogger(__name__)


class MarkdownWriter:
    """Markdown形式でファイルに出力"""
    
    def __init__(self):
        self.output_dir = Path(OUTPUT_DIR)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def _format_date(self, dt: datetime) -> str:
        """日時をフォーマット"""
        return dt.strftime('%Y-%m-%d %H:%M')
    
    def _format_date_only(self, dt: datetime) -> str:
        """日付のみをフォーマット"""
        return dt.strftime('%Y-%m-%d')
    
    def _format_relative_time(self, dt: datetime) -> str:
        """相対時間をフォーマット（例: 2時間前）"""
        now = datetime.now()
        diff = now - dt
        
        if diff.days > 0:
            return f"{diff.days}日前"
        elif diff.seconds >= 3600:
            hours = diff.seconds // 3600
            return f"{hours}時間前"
        elif diff.seconds >= 60:
            minutes = diff.seconds // 60
            return f"{minutes}分前"
        else:
            return "たった今"

    def _short_title(self, title: str, max_len: int = 50) -> str:
        """見出し用にタイトルを短くする（スマホカード用）"""
        if not title:
            return "（タイトルなし）"
        t = title.strip()
        return (t[:max_len] + "…") if len(t) > max_len else t

    def write(self, date: datetime, nikkei_articles: List[Dict],
              twitter_tweets: List[Dict], techcrunch_articles: List[Dict],
              zenn_articles: List[Dict], qiita_articles: List[Dict] = None) -> Path:
        """
        Markdownファイルを生成（アプリ風デザイン）
        セクション順: TechCrunch -> Zenn -> Qiita -> 日経 -> Twitter
        """
        if qiita_articles is None:
            qiita_articles = []
        filename = f"log_{date.strftime('%Y%m%d')}.md"
        filepath = self.output_dir / filename
        
        content = []
        total_items = len(nikkei_articles) + len(twitter_tweets) + len(techcrunch_articles) + len(zenn_articles) + len(qiita_articles)
        date_str = date.strftime('%Y年%m月%d日')
        weekday = ['月', '火', '水', '木', '金', '土', '日'][date.weekday()]
        
        content.append("---\n")
        content.append(f"# 📱 ITトレンド・ウォッチャー\n\n")
        content.append(f"<div align=\"center\">\n\n")
        content.append(f"### 📅 {date_str}（{weekday}）\n\n")
        content.append(f"**📊 本日の収集結果**\n\n")
        content.append(f"| 🌐 TechCrunch | 📘 Zenn | 📝 Qiita | 📰 日経 | 🐦 Twitter | 📈 合計 |\n")
        content.append(f"|:---:|:---:|:---:|:---:|:---:|:---:|\n")
        content.append(f"| **{len(techcrunch_articles)}** | **{len(zenn_articles)}** | **{len(qiita_articles)}** | **{len(nikkei_articles)}** | **{len(twitter_tweets)}** | **{total_items}** |\n\n")
        content.append(f"</div>\n\n")
        content.append("---\n\n")
        
        # TechCrunchセクション（安定ソース・先頭）
        content.append("## 🌐 TechCrunch\n\n")
        if techcrunch_articles:
            for idx, article in enumerate(techcrunch_articles, 1):
                title_full = article.get('title', 'No Title')
                title_short = self._short_title(title_full)
                url = article.get('url', '')
                published = article.get('published', datetime.now())
                summary_jp = article.get('summary_jp', '')
                relative_time = self._format_relative_time(published)
                date_only = self._format_date_only(published)
                content.append(f"### 🚀 {idx}. {title_short}\n\n")
                content.append(f"<small>🕒 {relative_time} ({date_only})</small>\n\n")
                if summary_jp:
                    content.append("> **AI要約**:\n")
                    for line in summary_jp.strip().split('\n'):
                        content.append(f"> {line.strip()}\n")
                    content.append("\n")
                else:
                    content.append("> 要約は利用できませんでした\n\n")
                if url:
                    content.append(f"[記事を読む]({url})\n\n")
                content.append("---\n\n")
        else:
            content.append("📭 本日の記事はありません\n\n")
        
        # Zennセクション（安定ソース・カード型）
        content.append("## 📘 Zenn（Tech）\n\n")
        if zenn_articles:
            for idx, article in enumerate(zenn_articles, 1):
                title_full = article.get('title', 'No Title')
                title_short = self._short_title(title_full)
                url = article.get('url', '')
                published = article.get('published', datetime.now())
                summary = article.get('summary', '')
                relative_time = self._format_relative_time(published)
                date_only = self._format_date_only(published)
                content.append(f"### 📄 {idx}. {title_short}\n\n")
                content.append(f"<small>🕒 {relative_time} ({date_only})</small>\n\n")
                if summary:
                    preview = summary[:300] + "…" if len(summary) > 300 else summary
                    content.append("> **概要**:\n")
                    content.append(f"> {preview}\n\n")
                if url:
                    content.append(f"[記事を読む]({url})\n\n")
                content.append("---\n\n")
        else:
            content.append("📭 本日の記事はありません\n\n")
        
        # Qiitaセクション（日本語ソース・カード型）
        content.append("## 📝 Qiita（Tech）\n\n")
        if qiita_articles:
            for idx, article in enumerate(qiita_articles, 1):
                title_full = article.get('title', 'No Title')
                title_short = self._short_title(title_full)
                url = article.get('url', '')
                published = article.get('published', datetime.now())
                summary = article.get('summary', '')
                relative_time = self._format_relative_time(published)
                date_only = self._format_date_only(published)
                content.append(f"### 📄 {idx}. {title_short}\n\n")
                content.append(f"<small>🕒 {relative_time} ({date_only})</small>\n\n")
                if summary:
                    preview = summary[:300] + "…" if len(summary) > 300 else summary
                    content.append("> **概要**:\n")
                    content.append(f"> {preview}\n\n")
                if url:
                    content.append(f"[記事を読む]({url})\n\n")
                content.append("---\n\n")
        else:
            content.append("📭 本日の記事はありません\n\n")
        
        # 日経電子版セクション（一時無効時は0件）
        content.append("## 🇯🇵 日経電子版テック面\n\n")
        if nikkei_articles:
            for idx, article in enumerate(nikkei_articles, 1):
                title_full = article.get('title', 'No Title')
                title_short = self._short_title(title_full)
                url = article.get('url', '')
                published = article.get('published', datetime.now())
                summary = article.get('summary', '')
                summary_jp = article.get('summary_jp', '')
                needs_translation = article.get('needs_translation', False)
                relative_time = self._format_relative_time(published)
                date_only = self._format_date_only(published)
                content.append(f"### 📄 {idx}. {title_short}\n\n")
                content.append(f"<small>🕒 {relative_time} ({date_only})</small>\n\n")
                if needs_translation and summary_jp:
                    content.append("> **AI要約**:\n")
                    for line in summary_jp.strip().split('\n'):
                        content.append(f"> {line.strip()}\n")
                    content.append("\n")
                elif needs_translation:
                    content.append("> 要約は利用できませんでした\n\n")
                elif summary:
                    preview = summary[:300] + "…" if len(summary) > 300 else summary
                    content.append("> **概要**:\n")
                    content.append(f"> {preview}\n\n")
                if url:
                    content.append(f"[記事を読む]({url})\n\n")
                content.append("---\n\n")
        else:
            content.append("📭 本日の記事はありません\n\n")
        
        # Twitterセクション（カード型・スマホ最適化）
        content.append("## 🐦 X（Twitter）\n\n")
        if twitter_tweets:
            tweets_by_user = {}
            for tweet in twitter_tweets:
                username = tweet.get('username', 'unknown')
                if username not in tweets_by_user:
                    tweets_by_user[username] = []
                tweets_by_user[username].append(tweet)
            for username, tweets in tweets_by_user.items():
                content.append(f"### 👤 @{username}\n\n")
                for idx, tweet in enumerate(tweets, 1):
                    content_text = tweet.get('content', '')
                    url = tweet.get('url', '')
                    published = tweet.get('published', datetime.now())
                    summary_jp = tweet.get('summary_jp', '')
                    relative_time = self._format_relative_time(published)
                    date_only = self._format_date_only(published)
                    content.append(f"**💬 ツイート #{idx}** <small>🕒 {relative_time} ({date_only})</small>\n\n")
                    if content_text:
                        display_text = content_text[:280] + "…" if len(content_text) > 280 else content_text
                        for line in display_text.strip().split('\n'):
                            content.append(f"> {line.strip()}\n")
                        content.append("\n")
                    else:
                        content.append("> *（本文なし）*\n\n")
                    if summary_jp:
                        content.append("> **AI要約**:\n")
                        for line in summary_jp.strip().split('\n'):
                            content.append(f"> {line.strip()}\n")
                        content.append("\n")
                    else:
                        content.append("> 要約は利用できませんでした\n\n")
                    if url:
                        content.append(f"[元ツイートを見る]({url})\n\n")
                    content.append("---\n\n")
        else:
            content.append("📭 本日のツイートはありません\n\n")
        
        # フッター（アプリ風）
        content.append("\n---\n\n")
        content.append("<div align=\"center\">\n\n")
        content.append(f"**🤖 自動生成レポート**\n\n")
        content.append(f"生成日時: `{self._format_date(datetime.now())}`\n\n")
        content.append("---\n\n")
        content.append("**💡 このレポートは毎日自動的に更新されます**\n\n")
        content.append("</div>\n")
        
        # ファイルに書き込み
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(''.join(content))
            
            logger.info(f"Markdownファイルを生成しました: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Markdownファイルの書き込みエラー: {e}")
            raise
