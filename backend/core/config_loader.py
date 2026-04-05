import os
import json
from typing import Dict, Any

class ConfigLoader:
    """
    配置加载器 (免依赖 JSON 版本)。
    用于从 configs/settings.json 读取本地/云端开关状态及 API Keys。
    确保系统在 Laptop 环境下能正确 Mock 运行，或在 P100 架构下调度资源。
    """
    def __init__(self, config_path: str = None):
        if config_path is None:
            # 默认路径：向上两级到 configs/ 目录
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.config_path = os.path.abspath(os.path.join(current_dir, '..', '..', 'configs', 'settings.json'))
        else:
            self.config_path = config_path

    def load_config(self) -> Dict[str, Any]:
        """
        加载 json 配置文件。
        """
        if not os.path.exists(self.config_path):
            print(f"⚠️ Warning: Config file not found at {self.config_path}")
            return self._get_default_config()

        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config if config else self._get_default_config()
        except Exception as e:
            print(f"❌ Error loading config: {e}")
            return self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """
        返回默认安全配置（强制隐私模式和 Laptop 环境）。
        """
        return {
            "privacy_mode": True,
            "local_gpu_available": False,
            "current_environment": "Laptop_Fallback",
            "vram_gb_mock": 0,
            "tokens": {}
        }

if __name__ == "__main__":
    # 高层级单独测试
    loader = ConfigLoader()
    config = loader.load_config()
    print("--- Loaded Configuration ---")
    for k, v in config.items():
        print(f"{k}: {v}")
