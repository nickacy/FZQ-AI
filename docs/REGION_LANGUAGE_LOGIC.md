# FZQ-AI 区域与语言推断逻辑

> 版本：V19 · 状态：生产就绪
> 重点：topic → region / language 的推断机制，规则为主 vs LLM 增强

---

## 1. 区域推断（Topic → Region）

### 1.1 当前实现：规则映射

```python
TOPIC_REGION_MAP: Dict[str, List[RegionCode]] = {
    "china": [RegionCode.CN, RegionCode.HK, RegionCode.TW],
    "us": [RegionCode.US, RegionCode.CA],
    "europe": [RegionCode.EU, RegionCode.UK, RegionCode.DE, RegionCode.FR],
    "middle east": [RegionCode.AE, RegionCode.SA],
    "asia": [RegionCode.JP, RegionCode.KR, RegionCode.IN, RegionCode.SG, ...],
    "africa": [RegionCode.AE],
    "latin america": [RegionCode.BR, RegionCode.MX],
    "russia": [RegionCode.RU],
    "ukraine": [RegionCode.EU, RegionCode.RU],
    "taiwan": [RegionCode.TW, RegionCode.CN, RegionCode.US],
    "gaza": [RegionCode.AE, RegionCode.SA],
    "oil": [RegionCode.AE, RegionCode.SA, RegionCode.RU, RegionCode.US],
    "ai": [RegionCode.US, RegionCode.CN, RegionCode.EU, RegionCode.JP],
    "trade": [RegionCode.US, RegionCode.CN, RegionCode.EU, RegionCode.SG, RegionCode.HK],
    "climate": [RegionCode.GLOBAL],
    "election": [RegionCode.US, RegionCode.EU, RegionCode.CN],
}
```

### 1.2 推断逻辑

```python
def infer_regions(self, topic: str) -> List[RegionCode]:
    regions = []
    lower_topic = topic.lower()
    
    for key, mapped_regions in TOPIC_REGION_MAP.items():
        if key in lower_topic or lower_topic in key:
            for r in mapped_regions:
                if r not in regions:
                    regions.append(r)
    
    if not regions:
        regions = [RegionCode.GLOBAL]  # 默认全球
    
    return regions
```

### 1.3 匹配规则

| 匹配类型 | 示例 | 结果 |
|----------|------|------|
| 关键词包含 topic | "china" in "China economy" | [CN, HK, TW] |
| topic 包含关键词 | "China-US trade war" contains "trade" | [US, CN, EU, SG, HK] |
| 无匹配 | "Mars exploration" | [GLOBAL] |

### 1.4 局限性

| 问题 | 示例 | 影响 |
|------|------|------|
| 关键词覆盖不全 | "Semiconductor export ban" → 无匹配 → GLOBAL | 可能遗漏 CN/US 相关源 |
| 同义词未覆盖 | "AI governance" → 无匹配（只有 "ai"） | 可能遗漏 |
| 多义词歧义 | "Apple" → 水果 vs 公司 → 无匹配 | 无影响（返回 GLOBAL） |
| 隐式地理关联 | "TSMC" → 未映射到 TW | 可能遗漏 TW 源 |
| 新兴议题 | "Generative AI regulation" → 无匹配 | 返回 GLOBAL |

### 1.5 LLM 增强（已定义但未启用）

```
模板: TOPIC_REGION_CLASSIFICATION_V1
输入: topic (str)
输出: {regions: [str], primary_region: str, confidence: float}

优势:
- 不受关键词覆盖限制
- 可处理同义词、隐式关联
- 可推断新兴议题的地理关联

未启用原因:
- 规则映射已覆盖 80% 常见议题
- LLM 调用有成本，每 topic 1 次
- 可未来作为规则 fallback 启用
```

---

## 2. 语言推断（Topic → Language）

### 2.1 当前实现：Unicode 范围检测

```python
def infer_languages(self, topic: str) -> List[LanguageCode]:
    languages = [LanguageCode.EN]  # 默认英文
    
    if any('\u4e00' <= ch <= '\u9fff' for ch in topic):
        languages.append(LanguageCode.ZH)
    if any('\u0600' <= ch <= '\u06ff' for ch in topic):
        languages.append(LanguageCode.AR)
    if any('\u0400' <= ch <= '\u04ff' for ch in topic):
        languages.append(LanguageCode.RU)
    if any('\u3040' <= ch <= '\u30ff' for ch in topic):
        languages.append(LanguageCode.JA)
    if any('\uac00' <= ch <= '\ud7af' for ch in topic):
        languages.append(LanguageCode.KO)
    
    return deduplicate(languages)
```

