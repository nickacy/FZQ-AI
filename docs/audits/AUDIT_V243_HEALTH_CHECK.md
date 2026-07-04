# FZQ-AI V24.3.0 · 全面体检审计报告

> **审计日期**：2026-07-04
> **审计基准**：commit `a092a601` (v24.3.0: civilization 4-layer integration)
> **审计方法**：`git grep` / `git diff` / `git log` / 静态分析 / 逐条验证
> **原则**：陈述可证伪事实，不做猜测
> **含评分 + 优先级排序的改进建议**

---

## TL;DR

- **综合健康度**：**75/100**（上次审计 60 → 本次 +15 分）
- **v24.3.0 是一次大规模清理**：删除了 ~150KB 死代码（intel/、interpreter/、llm/orchestrator/、旧 agents）
- **版本号已完全统一** ✅（V24.0.0 全域一致）
- **根目录已完全清洁** ✅
- **Civilization 已入门级接入** ✅（1 个 import，仍有深度接入空间）
- **仍有 8 个孤立子目录** ⚠️（~80KB 死代码）
- **API 仍未使用 Pydantic response_model** ❌（OpenAPI 无结构化的响应类型）

---

## 1. 维度评分

| 维度 | 上次评分 | 本次评分 | 变化 | 说明 |
|------|---------|---------|------|------|
| 版本一致性 | 30/100 🔴 | 95/100 🟢 | **+65** | 全部统一 V24.0.0 |
| 根目录清洁度 | 40/100 🔴 | 95/100 🟢 | **+55** | 9 个污染物全部清除 |
| 代码结构 | 60/100 🟡 | 83/100 🟢 | **+23** | 死代码 -40 文件 |
| 架构完整性 | 50/100 🔴 | 78/100 🟢 | **+28** | 5 代→1 代，11 孤立→8 孤立 |
| 测试质量 | 30/100 🔴 | 55/100 🟡 | **+25** | 新增 civilization 测试 |
| 文档一致性 | 55/100 🟡 | 70/100 🟡 | **+15** | V24 双语架构文档 |
| 前端结构 | 80/100 🟢 | 82/100 🟢 | +2 | 稳定 |
| API 规范性 | 30/100 🔴 | 50/100 🟡 | **+20** | RouteResult Pydantic 化 |
| 安全性 | 95/100 🟢 | 95/100 🟢 | 0 | 稳定 |
| **综合** | **~60/100** | **75/100** | **+15** | |

---

## 2. 与上次审计的对比：已治理的债务

### ✅ 已完全修复

| # | 上次审计问题 | 修复情况 | 证据 |
|---|------------|---------|------|
| 1 | 版本号混乱（7 文件 4 种版本） | ✅ 全部统一 V24.0.0 | `VERSION.txt`, `pyproject.toml`, `setup.py`, `api/app.py`, `frontend-react/package.json` |
| 2 | 根目录污染物（9 个文件/目录） | ✅ 全部清除 | `git ls-files` 无污染物 |
| 3 | `.gitignore` 缺少 `*.jsonl` 等 | ✅ 已补全 | `*.jsonl`, `.pytest_cache/`, `data/logs/` |
| 4 | llm/orchestrator 33 文件死代码 | ✅ 全部删除 | 0 文件残留 |
| 5 | llm/model_router、llm_router | ✅ 已删除 | 5 套→2 套（router.py + task_router.py） |
| 6 | intel/ 11 文件孤立子系统 | ✅ 全部删除 | 0 文件残留 |
| 7 | interpreter/kimi_interpreter.py（730行） | ✅ 已删除 | 0 文件残留 |
| 8 | longcat/ 孤立模块 | ✅ 已删除 | 0 文件残留 |
| 9 | V19/V21/V22/V23 agents 残留 | ✅ 删除 13 个旧文件 | agents 27→14 文件 |
| 10 | 旧 orchestrator 文件（4个+selector+builder） | ✅ 删除 6 个 | orchestrator 10→6 文件 |
| 11 | sync/async 混合 | ✅ Task agents 改为 async | 4/4 task agents async |
| 12 | BaseAgent AgentContext/Result 非 Pydantic | ✅ 已 Pydantic 化 | BaseModel |
| 13 | RouteResult 非 Pydantic | ✅ 已 Pydantic 化 | BaseModel + model_dump() |
| 14 | Civilization 0 import | ✅ 1 个入门级接入 | `entry_service_v24.py:8` |
| 15 | Domain 模型孤立 | ✅ 20+ 生产 import | pipelines/tools/store 引用 |

---

## 3. 仍存在的问题

### P0 — 影响架构诚信/API 安全

#### 3.1 API 端点无 `response_model=`（0/7）

```bash
$ git grep "response_model=" -- src/fzq_ai/api/**.py
# 输出: (空)
```

**影响**：
- OpenAPI/Swagger 文档看不到响应结构
- FastAPI 不做响应验证，错误不会在 API 层被拦截
- 前端得不到编译期类型保护

