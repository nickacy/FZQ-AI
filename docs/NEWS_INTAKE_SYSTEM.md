# FZQ-AI 新闻 Intake 系统详解

> 版本：v9 · 状态：审计准备版
> 重点：v8 新增的全球搜索、多源抓取、过滤、平衡报告

---

## 1. Intake 系统总览

```
┌────────────────────────────────────────────────────────────────────┐
│                         新闻 Intake 系统 v8                        │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  输入：topic (str)                                                  │
│        例如："AI regulation" / "中东局势" / "中美贸易"                  │
│                                                                    │
│  输出：PipelineInput（包含 items + 平衡报告）                         │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ 1. 议题扩展（expand_topic_keywords）                        │  │
│  │    ├─ 规则扩展：TOPIC_REGION_MAP → 区域变体                  │  │
│  │    └─ LLM 扩展：TOPIC_EXPANSION_V1 → 关键词列表              │  │
│  │       输出：List[str]（最多 20 个）                           │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                              │                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ 2. 区域推断（infer_regions）                                  │  │
│  │    └─ TOPIC_REGION_MAP 匹配 → RegionCode 列表                  │  │
│  │       输出：List[RegionCode]（默认 [GLOBAL]）                  │  │
│  │  2b. 语言推断（infer_languages）                             │  │
│  │    └─ Unicode 范围检测 → LanguageCode 列表                    │  │
│  │       输出：List[LanguageCode]（默认 [EN]）                    │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                              │                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ 3. 多源并行抓取（fetch_multi_source）                         │  │
│  │    ├─ RSS 源（按区域）：RSS_SOURCES_BY_REGION                 │  │
│  │    │   └─ 10+ 区域 × 3 源/区域 = 30+ 个 RSS 源               │  │
│  │    ├─ Google News RSS（按语言）                               │  │
│  │    │   └─ 6 种语言模板                                        │  │
│  │    ├─ Bing News RSS（按语言）                                 │  │
│  │    │   └─ 2 种语言模板                                        │  │
│  │    ├─ NewsAPI（如果配置了 key）                              │  │
│  │    │   └─ v2/everything endpoint                              │  │
│  │    └─ GDELT                                                   │  │
│  │        └─ GKG API                                             │  │
│  │                                                               │  │
│  │    并发控制：asyncio.Semaphore(max_fetch_concurrency=10)      │  │
│  │    失败隔离：每个源独立失败，不影响其他源                     │  │
│  │    输出：List[RawNewsItem]（最多 max_total 条）               │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                              │                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ 4. 过滤层                                                     │  │
│  │    ├─ filter_non_news()：广告/PR/非新闻过滤                    │  │
│  │    │   规则：关键词匹配（advertisement, sponsored, press      │  │
│  │    │          release 等）                                    │  │
│  │    ├─ filter_by_relevance()：LLM 相关性评分                  │  │
│  │    │   LLM Prompt: NEWS_RELEVANCE_FILTER_V1                 │  │
│  │    │   批量：每批 10 条，逐条评分 0-1                         │  │
│  │    │   过滤：低于 min_score（默认 0.5）的丢弃                   │  │
│  │    └─ 去重：SHA-256 hash（title + content[:200]）             │  │
│  │       同一新闻在不同源出现 → 只保留第一条                        │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                              │                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ 5. 平衡报告（compute_balance_report）                         │  │
│  │    ├─ region_distribution：区域分布 + 百分比                    │  │
│  │    ├─ language_distribution：语言分布 + 百分比                │  │
│  │    ├─ source_distribution：来源分布 + 百分比（Top 10）         │  │
│  │    ├─ region_balance_score：区域平衡度（0-1）                 │  │
│  │    ├─ language_balance_score：语言平衡度（0-1）               │  │
│  │    └─ source_balance_score：来源平衡度（0-1）                 │  │
│  │                                                               │  │
│  │    平衡度计算：标准差法                                       │  │
│  │    score = 1 - (std_dev / max_possible)                       │  │
│  │    1.0 = 完全平衡（各区域/语言/来源数量相等）                  │  │
│  │    0.0 = 完全不平衡（全部来自同一区域/语言/来源）             │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                              │                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ 6. 构建 PipelineInput                                         │  │
│  │    ├─ items = 过滤后的新闻列表                                │  │
│  │    ├─ target_language = options.target_language               │  │
│  │    ├─ dimensions = options.dimensions                         │  │
│  │    ├─ max_items = options.max_items                           │  │
│  │    ├─ region_filter = regions                                 │  │
│  │    └─ options.intake_balance_report = 平衡报告                │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

---

## 2. 各源抓取策略

### 2.1 RSS 源（按区域）

| 区域 | 源数 | 示例源 | 语言 | 可信度 |
|------|------|--------|------|--------|
| GLOBAL | 3 | Reuters, BBC World, Al Jazeera | EN | 0.85-0.9 |
| US | 3 | CNN, Washington Post, NYT | EN | 0.8-0.9 |
| CN | 2 | 财联社, 澎湃新闻 | ZH | 0.8-0.85 |
| EU | 2 | Politico EU, Le Monde | EN/FR | 0.85 |
| AE | 1 | Gulf News | EN | 0.8 |
| SA | 1 | Arab News | EN | 0.8 |
| JP | 1 | Japan Times | EN | 0.85 |
| BR | 1 | Globo | PT | 0.8 |
| IN | 1 | The Hindu | EN | 0.85 |
| RU | 1 | TASS | EN | 0.75 |

**总计：30+ 个 RSS 源**

### 2.2 Google News RSS（搜索驱动）

```
模板: https://news.google.com/rss/search?q={query}&hl={lang}&gl={region}&ceid={region}:{lang}