### 2.2 检测范围

| 语言 | Unicode 范围 | 检测方法 | 示例 |
|------|-------------|----------|------|
| 中文 | \u4e00-\u9fff | 逐字符检查 | "中国经济" → ZH |
| 阿拉伯语 | \u0600-\u06ff | 逐字符检查 | "الشرق الأوسط" → AR |
| 俄语 | \u0400-\u04ff | 逐字符检查 | "Россия" → RU |
| 日语 | \u3040-\u30ff | 逐字符检查 | "日本経済" → JA |
| 韩语 | \uac00-\ud7af | 逐字符检查 | "한국" → KO |
| 其他 | 无匹配 | 默认 EN | "AI regulation" → EN |

### 2.3 局限性

| 问题 | 示例 | 影响 |
|------|------|------|
| 仅检测输入 topic 的语言 | topic="AI regulation" → 仅 EN | 未搜索 ZH 源（"人工智能监管"） |
| 无法处理拼音 | topic="Zhongguo" → 无中文字符 → EN | 可能遗漏中文源 |
| 无法处理混合语言 | topic="China AI 人工智能" → ZH | 正确检测，但可能漏掉其他语言 |
| 无法推断目标语言 | 用户搜索 "俄乌冲突" → 仅检测 ZH | 未搜索 RU 源（"Россия-Украина"） |
| 新兴语言 | 越南语、泰语等未检测 | 无法覆盖 |

### 2.4 优化方向

```
当前：infer_languages("AI regulation")
  → 检测：无特殊字符 → [EN]
  → 搜索：仅 EN 源
  → 遗漏：中文 "人工智能监管"、日文 "AI規制" 等

理想：infer_languages("AI regulation")
  → 检测：EN → [EN]
  → LLM 扩展：识别该议题在多国语言中的重要性 → [EN, ZH, JA, DE]
  → 搜索：EN + ZH + JA + DE 源
  → 覆盖：更全面
```

### 2.5 LLM 增强（已定义但未启用）

```
模板: TOPIC_LANGUAGE_CLASSIFICATION_V1
输入: topic (str)
输出: {original_language: str, search_languages: [str], confidence: float}

优势:
- 不受 Unicode 范围限制
- 可推断跨语言相关性（如 "AI regulation" 应搜索 ZH/DE）
- 可处理拼音、音译

未启用原因:
- Unicode 检测已覆盖 90% 直接语言检测
- 跨语言推断需要领域知识，LLM 可能不准确
- 可未来作为增强选项启用
```

---

## 3. Translator 语言检测（v8）

### 3.1 检测引擎

```python
LANGUAGE_PATTERNS: Dict[LanguageCode, re.Pattern] = {
    LanguageCode.EN: re.compile(r"[A-Za-z]"),
    LanguageCode.ZH: re.compile(r"[\u4e00-\u9fff]"),
    LanguageCode.JA: re.compile(r"[\u3040-\u30ff\u31f0-\u31ff]"),
    LanguageCode.KO: re.compile(r"[\uac00-\ud7af]"),
    LanguageCode.AR: re.compile(r"[\u0600-\u06ff]"),
    LanguageCode.RU: re.compile(r"[\u0400-\u04ff]"),
    LanguageCode.FR: re.compile(r"[\u00e0-\u00ff]"),
    LanguageCode.ES: re.compile(r"[\u00e1\u00e9\u00ed\u00f3\u00fa\u00f1\u00d1]"),
    LanguageCode.DE: re.compile(r"[\u00e4\u00f6\u00fc\u00df]"),
    LanguageCode.PT: re.compile(r"[\u00e7\u00e3\u00f5]"),
    LanguageCode.IT: re.compile(r"[\u00e0\u00e8\u00e9\u00ec\u00f2\u00f9]"),
    LanguageCode.VI: re.compile(r"[\u00e0\u00e1\u1ea1...\u0111]"),
    LanguageCode.TH: re.compile(r"[\u0e00-\u0e7f]"),
    LanguageCode.ID: re.compile(r"[\u00e9\u00e8]"),
    LanguageCode.TR: re.compile(r"[\u011f\u011f\u015f\u0131\u00f6\u00e7\u00fc]"),
    LanguageCode.PL: re.compile(r"[\u0105\u0107\u0119...\u017c]"),
    LanguageCode.NL: re.compile(r"[\u00e9\u00eb\u00ef\u00f6\u00fc]"),
}
```

