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
    
    def write(self, date: datetime, nikkei_articles: List[Dict], 
              twitter_tweets: List[Dict], techcrunch_articles: List[Dict]) -> Path:
        """
        Markdownファイルを生成（アプリ風デザイン）
        
        Args:
            date: 日付
            nikkei_articles: 日経記事リスト
            twitter_tweets: Twitterツイートリスト
            techcrunch_articles: TechCrunch記事リスト
            
        Returns:
            Path: 生成されたファイルのパス
        """
        filename = f"log_{date.strftime('%Y%m%d')}.md"
        filepath = self.output_dir / filename
        
        # Markdownコンテンツを構築
        content = []
        
        # 統計情報を計算
        total_items = len(nikkei_articles) + len(twitter_tweets) + len(techcrunch_articles)
        
        # ヘッダー（アプリ風）
        date_str = date.strftime('%Y年%m月%d日')
        weekday = ['月', '火', '水', '木', '金', '土', '日'][date.weekday()]
        
        content.append("---\n")
        content.append(f"# 📱 ITトレンド・ウォッチャー\n\n")
        content.append(f"<div align=\"center\">\n\n")
        content.append(f"### 📅 {date_str}（{weekday}）\n\n")
        content.append(f"**📊 本日の収集結果**\n\n")
        content.append(f"| 📰 日経 | 🐦 Twitter | 🌐 TechCrunch | 📈 合計 |\n")
        content.append(f"|:---:|:---:|:---:|:---:|\n")
        content.append(f"| **{len(nikkei_articles)}** | **{len(twitter_tweets)}** | **{len(techcrunch_articles)}** | **{total_items}** |\n\n")
        content.append(f"</div>\n\n")
        content.append("---\n\n")
        
        # 日経電子版セクション（カード形式）
        content.append("## 🇯🇵 日経電子版テック面\n\n")
        if nikkei_articles:
            for idx, article in enumerate(nikkei_articles, 1):
                title = article.get('title', 'No Title')
                url = article.get('url', '')
                published = article.get('published', datetime.now())
                summary = article.get('summary', '')
                summary_jp = article.get('summary_jp', '')
                needs_translation = article.get('needs_translation', False)
                relative_time = self._format_relative_time(published)
                
                content.append(f"### 📄 {idx}. [{title}]({url})\n\n")
                content.append(f"<div style=\"background-color: #f6f8fa; padding: 12px; border-radius: 8px; margin: 8px 0;\">\n\n")
                
                content.append(f"**🕐 公開日時**: `{self._format_date(published)}` ({relative_time})\n\n")
                
                if needs_translation and summary_jp:
                    content.append(f"**📝 AI要約**:\n\n")
                    content.append(f"> {summary_jp}\n\n")
                elif summary:
                    preview = summary[:300] + "..." if len(summary) > 300 else summary
                    content.append(f"**📄 概要**:\n\n")
                    content.append(f"> {preview}\n\n")
                
                content.append(f"**🔗 [記事を読む →]({url})**\n\n")
                content.append(f"</div>\n\n")
                content.append("---\n\n")
        else:
            content.append("<div align=\"center\" style=\"padding: 40px;\">\n\n")
            content.append("📭 本日の記事はありません\n\n")
            content.append("</div>\n\n")
        
        # Twitterセクション（カード形式）
        content.append("## 🐦 X（Twitter）\n\n")
        if twitter_tweets:
            # ユーザーごとにグループ化
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
                    
                    content.append(f"**💬 ツイート #{idx}**\n\n")
                    content.append(f"<div style=\"background-color: #f0f9ff; padding: 12px; border-left: 4px solid #1da1f2; border-radius: 8px; margin: 8px 0;\">\n\n")
                    
                    if content_text:
                        # ツイート内容を表示（改行を保持）
                        display_text = content_text.replace('\n', '  \n')
                        if len(content_text) > 280:
                            display_text = content_text[:280] + "..."
                        content.append(f"{display_text}\n\n")
                    
                    content.append(f"**🕐 投稿日時**: `{self._format_date(published)}` ({relative_time})\n\n")
                    
                    if summary_jp:
                        content.append(f"**📝 AI要約**:\n\n")
                        content.append(f"> {summary_jp}\n\n")
                    
                    content.append(f"**🔗 [ツイートを見る →]({url})**\n\n")
                    content.append(f"</div>\n\n")
                
                content.append("---\n\n")
        else:
            content.append("<div align=\"center\" style=\"padding: 40px;\">\n\n")
            content.append("📭 本日のツイートはありません\n\n")
            content.append("</div>\n\n")
        
        # TechCrunchセクション（カード形式）
        content.append("## 🌐 TechCrunch\n\n")
        if techcrunch_articles:
            for idx, article in enumerate(techcrunch_articles, 1):
                title = article.get('title', 'No Title')
                url = article.get('url', '')
                published = article.get('published', datetime.now())
                summary_jp = article.get('summary_jp', '')
                relative_time = self._format_relative_time(published)
                
                content.append(f"### 🚀 {idx}. [{title}]({url})\n\n")
                content.append(f"<div style=\"background-color: #fff5f5; padding: 12px; border-radius: 8px; margin: 8px 0;\">\n\n")
                
                content.append(f"**🕐 公開日時**: `{self._format_date(published)}` ({relative_time})\n\n")
                
                if summary_jp:
                    content.append(f"**📝 AI要約**:\n\n")
                    content.append(f"> {summary_jp}\n\n")
                else:
                    content.append(f"*要約を生成中...*\n\n")
                
                content.append(f"**🔗 [記事を読む →]({url})**\n\n")
                content.append(f"</div>\n\n")
                content.append("---\n\n")
        else:
            content.append("<div align=\"center\" style=\"padding: 40px;\">\n\n")
            content.append("📭 本日の記事はありません\n\n")
            content.append("</div>\n\n")
        
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
