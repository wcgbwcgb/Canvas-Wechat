"""Basic tests for configuration loading."""


def test_settings_load():
    from app.config import Settings

    s = Settings(canvas_base_url="https://canvas.instructure.com")
    assert s.canvas_base_url == "https://canvas.instructure.com"
    assert s.ilink_base_url == "https://ilinkai.weixin.qq.com"
    assert s.ilink_channel_version == "1.0.3"
    assert s.port == 8000
    assert s.quiet_hours_start == 22
    assert s.quiet_hours_end == 8


def test_settings_properties():
    from app.config import Settings

    s = Settings(canvas_base_url="https://canvas.test.edu")
    assert s.canvas_oauth2_auth_url == "https://canvas.test.edu/login/oauth2/auth"
    assert s.canvas_oauth2_token_url == "https://canvas.test.edu/login/oauth2/token"
