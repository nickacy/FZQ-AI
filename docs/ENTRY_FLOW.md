# ENTRY_FLOW.md

> FZQ-AI Entry Layer Data Flow & State Transition Diagram
> 版本：V19.0.0 | 状态：生产就绪
> 最后更新：2025-07-03

---

## 1. 概述

本文档描述 Entry Layer 的完整数据流：从请求进入系统，到意图识别、任务路由、智能体执行，再到结果返回的每一步。

---

## 2. 整体架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                        Client (Web UI / APP)                    │
│                                                                 │
│  POST /api/v1/entry    POST /api/v1/multi    POST /api/v1/autonomy
└────────────────────┬─────────────────────┬────────────────────┘
                     │                     │
                     ▼                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                         FastAPI (app.py)                        │
│                     1. 参数校验 (Pydantic)                        │
│                     2. CORS 处理                                  │
│                     3. 异常捕获                                   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                     EntryServiceV24                             │
│                     4. 构建 AgentContext                          │
│                     5. 选择执行模式 (single/multi/autonomy)       │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                   UnifiedOrchestratorV24                        │
│                     6. 意图识别 (IntentEngine)                    │
│                     7. 任务路由 (TaskRouter)                      │
│                     8. Blackboard 状态管理                         │
└────────────────────────┬────────────────────────────────────────┘
                         │
            ┌────────────┼────────────┐
            ▼            ▼            ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  Pipeline    │ │  Pipeline    │ │  Pipeline    │
│  (Single)    │ │  (Multi)     │ │  (Autonomy)  │
│              │ │              │ │              │
│  - zh_policy │ │  - Parallel  │ │  - Analysis  │
│  - zh_risk   │ │  - Merge     │ │  - Planning  │
│  - zh_opinion│ │  - Aggregate │ │  - Execution │
│  - zh_merge  │ │              │ │  - Finalize  │
└──────┬───────┘ └──────┬───────┘ └──────┬───────┘
       │                │                │
       ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────┐
│                         LLM Router                                │
│                    9. 多模型路由 (6 Providers)                     │
│                   10. Fallback 链（降级处理）                      │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Result Aggregation                          │
│                    11. 结果格式化 (V23 Schema)                  │
│                   12. UI Schema 生成                            │
│                   13. Timeline 构建                             │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                        V24 Response                             │
│                    14. 翻译为前端契约                             │
│                    15. 返回 JSON                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. 状态机转换图

### 3.1 Single Agent 状态流

```
┌─────────┐     ┌──────────┐     ┌───────────┐     ┌───────────┐     ┌──────────┐
│  INTAKE │ ──► │  ROUTING │ ──► │ EXECUTION │ ──► │ FINALIZE │ ──► │  DONE   │
└─────────┘     └──────────┘     └───────────┘     └───────────┘     └──────────┘
     │               │                  │                  │
     │               │                  │                  │
     ▼               ▼                  ▼                  ▼
  参数校验        意图识别        Pipeline 执行        结果格式化
  安全校验        智能体选择        LLM 调用            UI Schema
  Blackboard      模型选择          Fallback 链         Timeline
  初始化          Fallback 预配                       返回
```

---

### 3.2 Multi Agent 状态流

```
┌─────────┐     ┌──────────┐     ┌──────────┐     ┌───────────┐     ┌──────────┐
│  INTAKE │ ──► │  ROUTING │ ──► │ PARALLEL │ ──► │   MERGE   │ ──► │ FINALIZE│
└─────────┘     └──────────┘     └──────────┘     └───────────┘     └──────────┘
                                      │
                                      ▼
                              ┌──────────────┐
                              │  Task 1      │
                              │  Task 2      │  并行执行
                              │  Task 3      │
                              └──────────────┘
```

---

### 3.3 Autonomy 状态流

```
┌─────────┐     ┌──────────┐     ┌──────────┐     ┌───────────┐     ┌──────────┐
│  INTAKE │ ──► │  ANALYSIS│ ──► │  PLANNING│ ──► │ EXECUTION │ ──► │ FINALIZE│
└─────────┘     └──────────┘     └──────────┘     └───────────┘     └──────────┘
                    │                 │                 │
                    ▼                 ▼                 ▼
               意图深度分析      生成执行计划      按计划执行
               需求拆解          智能体选择        动态调度
               上下文推断        优先级排序
```

---

### 3.4 错误状态流

```
┌───────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│ EXECUTION │ ──► │  RETRY   │ ──► │ FALLBACK │ ──► │ FINALIZE │
└───────────┘     └──────────┘     └──────────┘     └──────────┘
   (失败)           (重试)          (降级模型)        (降级结果)
```

**重试策略：**
- 首次失败：等待 1s 重试
- 二次失败：切换到 Fallback Provider（如 deepseek → glm）
- 三次失败：返回降级结果（本地缓存 / 简单模板）

---

## 4. 数据流详解

### 4.1 请求进入 → 参数校验

```
Client Request
     │
     ▼
POST /api/v1/entry
{
  "text": "分析中美科技竞争",
  "language": "zh"
}
     │
     ▼
FastAPI Pydantic Validation
     │
     ▼
V24EntryRequest(text="分析中美科技竞争", language="zh")
     │
     ▼
✅ 校验通过 → 进入 EntryServiceV24
❌ 校验失败 → 返回 400 + 错误详情
```

