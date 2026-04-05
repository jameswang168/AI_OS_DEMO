from abc import ABC, abstractmethod
from typing import List

class BaseEmbeddingProvider(ABC):
    """
    向量嵌入提供商抽象基类。
    所有具体的提供商（Gemini, Ollama 等）必须实现此类接口。
    """
    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        """
        将文本转换为浮点数向量。
        """
        pass
