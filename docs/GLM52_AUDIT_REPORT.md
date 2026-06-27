# FZQ‑AI 项目审计报告（GLM‑5.2 审计专用版）
# FZQ‑AI Project Audit Report (GLM‑5.2 Audit Edition)

**版本 / Version**: V15‑Audit‑Final  
**日期 / Date**: 2026‑06‑27  
**审计方 / Auditor**: GLM‑5.2  
**被审计项目 / Audited Project**: FZQ‑AI (Personal Intelligence Officer)  
**项目仓库 / Repository**: `C:\Users\nicka\FZQ-AI-WORKSPACE\FZQ-AI`  

---

## 执行摘要 / Executive Summary

FZQ‑AI 项目已完成 **V14 核心层**（大脑层）的建设，多模型路由、Orchestrator、Pipelines、Agents、Schemas、Metrics 均已成熟。然而，**入口端（Entry Layer）严重滞后于核心层**，目前仍处于 **V10 水平**，与 V14 核心层形成显著的不匹配。双语化、归档机制、App/Agent Store 准备度均存在明显缺口。

**核心结论 / Key Conclusion**: 项目当前处于 "大脑强于入口" 的不均衡状态。V15 的首要任务不是继续扩展核心能力，而是全面升级入口端，使其与核心层能力相匹配。

| 维度 / Dimension | 状态 / Status | 版本 / Version |
|------|------|------|
| 核心层 / Core Layer | 🟢 成熟 / Mature | V14 |
| 多模型路由 / Multi‑Model Routing | 🟢 成熟 / Mature | V14 |
| Pipelines / Agents | 🟢 体系化 / Structured | V14 |
| Schemas + Validators | 🟢 完整 / Complete | V14 |
| Metrics + Logging | 🟢 成熟 / Mature | V14 |
| **入口端 / Entry Layer** | 🔴 **严重滞后 / Severely Lagging** | **V10** |
| 意图识别 / Intent Recognition | 🟡 存在但未被集成 / Exists but not integrated | V15‑Draft |
| 任务路由 / Task Routing | 🟡 存在但未被集成 / Exists but not integrated | V15‑Draft |
| 智能 UI / Intelligent UI | 🔴 缺失 / Missing | — |
| 双语化 / Bilingualization | 🟡 部分 / Partial | V10 |
| 归档机制 / Archiving | 🔴 缺失 / Missing | — |
| App/Agent Store 准备 / App Readiness | 🔴 缺失 / Missing | — |

---

## 一、项目现状总览 / Project Current State Overview

### 1.1 代码规模 / Code Scale

```
Python 文件数 / Python files:     140+
Markdown 文件数 / Markdown files: 25
测试文件 / Test files:            8
Provider 实现 / Providers:          6
Pipeline 实现 / Pipelines:          8+
Agent 实现 / Agents:              10+
文档数 / Docs:                    15+ (docs/ 目录)
```

### 1.2 核心层能力评估 / Core Layer Capability Assessment

**多模型路由 (Multi‑Model Routing)** — V14 成熟
- 6 个 Provider 实现：DeepSeek, OpenAI, Gemini, GLM, Kimi, Qwen
- 统一 Router + ModelSelector（按能力 + 成功率排序）
- ProviderRegistry 集中管理
- 自动 fallback 机制

**Orchestrator (调度器)** — V14 成熟
- TaskOrchestrator：自然语言 → Pipeline → Agent → Model 全链路
- 自愈链路（Recovery Trace）
- Pipeline fallback + Model fallback + Agent fallback

**Pipelines (任务链)** — V14 体系化
- BasePipeline 抽象基类（preprocess → call_llm → postprocess → finalize）
- PipelineRegistry 注册体系
- 8 个具体 Pipeline：news, narrative, risk, sentiment, scenario, daily_report, zh_policy_brief, zh_risk_scan, zh_opinion_landscape, zh_multisource_merge

**Agents (角色智能体)** — V14 角色化
- BaseAgent 基类 + AgentContext / AgentResult
- 10 个角色：news_center, autonomy, alert, report, watchlist, policy_brief 等
- AgentHub 注册体系

**Schemas + Validators** — V14 完整
- PipelineOutputSchema 统一输出
- 20+ 个数据模型（LanguageCode, RegionCode, NewsSource, LLMRequest 等）
- SchemaValidator + SchemaRegistry + SchemaAlignmentChecker

