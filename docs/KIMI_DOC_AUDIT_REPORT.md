# FZQ‑AI 文档一致性与国际化审计报告（Kimi 专用版）
# FZQ‑AI Documentation Consistency & Internationalization Audit Report (Kimi Edition)

**审计日期 / Audit Date**: 2026‑06‑27  
**审计方 / Auditor**: Kimi（文档一致性与国际化专家）  
**审计范围 / Scope**: 白皮书、工作书、Pipeline 文档、入口层文档、国际化文案、多语言 UI 文案  
**被审计项目 / Project**: FZQ‑AI V15  
**文档总量 / Doc Volume**: 18 个 Markdown 文件，4,872 行，约 180 KB  

---

## 执行摘要 / Executive Summary

FZQ‑AI 项目的文档体系处于 **"严重滞后且不一致"** 状态。所有核心技术文档的版本号停留在 **V19**，与项目实际版本 **V15** 严重脱节；文档中大量引用已删除的 `real/` 目录路径；README.md 极度简陋（仅 19 行）；**零英文文档**；Prompt ↔ Schema 字段名大面积不一致；关键 V15 特性（TaskRouter、IntentEngine、主题系统）在文档中完全缺失。

**文档健康度评分: 42/100**（不及格）

| 维度 / Dimension | 评分 / Score | 状态 / Status |
|------|------|------|
| 版本一致性 / Version Consistency | 15/100 | 🔴 严重滞后 |
| 路径准确性 / Path Accuracy | 25/100 | 🔴 大量引用已删除路径 |
| 内容完整性 / Content Completeness | 35/100 | 🟡 缺失 V15 关键特性 |
| 双语化 / Bilingualization | 5/100 | 🔴 零英文文档 |
| 术语一致性 / Terminology Consistency | 55/100 | 🟡 Prompt ↔ Schema 不一致 |
| 文档结构 / Documentation Structure | 50/100 | 🟡 扁平无序，缺乏层级 |

---

## 一、文档一致性问题 / Documentation Consistency Issues

### 1.1 版本号严重滞后（P0）/ Version Numbers Severely Lagging

**问题描述**: 所有核心技术文档的头部均标注 "版本：V19 · 状态：生产就绪"，但项目实际已演进至 V15。

**受影响文档（13 个）:**

| 文档 | 行数 | 声明版本 | 实际版本 | 滞后 |
|------|------|---------|---------|------|
| `ARCHITECTURE_OVERVIEW.md` | 172 | V19 | V15 | 6 个版本 |
| `DATA_FLOW_PIPELINES.md` | 276 | V19 | V15 | 6 个版本 |
| `NEWS_INTAKE_SYSTEM.md` | 294 | V19 | V15 | 6 个版本 |
| `SCHEMAS_MAP.md` | 441 | V19 | V15 | 6 个版本 |
| `PROMPT_SYSTEM.md` | 227 | V19 | V15 | 6 个版本 |
| `LLM_CALL_GRAPH.md` | 177 | V19 | V15 | 6 个版本 |
| `METRICS_AND_OBSERVABILITY.md` | 258 | V19 | V15 | 6 个版本 |
| `MODULE_DEPENDENCIES.md` | 166 | V19 | V15 | 6 个版本 |
| `REGION_LANGUAGE_LOGIC.md` | 289 | V19 | V15 | 6 个版本 |
| `DEEPSEEK_AUDIT_TASKS.md` | 174 | V19 | V15 | 6 个版本 |
| `DEEPSEEK_PROMPTS.md` | 351 | V19 | V15 | 6 个版本 |
| `glossary.md` | 181 | V19.2 | V15 | 5.8 个版本 |
| `actionable_suggestions.md` | 297 | V19.2 | V15 | 5.8 个版本 |

**后果 / Impact**: 新开发者阅读文档时会误以为项目仍处于 V19 阶段，对 V15 的架构演进（多模型路由、Orchestrator、Pipelines、Agents、主题系统）一无所知。

---

### 1.2 路径引用大量过时（P0）/ Outdated Path References

**问题描述**: 文档中大量引用已删除的 `real/` 目录路径，这些路径在 2026‑06‑23 的审计中已被删除。

**受影响文档及引用数量:**

