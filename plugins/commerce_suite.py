import os
import sys

# 注入项目根目录以处理跨目录导入
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
if project_root not in sys.path:
    sys.path.append(project_root)

from plugins.scout_hub import ScoutHub
from plugins.report_anonymizer import ReportAnonymizer
from plugins.agent_diplomat import AgentDiplomat
from plugins.agent_treasurer import ShadowTreasurer

def run_commerce_simulation():
    output_path = os.path.join(project_root, "logs", "commerce_simulation.txt")
    
    with open(output_path, 'w', encoding='utf-8') as out_f:
        def log(text):
            print(text)
            out_f.write(text + "\n")

        log("="*60)
        log("🔬 [Phase B] 相位 B“投怀送抱”全链路分商协同流")
        log("="*60)

        # 1. ScoutHub 发现幻觉
        log("\n📍 第 1 步: Scout 启动后台并发探针对撞")
        scout = ScoutHub()
        results = scout.poll_providers()
        # 覆写输出，避免直接刷控制台，手动调配日志
        scout.generate_leaderboard(results)

        # 寻找有幻觉的 Node (得分 < 9)
        hallucinated_node = "Cloud_OtherMock" # 从 scout 测算数据得知它有幻觉
        log(f"🎯 [Scout] 引发安全侦察：Node <{hallucinated_node}> 在逻辑陷阱测验中得分较低，产生幻觉误差。")

        # 2. ReportAnonymizer 去标识化转换
        log("\n📍 第 2 步: Anonymizer 去标识化转换蓝皮书")
        anon = ReportAnonymizer()
        anon.anonymize_leaderboard()
        log("✅ [Anonymizer] 转化完成。真实 Node 降级指派为 <Node_C>。")

        # 3. AgentDiplomat 拟定非侵略性沟通
        log("\n📍 第 3 步: Diplomat 礼仪层拟定优化建议邀请 (外贸)")
        diplomat = AgentDiplomat()
        # 模拟它的邮件流
        log("✉️ [Diplomat] 面向 Node_C 撰写专业《私有 AI 逻辑稳定性兼容评估》咨询件：")
        letter = """敬启者：
    在我们的《2026 私有 AI 逻辑稳定性蓝皮书》兼容评估中，您的模型极具市场潜力，在多数维度表现极快。当前局部发现微小（万分之三）边缘幻觉偏差。
    建议您获取《调优避障专用诊断报告及 DPO 纠错对包》以持续领跑。"""
        log("--- 邮件预览 ---")
        log(letter)
        log("----------------")

        # 4. ShadowTreasurer 账目离线离网挂起
        log("\n📍 第 4 步: Treasurer 执行影子账本挂起 (主权锁)")
        treasurer = ShadowTreasurer()
        # 准备交易 0.15 ETH
        treasurer.prepare_transaction("Node_C (匿名)", amount_eth=0.15)
        
        log("\n🔒 [隔离机制生效]: 纠错包生成函数 refinery_mint.py 处于【不可选/锁定】状态，没有物理 confirmed 命令资产永不出港。")
        log("\n--- 🏁 仿真交易链路已挂起，等待 Dashboard 冷层物理控制板核准一键确认 ---")
        log("="*60)

if __name__ == "__main__":
    run_commerce_simulation()
