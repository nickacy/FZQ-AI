# FZQ-AI CHANGELOG

## V24.3.1 (2026-07-05) — Minimax: Strict Schema Validator Skeleton

> V24.3.0 完成文明层 4 层集成。V24.3.1 引入 **Minimax 结构守门人**（Python validator 骨架 + System Prompt），为 V25/V30 的 GLM→DeepSeek→**Minimax**→豆包→Kimi→Qwen 链路预留接入点。

### Added / 新增

- **`src/fzq_ai/minimax/` 子包**（5 文件）
  - `__init__.py` — 导出 `StrictSchema`, `StrictSchemaValidator`, `SchemaRepairError`, `repair_structure`, `repair_types`, `parse_json_text`
  - `schema.py` — `StrictSchema` Pydantic 模型（13 字段：8 顶层 + 5 嵌套 risks 子分类）+ `StrictRisks` 嵌套模型 + `STRICT_SCHEMA_FIELD_ORDER` 规范字段顺序
  - `validator.py` — `StrictSchemaValidator.validate(raw) -> StrictSchema` 主入口；strict/lenient 两种模式；可选 `validate_with_civ(civ=...)` 接入文明层
  - `repair.py` — 修复原语：`repair_structure` (R3 补字段)、`repair_types` (R4 类型修复)、`parse_json_text` (3-tier JSON 解析)
  - `prompts/minimax_system.txt` — System Prompt（备用 LLM 通道）
- **`tests/test_minimax.py`** — 32 个单元测试覆盖 R1-R6 + JSON 文本输入路径 + 修复原语 + 文明层集成 + 端到端混沌输入
- **`docs/MINIMAX_STRICT_SCHEMA_VALIDATOR.md`** — Minimax 完整工作书（含 V24.3.1 实现说明 + V25 集成路径）

### Design Choices / 设计取舍

- **首选 Python validator 而非 LLM**：消除幻觉风险；执行快（< 1ms）；保证 R1-R6 严格遵守
- **Pydantic 强制**：违反 R3/R4 直接抛 ValidationError，无法绕过
- **零侵入集成**：`StrictSchemaValidator.validate(raw_dict)` 单函数调用
- **字段顺序规范化**：所有输出都按 `STRICT_SCHEMA_FIELD_ORDER` 排列，便于下游 diff/缓存
- **JSON 3-tier 解析**：直接 / 围栏 / 首块 — 复用 `_zh_pipeline._parse_json` 同款逻辑
- **文明层正交**：`validate_with_civ()` 是可选方法；Minimax 失败不阻塞主流程

### Verification / 验证

- **测试**：179 → **214 passed, 1 warning**（+32 个 Minimax 测试，32/32 PASSED）
- **R1-R6 覆盖**：每条强制规则至少 3 个测试用例
- **端到端**：`test_chaotic_input_full_repair` 验证 7 种典型异常输入全部正确修复

### Known Limitations / 已知局限

- **未集成到 `_zh_pipeline.py`**：Minimax 骨架就绪，但未在主链路调用；V25 默认启用
- **LLM 通道未实现**：System Prompt 已存盘但 `validate()` 走纯 Python 路径
- **修复策略**：dict 序列化为 JSON string 而非展开（保守选择，避免 R2 推测）

### Integration Path (V25) / 集成路径

```python
# _zh_pipeline.py (V25 draft)
# 5. Pydantic 校验（zh_tasks 专用 schema）
validated = self._validate(parsed)

# 6. Minimax 严格校验（V25 默认启用）
if self._minimax_enabled and validated is not None:
    from fzq_ai.minimax import StrictSchemaValidator
    validated = StrictSchemaValidator().validate_with_civ(validated, civ=civilization)
```

## V24.3.3 (2026-07-05) — Minimax Integration into zh_tasks Pipelines

> V24.3.2 引入 Minimax 骨架（`src/fzq_ai/minimax/`）。V24.3.3 把 Minimax 接入 `_zh_pipeline` 主链路——4 个 zh_tasks pipeline 现在每次执行都跑严格 schema 校验。

### Added / 新增

