# ENTRY_SCHEMA.md

> FZQ-AI Entry Layer Schema Definitions
> 版本：V19.0.0 | 状态：生产就绪
> 最后更新：2025-07-03

---

## 1. 概述

本文档定义 Entry Layer 的所有 Pydantic Schema，用于请求校验、响应序列化和前端契约。

---

## 2. 请求 Schema

### 2.1 V24EntryRequest（单智能体/自治请求）

```python
class V24EntryRequest(BaseModel):
    text: str = Field(..., min_length=1, description="用户输入文本")
    language: str = Field("zh", pattern="^(zh|en)$", description="语言：zh 或 en")
    session_id: Optional[str] = Field(None, max_length=64, description="会话 ID")
    agent: Optional[str] = Field(None, description="指定智能体名称（可选）")
```

| 字段 | 类型 | 必需 | 约束 | 说明 |
|------|------|------|------|------|
| `text` | `str` | ✅ | `min_length=1` | 用户输入文本 |
| `language` | `str` | ❌ | `pattern="^(zh\|en)$"` | 语言，默认 `zh` |
| `session_id` | `str` | ❌ | `max_length=64` | 会话追踪 ID |
| `agent` | `str` | ❌ | — | 指定智能体（如 `risk_scan`, `policy_brief`） |

---

### 2.2 V24MultiRequest（多智能体请求）

```python
class V24MultiRequest(BaseModel):
    text: str = Field(..., description="用户输入文本")
    language: str = Field("zh", description="语言")
    tasks: List[Dict[str, Any]] = Field(..., description="多智能体任务列表")
```

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `text` | `str` | ✅ | 用户输入文本 |
| `language` | `str` | ❌ | 语言，默认 `zh` |
| `tasks` | `List[Dict]` | ✅ | 任务列表，每项包含 `agent` 和 `task` |

**tasks 示例：**

```json
[
  {"agent": "risk_scan", "task": "识别风险"},
  {"agent": "policy_brief", "task": "政策解读"}
]
```

---

### 2.3 EntryPayload（内部使用，兼容层）

```python
class EntryPayload(BaseModel):
    input: str = Field(..., description="用户输入")
    languages: List[str] = Field(["zh"], description="语言列表")
    focus_regions: List[str] = Field([], description="关注区域")
    metadata: Dict[str, Any] = Field({}, description="附加元数据")
```

---

## 3. 响应 Schema

### 3.1 V24EntryResponse（统一响应）

```python
class V24EntryResponse(BaseModel):
    status: str = Field(..., pattern="^(ok|error)$")
    data: Dict[str, Any] = Field(default_factory=dict)
    message: str = Field(default="")
    trace_id: str = Field(...)
    duration_ms: int = Field(default=0)
```

---

### 3.2 ExecutionDetail（执行详情）

```python
class ExecutionDetail(BaseModel):
    intent: Dict[str, Any] = Field(default_factory=dict)
    route: Dict[str, Any] = Field(default_factory=dict)
    pipeline: Dict[str, Any] = Field(default_factory=dict)
    model: Dict[str, Any] = Field(default_factory=dict)
    agent: Dict[str, Any] = Field(default_factory=dict)
    state_machine: StateMachine = Field(default_factory=dict)
    timeline: List[TimelineEvent] = Field(default_factory=list)
    duration_ms: int = Field(default=0)
    trace_id: str = Field(default="")
```

---

### 3.3 StateMachine（状态机）

```python
class StateMachine(BaseModel):
    current: str = Field(default="INTAKE")
    history: List[str] = Field(default_factory=list)
```

---

### 3.4 TimelineEvent（时间线事件）

```python
class TimelineEvent(BaseModel):
    phase: str = Field(...)
    timestamp: str = Field(...)
    detail: Optional[str] = Field(None)
```

**示例：**

```json
{
  "phase": "EXECUTION",
  "timestamp": "2025-07-03T10:00:03Z",
  "detail": "Pipeline zh_risk_scan completed"
}
```

