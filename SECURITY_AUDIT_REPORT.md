# FZQ-AI 项目安全审计与日志污染审计报告

> **审计时间**: 2026-06-30  
> **审计路径**: `C:/Users/nicka/FZQ-AI-WORKSPACE/FZQ-AI`  
> **审计范围**: 安全审计、日志污染、测试文件、数据文件

---

## 1. 安全审计

### 1.1 严重（Critical）: `.env` 文件包含真实 API 密钥

| 行号 | 变量名 | 密钥值（已脱敏） | 风险等级 |
|------|--------|----------------|---------|
| 57 | `ZHIPU_API_KEY` | `0b706b5...VnDUi6MGZnVCQftr` | 🔴 Critical |
| 58 | `api_key` | `ce44eefe...hcOlSS8ur5R8YNOk` | 🔴 Critical |
| 76 | `OpenAI API key` | `sk-proj-2Nz2...bqyFylnYA` | 🔴 Critical |

**详情分析**:
- `.env` 文件第 57 行包含 **智谱（Zhipu）真实 API Key**（`0b706b572a1d4b7e84c649df4ab558a2.VnDUi6MGZnVCQftr`）
- `.env` 文件第 58 行包含另一个 **智谱真实 API Key**（`ce44eefe7f174fa9b6c3838dab4067ec.hcOlSS8ur5R8YNOk`）
- `.env` 文件第 76 行包含 **OpenAI 真实 API Key**（`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`）
- `.env` 文件被 `.gitignore` 正确忽略（Git 历史中无 `.env` 提交记录），但密钥仍存在于本地文件中
- **密钥泄露范围**：经全局搜索，这些密钥仅存在于 `.env` 文件中，未扩散到其他 `.py`, `.yaml`, `.json`, `.md` 文件

**建议措施**:
1. 立即在对应平台（OpenAI, Zhipu）撤销/轮换这些 API Key
2. 从 `.env` 文件中删除这些真实密钥，替换为 `your_key_here` 或留空
3. 将 `.env` 加入 `.gitignore`（已存在）
4. 使用 `.env.local` 或密钥管理服务（如 AWS Secrets Manager, Azure Key Vault）存储真实密钥

---

### 1.2 中（Medium）: `.env` 文件格式问题

- 第 28 行：`kimi-code=irm https://code.kimi.com/kimi-code/install.ps1 | iex` — 这是一个 PowerShell 安装脚本，不应放在 `.env` 文件中
- 第 76 行：`OpenAI API key: sk-proj-...` — 变量名格式错误（含空格），应该是 `OPENAI_API_KEY=...`
- 第 23 行：`API_KEY=your_key_here` — 变量名过于通用，无法区分是哪个服务的 API Key

---

### 1.3 中（Medium）: `.env.example` 不完整

`.env.example` 文件（19 行）相比 `.env` 文件（90 行）严重不完整。缺失的变量包括：

| 缺失变量 | 在 `.env` 中的行号 | 说明 |
|----------|-------------------|------|
| `ENVIRONMENT` | 5 | 环境标识（dev/prod） |
| `DEBUG` | 6 | 调试开关 |
| `LLM_MODELS` | 33 | LLM 模型配置（JSON） |
| `API_KEY` | 23 | miniMaxi 通用 API Key |
| `ZHIPU_API_KEY` | 57 | 智谱 API Key |
| `ZHIPU_BASE_URL` | 62 | 智谱 Base URL |
| `ZHIPU_MODEL` | 69 | 智谱模型 |
| `MOONSHOT_API_KEY` | 82 | Moonshot API Key |
| `MOONSHOT_MODEL` | 83 | Moonshot 模型 |
| `GROQ_API_KEY` | 88 | Groq API Key |
| `GROQ_MODEL` | 89 | Groq 模型 |
| `kimi-code` | 28 | Kimi Code 安装命令（不应在 .env） |

