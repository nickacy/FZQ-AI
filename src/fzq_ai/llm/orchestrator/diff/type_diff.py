# src/fzq_ai/llm/orchestrator/diff/type_diff.py

class TypeDiff:
    """
    字段类型差异分析。
    """

    def compare(self, data, schema):
        issues = []

        for field, field_info in schema.model_fields.items():
            if field not in data:
                continue

            expected = field_info.annotation
            actual = type(data[field])

            if expected == list and actual != list:
                issues.append(f"字段类型错误: {field} 应为 list")
            elif expected == dict and actual != dict:
                issues.append(f"字段类型错误: {field} 应为 dict")
            elif expected == str and actual != str:
                issues.append(f"字段类型错误: {field} 应为 str")
            elif expected == int and actual != int:
                issues.append(f"字段类型错误: {field} 应为 int")

        return issues