**修复**：对 `/entry`, `/multi`, `/autonomy`, `/api/zh/*` 等 7 个端点逐一加 `response_model=RouteResult`

**工作量**：~4 小时

#### 3.2 `llm/router_v2/` 仍存在（第三套 Router）

| 文件 | 生产引用 |
|------|---------|
| `router.py` | 仅自身 |
| `selectors.py` | 仅 `router.py` |
| `rules.py` | 0 |
| `types.py` | 仅 `router_v2/*` |
| `metrics_adapter.py` | 0 |

**生产引用**：仅 `tests/test_router/test_router_v2.py` + `test_router_v2_integration.py`

**问题**：与生产 Router（`llm/router.py` + `core/task_router.py`）并存，新人不知道该用哪个

**修复方案**：接入主链路 OR 删除 + 移除 2 个对应测试文件

**工作量**：~2 小时

#### 3.3 `agents/coop/` 孤立 + 潜在循环依赖

```bash
$ git grep "from fzq_ai.agents.coop" -- src/fzq_ai/api/**.py
# 输出: (空)
```

`coop/orchestrator.py:12` 有 `from fzq_ai.registry.agents import get_agent` — 目前不触发循环，但如果 `agents/__init__.py` 被修改可能引爆。

**修复方案**：删除 coop/ 或改为 lazy import

**工作量**：~1 小时

---

### P1 — 影响代码库卫生

#### 3.4 8 个孤立子目录（~80KB 死代码）

| 子目录 | 文件数 | 生产引用 |
|--------|-------|---------|
| `cache/` | 1 | 0 |
| `cli/` | 1 | 0 |
| `clients/` | 1 | 0 |
| `dashboard/` | 1 | 0 |
| `logging/` | 2 | 0 |
| `monitor/` | 1 | 0 |
| `store/` | 3 | 0 |
| `storage/` | 1（空 __init__） | 0 |
| `tools/` | 12 | 0 |

**验证命令**：
```bash
git grep -l "from fzq_ai.cache\|from fzq_ai.cli\|from fzq_ai.clients\|from fzq_ai.dashboard\|from fzq_ai.logging\|from fzq_ai.monitor\|from fzq_ai.store\|from fzq_ai.storage\|from fzq_ai.tools" -- "src/fzq_ai/api/**/*.py" "src/fzq_ai/orchestrator/**/*.py" "src/fzq_ai/pipelines/**/*.py" "src/fzq_ai/agents/tasks/*.py" "src/fzq_ai/agents/news_*.py" "src/fzq_ai/agents/multi_agent.py" "src/fzq_ai/agents/news_center_agent.py" "src/fzq_ai/entry/**/*.py"
# 输出: (空 — 0 个生产引用)
```

**注意**：`tools/` 和 `store/` 内部互相引用 domain 模型，但这些引用本身在孤立代码间互调。从生产视角看，全部未接入。

**修复方案**：逐一评估 → 接入 or 归档 or 删除

**工作量**：~4 小时

#### 3.5 缺少 API e2e 测试

V24.2.0 曾经有 16 个端点 e2e 测试（commit `bc6a621d`），在某次 auto-commit 中被删除。当前仅有 `test_e2e/test_news_center.py` 一个 e2e 测试（30 行冒烟）。

**修复方案**：补写 `/entry`, `/multi`, `/autonomy` 的 happy path + error path 测试

**工作量**：~6 小时

---

### P2 — 影响开发体验

#### 3.6 USAGE_GUIDE.md 可能引用过时模块

`USAGE_GUIDE.md` 引用了 `fzq_ai.llm.enhanced_cache`、`fzq_ai.utils.circuit_breaker` 等——需逐条验证这些模块是否仍存在且可用。

#### 3.7 `docs/audits/` 过于拥挤

21 个审计/改进相关文件堆积在 `docs/audits/` 目录。建议：
- 保留最近 3 份审计报告
- 其余移入 `archive/audits/`

---

## 4. 当前架构快照

