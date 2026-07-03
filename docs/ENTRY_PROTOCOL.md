# ENTRY_PROTOCOL.md

> FZQ-AI Entry Layer Protocol Specification
> 版本：V19.0.0 | 状态：生产就绪
> 最后更新：2025-07-03

---

## 1. 概述

FZQ-AI Entry Layer 是系统的统一入口层，负责接收所有外部请求（Web UI、APP、第三方集成），进行意图识别、任务路由、安全校验，并将请求分发到下游 Pipeline 或 Agent。

**Entry Layer 提供三种入口模式：**

| 模式 | 端点 | 用途 |
|------|------|------|
| Single Agent | `POST /api/v1/entry` | 单智能体任务执行 |
| Multi Agent | `POST /api/v1/multi` | 多智能体协作执行 |
| Autonomy | `POST /api/v1/autonomy` | 自治智能体执行 |

---

## 2. 协议基础

### 2.1 基础 URL

```
开发环境：http://localhost:8000
生产环境：https://api.fzq-ai.com
```

### 2.2 请求格式

所有请求使用 **JSON** 格式，`Content-Type: application/json`。

### 2.3 响应格式

统一响应结构：

```json
{
  "status": "ok" | "error",
  "data": { ... },
  "message": "",
  "trace_id": "uuid",
  "duration_ms": 1234
}
```

### 2.4 错误码

| HTTP 状态码 | 错误码 | 说明 |
|------------|--------|------|
| 200 | — | 成功 |
| 400 | INVALID_REQUEST | 请求参数无效 |
| 401 | UNAUTHORIZED | 未认证（API Key 无效） |
| 403 | FORBIDDEN | 无权限 |
| 404 | NOT_FOUND | 端点或资源不存在 |
| 429 | RATE_LIMITED | 请求频率过高 |
| 500 | INTERNAL_ERROR | 内部错误 |

---

## 3. 入口模式详解

### 3.1 Single Agent（单智能体）

**端点：** `POST /api/v1/entry`

**用途：** 处理单个用户输入，由系统识别意图并路由到单个智能体或 Pipeline 执行。

**请求示例：**

```json
{
  "text": "帮我分析中美科技竞争的风险",
  "language": "zh",
  "session_id": "sess-1234567890",
  "agent": "risk_scan"
}
```

**响应示例：**

```json
{
  "status": "ok",
  "data": {
    "execution": {
      "intent": {
        "task_type": "zh_risk_scan",
        "confidence": 0.95,
        "language": "zh"
      },
      "route": {
        "pipeline": "zh_risk_scan",
        "provider": "deepseek",
        "model": "deepseek-chat"
      },
      "pipeline": {
        "output": { ... },
        "tokens": 1234,
        "latency_ms": 2345
      },
      "state_machine": {
        "current": "FINALIZE",
        "history": ["INTAKE", "ROUTING", "EXECUTION", "FINALIZE"]
      },
      "timeline": [
        {"phase": "INTAKE", "timestamp": "2025-07-03T10:00:00Z"},
        {"phase": "ROUTING", "timestamp": "2025-07-03T10:00:01Z"},
        {"phase": "EXECUTION", "timestamp": "2025-07-03T10:00:03Z"},
        {"phase": "FINALIZE", "timestamp": "2025-07-03T10:00:05Z"}
      ],
      "duration_ms": 5000,
      "trace_id": "trace-uuid-1234"
    },
    "ui_schema": {
      "title": "风险扫描报告",
      "sections": [ ... ]
    }
  },
  "message": "",
  "trace_id": "trace-uuid-1234",
  "duration_ms": 5000
}
```

---

### 3.2 Multi Agent（多智能体协作）

**端点：** `POST /api/v1/multi`

**用途：** 同时调度多个智能体协作处理一个复杂任务，每个智能体执行特定子任务，结果合并后返回。

**请求示例：**

