# FZQ-AI CHANGELOG

## V24.0.0 (2026-07-03) — Cleanup & Hardening Pass / 清理与硬化

> 本版本聚焦**代码质量与工程卫生**硬化，未引入新功能；为 V25 业务迭代铺路。

### 修复 / Fixed
- **P0-1 严重 bug**：9 处 `from src.fzq_ai` 错误路径 → 统一为 `from fzq_ai`
  - `orchestrator/unified_orchestrator_v24.py` (7 处)
  - `agents/news_agent_v24.py` (2 处)
  - `agents/aop_blackboard.py` (1 处)
- **P0-2 严重 bug**：`UnifiedOrchestrator.run_multi` 缩进错位成 module-level 函数 → 修正为 class method
- **P0-3 安全**：`api/app.py` 与 `ui/web_app.py` 的 CORS `["*"]` + `credentials=True` 违反 spec → 改为从 `ALLOWED_ORIGINS` env 读白名单，credentials 仅在不含 `*` 时启用
- **P0-4 部署**：`frontend-react/Dockerfile` 的 `CMD ["npm", "start"]` 不存在 → 改为 multi-stage build + `npm run preview`；`package.json` 补 `start` 脚本
- **版本号混乱**：`config/__init__.py` 的 `VERSION = "19.0.0"` → 改为从 `VERSION.txt` 读取（source of truth）
- **CORS / 配置文件**：`api/app.py` 硬编码 `version="24.0.0"` → 复用 `load_version()`
- **依赖 / `.gitignore`**：增加 `*.jsonl`, `agent_checkpoints/`, `data/logs/`, `FZQ_AI_Daily_Run.xml`, `pack.ps1`, `clean_*.ps1` 等

### 清理 / Cleanup
- **合并 Blackboard**：`agents/blackboard.py` 删除，全部 import 改走 `orchestrator/blackboard.py`（3 处：`api/v24_routes.py`, `entry/entry_service_v23.py`, `agents/autonomy_agent_v23.py`）
- **删除孤立文件**：
  - `src/fzq_ai/llm/enhanced_router.py`（0 引用）
  - `ci_health_check.py`, `check_prompts.py`（孤立脚本，CI 不调用）
  - 根目录 `_test_wl.json`, `FZQ_AI_Daily_Run.xml`, `test_report.pdf`, `pack.ps1`, `clean_frontend_audit.ps1`, `clean_v17.ps1`, `Git 清理和Push Files.txt`, `project_structure_clean.txt`
- **归档开发档案**：根目录 `IMPROVEMENT_PLAN.md`, `IMPROVEMENT_SUMMARY.md`, `APPLY_CHANGES.md`, `DELETION_GUIDE.md` 移至 `docs/audits/`；`README_legacy.md` 移至 `archive/`
- **整理 `docs/`**：9 个历史审计报告（含 `audit_report.md`, `REAUDIT_REPORT_20250703.md`, `minimax_alignment_report.{md,json}` 等）移入 `docs/audits/`
- **统一架构文档**：`docs/ARCHITECTURE_OVERVIEW.md` 由 V19 中文版（含 `real/` 双层目录、`task_registry/`）同步为 V24 双语版

### 改进 / Improved
- **Prompt 路径解析**：`utils/prompt_loader.py` 由 `_SRC_DIR.parent.parent.parent` 魔法拼接改为 `importlib.resources` —— 任意工作目录、zipapp、Docker 中均可用
- **版本号来源**：单一 `VERSION.txt`，`config/__init__.py` 启动时读取，fallback `24.0.0`

### 已知问题 / Known Issues（留待 V25）
- `agents/orchestrator.py` 仍是 15 行 stub（被 `news_center_agent.py` 引用但未真正运行；安全保留）
- `llm/router_v2/` 与 `llm/router.py` 并存，待统一
- `config/modern_config.py`（dataclass 风格）未真正接入 `get_config()`，仅 `tests/test_enhanced_features.py` 使用
- `civilization/civil_federation_*_v2.py` 18 个 V2 副本无外部 import，待决断
- 测试 e2e 深度仍较薄（`test_full_pipeline.py` 31 行、`test_json_repairer.py` 12 行）

### 验证 / Verification
- `pytest tests/ -v` → **117 passed, 0 failed, 1 warning**
- `from fzq_ai.orchestrator.blackboard import Blackboard` → OK
- `from fzq_ai.agents import blackboard` → `ImportError`（已删）
- `from fzq_ai.llm import enhanced_router` → `ImportError`（已删）
- `prompt_loader("zh/zh_risk_scan.txt")` 与 legacy 路径均返回相同 4345 字节

---

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
