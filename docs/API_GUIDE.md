# API_GUIDE.md

> FZQ-AI API Usage Guide
> 版本：V19.0.0 | 状态：生产就绪
> 最后更新：2025-07-03

---

## 1. 概述

本文档提供 FZQ-AI 所有 API 端点的完整使用指南，包含请求示例、响应示例和错误处理。

**基础 URL：**

```
开发环境：http://localhost:8000
生产环境：https://api.fzq-ai.com
```

---

## 2. 健康检查

### 2.1 GET /health

检查服务健康状态。

**请求：**

```bash
curl http://localhost:8000/health
```

**响应：**

```json
{
  "status": "ok",
  "version": "19.0.0"
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `status` | `str` | `ok` 或 `error` |
| `version` | `str` | 当前 API 版本 |

---

## 3. V24 入口端点（推荐）

### 3.1 POST /api/v1/entry — 单智能体执行

**说明：** 处理单个用户输入，由系统识别意图并路由到单个智能体执行。

**请求：**

```bash
curl -X POST http://localhost:8000/api/v1/entry \
  -H "Content-Type: application/json" \
  -d '{
    "text": "帮我分析中美科技竞争的风险",
    "language": "zh",
    "session_id": "sess-1234567890",
    "agent": "risk_scan"
  }'
```

**请求体：**

| 字段 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| `text` | `str` | ✅ | — | 用户输入文本 |
| `language` | `str` | ❌ | `zh` | 语言：`zh` 或 `en` |
| `session_id` | `str` | ❌ | `null` | 会话 ID |
| `agent` | `str` | ❌ | `null` | 指定智能体名称 |

**成功响应：**

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
        "output": {
          "risks": [
            {"category": "political", "description": "技术出口管制升级", "evidence": "..."},
            {"category": "economic", "description": "供应链断裂风险", "evidence": "..."}
          ]
        },
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
      "sections": [
        {
          "type": "text",
          "title": "风险概述",
          "content": "中美科技竞争存在以下主要风险..."
        },
        {
          "type": "list",
          "title": "风险列表",
          "content": [
            {"category": "political", "description": "技术出口管制升级"},
            {"category": "economic", "description": "供应链断裂风险"}
          ]
        }
      ]
    }
  },
  "message": "",
  "trace_id": "trace-uuid-1234",
  "duration_ms": 5000
}
```

**错误响应：**

```json
{
  "status": "error",
  "data": {},
  "message": "Pipeline not found: unknown_agent",
  "trace_id": "trace-uuid-error",
  "duration_ms": 0
}
```

---

### 3.2 POST /api/v1/multi — 多智能体协作

**说明：** 同时调度多个智能体协作处理一个复杂任务。

**请求：**

```bash
curl -X POST http://localhost:8000/api/v1/multi \
  -H "Content-Type: application/json" \
  -d '{
    "text": "全面分析中美科技竞争",
    "language": "zh",
    "tasks": [
      {"agent": "risk_scan", "task": "识别风险"},
      {"agent": "policy_brief", "task": "政策解读"},
      {"agent": "opinion_landscape", "task": "舆情分析"}
    ]
  }'
```

**请求体：**

| 字段 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| `text` | `str` | ✅ | — | 用户输入文本 |
| `language` | `str` | ❌ | `zh` | 语言 |
| `tasks` | `List[Dict]` | ✅ | — | 任务列表 |

**tasks 项：**

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `agent` | `str` | ✅ | 智能体名称 |
| `task` | `str` | ✅ | 任务描述 |

**成功响应：**

```json
{
  "status": "ok",
  "data": {
    "execution": {
      "intent": {"task_type": "multi_agent", "confidence": 0.98},
      "route": {"pipeline": "multi_agent_orchestrator"},
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

### 3.3 POST /api/v1/autonomy — 自治智能体

**说明：** 智能体自主决策、自主调度、自主执行。

**请求：**

```bash
curl -X POST http://localhost:8000/api/v1/autonomy \
  -H "Content-Type: application/json" \
  -d '{
    "text": "最近中美关系有什么新动向？",
    "language": "zh",
    "session_id": "sess-autonomy-123"
  }'