```
src/fzq_ai/
├── api/              V24 统一入口（app.py + entry + zh_endpoints + v24_routes）✅
├── agents/           14 文件，单代（V24）✅
│   ├── base.py           Pydantic AgentContext/Result ✅
│   ├── autonomy_agent_v24.py ✅
│   ├── multi_agent.py    ✅
│   ├── news_agent_v24.py ✅
│   ├── news_center_agent.py ✅
│   ├── tasks/            4 async agents ✅
│   └── coop/             3 文件孤立 ⚠️
├── civilization/     3 文件，1 生产 import（入门级接入）✅
├── config/           现代化配置（YAML + env）✅
├── core/             5 文件（IntentEngine/TaskRouter/LLMExecutor）✅
├── domain/           4 文件，20+ 生产引用 ✅
├── llm/
│   ├── router.py     生产 Router ✅
│   ├── failover.py   3 级故障转移 ✅
│   ├── router_v2/    5 文件孤立 ⚠️
│   └── test_adapter/ 测试桩
├── orchestrator/     6 文件（unified_v24 + task + blackboard）✅
├── pipelines/        14 文件（zh_* 真业务 + base/protocol/errors）✅
├── quality/          2 真业务文件 ✅
├── registry/         4 文件 ✅
├── schemas/          8 文件（含 Pydantic RouteResult）✅
├── ui/               2 文件（web_app thin re-export）✅
└── utils/            21 文件 ✅
│
├── cache/            孤立 ⚠️
├── cli/              孤立 ⚠️
├── clients/          孤立（V19 ModelClient）⚠️
├── dashboard/        孤立 ⚠️
├── logging/          孤立 ⚠️
├── monitor/          孤立 ⚠️
├── store/            孤立 ⚠️
├── storage/          真空 ⚠️
└── tools/            12 文件孤立 ⚠️
```

---

## 5. 改进路线图（按 ROI 排序）

### 立即执行（1-2 天，ROI 极高）

| # | 任务 | 工作量 | 收益 |
|---|------|--------|------|
| 1 | 所有 API 端点加 `response_model=RouteResult` | 4h | OpenAPI 类型安全 |
| 2 | 删除 `llm/router_v2/` + 对应 2 测试文件 | 2h | Router 实质统一 |
| 3 | 删除 `agents/coop/` 3 文件 | 1h | 消除潜在循环依赖 |
| 4 | 删除 `storage/` + `models/` 真空目录 | 0.5h | 清洁 |

### 本周执行（3-5 天，ROI 高）

| # | 任务 | 工作量 | 收益 |
|---|------|--------|------|
| 5 | 评估并处理 8 个孤立子目录（接入 or 删） | 4h | 减少 80KB 死代码 |
| 6 | 补写 API e2e 测试 | 6h | 测试覆盖 |
| 7 | Civilization 深度接入（parliament/consensus/evolution 接入主链路） | 8h | 架构诚信 |

### 长期（1-2 周，战略性）

| # | 任务 | 工作量 | 收益 |
|---|------|--------|------|
| 8 | 更新 USAGE_GUIDE.md 只保留 V24 有效模块 | 2h | 文档准确 |
| 9 | docs/audits/ 归档历史报告 | 1h | 清晰 |
| 10 | commit message 规范（禁止 "git pull" 匿名提交） | 持续 | git blame 可用 |
| 11 | 建立 "接入声明必须有 import 证据" 的代码审查规则 | 持续 | 防止债务回潮 |

---

## 6. 可复现验证命令

```bash
# 1. 版本号一致性
git grep -n "version.*24\.0\.0\|VERSION.*24\.0\.0\|V24\.0\.0" -- VERSION.txt pyproject.toml setup.py "src/fzq_ai/api/app.py" "frontend-react/package.json"

# 2. 根目录清洁度
# 应该只有项目文件，无日志/临时文件
git ls-files -cocmo -- :/"*.jsonl"  # 期望: (空)

# 3. 孤立子目录
for dir in cache cli clients dashboard logging monitor store storage tools; do
  refs=$(git grep -l "from fzq_ai.$dir" -- "src/fzq_ai/api/**/*.py" "src/fzq_ai/orchestrator/**/*.py" "src/fzq_ai/pipelines/**/*.py" "src/fzq_ai/agents/tasks/*.py" "src/fzq_ai/agents/news_*.py" 2>/dev/null)
  if [ -z "$refs" ]; then echo "ORPHAN: $dir"; fi
done

# 4. API response_model
git grep "response_model=" -- "src/fzq_ai/api/**.py"
# 期望: 至少 7 个匹配（实际: 0）

# 5. Civilization 接入深度
git grep -l "from fzq_ai.civilization" -- "src/**/*.py"
# 期望: >3 个入口（实际: 1）

# 6. agents/ 代际
git ls-files "src/fzq_ai/agents/" | Measure-Object
# 期望: ~10 个（实际: 14，含 coop/ 3 文件）

# 7. Router 套数
git ls-files "src/fzq_ai/llm/router*" "src/fzq_ai/llm/router_v2/" "src/fzq_ai/core/task_router.py"
# 期望: 仅 router.py 和 task_router.py（实际: 多了 router_v2/）

# 8. 文档是否有 README
git ls-files "docs/README.md"
# 期望: 存在（实际: 已存在 ✅）
```

---

## 7. 总结

**v24.3.0 是迄今为止最大的一次代码清理**，解决了上次审计中标记的 ~80% 问题。综合健康度从 60 分跃升至 75 分。

**剩余最关键的两项**：
1. **`response_model=`** — 这是 API 契约的最后缺口
2. **`llm/router_v2/`** — Router 仍未实质统一

完成 P0 项（约 7.5 小时）后，项目可达到 **~85/100** 的健康度。
