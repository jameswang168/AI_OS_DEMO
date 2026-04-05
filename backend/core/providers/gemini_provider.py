import urllib.request
import json
from typing import List

# 处理相对导出兼容性
try:
    from .base import BaseEmbeddingProvider
except ImportError:
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from base import BaseEmbeddingProvider

class GeminiProvider(BaseEmbeddingProvider):
    """
    Gemini 官方云端 API 向量生成（免依赖 urllib 版本）。
    """
    def __init__(self, api_key: str):
        self.api_key = api_key
        # 默认使用 text-embedding-004
        self.url = f"https://generativelanguage.googleapis.com/v1beta/models/text-embedding-004:embedContent?key={self.api_key}"

    def embed_text(self, text: str) -> List[float]:
        if not self.api_key or "YOUR" in self.api_key:
             print("⚠️ Warning: Gemini API Key 处于占位符状态，跳过真实请求返回空向量。")
             return []

        payload = {
            "content": {
                "parts": [{"text": text}]
            }
        }
        data = json.dumps(payload).encode('utf-8')

        req = urllib.request.Request(
            self.url, 
            data=data,
            headers={'Content-Type': 'application/json'},
            method='POST'
        )

        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                res_body = response.read().decode('utf-8')
                res_json = json.loads(res_body)
                
                # 兼容 Gemini 官方返回结构
                embedding = res_json.get("embedding", {})
                return embedding.get("values", [])
        except Exception as e:
            print(f"❌ Gemini API 调用失败: {e}")
            return []
