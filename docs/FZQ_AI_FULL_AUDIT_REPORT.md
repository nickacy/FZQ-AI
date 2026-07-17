# FZQ-AI 全文专业审计总报告（Full-Project Professional Audit）

**审计日期**：2026-07-17 ｜ **审计基线**：HEAD `91cdf303`，工作区 clean
**审计方式**：10 名专项审计员并行只读审计（安全 / 结构 / LLM 与客户端 / 流水线与编排 / 基础设施 / Schema 一致性 / 测试体系 / 文档与版本 / 前端 / 入口与部署），覆盖 src 210 个 .py、tests 31 个 .py、frontend-react 54 个源文件及全部配置/文档；关键发现均经运行时实测复现（import 抽查、`call_llm` 实测、pytest 基线、`tsc --noEmit`、PathFinder 实测等），无臆测项。

---

## 一、执行摘要与健康评分

### 综合健康评分：**42 / 100**

| 维度 | 得分 | 主要扣分原因 |
|------|------|--------------|
| 安全 | 4/10 | git 历史中明文真实 OpenAI 密钥；无 .dockerignore 致 .env/.git 烤进镜像；运行时数据文件仍被 git 跟踪 |
| 可运行性 | 3/10 | 主链路 8+ 处 100% 必败点（LLM router 契约脱节、/api/zh/* 全灭、/v23/entry 永败、CLI 必崩、Docker 启动必崩、前端白屏） |
| 结构 | 4/10 | 约 30% 文件零引用（59 个孤儿模块）；pipeline/pipelines、config.py/config 包、双 ModelClient、双 RouteResult、6 套 metrics、3 套缓存并存 |
| 测试 | 5/10 | pytest 320 passed/1 error 表面健康，但 21.6%（69 个）跑 src 内 mock 适配层；16 个测试被收集错误阻断；唯一在线 API 测试假绿 |
| 文档 | 5/10 | 版本元数据停滞 24.0.0 而 CHANGELOG 已到 V24.3.5；README 指标失真（352 文件/54 模块等）；docs/README 索引 7 个不存在文件 |
| 前端 | 3/10 | tsc 错误阻断构建、路由未接线 9 页面不可达、静态资源路径 404 白屏、Docker 下连不上后端 |

### 发现统计（去重后）

| 级别 | 数量 | 含义 |
|------|------|------|
| **P0** | 26 | 阻断性：运行错误、导入失败、契约脱节、安全泄露 |
| **P1** | 47 | 高：死代码群、重复实现、配置/版本漂移、测试失真、文档脱节 |
| **P2** | 90+ | 中：配置卫生、命名不一致、注释乱码、小优化项 |

**一句话结论**：项目骨架先进、文档体系庞大，但存在"测试全绿而主链路全断"的系统性失真——mock 适配层掩盖了 LLM 路由、zh 管线、v23 入口、CLI、Docker、前端共 6 条通路的 100% 必败缺陷；同时约 1/3 代码为多轮重构遗留的死代码，需一次彻底的"接通 + 清扫"治理。

---

## 二、P0 阻断性问题清单（26 项，去重合并）

### A. 安全（2 项）

| # | 问题 | 证据 | 修复 |
|---|------|------|------|
| P0-A1 | **git 历史中明文粘贴真实 OpenAI 密钥**：历史审计报告 `SECURITY_AUDIT_REPORT.md`（根目录及 docs/audits/）将 `.env:76` 的完整 `sk-proj-` 密钥原样写入报告并提交，29+ 个提交可恢复 | 提交 `e812e948`、`2908e3ad` 等（仅列号不贴值） | ① 立即吊销/轮换该密钥（用户操作）；② `git filter-repo`/BFG 重写历史并强推（不可逆，需确认）；③ 今后报告只记"位置+变量名+前 4 位" |
| P0-A2 | **无 `.dockerignore`**：`Dockerfile:13 COPY . /app` 将 `.env`（将来含真实密钥）、`.git/`（含 P0-A1 历史）、`data/`（3.5MB sqlite）烤进镜像层 | 项目根无 `.dockerignore`；docker-compose.yml 同时 `env_file: .env` | 新增 `.dockerignore`（.env*/.git/data/node_modules/__pycache__/.venv*）；已构建镜像视为泄露 |

### B. 导入与打包（7 项）

