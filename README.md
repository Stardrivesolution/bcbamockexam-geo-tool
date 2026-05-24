# GEO Internal Tool

公司自用 GEO 分析、内容生成和 AI 可见度监测工具。

当前第一步只实现一件事：

```text
输入 URL -> 抓取页面 -> 提取结构化页面数据
```

这一步是后续 GEO 评分、内容缺口分析、内容生成和 AI Visibility 监测的基础。

## 目录结构

```text
app/
  api/routes/      FastAPI 接口
  core/            配置、日志等基础设施
  schemas/         Pydantic 输入输出结构
  services/        抓取、解析、分析等业务逻辑
  utils/           URL 等通用工具
```

## 本地启动

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

健康检查：

```bash
curl http://127.0.0.1:8000/api/v1/health
```

页面分析：

```bash
curl -X POST http://127.0.0.1:8000/api/v1/analyze/page \
  -H "Content-Type: application/json" \
  -d '{"url":"https://example.com","target_keyword":"示例关键词"}'
```
