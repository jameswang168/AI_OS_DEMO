import os
import json
from datetime import datetime

# 注入项目根目录
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))

def generate_final_assets_report():
    print("📋 [Close_Phase_B] 正在汇聚《智力资产储量报告》...")
    
    # 1. 统计 Gold_Standard 案例数 (来自导出目录)
    export_dir = os.path.join(project_root, "data", "refinery_export")
    dpo_count = 0
    if os.path.exists(export_dir):
         for f in os.listdir(export_dir):
              if f.endswith(".jsonl"):
                   with open(os.path.join(export_dir, f), 'r', encoding='utf-8') as file:
                        dpo_count += len(file.readlines())

    # 2. 统计 匿名 Node 级数 (来自 leaderboard)
    leaderboard_path = os.path.join(project_root, "data", "leaderboard.json")
    node_count = 0
    if os.path.exists(leaderboard_path):
         with open(leaderboard_path, 'r', encoding='utf-8') as f:
              node_count = len(json.load(f))

    # 3. 影子财务挂起账单
    shadow_ledger = os.path.join(project_root, "vault", "shadow_ledger.json")
    pending_eth = 0.0
    if os.path.exists(shadow_ledger):
         with open(shadow_ledger, 'r', encoding='utf-8') as f:
              ledger = json.load(f)
              for item in ledger:
                   pending_eth += item.get("amount_eth", 0.0)

    report = {
        "phase": "Phase_B_Consolidation",
        "gold_standards_count": dpo_count,
        "anonymous_node_ratings": node_count,
        "shadow_invoices_pending_eth": pending_eth,
        "pre_evaluation_value": f"{pending_eth:.2f} ETH",
        "platform_agnostic_strategy": "Stealth_Bypass Enabled",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    out_p = os.path.join(project_root, "data", "Phase_B_Final_Assets.json")
    os.makedirs(os.path.dirname(out_p), exist_ok=True)
    with open(out_p, 'w', encoding='utf-8') as f:
         json.dump(report, f, indent=2, ensure_ascii=False)
         
    print(f"📊 [Close_Phase_B] 智力资产储量报告已汇编成功 => {out_p}")

if __name__ == "__main__":
    generate_final_assets_report()
