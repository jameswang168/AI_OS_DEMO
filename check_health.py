import os
import json
import socket
import sys

def check_health():
    output_path = os.path.join(os.path.dirname(__file__), 'logs', 'check_health_results.txt')
    
    with open(output_path, 'w', encoding='utf-8') as out_f:
        def log(text):
            print(text)
            out_f.write(text + "\n")

        log("=== 🛠️ 天予 Local AI 独立健康检查 (Check Health) ===\n")
        project_root = os.path.dirname(os.path.abspath(__file__))
        
        overall_status = True

        # 1. 检查目录结构
        log("[1] 🗂️ 目录结构检查:")
        required_dirs = ["backend", "frontend", "configs", "data/embeddings", "logs", "knowledge_base", "sim_sandbox"]
        for d in required_dirs:
             path = os.path.join(project_root, d)
             if os.path.exists(path):
                  log(f"  ✅ {d}/ 部署正确")
             else:
                  log(f"  ❌ {d}/ 缺失！")
                  overall_status = False

        # 2. 检查配置文件
        log("\n[2] ⚙️ 配置文件检查 (settings.json):")
        settings_path = os.path.join(project_root, "configs", "settings.json")
        if os.path.exists(settings_path):
             try:
                  with open(settings_path, 'r', encoding='utf-8') as f:
                       config = json.load(f)
                  log("  ✅ configs/settings.json 语法有效")
                  sensitive_words = config.get("sensitive_words", [])
                  log(f"  ✅ 隐私隔离库包含: {len(sensitive_words)} 个拦截词")
             except Exception as e:
                  log(f"  ❌ configs/settings.json 语法错误: {e}")
                  overall_status = False
        else:
             log("  ❌ configs/settings.json 缺失！")
             overall_status = False

        # 3. 检查写入权限 /data/embeddings
        log("\n[3] 💾 SSD 读写权限检查 (data/embeddings):")
        cache_dir = os.path.join(project_root, "data", "embeddings")
        test_file = os.path.join(cache_dir, "perm_test.json")
        if not os.path.exists(cache_dir):
             os.makedirs(cache_dir, exist_ok=True)
             
        try:
             with open(test_file, 'w', encoding='utf-8') as f:
                  json.dump({"test": "ok"}, f)
             os.remove(test_file)
             log("  ✅ /data/embeddings/ 读写权限正常")
        except Exception as e:
             log(f"  ❌ /data/embeddings/ 读写失败: {e}")
             overall_status = False

        # 4. 检查 Dashboard 运行端口 8000
        log("\n[4] 📡 端口探测 (Port 8000):")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', 8000))
        if result == 0:
             log("  ✅ Port 8000 当前处于激活状态 (Dashboard 正在后台运行)")
        else:
             log("  ⚠️ Port 8000 未启动。请运行 `python backend/app.py` 开启控制面板。")
        sock.close()

        log("\n=== 🏁 检查结论 ===")
        if overall_status:
             log("🎉 相位 A (移动内核一期) 健康状况：极度健壮！一键点火准备完毕。")
        else:
             log("⚠️ 相位 A 存在缺陷，请修正上面标记项。")

if __name__ == "__main__":
    check_health()
