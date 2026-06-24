def test_glm_basic(glm):
    output = glm.run_sync("你好，介绍一下你自己")
    assert isinstance(output, str)
    assert len(output) > 0
