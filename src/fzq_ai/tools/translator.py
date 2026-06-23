
"""
FZQ-AI Tools — 多语言翻译器 v10
支持自动语言检测、多语言翻译、翻译质量评分、翻译缓存
"""
import re
import asyncio
import hashlib
import time
from typing import Any, Dict, List, Optional, Tuple

from fzq_ai.schemas import (
    LanguageCode, ModelProvider, LLMRequest,
)
from fzq_ai.core.prompts import PromptTemplates


# ---------------------------------------------------------
# v10: 翻译缓存 — SHA-256 索引，24h TTL
# ---------------------------------------------------------

class TranslationCache:
    """v10: 基于 SHA-256 的翻译缓存，带 TTL。"""

    def __init__(self, ttl_seconds: int = 86400):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._ttl = ttl_seconds

    def _key(self, text: str, target: LanguageCode) -> str:
        """生成 SHA-256 缓存键。"""
        payload = f"{text}::{target.value}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def get(self, text: str, target: LanguageCode) -> Optional[Dict[str, Any]]:
        key = self._key(text, target)
        entry = self._cache.get(key)
        if entry is None:
            return None
        if time.time() - entry.get("ts", 0) > self._ttl:
            del self._cache[key]
            return None
        return entry.get("data")

    def set(self, text: str, target: LanguageCode, data: Dict[str, Any]) -> None:
        key = self._key(text, target)
        self._cache[key] = {"ts": time.time(), "data": data}

    def clear(self) -> None:
        self._cache.clear()

    def size(self) -> int:
        return len(self._cache)


# ---------------------------------------------------------
# Unicode 范围（语言检测用）
# ---------------------------------------------------------

LANGUAGE_PATTERNS: Dict[LanguageCode, re.Pattern] = {
    LanguageCode.EN: re.compile(r"[A-Za-z]"),
    LanguageCode.ZH: re.compile(r"[\u4e00-\u9fff]"),
    LanguageCode.JA: re.compile(r"[\u3040-\u30ff\u31f0-\u31ff]"),
    LanguageCode.KO: re.compile(r"[\uac00-\ud7af]"),
    LanguageCode.AR: re.compile(r"[\u0600-\u06ff]"),
    LanguageCode.RU: re.compile(r"[\u0400-\u04ff]"),
    LanguageCode.FR: re.compile(r"[\u00e0-\u00ff]"),  # 法语带音符字符
    LanguageCode.ES: re.compile(r"[\u00e1\u00e9\u00ed\u00f3\u00fa\u00f1\u00d1]"),
    LanguageCode.DE: re.compile(r"[\u00e4\u00f6\u00fc\u00df]"),
    LanguageCode.PT: re.compile(r"[\u00e7\u00e3\u00f5]"),
    LanguageCode.IT: re.compile(r"[\u00e0\u00e8\u00e9\u00ec\u00f2\u00f9]"),
    LanguageCode.VI: re.compile(r"[\u00e0\u00e1\u1ea1\u1ea3\u00e2\u0103\u00e8\u00e9\u1eb9\u1ebb\u00ea\u00ec\u00ed\u1ecb\u1ec9\u00f2\u00f3\u1ecd\u1ecf\u00f4\u01a1\u00f9\u00fa\u1ee5\u1ee7\u01b0\u1ef3\u00fd\u1ef5\u1ef7\u0111]"),
    LanguageCode.TH: re.compile(r"[\u0e00-\u0e7f]"),
    LanguageCode.ID: re.compile(r"[\u00e9\u00e8]"),  # 印尼语简单标记
    LanguageCode.TR: re.compile(r"[\u011f\u011f\u015f\u0131\u00f6\u00e7\u00fc]"),
    LanguageCode.PL: re.compile(r"[\u0105\u0107\u0119\u0142\u0144\u00f3\u015b\u017a\u017c]"),
    LanguageCode.NL: re.compile(r"[\u00e9\u00eb\u00ef\u00f6\u00fc]"),
}


# ---------------------------------------------------------
# v8: 增强版语言检测
# ---------------------------------------------------------

def detect_language(text: str) -> LanguageCode:
    """
    v8 增强版语言检测：基于 Unicode 字符范围判断。
    返回最可能的主要语言代码。
    """
    if not text or not text.strip():
        return LanguageCode.EN

    # 统计各语言字符数
    scores: Dict[LanguageCode, int] = {}
    for lang, pattern in LANGUAGE_PATTERNS.items():
        count = len(pattern.findall(text))
        if count > 0:
            scores[lang] = count

    if not scores:
        # 默认英文
        return LanguageCode.EN

    # 选择字符最多的语言
    best_lang = max(scores, key=lambda k: scores[k])

    # 如果中文和日文都有字符，优先中文（因为日文也有汉字）
    if best_lang == LanguageCode.JA and LanguageCode.ZH in scores:
        if scores[LanguageCode.ZH] > scores[LanguageCode.JA] * 0.5:
            return LanguageCode.ZH

    return best_lang