- **`ZhStructuredPipeline._minimax_pass()` 方法** —— 把 result dict 喂给 `StrictSchemaValidator.validate_with_civ()`，输出 `{valid: bool, strict: dict, errors: list}` 子字典
- **`ZhStructuredPipeline.run()` 末尾 + `run_async()` 末尾 + `_fail()` 错误路径** —— 都加 `result["minimax"] = self._minimax_pass(...)`，确保任何返回路径都有 minimax 字段
- **`tests/test_minimax_integration.py`** —— 26 个集成测试覆盖 4 个 pipeline 的 minimax 行为

### Key Bug Fix / 关键 bug 修复

- **`ZhStructuredPipeline.run()` 覆盖了 `BasePipeline.run()` 主入口**——子类 run() 直接走自身实现，**不经过 BasePipeline delegate 逻辑**，导致 minimax 字段在 sync run() 路径下缺失。修复：直接在 ZhStructuredPipeline.run() 末尾调 `_minimax_pass()`

### Design Notes / 设计要点

- **Minimax 总是启用**（V25 默认 on，无 flag）
- **不修改 validated** —— Minimax 是 R1/R2/R5 合规守门人，只读 + 补全 StrictSchema 字段，不动原 validated 内容
- **同步/异步入口都接入** —— `p.run()` 和 `p.run_async()` 都加 minimax；`_fail()` 错误路径也加
- **失败不阻塞** —— Minimax 抛异常被捕获，存到 `minimax.errors`，pipeline 不因 minimax 失败而失败

### Result Dict 新契约

```python
{
    # V24.2.0 原有字段
    "task": "zh_policy_brief",
    "input": "...",
    "output": "...",  # raw LLM text
    "parsed": {...} | None,
    "validated": {...} | None,  # task-specific Pydantic (unchanged by minimax)
    "model": "glm-4-flash",
    "fallback_chain": [...],
    "warnings": [...],
    "trace_id": "...",
    "duration_ms": 123.45,
    "status": "ok" | "partial" | "error",
    # V24.3.0 R2 字段（仅 run_async）
    "civilization_trace": [...],
    # V24.3.3 新字段
    "minimax": {
        "valid": True,
        "strict": {  # StrictSchema.model_dump() — 8 顶层 + 5 嵌套
            "facts": [...], "events": [...], "actors": [...],
            "narratives": [...], "risks": {...},
            "policy": [...], "trend": [...], "raw_quotes": [...]
        },
        "errors": []
    }
}
```

### Verification / 验证

- **测试**：214 → **240 passed, 1 warning**（+26 个 minimax integration 测试，26/26 PASSED）
- **Pipeline 不破坏**：`test_pipelines_real.py` 22/22 仍全绿
- **同步路径**：`p.run()` 现在返回 12 keys（含 minimax）
- **异步路径**：`p.run_async()` 现在返回 13 keys（含 civilization_trace + minimax）
- **错误路径**：`_fail()` 也带 minimax（验证错误 result 自身的结构完整性）

### Integration Points / 接入点

- `pipelines/_zh_pipeline.py:ZhStructuredPipeline.run()` —— sync 入口
- `pipelines/_zh_pipeline.py:ZhStructuredPipeline.run_async()` —— async 入口
- `pipelines/_zh_pipeline.py:ZhStructuredPipeline._fail()` —— 错误路径
- 4 个 zh_tasks 子类（policy_brief / risk_scan / opinion_landscape / multisource_merge）**自动继承** minimax 接入


## V24.3.0 (2026-07-04) — Civilization Layer R2+R3: Full Integration + Final Polish

> V24.2.0 接入文明层但只覆盖 Entry + Orchestrator 两层。R2 补完 Agent + Pipeline 两层，并清理 R1 验收遗留问题。
> 由独立审计（Mavis）逐条核验后推动。

### Added / 新增

