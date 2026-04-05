# 天予 AI OS DEMO - 云端预览版

> 🌐 **云端演示地址**: [https://ai-os-demo.onrender.com/](https://ai-os-demo.onrender.com/)
> 
> 💡 **核心主权独立于硬件，插上即可点火（Plug-and-Ignite）！**
> 本系统通过全平台硬件 Bypass 旁路感知，自适应各类老旧宿主机，维持不妥协的离线隐私底色。

---

---

## 🛠️ 1. 一键启动 (Dashboard)

环境要求：`Python 3.8+` (纯原生无第三方依赖)。

1. **点火后端服务器**：
   ```powershell
   python backend/app.py
   ```
2. **可视界面访问**：
   在浏览器中打开 **[http://localhost:8000](http://localhost:8000)**。

---

## 🔒 2. 控制开关与模式解释

您可以在面板上通过 **Toggle 微动效开关** 切换以下运行逻辑：

- **模式 A (🔒 本地隔离)**：任何文档输入和切片绝不向云端外送哪怕 1KB 数据。严格执行本地 1.5B 等效逻辑断离操作。成本消费为 **$0**。
- **模式 B (🌐 混合动力)**：依据包含“缠论”、“私钥”等预定义拦截池的敏感词。拦截池内的切片留在本地保护；非隐私数据允许向云端发送杠杆指令，拉取云端 14B 大模型实现极致收益。

---

## 📊 3. 性能对账单审核 (Performance Audit)

系统运作时将会实时进行日志流沉淀：
- **离散持久化**：向量数据将沉淀于 `/data/embeddings/{hash}.json`，断电或拔出 SSD 再次插入时，系统自动识别哈希加速渲染。
- **账单查看**：可直接在 **Dashboard 右侧看板** 或 `/logs/simulation_results.txt` 查看节约美金、命中古配命中次数统计。

---

## 📅 4. 4月份升级预告 (P100 落地预留)

第一阶段（Phase-1）底层全面遵循 **Provider 抽象工厂模式**：
- 核心代码：`backend/core/embedder_l2.py`
- 预留位：`backend/core/providers/`
届时 P100 上线，只需提供 `ollama_provider.py` 并接入，系统即可毫无感知的把云端算力切换为纯本地暴力运算，实现全流程完全离线自由。
