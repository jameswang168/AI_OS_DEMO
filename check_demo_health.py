import urllib.request
import json
import time
import sys
import subprocess
import os

def check_health():
    print("🧪 [P100 Cloud Demo] 开始健康检查...")
    
    # 模拟启动服务器 (通常自检是在服务器运行时执行的，这里我们假设它已启动或进行快速测试)
    base_url = "http://localhost:8000"
    
    try:
        # 1. 测试首页
        print("🔍 检查 Dashboard 首页...")
        with urllib.request.urlopen(f"{base_url}/", timeout=5) as response:
            if response.status == 200:
                print("✅ 首页加载成功")
            else:
                print(f"❌ 首页状态码异常: {response.status}")
                return False
        
        # 2. 测试 API 状态
        print("🔍 检查 /api/status...")
        with urllib.request.urlopen(f"{base_url}/api/status", timeout=5) as response:
            data = json.loads(response.read().decode())
            if "mode" in data:
                print(f"✅ 状态接口正常 (当前模式: {data['mode']})")
            else:
                print("❌ 状态数据结构异常")
                return False
                
        # 3. 测试仿真博弈
        print("🔍 检查 /api/simulate...")
        req = urllib.request.Request(
            f"{base_url}/api/simulate",
            data=json.dumps({"query": "测试指令"}).encode(),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            if data.get("status") == "success":
                print("✅ 仿真模拟接口正常")
            else:
                print("❌ 仿真模拟接口返回失败")
                return False

        print("\n🎉 [P100 Cloud Demo] 健康检查全部通过！")
        return True

    except Exception as e:
        print(f"❌ 健康检查失败: {e}")
        return False

if __name__ == "__main__":
    if check_health():
        sys.exit(0)
    else:
        sys.exit(1)
