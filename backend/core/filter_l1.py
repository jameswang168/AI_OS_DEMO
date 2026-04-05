import os
import json
import hashlib
from typing import List, Dict, Any, Tuple

# 支持导入同级目录下的 config_loader
try:
    from config_loader import ConfigLoader
except ImportError:
    from backend.core.config_loader import ConfigLoader

# =====================================================================
# 🛠️ 1. Sensitive Gate (隐私拦截阀门)
# =====================================================================

def sensitive_gate(func):
    """
    敏感词拦截器装饰器。
    在处理切片数据后介入，根据 configs/settings.json 的敏感词，
    将切片元数据打上 privacy_level 标签：
    - 0: Public (公开)
    - 1: Local_Only (本地隐私)
    """
    def wrapper(self, *args, **kwargs):
        # 1. 执行原函数（例如 chunk_file 或 index_documents）
        chunks = func(self, *args, **kwargs)
        if not chunks:
            return []

        # 2. 获取 L1Filter 实例中加载的敏感词配置
        # args[0] 是装饰器外函数的 self 实例
        # 假设装饰在 L1Filter 的方法上
        sensitive_words = self.config.get("sensitive_words", ["缠论", "账户", "私钥"])

        # 3. 扫描切片内容并进行“物理打标”
        for c in chunks:
            content = c.get("content", "")
            contains_sensitive = any(word in content for word in sensitive_words)
            if contains_sensitive:
                c["metadata"]["privacy_level"] = 1  # Local_Only
            else:
                c["metadata"]["privacy_level"] = 0  # Public

        return chunks
    return wrapper


# =====================================================================
# 🛠️ 2. Markdown Chunker (语义分块器)
# =====================================================================

class MarkdownChunker:
    """
    语义分块器。
    根据 Markdown 标题级联（H1 > H2 > H3）实现层次化的语义切片。
    """
    def chunk_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        加载 Markdown 并按标题层级切片。
        """
        if not os.path.exists(file_path):
            print(f"⚠️ 文件未找到: {file_path}")
            return []

        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        chunks = []
        # 用于跟踪当前各级标题的字典 {1: 'H1内容', 2: 'H2内容'}
        current_titles = {1: "", 2: "", 3: "", 4: "", 5: "", 6: ""}
        current_content = []

        for line in lines:
            line_strip = line.strip()
            # 识别标题
            if line_strip.startswith("#"):
                # 在新标题开始前，保存当前累积的文本内容为一个 Chunk
                joined_content = "".join(current_content).strip()
                if joined_content:
                    chunks.append(self._create_chunk(joined_content, current_titles))
                    current_content = []

                # 解析标题阶级和内容
                level = 0
                for char in line_strip:
                    if char == '#': level += 1
                    else: break
                
                title_text = line_strip[level:].strip()
                current_titles[level] = title_text
                # 清除当前级别以下的所有旧标题
                for l in range(level + 1, 7):
                    current_titles[l] = ""
            else:
                 # 将正文累积进当前块
                 current_content.append(line)

        # 保存最后一组缓存内容
        joined_content = "".join(current_content).strip()
        if joined_content:
            chunks.append(self._create_chunk(joined_content, current_titles))

        return chunks

    def _create_chunk(self, content: str, titles: Dict[int, str]) -> Dict[str, Any]:
        """
        组装切片并填充元数据。
        """
        # 构建递归的 Title Path [H1 > H2 > H3]
        path_parts = [titles[l] for l in sorted(titles.keys()) if titles[l]]
        title_path = " > ".join(path_parts) if path_parts else "General"

        # 生成 Content_Hash，用于避免重复索引
        content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()

        return {
            "content": content,
            "metadata": {
                "title_path": title_path,
                "privacy_level": 0,  # 默认 0 (Public)，由 L1Filter 装饰器拦截更改
                "char_count": len(content),
                "content_hash": content_hash
            }
        }


# =====================================================================
# 🛠️ 3. Keyword Indexer (内存倒排索引)
# =====================================================================

class KeywordIndexer:
    """
    轻量级内存倒排索引。
    支持索引序列化 save/load 至 /data/embeddings/。
    """
    def __init__(self, cache_dir: str = "data/embeddings/"):
        self.index = {}  # 结构: {"keyword": [{"hash": "...", "title_path": "..."}]}
        self.cache_dir = cache_dir

    def add_chunk(self, chunk: Dict[str, Any]):
        """
        提取关键词并加入倒排索引。
        """
        content = chunk["content"]
        meta = chunk["metadata"]
        content_hash = meta["content_hash"]
        title_path = meta.get("title_path", "General")

        # 轻量级分词（纯标准库简单分割）
        # L1 属于宏观扫描，过滤高频非停用词即可
        words = set(content.lower().split())

        for word in words:
            # 过滤掉过短或低价值词汇（比如 a, an, and 仅做参考）
            if len(word) < 2: continue

            if word not in self.index:
                self.index[word] = []
            
            # 使用 content_hash 查重避免追加
            if not any(item["hash"] == content_hash for item in self.index[word]):
                self.index[word].append({
                    "hash": content_hash,
                    "title_path": title_path
                })

    def save_index_cache(self, filename: str = "l1_index.json"):
        """
        将索引序列化至 /data/embeddings/。
        """
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
        path = os.path.join(self.cache_dir, filename)
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.index, f, indent=2, ensure_ascii=False)
        print(f"✅ L1 倒排索引已安全缓存至 {path}")

    def load_index_cache(self, filename: str = "l1_index.json") -> bool:
        """
        加载本地倒排索引，实现零预热唤醒。
        """
        path = os.path.join(self.cache_dir, filename)
        if not os.path.exists(path):
             return False

        with open(path, 'r', encoding='utf-8') as f:
             self.index = json.load(f)
        print(f"✅ L1 本地索引加载成功（大小: {len(self.index)} 关键节点）")
        return True


# =====================================================================
# 🛠️ 4. L1 Filter Orchestrator (L1 调度器)
# =====================================================================

class L1Filter:
    """
    L1 宏观调度器。
    协同 Chunker 与 Indexer 运行，且具备隐私自动标签与本地缓存。
    """
    def __init__(self):
        self.chunker = MarkdownChunker()
        self.indexer = KeywordIndexer()
        
        # 从 ConfigLoader 动态读取敏感词
        loader = ConfigLoader()
        self.config = loader.load_config()

    @sensitive_gate
    def parse_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        解析单文件切分（带敏感拦截）。
        """
        chunks = self.chunker.chunk_file(file_path)
        return chunks

    def build_index_for_chunks(self, chunks: List[Dict[str, Any]]):
        """
        将拦截处理后的数据编入内存索引（或做增量检查）。
        """
        for c in chunks:
            self.indexer.add_chunk(c)

if __name__ == "__main__":
    import json
    # 创建模拟数据并自动测试
    test_file = os.path.join(os.path.dirname(__file__), '..', '..', 'knowledge_base', 'test_doc.md')
    print("📋 开始测试 L1 宏观过滤算法...")
    
    if os.path.exists(test_file):
        filter_sys = L1Filter()
        chunks = filter_sys.parse_file(test_file)
        # 建立索引并序列化缓存
        filter_sys.build_index_for_chunks(chunks)
        filter_sys.indexer.save_index_cache()

        print("\n--- 🔍 MarkdownChunker 模拟文档输出样例 (前两个切片) ---")
        print(json.dumps(chunks[:2], indent=2, ensure_ascii=False))
    else:
        print(f"⚠️ Test doc not found at {test_file}. Please create test doc to check results.")
