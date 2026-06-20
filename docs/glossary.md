# FZQ-AI 中文情报任务术语表 (Glossary) v9.2

> KIMI 输出 — 文档优化与提示词增强专家
> 用途：统一 4 个 Pipeline 的术语、字段命名、枚举值，确保 Prompt ↔ Schema ↔ 代码 三者一致

---

## 一、全局通用术语

| 术语 | 英文 | 定义 | 使用场景 |
|------|------|------|----------|
| 任务类型 | task_type | Pipeline 的唯一标识字符串，用于路由和日志 | 所有输出 Schema 的顶层字段 |
| 置信度 | confidence | 0.0–1.0 浮点数，表示分析结果的可靠程度 | 所有输出 Schema 的顶层字段 |
| 置信度分级 | confidence_tiers | 5 档标准：0.9–1.0(优) / 0.7–0.89(良) / 0.5–0.69(中) / 0.3–0.49(差) / 0.0–0.29(不可用) | 所有 Prompt 的置信度判定规则 |
| 证据片段 | evidence_span | 从原文中直接提取的文本片段，用于溯源和验证 | 所有需要证据支撑的子结构 |
| 降级处理 | degradation | 当输入样本不足、噪声过高或来源单一时，降低输出质量并明确标注 | 所有 Prompt 的降级策略章节 |
| 结构化 JSON | structured_json | 严格的 JSON 对象，不含 Markdown 代码块标记、不含自然语言解释 | 所有 Prompt 的输出格式要求 |

---

## 二、zh_policy_brief（政策简报）专用术语

| 术语 | 字段名 | 枚举值 | 定义 |
|------|--------|--------|------|
| 要点分类 | category | 目标 / 执行 / 适用对象 / 配套措施 / 约束 / 其他 | 政策要点的分类维度 |
| 受影响主体 | affected_entity | — | 被政策直接影响或间接影响的组织、行业、人群 |
| 主体角色 | role | 执行方 / 适用方 / 监管方 / 受益方 / 约束方 | 主体在政策中的功能定位 |
| 影响方向 | impact | 正面 / 负面 / 中性 / 混合 | 政策对主体的影响性质 |
| 时间线类型 | timeline_type | 发布 / 生效 / 试点 / 评估 / 废止 | 政策生命周期节点类型 |
| 量化目标 | quantitative_target | — | 政策中明确提出的数值化指标（如 GDP 增速、减排量） |
| 风险信号 | risk_flag | — | 政策文本中隐含的不确定因素、执行障碍或冲突空间 |
| 用户关注 | user_focus | — | 用户特别指定的议题，要求分析中必须覆盖 |

---

## 三、zh_risk_scan（风险扫描）专用术语

| 术语 | 字段名 | 枚举值 | 定义 |
|------|--------|--------|------|
| 扫描范围 | scope | 地缘 / 金融 / 舆情 / 合规 / 供应链 / 技术 | 风险扫描的维度类别 |
| 风险等级 | level | 高 / 中 / 低 / 观察 | 风险的严重程度和紧急程度 |
| 等级判定 | level_criteria | 见 Prompt 执行规则 | 高=已发生+跨行业/跨境；中=已发生+范围有限；低=信号级；观察=方向不明 |
| 证据链 | evidence | — | 支撑风险判断的原始文本片段集合 |
| 传导链 | convey_chain | — | 风险从源头到最终影响的传导路径，如 [A→B→C] |
| 受影响实体 | affected_entities | — | 直接和间接受到风险影响的主体 |
| 可执行建议 | suggested_action | — | 包含动作对象 + 动作内容 + 时间/频率的具体行动指令 |
| 监控实体 | entity_watchlist | — | 用户指定必须扫描的实体清单，扫描后强制回溯检查 |
| 整体风险等级 | overall_risk_level | 高 / 中 / 低 / 观察 | 全局风险态势的综合评估 |
| 全局行动建议 | suggested_actions | — | 针对整体风险态势的系统性行动建议列表 |

