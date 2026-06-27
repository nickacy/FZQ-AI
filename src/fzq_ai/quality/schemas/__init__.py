"""Schema definitions for quality validation."""


def get_schema(task_type: str):
    """Return the expected output schema for a given task type."""
    # For now returns a simple passthrough schema
    return {"task_type": task_type, "validate": True}


__all__ = ["get_schema"]