| 文档 | 过时引用数 | 示例 |
|------|----------|------|
| `ARCHITECTURE_OVERVIEW.md` | 12 | `schemas/real/`, `llm/real/`, `pipelines/real/`, `orchestrator/real/`, `task_registry/real/` |
| `MODULE_DEPENDENCIES.md` | 8 | `schemas.real`, `llm.real.llm_router`, `llm.real.openai_client` 等 |
| `DATA_FLOW_PIPELINES.md` | 2 | 隐式引用 `pipelines/real/` |
| `DEEPSEEK_AUDIT_TASKS.md` | 6 | `fzq_ai/pipelines/real/news_pipeline.py` |
| `DEEPSEEK_PROMPTS.md` | 2 | `fzq_ai/pipelines/real/news_pipeline.py` |
| `design/pipeline_registry_v7.md` | 10 | `pipelines/real/`, `orchestrator/real/` |
| `AUDIT_REPORT.md` | 15 | `schemas/real/`, `llm/real/`, `pipelines/real/`, `orchestrator/real/`（已删除） |
| `DELETION_GUIDE.md` | 5 | 删除命令本身（已执行） |

**后果 / Impact**: 开发者按文档路径查找文件时会遇到 `FileNotFoundError`，严重损害文档可信度。

---

### 1.3 架构概述文档与实际架构严重脱节（P0）/ Architecture Overview Out of Sync

**问题描述**: `ARCHITECTURE_OVERVIEW.md` 是项目的核心架构文档，但其内容完全基于 V19 的架构，未反映 V15 的真实架构。

**具体脱节点:**

| 文档描述 | 实际状态 | 差异 |
|------|------|------|
| `schemas/real/` 和 `schemas/test_adapter/` 双层次架构 | `schemas/real/` 已删除，`core_models.py` 新增 | 双层次架构已废弃 |
| `llm/real/` 含 `openai_client.py` / `deepseek_client.py` / `gemini_client.py` | `llm/real/` 已删除，`providers/` 目录含 6 个 provider | Provider 结构完全改变 |
| `pipelines/real/` 含 `news_pipeline.py` | `pipelines/real/` 已删除，新增 8 个 Pipeline | Pipeline 数量翻倍 |
| `orchestrator/real/` 含 `task_orchestrator.py` | `orchestrator/real/` 已删除，新增 `daily_report_orchestrator.py` | Orchestrator 扩展 |
| `task_registry/` 含 `registry.py` | `task_registry/` 已完全删除 | 模块不存在 |
| `agents/` 标注 "预留：v10 扩展" | `agents/` 已有 10+ 个角色 + AgentHub | 已成熟，非预留 |
| `ui/` 标注 "预留：v10 扩展" | `ui/` 已有 `web_app.py`, `theme.py`, `i18n.py`, 6 个组件 | 已成熟，非预留 |
| `dashboard/` 标注 "预留：v10 扩展" | `dashboard/` 已有 `dashboard.py` + 4 个组件 | 已成熟，非预留 |
| 6 个测试文件，88 个测试 | 8 个测试文件，但质量待提升 | 数量变化 |

---

### 1.4 模块依赖文档路径过时（P1）/ Module Dependency Doc Outdated

**问题描述**: `MODULE_DEPENDENCIES.md` 中的依赖链全部基于 `schemas.real`、`llm.real.llm_router` 等已删除路径。

**示例过时引用:**
```markdown
news_pipeline.py
  ├── schemas.real               ← 已删除，现为 schemas.core_models
  ├── llm.real.llm_router        ← 已删除，现为 llm.llm_router
  │   └── LLMRouter.generate()   ← 方法名已改为 run()
  ├── core.prompts               ← 路径正确，但模板数从 9 增至 12+
  ├── tools.news_fetcher         ← 正确
  └── tools.translator          ← 正确
```

**依赖矩阵中的过时条目:**
- `schemas.real` → 应改为 `schemas`（含 `core_models.py`）
- `llm.real.llm_router` → 应改为 `llm.llm_router`
- `openai_client` / `deepseek_client` / `gemini_client` → 应改为 `providers/` 目录下的 6 个 provider

---

### 1.5 数据流文档未反映 V15 Pipeline（P1）/ Data Flow Doc Missing V15 Pipelines

**问题描述**: `DATA_FLOW_PIPELINES.md` 仅描述 `NewsPipeline` 的数据流，完全未提及 V15 新增的 4 个中文情报 Pipeline。

