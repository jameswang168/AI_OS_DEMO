import threading
import time
import urllib.request
import json
import os
import sys

# 导入 app.py
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from backend.app import run_server

def test_api(log):
    log("--- 🔬 开始端点验证 ---")
    time.sleep(3) # 给线程启动时间
    try:
        url = "http://localhost:8000/api/status"
        with urllib.request.urlopen(url, timeout=5) as response:
             log(f"✅ API 回应成功: {response.read().decode('utf-8')}")
             return True
    except Exception as e:
        log(f"❌ API 连线失败: {e}")
        return False

if __name__ == "__main__":
    output_path = os.path.join(os.path.dirname(__file__), 'logs', 'run_app_verify_output.txt')
    
    with open(output_path, 'w', encoding='utf-8') as out_f:
        def log(text):
            print(text)
            out_f.write(text + "\n")

        log("--- 🔬 启动后台线程运行 app.py ---")
        # 开启后台线程
        t = threading.Thread(target=run_server, args=(8000,), daemon=True)
        t.start()
        
        success = test_api(log)
        if success:
             log("\n🎉 全系统模拟服务器点火确认通过！")
        else:
             log("\n❌ 点火失败。")