支持语言：EN, ZH, ES, FR, DE, AR
执行方式：对每个关键词（最多 3 个）× 每种语言生成 URL
抓取方式：aiohttp GET → 解析 RSS XML
```

### 2.3 Bing News RSS（搜索驱动）

```
模板: https://www.bing.com/news/search?q={query}&format=rss
支持语言：EN, ZH
执行方式：与 Google News 类似
```

### 2.4 NewsAPI

```
Endpoint: https://newsapi.org/v2/everything
参数: q={query}, language={lang}, pageSize={max}, sortBy=publishedAt, apiKey={key}
返回: JSON（articles 数组）
限制: 需要 API key，免费版有请求限制
```

### 2.5 GDELT

```
Endpoint: https://api.gdeltproject.org/api/v2/doc/doc
参数: query={query}, mode=artlist, format=json
返回: JSON（articles 数组，含 title, url, domain）
特点: 无需 API key，全球事件数据库
```

---

## 3. 过滤层详解

### 3.1 非新闻过滤（filter_non_news）

| 过滤规则 | 类型 | 说明 |
|----------|------|------|
| 关键词匹配 | 规则 | 检查 title + content 中是否包含广告/PR 关键词 |
| 关键词列表 | 黑名单 | `advertisement`, `sponsored`, `promoted`, `pr newswire`, `press release`, `advertorial`, `buy now`, `discount`, `coupon` |
| 处理方式 | 丢弃 | 匹配到任一关键词 → 丢弃该新闻 |

**局限性**：
- 简单字符串匹配，可能误杀（如新闻标题中出现 "sponsored by"）
- 无法识别伪装成新闻的软文（内容中无广告关键词）

### 3.2 相关性过滤（filter_by_relevance）

| 属性 | 值 |
|------|-----|
| 方法 | LLM 批量评分 |
| Prompt | `NEWS_RELEVANCE_FILTER_V1` |
| 批量大小 | 10 条新闻/次 |
| 评分标准 | 主题匹配度、内容深度、时效性、来源可信度 |
| 输出格式 | `{scores: [float]}`（0-1，每条 1 个分数） |
| 过滤阈值 | `min_score`（默认 0.5） |
| 保留方式 | 评分 ≥ 阈值 的保留，写入 `raw_metadata["relevance_score"]` |

**局限性**：
- 批量评分牺牲了精度（LLM 只能浅层阅读）
- 10 条/次如果新闻量很大（1000+），成本不可忽略
- 评分标准较主观，不同 LLM 可能给出不同结果

### 3.3 去重（SHA-256 hash）

| 属性 | 值 |
|------|-----|
| 方法 | SHA-256 哈希 |
| 输入 | `title + content[:200]` |
| 输出 | 16 位十六进制字符串（前 16 位） |
| 碰撞概率 | 极低（16 位 = 64 bit，碰撞概率 ≈ 1/2^64） |
| 局限性 | 同一新闻标题不同（如翻译差异）会视为不同新闻 |

**优化建议**：
- 可考虑使用内容相似度（如余弦相似度）替代精确匹配
- 可考虑提取关键词指纹进行模糊去重

---

## 4. 平衡报告详解

### 4.1 区域平衡报告

```json
{
  "region_distribution": {
    "us": {"count": 35, "percentage": 35.0},
    "cn": {"count": 25, "percentage": 25.0},
    "eu": {"count": 20, "percentage": 20.0},
    "global": {"count": 20, "percentage": 20.0}
  },
  "region_balance_score": 0.92
}
```

### 4.2 语言平衡报告

```json
{
  "language_distribution": {
    "en": {"count": 70, "percentage": 70.0},
    "zh": {"count": 20, "percentage": 20.0},
    "fr": {"count": 10, "percentage": 10.0}
  },
  "language_balance_score": 0.65
}
```

### 4.3 来源平衡报告

```json
{
  "source_distribution": {
    "Reuters": {"count": 15, "percentage": 15.0},
    "BBC World": {"count": 12, "percentage": 12.0},
    "CNN": {"count": 10, "percentage": 10.0}
  },
  "source_balance_score": 0.78
}
```

### 4.4 平衡度评分计算

```
公式: score = 1 - (std_dev / max_possible)