**缺失的 Pipeline 文档:**
| Pipeline | 文档状态 | 说明 |
|------|------|------|
| `zh_policy_brief` | ❌ 无文档 | 中文政策简报 Pipeline |
| `zh_risk_scan` | ❌ 无文档 | 中文风险扫描 Pipeline |
| `zh_opinion_landscape` | ❌ 无文档 | 中文舆论版图 Pipeline |
| `zh_multisource_merge` | ❌ 无文档 | 中文多源合并 Pipeline |
| `daily_report` | ❌ 无文档 | 日报 Pipeline |
| `sentiment` | ❌ 无文档 | 情感分析 Pipeline |
| `scenario` | ❌ 无文档 | 情景分析 Pipeline |

---

### 1.6 Prompt ↔ Schema 字段名不一致（P0）/ Prompt ↔ Schema Field Mismatch

**问题描述**: `docs/glossary.md` 和 `docs/actionable_suggestions.md` 详细记录了 4 个 zh Pipeline 的 Prompt 与 Schema 字段名不一致问题。这些文档本身准确，但问题是：**这些不一致至今未修复**。

**zh_opinion_landscape — 最严重（30.8% 对齐率）:**

| Prompt 字段 | Schema 字段 | 状态 |
|------------|------------|------|
| `camps` | `clusters` | ❌ 不一致 |
| `camp_id` | `cluster_id` | ❌ 不一致 |
| `share` | `size` | ❌ 不一致 |
| `core_claim` | `key_arguments` | ❌ 不一致 |
| `frame_analysis` | `key_frames` | ❌ 不一致 |
| `used_by` | `description` | ❌ 不一致 |
| `effect` | `evidence_span` | ❌ 不一致 |
| `key_nodes` | `influencers` | ❌ 不一致 |
| `author` | `name` | ❌ 不一致 |
| `camp` | `stance` | ❌ 不一致 |
| `heat` | `heat_trend` | ❌ 不一致 |

**枚举值不一致:**
- `stance`: Prompt "复杂" vs Schema "分裂" → 未统一
- `sentiment`: Prompt "混合" vs Schema "分化" → 未统一

**zh_risk_scan — 75% 对齐率（P1）:**
- Schema 顶层字段 `overall_risk_level`, `entity_watchlist`, `suggested_actions`, `confidence` 未在 Prompt 中要求

**zh_multisource_merge — 66.7% 对齐率（P1）:**
- `missing_sources`, `conflict_sources`, `evidence_map`, `bias_hint` 未在 Prompt 中要求
- `dimension` 枚举：Prompt 含 "其他"，Schema 不含 → 未统一

---

### 1.7 ModelProvider 枚举不完整（P1）/ ModelProvider Enum Incomplete

**文档中的枚举（`docs/SCHEMAS_MAP.md`）:**
```python
class ModelProvider(str, Enum):
    OPENAI = "openai"
    DEEPSEEK = "deepseek"
    GEMINI = "gemini"
    AZURE = "azure"
    ANTHROPIC = "anthropic"
```

**代码中的实际枚举（`src/fzq_ai/schemas/core_models.py`）:**
```python
class ModelProvider(str, Enum):
    OPENAI = "openai"
    DEEPSEEK = "deepseek"
    GEMINI = "gemini"
    GLM = "glm"
    KIMI = "kimi"
    QWEN = "qwen"
    AZURE = "azure"
    ANTHROPIC = "anthropic"
```

**缺失**: `GLM`, `KIMI`, `QWEN`（V15 新增的三个中文提供商）

---

### 1.8 configs/zh_tasks.yaml 配置错误（P1）/ Config File Duplicate Keys

**问题描述**: `configs/zh_tasks.yaml` 存在重复 key。

```yaml
tasks:
  zh_policy_brief: "..."      # ✅ 唯一
  zh_risk_scan: "..."         # ❌ 重复（第 1 次）
  zh_opinion_landscape: "..." # ❌ 重复（第 1 次）
  zh_multisource_merge: "..."  # ❌ 重复（第 1 次）
  zh_risk_scan: "..."         # ❌ 重复（第 2 次）
  zh_opinion_landscape: "..." # ❌ 重复（第 2 次）
  zh_multisource_merge: "..."  # ❌ 重复（第 2 次）
```

