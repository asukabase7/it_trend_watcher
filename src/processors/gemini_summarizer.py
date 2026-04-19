"""
Gemini APIを使用した要約処理モジュール（google-genai パッケージ使用）
"""
import logging
import re
import time
import sys
from pathlib import Path
from typing import Optional

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from google import genai
    from google.genai import types
except ImportError as e:
    print(
        "google-genai のインポートに失敗しました。\n"
        "以下を実行してください: pip install google-genai\n"
        "古いパッケージを使っている場合: pip uninstall google-generativeai\n"
        "その後、bash setup.sh の再実行を推奨します。",
        file=sys.stderr,
    )
    raise

from config.settings import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
    GEMINI_MAX_TOKENS,
    GEMINI_TEMPERATURE
)

logger = logging.getLogger(__name__)


class GeminiSummarizer:
    """Gemini APIを使用して英語コンテンツを日本語要約（google-genai SDK 使用）"""

    def __init__(self):
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEYが設定されていません。.envファイルを確認してください。")
        # 安定版 v1 API を使用（v1beta では一部モデルが 404 になるため）
        http_options = types.HttpOptions(api_version="v1")
        self.client = genai.Client(api_key=GEMINI_API_KEY, http_options=http_options)
        self.model_name = GEMINI_MODEL
        self.max_retries = 3
        self.retry_delay_base = 60  # 秒（Free tier: 5 RPM のため 60s ベース）
        self.between_requests_delay = 13  # 記事間の待機（Free tier 5 RPM = 12s + バッファ）

    def summarize(self, text: str, title: Optional[str] = None) -> Optional[str]:
        """
        英語テキストを3行のプロエンジニア風日本語で要約

        Args:
            text: 要約するテキスト
            title: タイトル（オプション、コンテキストとして使用）

        Returns:
            str: 要約結果（エラーの場合None）
        """
        if not text or not text.strip():
            logger.warning("要約するテキストが空です")
            return None

        context = f"タイトル: {title}\n\n" if title else ""
        prompt = f"""以下の英語のテキストを、3行のプロエンジニア風日本語で要約してください。
技術的な内容を正確に伝えつつ、簡潔で読みやすい形式にしてください。

{context}テキスト:
{text}

要約（3行のプロエンジニア風日本語）:"""

        for attempt in range(self.max_retries):
            try:
                logger.debug(f"Gemini API呼び出し中（試行 {attempt + 1}/{self.max_retries}）...")
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        max_output_tokens=GEMINI_MAX_TOKENS,
                        temperature=GEMINI_TEMPERATURE,
                    ),
                )
                if response and response.text:
                    summary = response.text.strip()
                    logger.debug("要約が正常に生成されました")
                    return summary
                reason = "空応答"
                logger.warning("Gemini APIからの応答が空でした")
                break
            except Exception as e:
                logger.error(f"Gemini API呼び出しエラー（試行 {attempt + 1}/{self.max_retries}）: {e}")
                if attempt < self.max_retries - 1:
                    # API レスポンスの retryDelay を尊重する（例: "Please retry in 59.9s"）
                    match = re.search(r"retry in (\d+(?:\.\d+)?)s", str(e), re.IGNORECASE)
                    if match:
                        delay = int(float(match.group(1))) + 3  # +3s バッファ
                    else:
                        delay = self.retry_delay_base * (2 ** attempt)
                    delay = min(delay, 180)  # 最大 3 分
                    logger.info(f"リトライまで {delay} 秒待機します")
                    time.sleep(delay)
                else:
                    logger.error("最大リトライ回数に達しました")
                    reason = "最大リトライ"
                    break
        title_preview = (title[:40] + "…") if title and len(title) > 40 else (title or "(タイトルなし)")
        logger.warning(f"要約失敗: title={title_preview} / 理由={reason}")
        return None

    def summarize_batch(self, items: list) -> list:
        """複数のアイテムをバッチで要約"""
        results = []
        success_count = 0
        fail_count = 0
        for item in items:
            text = item.get('text', item.get('content', item.get('summary', '')))
            title = item.get('title', '')
            if not text:
                logger.warning("要約対象のテキストが見つかりません")
                item['summary_jp'] = None
                fail_count += 1
                results.append(item)
                continue
            summary = self.summarize(text, title)
            item['summary_jp'] = summary
            if summary:
                success_count += 1
            else:
                fail_count += 1
            time.sleep(self.between_requests_delay)  # レート制限対策: 記事間 2 秒待機
            results.append(item)
        logger.info(f"要約バッチ完了: 成功 {success_count} 件 / 失敗 {fail_count} 件")
        return results