**Metrics + Logging** — V14 成熟
- TokenMonitor（token 使用追踪 + 成本计算）
- MetricsStore（性能指标）
- LLMLogger（调用日志）
- 统一日志格式（trace_id + duration_ms）

---

## 二、五大关键问题审计 / Five Key Issues Audit

### 2.1 问题一：入口端严重滞后 / Issue 1: Entry Layer Severely Lagging

**严重程度 / Severity**: 🔴 P0（阻塞 V15 发布）

#### 现状分析 / Current State Analysis

**当前入口端文件：**

| 文件 / File | 版本 / Version | 状态 / Status | 问题 / Issue |
|------|------|------|------|
| `ui_app.py` | V10 | 🟢 活跃入口 | 老旧、简陋、无智能性 |
| `main.py` | V10 | 🟢 启动器 | 仍启动 `ui_app.py`（V10）而非 `web_app.py`（V15） |
| `src/fzq_ai/ui/web_app.py` | V15‑Draft | 🟡 存在但未被启用 | 意图识别 + 任务路由已集成，但 `main.py` 不启动它 |
| `src/fzq_ai/ui/views/zh_intel.py` | V10 | 🟡 视图层 | 硬编码 API URL (`http://localhost:8000/api/zh`)，直接调用 requests |
| `src/fzq_ai/ui/views/metrics_dashboard.py` | V10 | 🟡 视图层 | 简单占位 |
| `src/fzq_ai/ui/theme.py` | V15 | 🟢 设计系统 | **250 行 Bloomberg Terminal 风格，但未被任何 UI 使用** |
| `src/fzq_ai/ui/i18n.py` | V15‑Draft | 🟡 国际化 | 仅 15 个文本条目，覆盖范围不足 |
| `src/fzq_ai/ui/components/` | V15 | 🟡 组件库 | 6 个组件（narrative_block, news_card, radar_chart, risk_block, sentiment_trend, timeline），但 **未在 UI 中引用** |
| `src/fzq_ai/dashboard/` | V15 | 🟡 Dashboard | 4 个组件 + 1 个 dashboard.py，但 **未被使用** |

#### 具体问题 / Specific Issues

**1. 入口层版本混乱 / Entry Layer Version Confusion**
- `main.py` 启动的是 `ui_app.py`（V10），而非 `web_app.py`（V15‑Final）
- `web_app.py` 虽然已集成 `intent_engine` + `task_router`，但形同虚设
- 用户实际看到的仍是 V10 的老旧界面

**2. 缺乏意图识别 / No Intent Recognition**
- `ui_app.py` 使用 `st.sidebar.selectbox` 硬编码页面路由，**完全无视 `intent_engine.py`**
- `intent_engine.py` 已覆盖 8 大任务类型（中英文关键词），但没有任何 UI 调用它
- 用户必须手动选择任务类型，而非输入自然语言让系统自动识别

**3. 缺乏任务路由 / No Task Routing**
- `task_router.py` 已存在，支持 Pipeline fallback 和错误恢复
- 但 `ui_app.py` 的 `selectbox` 直接映射到 `render_zh_intel_page()`，不经过 TaskRouter
- `zh_intel.py` 视图层直接调用 `requests.post()`，不经过 TaskRouter

**4. 缺乏专业美观的界面 / No Professional UI**
- `theme.py` 包含 250 行 Bloomberg Terminal 暗色设计系统（CSS 注入、颜色系统、卡片、标签、状态条、导航药丸）
- **但 `theme.py` 的 `inject_theme()` 从未被调用**
- `ui_app.py` 使用 Streamlit 默认白底主题，与设计系统完全脱节

**5. 缺乏韧性（错误处理、状态恢复）/ Weak Resilience**
- `ui_app.py` 的错误处理：仅 `st.error()` 一行，无状态恢复
- `web_app.py` 有 `SessionState` 和错误边界，但未被启用
- 无重试机制、无降级策略、无用户澄清机制
- `intent_engine.py` 的低置信度澄清机制（`clarification_required`）存在但未被使用

---

### 2.2 问题二：入口端与核心层不匹配 / Issue 2: Entry Layer Mismatched with Core Layer

**严重程度 / Severity**: 🔴 P0（架构失衡）