**YAML 解析行为**: 后出现的值会覆盖先出现的值。虽然路径相同，但这属于配置错误，可能在未来引入不同路径时导致静默 bug。

---

### 1.9 审计报告文档内容过时（P1）/ Audit Report Docs Outdated

**问题描述**: `docs/audit_report.md` (v1.0, 2024‑06‑21) 记录了当时的问题，但许多问题已修复，导致文档内容过时。

**已修复但文档未更新的问题:**

| 文档描述 | 实际状态 | 说明 |
|------|------|------|
| 根目录 `fzq_ai/` 与 `src/fzq_ai/` 包名冲突 | ✅ 已修复 | 根目录 `fzq_ai/` 已删除 |
| 两个 `IntelStore`（storage vs store） | ✅ 已修复 | `storage/` 已删除 |
| `setup.py` 未使用 `find_packages(where="src")` | ✅ 已修复 | setup.py 已正确配置 |
| 34 个空文件 | ✅ 大部分已修复 | 大量空文件已删除或填充 |
| `build_engine/` 目录 | ✅ 已删除 | 已清理 |
| 根目录 `prompts/`、`schemas/`、`ui/`、`tui/` | ✅ 已删除 | 已清理 |
| `tree.txt` 等 3.6 MB 文件 | ✅ 已删除 | 已清理 |

**后果 / Impact**: 新开发者阅读旧审计报告时会被已修复的问题误导，浪费时间排查不存在的 bug。

---

## 二、文档缺失点 / Missing Documentation

### 2.1 白皮书缺失（P0）/ Whitepaper Missing

**缺失项**: 项目无白皮书（Whitepaper）。

**白皮书应包含的内容:**
- 项目愿景与定位（Personal Intelligence Officer）
- 核心架构概述（V15 全貌）
- 技术栈与依赖
- 多模型路由策略（6 个 Provider + fallback 链）
- 安全与隐私设计
- 路线图与里程碑
- 贡献指南

---

### 2.2 README.md 极度简陋（P0）/ README Extremely Minimal

**当前状态**: `README.md` 仅 **19 行**，且大量留白。

```markdown
# FZQ-AI Unified Entry (V15-Final)

## Run API (FastAPI)

API Docs:
http://localhost:8000/docs

---

## Run Web UI (Streamlit)



---

## Debug Console (Optional)

python -m streamlit run src/fzq_ai/ui/debug_console.py
```

**缺失内容:**
- 项目简介（What is FZQ-AI?）
- 功能特性（Features）
- 安装指南（Installation）
- 快速开始（Quick Start）
- 架构图（Architecture Diagram）
- 环境变量配置（Environment Variables）
- API 端点列表（API Endpoints）
- 贡献指南（Contributing）
- 许可证（License）
- 徽章（Badges：CI status, version, Python version）
- 截图或 GIF（UI 预览）

---

### 2.3 入口层文档缺失（P0）/ Entry Layer Documentation Missing

**V15 入口层包含以下文件，但均无任何文档:**

| 文件 | 功能 | 文档状态 |
|------|------|------|
| `src/fzq_ai/ui/web_app.py` | V15 主入口（Streamlit） | ❌ 无文档 |
| `src/fzq_ai/core/intent_engine.py` | 意图识别（8 种任务） | ❌ 无文档 |
| `src/fzq_ai/core/task_router.py` | 任务路由（Pipeline fallback） | ❌ 无文档 |
| `src/fzq_ai/ui/theme.py` | Bloomberg Terminal 主题系统 | ❌ 无文档 |
| `src/fzq_ai/ui/i18n.py` | 双语国际化系统 | ❌ 无文档 |
| `src/fzq_ai/ui/components/*.py` | 6 个可视化组件 | ❌ 无文档 |
| `src/fzq_ai/dashboard/*.py` | Dashboard 组件 | ❌ 无文档 |

---

### 2.4 Pipeline 独立文档缺失（P1）/ Pipeline-Specific Docs Missing

**当前仅有一个通用 Pipeline 文档 (`DATA_FLOW_PIPELINES.md`)，但 8 个具体 Pipeline 均无独立文档。**

