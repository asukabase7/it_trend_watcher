"""
Slack Incoming Webhook で実行結果を通知するモジュール
"""
import logging
import sys
from pathlib import Path
from typing import Optional

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import requests

from config.settings import SLACK_WEBHOOK_URL

logger = logging.getLogger(__name__)


def notify_slack(
    success: bool,
    total_collected: int = 0,
    summary_ok: int = 0,
    summary_fail: int = 0,
    output_path: Optional[str] = None,
    error_message: Optional[str] = None,
) -> None:
    """
    実行完了時に Slack へ投稿する。
    SLACK_WEBHOOK_URL が未設定の場合は何もしない。

    Args:
        success: 処理が正常終了したか
        total_collected: 収集した総件数
        summary_ok: 要約成功件数
        summary_fail: 要約失敗件数
        output_path: 出力 Markdown ファイルパス
        error_message: 失敗時のエラーメッセージ（アラート用）
    """
    if not SLACK_WEBHOOK_URL or not SLACK_WEBHOOK_URL.strip():
        return
    try:
        if success:
            text = (
                "✅ *ITトレンド・ウォッチャー 実行完了*\n"
                f"• 収集件数: {total_collected}\n"
                f"• 要約: 成功 {summary_ok} / 失敗 {summary_fail}\n"
                f"• 出力: `{output_path or '-'}`"
            )
        else:
            text = (
                "⚠️ *ITトレンド・ウォッチャー 実行失敗*\n"
                f"• エラー: {error_message or '不明'}"
            )
        payload = {"text": text}
        resp = requests.post(SLACK_WEBHOOK_URL, json=payload, timeout=10)
        resp.raise_for_status()
        logger.info("Slack へ通知を送信しました")
    except Exception as e:
        logger.warning(f"Slack 通知の送信をスキップしました: {e}")