---

## 四、zh_opinion_landscape（舆情分析）专用术语

| 术语 | 字段名 | 枚举值 | 定义 |
|------|--------|--------|------|
| 舆论阵营 | cluster | — | 对议题持有相似观点的群体聚合 |
| 阵营标签 | label | 如"支持监管派"、"市场自由派" | 对阵营观点的高度概括命名 |
| 立场 | stance | 支持 / 反对 / 中性 / 分裂 | 阵营对议题的核心态度 |
| 情绪 | sentiment | 正面 / 负面 / 中性 / 混合 | 阵营表达的情绪倾向 |
| 阵营规模 | size | ≥1 整数 | 该阵营在样本中的估计人数或样本量 |
| 话语框架 | frame | 安全 / 民生 / 技术 / 民族 / 经济效率 / 公平正义 / 自由市场 / 国家发展 / 环保 / 人权 | 用于组织和解读议题的认知框架 |
| 关键意见领袖 | influencer | — | 在舆论传播中具有显著影响力的个体或账号 |
| 影响力评分 | influence_score | 0.0–1.0 | 综合互动量(40%) + 传播深度(30%) + 原创性(30%) 的加权评估 |
| 热度趋势 | heat_trend | — | 议题讨论量随时间变化的序列数据 |
| 整体立场 | overall_stance | 支持 / 反对 / 中性 / 分裂 | 全样本的立场分布综合判断 |
| 整体情绪 | overall_sentiment | 正面 / 负面 / 中性 / 分化 | 全样本的情绪分布综合判断 |
| 引用溯源 | item_id | — | representative_quotes 中必须附带的原始条目标识，实现证据可追溯 |
| 单一声浪 | single_voice | — | 当样本中>80%观点一致时，标注为单一观点分布，说明可能原因 |

---

## 五、zh_multisource_merge（多源合并）专用术语

| 术语 | 字段名 | 枚举值 | 定义 |
|------|--------|--------|------|
| 5W1H 主轴 | main_axis | — | 事件的核心事实骨架：what/when/where/who/why/how |
| 三态 | tri_state | 一致 / 分歧 / 缺失 | 5W1H 各维度在多源中的状态：一致=多源共识；分歧=多源矛盾；缺失=均未提及 |
| 视角差异 | perspective_diff | — | 不同信源对同一事件的报道差异 |
| 差异维度 | dimension | 归因 / 措辞强度 / 被引主体 / 时间线侧重 / 数据口径 | 标准化的差异分类维度 |
| 信源可靠性 | source_reliability | — | 对信源可信度、权威性、透明度的综合评估 |
| 可靠性评分 | reliability_score | 0.0–1.0 | 基于具名程度(1) + 首信源地位(2) + 权威引用(3) + 历史信誉(4) 的优先级评估 |
| 一致性评分 | consistency_score | 0.0–1.0 | 5W1H 各维度一致程度的量化映射：6一致→1.0，5一致→0.8-0.99，以此类推 |
| 缺失视角 | missing_sources | — | 事件中明显缺位的视角或信源类型（如缺少官方表态、缺少第三方数据） |
| 冲突视角 | conflict_sources | — | 事件中存在明显矛盾的视角或信源（如冲突双方官方声明） |
| 证据映射 | evidence_map | — | 全局可溯源的证据列表，用于追踪每个事实的来源 |
| 互斥信源 | mutually_exclusive | — | 已知存在立场对立或利益冲突的信源组合，其一致性评分天然受限 |

---

## 六、术语映射表（Prompt ↔ Schema ↔ 代码）

### 6.1 字段名映射一致性检查

