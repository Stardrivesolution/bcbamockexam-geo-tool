# GEO Internal Tool

公司自用 GEO 分析、内容生成和 AI 可见度监测工具。

当前第一步只实现一件事：

```text
输入 URL -> 抓取页面 -> 提取结构化页面数据
```

现在还会把每次分析保存到 SQLite 数据库，方便后续做历史记录、GEO 评分、内容缺口分析和 AI Visibility 趋势追踪。

## 目录结构

```text
app/
  api/routes/      FastAPI 接口
  core/            配置、日志等基础设施
  schemas/         Pydantic 输入输出结构
  services/        抓取、解析、分析等业务逻辑
  db/              SQLAlchemy 数据库连接和表结构
  repositories/    数据库读写封装
  utils/           URL 等通用工具
```

## 本地启动

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
PYTHONPATH=. python scripts/init_db.py
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

查看最近分析记录：

```bash
curl http://127.0.0.1:8000/api/v1/analyze/runs
```

运行 GEO Readiness 规则评分：

```bash
curl -X POST http://127.0.0.1:8000/api/v1/geo/readiness/1
```

这里的 `1` 是 `analysis_run_id`。推荐流程是先分析页面，拿到
`analysis_run_id`，再对这次分析运行 GEO 评分。

```text
POST /api/v1/analyze/page
  -> 得到 analysis_run_id

POST /api/v1/geo/readiness/{analysis_run_id}
  -> 得到 GEO Readiness Score、维度分数、问题和建议
```

运行 GEO Gap Analysis：

```bash
curl -X POST http://127.0.0.1:8000/api/v1/geo/gap-analysis/1
```

这个接口会基于 `analysis_run_id` 生成目标用户问题池，并判断页面对每个问题是
`covered`、`partial` 还是 `missing`。

生成 GEO Markdown 报告：

```bash
curl -X POST http://127.0.0.1:8000/api/v1/reports/geo/1
```

这个接口会把页面分析、Readiness 评分和 Gap Analysis 合并成一份 Markdown 报告。
如果指定的 `analysis_run_id` 还没有 readiness 或 gap 结果，它会自动补算。

创建公司默认项目配置：

```bash
PYTHONPATH=. python scripts/seed_bcbamockexam_project.py
```

查看项目：

```bash
curl http://127.0.0.1:8000/api/v1/projects
```

## 当前数据表

```text
projects
  未来用于保存公司品牌、域名、竞品和项目配置。

pages
  保存被分析页面的 URL、标题、字数、H1 数量、noindex 等基础信息。

analysis_runs
  保存每次分析的原始结构化结果、关键词、语言、版本和 warning。

geo_readiness_assessments
  保存每次 GEO Readiness 评分结果、维度分数、问题和建议。

geo_gap_analyses
  保存每次内容缺口分析的问题覆盖结果和建议。

geo_reports
  保存生成后的 Markdown 报告。
```

为什么要有 `analysis_runs`：

```text
同一个页面会被反复优化和分析。
如果没有 run 记录，我们就无法比较优化前后差异。
后续 GEO 评分、内容生成、AI Visibility 都会挂到 run 上。
```

## 团队协作

- 竞品筛选标准见 [docs/competitor_selection.md](docs/competitor_selection.md)
- 环境变量共享规则见 [docs/team_environment.md](docs/team_environment.md)