| # | 问题 | 证据 | 修复 |
|---|------|------|------|
| P0-B1 | **`fzq_ai.glm` 整包 ImportError**：`glm/extractor.py:21-22` `from src.fzq_ai.config import GlobalSettings` —— `GlobalSettings` 全库不存在、`src.` 前缀非法、且 `settings` 定义后从未使用（死代码）。连锁：① zh 管线 GLM/Doubao/Kimi 三阶段静默失效（`_zh_pipeline.py:132` `civ` 未绑定 → NameError 被吞）；② `tests/test_glm_extractor.py` 16 个测试收集阻断；③ `tests/test_doubao.py` 受牵连 | 实测 `import fzq_ai.glm` 报 ImportError；pytest 收集实测 | 删除 extractor.py:21-22 两行死代码；`_zh_pipeline.py` 将 `civ = kwargs.get("civilization")` 前置到 try 块外 |
| P0-B2 | `pipeline/`（单数）无 `__init__.py`：`find_packages` 不收录，pip 安装后 `from fzq_ai.pipeline.feedback_loop import FeedbackLoop`（`_zh_pipeline.py:205,221`）必 ImportError 且被宽 except 吞掉 | `src/fzq_ai/pipeline/` 仅 feedback_loop.py；`setup.py:7` | 补 `__init__.py`（Batch B 再决定并入 pipelines/） |
| P0-B3 | `ui/` 无 `__init__.py`：`main.py:7`、`orchestrator/unified_orchestrator_v24.py:11` 顶层导入，pip 安装后启动即崩 | `src/fzq_ai/ui/` 仅 web_app.py、ui_schema.py | 补 `__init__.py` |
| P0-B4 | `llm/clients/` 无 `__init__.py`：`llm/providers/deepseek_provider.py:11` 顶层导入 | `src/fzq_ai/llm/clients/` 6 个 *_api.py | 补 `__init__.py` |
| P0-B5 | **包数据全未声明**：`config/config.yaml`、`config/global_settings.yaml`、`manifest.json`、`prompts/zh/*.txt`（5 个）、`prompts/system/kimi_v9.3.txt`、`prompts/daily_report_generate.j2` 安装后全部丢失 | pyproject/setup.py 均无 package-data | pyproject 增加 `[tool.setuptools.package-data]` |
| P0-B6 | **Docker 后端启动必崩**：仅 `pip install -r requirements.txt`，无 `pip install -e .` / PYTHONPATH；CMD `uvicorn src.fzq_ai.api.app:app` 可解析但 `app.py` 内 `from fzq_ai...` 绝对导入必 ModuleNotFoundError → crash-loop | `Dockerfile:13,17,26` | Dockerfile 增加 `pip install -e .`（或 ENV PYTHONPATH=/app/src） |
| P0-B7 | **CI pytest 在干净 runner 必挂**：workflow 缺 `pip install -e .`；`tests/conftest.py:2` 收集期即 `from fzq_ai...`；仅 4/31 测试文件自助插 sys.path。本地能跑只因做过 editable 安装 | `.github/workflows/python.yml`、`daily-report.yml` | 两个 workflow 的 Install 步骤追加 `pip install -e .` |

### C. 运行链路（10 项）

