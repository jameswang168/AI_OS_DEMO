import urllib.request
import json
import os

def test_api():
    print("--- 🔬 开始测试本地 Dashboard API 服务器 ---")
    url_status = "http://localhost:8000/api/status"
    url_simulate = "http://localhost:8000/api/simulate"

    output_path = os.path.join(os.path.dirname(__file__), 'logs', 'api_test_results.txt')

    with open(output_path, 'w', encoding='utf-8') as out_f:
        def log(text):
            print(text)
            out_f.write(text + "\n")

        # 1. 测试 GET /api/status
        try:
            with urllib.request.urlopen(url_status, timeout=5) as response:
                res_body = response.read().decode('utf-8')
                log(f"✅ GET /api/status 成功!\n响应内容: {res_body}")
        except Exception as e:
            log(f"❌ GET /api/status 失败: {e}")

        # 2. 测试 POST /api/simulate (公开问答)
        try:
            payload = {"query": "请解释江恩时间周期的主要因素是什么？"}
            data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(url_simulate, data=data, headers={'Content-Type': 'application/json'}, method='POST')

            with urllib.request.urlopen(req, timeout=10) as response:
                 res_body = response.read().decode('utf-8')
                 log(f"\n✅ POST /api/simulate [公共] 成功!\n响应内容摘要: {res_body[:200]}...")
        except Exception as e:
            log(f"❌ POST /api/simulate 失败: {e}")

if __name__ == "__main__":
    import time
    time.sleep(2) # 等待服务器启动
    test_api()
