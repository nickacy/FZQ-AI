# FZQ-AI CHANGELOG

## V15.0.0 (2026-06-27) — Entry Layer Upgrade / 入口层升级

### 新增 / Added
- **V15 智能入口端**：`web_app.py` + `intent_engine.py` + `task_router.py`
- **主题系统**：`theme.py`（Bloomberg Terminal 暗色设计系统）
- **双语 i18n**：`i18n.py`（支持 zh/en 切换）
- **4 个中文情报 Pipeline**：`zh_policy_brief`, `zh_risk_scan`, `zh_opinion_landscape`, `zh_multisource_merge`
- **API 端点**：`/api/zh/*` 四大中文情报任务端点
- **统一入口**：`main.py` 支持 `api` / `web` 双模式启动
- **审计报告**：`docs/GLM52_AUDIT_REPORT.md`（本审计报告）

### 修复 / Fixed
- CORS 安全：`allow_origins=["*"]` → 环境变量白名单
- 配置管理：`config/__init__.py` YAML 解析 bug（`json.load` → `yaml.safe_load`）
- 依赖同步：`requirements.txt` + `setup.py` 完全同步
- 异步架构：`news_intel_engine.py` / `narrative_engine.py` 移除 `asyncio.run()` 反模式
- 废弃代码：删除 `real/` 目录、重复 FastAPI 应用、死代码文件
- 时间戳：`datetime.utcnow()` → `datetime.now(timezone.utc)`（Python 3.12 兼容）
- 安全：`.env` 真实 API 密钥清理为占位符

### 已知问题 / Known Issues
- 入口端版本混乱：`main.py` 已支持 `web_app.py`，但 `ui_app.py` 仍被部分引用
- i18n 覆盖不足：仅 15 个文本，需扩展至 100+
- 归档机制：刚建立 CHANGELOG，历史版本未完全回溯

---

## V14.0.0 (2026-06-20) — Core Layer Mature / 核心层成熟

### 完成 / Completed
- **多模型路由**：6 个 Provider（DeepSeek, OpenAI, Gemini, GLM, Kimi, Qwen）+ Router + ModelSelector
- **Orchestrator 成熟**：TaskOrchestrator（自然语言 → Pipeline → Agent → Model 全链路）+ Recovery Trace
- **Pipelines 体系化**：BasePipeline Protocol + PipelineRegistry + 8 个 Pipeline
- **Agents 角色化**：BaseAgent + AgentContext + 10 个角色 + AgentHub
- **Schemas 完整**：PipelineOutputSchema + 20+ 数据模型 + SchemaValidator
- **Metrics + Logging**：TokenMonitor + MetricsStore + LLMLogger（trace_id + duration_ms）
- **V2 框架**：80% 完成

---

## V13.0.0 (Earlier) — Infrastructure / 基础设施

### 完成 / Completed
- Provider Registry 体系
- Prompt 模板系统
- 翻译管理器
- 事件聚类
- 去噪与评分

---

## V10.0.0 (Earlier) — Prototype / 原型

### 完成 / Completed
- Streamlit UI 初版（`ui_app.py`）
- 基础 API 端点（`api_server.py`）
- 简单新闻抓取
- 基础配置管理

---

*架构演进：V10 (Prototype) → V13 (Infrastructure) → V14 (Core Mature) → V15 (Entry Layer Upgrade)*