```

**请求体：** 同 `/api/v1/entry`

**成功响应：**

```json
{
  "status": "ok",
  "data": {
    "execution": {
      "intent": {"task_type": "autonomy", "confidence": 0.92},
      "route": {"pipeline": "autonomy_orchestrator"},
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

## 4. V23 兼容端点（已废弃）

### 4.1 POST /v23/entry

**说明：** V23 兼容入口，保留旧系统调用。

**请求：**

```bash
curl -X POST http://localhost:8000/v23/entry \
  -H "Content-Type: application/json" \
  -d '{
    "text": "分析中美科技竞争",
    "language": "zh"
  }'
```

**注意：** 此端点将在 V25 中移除，请迁移到 `/api/v1/entry`。

---

## 5. 错误处理

### 5.1 错误响应格式

所有错误返回统一格式：

```json
{
  "status": "error",
  "data": {},
  "message": "错误描述",
  "trace_id": "trace-uuid",
  "duration_ms": 0
}
```

### 5.2 常见错误

| HTTP 状态码 | 错误信息 | 原因 | 解决方式 |
|------------|----------|------|----------|
| 400 | `text must not be empty` | 输入为空 | 提供非空 `text` |
| 400 | `language must be zh or en` | 语言不支持 | 使用 `zh` 或 `en` |
| 404 | `Pipeline not found: xxx` | 智能体不存在 | 使用正确的智能体名称 |
| 429 | `Rate limit exceeded` | 请求频率过高 | 降低请求频率 |
| 500 | `Internal server error` | 内部错误 | 查看日志，联系管理员 |
| 502 | `Provider unavailable` | LLM 提供商不可用 | 等待后重试，或更换提供商 |

---

## 6. 前端集成指南

### 6.1 React 集成

```typescript
// services/apiClient.ts
const BASE_URL = 'http://localhost:8000';

async function entry(text: string, language: string = 'zh') {
  const response = await fetch(`${BASE_URL}/api/v1/entry`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text, language }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message);
  }

  return await response.json();
}

// 使用
const result = await entry('分析中美科技竞争', 'zh');
console.log(result.data.ui_schema);
```

### 6.2 SSE 流式集成

```typescript
async function entryStream(text: string, onMessage: (msg: any) => void) {
  const response = await fetch(`${BASE_URL}/api/v1/entry`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'text/event-stream',
    },
    body: JSON.stringify({ text, language: 'zh' }),
  });

  const reader = response.body!.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    const chunk = decoder.decode(value);
    const lines = chunk.split('\n');

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const data = line.slice(6);
        if (data === '[DONE]') return;
        try {
          const parsed = JSON.parse(data);
          onMessage(parsed);
        } catch (e) {
          console.warn('Invalid SSE message:', data);
        }
      }
    }
  }
}
```

### 6.3 健康检查轮询

```typescript
useEffect(() => {
  const interval = setInterval(async () => {
    try {
      const res = await fetch('/health');
      const data = await res.json();
      setApiStatus(data.status === 'ok' ? 'connected' : 'error');
      setBackendVersion(data.version);
    } catch {
      setApiStatus('error');
    }
  }, 5000);

  return () => clearInterval(interval);
}, []);
```

---

## 7. 智能体列表

| 智能体名称 | 功能 | 示例输入 |
|------------|------|----------|
| `risk_scan` | 风险扫描 | "分析中美科技竞争的风险" |
| `policy_brief` | 政策简报 | "解读最新芯片出口管制政策" |
| `opinion_landscape` | 舆情版图 | "分析中美科技竞争的舆论立场" |
| `multisource_merge` | 多源合并 | "合并中美科技竞争的多源信息" |
| `news` | 新闻分析 | "分析今天的中美科技新闻" |
| `sentiment` | 情感分析 | "分析市场对中美科技竞争的情绪" |

---

## 8. 限流与配额

| 限制项 | 默认值 | 说明 |
|--------|--------|------|
| 单 IP 请求频率 | 60/min | 超过返回 429 |
| 单次请求超时 | 30s | Single 模式 |
| 单次请求超时 | 60s | Multi 模式 |
| 单次请求超时 | 90s | Autonomy 模式 |

---

## 9. 相关文档

- [ENTRY_PROTOCOL.md](ENTRY_PROTOCOL.md) — Entry 层协议规范
- [ENTRY_SCHEMA.md](ENTRY_SCHEMA.md) — Schema 定义
- [ENTRY_FLOW.md](ENTRY_FLOW.md) — 数据流和状态转换