#### 核心层 vs 入口层对比 / Core Layer vs Entry Layer Comparison

| 能力 / Capability | 核心层 (V14) | 入口层 (V10) | 匹配度 / Match |
|------|------|------|------|
| 自然语言输入 | ✅ TaskOrchestrator.run() | ❌ 硬编码 selectbox | 0% |
| 意图识别 | ✅ IntentEngine (8 种任务) | ❌ 无 | 0% |
| 任务路由 | ✅ TaskRouter (Pipeline fallback) | ❌ 无 | 0% |
| 模型选择 | ✅ ModelSelector (6 个 provider) | ❌ 无 | 0% |
| 多模型 fallback | ✅ Router (自动切换) | ❌ 无 | 0% |
| 错误恢复 | ✅ Recovery Trace | ❌ 仅 st.error() | 10% |
| 双语支持 | ✅ i18n.py (15 文本) | ❌ 硬编码双语 | 20% |
| 专业 UI | ✅ theme.py (250 行 CSS) | ❌ 默认白底 | 0% |
| 可视化组件 | ✅ 6 个组件 + 4 个 dashboard | ❌ 未使用 | 0% |
| 指标展示 | ✅ Metrics Dashboard | ❌ 占位 | 10% |

**关键矛盾 / Key Contradiction**: 核心层拥有完整的 "自然语言 → 意图识别 → 任务路由 → Pipeline → 多模型 fallback → 结构化输出" 全链路，但入口层仍停留在 "手动选择页面 → 手动输入 JSON → 手动调用 API" 的 V10 水平。

---

### 2.3 问题三：双语化不完整 / Issue 3: Incomplete Bilingualization

**严重程度 / Severity**: 🟠 P1

#### 双语化审计 / Bilingualization Audit

**1. UI 层 / UI Layer**
- `ui_app.py`: 硬编码双语（如 `"Home / 首页"`），但 `metrics_dashboard.py` 和 `zh_intel.py` 视图完全英文
- `web_app.py`: 使用 `i18n.py` 系统，但仅 15 个文本条目，无法覆盖完整 UI
- `theme.py`: 完全英文（CSS 类名、注释）
- 组件层：`ui/components/*.py` 和 `dashboard/components/*.py` 完全英文

**2. 文档层 / Documentation Layer**
- `docs/*.md`（15 个文件）：**全部中文，无英文版本**
- `README.md`：双语但已被覆盖为 239 字节（之前审计时重写），旧版 `README_legacy.md` 完整但已过时
- `ROADMAP.md`：仅 Phase C/D 规划，无英文

**3. 代码层 / Code Layer**
- 代码注释：部分双语，但大量文件只有中文或只有英文
- 错误信息：`ui_app.py` 和 `web_app.py` 的双语错误信息不一致
- API 返回：统一为英文，缺少中文本地化

**4. 配置层 / Configuration Layer**
- `.env.example`: 双语标签（中文 + 英文说明）
- `i18n.py`: 15 个 key 的双语字典，但无扩展机制（如从文件加载）

---

### 2.4 问题四：缺乏归档机制 / Issue 4: Missing Archiving Mechanism

**严重程度 / Severity**: 🟠 P1

#### 归档审计 / Archiving Audit

**缺失项 / Missing Items:**

| 归档类型 / Archive Type | 存在 / Exists | 位置 / Location | 问题 / Issue |
|------|------|------|------|
| CHANGELOG | ❌ 不存在 | — | 无版本演进记录 |
| VERSION | ❌ 不存在 | — | 无版本号文件 |
| 架构演进文档 | ❌ 不存在 | — | 无架构决策记录 (ADR) |
| 版本总结 | 🟡 部分 | `docs/` 下多个审计报告 | 分散在不同文件中，无系统整理 |
| 审计历史 | 🟡 部分 | `docs/audit_report.md`, `AUDIT_REPORT.md` | 分散、命名不统一 |
| 路线图 | 🟡 部分 | `ROADMAP.md` | 只有 Phase C/D，缺少 Phase E+ |

**问题影响 / Impact:**
- 无法追溯 V10 → V14 的架构演进过程
- 多次审计报告（DeepSeek, KIMI, 本次 GLM-5.2）散落在不同目录
- 版本号混乱（`app.py` 写 v4.0.0，`api_server.py` 写 v2.5.0，代码注释写 v13/v15）
- 新开发者无法快速理解项目历史

