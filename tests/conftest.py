import pytest
from fzq_ai.config.global_settings import settings

@pytest.fixture
def glm():
    return settings.get_client("glm-5.2")

@pytest.fixture
def deepseek():
    return settings.get_client("deepseek")

@pytest.fixture
def qwen():
    return settings.get_client("qwen")

@pytest.fixture
def kimi():
    return settings.get_client("kimi")
