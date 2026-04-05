import os
import json
from backend.core.filter_l1 import L1Filter

def run_test():
    filter_sys = L1Filter()
    test_file = os.path.join(os.path.dirname(__file__), 'knowledge_base', 'test_doc.md')
    output_path = os.path.join(os.path.dirname(__file__), 'logs', 'l1_test_output.json')

    print(f"Testing file: {test_file}")
    print(f"Output to: {output_path}")

    if not os.path.exists(test_file):
        print("❌ Test file index not found!")
        return

    # 1. 解析并过滤数据
    chunks = filter_sys.parse_file(test_file)
    
    # 2. 建立倒排索引
    filter_sys.build_index_for_chunks(chunks)
    filter_sys.indexer.save_index_cache()

    # 3. 将切片结果写入日志，方便查看结果
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)
    
    # 检查 embeddings 目录
    emb_path = os.path.join(os.path.dirname(__file__), 'data', 'embeddings', 'l1_index.json')
    if os.path.exists(emb_path):
        print("✅ Embeddings Index Saved.")

if __name__ == "__main__":
    run_test()
