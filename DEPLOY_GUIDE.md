# P100 Cloud Demo 部署指南

本项目采用 100% Python 标准库构建，零第三方依赖，极其适合在云端快速部署。以下是推荐的部署方案：

## 推荐方案：Render (最简 / 免费)

- | [Render](https://render.com/)，选择 **New +** -> **Web Service**。
- 连接您的 GitHub 仓库 `AI_OS_DEMO`。
3. **配置参数**:
    - **Name**: `ai-os-demo`
    - **Build Command**: `pip install -r requirements.txt` (虽然它是空的，但能让平台识别项目)
    - **Start Command**: `python backend/app.py`
4. **环境变量 (Environment Variables)**:
   - 添加 `PORT`: `8000` (或保持默认，Render 会自动注入)
   - 添加 `DEPLOYMENT_MODE`: `cloud_demo`
5. **部署**:
   - 点击 **Create Web Service**。等待 1-2 分钟即可获得公网 URL。

---

## 备选方案：Railway

1. 安装 [Railway CLI](https://docs.railway.app/guides/cli)。
2. 在项目根目录执行：
   ```bash
   railway login
   railway init
   railway up
   ```
3. Railway 会自动识别 `Procfile` 并启动服务。

---

## 验证部署

部署完成后，可以使用项目根目录下的 [check_demo_health.py](file:///E:/Project_Antigravity_P100/Project_Antigravity_P100_demo/check_demo_health.py) 进行验证：

```bash
# 修改脚本中的 base_url 为你的公网地址后运行
python check_demo_health.py
```

---

## 优化建议 (Tianyu OS 预留位)

- **持久化**: 目前 `vault/demo_ledger.json` 在某些云平台上（如 Render 静态磁盘）重启后会重置。若需持久化，可挂载 Disk。
- **自定义域名**: 可以在 Render/Railway 侧绑定你自己的官网子域名。