---

### 2.5 问题五：App / Agent Store 准备不足 / Issue 5: Insufficient App/Agent Store Preparation

**严重程度 / Severity**: 🟠 P1（不阻塞 V15 但阻塞 V16）

#### App/Agent Store 准备度审计 / App Readiness Audit

| 准备项 / Readiness Item | 存在 / Exists | 状态 / Status | 缺失 / Missing |
|------|------|------|------|
| `manifest.json` | ❌ | — | Agent Store 上架必需的元数据文件 |
| `Dockerfile` | ❌ | — | 容器化部署 |
| `docker-compose.yml` | ❌ | — | 多服务编排 |
| `mobile/` 目录 | ❌ | — | 移动端适配 |
| `android/` 目录 | ❌ | — | Android App 入口 |
| `ios/` 目录 | ❌ | — | iOS App 入口 |
| API 文档 | 🟡 | FastAPI 自动生成 `/docs` | 缺少手写的 API 使用指南 |
| Agent Store 协议 | ❌ | — | 缺乏标准化的 Agent 描述协议 |
| 多平台入口 | ❌ | — | 仅 Web (Streamlit)，无 App/小程序 |
| 离线能力 | ❌ | — | 无本地模型/缓存策略 |

---

### 2.6 附加问题：多模型路由与 Provider 一致性 / Bonus Issue: Multi-Model Provider Consistency

**严重程度 / Severity**: 🟡 P1（运行时错误风险）

#### Provider 签名不一致 / Provider Signature Inconsistency

| Provider | `run()` 签名 | 返回类型 | 与 Router 兼容 |
|------|------|------|------|
| DeepSeekProvider | `run(self, req: Dict) -> Dict` | `Dict[str, Any]` | ✅ |
| OpenAIProvider | `run(self, req: Dict) -> Dict` | `Dict[str, Any]` | ✅ |
| GeminiProvider | `run(self, req: Dict) -> Dict` | `Dict[str, Any]` | ✅ |
| **GLMProvider** | `run(self, req: LLMRequestSchema) -> str` | `str` | ❌ **不兼容** |
| **KimiProvider** | `run(self, req: LLMRequestSchema) -> str` | `str` | ❌ **不兼容** |
| **QwenProvider** | `run(self, req: LLMRequestSchema) -> str` | `str` | ❌ **不兼容** |

**风险 / Risk**: `Router.run()` 期望接收 `Dict` 并返回 `Dict`，但 GLM/Kimi/Qwen 的 `run()` 接收 `LLMRequestSchema` 并返回 `str`。当 Router 尝试调用这些 provider 时，会抛出 `TypeError`（传参错误）或 `AttributeError`（尝试从 str 取 `get()`）。

**触发场景 / Trigger Scenario**: 当 `settings.model_priority` 包含 `"glm"`、 `"kimi"` 或 `"qwen"`，且这些 provider 被 Router 选中时，系统崩溃。

---

### 2.7 附加问题：Pipelines 与核心层一致性 / Bonus Issue: Pipeline-Core Consistency

**严重程度 / Severity**: 🟡 P2

#### 问题清单 / Issue List

1. **BasePipeline 接口未完全遵循**
   - `NewsPipeline` 没有实现 `call_llm()`（抽象基类要求），而是在 `preprocess()` 中直接构造 prompt 和调用 `fetch_all_news()`
   - `BasePipeline.run()` 会尝试调用 `run_async()`，如果子类定义了 `run_async` 则走 `run_async` 路径，否则走标准流程（validate → preprocess → call_llm → postprocess）
   - `NewsPipeline` 没有定义 `run_async`，但也没有实现 `call_llm`，所以标准流程会抛出 `NotImplementedError`

2. **4 个 zh pipelines 未注册到 PipelineRegistry**
   - `zh_policy_brief_pipeline.py`, `zh_risk_scan_pipeline.py`, `zh_opinion_landscape_pipeline.py`, `zh_multisource_merge_pipeline.py` 存在
   - 但 `@PipelineRegistry.register()` 装饰器未在这些文件中使用
   - 因此 `TaskRouter` 的 `PipelineRegistry.get()` 会抛出 `KeyError`

