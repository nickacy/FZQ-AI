def test_glm_basic(glm):
    output = glm.chat("hello")
    assert isinstance(output, str)