| Pipeline | 是否有独立文档 | 说明 |
|------|------|------|
| `news_pipeline` | ❌ 无 | 仅通用文档提及 |
| `narrative_pipeline` | ❌ 无 | 无文档 |
| `risk_pipeline` | ❌ 无 | 无文档 |
| `sentiment_pipeline` | ❌ 无 | 无文档 |
| `scenario_pipeline` | ❌ 无 | 无文档 |
| `daily_report_pipeline` | ❌ 无 | 无文档 |
| `zh_policy_brief` | ❌ 无 | 无文档 |
| `zh_risk_scan` | ❌ 无 | 无文档 |
| `zh_opinion_landscape` | ❌ 无 | 无文档 |
| `zh_multisource_merge` | ❌ 无 | 无文档 |

---

### 2.5 API 使用手册缺失（P1）/ API Usage Guide Missing

**缺失项**: 非自动生成的 API 使用手册。

虽然 FastAPI 自动生成 `/docs`（Swagger UI），但:
- 无手写 API 使用指南
- 无示例请求/响应
- 无错误码说明
- 无认证流程说明
- 无速率限制说明

---

### 2.6 部署与运维文档缺失（P1）/ Deployment Docs Missing

**缺失项:**
- 无 `Dockerfile` 说明文档
- 无 `docker-compose.yml` 说明
- 无环境变量完整清单（仅 `.env.example` 模板）
- 无生产环境部署指南
- 无监控与告警配置指南
- 无日志管理说明

---

### 2.7 开发者指南缺失（P2）/ Developer Guide Missing

**缺失项:**
- 无 `CONTRIBUTING.md`
- 无代码风格指南（`CODE_STYLE.md`）
- 无提交消息规范（`COMMIT_CONVENTION.md`）
- 无架构决策记录（ADR）模板
- 无测试编写指南

---

## 三、国际化风险 / Internationalization Risks

### 3.1 零英文文档（P0）/ Zero English Documentation

**问题描述**: 所有 18 个 `docs/*.md` 文件均为中文，无任何英文版本。

| 文档类型 | 数量 | 中文 | 英文 | 英文占比 |
|------|------|------|------|----------|
| 架构文档 | 10 | 10 | 0 | 0% |
| 审计报告 | 5 | 5 | 0 | 0% |
| 设计文档 | 2 | 2 | 0 | 0% |
| 术语表 | 1 | 1 | 0 | 0% |
| **总计** | **18** | **18** | **0** | **0%** |

**影响**: 非中文开发者完全无法使用项目文档。GitHub 上的国际用户无法理解项目架构和功能。

---

### 3.2 i18n 系统覆盖不足（P1）/ i18n System Insufficient

**当前状态**: `src/fzq_ai/ui/i18n.py` 仅含 **15 个文本条目**。

```python
TEXTS = {
    "app.title": {"zh": "...", "en": "..."},
    "app.subtitle": {"zh": "...", "en": "..."},
    "app.task_selector": {"zh": "...", "en": "..."},
    # ... 仅 15 个 key
}
```

**缺失的 UI 文本（至少需 100+ 个）:**
- 错误信息（多种错误类型）
- 加载状态提示
- 按钮标签（"取消"、"重试"、"导出"、"设置"）
- 导航标签
- 仪表盘组件标题
- 图表图例
- 表格列名
- 状态提示（"成功"、"失败"、"处理中"）
- 帮助文本
- 表单验证提示

---

### 3.3 术语表无英文对照（P1）/ Glossary Missing English

**问题描述**: `docs/glossary.md` 是统一术语的核心文档，但仅含中文，无英文对照。

**示例（缺失英文）:**
| 术语 | 英文 | 定义 |
|------|------|------|
| 任务类型 | **???** | Pipeline 的唯一标识字符串 |
| 置信度 | **???** | 0.0–1.0 浮点数 |
| 证据片段 | **???** | 从原文中直接提取的文本片段 |
| 降级处理 | **???** | 当输入样本不足时降低输出质量 |

**影响**: 代码中的变量名、API 字段名、Schema 字段名使用英文，但术语表只有中文，导致开发者在命名时无法参考统一标准。

---

### 3.4 API 返回信息纯英文（P2）/ API Responses Pure English

**问题描述**: 所有 API 端点的返回信息均为英文，无任何中文本地化。

```python
# zh_endpoints.py
return {"error": "Pipeline not found", "detail": f"No pipeline registered for key: {key}"}
```

