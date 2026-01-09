from app.core.robots import is_allowed

def test_robots_invalid_scheme():
    allowed, info = is_allowed("file:///etc/passwd")
    assert allowed is False