3. **NewsPipeline 中文字符乱码**
   - `news_pipeline.py` 第 3 行和多个注释位置出现中文乱码（显示为 `?` 或乱码字符），可能是编码问题

---

## 三、问题清单（按优先级排序）/ Issue List (Prioritized)

### P0 — 阻塞级（阻塞 V15 发布）

| # | 问题 / Issue | 文件 / File | 影响 / Impact | 建议修复 / Fix |
|---|------|------|------|------|
| P0‑1 | 入口层版本混乱：`main.py` 启动 V10 `ui_app.py` 而非 V15 `web_app.py` | `main.py`, `ui_app.py` | 用户无法使用 V15 的智能入口 | 修改 `main.py` 启动 `web_app.py`；将 `ui_app.py` 标记为废弃 |
| P0‑2 | 入口层未使用核心层能力：`ui_app.py` 完全绕过 `intent_engine` + `task_router` | `ui_app.py` | 核心层的自然语言 + 意图识别 + 任务路由能力被浪费 | 重写 `ui_app.py` 或全面启用 `web_app.py`，集成 `intent_engine` + `task_router` |
| P0‑3 | `theme.py` 设计系统未被使用 | `theme.py`, `ui_app.py` | 250 行专业设计系统形同虚设 | 在 `web_app.py` 中调用 `inject_theme()` |
| P0‑4 | `zh_intel.py` 视图硬编码 API URL | `zh_intel.py` | 无法部署到非 localhost 环境 | 从环境变量读取 `API_BASE_URL` |
| P0‑5 | zh pipelines 存在重复文件：`zh_policy_pipeline.py` 和 `zh_policy_brief_pipeline.py` 注册同一个 key；`zh_policy_brief_pipeline.py` 未被导入 | `zh_policy_pipeline.py`, `zh_policy_brief_pipeline.py` | 可能引发注册冲突；更完整的版本被忽略 | 保留 `zh_policy_brief_pipeline.py`（更完整），删除 `zh_policy_pipeline.py`，更新 `__init__.py` 导入 |
| P0‑6 | Provider 签名不一致：GLM/Kimi/Qwen 返回 `str` 而非 `Dict` | `glm_provider.py`, `kimi_provider.py`, `qwen_provider.py` | 运行时 `TypeError`/`AttributeError` | 统一所有 provider 的 `run()` 签名：`run(self, req: Dict[str, Any]) -> Dict[str, Any]` |
| P0‑7 | `NewsPipeline` 未实现 `call_llm()` | `news_pipeline.py` | `BasePipeline.run()` 标准流程会抛出 `NotImplementedError` | 添加 `call_llm()` 实现，或添加 `run_async()` 覆盖 |

### P1 — 高优先级（影响 V15 质量）

| # | 问题 / Issue | 文件 / File | 影响 / Impact | 建议修复 / Fix |
|---|------|------|------|------|
| P1‑1 | i18n 系统覆盖不足（仅 15 个文本） | `i18n.py` | 无法覆盖完整 UI 双语化 | 扩展至 100+ 文本条目；添加从 JSON/YAML 文件加载机制 |
| P1‑2 | 文档层无英文版本 | `docs/*.md` | 非中文用户无法使用 | 为所有 `docs/*.md` 添加英文版本（如 `docs/en/`） |
| P1‑3 | 缺乏 CHANGELOG | 根目录 | 无法追溯版本演进 | 创建 `CHANGELOG.md`，记录 V10 → V14 → V15 的关键变更 |
| P1‑4 | 缺乏版本号文件 | 根目录 | 版本号分散在多个文件中 | 创建 `VERSION` 文件，统一版本号管理 |
| P1‑5 | 审计历史分散 | `docs/`, 根目录 | 多次审计报告命名不统一 | 创建 `archive/audits/` 目录，统一归档所有审计报告 |
| P1‑6 | `.env` 曾包含真实 API 密钥（已清理） | `.env` | 密钥泄露风险 | 撤销并重新生成所有已泄露的密钥 |
| P1‑7 | `ui_app.py` 错误处理简单（仅 `st.error()`） | `ui_app.py` | 无状态恢复、无重试 | 集成 `web_app.py` 的 `SessionState` + 错误边界机制 |
| P1‑8 | dashboard 组件未使用 | `dashboard/components/*.py` | 4 个可视化组件形同虚设 | 在 `web_app.py` 中集成 dashboard 组件 |
| P1‑9 | `ui/components/` 未使用 | `ui/components/*.py` | 6 个 UI 组件形同虚设 | 在 `web_app.py` 中集成 narrative_graph, risk_block, sentiment_trend 等组件 |