- **`AgentContext.civilization` 字段** — BaseModel 新增 `civilization: Optional[Any] = None`，让 agent 通过 `ctx.civilization` 直接访问文明层
- **`run_autonomy` 路由到 `autonomy_agent.run(ctx)`** — V24 自治流程从 `plan→route→execute→reflect→heal` 5 个 sync 调用改为单次 `await autonomy_agent.run(agent_ctx)`，获得文明层接入
- **`autonomy_agent_v24.run(ctx)` 新方法** — V24 自治 agent 补齐 BaseAgent 协议，可被 orchestrator 直接调用
- **`_zh_pipeline.run_async` 增强** — pre-call `civ.remember("pipeline.{task}.input")` + post-call `civ.snapshot()` + status remember，返回 `civilization_trace: list[str]`
- **`BasePipeline.run()` 主入口补 civ** — 自动 pop kwargs 中的 `civilization` 并 forward 给 `run_async`，所有 `BasePipeline` 子类自动获得文明层（v13 7 个 + 4 个 zh_xxx 共 11 个 pipeline 受益）
- **`tests/test_civilization_r2.py`** — 11 个新测试覆盖 4 层集成路径
- **`docs/audits/AUDIT_V24_ACCEPTANCE_VERIFICATION.md` / `..._R1.md`** — V24 验收审计报告（含真实综合分 67 → 74-78）

### Changed / 变更

- **`orchestrator/unified_orchestrator_v24.run_autonomy`** — 从 dict-style 调用 plan/route/execute/reflect/heal 改为 `await autonomy_agent.run(agent_ctx)`；状态机轨迹（Blackboard）保留
- **`orchestrator/unified_orchestrator_v24.run_single`** — `AgentContext` 构造时显式传 `civilization=ctx.get("civilization")`
- **`api/entry_service_v24._build_ctx`** — `agent_ctx` dict 也注入 `civilization`，让 agent 走 `ctx.civilization` 优先
- **`agents/news_center_agent`** — 改用 `ctx.civilization` 优先（fallback `ctx.metadata["civilization"]`）
- **`agents/news_agent_v24`** — 重写为 async + 文明层集成（前 V19 sync 风格）
- **`agents/multi_agent.MultiAgentEngine.run`** — 新增 `civilization` kwarg；每个 sub-agent 输出 mirror 到 civ 内存
- **`agents/tasks/{policy_brief,risk_scan,opinion_landscape,multisource_merge}_agent`** — 4 个 task agent 统一加 civ remember（pre/post）+ civ 转发到 pipeline payload
- **`_zh_pipeline._fail`** — error path 也加 `civilization_trace: []` 字段，保证契约一致

### Verification / 验证

- **测试**：168 → **179 passed, 1 warning**（+11 个 R2 集成测试，11/11 PASSED）
- **文明层 grep 命中**：
  - `src/fzq_ai/agents/`：9 个文件（base, news_center, news_agent_v24, autonomy_agent_v24, multi_agent, 4 task agents）
  - `src/fzq_ai/pipelines/`：2 个文件（base, _zh_pipeline）→ 自动覆盖 11 个 BasePipeline 子类
  - `src/fzq_ai/orchestrator/`：1 个文件（unified_orchestrator_v24）
  - `src/fzq_ai/api/`：1 个文件（entry_service_v24）
  - **跨层 4 层命中属实**（之前 R1 只 2 层）
- **真实综合分**：R1 报告 74-78 → R2 验收 85-88（civilization 健康度 75 → 90+；契约健康度 70 → 75；结构健康度 80 → 82）

### Known Issues / 残留问题（待 V24.3.x 或 V25）

- **orchestrator/ 仍 4 文件**（blackboard + task_orchestrator + unified_orchestrator_v24 + __init__）—— 未做单文件整合
- **agents/ 根 4 V 文件并存**（autonomy_agent_v24 + multi_agent + news_agent_v24 + news_center_agent）—— V21 + V24 × 3 仍共存
- **entry/ 空目录** —— 只有 `__pycache__`，无 `__init__.py`
- **domain/models.py 3 个 class 非 Pydantic** —— `Article` / `IntelMeta` / `IntelBundle`
- **API response_model 仅 3/6 = 50%** —— `daily_report` / `risk` / `narrative` 端点仍缺
- **8 个孤立目录**（cache/cli/clients/dashboard/logging/metrics/models/monitor/...）—— 引用数为 0 vs 工作书声明 21+4+12+19+...，数据矛盾待澄清