**建议**: 更新 `.env.example` 使其与 `.env` 的变量结构保持一致，同时移除不应在 `.env` 中的条目（如 `kimi-code`）。

---

### 1.4 低（Low）: 代码中无硬编码 API 密钥

经全局搜索（`grep -rn "sk-"` 和 `grep -rn "api_key\|API_KEY\|secret\|password\|token"`）：

- ✅ Python 源码中没有硬编码的 `sk-` 格式 API 密钥
- ✅ 所有 API Key 读取均通过 `os.getenv()` 或环境变量配置
- ✅ `src/fzq_ai/config/__init__.py:68` 有验证逻辑：`if not val or val.startswith("your-") or val.startswith("sk-your-")` — 用于检测占位符密钥
- ⚠️ `src/fzq_ai/clients/model_client.py` 中的 `api_key` 参数通过构造函数传入，运行时从环境变量解析，设计合理

---

### 1.5 低（Low）: `src/fzq_ai/utils/key_health.py` 审计

| 项目 | 状态 | 说明 |
|------|------|------|
| 硬编码密钥 | ✅ 无 | 全部使用 `os.getenv()` |
| 密钥泄露 | ✅ 无 | 不会记录或打印密钥 |
| API 测试调用 | ⚠️ 注意 | 会向真实 API 发送 "ping" 测试消息，消耗 token |
| 超时设置 | ✅ 有 | DeepSeek 检查设置了 10 秒超时 |
| 异常处理 | ✅ 有 | 各检查方法均有 try/except |

**风险**: 如果环境变量配置了真实密钥，运行 `key_health.py` 会产生实际的 API 调用费用。建议添加 `--dry-run` 模式或明确的测试开关。

---

### 1.6 日志文件敏感数据检查

#### `fzqai_metrics.jsonl`（根目录，11,327 字节，约 50 条记录）

```json
{"timestamp": 1782724002.498994, "datetime": "2026-06-29T09:06:42.498994+00:00", "name": "provider_call", "duration_ms": 10120.866775512695, "extra": {"provider": "deepseek", "model": "deepseek-chat", "success": true}}
```

- ✅ 不包含 API Key 或用户身份信息
- ✅ 不包含敏感内容（仅 provider 名称、模型、耗时、成功状态）
- ⚠️ 包含时间戳和 API 调用历史（可推断使用模式）

#### `fzqai_token_log.jsonl`（根目录，13,465 字节，约 50 条记录）

```json
{"timestamp": 1782724002.587919, "datetime": "2026-06-29T09:06:42.587919+00:00", "provider": "deepseek", "model": "deepseek-chat", "task_type": "zh_multisource_merge", "prompt_tokens": 16, "completion_tokens": 807, "total_tokens": 823, "cost_usd": 0.001646, "trace_id": null, "meta": {}}
```

- ✅ 不包含 API Key、用户身份、消息内容
- ✅ 仅包含 token 用量和费用（cost_usd）
- ⚠️ 包含 task_type（可推断业务场景）

**结论**: 日志文件本身不含敏感数据泄露风险，但**不应放在根目录**。

---

## 2. 日志文件污染审计

### 2.1 严重（Critical）: 日志文件在根目录

| 文件 | 大小 | 位置 | 应移动位置 | 状态 |
|------|------|------|-----------|------|
| `fzqai_metrics.jsonl` | 11,327 B | 根目录 | `data/logs/` | ❌ 污染 |
| `fzqai_token_log.jsonl` | 13,465 B | 根目录 | `data/logs/` | ❌ 污染 |

**问题**:
- `data/logs/` 目录已存在但**完全为空**（仅 `__init__.py`）
- 两个日志文件在根目录造成项目结构混乱
- 根目录已包含过多文件（50+ 个文件/目录）

**建议**:
1. 将 `fzqai_metrics.jsonl` → `data/logs/metrics.jsonl`
2. 将 `fzqai_token_log.jsonl` → `data/logs/token_usage.jsonl`
3. 更新代码中写入日志的路径引用
4. 在 `.gitignore` 中添加 `data/logs/*.jsonl`（如日志不应提交）