def detect_language_v2(text: str) -> Tuple[LanguageCode, float]:
    """
    v8 增强版：返回 (语言, 置信度)。
    """
    if not text or not text.strip():
        return LanguageCode.EN, 0.0

    total_chars = len(text.strip())
    scores: Dict[LanguageCode, int] = {}

    for lang, pattern in LANGUAGE_PATTERNS.items():
        count = len(pattern.findall(text))
        if count > 0:
            scores[lang] = count

    if not scores:
        return LanguageCode.EN, 0.5

    best = max(scores, key=lambda k: scores[k])
    confidence = min(scores[best] / total_chars, 1.0) if total_chars > 0 else 0.5
    return best, round(confidence, 2)


# ---------------------------------------------------------
# 旧接口兼容（保留）
# ---------------------------------------------------------

def is_english_or_chinese(text: str) -> bool:
    """
    判断文本是否主要由英文或中文组成。
    - 保留旧逻辑：只判断"是否英/中文"
    - 增强准确性：排除日文/韩文/俄文/阿拉伯文等
    """
    if not text:
        return True

    # 如果包含日文/韩文/阿拉伯文/俄文 → 直接判定为非英中
    if LANGUAGE_PATTERNS[LanguageCode.JA].search(text):
        return False
    if LANGUAGE_PATTERNS[LanguageCode.KO].search(text):
        return False
    if LANGUAGE_PATTERNS[LanguageCode.AR].search(text):
        return False
    if LANGUAGE_PATTERNS[LanguageCode.RU].search(text):
        return False

    # 如果包含中文 → 是中文
    if LANGUAGE_PATTERNS[LanguageCode.ZH].search(text):
        return True

    # 如果包含英文 → 是英文
    if LANGUAGE_PATTERNS[LanguageCode.EN].search(text):
        return True

    # 其他语言 → 非英中
    return False


# ---------------------------------------------------------
# v8: Translator 类 — 异步多语言翻译
# ---------------------------------------------------------