| 概念 | Prompt 中使用的字段名 | Schema 中使用的字段名 | 状态 |
|------|----------------------|----------------------|------|
| 政策要点 | `key_points[].point` | `key_points[].point` | ✅ 一致 |
| 要点分类 | `key_points[].category` | `key_points[].category` | ✅ 一致 |
| 证据片段 | `key_points[].evidence_span` | `key_points[].evidence_span` | ✅ 一致 |
| 受影响主体 | `affected_entities[].entity` | `affected_entities[].entity` | ✅ 一致 |
| 主体角色 | `affected_entities[].role` | `affected_entities[].role` | ✅ 一致 |
| 影响方向 | `affected_entities[].impact` | `affected_entities[].impact` | ✅ 一致 |
| 时间线 | `timeline[]` | `timeline[]` | ✅ 一致 |
| 量化目标 | `quantitative_targets[]` | `quantitative_targets[]` | ✅ 一致 |
| 风险信号 | `risk_flags[]` | `risk_flags[]` | ✅ 一致 |
| 风险等级 | `level` | `level` | ✅ 一致 |
| 风险类别 | `category` | `category` | ✅ 一致 |
| 证据链 | `evidence[]` | `evidence[]` | ✅ 一致 |
| 传导链 | `convey_chain` | `convey_chain` | ✅ 一致 |
| 可执行建议 | `suggested_action` | `suggested_action` | ✅ 一致 |
| 整体风险等级 | 未提及 | `overall_risk_level` | ⚠️ 不一致 |
| 监控实体 | 提及但未输出 | `entity_watchlist` | ⚠️ 不一致 |
| 全局行动建议 | 未提及 | `suggested_actions` | ⚠️ 不一致 |
| 全局置信度 | 未提及 | `confidence` | ⚠️ 不一致 |
| 舆论阵营 | `camps[]` | `clusters[]` | ❌ 不一致 |
| 阵营ID | `camp_id` | `cluster_id` | ❌ 不一致 |
| 阵营占比 | `share` | `size` | ❌ 不一致 |
| 核心主张 | `core_claim` | `key_arguments` | ❌ 不一致 |
| 话语框架 | `frame_analysis[]` | `key_frames[]` | ❌ 不一致 |
| 框架使用者 | `used_by` | `description` | ❌ 不一致 |
| 框架效果 | `effect` | `evidence_span` | ❌ 不一致 |
| 关键节点 | `key_nodes[]` | `influencers[]` | ❌ 不一致 |
| 节点作者 | `author` | `name` | ❌ 不一致 |
| 节点阵营 | `camp` | `stance` | ❌ 不一致 |
| 热度 | `heat` | `heat_trend[]` | ❌ 不一致 |
| 整体立场 | 未提及 | `overall_stance` | ⚠️ 不一致 |
| 整体情绪 | 未提及 | `overall_sentiment` | ⚠️ 不一致 |
| 全局引用 | 未提及 | `representative_quotes` | ⚠️ 不一致 |
| 5W1H 状态 | "一致/分歧/缺失"(三态) | `status` + `value` | ⚠️ 部分一致 |
| 差异维度 | `dimension` + "其他" | `dimension`(无"其他") | ⚠️ 部分一致 |
| 缺失视角 | 未提及 | `missing_sources` | ⚠️ 不一致 |
| 冲突视角 | 未提及 | `conflict_sources` | ⚠️ 不一致 |
| 证据映射 | 未提及 | `evidence_map` | ⚠️ 不一致 |
| 信源偏向提示 | 未提及 | `bias_hint` | ⚠️ 不一致 |

---

## 七、关键发现与建议

### 7.1 一致性良好的字段（可直接使用）

- zh_policy_brief：所有字段完全对齐，无差异
- zh_risk_scan：risks 子结构完全对齐，但顶层新增 3 个字段未在 Prompt 中提及
- zh_multisource_merge：三态概念已对齐，但部分新增字段未提及

### 7.2 需要同步的字段（Prompt 与 Schema 不一致）

