import os
import json
from backend.api_gate.router import ModeController

def run_router_dashboard_test():
    controller = ModeController(mode="A")
    output_path = os.path.join(os.path.dirname(__file__), 'logs', 'router_test_output.json')

    # 1. 制造模拟切片
    sample_chunk_private = {
        "content": "私钥密码是 123456。这里存放一些极其敏感的交易动作设计：例如中枢买卖点。",
        "metadata": {
            "title_path": "缠论基础 > 1.2 交易策略与密码",
            "privacy_level": 1  # Local_Only
        }
    }
    
    sample_chunk_public = {
        "content": "江恩理论中，时间是决定市场转向的主要因素。时间与缠论共振提高胜率点。",
        "metadata": {
            "title_path": "江恩时间周期 > 1.1 核心理论",
            "privacy_level": 0  # Public
        }
    }

    logs = []

    def log_route(chunk):
         res = controller.route_chunk(chunk)
         logs.append({
             "mode": controller.mode,
             "title": chunk["metadata"]["title_path"],
             "privacy_level": chunk["metadata"]["privacy_level"],
             "route": res["route"],
             "privacy_score": res["privacy_score"]
         })

    print("--- 🔬 开始测试路由控制器 ---")
    
    # 2. 测试 A 模式
    print("\n--- [测试] MODE A (纯本地) ---")
    log_route(sample_chunk_private)
    log_route(sample_chunk_public)

    # 3. 测试 B 模式
    print("\n--- [测试] MODE B (混合动力) ---")
    controller.set_mode("B")
    log_route(sample_chunk_private)
    log_route(sample_chunk_public)

    # 4. 落地测试日志
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(logs, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ 路由切换测试日志已落地至: {output_path}")

if __name__ == "__main__":
    run_router_dashboard_test()