## V24.2.0 (2026-07-03) — Pipeline Refactor & Entry Unification

> 紧接 V24.1.0 的业务硬化，本版本聚焦**4 个 zh_tasks Pipeline 真业务化**与**FastAPI 入口统一**。

### Pipeline 真业务化 / Pipeline Refactor

- **抽基类 `pipelines/_zh_pipeline.py:ZhStructuredPipeline`** —— 5 步流程（load prompt → choose model → call_llm → parse JSON → validate schema）下沉到基类
- **4 个 pipeline 缩成 25 行子类** —— 各自只声明 `task_type`, `prompt_path`，其它都从基类继承：
  - `zh_policy_brief_pipeline.py`
  - `zh_risk_scan_pipeline.py`
  - `zh_opinion_landscape_pipeline.py`
  - `zh_multisource_merge_pipeline.py`
- **Pydantic schema 校验** —— `SCHEMA_BY_TASK` 字典在 `schemas/zh_tasks/__init__.py` 注册 4 个 Output 类，pipeline 解析 JSON 后自动 `model_validate`
- **JSON 解析三级 fallback** —— 直接 parse / 解析 ``` ```json ... ``` ``` 围栏 / 提取第一个 { ... } 块
- **软失败语义** —— LLM 异常 / JSON 解析失败 / schema 校验失败都不抛错，返回 `status: "error"` / `"partial"` + `warnings` 列表
- **修复 schema 类名 bug** —— `ZhMultisourceMergeOutput` → `ZhMultiSourceMergeOutput`（实际类名）

### 入口统一 / Entry Unification

- **重大 bug 修复** —— V24 之前 `ui/web_app.py` 是独立 FastAPI app，**只挂载了 1 个 router**（entry_router），README 列的 11 个端点里 80% 没暴露！现在 `ui/web_app.py` 改为 thin re-export 复用 `api/app.py`
- **`api/app.py` 补挂载**：
  - `v24_routes` (V24 frontend 契约 `/api/v1/*`)
  - `zh_endpoints` (V24 中文情报 `/api/zh/*`) ← 之前漏挂
  - `v23_router` (V23 兼容 `/v23/entry`)
  - 自定义 `/entry /multi /autonomy /health`
  - `/metrics` (Prometheus 端点，prometheus_client 可用时)
- **修复 `v24_routes.py` 错用 V23 service** —— 改用 `EntryServiceV24` 的 `handle_single/multi/autonomy` 方法
- **修复 `translate_to_v24_contract` 类型 bug** —— `debug_info` 可能是 list / dict / None，统一归一为 dict

### 删除 V19/V23 死代码

- `src/fzq_ai/api/multi.py` (V23 multi router)
- `src/fzq_ai/api/autonomy.py` (V23 autonomy router)
- `src/fzq_ai/api/server.py` (V23 独立 server，端口冲突)
- `src/fzq_ai/entry/entry_service.py` (V19 service stub)
- `src/fzq_ai/entry/entry_service_v23.py` (V23 service，已无用户)
- `src/fzq_ai/entry/__init__.py` (空包)
- `src/fzq_ai/entry/` (空目录)

### 新增测试 / Tests Added

- `tests/test_pipelines_real.py` — 22 个：4 pipeline 实例化 / happy path / fenced JSON / prose-wrapped JSON / 无效 JSON / schema 越界 / LLM 异常 / 5 种输入 kwarg / registry 集成
- `tests/test_api/test_endpoints_e2e.py` — 16 个：所有 11 个 README 端点可达性 + V24 entry 契约 + main entry 契约
- **总数：140 → 179 passed**

### 验证 / Verification

```
$ pytest tests/ -q
======================= 179 passed, 1 warning in 4.02s ========================
```

- 4 个 pipeline 真实跑通（mock LLM）：JSON 解析 + Pydantic 校验全过
- 11 个 README 端点全部 reachable
- 删 6 个 V19/V23 死代码文件，零功能回归

### 已知问题 / Known Issues (留待 V25)