---

### 2.2 额外发现: 根目录杂项文件

| 文件 | 大小 | 说明 | 建议 |
|------|------|------|------|
| `stdout.txt` | 0 B | 空文件 | 删除或归档 |
| `stderr.txt` | 363 B | 错误日志 | 移至 `data/logs/` |
| `test_report.pdf` | 79,663 B | 旧测试报告 | 移至 `docs/` 或删除 |
| `project_structure_clean.txt` | 54,826 B | 项目结构文档 | 可保留或移至 `docs/` |
| `README_legacy.md` | 20,659 B | 旧版 README | 删除或归档至 `archive/` |
| `app_legacy.py` | 3,737 B | 旧版应用 | 删除或归档至 `archive/` |
| `FZQ_AI_Daily_Run.xml` | 1,635 B | 定时任务配置 | 可保留或移至 `configs/` |

---

## 3. 测试文件审计

### 3.1 测试文件统计

| 类别 | 数量 | 行数 | 说明 |
|------|------|------|------|
| 有内容的测试文件 | 7 个 | 688 行 | 实际测试代码 |
| 空测试文件（0 字节） | 16 个 | 0 行 | 仅占位 |
| 总计 | 23 个 | 688 行 | 测试覆盖率有限 |

### 3.2 有内容的测试文件（7 个）

| 文件 | 行数 | 测试类型 | 质量评估 |
|------|------|----------|---------|
| `test_api.py` | 124 | Schema/Config 导入测试 | ⭐⭐⭐ 基础但完整 |
| `test_schemas.py` | 167 | Schema 模型单元测试 | ⭐⭐⭐ 枚举、字段验证 |
| `test_pipelines.py` | 146 | Mock Pipeline 异步测试 | ⭐⭐⭐ 使用 Mock 对象 |
| `test_llm_router.py` | 95 | LLM 路由测试 | ⭐⭐ 基础路由逻辑 |
| `test_orchestrator.py` | 67 | 编排器测试 | ⭐⭐ 较简单 |
| `test_formatter.py` | 71 | 格式化器测试 | ⭐⭐ 基础测试 |
| `conftest.py` | 18 | pytest 配置 | ⭐⭐ 配置简单 |

**测试文件特点**:
- 测试主要使用 **Mock 对象**（如 `MockNewsPipeline`, `MockRiskPipeline`），未测试真实 LLM 调用
- 测试覆盖 Schema 验证、枚举值、默认值等基础功能
- 没有集成测试或 E2E 测试（除 `test_e2e/` 中有一个小文件）
- 没有真实 API 调用的测试（这是合理的，避免消耗费用）

### 3.3 空测试文件（16 个）⚠️

以下文件为 **0 字节空文件**，无实际测试内容：

```
tests/test_audit/test_prompt_linter.py
tests/test_models/test_deepseek.py
tests/test_models/test_kimi.py
tests/test_models/test_qwen.py
tests/test_pipelines/test_opinion.py
tests/test_pipelines/test_policy.py
tests/test_pipelines/test_risk.py
tests/test_recovery/test_error_classifier.py
tests/test_recovery/test_fallback_policy.py
tests/test_recovery/test_repair_policy.py
tests/test_recovery/test_retry_policy.py
tests/test_router/test_router_v1.py
tests/test_router/test_task_selector.py
tests/test_self_healing/test_field_filler.py
tests/test_self_healing/test_schema_repairer.py
tests/test_self_healing/test_structure_fixer.py
```

**建议**:
1. 删除空测试文件或添加基础测试内容
2. 如果使用 `pytest` 运行测试，空文件不会报错但会造成目录混乱

---

## 4. 数据文件审计

### 4.1 `_test_wl.json`（根目录，63 字节）