其中:
  n = 类别数（如区域数）
  total = 总新闻数
  ideal = total / n（理想均匀分布时每类数量）
  std_dev = sqrt(Σ(v - ideal)^2 / n)（实际分布的标准差）
  max_possible = ideal * (n - 1) / sqrt(n)（最大可能标准差）

示例:
  100 条新闻，4 个区域
  理想分布: 每区域 25 条
  实际分布: [35, 25, 20, 20]
  std_dev = sqrt((100 + 0 + 25 + 25) / 4) = sqrt(37.5) ≈ 6.12
  max_possible = 25 * 3 / 2 = 37.5
  score = 1 - (6.12 / 37.5) ≈ 0.84
```

---

## 5. 规则 vs LLM 使用点

| 步骤 | 规则为主 | LLM 辅助 | 说明 |
|------|---------|----------|------|
| 议题扩展 | ✅ 规则优先 | ✅ LLM 增强 | 规则扩展（TOPIC_REGION_MAP）+ LLM 扩展（TOPIC_EXPANSION_V1） |
| 区域推断 | ✅ 规则 | ❌ 模板未启用 | 当前使用 TOPIC_REGION_MAP，未使用 LLM |
| 语言推断 | ✅ 规则 | ❌ 模板未启用 | 当前使用 Unicode 检测，未使用 LLM |
| 多源抓取 | ✅ 规则 | ❌ 无 LLM | 纯 HTTP 请求，无 LLM 参与 |
| 非新闻过滤 | ✅ 规则 | ❌ 无 LLM | 关键词黑名单匹配 |
| 相关性过滤 | ❌ 规则 | ✅ LLM | 使用 NEWS_RELEVANCE_FILTER_V1 批量评分 |
| 去重 | ✅ 规则 | ❌ 无 LLM | SHA-256 哈希 |
| 平衡报告 | ✅ 规则 | ❌ 无 LLM | 纯数学计算 |

---

## 6. DeepSeek 优化重点（建议审计方向）

| 优先级 | 优化点 | 当前问题 | 建议方向 |
|--------|--------|----------|----------|
| 🔴 高 | 相关性过滤 | 批量评分精度低 | 改用单条评分或规则+LLM 双层过滤 |
| 🔴 高 | 去重 | 精确匹配，无法处理变体 | 引入语义相似度（如 embeddings） |
| 🟡 中 | 非新闻过滤 | 关键词匹配太粗糙 | 训练分类器或引入 LLM 单条判断 |
| 🟡 中 | 区域推断 | 仅 16 个关键词映射 | 引入 LLM 分类（模板已定义但未启用） |
| 🟡 中 | 语言推断 | 仅 Unicode 检测 | 引入 LLM 分类（模板已定义但未启用） |
| 🟢 低 | 平衡报告 | 仅计算，不干预 | 根据平衡度自动调整抓取策略 |

---

*文档结束 — 配合 `REGION_LANGUAGE_LOGIC.md` 和 `METRICS_AND_OBSERVABILITY.md` 阅读*
