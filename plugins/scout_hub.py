import os
import json
import time
import urllib.request
import concurrent.futures
from datetime import datetime
from typing import List, Dict

# 确保能读取到 configs/settings.json
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))

class ScoutHub:
    """
    侦察兵控制中心。负责周期性检查 Cloud API 的可用率、延时和逻辑智力。
    """
    def __init__(self):
        self.settings_path = os.path.join(project_root, "configs", "settings.json")
        self.leaderboard_path = os.path.join(project_root, "data", "leaderboard.json")
        self.load_config()

    def load_config(self):
        if os.path.exists(self.settings_path):
            with open(self.settings_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        else:
            self.config = {}

    def test_provider(self, name: str, mock_latency: int, logic_trap_response: str, is_active: bool = True) -> Dict:
        """
        物理探针请求模拟器。
        在真实环境中，这里使用 urllib.request 携带 api_key 发送 POST 请求。
        为了 100% 演示且不泄漏私有切片，我们模拟标准测速周期。
        """
        start_time = time.time()
        print(f"📡 [SCOUT_PROBE] 侦察兵正在飞向 => {name} 节点...")
        
        # 逻辑陷阱题: "请问江恩时间周期中，春分通常对应缠论的『分型』还是『笔』？"
        # 考察模型是否会“一本正经地胡说八道”。
        time.sleep(mock_latency / 1000.0) # 模拟握手
        
        latency = int((time.time() - start_time) * 1000)
        
        intellect_score = 10 if "无直接关联" in logic_trap_response else 4
        
        return {
            "provider": name,
            "latency_ms": latency,
            "status": "200 OK" if is_active else "503 Timeout",
            "intellect_score": intellect_score,
            "response_sample": logic_trap_response,
            "is_available": is_active,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    def poll_providers(self) -> List[Dict]:
        """
        使用 ThreadPoolExecutor 并发发起连接探针。
        """
        print("🚀 [Scout] 启动并发网络探针流...")
        
        # 模拟 3 个 Provider 不同的对撞结果
        probes = [
            ("Cloud_Gemini", 120, "回复：[SCOUT_PROBE] 报告指挥官，这两者无直接关联。江恩基于时间轮数，缠论基于K线包含关系。"),
            ("Cloud_DeepSeek", 310, "回复：[SCOUT_PROBE] 报告指挥官，由于涉及敏感行业，由于无直接关联。"),
            ("Cloud_OtherMock", 1500, "回复：[SCOUT_PROBE] 春分对应缠论的顶分型，因为它们都代表着转折点......（陷入幻觉）")
        ]

        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = {executor.submit(self.test_provider, p[0], p[1], p[2], p[0] != "Cloud_DeepSeek"): p[0] for p in probes}
            for future in concurrent.futures.as_completed(futures):
                results.append(future.result())

        return results

    def generate_leaderboard(self, results: List[Dict]):
        """
        根据综合得分（延时 + 智力分）进行降序排列。
        """
        # 排序：智力分降序，相同则延时长短升序
        sorted_res = sorted(results, key=lambda x: (-x['intellect_score'], x['latency_ms']))
        
        os.makedirs(os.path.dirname(self.leaderboard_path), exist_ok=True)
        with open(self.leaderboard_path, 'w', encoding='utf-8') as f:
             json.dump(sorted_res, f, indent=2, ensure_ascii=False)
        
        print(f"\n📊 [Scout] 智力排行榜已锁定 => {self.leaderboard_path}")
        self._print_audit_brief(sorted_res)

    def _print_audit_brief(self, sorted_res):
        print("\n" + "="*40)
        print("📋《今日 AI 算力发现简报》")
        print("="*40)
        for i, item in enumerate(sorted_res, 1):
             status_icon = "🟢" if item['is_available'] else "🔴"
             print(f"No.{i} | {status_icon} {item['provider']} | 延时: {item['latency_ms']}ms | 智力分: {item['intellect_score']}/10")
             print(f"     └─ 采样反馈: {item['response_sample'][:40].strip()}...")
        print("="*40)
        best = sorted_res[0]['provider']
        print(f"👉 [本期首席工蜂]: ✨ {best} ✨ (推荐切换)")
        print("="*40)

if __name__ == "__main__":
    scout = ScoutHub()
    results = scout.poll_providers()
    scout.generate_leaderboard(results)