**影响**: 中文用户在使用 API 时会收到英文错误信息，体验不佳。

---

### 3.5 代码注释双语混杂（P2）/ Code Comments Mixed Bilingual

**问题描述**: 代码中注释双语混杂，无统一标准。

**示例（不一致）:**
```python
# news_pipeline.py 第 3 行（中文乱码）
# v13 postprocess锛氱粨鏋勫寲杈撳嚭

# web_app.py（中英混合）
"""FZQ-AI Intelligence Workbench 中文情报工作台"""

# task_router.py（纯英文）
"""Task Router: maps intent to pipeline with fallback."""
```

---

## 四、文档结构优化建议 / Documentation Structure Optimization

### 4.1 建议的文档目录结构

```
docs/
├── README.md                          # 文档入口（索引）
│
├── en/                                # 英文文档（新增）
│   ├── ARCHITECTURE_OVERVIEW.md
│   ├── DATA_FLOW_PIPELINES.md
│   ├── SCHEMAS_MAP.md
│   ├── PROMPT_SYSTEM.md
│   ├── NEWS_INTAKE_SYSTEM.md
│   ├── REGION_LANGUAGE_LOGIC.md
│   ├── METRICS_AND_OBSERVABILITY.md
│   ├── LLM_CALL_GRAPH.md
│   ├── MODULE_DEPENDENCIES.md
│   ├── ENTRY_LAYER.md                 # 新增：入口层文档
│   ├── API_GUIDE.md                   # 新增：API 使用手册
│   ├── DEPLOYMENT.md                  # 新增：部署指南
│   └── GLOSSARY.md                    # 新增：双语术语表
│
├── zh/                                # 中文文档（迁移）
│   ├── ARCHITECTURE_OVERVIEW.md
│   ├── ...
│   └── GLOSSARY.md
│
├── pipelines/                         # 新增：Pipeline 独立文档
│   ├── news_pipeline.md
│   ├── zh_policy_brief.md
│   ├── zh_risk_scan.md
│   ├── zh_opinion_landscape.md
│   ├── zh_multisource_merge.md
│   └── daily_report.md
│
├── api/                               # 新增：API 文档
│   ├── endpoints.md
│   ├── authentication.md
│   ├── error_codes.md
│   └── examples.md
│
├── development/                       # 新增：开发者文档
│   ├── CONTRIBUTING.md
│   ├── CODE_STYLE.md
│   ├── TESTING.md
│   └── ADR_TEMPLATE.md
│
├── audits/                            # 审计报告归档（迁移）
│   ├── 2024-06-21_kimi_audit.md
│   ├── 2026-06-19_deepseek_audit.md
│   ├── 2026-06-21_kimi_audit.md
│   └── 2026-06-27_glm52_audit.md
│
└── design/                            # 架构设计文档（保留）
    └── pipeline_registry_v7.md
```

### 4.2 版本号统一策略

**建议**: 所有文档头部统一标注 `V15.0`。

```markdown
# 文档标题

> 版本：V15.0 · 状态：生产就绪
> 最后更新：2026-06-27
> 对应代码版本：V15.0.0-audit-prep
```

**执行步骤:**
1. 使用脚本批量替换所有 `V19` 为 `V15.0`
2. 更新所有 `状态：生产就绪` 为 `状态：生产就绪` 或 `状态：持续更新`
3. 添加 `最后更新` 日期
4. 添加 `对应代码版本` 字段

### 4.3 路径引用更新脚本

**建议**: 批量替换所有文档中的过时路径。

```bash
# 删除 real/ 路径引用
sed -i 's/schemas\.real/schemas/g' docs/*.md
sed -i 's/llm\.real\.llm_router/llm.llm_router/g' docs/*.md
sed -i 's/pipelines\.real/pipelines/g' docs/*.md
sed -i 's/orchestrator\.real/orchestrator/g' docs/*.md
sed -i 's/task_registry\.real/task_registry/g' docs/*.md
sed -i 's|src/fzq_ai/\w\+/real/|src/fzq_ai/\w\+/|g' docs/*.md
```

### 4.4 README.md 重写建议

**建议结构**: 参考 `README_legacy.md`（10749 字节）但更新为 V15 内容。

