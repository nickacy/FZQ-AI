Phase C — 鲁棒性 & 架构修正（1–2 周）
C1：统一 Pipeline 同步/异步模型

引入 BasePipeline Protocol（run_async + run 包装）。

NewsPipeline / RiskPipeline / SentimentPipeline 全部改为 async 内核。

TaskOrchestrator 全部改为 await pipeline.run_async(...)。

C2：修复 NewsPipeline 的多次 fetch

fetch_all_news() 只调用一次，结果缓存。

_compose() 只消费缓存。

C3：修复 RiskPipeline 的 query bug

统一命名 & 补测试。

C4：统一 Pipeline 返回 ServiceResult

News / Risk / Sentiment / Scenario 全链路用 ServiceResult。

PoliticalIntelScenario 改为只消费 ServiceResult。

Phase D — 结构化输出 & 模型插件化（2–4 周）
D1：LLM 结构化输出强化

所有结构化任务统一用 JSON mode + Pydantic Schema。

去掉 text.split("```") 这种脆弱解析。

D2：IntelStore 合并

统一到 fzq_ai/storage/intel_store.py。

补迁移逻辑 & 测试。

D3：Provider Registry / 模型插件系统

Provider 声明能力（语言 / 上下文 / 任务）。

Router 动态选择模型。

为 KIMI / MiniMax / DeepSeek / OpenAI 预留插槽。