```json
[
  "global conflict",
  "US election",
  "energy market"
]
```

- ✅ 内容：3 个测试关键词，无敏感信息
- ⚠️ 位置：应在 `data/` 或 `tests/fixtures/` 目录

### 4.2 `watchlist.json`（根目录，88 字节）

```json
[
  "global conflict",
  "US election 2028",
  "energy market",
  "AI regulation"
]
```

- ✅ 内容：4 个监控关键词，无敏感信息
- ⚠️ 位置：应在 `data/` 或 `configs/` 目录

### 4.3 `data/` 目录内容

| 路径 | 大小 | 说明 | 敏感数据 |
|------|------|------|---------|
| `data/intel_store.sqlite` | 3,514,368 B | SQLite 数据库 | 未检查内容 |
| `data/cache/news_cache.json` | 211,580 B | 新闻缓存 | 未检查（可能含新闻内容） |
| `data/cache/risk_cache.json` | 168,230 B | 风险缓存 | 未检查 |
| `data/cache/summary_cache.json` | 95,389 B | 摘要缓存 | 未检查 |
| `data/news/*.json` | ~10-50 KB | 按日期新闻文件 | 未检查 |
| `data/logs/` | 0 B | 空日志目录 | N/A |
| `data/backups/` | 0 B | 空备份目录 | N/A |
| `data/output/` | 0 B | 空输出目录 | N/A |

---

## 5. 综合风险评估

| 风险等级 | 数量 | 项目 |
|----------|------|------|
| 🔴 Critical | 3 | `.env` 中 3 个真实 API 密钥泄露 |
| 🟡 Medium | 2 | `.env.example` 不完整；`.env` 格式问题 |
| 🟡 Medium | 2 | 日志文件在根目录；大量空测试文件 |
| 🟢 Low | 4 | 根目录杂项文件；key_health.py 会消耗 token；测试仅覆盖 Mock 对象；data 目录部分文件未检查 |

---

## 6. 修复建议清单

### 立即执行（Critical）
1. [ ] 在 OpenAI 和 Zhipu 平台撤销/轮换以下 API Key:
   - `sk-proj-2Nz2UX3YKRX2T_zHB0lPJNZi5w2Lj...` (OpenAI)
   - `0b706b572a1d4b7e84c649df4ab558a2.VnDUi6MGZnVCQftr` (Zhipu)
   - `ce44eefe7f174fa9b6c3838dab4067ec.hcOlSS8ur5R8YNOk` (Zhipu)
2. [ ] 从 `.env` 删除真实密钥，替换为 `your_key_here`
3. [ ] 修复 `.env` 第 76 行格式：`OPENAI_API_KEY=your_key_here`（而非 `OpenAI API key: ...`）

### 短期执行（1-2 天）
4. [ ] 将 `fzqai_metrics.jsonl` → `data/logs/metrics.jsonl`
5. [ ] 将 `fzqai_token_log.jsonl` → `data/logs/token_usage.jsonl`
6. [ ] 将 `watchlist.json` → `data/watchlist.json`
7. [ ] 将 `_test_wl.json` → `tests/fixtures/test_watchlist.json`
8. [ ] 更新 `.env.example` 包含所有必要变量（参考 `.env` 但不包含真实值）
9. [ ] 删除或填充 16 个空测试文件

### 中期执行（1 周内）
10. [ ] 审查 `data/intel_store.sqlite` 内容是否含敏感数据
11. [ ] 为 `key_health.py` 添加 `--dry-run` 模式
12. [ ] 在 `.gitignore` 中添加 `data/logs/*.jsonl`
13. [ ] 归档或删除 `app_legacy.py`, `README_legacy.md`, `test_report.pdf`
14. [ ] 将 `stdout.txt`, `stderr.txt` 移至 `data/logs/`

---

> **报告生成**: 由安全审计工具自动生成  
> **建议**: 请立即处理 Critical 级别的 API 密钥泄露问题
