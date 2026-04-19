#!/usr/bin/env python3
"""
ITトレンド・ウォッチャー & バイブス・コレクター
メイン実行スクリプト
"""
import sys
import logging
import os
from datetime import datetime
from pathlib import Path

# プロジェクトルートをパスに追加し、.env を他モジュールより前に読み込む
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
from dotenv import load_dotenv
load_dotenv(project_root / '.env')

from src.collectors import NikkeiCollector, TwitterCollector, TechCrunchCollector, ZennCollector, QiitaCollector
from src.processors import GeminiSummarizer
from src.writers import MarkdownWriter
from src.notifiers import notify_slack
from config.settings import OUTPUT_DIR

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
        
        # 不安定なソースは一時無効化（将来再有効化のためコードは残す）
        # nikkei_collector = NikkeiCollector()
        # twitter_collector = TwitterCollector()
        # nikkei_articles = nikkei_collector.collect()
        # twitter_tweets = twitter_collector.collect()
        nikkei_articles = []
        twitter_tweets = []
        logger.info("✓ 日経電子版: 0 件（一時無効）")
        logger.info("✓ Twitter: 0 件（一時無効）")
        
        techcrunch_collector = TechCrunchCollector()
        zenn_collector = ZennCollector()
        qiita_collector = QiitaCollector()
        techcrunch_articles = techcrunch_collector.collect()
        logger.info(f"✓ TechCrunch: {len(techcrunch_articles)} 件")
        zenn_articles = zenn_collector.collect()
        logger.info(f"✓ Zenn: {len(zenn_articles)} 件")
        qiita_articles = qiita_collector.collect()
        logger.info(f"✓ Qiita: {len(qiita_articles)} 件")
        
        # 2. 要約処理（英語コンテンツのみ）
        logger.info("\n[Step 2] 要約処理を開始...")
        
        if os.getenv('GEMINI_API_KEY'):
            logger.info("GEMINI_API_KEY が設定されています。要約を実行します。")
        else:
            logger.warning("GEMINI_API_KEY が未設定です。要約はスキップされ、要約不可として出力されます。")
        
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
        
        # TechCrunch記事（Zennは日本語のため要約対象外）
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
        summary_success = 0
        summary_fail = 0
        for item in summarized_items:
            summary_jp = item.get('summary_jp')
            item_type = item.get('type')
            index = item.get('index')
            if summary_jp:
                summary_success += 1
            else:
                summary_fail += 1
            if item_type == 'nikkei' and summary_jp:
                nikkei_articles[index]['summary_jp'] = summary_jp
            elif item_type == 'twitter' and summary_jp:
                twitter_tweets[index]['summary_jp'] = summary_jp
            elif item_type == 'techcrunch' and summary_jp:
                techcrunch_articles[index]['summary_jp'] = summary_jp
            # Zennは needs_translation=False のため要約対象外
        
        total_to_summarize = len(items_to_summarize)
        logger.info(f"要約: 成功 {summary_success} 件 / 失敗 {summary_fail} 件 / 対象 {total_to_summarize} 件")
        logger.info("✓ 要約処理が完了しました")
        
        # 3. Markdownファイル生成
        logger.info("\n[Step 3] Markdownファイルを生成...")
        
        writer = MarkdownWriter()
        today = datetime.now()
        output_path = writer.write(
            date=today,
            nikkei_articles=nikkei_articles,
            twitter_tweets=twitter_tweets,
            techcrunch_articles=techcrunch_articles,
            zenn_articles=zenn_articles,
            qiita_articles=qiita_articles,
        )
        
        logger.info(f"✓ Markdownファイルを生成しました: {output_path}")

        total_collected = len(nikkei_articles) + len(twitter_tweets) + len(techcrunch_articles) + len(zenn_articles) + len(qiita_articles)

        # 実行サマリを日次ファイルに追記（障害調査・稼働確認用）
        try:
            summary_filename = f"run_summary_{today.strftime('%Y%m%d')}.txt"
            summary_path = Path(OUTPUT_DIR) / summary_filename
            summary_path.parent.mkdir(parents=True, exist_ok=True)
            summary_line = (
                f"{today.strftime('%Y-%m-%d %H:%M:%S')}\t"
                f"nikkei={len(nikkei_articles)}\ttwitter={len(twitter_tweets)}\ttc={len(techcrunch_articles)}\tzenn={len(zenn_articles)}\tqiita={len(qiita_articles)}\t"
                f"total={total_collected}\tsummary_ok={summary_success}\tsummary_fail={summary_fail}\t"
                f"output={output_path}\n"
            )
            with open(summary_path, "a", encoding="utf-8") as f:
                f.write(summary_line)
        except Exception as e:
            logger.warning(f"実行サマリファイルの書き込みをスキップしました: {e}")
        
        # Slack 通知（Webhook URL が設定されている場合のみ）
        notify_slack(
            success=True,
            total_collected=total_collected,
            summary_ok=summary_success,
            summary_fail=summary_fail,
            output_path=str(output_path),
        )
        
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
        notify_slack(success=False, error_message=str(e))
        return 1


if __name__ == '__main__':
    sys.exit(main())
