import os
import json
from typing import Dict, Any, List

class ModeController:
    """
    状态管理与 API 网关路由器。
    - MODE_A: Local-Only (全本地模式) - 强制切断一切外部网络请求，仅使用本地索引算力。
    - MODE_B: Hybrid (混合动力模式) - 动态分流。根据切片隐私打标（Level 0 或 Level 1）精细化外流。
    """
    def __init__(self, mode: str = "A", config: Dict = None):
        self.mode = mode.upper()  # 'A' 或 'B'
        self.config = config if config else {}

    def set_mode(self, mode: str):
        """
        动态切换运行模式。
        """
        self.mode = mode.upper()
        print(f"🔄 [Router] 模式切换为: {self.mode}")

    def route_chunk(self, chunk: Dict[str, Any]) -> Dict[str, Any]:
        """
        依据当前模式和 Data 隐私等级，对切片分配计算管道。
        """
        meta = chunk.get("metadata", {})
        privacy_level = meta.get("privacy_level", 0)
        title_path = meta.get("title_path", "General")

        print(f"\n👉 [Router] 检查切片: < {title_path} >")

        # ----------------------------------------------------
        # 🔒 模式 A (Local-Only): 强制全部阻断
        # ----------------------------------------------------
        if self.mode == "A":
            print("🔒 [MODE A - 纯本地] 状态：强制隔离。不外发任何 API，交由本地 KeywordIndexer 索引计算。")
            return {
                "status": "success",
                "route": "LOCAL_INDEX",
                "mode_active": "A",
                "privacy_score": "100% Secure",
                "data_snippet": chunk["content"][:30] + "..."
            }

        # ----------------------------------------------------
        # 🌐 模式 B (Hybrid): 动态隔离 + 免费云端补足
        # ----------------------------------------------------
        elif self.mode == "B":
            if privacy_level == 1:
                print("⛔ [MODE B - 混合动力] 状态：检测到隐私级别 1 (Local_Only)。强制拦截外流，仅进入本地缓存。")
                return {
                    "status": "success",
                    "route": "LOCAL_INDEX_FORCED",
                    "mode_active": "B",
                    "privacy_score": "100% Secure (Rule Match)",
                    "data_snippet": chunk["content"][:30] + "..."
                }
            else:
                print("🌐 [MODE B - 混合动力] 状态：隐私级别 0 (Public)。允许通过云端 API 连跳测试（如 Embedding）。")
                return {
                    "status": "success",
                    "route": "CLOUD_API",
                    "mode_active": "B",
                    "privacy_score": "Normal",
                    "data_snippet": chunk["content"][:30] + "..."
                }
                
        return {"status": "error", "message": "Unknown Mode Router"}

if __name__ == "__main__":
    # 简单的本地测试
    controller = ModeController(mode="A")
    sample_chunk_private = {"content": "私钥密码是 123456。这里存放一些敏感。内容极其严密。", "metadata": {"title_path": "缠论基础 > 交易密码", "privacy_level": 1}}
    sample_chunk_public = {"content": "江恩理论中，时间是决定市场转向的主要因素。24节气和圆周分割法是核心。", "metadata": {"title_path": "江恩时间周期 > 理论详情", "privacy_level": 0}}
    
    print("--- 🔬 测试模式 A (Local-Only) ---")
    controller.route_chunk(sample_chunk_private)
    controller.route_chunk(sample_chunk_public)
    
    print("\n--- 🔬 测试模式 B (Hybrid) ---")
    controller.set_mode("B")
    controller.route_chunk(sample_chunk_private)
    controller.route_chunk(sample_chunk_public)