| # | 问题 | 证据 | 修复 |
|---|------|------|------|
| P0-C1 | **`llm/router.py` 调用不存在的 `run_sync`**：7 处 `XxxProvider(...).run_sync`，但全部 Provider 只有 `async run()` → 经 `call_llm` 的 LLM 调用 100% 失败（实测 5 模型全灭）；更糟：`core/llm_executor.py:70` 重试耗尽后**静默返回伪造文本** `"[Fake LLM output...]"` 冒充真实结果。影响 _zh_pipeline/risk/sentiment/narrative/refinement/scenario/daily_report/news 全部管道 | `router.py:209-228`；实测 `await call_llm('deepseek-chat','hello')` 全失败 | 统一契约：`_call_one_model` 改为直接 `await provider.run(req)`，删除 run_in_executor；删除 llm_executor 的 fake 输出兜底（改为抛错） |
| P0-C2 | **OpenAI/Gemini Provider `client=None` 必败**：构造器允许 `client=None`，`run()` 内 `await None.chat(req)` 必 AttributeError；router 正是无 client 实例化 | `openai_provider.py:22-24,33`、`gemini_provider.py:22-24,33` | 构造器内自建默认 client（参照 DeepSeekProvider）或 client is None 时 raise |
| P0-C3 | **`/api/zh/*` 四端点全灭**：`core/task_router.py:148` 兜底 `await pipeline.run_async(user_input)` 位置参数调用，而 zh 管道签名 `run_async(self, **kwargs)` → 必 TypeError 被吞，永远 `success=False`（HTTP 200）。测试只断言结构不断言 `execution.success` 故全绿 | 实测复现 TypeError；`zh_endpoints.py:82-99` | 兜底改 `await pipeline.run_async(text=user_input)`（或 content=）；测试补 `assert execution.success is True` |
| P0-C4 | **`TaskOrchestrator.run` 双重 bug**：`:61` 对 `@dataclass` IntentResult 调 `.model_dump()`（不存在）；`:64` 未 await 异步 `router.route()` → 任何调用永远失败。另 `_resolve_pipeline` 恒 None 死桩 | 实测复现 AttributeError | `dataclasses.asdict(intent)`；run 改 async/await；删除或实现 _resolve_pipeline |
| P0-C5 | **`news_pipeline.py:37` 缺 await**：`articles = fetch_all_news(query)`（async 函数未 await）→ `'coroutine' object is not subscriptable` 必崩；且把 str 传给 `List[str]` 签名、Article 类型标注与 List[str] 实际不符 | 实测复现 + RuntimeWarning | 补 await；统一入参/元素类型 |
| P0-C6 | **`/v23/entry` 永远 UNKNOWN 失败**：同步 handler 调用异步 `orchestrator.run()` 未 await；返回值是 dict 而非 RouteResult，`hasattr(to_dict)` 恒 False → 永远失败分支。API_GUIDE.md:281 仍在教用户调用 | `api/entry.py:18-22`；实测复现 | handler 改 async + await；按 dict 取字段重写响应逻辑 |
| P0-C7 | **CLI 必崩**：`cli/agent.py:48` `await orch.orchestrate()` —— 该方法不存在且对同步方法 await | `task_orchestrator.py` 仅有 run() | 改为 `orch.run(text=...)`（配合 P0-C4 修复后） |
| P0-C8 | **`store/event_extractor.py` 导入即 NameError**：`:12` 用 `@dataclass` 但从未 import；另含变量先用后定义、extract() 恒返回 None、Article 字段名错误（title vs title_original）、空 Event 传参必 TypeError 共 4 层 bug | `store/event_extractor.py:12-42` | 当前零引用——Batch B 整体删除或完整重写 |
| P0-C9 | **`intel_store.save_bundle` 永远失败**：`:60` 用 `dataclasses.asdict()` 序列化 pydantic BaseModel → 必 TypeError 被 except 吞成 warning，**持久化静默失效数据全丢** | `store/intel_store.py:60,69-70` 实测 asdict 行为 | 改 `bundle.model_dump(mode="json")`；失败默认抛错而非 warning |
| P0-C10 | **`intel_store(":memory:")` 模式必崩**：`_get_conn()` 每次新建独立内存库，建表连接随即销毁 → 后续查询 `no such table` 崩溃 | `intel_store.py:33-37,88-92` | :memory: 模式持有单一持久连接或共享缓存 URI |
| P0-C11 | **zh 四管道 prompt 从不注入用户输入**：`_zh_pipeline.py:147-151` `.format(intent=..., context=...)` 对含字面 JSON 花括号的模板必 KeyError → 静默回退为静态模板 → **LLM 只收到任务说明书，用户输入从未出现**，输出只能凭空编造 | 实测 `.format()` 抛 KeyError；prompts/zh/*.txt 无 {intent}/{context} 占位符 | 模板改 `string.Template`（`$content` 语法与字面 JSON 不冲突）并在 4 个 .txt 末尾追加输入区块；`_zh_pipeline` 改 `safe_substitute` |
| P0-C12 | **Minimax 校验对象错误（假阳性）**：`_zh_pipeline.py:294-311` 把流水线包装 dict 喂给只认 8 字段的 StrictSchema → repair 丢弃全部真实内容产出**空 Schema 且 valid=True**，监控显示"校验通过"而分析内容全丢；Phase 2 反馈随之失效。另 run() 与 run_async() 重复执行 _minimax_pass | 实测：含真实 parsed 内容的 result → 全空 8 字段 | 校验目标改为 `result["parsed"]` 或另建 PipelineResultSchema；删重复调用 |

### D. 前端（4 项）

| # | 问题 | 证据 | 修复 |
|---|------|------|------|
| P0-D1 | **tsc 类型错误阻断构建**：`state/agentState.ts:42` `Property 'agents' does not exist on type 'V24Response'` → `npm run build`（tsc && vite build）与前端 Docker 构建同步阻断 | 实测 `tsc --noEmit` exit 2 | `apiClient.post<{ agents: Agent[] }>('/agents/list', {})` |
| P0-D2 | **路由未接线，9 个页面不可达**：`main.tsx` 只渲染 `<AppShell/>`，`app/routes.tsx` 的 AppRoutes 全项目 0 引用；页面区永远空白；导航用 `<a href>` 整页刷新丢状态 | `main.tsx:11`、`AppShell.tsx:26`；vite 产物 tree-shake 后不含任何页面 | main.tsx 接线 `<AppRoutes/>`（AppShell 作布局 Route）；导航改 `<Link>` |
| P0-D3 | **生产静态资源 404 白屏**：后端把 dist 挂 `/static`，而 dist/index.html 引用绝对路径 `/assets/*`；无 SPA fallback | `api/app.py:90-105`、`vite.config.ts` 无 base | vite `base:'/static/'` 或后端改挂 `app.mount("/", StaticFiles(html=True))`（API 路由之后） |
| P0-D4 | **Docker 下前端永远连不上后端**：compose 注入 `VITE_API_BASE_URL` 但 apiClient 硬编码 `/api/v1` 且从不读 env；`vite preview` 无代理；容器主机名浏览器不可解析 | `docker-compose.yml:34`、`apiClient.ts:5` | apiClient 改 `import.meta.env.VITE_API_BASE_URL ?? '/api/v1'`，或弃独立前端容器由后端托管 dist |

### E. 文档/入门（3 项）

| # | 问题 | 证据 | 修复 |
|---|------|------|------|
| P0-E1 | **README 快速开始在全新环境必 ImportError**：Quick Start 仅 `pip install -r requirements.txt` → `python main.py` / `pytest`，但 src-layout 未 `pip install -e .`、无 pythonpath 配置 → `ModuleNotFoundError: No module named 'fzq_ai'`（新开发者路径 100% 踩中） | README.md:49-55,97；实测无 PYTHONPATH 解释器 | Quick Start 增加 `pip install -e .`；pytest.ini 加 `pythonpath = ["src"]` |
| P0-E2 | **Makefile 完全不可用**：recipe 行为 4 空格而非 TAB + 全文件 CRLF → GNU make 每个 target 报 `missing separator` | `cat -A Makefile` 实测 | 改 TAB + LF；run-backend 前置 install 依赖 |
| P0-C3-关联 | （见 P0-C3）测试断言缺口是 `/api/zh/*` 全灭长期隐身的原因之一 | `tests/api/test_zh_endpoints.py` | 补 success 断言 |

---

## 三、P1 高严重度问题（47 项，按主题归并）

### 1. 版本与发布漂移（4 项）
- **P1-1 版本元数据停滞**：VERSION.txt/pyproject/setup.py/api app.py:40,202/manifest.json/前端 package.json 八处均 24.0.0，CHANGELOG 已到 **V24.3.5**，minimax docstring 自认 24.3.x——历史"版本统一"状态已回退。`config/__init__.py:119` BUILD_TIME 硬编码 "2026-07-03" 停滞。
- **P1-2 `config/__init__.py:43` `_PROJECT_ROOT` 算错一级**（解析到 src/ 而非仓库根）→ VERSION.txt/config.json 永远找不到、静默回退；根 `config.json` 带 UTF-8 BOM，路径修好后 `json.load` 仍会炸（需 `utf-8-sig`）。
- **P1-3 editable 安装元数据 0.1.0 与声明 24.0.0 漂移**；无锁定 venv。
- **P1-4 CHANGELOG 编号错乱**：V24.3.1→V24.3.3 升序混排、引用不存在的 V24.3.2、V24.3.0 排在 V24.3.5 后。

### 2. 死代码与重复结构（14 项）
- **P1-5 `config.py` 被 `config/` 包永久遮蔽**（PathFinder 实测包优先），自称"向后兼容"实为不可达死代码；且并存 4 套配置（config 包 dict 式 / modern_config dataclass 式 / global_settings / core/config.py）。
- **P1-6 `modern_config.py:11,108-122` 偷调 `load_dotenv()`**，与 `config/__init__.py:10-11`"统一移至入口"声明直接矛盾。
- **P1-7 死代码包群**（grep 零引用实测）：`logging/`（且 logger.py import 时清 root handlers，误导入即破坏现有日志）、`cache/`、`quality/`（minimax.validate_and_fix 是 `return data` 假实现）、`store/`（除自引用）、`registry/orchestrators.py|pipelines.py`（第三处同名 PipelineRegistry）、`cli/`、`monitor/`、`entry/`（0 引用 shim）、`models/`（完全空目录）、`api/v24_formatter.py`、`core/prompts.py`（481 行）、`core/config.py`、`core/llm_executor.py`（导入期副作用）、`pipelines/errors.py`、`pipelines/refinement_pipeline.py`（死链核心）。
- **P1-8 59 个孤儿模块**（AST 引用图判定）：含 `llm/clients/{gemini,glm,kimi,openai,qwen}_api.py` 5 个 V19 客户端、`llm/model_client.py`、`prompts/` 下 14 个英文模板模块、`schemas/metrics.py`、`schemas/test_adapter/` 6 文件、`store/event_extractor.py|trend_engine.py`、`utils/{concurrency,helpers,json_formatter,key_health,metrics,translation}.py` 等。
- **P1-9 双 `ModelClient` 同名并存**：`clients/model_client.py`（活跃，同步 chat+异步 chat_async）vs `llm/model_client.py`（死代码）；接口互矛盾，极易导错包。
- **P1-10 双 `RouteResult` 同名不同契约**：`schemas/route.py`（status/data/...）vs `core/task_router.py:17`（success/task_type/...）；文档 ENTRY_SCHEMA.md 是第三种形状。
- **P1-11 `schemas/__init__.py` 双 `PipelineInput` 导入遮蔽**（pipeline_input.py 版被 core_models 版覆盖成幽灵定义，字段完全不同）。
- **P1-12 metrics 6 套并存**：活 3（metrics.py/metrics_writer/metrics_store）+ 死 3（recorder.py 第二个同名 MetricsRecorder/metrics_v2/cost_model）+ utils/metrics.py 第四套 + schemas/metrics.py 第五套。
- **P1-13 LLM 缓存 3-4 套并存**（cache.py / cache_redis.py 导入期硬连 localhost / enhanced_cache.py / cache/news_cache.py），接口各异。
- **P1-14 prompts 双 `PromptTemplate`**（template.py vs base/template.py 实现相同）、`utils/prompt_loader.py` vs `prompts/template_loader.py` 双份加载器；retry 三套；`run_concurrent` 双份；`setup_logging` 双份格式不同。
- **P1-15 archive/ 内部已腐坏**：ui_backup 导入已不存在的 `fzq_ai.ui.theme/i18n`；全仓 0 引用但 31 个文件被 git 跟踪。
- **P1-16 前端死代码群（约 20 文件）**：双入口双 App（index.tsx/App.tsx/NavigationBar.tsx）、routes.tsx 及连带组件群、entryService.ts（143 行封装 0 调用方）、AgentsPage/HistoryPage/FavoritesPage 硬编码 mock 数据。
- **P1-17 英文 prompts/ 子树整体孤儿化**且与流水线内联英文模板双向漂移（中英不一致）；`prompt_templates_v24.py` 自称"MUST use"却零调用方，且其 zh 模板与 zh schema 字段**零重合**——任何按治理声明接入者 100% 校验失败。
- **P1-18 tests 结构混乱**：tests/api vs test_api.py vs test_api/（空壳）三套；4 个空壳目录残留 10 个已删测试的 .pyc（audit/recovery/self-healing/router-v1v2/e2e 五领域测试曾丢失）；tests/utils/ 两个 mock 文件无引用。

### 3. 代码契约与错误处理（9 项）
- **P1-19 三家提供商及 Provider 层返回类型/错误处理不统一**：哨兵 dict / 抛异常 / 静默默认值 / **错误文本冒充正常 output**（glm/qwen/kimi provider `except: content = str(data)` 把 API 错误体当正文返回）四种机制并存。
- **P1-20 `clients/model_client.py` 双重致命**：失败时 `return json.dumps({"error":...})` 与成功同型（调用方无法区分成败）；**Gemini/Doubao 凭据误路由**——_BASE_URLS 无此两家，base_url 落默认 api.openai.com，GEMINI/DOUABO_API_KEY 会随 Authorization 头发往 OpenAI 端点。
- **P1-21 `LLMRouter.call()` 静默丢弃调用方指定的 provider/model/api_key/base_url**（Router.run 只读 prompt/task_type/language）；`router.py:303` error 分支为死代码。
- **P1-22 Provider 能力声明双份矛盾**：provider_registry.py（4 家含 minimax 但无 MinimaxProvider 类）vs provider_capabilities.py（6 家无 minimax）；`model_selector.py:23` 遇未知 provider 直接 KeyError。
- **P1-23 环境变量命名三套不一致**：GLM_API_KEY vs ZHIPU_API_KEY；QWEN_API_KEY vs DASHSCOPE_API_KEY（连 API 协议都不同）；KIMI_API_KEY vs MOONSHOT_API_KEY。另代码读 `NEWSAPI_KEY` 而 .env 定义 `NEWSAPI_API_KEY` → key 永远加载不到。
- **P1-24 `monitor/token_monitor.py:48-53` 对 dict 用 getattr** → 预算上限（daily_cap 等）永远取硬编码默认值，**预算控制形同虚设有超支风险**（活代码，被 3 个 provider 引用）。
- **P1-25 `utils/error_handler.py` circuit_breaker 对 async 函数失效**：同步 `cb.call()` 包装协程 → 函数体从不执行、熔断无感知、调用方拿到未 await 的协程；`safe_execute` 同类语义错误。
- **P1-26 `utils/concurrency.py:24-30` `run_async()` 在异步上下文必抛 RuntimeError**（恰恰在最需要它的场景必崩）。
- **P1-27 TaskRouter 路由覆盖不全**：8 种意图仅 4 个 zh 有映射，daily_report/narrative/risk/news 落 fallback 被**静默改派 zh_policy_brief**。

### 4. Schema/提示词一致性（8 项）
- **P1-28 GLM→DeepSeek→Minimax 链路两套字段方言 + facts 三种形状**：`policy_signals/trend_signals`（方言 A）在 repair 中被整体静默丢弃；facts 在 对象列表/分组字典/JSON 字符串间漂移；风险条目 description/evidence 因键名不匹配（`text` vs `description`）被替换为空串。
- **P1-29 `prompts/system/kimi_v9.3.txt` 与实现完全脱节**：声称的输入字段（policy_signals/error_report）不存在，要求的 7 段输出与 `ExplanationResult` 零重合。
- **P1-30 两套 FeedbackLoop 键约定互不兼容**（点号键 vs 下划线键）→ "结构闭环"断裂，doubao/kimi 的 feedback_context 恒 None；FeedbackLoop→KimiInterpreter 键名第三套错位（consistency_score/suggestions 永不提供）。
- **P1-31 test_adapter（mock 全集）与 core_models 已漂移**：缺 GLM/KIMI/QWEN 枚举、缺 detected_language/relevance_score/confidence 等 v10 演进字段；`tests/test_schemas.py` 28 个测试全跑 mock，真实 schema 0 覆盖。
- **P1-32 `docs/ENTRY_SCHEMA.md` 与代码大面积漂移**：6 个文档模型代码不存在；响应形状、UISchema、RouteResult、StateMachine 词汇、AgentContext 全部不符。
- **P1-33 `docs/SCHEMAS_MAP.md` 漂移**：枚举 5 值 vs 实际 8 值（且与 ENTRY_SCHEMA.md 自相矛盾）、6 处默认值不符、仅覆盖 core_models 一个模块。
- **P1-34 `system_zh_intel.txt` 与任务提示矛盾**：要求 Markdown 摘要 vs 任务提示"仅输出 JSON"；降级字段 status/risk_flags 在 schema 中不存在；且 `_zh_pipeline.py:44` 另有硬编码系统提示，两份并存。
- **P1-35 zh 降级规则违反 schema 约束**：`zh_multisource_merge.txt:130` 要求 sources<2 时 score=-1.0，但 schema `score ge=0.0` → 按 prompt 降级必触发 ValidationError。

### 5. 测试失真（4 项）
- **P1-36 21.6%（69/320）通过测试跑 src 内 mock 适配层**：test_llm_router（13)/test_schemas（28)/test_pipelines（17)/test_orchestrator（11）全部只测 Mock；真实 llm.router/pipelines.base/schemas/orchestrator 直接测试为 0——这是全部 P0-C 类缺陷长期隐身的根因；coverage omit 还排除 test_adapter。
- **P1-37 唯一在线 API 测试假绿**：`test_glm_basic` 断言 `isinstance(output, str)`，而 ModelClient 失败也返回 str → 失败照样"通过"；且默认套件每次运行发真实付费 API 请求。
- **P1-38 pytest 配置双份漂移**：pytest.ini（生效）vs pyproject `[tool.pytest.ini_options]`（死配置）filterwarnings 不一致。
- **P1-39 conftest fixture 3/4 闲置**；provider 命名双轨（"glm-5.2" vs "glm"）。

### 6. 前端结构（3 项，P0 之外）
- **P1-40 CSS 变量体系断裂**：两套变量名（--accent/--border vs --card-bg/--border-color），唯一定义点在死代码 index.tsx 内联 style 里 → live 应用全部 var(--*) 回退初始值，视觉破损。
- **P1-41 `npm run lint` 不可用**（无 eslint 配置但装了全套依赖）。
- **P1-42 前端契约小漂移**：`systemVersion: '19.0.0'` 硬编码过期；响应契约缺 version 字段致版本显示链路全断；同语义三种请求字段名（input/query/text）靠后端别名兜底。

### 7. 部署与运维（5 项）
- **P1-43 已被 .gitignore 忽略的运行时数据仍被 git 跟踪**：`data/logs/fzqai_token_log.jsonl`（含模型用量/成本元数据）、`data/cache/*`（约 474KB）、`data/news/*`、`src/fzq_ai/logs/fzq_ai_20260703.jsonl`。
- **P1-44 运行时日志写入源码包内部**：`utils/logger.py:69-70,192-193` 默认 log_dir = `src/fzq_ai/logs/`（docstring 谎称项目根 logs/）→ 日志打进 wheel；需改默认路径 + git rm --cached。
- **P1-45 `.gitignore` 缺 `.env.*` 变体规则**；`:50` `fzq_ai/data/backups/` 为永不命中的陈旧规则。
- **P1-46 CI 从不运行 lint/类型检查/安全扫描**（本地 pre-commit 有 black/ruff/mypy/bandit，CI 脱节——P0-C 类错误本可被 mypy/ruff 拦截）；pre-commit 无密钥扫描钩子（gitleaks/detect-secrets）。
- **P1-47 frontend-react 无 .dockerignore**（Windows node_modules 覆盖容器 Linux 版，原生模块大概率损坏）；docker-compose `version:"3.9"` 已废弃、`./configs` 死挂载（zh_tasks.yaml 全库无人读取）。

---

## 四、P2 中严重度问题（90+ 项，精选代表）

- **配置卫生**：`.env.example` 缺 `API_KEY`/`api_key` 两变量（且 `.env:58` 小写孤儿行疑似手误）；`.env:11` 与 `:76` OPENAI_API_KEY 重复定义；`ENV` vs `ENVIRONMENT` 双轨；`.env` 末尾无换行；`DEEPSEEK_KEY` vs `DEEPSEEK_API_KEY` 并存无说明。
- **依赖卫生**：requirements.txt 孤儿 pin（pydantic-settings、httpx 全库零导入）；pytest 三件套混入生产依赖；streamlit/plotly 仅 archive 使用；`uvicorn==0.30.0` 与 `uvicorn[standard]` 冗余。
- **打包双配置**：setup.py vs pyproject（pydantic 约束冲突 `>=2.0` vs `>=2.7,<3.0`）；`src.fzq_ai` vs `fzq_ai` 双导入路径（Dockerfile/Makefile 用前者，其余用后者）。
- **异常吞咽**：全库 20+ 处 `except Exception: pass`（config 3 处使版本静默回退、memory 2 处、tracing 3 处、minimax repair 3 处、_zh_pipeline 2 处纯静默无日志等）。
- **注释/字符串乱码（mojibake）**：`news_fetcher.py:2`、`news_pipeline.py`（**输出字符串**含 `"## 馃摪"` 乱码 emoji）、`daily_report_pipeline.py`（**LLM prompt 模板内** `"2鈥? concise paragraphs"` 乱码会直接发给模型）、`narrative_pipeline.py`、`risk_pipeline.py` 等，含 `\x3f` 字节已不可逆，需按 UTF-8 重写。
- **类型标注**：`model: str = None` 等隐式 Optional 8+ 处（pyright/mypy strict 下报错）。
- **小契约漂移**：minimax "13 字段" docstring 实为 8；`registry.py:15` `_DEFAULT: str = None`；4 个管道均 `set_default=True` 默认语义混乱；`base.py:84` 只查本类不查 MRO；三名别名 ZhMultisourceMerge*；`zh_endpoints.py` 未导入 Any/未用 classify/覆盖 task_type 使分类形同虚设。
- **README 失真**：首行 git 培训残留；"352 Python files"（实测 210）、"7 Supported LLMs"（实测 6，Kimi/Moonshot 重复计数）、"54 Civilization modules"（实测 3）；模块地图列已删除的 tools/；三文档三个测试数（182/165/333 vs 实测 308+）。
- **run_web/run_api 名不副实**：main.py 不解析 argv，`web`/`api` 为死参数。
- **前端小项**：WorkspacePage 硬编码英文绕过 i18n；service-worker.js 惰性缓存隐患；manifest 未链接。
- **文档细节**：docs/README 索引 7 个不存在审计文件；docs/ARCHITECTURE_OVERVIEW.md 自称与根目录一致实则不同；DEEPSEEK_AUDIT_TASKS.md 头部 V19 陈旧；V24_POLISH 日期疑 2025 笔误；archive/audits 空目录而约 16 份历史报告被删除未归档。
- **rss_sources.yaml:19,61** 两处明文 HTTP 源（数据完整性风险）。

---

## 五、历史审计回归检查（抽样 14 项）

| 结论 | 数量 | 明细 |
|------|------|------|
| ✅ 在位 | 8 | Dockerfile CMD、compose healthcheck、requirements-dev、前端 apiClient 修复、intel//longcat//llm/orchestrator/ 未复活、llm/router_v2/ 等 5 目录未复活、老 unified_orchestrator 未复活、domain 模型 Pydantic 化 |
| ⚠️ 部分在位/正当重建 | 2 | entry/ 已填 shim 但 0 引用；interpreter/ 被正当重建（有测试有引用）但 CHANGELOG 无记录 |
| ❌ 回退/从未达标 | 4 | **版本统一状态回退**（CHANGELOG 已 V24.3.5）；"cache/logging/store/monitor/cli 均有引用"结论不实（实测仅 clients 有）；API response_model 覆盖率仍 3/18（三次审计标记未修）；commit message 治理未落实（最近 3 条全叫 "pull"） |

---

## 六、修复路线图

### Batch A — P0 无争议修复（立即执行，代码编辑类，可 git 回退）
1. glm/extractor.py 删 21-22 死导入；_zh_pipeline.py civ 前置（P0-B1）
2. 补 pipeline/、ui/、llm/clients/ 三个 `__init__.py`；pyproject 补 package-data（P0-B2~B5）
3. llm/router.py 统一 `await provider.run(req)` 契约；删除 llm_executor fake 输出兜底；OpenAI/Gemini Provider 构造期自建 client 或 raise（P0-C1/C2）
4. task_router._call_pipeline 兜底改关键字调用；测试补 success 断言（P0-C3）
5. task_orchestrator：asdict + async/await + 删死桩；cli/agent.py 改调 run()（P0-C4/C7）
6. news_pipeline 补 await + 类型适配（P0-C5）
7. api/entry.py v23 端点改 async + 按 dict 取字段（P0-C6）
8. intel_store：model_dump 序列化 + :memory: 单连接 + 失败抛错（P0-C9/C10）
9. zh 模板改 string.Template + 4 个 .txt 补输入区块；_zh_pipeline safe_substitute；Minimax 校验对象改为 parsed（P0-C11/C12）
10. 前端：agentState 泛型修复、路由接线、vite base/后端托管二选一、apiClient 读 env（P0-D1~D4）
11. .dockerignore（根 + frontend-react）；Dockerfile pip install -e .；CI 两 workflow 补 editable 安装；Makefile TAB+LF；README Quick Start + pytest.ini pythonpath（P0-A2/B6/B7/E1/E2）

### Batch B — 结构清理（删除类，**需用户确认**）
- 删除死代码包/文件：config.py、logging/、cache/、quality/、store/（或修复后接入）、registry/{orchestrators,pipelines}.py、models/ 空目录、entry/ shim、cli/（或修复后保留）、monitor/（确认后）、59 个孤儿模块中的确认死亡子集、pipeline/（并入 pipelines/）、前端死代码约 20 文件、archive/ 处理（移出仓库或标注快照）、tests 空壳目录与 __pycache__
- `git rm -r --cached data/logs data/cache data/news src/fzq_ai/logs`（保留本地文件）
- 收敛：单一日志入口、单一 metrics 入口、单一缓存接口、双 ModelClient/RouteResult/PipelineInput 改名合并

### Batch C — 安全根治（**需用户行动与确认**）
- 用户立即吊销/轮换 git 历史中的 OpenAI `sk-proj-` 密钥（视为已泄露）
- `git filter-repo` 重写历史移除密钥文件 + 顺带剔除 node_modules/venv 历史 → 强推 → 协作者重新克隆（不可逆）
- pre-commit 增加 gitleaks/detect-secrets 钩子

### Batch D — 版本与文档写实
- 版本 bump 至 24.3.5（VERSION.txt 单一事实源 + 其余 7 处同步 + `__init__.py` 补 `__version__`）
- README 重写（删培训行、更正指标 210 文件/6 LLM/3 模块、模块地图重绘、Quick Start、端点表补 /api/v1 系）
- CHANGELOG 重排降序 + 补 V24.3.6（本次审计修复）条目
- docs/README 审计索引重写；ENTRY_SCHEMA.md/SCHEMAS_MAP.md 按代码重新生成；response_model 补全

### 验收标准
- `pytest`：320+16 全部可收集并通过，0 error 0 项目警告
- `python -c "import fzq_ai.glm"`、`call_llm` 冒烟、TestClient 打 `/api/zh/*` 与 `/v23/entry` 断言 `success=True`
- `npm run build` 通过；`pip install .` 后 `python -c "import fzq_ai.ui.web_app, fzq_ai.pipeline.feedback_loop"` 通过
- Docker 构建后 `/health` 冒烟通过

---

## 七、对齐良好项（正面确认）

- 当前 .env 全部为占位符、从未入 git；全工作树硬编码密钥/内网 IP 扫描 0 命中；CI 注入假密钥做法正确
- `zh_policy_brief.txt ↔ ZhPolicyBriefOutput` 字段/枚举/长度约束完全一致；`glm_system.txt ↔ GLMRawMaterial`、`doubao_system.txt ↔ StrictSchema` 对齐良好
- Minimax 三级 JSON 解析容错、Doubao `_error` 哨兵设计合格；`pipelines/base.py` 三种返回值归一化完整；`interpreter/` 模块实现干净
- Pydantic V2 用法规范（全 src 仅 v24_routes.py:122 一处带守卫的 `.dict()`）；无裸露 `except:`；无循环导入（除 P0-B1 外全部包可导入）
- 前端 i18n en/zh 各 68 key 零单边缺失；前端调用的 5 个端点后端全部存在；dist 未被 git 跟踪且不过期
- USAGE_GUIDE.md 全部代码引用逐条验证有效；README 端点表与 app.py 实际路由全部吻合

---

*报告生成：Kimi Orchestrator + 10 名专项审计员（agent-swarm 并行审计）*
*各专项原始报告（含完整证据链）留存于审计会话工作区。*
