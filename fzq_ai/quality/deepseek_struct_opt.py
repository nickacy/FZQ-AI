# fzq_ai/quality/deepseek_struct_opt.py
# DeepSeek V4 Pro - v9.2 Structure & Logic Optimization Expert
# Role: between GLM-5.2 (draft) and Minimax (validator)
# Only does: structure reorder + logic fix + de-redundancy + hierarchy unify
# NEVER: schema enforcement, empty-field cleansing, final formatting

import copy, json, re, hashlib
from datetime import datetime
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class StructOptResult:
    task_name: str
    status: str  # "optimized" | "unchanged" | "error"
    optimized: Dict[str, Any]
    report: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class DeepSeekStructOptimizer:
    """
    DS v9.2 optimizer. Receives GLM-5.2 JSON draft, outputs structured JSON.

    Pipeline: GLM-5.2 -> DS (here) -> Minimax (validation) -> Doubao (format)
    """

    def optimize(self, task_name: str, schema: Dict[str, Any],
                 raw_draft: Dict[str, Any]) -> StructOptResult:
        draft = copy.deepcopy(raw_draft)
        report = {
            "reordered": [], "logic_fixes": [], "deduplicated": [],
            "hierarchy_fixes": [], "warnings": []
        }
        t0 = datetime.utcnow()

        try:
            draft = self._reorder_fields(draft, schema, report)
            draft = self._fix_logic_consistency(draft, task_name, report)
            draft = self._remove_redundancy(draft, report)
            draft = self._unify_hierarchy(draft, schema, report)
            return StructOptResult(
                task_name=task_name, status="optimized", optimized=draft,
                report=report,
                metadata={
                    "processed_at": t0.isoformat(),
                    "optimizer_version": "v9.2",
                    "original_bytes": len(json.dumps(raw_draft, ensure_ascii=False)),
                    "optimized_bytes": len(json.dumps(draft, ensure_ascii=False))
                })
        except Exception as e:
            return StructOptResult(
                task_name=task_name, status="error", optimized=draft,
                report={"error": str(e), **report},
                metadata={"processed_at": t0.isoformat()})

    # ── 6.1 FIELD REORDER ──────────────────────────────────
    def _reorder_fields(self, data: Any, schema: Dict[str, Any],
                        report: Dict) -> Any:
        if not isinstance(data, dict):
            return data
        props = schema.get("properties", {})
        if not props:
            return data
        ordered = {}
        for k in props:
            if k in data:
                val = data[k]
                sub = props.get(k, {})
                if sub.get("type") == "object" and isinstance(val, dict):
                    ordered[k] = self._reorder_fields(val, sub, report)
                elif sub.get("type") == "array" and isinstance(val, list):
                    items_s = sub.get("items", {})
                    if items_s.get("type") == "object":
                        ordered[k] = [
                            self._reorder_fields(v, items_s, report)
                            for v in val if isinstance(v, dict)]
                    else:
                        ordered[k] = val
                else:
                    ordered[k] = val
        for k in data:
            if k not in ordered:
                ordered[k] = data[k]
        if ordered != data:
            report["reordered"].append("fields aligned to schema order")
        return ordered

    # ── 6.2 LOGIC CONSISTENCY ──────────────────────────────
    def _fix_logic_consistency(self, data: Dict, task_name: str,
                               report: Dict) -> Dict:
        if task_name in ("zh_policy_brief",):
            data = self._fix_policy_logic(data, report)
        elif task_name in ("zh_risk_scan",):
            data = self._fix_risk_logic(data, report)
        elif task_name in ("zh_opinion_landscape",):
            data = self._fix_opinion_logic(data, report)
        data = self._fix_timeline_order(data, report)
        return data

    def _fix_policy_logic(self, data: Dict, report: Dict) -> Dict:
        kps = data.get("key_points", [])
        if not isinstance(kps, list):
            data["key_points"] = [{"point": str(kps), "category": "\u5176\u4ed6",
                                    "evidence_span": ""}]
            report["hierarchy_fixes"].append("key_points: singular -> [obj]")
        seen = set()
        deduped = []
        for kp in (kps if isinstance(kps, list) else []):
            if not isinstance(kp, dict):
                kp = {"point": str(kp), "category": "\u5176\u4ed6",
                      "evidence_span": ""}
            sig = hashlib.sha256(
                kp.get("point", "").encode()
            ).hexdigest()[:12]
            if sig not in seen:
                seen.add(sig)
                deduped.append(kp)
        if len(deduped) < len(kps):
            report["logic_fixes"].append(
                f"Removed {len(kps)-len(deduped)} duplicate key_points")
        data["key_points"] = deduped
        return data

    def _fix_risk_logic(self, data: Dict, report: Dict) -> Dict:
        risks = data.get("risk_items", [])
        if not isinstance(risks, list):
            data["risk_items"] = [risks] if risks else []
            risks = data["risk_items"]
        for i, r in enumerate(risks):
            if not isinstance(r, dict):
                continue
            severity = r.get("severity", 3)
            desc = str(r.get("description", "")).lower()
            danger_signals = ["\u4e25\u91cd", "crisis", "\u5d29\u6e83",
                              "war", "\u6218\u4e89", "\u7cfb\u7edf\u6027"]
            if any(w in desc for w in danger_signals):
                if isinstance(severity, (int, float)) and severity < 3:
                    report["logic_fixes"].append(
                        f"risk_items[{i}]: severity {severity} -> 4")
                    risks[i]["severity"] = 4
                if isinstance(severity, str) and severity in ("1", "2"):
                    report["logic_fixes"].append(
                        f"risk_items[{i}]: severity '{severity}' -> 4")
                    risks[i]["severity"] = 4
        return data

    def _fix_opinion_logic(self, data: Dict, report: Dict) -> Dict:
        stance = data.get("stance_distribution", {})
        if isinstance(stance, dict):
            total = sum(
                v for v in stance.values() if isinstance(v, (int, float)))
            if total > 0 and abs(total - 1.0) > 0.05:
                for k in stance:
                    if isinstance(stance[k], (int, float)):
                        stance[k] = round(stance[k] / total, 4)
                report["logic_fixes"].append(
                    "stance_distribution normalized to sum=1.0")
                data["stance_distribution"] = stance
        pi = data.get("polarization_index")
        if isinstance(pi, str):
            try:
                data["polarization_index"] = float(pi)
                report["logic_fixes"].append("polarization_index: str->float")
            except ValueError:
                pass
        return data

    def _fix_timeline_order(self, data: Dict, report: Dict) -> Dict:
        tl = data.get("timeline", [])
        if not isinstance(tl, list) or len(tl) < 2:
            return data
        def _key(item):
            d = item.get("date", "") if isinstance(item, dict) else ""
            if d in ("\u5f85\u5b9a", "unknown"):
                return "9999"
            return str(d).replace("-", "")
        sorted_tl = sorted(tl, key=_key)
        if sorted_tl != tl:
            report["logic_fixes"].append("timeline reordered by date asc")
            data["timeline"] = sorted_tl
        return data

    # ── 6.3 DEDUPLICATION ──────────────────────────────────
    def _remove_redundancy(self, data: Dict, report: Dict) -> Dict:
        LIST_KEYS = ["key_points", "risk_items", "key_narratives",
                     "affected_regions", "affected_sectors",
                     "representative_quotes", "risk_factors",
                     "opportunities", "industries", "stakeholders"]
        for key in LIST_KEYS:
            if key in data and isinstance(data[key], list):
                original = len(data[key])
                data[key] = self._dedup_list(data[key])
                removed = original - len(data[key])
                if removed:
                    report["deduplicated"].append(
                        f"{key}: removed {removed} duplicates")
        for sub_key in ("affected_entities", "impact_analysis",
                        "evidence_map", "source_attribution",
                        "viewpoint_diversity"):
            if sub_key in data and isinstance(data[sub_key], dict):
                data[sub_key] = self._dedup_dict(data[sub_key], report,
                                                  sub_key)
        return data

    def _dedup_list(self, lst: List) -> List:
        seen, result = set(), []
        for item in lst:
            if isinstance(item, dict):
                sig = hashlib.sha256(
                    json.dumps(item, sort_keys=True, ensure_ascii=False,
                               default=str).encode()).hexdigest()[:16]
            else:
                sig = hashlib.sha256(str(item).encode()).hexdigest()[:16]
            if sig not in seen:
                seen.add(sig)
                result.append(item)
        return result

    def _dedup_dict(self, d: Dict, report: Dict, path: str) -> Dict:
        for k, v in list(d.items()):
            if isinstance(v, list):
                original = len(v)
                d[k] = self._dedup_list(v)
                if len(d[k]) < original:
                    report["deduplicated"].append(
                        f"{path}.{k}: removed {original-len(d[k])} dup")
            elif isinstance(v, dict):
                d[k] = self._dedup_dict(v, report, f"{path}.{k}")
        return d

    # ── 6.4 HIERARCHY UNIFICATION ──────────────────────────
    def _unify_hierarchy(self, data: Dict, schema: Dict,
                         report: Dict) -> Dict:
        props = schema.get("properties", {})
        for field, fschema in props.items():
            if field not in data:
                continue
            ftype = fschema.get("type")
            # String items in object arrays -> wrap as objects
            if (ftype == "array" and field in
                    ("key_points", "risk_items", "events", "timeline",
                     "key_narratives")):
                items_s = fschema.get("items", {})
                if items_s.get("type") == "object":
                    wrapped = []
                    any_fixed = False
                    for item in data[field]:
                        if isinstance(item, dict):
                            wrapped.append(item)
                        else:
                            wrapped.append(
                                {"value": str(item), "_original": str(item)})
                            any_fixed = True
                    if any_fixed:
                        report["hierarchy_fixes"].append(
                            f"{field}: str-items wrapped as objects")
                    data[field] = wrapped
            # Scalar -> list promotion
            if ftype == "array" and not isinstance(data[field], list):
                data[field] = [data[field]]
                report["hierarchy_fixes"].append(
                    f"{field}: singular -> [array]")
            # Object keys
            if ftype == "object" and isinstance(data[field], dict):
                sub_props = fschema.get("properties", {})
                if sub_props:
                    cleaned = {}
                    for sk, sv in sub_props.items():
                        if sk in data[field]:
                            cleaned[sk] = data[field][sk]
                    if cleaned:
                        data[field] = cleaned
        return data


# ── Convenience functions ──────────────────────────────────
def make_optimizer() -> DeepSeekStructOptimizer:
    return DeepSeekStructOptimizer()


def optimize_json_string(task_name: str, schema: Dict[str, Any],
                         raw_json: str) -> StructOptResult:
    """Parse raw JSON with optional markdown wrapping, then optimize."""
    text = raw_json.strip()
    m = re.match(r"^```(?:json)?\s*\n?(.*?)\n?```$", text, re.DOTALL)
    if m:
        text = m.group(1).strip()
    draft = json.loads(text)
    return make_optimizer().optimize(task_name, schema, draft)