---

### 3.5 UI Schema（前端渲染契约）

```python
class UISchema(BaseModel):
    title: str = Field(default="")
    subtitle: Optional[str] = Field(None)
    sections: List[Section] = Field(default_factory=list)
    tabs: Optional[List[Tab]] = Field(None)
    actions: Optional[List[Action]] = Field(None)
```

**Section 结构：**

```python
class Section(BaseModel):
    type: str = Field(..., pattern="^(text|chart|table|list|quote|code)$")
    title: str = Field(default="")
    content: Any = Field(None)
    metadata: Dict[str, Any] = Field(default_factory=dict)
```

---

## 4. 内部 Schema

### 4.1 RouteResult（路由结果）

```python
class RouteResult(BaseModel):
    data: Optional[Dict[str, Any]] = Field(None)
    ui_layout: Optional[Dict[str, Any]] = Field(None)
    ui_schema: Optional[Dict[str, Any]] = Field(None)
    debug_info: Optional[Dict[str, Any]] = Field(None)
    timeline: Optional[List[Dict]] = Field(None)
    warnings: List[str] = Field(default_factory=list)
    trace: Optional[Dict[str, Any]] = Field(None)
    status: str = Field(default="ok")
    error: Optional[str] = Field(None)
```

---

### 4.2 AgentContext（智能体上下文）

```python
class AgentContext(BaseModel):
    user_id: str = Field(default="anonymous")
    locale: str = Field(default="zh-CN")
    focus_regions: List[str] = Field(default_factory=list)
    languages: List[str] = Field(default_factory=lambda: ["zh"])
    raw_input: str = Field(default="")
    metadata: Dict[str, Any] = Field(default_factory=dict)
```

---

## 5. 枚举定义

### 5.1 TaskType（任务类型）

```python
class TaskType(str, Enum):
    ZH_POLICY_BRIEF = "zh_policy_brief"
    ZH_RISK_SCAN = "zh_risk_scan"
    ZH_OPINION_LANDSCAPE = "zh_opinion_landscape"
    ZH_MULTISOURCE_MERGE = "zh_multisource_merge"
    NEWS = "news"
    NARRATIVE = "narrative"
    RISK = "risk"
    SENTIMENT = "sentiment"
    SCENARIO = "scenario"
    DAILY_REPORT = "daily_report"
    MULTI_AGENT = "multi_agent"
    AUTONOMY = "autonomy"
    UNKNOWN = "unknown"
```

---

### 5.2 ModelProvider（模型提供商）

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

---

### 5.3 ExecutionPhase（执行阶段）

```python
class ExecutionPhase(str, Enum):
    INTAKE = "INTAKE"
    ROUTING = "ROUTING"
    PARALLEL = "PARALLEL"
    MERGE = "MERGE"
    EXECUTION = "EXECUTION"
    RETRY = "RETRY"
    FALLBACK = "FALLBACK"
    FINALIZE = "FINALIZE"
```

---

## 6. 校验规则

| 规则 | 说明 |
|------|------|
| `text` 不能为空 | 最小长度 1，空字符串返回 400 |
| `language` 只能是 `zh` 或 `en` | 其他值返回 400 |
| `session_id` 最大 64 字符 | 超长截断或返回 400 |
| `tasks` 至少包含一项 | 空列表返回 400 |

---

## 7. 版本兼容性

| 版本 | 请求 Schema | 响应 Schema | 兼容说明 |
|------|-------------|-------------|----------|
| V23 | `dict` (无 Pydantic) | `RouteResult` | 已废弃 |
| V24 | `V24EntryRequest` / `V24MultiRequest` | `V24EntryResponse` | 当前推荐 |

---

## 8. 相关文档

- [ENTRY_PROTOCOL.md](ENTRY_PROTOCOL.md) — 协议规范
- [ENTRY_FLOW.md](ENTRY_FLOW.md) — 数据流和状态转换
- [API_GUIDE.md](API_GUIDE.md) — 完整 API 使用指南