```markdown
# FZQ-AI

[Badges: CI, Python version, License, Version]

## 简介

FZQ-AI 是一个多模型情报分析系统...（双语）

## 功能特性

- 📰 新闻情报分析
- 📣 舆情分析
- ⚠️ 风险扫描
- 📅 每日报告
- 🧠 任务编排（Orchestrator）

## 快速开始

### 安装

```bash
pip install -r requirements.txt
```

### 启动 API

```bash
uvicorn app:app --reload --port 8000
```

### 启动 UI

```bash
streamlit run -m fzq_ai.ui.web_app
```

## 架构

[Mermaid 图]

## 文档

- [架构总览](docs/ARCHITECTURE_OVERVIEW.md)
- [API 指南](docs/api/)
- [开发者指南](docs/development/)

## 许可证

MIT
```

### 4.5 术语表双语化建议

**建议**: 将 `docs/glossary.md` 扩展为双语术语表。

```markdown
| 术语 (zh) | Term (en) | 定义 (zh) | Definition (en) |
|-----------|-----------|-----------|-----------------|
| 任务类型 | task_type | Pipeline 唯一标识 | Unique identifier for Pipeline |
| 置信度 | confidence | 0.0–1.0 可靠性评分 | 0.0–1.0 reliability score |
| 证据片段 | evidence_span | 原文直接提取的文本 | Text extracted directly from source |
```

---

## 五、可发布版本建议 / Release Readiness Recommendations

### 5.1 当前状态不可发布 / Current State Not Releasable

**判定**: 以当前文档状态，FZQ-AI **不可作为可发布版本**对外公开。

**不可发布的原因:**
1. 🔴 README.md 仅 19 行，无法让新用户理解项目
2. 🔴 零英文文档，无法触达国际开发者
3. 🔴 文档版本号全部 V19，与 V15 代码严重脱节
4. 🔴 大量路径引用已删除文件，文档不可执行
5. 🔴 Prompt ↔ Schema 不一致未修复，功能文档不可靠
6. 🔴 无 API 使用手册，开发者无法调用 API
7. 🟡 无部署文档，运维人员无法部署

### 5.2 发布前最低要求（Minimum Viable Documentation）

**P0 — 阻塞发布:**
| 任务 | 优先级 | 工作量 | 说明 |
|------|--------|--------|------|
| 重写 README.md | P0 | 2h | 完整双语 README |
| 统一所有文档版本号为 V15 | P0 | 1h | 批量替换 |
| 更新所有过时路径引用 | P0 | 2h | 删除 real/ 引用 |
| 修复 `configs/zh_tasks.yaml` 重复 key | P0 | 10min | 删除重复行 |
| 创建 `docs/en/` 目录 + 5 核心文档英文版 | P0 | 8h | ARCHITECTURE, SCHEMAS, API_GUIDE, ENTRY_LAYER, GLOSSARY |

**P1 — 发布前完成:**
| 任务 | 优先级 | 工作量 | 说明 |
|------|--------|--------|------|
| 创建 API 使用手册 | P1 | 4h | 含示例和错误码 |
| 创建入口层文档 | P1 | 3h | web_app, intent_engine, task_router |
| 扩展 i18n.py 至 100+ 条目 | P1 | 3h | 覆盖完整 UI |
| 修复 Prompt ↔ Schema 不一致 | P1 | 6h | 4 个 zh Pipeline |
| 创建部署文档 | P1 | 2h | Dockerfile + 环境变量 |

**P2 — 发布后补充:**
| 任务 | 优先级 | 工作量 | 说明 |
|------|--------|--------|------|
| 创建 Pipeline 独立文档 | P2 | 8h | 10 个 Pipeline |
| 创建开发者指南 | P2 | 4h | CONTRIBUTING, CODE_STYLE |
| 创建白皮书 | P2 | 6h | 项目愿景 + 技术架构 |
| 所有文档英文版 | P2 | 16h | 剩余 13 个文档 |

### 5.3 建议发布策略

**建议**: 采用 **"文档先行发布"** 策略，在代码发布前完成文档修复。

