# fzq_ai/quality/deepseek_struct_opt.py
# DeepSeek V4 Pro — v9.3 Structure & Logic Optimization Expert
# Role: between GLM-5.2 (raw draft) and Minimax (validator)
# Only: structure + logic + de-redundancy + 5W1H grouping + narrative layering
# Never: create facts, add opinions, format, enforce schema

import copy, json, re, hashlib
from datetime import datetime
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class StructOptResult:
    task_name: str
    status: str  # optimized | unchanged | error
    optimized: Dict[str, Any]
    report: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class DeepSeekStructOptimizer:
    """v9.3 Structural Optimization Expert for FZQ-AI quality pipeline."""

    # ==================================================================
    # PUBLIC API
    # ==================================================================

    def optimize(self, task_name: str, schema: Dict[str, Any],
                 raw_draft: Dict[str, Any]) -> StructOptResult:
        """v9.2 legacy entry: field-reorder + logic-fix + dedup + hierarchy-unify."""
        return self._core_optimize(task_name, schema, raw_draft, mode="v9.2")

    def optimize_v93(self, raw_draft: Dict[str, Any]) -> StructOptResult:
        """v9.3 entry: receives GLM-5.2 8-field JSON, outputs schema-ready JSON."""
        return self._core_optimize("glm_v93", {}, raw_draft, mode="v9.3")

    def _core_optimize(self, task_name: str, schema: Dict[str, Any],
                       raw_draft: Dict[str, Any], mode: str) -> StructOptResult:
        draft = copy.deepcopy(raw_draft)
        report = {"reordered": [], "logic_fixes": [], "deduplicated": [],
                   "hierarchy_fixes": [], "warnings": [], "v93_groups": []}
        t0 = datetime.utcnow()
        try:
            if mode == "v9.3":
                draft = self._v93_transform(draft, report)
            else:
                draft = self._reorder_fields(draft, schema, report)
                draft = self._fix_logic_consistency(draft, task_name, report)
                draft = self._remove_redundancy(draft, report)
                draft = self._unify_hierarchy(draft, schema, report)
            return StructOptResult(
                task_name=task_name, status="optimized", optimized=draft,
                report=report,
                metadata={"processed_at": t0.isoformat(), "version": mode})
        except Exception as e:
            return StructOptResult(
                task_name=task_name, status="error", optimized=raw_draft,
                report={"error": str(e), **report},
                metadata={"processed_at": t0.isoformat(), "version": mode})

    # ==================================================================
    # v9.3 TRANSFORM (8-field GLM-5.2 → schema-ready JSON)
    # ==================================================================

    def _v93_transform(self, draft: Dict, report: Dict) -> Dict:
        facts = draft.get("core_facts", [])
        events_raw = draft.get("event_chain", [])
        actors = draft.get("actors", [])
        narratives = draft.get("narratives", [])
        risks = draft.get("risks", [])
        policy_signals = draft.get("policy_signals", [])
        trend_signals = draft.get("trend_signals", [])
        raw_quotes = draft.get("raw_quotes", [])

        output = {
            "facts": self._group_5w1h(facts, report),
            "events": self._convert_event_chain(events_raw, report),
            "actors": self._fill_actors(actors, output_ref=None, report=report),
            "narratives": self._layer_narratives(narratives, report),
            "risks": self._categorize_signals(risks, "risk", report),
            "policy_signals": self._struct_policy_signals(policy_signals, report),
            "trend_signals": self._struct_trend_signals(trend_signals, report),
            "raw_quotes": self._preserve_quotes(raw_quotes, report),
        }
        # Post-pass: fill actors.actions from events if empty
        output["actors"] = self._fill_actors(
            output["actors"], output_ref=output["events"], report=report)
        return output

    # ---------- 5W1H GROUPING ----------
    _WHO_KW = ["宣布", "表示", "声明", "警告", "呼吁", "announces", "says", "declares",
               "总统", "主席", "外交部", "商务部", "国防部", "领导人", "发言人",
               "president", "ministry", "spokesperson", "official"]
    _WHAT_KW = ["实施", "制裁", "限制", "禁止", "出口管制", "制裁清单", "制裁法案",
                "sanctions", "ban", "restrict", "export control", "tariff"]
    _WHERE_KW = ["在", "于", "位于", "from", "in", "首都", "总部", "地区", "区域"]
    _WHY_KW = ["为了", "以", "原因", "理由", "目的", "因为", "由于",
               "because", "due to", "in order to", "国家安全", "反制", "回应"]

    def _group_5w1h(self, facts: List, report: Dict) -> Dict[str, List[str]]:
        groups: Dict[str, List] = {"who": [], "what": [], "when": [],
                                     "where": [], "why": [], "how": []}
        if not facts:
            return groups
        for f in facts:
            text = str(f)
            matched = False
            if any(kw in text for kw in self._WHO_KW):
                groups["who"].append(text); matched = True
            if any(kw in text for kw in self._WHAT_KW):
                groups["what"].append(text); matched = True
            if any(kw in text for kw in self._WHERE_KW):
                groups["where"].append(text); matched = True
            if any(kw in text for kw in self._WHY_KW):
                groups["why"].append(text); matched = True
            if not matched:
                groups["what"].append(text)
        for k in groups:
            groups[k] = list(dict.fromkeys(groups[k]))  # dedup preserve order
        report["v93_groups"].append(f"5W1H: {sum(len(v) for v in groups.values())} facts grouped")
        return groups

    # ---------- EVENT CHAIN PARSER ----------
    def _convert_event_chain(self, events_raw: List, report: Dict) -> List[Dict]:
        result = []
        if not events_raw:
            return result
        for raw in events_raw:
            text = str(raw)
            parts = re.split(r"\s*->\s*|→|—>|>\s*", text)
            for i, part in enumerate(parts):
                part = part.strip()
                if not part:
                    continue
                node = {"step": i + 1, "action": part, "actor": "", "target": "", "timestamp": None}
                actor_match = re.match(r"^(.+?)(?:宣布|表示|声明|警告|呼吁|实施|批评|制裁|禁止)", part)
                if actor_match:
                    node["actor"] = actor_match.group(1).strip()
                    node["action"] = part
                result.append(node)
        if result:
            report["v93_groups"].append(f"event_chain: {len(result)} nodes")
        return result

    # ---------- ACTOR FILLER ----------
    def _fill_actors(self, actors: List, output_ref: Optional[List], report: Dict) -> List:
        if not isinstance(actors, list):
            actors = [actors] if actors else []
        filled = []
        seen_names = set()
        for a in actors:
            if isinstance(a, str):
                a = {"name": a, "role": "", "position": "", "actions": []}
            if not isinstance(a, dict):
                continue
            name = a.get("name", "")
            if name in seen_names:
                continue
            seen_names.add(name)
            if not a.get("role"):
                a["role"] = "发言人" if any(k in str(a) for k in ["外交部","发言人"]) else "机构"
            if not a.get("position") and a.get("actions"):
                a["position"] = "参与方"
            if output_ref and not a.get("actions"):
                a["actions"] = [e.get("action", "") for e in output_ref
                                if name and name in str(e.get("actor", ""))]
            filled.append(a)
        report["v93_groups"].append(f"actors: {len(filled)} deduped/filled")
        return filled

    # ---------- NARRATIVE LAYERING ----------
    _SRC_KW = ["X国", "Y国", "Z国", "西方媒体", "中国媒体", "俄罗斯媒体", "中东媒体",
               "state media", "western media", "official", "US media", "Chinese media"]

    def _layer_narratives(self, narratives: List, report: Dict) -> List[Dict]:
        if not isinstance(narratives, list):
            return []
        layered = []
        seen_claims = set()
        for n in narratives:
            if isinstance(n, str):
                src = "未知来源"
                for kw in self._SRC_KW:
                    if kw in n:
                        src = kw; break
                n = {"source": src, "stance": "", "claims": [n]}
            if not isinstance(n, dict):
                continue
            claims = n.get("claims", [])
            if isinstance(claims, str):
                claims = [claims]
            deduped_claims = []
            for c in claims:
                h = hashlib.sha256(str(c).encode()).hexdigest()[:12]
                if h not in seen_claims:
                    seen_claims.add(h)
                    deduped_claims.append(str(c))
            n["claims"] = deduped_claims
            layered.append(n)
        report["v93_groups"].append(f"narratives: {len(layered)} sources layered")
        return layered

    # ---------- SIGNAL CATEGORIZATION ----------
    _CAT_MAP = {
        "political": ["政治", "选举", "制裁", "外交", "政府", "policy", "sanction", "election", "diplomacy", "parliament", "congress"],
        "economic": ["经济", "贸易", "关税", "股票", "市场", "衰退", "GDP", "economic", "trade", "tariff", "stock", "market", "inflation"],
        "security": ["军事", "战争", "冲突", "导弹", "军事演习", "军队", "security", "military", "war", "conflict", "missile", "troop"],
        "technological": ["芯片", "AI", "科技", "出口管制", "半导体", "tech", "chip", "semiconductor", "AI", "artificial intelligence"],
        "social": ["民众", "抗议", "舆论", "社会", "民心", "social", "protest", "public", "civil"],
    }

    def _categorize_signals(self, signals: List, signal_type: str, report: Dict) -> Dict[str, List]:
        categories: Dict[str, List] = {"political": [], "economic": [], "security": [], "technological": [], "social": []}
        if not isinstance(signals, list):
            return categories
        for s in signals:
            text = str(s.get("description", s)) if isinstance(s, dict) else str(s)
            placed = False
            for cat, kws in self._CAT_MAP.items():
                if any(kw.lower() in text.lower() for kw in kws):
                    categories[cat].append(s if isinstance(s, dict) else {"signal": text})
                    placed = True; break
            if not placed:
                categories["political"].append(s if isinstance(s, dict) else {"signal": text})
        total = sum(len(v) for v in categories.values())
        report["v93_groups"].append(f"{signal_type}: {total} signals categorized")
        return categories

    def _struct_policy_signals(self, signals: List, report: Dict) -> List:
        return self._categorize_signals(signals, "policy", report)

    def _struct_trend_signals(self, signals: List, report: Dict) -> List:
        return self._categorize_signals(signals, "trend", report) if isinstance(signals, list) else []

    def _preserve_quotes(self, quotes: List, report: Dict) -> List[str]:
        if not isinstance(quotes, list):
            return []
        result = [str(q) for q in quotes]
        report["v93_groups"].append(f"raw_quotes: {len(result)} preserved verbatim")
        return result

    # ==================================================================
    # v9.2 LEGACY METHODS (preserved for backward compatibility)
    # ==================================================================

    def _reorder_fields(self, data: Any, schema: Dict, report: Dict) -> Any:
        if not isinstance(data, dict):
            return data
        props = schema.get("properties", {})
        if not props:
            return data
        ordered = {}
        for k in list(props.keys()):
            if k in data:
                sub = props.get(k, {})
                if sub.get("type") == "object" and isinstance(data[k], dict):
                    ordered[k] = self._reorder_fields(data[k], sub, report)
                elif sub.get("type") == "array" and isinstance(data[k], list):
                    items_schema = sub.get("items", {})
                    if items_schema.get("type") == "object":
                        ordered[k] = [self._reorder_fields(v, items_schema, report) for v in data[k] if isinstance(v, dict)]
                    else:
                        ordered[k] = data[k]
                else:
                    ordered[k] = data[k]
        for k in data:
            if k not in ordered:
                ordered[k] = data[k]
        if ordered != data:
            report["reordered"].append("fields aligned to schema order")
        return ordered

    def _fix_logic_consistency(self, data: Dict, task_name: str, report: Dict) -> Dict:
        if "key_points" in data:
            data = self._fix_policy_logic(data, report)
        if "risk_items" in data:
            data = self._fix_risk_logic(data, report)
        data = self._fix_timeline_order(data, report)
        return data

    def _fix_policy_logic(self, data: Dict, report: Dict) -> Dict:
        kps = data.get("key_points", [])
        if not isinstance(kps, list):
            kps = [{"point": str(kps), "evidence_span": ""}]
            data["key_points"] = kps
        seen = set()
        deduped = []
        for kp in kps:
            if isinstance(kp, str):
                kp = {"point": kp, "evidence_span": ""}
            h = hashlib.sha256(str(kp.get("point", "")).encode()).hexdigest()[:12]
            if h not in seen:
                seen.add(h); deduped.append(kp)
        if len(deduped) < len(kps):
            report["deduplicated"].append(f"key_points: removed {len(kps)-len(deduped)} duplicates")
        data["key_points"] = deduped
        return data

    def _fix_risk_logic(self, data: Dict, report: Dict) -> Dict:
        risks = data.get("risk_items", [])
        for i, r in enumerate(risks):
            if not isinstance(r, dict):
                continue
            desc = str(r.get("description", "")).lower()
            sev = r.get("severity", 3)
            danger = any(w in desc for w in ["严重","危机","崩溃","战争","系统性"])
            if danger and isinstance(sev, (int, float)) and sev < 4:
                risks[i]["severity"] = 4
                report["logic_fixes"].append(f"risk_items[{i}]: severity {sev}→4")
        return data

    def _fix_timeline_order(self, data: Dict, report: Dict) -> Dict:
        tl = data.get("timeline", [])
        if not isinstance(tl, list) or len(tl) < 2:
            return data
        def _key(item):
            d = item.get("date", "") if isinstance(item, dict) else ""
            return str(d).replace("-", "") if d != "待定" else "9999"
        sorted_tl = sorted(tl, key=_key)
        if sorted_tl != tl:
            data["timeline"] = sorted_tl
            report["logic_fixes"].append("timeline reordered by date asc")
        return data

    def _remove_redundancy(self, data: Dict, report: Dict) -> Dict:
        list_keys = ["key_points", "risk_items", "events", "industries",
                      "affected_regions", "affected_sectors", "stakeholders"]
        for key in list_keys:
            if key in data and isinstance(data[key], list):
                data[key], removed = self._dedup_list(data[key])
                if removed:
                    report["deduplicated"].append(f"{key}: removed {removed} duplicates")
        return data

    def _dedup_list(self, lst: List) -> Tuple[List, int]:
        seen, result = set(), []
        for item in lst:
            sig = hashlib.sha256(
                json.dumps(item, sort_keys=True, ensure_ascii=False, default=str).encode()
            ).hexdigest()[:16]
            if sig not in seen:
                seen.add(sig); result.append(item)
        return result, len(lst) - len(result)

    def _unify_hierarchy(self, data: Dict, schema: Dict, report: Dict) -> Dict:
        props = schema.get("properties", {})
        for field_name, field_schema in props.items():
            if field_name not in data:
                continue
            ftype = field_schema.get("type")
            if ftype == "array" and not isinstance(data[field_name], list):
                data[field_name] = [data[field_name]]
                report["hierarchy_fixes"].append(f"{field_name}: singular → [array]")
            if ftype == "array" and field_schema.get("items", {}).get("type") == "object":
                cleaned = []
                for item in data[field_name]:
                    if isinstance(item, dict):
                        cleaned.append(item)
                    elif isinstance(item, str):
                        cleaned.append({"value": item})
                if cleaned:
                    data[field_name] = cleaned
        return data


# ========== Module singleton ==========
_optimizer: Optional[DeepSeekStructOptimizer] = None


def get_optimizer() -> DeepSeekStructOptimizer:
    global _optimizer
    if _optimizer is None:
        _optimizer = DeepSeekStructOptimizer()
    return _optimizer


def optimize(task_name: str, schema: Dict[str, Any], raw_draft: Dict[str, Any]) -> StructOptResult:
    """v9.2 legacy: field-reorder + logic-fix + dedup + hierarchy-unify."""
    return get_optimizer().optimize(task_name, schema, raw_draft)


def optimize_v93(raw_draft: Dict[str, Any]) -> StructOptResult:
    """v9.3: receives GLM-5.2 8-field JSON, outputs schema-ready JSON."""
    return get_optimizer().optimize_v93(raw_draft)
