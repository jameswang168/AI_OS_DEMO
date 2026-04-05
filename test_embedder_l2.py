import os
import json
from backend.core.embedder_l2 import EmbedManager, SecurityViolationError
from backend.core.providers.base import BaseEmbeddingProvider

class MockProvider(BaseEmbeddingProvider):
    """
    测试用 Mock Provider，模拟生成向量。
    """
    def embed_text(self, text: str) -> list:
        # 简单模拟生成一个固定维度的向量 [0.1, 0.2 ... 1.0]
        return [0.1 * (i+1) for i in range(10)]

def run_test():
    output_path = os.path.join(os.path.dirname(__file__), 'logs', 'test_embedder_l2_output.txt')
    
    with open(output_path, 'w', encoding='utf-8') as out_f:
        def log(text):
            print(text)
            out_f.write(text + "\n")

        log("--- 🔬 开始 L2 嵌入层三大防线测试 ---")
        
        # 初始化 Mock 计算和管理器
        mock_prov = MockProvider()
        # 显式使用本文件所在目录的 data/embeddings/ 避免 Cwd 导致不同位置引发文件读写失败
        cache_dir = os.path.join(os.path.dirname(__file__), 'data', 'embeddings')
        manager = EmbedManager(provider=mock_prov, cache_dir=cache_dir)

        # 1. 构造公共切片 (Level 0)
        public_chunk = {
            "content": "江恩时间周期是决定市场转向的核心工具。",
            "metadata": {
                "title_path": "江恩理论 > 核心时间",
                "privacy_level": 0,
                "content_hash": "mock_hash_public_123"
            }
        }

        log("\n[测试 A] 第一次处理公共切片 (预备未命中缓存):")
        try:
             # 清除旧缓存以确保“未命中”状态
             p = os.path.join(cache_dir, "mock_hash_public_123.json")
             if os.path.exists(p): os.remove(p)

             manager.embed_chunk(public_chunk)
             if os.path.exists(p):
                 log("✅ [API Call] 向量生成并高速写入 SSD 缓存。")
        except Exception as e:
             log(f"❌ 出错: {e}")

        log("\n[测试 B] 第二次处理公共切片 (预期命中古配):")
        try:
             # 预期输出 [Cache Hit] 语句
             manager.embed_chunk(public_chunk)
             log("✅ [Cache Hit] 本地持久化缓存验证通过。")
        except Exception as e:
             log(f"❌ 出错: {e}")

        # 2. 构造隐私切片 (Level 1)
        private_chunk = {
            "content": "私钥密码是 123456 的绝密策略。",
            "metadata": {
                "title_path": "缠论基础 > 私有密码",
                "privacy_level": 1,
                "content_hash": "mock_hash_private_999"
            }
        }

        log("\n[测试 C] 处理隐私切片 (预期触发 Final Gate 熔断):")
        try:
            manager.embed_chunk(private_chunk)
            log("❌ 警告：应当报错但未报错！防线 1 失效。")
        except SecurityViolationError as e:
            log(f"🛡️ 防线 1 拦截成功：触发了预期的安全熔断错误!")
            log(f"错误信息: {e}")
        except Exception as e:
             log(f"❌ 触发了非预期错误: {e}")

if __name__ == "__main__":
    run_test()