### P2 — 中优先级（V16 准备）

| # | 问题 / Issue | 文件 / File | 影响 / Impact | 建议修复 / Fix |
|---|------|------|------|------|
| P2‑1 | 无 `manifest.json` | 根目录 | 无法上架 Agent Store | 创建 `manifest.json`，包含 Agent 元数据、能力声明、API 端点 |
| P2‑2 | 无 Dockerfile | 根目录 | 无法容器化部署 | 创建 `Dockerfile` + `docker-compose.yml` |
| P2‑3 | 无移动端入口 | 根目录 | 无 iOS/Android App | 调研 React Native / Flutter 方案，或先准备 PWA |
| P2‑4 | 无离线能力 | 全局 | 无网络时无法使用 | 设计本地缓存策略 + 轻量模型 fallback |
| P2‑5 | 版本号混乱 | 全局 | 同一代码中同时出现 v2.5, v4.0, v9, v10, v13, v14, v15 | 统一版本号：当前为 V15，所有文件引用统一版本号 |
| P2‑6 | 无 API 使用手册（非自动生成） | 根目录 | 开发者/用户不了解 API 用法 | 创建 `API_GUIDE.md` 或 `API_REFERENCE.md` |
| P2‑7 | `news_pipeline.py` 编码问题（中文乱码） | `news_pipeline.py` | 注释和字符串乱码，影响可读性 | 检查文件编码，重新保存为 UTF-8 |

---

## 四、修正建议（按优先级）/ Recommendations (Prioritized)

### P0 修正建议 / P0 Fix Recommendations

#### P0‑1: 统一入口层为 V15 `web_app.py`

```python
# main.py 修改建议
"""
FZQ-AI Launcher (V15-Final)
启动 V15 智能入口（web_app.py），废弃 V10 入口（ui_app.py）
"""

import sys
import os

# 确保 src 在 PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from fzq_ai.ui.web_app import main

if __name__ == "__main__":
    main()
```

```python
# ui_app.py 标记为废弃
import warnings
warnings.warn(
    "ui_app.py is deprecated. Use 'streamlit run -m fzq_ai.ui.web_app' instead.",
    DeprecationWarning,
    stacklevel=2,
)
```

#### P0‑2: 在 `web_app.py` 中注入主题系统

```python
# web_app.py 修改
from fzq_ai.ui.theme import inject_theme

def main():
    st.set_page_config(...)
    inject_theme()  # 注入 Bloomberg Terminal 暗色主题
    # ... 其余代码
```

#### P0‑3: 注册 4 个 zh pipelines

```python
# zh_policy_brief_pipeline.py 顶部添加
from fzq_ai.pipelines.registry import PipelineRegistry

@PipelineRegistry.register("zh_policy_brief@v1")
class ZhPolicyBriefPipeline(BasePipeline):
    ...
```

#### P0‑4: 统一 Provider 签名

```python
# glm_provider.py 修改建议
class GLMProvider:
    async def run(self, req: Dict[str, Any]) -> Dict[str, Any]:
        # 将 Dict 转换为 LLMRequestSchema
        llm_req = LLMRequestSchema(**req)
        raw_output = await self._call_api(llm_req)
        return {"output": raw_output, "provider": "glm", "model": llm_req.model}
```

---

### P1 修正建议 / P1 Fix Recommendations

#### P1‑1: 扩展 i18n 系统

```python
# i18n.py 扩展建议
# 从 JSON 文件加载，支持热更新
import json
from pathlib import Path

_TEXTS_PATH = Path(__file__).parent / "locales"

def load_texts():
    texts = {}
    for lang in ["zh", "en"]:
        path = _TEXTS_PATH / f"{lang}.json"
        if path.exists():
            texts[lang] = json.loads(path.read_text(encoding="utf-8"))
    return texts
```

#### P1‑3: 创建 CHANGELOG