```json
{
  "text": "全面分析中美科技竞争",
  "language": "zh",
  "tasks": [
    {"agent": "risk_scan", "task": "识别风险"},
    {"agent": "policy_brief", "task": "政策解读"},
    {"agent": "opinion_landscape", "task": "舆情分析"}
  ]
}
```

**响应示例：**

```json
{
  "status": "ok",
  "data": {
    "execution": {
      "intent": { "task_type": "multi_agent", "confidence": 0.98 },
      "route": { "pipeline": "multi_agent_orchestrator" },
      "state_machine": {
        "current": "FINALIZE",
        "history": ["INTAKE", "PARALLEL", "MERGE", "FINALIZE"]
      },
      "timeline": [ ... ],
      "duration_ms": 8000,
      "trace_id": "trace-uuid-5678"
    },
    "ui_schema": {
      "title": "多智能体协作报告",
      "tabs": [
        {"title": "风险扫描", "content": { ... }},
        {"title": "政策解读", "content": { ... }},
        {"title": "舆情分析", "content": { ... }}
      ]
    }
  },
  "trace_id": "trace-uuid-5678",
  "duration_ms": 8000
}
```

---

### 3.3 Autonomy（自治智能体）

**端点：** `POST /api/v1/autonomy`

**用途：** 智能体自主决策、自主调度、自主执行，无需用户指定具体任务或智能体。系统根据输入自动判断需要执行哪些分析。

**请求示例：**

```json
{
  "text": "最近中美关系有什么新动向？",
  "language": "zh",
  "session_id": "sess-autonomy-123"
}
```

**响应示例：**

```json
{
  "status": "ok",
  "data": {
    "execution": {
      "intent": { "task_type": "autonomy", "confidence": 0.92 },
      "route": { "pipeline": "autonomy_orchestrator" },
      "state_machine": {
        "current": "FINALIZE",
        "history": ["INTAKE", "ANALYSIS", "PLANNING", "EXECUTION", "FINALIZE"]
      },
      "timeline": [ ... ],
      "duration_ms": 12000,
      "trace_id": "trace-uuid-9999"
    },
    "ui_schema": {
      "title": "自治分析结果",
      "sections": [ ... ]
    }
  },
  "trace_id": "trace-uuid-9999",
  "duration_ms": 12000
}
```

---

## 4. 状态机定义

Entry Layer 使用状态机跟踪执行进度：

```
INTAKE → ROUTING → EXECUTION → FINALIZE
            ↓        ↓
         PARALLEL  RETRY
            ↓        ↓
         MERGE    FALLBACK
```

| 状态 | 说明 |
|------|------|
| `INTAKE` | 接收输入，参数校验 |
| `ROUTING` | 意图识别，智能体选择 |
| `PARALLEL` | 多智能体并行调度（Multi 模式） |
| `MERGE` | 多智能体结果合并（Multi 模式） |
| `EXECUTION` | 智能体/Pipeline 执行 |
| `RETRY` | 失败后重试（Fallback） |
| `FALLBACK` | 降级处理（降级到更轻量的模型） |
| `FINALIZE` | 结果格式化，输出 |

---

## 5. 认证

当前版本（V19）**暂不需要认证**。后续版本将引入 API Key 认证：

```
Authorization: Bearer <api_key>
```

---

## 6. 时序保证

| 模式 | 目标延迟 | 超时时间 |
|------|---------|---------|
| Single | < 5s | 30s |
| Multi | < 10s | 60s |
| Autonomy | < 15s | 90s |

---

## 7. 版本兼容性

| 版本 | 端点前缀 | 状态 |
|------|----------|------|
| V23 | `/v23/` | 兼容，已废弃 |
| V24 | `/api/v1/` | 当前推荐 |
| V25 | `/api/v2/` | 规划中 |

---

## 8. 相关文档

- [ENTRY_SCHEMA.md](ENTRY_SCHEMA.md) — 详细的 Schema 定义
- [ENTRY_FLOW.md](ENTRY_FLOW.md) — 数据流和状态转换图
- [API_GUIDE.md](API_GUIDE.md) — 完整 API 使用指南