class Translator:
    """v10 多语言翻译器：自动检测 + 多语言翻译 + 质量评分 + 缓存。

    支持：
    - 中英互译（核心）
    - 阿语/法语/西语/俄语/日语/韩语 fallback
    - LLM 翻译质量评分
    - v10: SHA-256 翻译缓存（24h TTL）
    """

    def __init__(self, llm_router: Optional[Any] = None, cache: Optional[TranslationCache] = None):
        self.llm_router = llm_router
        self._cache = cache or TranslationCache()

    # -------------------------------------------------------------------
    # v10: 批量翻译（batch_size=20）— 带缓存
    # -------------------------------------------------------------------
    async def batch_translate(
        self,
        items: List[Any],
        target_language: LanguageCode,
        batch_size: int = 20,
    ) -> List[Any]:
        """批量翻译新闻列表。

        v10 新增：
        - 每次最多 batch_size 条一起翻译
        - 缓存命中跳过 LLM 调用
        - 保留 fallback（单条失败不影响其他）
        - 保留错误隔离
        - 保留翻译质量评分
        """
        from fzq_ai.schemas import TranslatedNewsItem
        results: List[TranslatedNewsItem] = []

        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]

            # v10: 先检查缓存
            uncached_batch: List[Any] = []
            cached_results: List[Tuple[int, Any]] = []
            for idx, item in enumerate(batch):
                cache_key_text = f"{item.title}::{item.content[:500]}"
                cached = self._cache.get(cache_key_text, target_language) if self._cache else None
                if cached:
                    cached_results.append((idx, TranslatedNewsItem(
                        original=item,
                        translated_title=cached.get("title", item.title),
                        translated_content=cached.get("content", item.content),
                        target_language=target_language,
                        translation_provider="cache",
                        translation_confidence=cached.get("confidence", 0.9),
                        translation_latency_ms=0,
                    )))
                else:
                    uncached_batch.append(item)

            if not uncached_batch:
                # 全部缓存命中
                for idx, res in sorted(cached_results, key=lambda x: x[0]):
                    results.append(res)
                continue

            # 构建批量 prompt（仅对未缓存条目）
            batch_text = "\n\n".join(
                f"[ITEM_{idx}]\nTitle: {item.title}\nContent: {item.content[:500]}"
                for idx, item in enumerate(uncached_batch)
            )

            prompt = f"""你是一名专业翻译。请将以下 {len(uncached_batch)} 条新闻翻译成 {target_language.value}。

【待翻译内容】
{batch_text}

【输出要求】
1. 只输出 JSON，不要输出任何解释性文字、Markdown 代码块标记或自然语言。
2. 不要输出 ```json 或 ``` 等标记。
3. 如果无法翻译，返回空 JSON：{{}}

严格输出 JSON 格式：
{{
    "translations": [
        {{
            "title": "翻译后的标题",
            "content": "翻译后的内容",
            "confidence": 0.95
        }}
    ]
}}
"""

            if self.llm_router is None:
                # 无 LLM → simple fallback 逐条
                for item in uncached_batch:
                    results.append(self._simple_translate_item(item, target_language))
                continue

            try:
                request = LLMRequest(
                    prompt=prompt,
                    provider=ModelProvider.DEEPSEEK,
                    temperature=0.1,
                    max_tokens=4096,
                )
                resp = await self.llm_router.generate(request)
                data = _try_parse_json(resp.content)

                translations = []
                if data and "translations" in data and isinstance(data["translations"], list):
                    translations = data["translations"]

                for idx, item in enumerate(uncached_batch):
                    if idx < len(translations) and isinstance(translations[idx], dict):
                        t = translations[idx]
                        title = _safe_str(t, "title", item.title)
                        content = _safe_str(t, "content", item.content)
                        confidence = _safe_float(t, "confidence", 0.8)
                        # v10: 写入缓存
                        if self._cache:
                            cache_key_text = f"{item.title}::{item.content[:500]}"
                            self._cache.set(cache_key_text, target_language, {
                                "title": title, "content": content, "confidence": confidence
                            })
                        results.append(
                            TranslatedNewsItem(
                                original=item,
                                translated_title=title,
                                translated_content=content,
                                target_language=target_language,
                                translation_provider="llm-batch",
                                translation_confidence=confidence,
                                translation_latency_ms=resp.latency_ms,
                            )
                        )
                    else:
                        # 单条 fallback
                        results.append(self._simple_translate_item(item, target_language))

            except Exception:
                # 批量失败 → 逐条 simple fallback
                for item in uncached_batch:
                    results.append(self._simple_translate_item(item, target_language))

        return results

    def _simple_translate_item(self, item: Any, target_language: LanguageCode) -> Any:
        from fzq_ai.schemas import TranslatedNewsItem
        return TranslatedNewsItem(
            original=item,
            translated_title=item.title,
            translated_content=item.content,
            target_language=target_language,
            translation_provider="simple_fallback",
            translation_confidence=0.5,
            translation_latency_ms=0,
        )

    # -------------------------------------------------------------------
    # v8: 单条翻译（保留原有接口）— v10 增加缓存
    # -------------------------------------------------------------------
    async def translate(
        self,
        text: str,
        target_language: LanguageCode,
        source_language: Optional[LanguageCode] = None,
    ) -> Dict[str, Any]:
        """
        翻译文本。返回 dict：
        {
            "text": str,              # 翻译后的文本
            "source_language": str,   # 源语言代码
            "target_language": str,   # 目标语言代码
            "confidence": float,      # 翻译置信度
            "quality_score": float,   # 质量评分（LLM）
            "provider": str,          # 翻译提供者
            "latency_ms": int,        # 延迟
        }
        """
        # 1. 检测源语言
        if source_language is None:
            source_language, detection_conf = detect_language_v2(text)
        else:
            detection_conf = 1.0

        # 2. 如果已经是目标语言，直接返回
        if source_language == target_language:
            return {
                "text": text,
                "source_language": source_language.value,
                "target_language": target_language.value,
                "confidence": 1.0,
                "quality_score": 1.0,
                "provider": "passthrough",
                "latency_ms": 0,
            }

        # v10: 检查缓存
        if self._cache:
            cached = self._cache.get(text, target_language)
            if cached:
                return {
                    "text": cached.get("text", text),
                    "source_language": source_language.value,
                    "target_language": target_language.value,
                    "confidence": cached.get("confidence", 0.9),
                    "quality_score": cached.get("quality_score", 0.9),
                    "provider": "cache",
                    "latency_ms": 0,
                }

        # 3. 如果无 LLM router，使用简单 fallback
        if self.llm_router is None:
            result = self._simple_translate(text, source_language, target_language)
            if self._cache:
                self._cache.set(text, target_language, result)
            return result

        # 4. LLM 翻译
        start = asyncio.get_event_loop().time()
        try:
            prompt = PromptTemplates.render(
                PromptTemplates.TRANSLATION_V1,
                {
                    "target_language": target_language.value,
                    "title": text[:100],
                    "content": text[:2000],
                },
            )
            request = LLMRequest(
                prompt=prompt,
                provider=ModelProvider.DEEPSEEK,
                temperature=0.1,
                max_tokens=2048,
            )
            resp = await self.llm_router.generate(request)
            latency_ms = int((asyncio.get_event_loop().time() - start) * 1000)

            data = _try_parse_json(resp.content)
            if data and ("title" in data or "content" in data):
                translated = str(data.get("content", data.get("title", text)))
                confidence = float(data.get("confidence", 0.8)) if isinstance(data.get("confidence"), (int, float)) else 0.8
                provider = str(data.get("provider", "llm"))

                # v8: 质量评分
                quality_score = await self._score_translation_quality(
                    text, translated, source_language, target_language
                )

                result = {
                    "text": translated,
                    "source_language": source_language.value,
                    "target_language": target_language.value,
                    "confidence": min(confidence * detection_conf, 1.0),
                    "quality_score": quality_score,
                    "provider": provider,
                    "latency_ms": latency_ms,
                }
                # v10: 写入缓存
                if self._cache:
                    self._cache.set(text, target_language, result)
                return result

        except Exception as exc:
            pass

        # 5. Fallback
        result = self._simple_translate(text, source_language, target_language)
        if self._cache:
            self._cache.set(text, target_language, result)
        return result

    # -------------------------------------------------------------------
    # v8: 翻译质量评分（LLM）
    # -------------------------------------------------------------------
    async def _score_translation_quality(
        self,
        original: str,
        translated: str,
        source: LanguageCode,
        target: LanguageCode,
    ) -> float:
        """使用 LLM 评估翻译质量，返回 0-1 的分数。"""
        if self.llm_router is None:
            return 0.5

        try:
            prompt = f"""
请评估以下翻译的质量。评分标准：
- 语义准确性（是否保留原文含义）
- 语言流畅度（目标语言是否自然）
- 完整性（是否遗漏信息）

原文（{source.value}）：
{original[:500]}

译文（{target.value}）：
{translated[:500]}

只输出一个 0-1 之间的数字，不要其他文字：
"""
            request = LLMRequest(
                prompt=prompt,
                provider=ModelProvider.DEEPSEEK,
                temperature=0.0,
                max_tokens=10,
            )
            resp = await self.llm_router.generate(request)
            content = resp.content.strip()
            # 提取数字
            match = re.search(r"([0-9]*\.?[0-9]+)", content)
            if match:
                score = float(match.group(1))
                return max(0.0, min(1.0, score))
        except Exception:
            pass
        return 0.5

    # -------------------------------------------------------------------
    # Simple fallback 翻译（保留旧函数）
    # -------------------------------------------------------------------
    def _simple_translate(
        self,
        text: str,
        source: LanguageCode,
        target: LanguageCode,
    ) -> Dict[str, Any]:
        """简单 fallback 翻译。"""
        # 中英互译
        if source == LanguageCode.ZH and target == LanguageCode.EN:
            return {
                "text": f"[EN translation of]: {text}",
                "source_language": source.value,
                "target_language": target.value,
                "confidence": 0.5,
                "quality_score": 0.3,
                "provider": "simple_fallback",
                "latency_ms": 0,
            }
        if source == LanguageCode.EN and target == LanguageCode.ZH:
            return {
                "text": f"[CN translation of]: {text}",
                "source_language": source.value,
                "target_language": target.value,
                "confidence": 0.5,
                "quality_score": 0.3,
                "provider": "simple_fallback",
                "latency_ms": 0,
            }
        # 其他语言 → 返回原文并标记
        return {
            "text": text,
            "source_language": source.value,
            "target_language": target.value,
            "confidence": 0.0,
            "quality_score": 0.0,
            "provider": "untranslated",
            "latency_ms": 0,
        }


# ---------------------------------------------------------
# 旧函数兼容（保留）
# ---------------------------------------------------------

def translate_to_english(text: str) -> str:
    return f"[EN translation of]: {text}"


def translate_to_chinese(text: str) -> str:
    return f"[CN translation of]: {text}"


# ---------------------------------------------------------
# 辅助函数
# ---------------------------------------------------------

def _try_parse_json(text: str) -> Optional[Dict[str, Any]]:
    """尝试解析 JSON。"""
    import json
    try:
        return json.loads(text.strip())
    except Exception:
        return None


def _safe_str(data: Dict[str, Any], key: str, default: str = "") -> str:
    val = data.get(key, default)
    if val is None:
        return default
    return str(val) if not isinstance(val, str) else val


def _safe_float(data: Dict[str, Any], key: str, default: float = 0.0) -> float:
    val = data.get(key, default)
    if val is None:
        return default
    if isinstance(val, (int, float)):
        return float(val)
    try:
        return float(val)
    except (ValueError, TypeError):
        return default
