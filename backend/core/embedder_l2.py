import os
import json
from typing import Dict, Any, List

class SecurityViolationError(Exception):
    """
    安全等级熔断错案。
    防止隐私切片意外接触任何涉及发包的网络链路。
    """
    pass

class EmbedManager:
    """
    L2 向量嵌入层中心调配器。
    统筹 L1 切片的最终隔离阀门、哈希缓存以及 Provider 的接入。
    """
    def __init__(self, provider, cache_dir: str = "data/embeddings/"):
        self.provider = provider
        # 统一使用绝对路径以防不同执行 Cwd 导致错位
        self.cache_dir = os.path.abspath(cache_dir)

    def embed_chunk(self, chunk: Dict[str, Any]) -> List[float]:
        """
        执行单个切片的向量式嵌入。
        - 防线 1: 物理拦截 privacy_level == 1
        - 防线 2: 命中 content_hash 缓存
        - 防线 3: 调度 Provider
        """
        meta = chunk.get("metadata", {})
        privacy_level = meta.get("privacy_level", 0)
        content_hash = meta.get("content_hash", "")
        content = chunk.get("content", "")

        # 🛡️ 防线 1: Final Gate (安全熔断)
        if privacy_level == 1:
            raise SecurityViolationError("🚨 绝对防线拦截：严禁将 Local_Only 的切片发往云端 API！")

        if not content_hash:
             raise ValueError("❌ 切片缺少 content_hash，无法检查持久化缓存。")

        # 🛡️ 防线 2: Persistent Caching (SSD 级哈希持久化)
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir, exist_ok=True)

        cache_path = os.path.join(self.cache_dir, f"{content_hash}.json")
        if os.path.exists(cache_path):
             print(f"✅ [Cache Hit] 命中古配 {content_hash[:16]}...json，读取本地向量。")
             return self._load_local_vector(cache_path)

        # 🛡️ 防线 3: 接口弹性适配 (调用 Provider)
        print(f"🌐 [API Call] 未命中缓存，调用 Provider 接口生成向量: < {meta.get('title_path')} >")
        vector = self.provider.embed_text(content)
        
        if vector:
             self._save_local_vector(cache_path, vector)
             print(f"💾 [Cache Save] 向量已写入 {content_hash[:16]}...json")
        return vector

    def _save_local_vector(self, path: str, vector: List[float]):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(vector, f)

    def _load_local_vector(self, path: str) -> List[float]:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
