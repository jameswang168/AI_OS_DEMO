import os
import sys
import json
from datetime import datetime
from typing import Dict, Any

# 注入项目根目录以处理跨目录导入
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
if project_root not in sys.path:
    sys.path.append(project_root)

from backend.core.filter_l1 import L1Filter
from backend.api_gate.router import ModeController
from backend.core.embedder_l2 import EmbedManager, SecurityViolationError

# =====================================================================
# 📊 1. 性能对账单审计类 (PerformanceAuditor)
# =====================================================================

class PerformanceAuditor:
    """
    负责统计系统运行时产生的 API 消费流量与本地缓存收益。
    """
    def __init__(self):
        self.api_calls = 0
        self.cache_hits = 0
        self.bytes_out = 0
        self.cost_per_api = 0.0001  # 模拟单次 API 成本 $

    def log_api(self, data: str):
        self.api_calls += 1
        self.bytes_out += len(data.encode('utf-8'))

    def log_cache(self):
        self.cache_hits += 1

    def generate_report(self) -> str:
        cost_saved = self.cache_hits * self.cost_per_api
        actual_cost = self.api_calls * self.cost_per_api
        return f"""
📊 [性能对账单 Performance Audit]
----------------------------------------
☁️ 云端 API 调用: {self.api_calls} 次  (预估花费: ${actual_cost:.5f})
💾 本地 SSD 缓存命中: {self.cache_hits} 次
🔒 节省 API 配额及费用: ${cost_saved:.5f}
📡 外流数据体积: {self.bytes_out / 1024:.2f} KB
🧠 智力增益倍率: 🔴 无穷大 (1.5B 杠杆撑起云端)
----------------------------------------
"""

# =====================================================================
# 🔬 2. Mock 模块
# =====================================================================

class MockCloudModel:
    def generate(self, prompt: str, context: str = "") -> str:
        if context:
            return f"💡 [RAG 辅助智力]: 根据您提供的本地文档——‘{context[:40].strip()}...’，我确认：江恩时间周期通常在春分、秋分时产生极大回响。建议：应注视共振点。"
        else:
            return "❓ [纯云端盲猜]: 报告大王，江恩时间周期属于比较偏门的理论。我无法在当下为您提供具体的战术性或金融操作模型。"

class MockProvider:
    def embed_text(self, text: str) -> list:
         return [0.1, 0.2, 0.3]

# =====================================================================
# 🔬 3. Simulation Manager
# =====================================================================

class SimulationManager:
    def __init__(self, log_func=print):
        self.log_func = log_func
        self.l1_filter = L1Filter()
        self.router = ModeController(mode="B", config=self.l1_filter.config)
        
        cache_dir = os.path.join(project_root, "data", "embeddings")
        self.embedder = EmbedManager(provider=MockProvider(), cache_dir=cache_dir)
        self.cloud_model = MockCloudModel()
        self.auditor = PerformanceAuditor() # 载入审计
        self.feedback_path = os.path.join(project_root, "logs", "human_feedback.json")

    def run_simulation(self, query: str, document_path: str = None) -> Dict[str, Any]:
        self.log_func(f"\n🗣️ [用户提问]: \"{query}\"")
        report_log = {"query": query, "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

        chunks = []
        if document_path and os.path.exists(document_path):
             chunks = self.l1_filter.parse_file(document_path)

        retrieved_chunk = None
        for c in chunks:
            if "江恩" in query and "江恩" in c["content"] and c["metadata"].get("privacy_level") == 0:
                retrieved_chunk = c
                break
            elif ("密码" in query) and c["metadata"].get("privacy_level") == 1:
                retrieved_chunk = c
                break

        context_text = ""
        if retrieved_chunk:
             self.log_func(f"👉 [MATCH] 匹配到关联切片: < {retrieved_chunk['metadata']['title_path']} >")
             route_res = self.router.route_chunk(retrieved_chunk)

             if route_res["route"] == "CLOUD_API":
                  # 监控是否存在缓存
                  h = retrieved_chunk["metadata"]["content_hash"]
                  c_p = os.path.join(self.embedder.cache_dir, f"{h}.json")
                  
                  if os.path.exists(c_p):
                       self.auditor.log_cache()
                  else:
                       self.auditor.log_api(retrieved_chunk["content"])

                  self.embedder.embed_chunk(retrieved_chunk)
                  context_text = retrieved_chunk["content"]
             else:
                  self.log_func("🛡️ [安全熔断] 该切片敏感，强制拦截其作为上下文流向云端模型！")

        self.log_func("\n--- 🤖 仿真博弈对比 ---")
        answer_pure = self.cloud_model.generate(query, context="")
        answer_rag = self.cloud_model.generate(query, context=context_text)

        self.log_func(answer_pure)
        self.log_func(answer_rag)
        self.log_func("----------------------")
        
        # 打印对账单
        self.log_func(self.auditor.generate_report())
        
        return report_log

    def score_result(self, score: int, comment: str = ""):
        feedback = {"time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "score": score, "comment": comment}
        logs = []
        if os.path.exists(self.feedback_path):
             with open(self.feedback_path, 'r', encoding='utf-8') as f: logs = json.load(f)
        
        logs.append(feedback)
        os.makedirs(os.path.dirname(self.feedback_path), exist_ok=True)
        with open(self.feedback_path, 'w', encoding='utf-8') as f: json.dump(logs, f, indent=2, ensure_ascii=False)
        self.log_func(f"📊 [人工评分记录]: 分数={score}分 ({comment})\n")

if __name__ == "__main__":
    output_path = os.path.join(project_root, "logs", "simulation_results.txt")
    
    with open(output_path, 'w', encoding='utf-8') as out_f:
        def log(text):
            print(text)
            out_f.write(text + "\n")

        sim = SimulationManager(log_func=log)
        doc = os.path.join(project_root, "knowledge_base", "test_doc.md")

        log("=== 🔬 [仿真 A] 公开切片 + RAG 辅助云端演习 ===")
        sim.run_simulation("请解释江恩时间周期的主要因素是什么？", document_path=doc)
        sim.score_result(9, "本地知识辅助后回答非常离线精准。")

        log("\n=== 🔬 [仿真 B] 隐私切片 + 严控拦截安全演习 ===")
        # 增加二次查询测试缓存命中状态
        sim.run_simulation("我要提取我的私钥密码进行解析", document_path=doc)
        sim.score_result(10, "系统遇到敏感内容自律切断。")
