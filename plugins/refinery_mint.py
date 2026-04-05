import os
import json
from datetime import datetime

class RefineryMint:
    """
    数据精炼厂 (Refinery Mint)。
    将 logs/human_feedback.json 及对撞对，映射为 standard .jsonl 格式供 Fine-tuning 使用。
    具备【隐私指纹擦除 (Fingerprint Erase)】安全性。
    """
    def __init__(self):
         # 用绝对路径防止相对路径漂移
         self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
         self.feedback_path = os.path.join(self.project_root, "logs", "human_feedback.json")
         self.export_dir = os.path.join(self.project_root, "data", "refinery_export")

    def erase_fingerprint(self, text: str) -> str:
        """
        擦除可能暴露指挥官身份或物理环境的指纹元数据。
        """
        if not text: return ""
        # 移除绝对路径等调试残留
        bad_words = ["C:\\", "E:\\", "User\\", "Project_Antigravity", "127.0.0.1"]
        for w in bad_words:
             text = text.replace(w, "[REDACTED]")
        return text

    def convert_feedback_to_dpo(self, filename: str = "dpo_train_pairs.jsonl"):
        """
        提纯人类反馈日志，生成 DPO (Direct Preference Optimization) .jsonl 数据包。
        格式: {"prompt": "...", "chosen": "...", "rejected": "..."}
        """
        print(f"🛠️ [Refinery] 正在泵入并发反馈日志: {self.feedback_path}")
        if not os.path.exists(self.feedback_path):
             print("⚠️ [Refinery] 暂无人类反馈数据，跳过转换。")
             return

        with open(self.feedback_path, 'r', encoding='utf-8') as f:
             feedback_data = json.load(f)

        os.makedirs(self.export_dir, exist_ok=True)
        out_path = os.path.join(self.export_dir, filename)

        count = 0
        with open(out_path, 'w', encoding='utf-8') as out_f:
             for item in feedback_data:
                  score = item.get("score", 0)
                  comment = item.get("comment", "")
                  
                  # 假设 8分以上为 Chosen, 以下为 Rejected (仿真模拟样例)
                  prompt = self.erase_fingerprint(comment.replace("从面板反馈，提问：", ""))
                  if score >= 8:
                       chosen = "RAG 辅佐后的答案: 江恩时间周期 spring node 是最佳阻力位。"
                       rejected = "纯云端盲猜: 江恩时间周期是偏门理论。"
                  else:
                       chosen = "本地隔离警告: 触发敏感熔断。"
                       rejected = "泄漏回答。"

                  dpo_pair = {
                      "prompt": prompt or "关于江恩或缠论的市场周期测算",
                      "chosen": chosen,
                      "rejected": rejected
                  }
                  out_f.write(json.dumps(dpo_pair, ensure_ascii=False) + "\n")
                  count += 1

        print(f"🚀 [Refinery] 数据金块脱敏铸造完毕 ({count} 份)，已打包导出 => {out_path}")

if __name__ == "__main__":
    ref = RefineryMint()
    ref.convert_feedback_to_dpo()
