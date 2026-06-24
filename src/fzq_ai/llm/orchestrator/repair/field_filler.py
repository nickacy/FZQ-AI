# src/fzq_ai/llm/orchestrator/repair/field_filler.py

class FieldFiller:
    """
    根据 Schema 自动补全缺失字段。
    """

    def fill_missing_fields(self, data, schema):
        for field, field_type in schema.model_fields.items():
            if field not in data:
                data[field] = self._default_value(field_type)
        return data

    def _default_value(self, field_type):
        if field_type.annotation == list:
            return []
        if field_type.annotation == dict:
            return {}
        if field_type.annotation == str:
            return ""
        if field_type.annotation == int:
            return 0
        return None