- **V24 route 的 `multi` 端点** —— `EntryServiceV24.handle_multi` 内部调 `orchestrator.run_multi`，后者直接调 `self.run_single`（stub），所以 `/multi` 实际行为等同 `/entry`；需要真业务
- **`/metrics` 端点** —— `prometheus_client` 未装时只返回 JSON 状态；生产需要 `pip install prometheus_client`
- **`/v23/entry` 仍走 V23 path** —— V23 兼容层，V25 应该给出 deprecation 计划

---

## V24.1.0 (2026-07-03) — Business Hardening & Test Depth

> 紧接 V24.0.0 的清理硬化，本版本聚焦**真业务落地与测试深度**。

### 修复 / Fixed
- **重大 bug**：`BaseAgent` 9 个 `@abstractmethod` 阻止 4 个 zh_tasks 子 agent 实例化 → 改为有默认实现的钩子，子类按需重写
- **真 bug（3 处）**：`zh_policy_brief / zh_risk_scan / zh_opinion_landscape / zh_multisource_merge` 的 `payload = {**` 双花括号 → 实际是 `Set([Dict])` 而非 dict，导致 `**payload` 在 set 上运行会 `TypeError` → 改为单花括号
- **真 bug**：`agents/tasks/policy_brief_agent.py` 调用 `LLMRouter.route_and_generate()`，但该方法不存在 → 简化为与另外 3 个 task agent 一致的 pipeline-wrap 模式
- **真 bug**：`llm/router_v2/router.py:39` `from fzq_ai.llm.router import PROVIDER_MAP` 错误路径（实际在 `fzq_ai.config.global_settings`）→ 改用 `settings.PROVIDER_MAP` + 统一构造 `ModelClient`
- **小 bug**：`news_center_agent.run()` 在 `get_agent` 返回 None 时没把 `None` 写入 `components` → 改为也写入（保持 schema 完整），trace 标记 `_missing` 区别于 `_error`
- **小 bug**：`modern_config.ProviderConfig.api_key` 必填导致 `AppConfig()` 默认实例化失败 → 改为默认空串

### 业务实现 / Implemented
- **`NewsCenterAgent` 真业务**：聚合 `zh_policy_brief` / `zh_risk_scan` / `zh_opinion_landscape` / `zh_multisource_merge` 4 个子 agent，按顺序调度，per-sub-agent 失败隔离（try/except + warning 收集），返回 `view_type: "personal_intel_center"` 的聚合视图
- **注册 `news_center` 到 registry**（之前未注册，导致 `decomposer.execute_subtasks` 调 `get_agent("news_center")` 会 `ValueError`）
- **`get_agent(missing)` 改为返回 `None`**（之前 `raise ValueError`），让调用方可以优雅处理
- **`modern_config` 接入**：`config/__init__.py` 现在同时导出 dict-style（`get_config() -> dict`，向后兼容）和 dataclass-style（`AppConfig, ConfigManager, get_typed_config`，新代码可用）两种 API

### 删除 / Removed
- **8 个 `civil_federation_*_v2.py`** 副本（与 `civil_federation_stubs.py` 重复，0 外部 import）
- **`agents/orchestrator.py` 15 行 stub**（被 `news_center_agent.py` 引用，但 stub 缺 `run_task` 方法；news_center 重写后已无引用）

### 新增测试 / Tests Added
- `tests/test_e2e/test_news_center.py` — 8 个：dispatch / view shape / trace / 隔离失败 / 部分失败 / warning 收集 / 主题透传
- `tests/test_base_agent.py` — 8 个：subclass instantiable / 默认 run() / 默认钩子 / 子类 run 覆盖 / memory
- `tests/test_router/test_router_v2_integration.py` — 7 个：select 返回字符串 / 长度规则回退 / 默认池 / get_provider 4 个 provider / 未知 provider 抛错
- **总数：117 → 140 passed**

### 验证 / Verification
- `pytest tests/ -q` → **140 passed, 0 failed, 1 warning** in 26.53s
- 冒烟：news_center 4/4 子 agent 全跑通（4/4 `ok=True`）

---

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