```markdown
# CHANGELOG.md

## V15.0.0 (2026-06-27)
- 入口端升级为 V15：新增 web_app.py + intent_engine + task_router
- 多模型路由新增 GLM / Kimi / Qwen  providers
- 主题系统：Bloomberg Terminal 暗色设计系统
- 双语化：i18n 系统覆盖 15+ 文本

## V14.0.0 (2026-06-20)
- 多模型路由成熟：DeepSeek / OpenAI / Gemini
- Orchestrator 成熟：TaskOrchestrator + Recovery Trace
- Pipelines 体系化：8 个 Pipeline + BasePipeline Protocol
- Schemas + Validators 完整
- Metrics + Logging 成熟

## V10.0.0 (Earlier)
- Streamlit UI 初版
- 基础 API 端点
- 简单新闻抓取
```

#### P1‑5: 统一审计归档

```
archive/
├── audits/
│   ├── 2026-06-19_deepseek_audit.md
│   ├── 2026-06-21_kimi_audit.md
│   └── 2026-06-27_glm52_audit.md  # 本次审计
├── architecture/
│   ├── v10_entry_layer.md
│   ├── v14_core_layer.md
│   └── v15_entry_layer_plan.md
└── decisions/
    └── 001_use_streamlit_for_ui.md  # ADR
```

---

## 五、V15 入口端开发路线图（双语）/ V15 Entry Layer Development Roadmap (Bilingual)

### Phase E — 入口端统一（1 周）/ Phase E — Entry Layer Unification (1 Week)

**目标 / Goal**: 统一入口为 `web_app.py`，废弃 `ui_app.py`

| 任务 / Task | 负责人 / Owner | 产出 / Deliverable |
|------|------|------|
| 修改 `main.py` 启动 `web_app.py` | Nick | `main.py` V15 |
| 在 `web_app.py` 注入 `theme.py` | Nick | 暗色主题生效 |
| 将 `ui_app.py` 标记为废弃 | Nick | 废弃警告 |
| 验证 `web_app.py` 的 4 个任务入口可用 | Nick | 端到端测试通过 |

### Phase F — 智能性增强（1 周）/ Phase F — Intelligence Enhancement (1 Week)

**目标 / Goal**: 集成意图识别 + 任务路由，让入口端具备智能性

| 任务 / Task | 负责人 / Owner | 产出 / Deliverable |
|------|------|------|
| 在 `web_app.py` 集成 `intent_engine.classify()` | Nick | 自然语言输入自动识别任务 |
| 在 `web_app.py` 集成 `task_router.route()` | Nick | 自动路由到 Pipeline |
| 添加低置信度澄清 UI（用户确认） | Nick | 意图不明确时弹出确认对话框 |
| 集成 dashboard 组件（narrative_graph, risk_block, sentiment_trend） | Nick | 专业可视化 |
| 集成 `ui/components/` 到 `web_app.py` | Nick | 组件库生效 |

### Phase G — 韧性增强（3–5 天）/ Phase G — Resilience Enhancement (3–5 Days)

**目标 / Goal**: 错误处理、状态恢复、降级策略

| 任务 / Task | 负责人 / Owner | 产出 / Deliverable |
|------|------|------|
| 统一错误边界：API 错误、Pipeline 错误、Model 错误 | Nick | 三级错误分类 + 用户友好提示 |
| SessionState 持久化：刷新页面不丢失状态 | Nick | 状态恢复机制 |
| 自动重试：API 失败时自动重试 3 次 | Nick | 重试逻辑 + 指数退避 |
| 降级策略：当所有模型失败时显示本地缓存/静态内容 | Nick | 降级 UI |
| 加载状态优化：Skeleton Screen / 进度条 | Nick | 专业加载体验 |

### Phase H — 双语化全面落地（3–5 天）/ Phase H — Full Bilingualization (3–5 Days)

**目标 / Goal**: UI 和文档完全双语化

| 任务 / Task | 负责人 / Owner | 产出 / Deliverable |
|------|------|------|
| 扩展 `i18n.py` 至 100+ 文本条目 | Nick | 完整 UI 覆盖 |
| 将 i18n 改为 JSON 文件加载（支持热更新） | Nick | `locales/zh.json` + `locales/en.json` |
| 所有 `docs/*.md` 添加英文版本（`docs/en/*.md`） | Nick | 双语文档 |
| 更新 `README.md` 为完整双语版 | Nick | 专业 README |
| API 返回信息双语化 | Nick | 中文/英文动态切换 |