| 优先级 | Pipeline | 问题 | 建议操作 |
|--------|----------|------|----------|
| P0 | zh_opinion_landscape | 字段名大面积不一致（camps→clusters, frame_analysis→key_frames, key_nodes→influencers, heat→heat_trend） | 重写 Prompt 的输出格式章节，与 Schema 完全对齐 |
| P0 | zh_risk_scan | 顶层新增 overall_risk_level, entity_watchlist, suggested_actions, confidence 未在 Prompt 中要求 | 更新 Prompt 输出格式，要求输出这些字段 |
| P1 | zh_multisource_merge | 新增 missing_sources, conflict_sources, evidence_map, bias_hint 未在 Prompt 中要求 | 在 Prompt 中增加这些字段的输出说明 |
| P1 | zh_multisource_merge | Prompt 要求 dimension 包含"其他"，但 Schema 的 Literal 不包含"其他" | 同步：要么 Schema 增加"其他"，要么 Prompt 移除"其他" |
| P2 | zh_opinion_landscape | 新增 overall_stance, overall_sentiment, representative_quotes(顶层) | 在 Prompt 中增加这些字段的输出要求 |
| P2 | zh_opinion_landscape | Schema 的 stance 包含"分裂"，Prompt 的枚举为"支持/反对/中立/复杂" | 统一枚举：建议 Schema 改为"支持/反对/中立/复杂"或 Prompt 改为"分裂" |
| P2 | zh_opinion_landscape | Schema 的 sentiment 包含"分化"，Prompt 的枚举为"正面/负面/中性/混合" | 统一枚举：注意"混合"和"分化"语义差异 |

---

## 八、枚举值统一建议

### 8.1 需要统一的枚举

| 字段 | 当前 Prompt 值 | 当前 Schema 值 | 建议统一值 | 理由 |
|------|---------------|---------------|-----------|------|
| stance | 支持/反对/中立/复杂 | 支持/反对/中性/分裂 | 支持/反对/中性/复杂 | "复杂"比"分裂"更中性，"中性"与"中立"同义，选"中性"更简洁 |
| sentiment | 正面/负面/中性/混合 | 正面/负面/中性/分化 | 正面/负面/中性/混合 | "混合"已广泛使用，"分化"易与 stance 混淆 |
| dimension | 归因/措辞强度/被引主体/时间线侧重/数据口径/其他 | 归因/措辞强度/被引主体/时间线侧重/数据口径 | 归因/措辞强度/被引主体/时间线侧重/数据口径/其他 | 保留"其他"作为兜底，增强鲁棒性 |
| timeline_type | 发布/生效/试点/评估/废止 | 发布/生效/试点/评估/废止 | 发布/生效/试点/评估/废止 | ✅ 已一致，无需修改 |
| category(policy) | 目标/执行/适用对象/配套措施/约束/其他 | 目标/执行/适用对象/配套措施/约束/其他 | 目标/执行/适用对象/配套措施/约束/其他 | ✅ 已一致，无需修改 |
| role | 执行方/适用方/监管方/受益方/约束方 | 执行方/适用方/监管方/受益方/约束方 | 执行方/适用方/监管方/受益方/约束方 | ✅ 已一致，无需修改 |
| impact | 正面/负面/中性/混合 | 正面/负面/中性/混合 | 正面/负面/中性/混合 | ✅ 已一致，无需修改 |
| level | 高/中/低/观察 | 高/中/低/观察 | 高/中/低/观察 | ✅ 已一致，无需修改 |
| risk_category | 地缘/金融/舆情/合规/供应链/技术 | 地缘/金融/舆情/合规/供应链/技术/其他 | 地缘/金融/舆情/合规/供应链/技术/其他 | 保留"其他"作为兜底 |
| trend | 上升/下降/平稳/震荡 | — | 上升/下降/平稳/震荡 | Schema 中 heat_trend 的 trend 字段缺失，需补充 |

---

> 文档版本：v9.2  
> 维护者：KIMI（文档优化与提示词增强专家）  
> 最后更新：2024-XX-XX
