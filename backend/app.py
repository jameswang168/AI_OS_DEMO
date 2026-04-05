import http.server
import json
import os
import sys
from urllib.parse import urlparse
from datetime import datetime

# 注入项目根目录以处理跨目录导入
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
if project_root not in sys.path:
    sys.path.append(project_root)

# 导入业务逻辑
from sim_sandbox.interact import SimulationManager

class DashboardAPIHandler(http.server.BaseHTTPRequestHandler):
    # 重用 SimulationManager 做全局单例
    sim = SimulationManager()

    def do_GET(self):
        # 静态网页服务
        if self.path == "/" or self.path == "/index.html":
            self._serve_static("frontend/index.html", "text/html")
        elif self.path == "/api/status":
            # 基础运行状况
            vault_path = os.path.join(project_root, "vault", "demo_ledger.json")
            ledger_count = 0
            if os.path.exists(vault_path):
                with open(vault_path, 'r', encoding='utf-8') as f:
                    ledger_count = len(json.load(f))

            self._send_json({
                "mode": self.sim.router.mode,
                "api_calls": self.sim.auditor.api_calls,
                "cache_hits": self.sim.auditor.cache_hits,
                "bytes_out": self.sim.auditor.bytes_out,
                "ledger_count": ledger_count
            })
        elif self.path == "/api/vault/status":
            # 5. 获取模拟账本 (Demo 专用) - 移至 GET 以适配前端
            vault_path = os.path.join(project_root, "vault", "demo_ledger.json")
            ledger = []
            if os.path.exists(vault_path):
                with open(vault_path, 'r', encoding='utf-8') as f:
                    ledger = json.load(f)
            self._send_json({"status": "success", "ledger": ledger})

        # --- 新增 Mock APIs 用于 Final Validation ---
        elif self.path == "/api/account":
            self._send_json({
                "node_id": "P100-CLOUD-DEMO-001",
                "owner": "jameswang168",
                "status": "ACTIVE",
                "tier": "SOVEREIGN_VIVA"
            })
        elif self.path == "/api/billing":
            self._send_json({
                "balance": 1.25,
                "saved_usd": self.sim.auditor.api_calls * 0.05,
                "utilization": "LOW",
                "next_invoice": datetime.now().strftime("%Y-%m-%d")
            })
        elif self.path == "/api/model_store":
            self._send_json({
                "available": ["Qwen-14B (Local)", "GPT-4o (Cloud Proxy)", "Llama-3 (Adapter)"],
                "active": "Mixed Mode B"
            })
        elif self.path == "/api/detail":
            self._send_json({
                "version": "1.3.0",
                "defense_layers": ["L1_Semantic", "L2_Embedding_Cache", "L3_Dynamic_Router"],
                "hardware_bypass": "ENABLED"
            })
        else:
            self.send_error(404)

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else ""
        data = json.loads(body) if body else {}

        # 1. 设置模式
        if self.path == "/api/set_mode":
            mode = data.get("mode", "A")
            self.sim.router.set_mode(mode)
            self._send_json({"status": "success", "mode": mode})

        # 2. 激发仿真博弈
        elif self.path == "/api/simulate":
            query = data.get("query", "")
            doc_path = os.path.join(project_root, "knowledge_base", "test_doc.md")
            
            # 捕获输出日志的重定向暂不全等，直接触发
            res = self.sim.run_simulation(query, document_path=doc_path)
            
            # 手动注入当前审计数据供前端刷新
            res["auditor"] = {
                "api_calls": self.sim.auditor.api_calls,
                "cache_hits": self.sim.auditor.cache_hits,
                "bytes_out": self.sim.auditor.bytes_out
            }
            self._send_json({"status": "success", "data": res})

        # 3. 提交评分
        elif self.path == "/api/score":
            score = int(data.get("score", 0))
            comment = data.get("comment", "")
            self.sim.score_result(score, comment)
            self._send_json({"status": "success"})

        # 4. 模拟金库签名 (Demo 专用)
        elif self.path == "/api/vault/sign":
            node = data.get("node", "Unknown_Node")
            amount = data.get("amount", 0.0)
            
            # 记录到 demo_ledger.json
            vault_dir = os.path.join(project_root, "vault")
            os.makedirs(vault_dir, exist_ok=True)
            vault_path = os.path.join(vault_dir, "demo_ledger.json")
            
            ledger = []
            if os.path.exists(vault_path):
                with open(vault_path, 'r', encoding='utf-8') as f:
                    ledger = json.load(f)
            
            entry = {
                "node": node,
                "amount": amount,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "status": "APPROVED (DEMO)"
            }
            ledger.append(entry)
            
            with open(vault_path, 'w', encoding='utf-8') as f:
                json.dump(ledger, f, indent=2, ensure_ascii=False)
                
            self._send_json({"status": "success", "entry": entry})

        else:
            self.send_error(404)

    def _serve_static(self, rel_path: str, content_type: str):
        path = os.path.join(project_root, rel_path)
        if os.path.exists(path):
            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.send_header('Cache-Control', 'no-cache') # 调试友好
            self.end_headers()
            with open(path, 'rb') as f:
                 self.wfile.write(f.read())

    def _send_json(self, data: dict):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*') # 允许跨域
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

def run_server(port=None):
    if port is None:
        port = int(os.environ.get("PORT", 8000))
    server_address = ('0.0.0.0', port)
    httpd = http.server.HTTPServer(server_address, DashboardAPIHandler)
    print(f"🚀 [Cloud Demo Server] 点火成功！监听端口 => {port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 服务器停止运行。")

if __name__ == "__main__":
    run_server()