### Phase I — 归档机制建立（2–3 天）/ Phase I — Archiving Mechanism (2–3 Days)

**目标 / Goal**: 建立系统化的版本归档和审计记录

| 任务 / Task | 负责人 / Owner | 产出 / Deliverable |
|------|------|------|
| 创建 `CHANGELOG.md` | Nick | 版本演进记录 |
| 创建 `VERSION` 文件 | Nick | 统一版本号 |
| 创建 `archive/` 目录结构 | Nick | 审计归档 + 架构决策 |
| 迁移所有历史审计报告到 `archive/audits/` | Nick | 统一归档 |
| 编写架构决策记录（ADR）模板 | Nick | ADR 模板 + 已有决策记录 |

### Phase J — App / Agent Store 准备（1–2 周）/ Phase J — App/Agent Store Preparation (1–2 Weeks)

**目标 / Goal**: 为 V16 的 App/Agent Store 发布做准备

| 任务 / Task | 负责人 / Owner | 产出 / Deliverable |
|------|------|------|
| 创建 `manifest.json`（Agent Store 元数据） | Nick | Agent Store 上架文件 |
| 创建 `Dockerfile` + `docker-compose.yml` | Nick | 容器化部署 |
| 设计 PWA 方案（渐进式 Web App） | Nick | PWA manifest + service worker |
| 编写 API 使用手册（非自动生成） | Nick | `API_GUIDE.md` |
| 调研移动端框架（React Native / Flutter） | Nick | 技术选型报告 |
| 设计离线缓存策略 | Nick | 离线模式方案 |

---

## 六、修复后的理想状态 / Ideal State After Fixes

### 入口端（V15）/ Entry Layer (V15)

```
用户打开 FZQ-AI
    ↓
[暗色 Bloomberg Terminal 主题] ← theme.py 注入
    ↓
用户输入自然语言（中文/英文）
    ↓
[intent_engine] → 识别任务类型（8 种 + 澄清）
    ↓
[task_router] → 自动选择 Pipeline（带 fallback）
    ↓
[Pipeline] → 执行（preprocess → call_llm → postprocess）
    ↓
[Router] → 选择最优模型（6 providers + fallback）
    ↓
[可视化] → narrative_graph / risk_block / sentiment_trend
    ↓
[双语输出] → 中文/英文根据用户偏好自动切换
```

### 核心层（V14）→ 入口端（V15）匹配度 / Core-to-Entry Match

| 能力 | 核心层 | 入口端（修复后） | 匹配度 |
|------|------|------|------|
| 自然语言输入 | ✅ | ✅ 集成 intent_engine | 100% |
| 意图识别 | ✅ | ✅ 自动识别 8 种任务 | 100% |
| 任务路由 | ✅ | ✅ 自动路由 + fallback | 100% |
| 模型选择 | ✅ | ✅ 6 providers + metrics | 100% |
| 多模型 fallback | ✅ | ✅ 自动切换 | 100% |
| 错误恢复 | ✅ | ✅ 三级错误 + 重试 | 90% |
| 双语支持 | ✅ | ✅ 100+ 文本 + JSON 加载 | 90% |
| 专业 UI | ✅ | ✅ 暗色主题 + 组件库 | 90% |
| 可视化组件 | ✅ | ✅ 6 组件 + 4 dashboard | 90% |
| 指标展示 | ✅ | ✅ 完整 Metrics Dashboard | 90% |

---

## 七、附录 / Appendix

### A. 项目仓库信息 / Repository Info

| 仓库 / Repository | 路径 / Path | 用途 / Purpose |
|------|------|------|
| DS GUI 工作目录 | `C:\Users\nicka\.kun\default_workspace\fzq_ai_review` | 自动修复代码存放 |
| 本地 Git 仓库 | `C:\Users\nicka\FZQ-AI-WORKSPACE\FZQ-AI` | 当前审计对象 |
| GitHub 远程 | `https://github.com/nickacy/FZQ-AI` | 远程备份 |

### B. 两轮审计累计修改清单 / Cumulative Fix Log (Two Rounds)

**第一轮审计（2026-06-23）/ Round 1:**
- 删除 15+ 死代码文件和目录
- 修复 `config/__init__.py` YAML 解析 bug（`json.load` → `yaml.safe_load`）
- 移除 5 处重复 `load_dotenv()`
- CORS 从 `allow_origins=[