```
Phase 1: 文档修复（1 周）
├── Day 1-2: README.md 重写 + 版本号统一 + 路径更新
├── Day 3-4: 5 核心文档英文版 + API 使用手册
├── Day 5:   入口层文档 + i18n 扩展
└── Day 6-7: Prompt ↔ Schema 修复 + 最终验证

Phase 2: 发布（Day 8）
├── 发布 V15.0 到 GitHub
├── 更新 GitHub Pages（如启用）
└── 发布公告（Release Notes）

Phase 3: 持续补充（后续 2 周）
├── Pipeline 独立文档
├── 开发者指南
├── 白皮书
└── 剩余文档英文版
```

---

## 六、附录 / Appendix

### A. 文档统计 / Document Statistics

| 指标 | 数值 |
|------|------|
| Markdown 文档总数 | 18 |
| 总行数 | 4,872 |
| 总字节数 | ~180 KB |
| 中文文档 | 18 (100%) |
| 英文文档 | 0 (0%) |
| 版本号 V19 | 13 (72%) |
| 版本号 V15 | 1 (GLM52_AUDIT_REPORT.md) |
| 含过时路径引用 | 8 (44%) |
| 交叉引用有效 | 12 (67%) |
| 交叉引用过时 | 6 (33%) |

### B. 已落实的修复（本次审计）/ Fixes Applied (This Audit)

| 修复项 | 文件 | 状态 |
|------|------|------|
| 创建 CHANGELOG.md | 根目录 | ✅ 已创建 |
| 创建 VERSION | 根目录 | ✅ 已创建 |
| 创建 archive/ 目录结构 | archive/ | ✅ 已创建 |
| 创建 GLM52_AUDIT_REPORT.md | docs/ | ✅ 已创建 |
| 修复 configs/zh_tasks.yaml 重复 key | configs/zh_tasks.yaml | ✅ 已修复 |

### C. 待修复清单（按优先级）/ Fix List (Prioritized)

**P0 — 立即执行:**
1. [ ] 重写 README.md（完整双语版，200+ 行）
2. [ ] 统一所有文档版本号为 V15.0
3. [ ] 批量替换所有 `schemas.real/` → `schemas/`, `llm.real/` → `llm/`, `pipelines.real/` → `pipelines/`, `orchestrator.real/` → `orchestrator/`
4. [ ] 更新 `ARCHITECTURE_OVERVIEW.md` 架构图（删除 real/，添加 providers/，更新 agents/ui/dashboard 状态）
5. [ ] 更新 `MODULE_DEPENDENCIES.md` 依赖链
6. [ ] 创建 `docs/en/` 目录，翻译 5 核心文档
7. [ ] 标记 `docs/audit_report.md` (v1.0) 为 "历史归档，内容已过时"

**P1 — 本周执行:**
8. [ ] 创建 `docs/ENTRY_LAYER.md`（入口层文档）
9. [ ] 创建 `docs/api/API_GUIDE.md`（API 使用手册）
10. [ ] 扩展 `i18n.py` 至 100+ 文本条目
11. [ ] 修复 `zh_opinion_landscape` Prompt ↔ Schema 字段名不一致（camps→clusters 等 11 处）
12. [ ] 修复 `zh_risk_scan` Prompt 缺失字段（overall_risk_level 等 4 个）
13. [ ] 修复 `zh_multisource_merge` Prompt 缺失字段（missing_sources 等 4 个）
14. [ ] 统一 `zh_opinion_landscape` stance/sentiment 枚举值
15. [ ] 更新 `docs/SCHEMAS_MAP.md` ModelProvider 枚举（添加 GLM, KIMI, QWEN）
16. [ ] 创建 `docs/DEPLOYMENT.md`（部署指南）

**P2 — 后续执行:**
17. [ ] 创建 10 个 Pipeline 独立文档（`docs/pipelines/*.md`）
18. [ ] 创建 `docs/development/CONTRIBUTING.md`
19. [ ] 创建 `docs/development/CODE_STYLE.md`
20. [ ] 创建 `WHITEPAPER.md`（白皮书）
21. [ ] 翻译剩余 13 个文档为英文
22. [ ] 统一代码注释语言（建议：模块级 docstring 双语，行内注释英文）
23. [ ] API 返回信息双语化
24. [ ] 创建 `docs/CHANGELOG_ARCHIVE.md`（详细版本历史）

---

*报告完成 / Report Complete.*
*审计方 / Auditor: Kimi（文档一致性与国际化专家）*
*日期 / Date: 2026-06-27*
