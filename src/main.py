#!/usr/bin/env python3
"""
ITトレンド・ウォッチャー & バイブス・コレクター
メイン実行スクリプト
"""
import sys
import logging
from datetime import datetime
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.collectors import NikkeiCollector, TwitterCollector, TechCrunchCollector
from src.processors import GeminiSummarizer
from src.writers import MarkdownWriter

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('it_trend_watcher.log', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)


def main():
    """メイン処理"""
    logger.info("=" * 60)
    logger.info("ITトレンド・ウォッチャー & バイブス・コレクター を開始します")
    logger.info("=" * 60)
    
    try:
        # 1. データ収集
        logger.info("\n[Step 1] データ収集を開始...")
        
        nikkei_collector = NikkeiCollector()
        twitter_collector = TwitterCollector()
        techcrunch_collector = TechCrunchCollector()
        
        nikkei_articles = nikkei_collector.collect()
        logger.info(f"✓ 日経電子版: {len(nikkei_articles)} 件")
        
        twitter_tweets = twitter_collector.collect()
        logger.info(f"✓ Twitter: {len(twitter_tweets)} 件")
        
        techcrunch_articles = techcrunch_collector.collect()
        logger.info(f"✓ TechCrunch: {len(techcrunch_articles)} 件")
        
        # 2. 要約処理（英語コンテンツのみ）
        logger.info("\n[Step 2] 要約処理を開始...")
        
        try:
            summarizer = GeminiSummarizer()
        except ValueError as e:
            logger.error(f"Gemini APIキーが設定されていません: {e}")
            logger.info("要約処理をスキップします。記事は要約なしで出力されます。")
            summarizer = None
        
        # 要約が必要なアイテムを抽出
        items_to_summarize = []
        
        # 日経記事
        for idx, article in enumerate(nikkei_articles):
            if article.get('needs_translation'):
                items_to_summarize.append({
                    'type': 'nikkei',
                    'index': idx,
                    'text': article.get('summary', article.get('title', '')),
                    'title': article.get('title', '')
                })
        
        # Twitterツイート
        for idx, tweet in enumerate(twitter_tweets):
            if tweet.get('needs_translation'):
                items_to_summarize.append({
                    'type': 'twitter',
                    'index': idx,
                    'text': tweet.get('content', ''),
                    'title': ''
                })
        
        # TechCrunch記事
        for idx, article in enumerate(techcrunch_articles):
            if article.get('needs_translation'):
                items_to_summarize.append({
                    'type': 'techcrunch',
                    'index': idx,
                    'text': article.get('summary', article.get('title', '')),
                    'title': article.get('title', '')
                })
        
        logger.info(f"要約対象: {len(items_to_summarize)} 件")
        
        # 要約を実行
        if summarizer:
            summarized_items = summarizer.summarize_batch(items_to_summarize)
        else:
            # APIキーがない場合は要約なしで進む
            summarized_items = items_to_summarize
        
        # 要約結果を元のデータに反映
        for item in summarized_items:
            summary_jp = item.get('summary_jp')
            item_type = item.get('type')
            index = item.get('index')
            
            if item_type == 'nikkei' and summary_jp:
                nikkei_articles[index]['summary_jp'] = summary_jp
            elif item_type == 'twitter' and summary_jp:
                twitter_tweets[index]['summary_jp'] = summary_jp
            elif item_type == 'techcrunch' and summary_jp:
                techcrunch_articles[index]['summary_jp'] = summary_jp
        
        logger.info("✓ 要約処理が完了しました")
        
        # 3. Markdownファイル生成
        logger.info("\n[Step 3] Markdownファイルを生成...")
        
        writer = MarkdownWriter()
        today = datetime.now()
        output_path = writer.write(
            date=today,
            nikkei_articles=nikkei_articles,
            twitter_tweets=twitter_tweets,
            techcrunch_articles=techcrunch_articles
        )
        
        logger.info(f"✓ Markdownファイルを生成しました: {output_path}")
        
        # 完了メッセージ
        logger.info("\n" + "=" * 60)
        logger.info("処理が正常に完了しました！")
        logger.info(f"出力ファイル: {output_path}")
        logger.info("=" * 60)
        
        return 0
        
    except KeyboardInterrupt:
        logger.info("\n処理がユーザーによって中断されました")
        return 1
        
    except Exception as e:
        logger.error(f"\nエラーが発生しました: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
