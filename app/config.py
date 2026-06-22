"""Application configuration loaded from environment variables."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Canvas LMS
    canvas_base_url: str = "https://canvas.instructure.com"
    canvas_client_id: str = ""
    canvas_client_secret: str = ""
    canvas_redirect_uri: str = "http://localhost:8000/auth/canvas/callback"
    canvas_token_encryption_key: str = "change_me"

    # WeChat iLink Bot API
    ilink_base_url: str = "https://ilinkai.weixin.qq.com"
    ilink_bot_token: str = ""
    ilink_channel_version: str = "1.0.3"

    # PostgreSQL
    postgres_user: str = "canvasbot"
    postgres_password: str = "canvasbot_secret"
    postgres_db: str = "canvas_wechat"
    database_url: str = (
        "postgresql+asyncpg://canvasbot:canvasbot_secret@localhost:5432/canvas_wechat"
    )
    database_url_sync: str = (
        "postgresql://canvasbot:canvasbot_secret@localhost:5432/canvas_wechat"
    )

    # Redis
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    # AI / LLM
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com/v1"
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    log_level: str = "INFO"

    # Notifications
    quiet_hours_start: int = 22
    quiet_hours_end: int = 8
    context_token_stale_hours: int = 12
    max_daily_notifications: int = 20

    @property
    def canvas_oauth2_auth_url(self) -> str:
        return f"{self.canvas_base_url}/login/oauth2/auth"

    @property
    def canvas_oauth2_token_url(self) -> str:
        return f"{self.canvas_base_url}/login/oauth2/token"


settings = Settings()
