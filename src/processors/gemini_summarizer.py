"""
Gemini APIを使用した要約処理モジュール
"""
import logging
import time
import sys
from pathlib import Path
from typing import Optional
import google.generativeai as genai

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from config.settings import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
    GEMINI_MAX_TOKENS,
    GEMINI_TEMPERATURE
)

logger = logging.getLogger(__name__)


class GeminiSummarizer:
    """Gemini APIを使用して英語コンテンツを日本語要約"""
    
    def __init__(self):
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEYが設定されていません。.envファイルを確認してください。")
        
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel(GEMINI_MODEL)
        self.max_retries = 3
        self.retry_delay = 2  # 秒
    
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
        
        # プロンプトの構築
        context = f"タイトル: {title}\n\n" if title else ""
        prompt = f"""以下の英語のテキストを、3行のプロエンジニア風日本語で要約してください。
技術的な内容を正確に伝えつつ、簡潔で読みやすい形式にしてください。

{context}テキスト:
{text}

要約（3行のプロエンジニア風日本語）:"""
        
        # リトライロジック付きでAPI呼び出し
        for attempt in range(self.max_retries):
            try:
                logger.debug(f"Gemini API呼び出し中（試行 {attempt + 1}/{self.max_retries}）...")
                
                response = self.model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=GEMINI_MAX_TOKENS,
                        temperature=GEMINI_TEMPERATURE,
                    )
                )
                
                if response and response.text:
                    summary = response.text.strip()
                    logger.debug("要約が正常に生成されました")
                    return summary
                else:
                    logger.warning("Gemini APIからの応答が空でした")
                    return None
                    
            except Exception as e:
                logger.error(f"Gemini API呼び出しエラー（試行 {attempt + 1}/{self.max_retries}）: {e}")
                
                if attempt < self.max_retries - 1:
                    # リトライ前に待機
                    time.sleep(self.retry_delay * (attempt + 1))
                else:
                    logger.error("最大リトライ回数に達しました")
                    return None
        
        return None
    
    def summarize_batch(self, items: list) -> list:
        """
        複数のアイテムをバッチで要約
        
        Args:
            items: 要約対象のアイテムリスト
                各アイテムは辞書で、'text'と'title'（オプション）を含む
        
        Returns:
            list: 要約結果を含むアイテムリスト
        """
        results = []
        
        for item in items:
            text = item.get('text', item.get('content', item.get('summary', '')))
            title = item.get('title', '')
            
            if not text:
                logger.warning("要約対象のテキストが見つかりません")
                item['summary_jp'] = None
                results.append(item)
                continue
            
            summary = self.summarize(text, title)
            item['summary_jp'] = summary
            
            # APIレート制限を考慮して少し待機
            time.sleep(0.5)
            
            results.append(item)
        
        return results