---

### 4.2 EntryService → Orchestrator

```
EntryServiceV24.handle_single(payload)
     │
     ▼
构建 AgentContext
{
  "user_id": "anonymous",
  "locale": "zh-CN",
  "focus_regions": [],
  "languages": ["zh"],
  "raw_input": "分析中美科技竞争",
  "metadata": {}
}
     │
     ▼
调用 UnifiedOrchestratorV24.run_single(task, ctx, options)
```

---

### 4.3 Orchestrator → Pipeline

```
UnifiedOrchestratorV24
     │
     ├─► IntentEngine.classify("分析中美科技竞争")
     │       │
     │       ▼
     │   {"task_type": "zh_risk_scan", "confidence": 0.95, "language": "zh"}
     │
     ├─► TaskRouter.route(task_type, content)
     │       │
     │       ▼
     │   PipelineRegistry.get("zh_risk_scan")
     │       │
     │       ▼
     │   zh_risk_scan_pipeline.run(content="分析中美科技竞争")
     │
     ├─► Blackboard.write("sys.timeline", [...])
     │
     ▼
Pipeline 返回 Dict
```

---

### 4.4 Pipeline → LLM Router

```
zh_risk_scan_pipeline.run(content)
     │
     ├─► 1. preprocess(content)
     │
     ├─► 2. call_llm(prompt)
     │       │
     │       ▼
     │   ModelRouter.select("zh_risk_scan")
     │       │
     │       ▼
     │   Provider 优先级：deepseek → glm → kimi → qwen
     │       │
     │       ▼
     │   await provider.run(req)
     │
     ├─► 3. postprocess(result)
     │
     ▼
返回结构化 Dict
```

---

### 4.5 结果 → 响应

```
Pipeline Result
     │
     ▼
RouteResult(data=result, ui_layout=..., timeline=...)
     │
     ▼
EntryServiceV24 返回
     │
     ▼
translate_to_v24_contract(v23_result)
     │
     ▼
{
  "execution": { ... },
  "ui_schema": { ... }
}
     │
     ▼
FastAPI JSONResponse
     │
     ▼
Client
```

---

## 5. Blackboard 状态管理

Blackboard 是 Orchestrator 的共享状态空间，所有智能体可以读写：

```
Blackboard Key Structure:

req.*         — 请求层（不可变）
  req.task        = "分析中美科技竞争"
  req.ctx         = AgentContext
  req.language    = "zh"

sys.*         — 系统层（Orchestrator 管理）
  sys.phase       = "EXECUTION"
  sys.timeline    = [TimelineEvent, ...]
  sys.providers   = ["deepseek", "glm", "kimi"]
  sys.fallbacks   = 0

intent.*      — 意图层（IntentEngine 写入）
  intent.type     = "zh_risk_scan"
  intent.conf     = 0.95
  intent.language = "zh"

route.*       — 路由层（TaskRouter 写入）
  route.pipeline  = "zh_risk_scan"
  route.provider  = "deepseek"
  route.model     = "deepseek-chat"

exec.*        — 执行层（Pipeline 写入）
  exec.output     = { ... }
  exec.tokens     = 1234
  exec.latency    = 2345

result.*      — 结果层（最终输出）
  result.data     = { ... }
  result.ui       = { ... }
  result.errors   = []
```

---

## 6. Timeline 构建

Timeline 记录执行全过程，用于前端展示：

```json
[
  {"phase": "INTAKE",    "timestamp": "2025-07-03T10:00:00Z", "detail": "Received input: 分析中美科技竞争"},
  {"phase": "ROUTING",   "timestamp": "2025-07-03T10:00:01Z", "detail": "Intent: zh_risk_scan, confidence: 0.95"},
  {"phase": "EXECUTION", "timestamp": "2025-07-03T10:00:03Z", "detail": "Pipeline zh_risk_scan running"},
  {"phase": "EXECUTION", "timestamp": "2025-07-03T10:00:04Z", "detail": "LLM call: deepseek-chat, 1234 tokens"},
  {"phase": "FINALIZE",  "timestamp": "2025-07-03T10:00:05Z", "detail": "UI schema generated"}
]
```

---

## 7. 错误处理流

### 7.1 正常流程

```
INTAKE → ROUTING → EXECUTION → FINALIZE → DONE
```

### 7.2 路由失败

```
INTAKE → ROUTING → ❌ (未知任务类型) → FALLBACK → FINALIZE → DONE
                                      │
                                      ▼
                              使用默认 Pipeline (news)
```

### 7.3 LLM 调用失败

```
INTAKE → ROUTING → EXECUTION → ❌ (Provider 超时) → RETRY → ❌ → FALLBACK → FINALIZE → DONE
                                                        │
                                                        ▼
                                                 切换到 glm Provider
```

### 7.4 严重错误

```
INTAKE → ROUTING → EXECUTION → ❌ → RETRY → ❌ → FALLBACK → ❌ → FINALIZE → ERROR
                                                                     │
                                                                     ▼
                                                              返回降级结果 + 错误信息
```

---

## 8. 相关文档

- [ENTRY_PROTOCOL.md](ENTRY_PROTOCOL.md) — 协议规范
- [ENTRY_SCHEMA.md](ENTRY_SCHEMA.md) — Schema 定义
- [API_GUIDE.md](API_GUIDE.md) — 完整 API 使用指南