**覆盖 17 种语言**

### 3.2 检测逻辑

```python
def detect_language(text: str) -> LanguageCode:
    if not text:
        return LanguageCode.EN
    
    scores = {}
    for lang, pattern in LANGUAGE_PATTERNS.items():
        count = len(pattern.findall(text))
        if count > 0:
            scores[lang] = count
    
    if not scores:
        return LanguageCode.EN
    
    best = max(scores, key=lambda k: scores[k])
    
    # 中日文混淆处理：如果日文最多但中文也有相当比例，优先中文
    if best == LanguageCode.JA and LanguageCode.ZH in scores:
        if scores[LanguageCode.ZH] > scores[LanguageCode.JA] * 0.5:
            return LanguageCode.ZH
    
    return best
```

### 3.3 检测精度

| 场景 | 精度 | 说明 |
|------|------|------|
| 纯中文文本 | ✅ 高 | 中文字符独占，无混淆 |
| 纯日文文本 | ✅ 高 | 平假名/片假名独占 |
| 中日混合 | ⚠️ 中 | 日文汉字 vs 中文汉字，需特殊处理 |
| 纯阿拉伯文 | ✅ 高 | 阿拉伯文独占 |
| 纯俄文 | ✅ 高 | 西里尔文独占 |
| 纯英文 | ✅ 高 | 英文字母独占 |
| 带音符的欧洲语言 | ⚠️ 中 | 法语/西班牙语/德语等有重叠字符 |
| 拉丁语系混合 | ⚠️ 低 | 法语/西班牙语/意大利文等共享大量拉丁字符 |
| 拼音/罗马化 | ❌ 低 | "Zhongguo" → 无中文字符 → EN |

### 3.4 v2 检测（带置信度）

```python
def detect_language_v2(text: str) -> Tuple[LanguageCode, float]:
    if not text:
        return LanguageCode.EN, 0.0
    
    total_chars = len(text.strip())
    scores = {}
    for lang, pattern in LANGUAGE_PATTERNS.items():
        count = len(pattern.findall(text))
        if count > 0:
            scores[lang] = count
    
    if not scores:
        return LanguageCode.EN, 0.5
    
    best = max(scores, key=lambda k: scores[k])
    confidence = min(scores[best] / total_chars, 1.0)
    return best, round(confidence, 2)
```

| 置信度 | 含义 | 建议 |
|--------|------|------|
| 0.8-1.0 | 高置信度 | 可直接使用 |
| 0.5-0.8 | 中置信度 | 建议人工复核或 LLM 确认 |
| 0.0-0.5 | 低置信度 | 建议使用 LLM 或默认 EN |

---

## 4. 规则 vs LLM 对比

| 维度 | 规则（当前） | LLM（未来） | 建议 |
|------|-------------|------------|------|
| **区域推断** | 关键词映射（16 个） | 自然语言理解 | 规则为主 + LLM 兜底 |
| **语言推断** | Unicode 范围（17 种） | 语义理解 | 规则为主 + LLM 扩展跨语言 |
| **翻译** | 无（fallback） | LLM 翻译 + 质量评分 | LLM 为主 |
| **质量评分** | 无 | LLM 评分 | 已启用 |

---

## 5. DeepSeek 知识增强建议

| 领域 | 当前问题 | DeepSeek 可优化方向 |
|------|----------|----------------------|
| **隐式地理关联** | "TSMC" → 未映射到 TW | 知识库增强：公司→国家映射 |
| **新兴议题** | "Generative AI" → 无匹配 | 知识库增强：技术→国家关联 |
| **跨语言推断** | "AI regulation" → 仅 EN | 知识增强：议题→多语言关联 |
| **拼音/音译** | "Zhongguo" → EN | 知识增强：拼音→汉字→语言 |
| **区域重要性排序** | 无排序 | 知识增强：根据时效性排序区域 |

---

*文档结束 — 配合 `NEWS_INTAKE_SYSTEM.md` 和 `METRICS_AND_OBSERVABILITY.md` 阅读*
