from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    app_name: str = Field(default="bfsg-checker", alias="APP_NAME")
    database_url: str = Field(default="sqlite:///./data/bfsg_checker.sqlite", alias="DATABASE_URL")

    scan_timeout_ms: int = Field(default=45000, alias="SCAN_TIMEOUT_MS")
    max_navigation_wait_ms: int = Field(default=30000, alias="MAX_NAVIGATION_WAIT_MS")
    user_agent: str = Field(default="BFSGCheckerBot/0.1 (+https://localhost)", alias="USER_AGENT")

    allow_robots_deny: bool = Field(default=True, alias="ALLOW_ROBOTS_DENY")
    robots_user_agent: str = Field(default="*", alias="ROBOTS_USER_AGENT")

    desktop_width: int = Field(default=1280, alias="DESKTOP_WIDTH")
    desktop_height: int = Field(default=720, alias="DESKTOP_HEIGHT")
    mobile_width: int = Field(default=390, alias="MOBILE_WIDTH")
    mobile_height: int = Field(default=844, alias="MOBILE_HEIGHT")

    artifacts_dir: str = Field(default="./data/artifacts", alias="ARTIFACTS_DIR")
    axe_path: str = Field(default="./vendor/axe/axe.min.js", alias="AXE_PATH")

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
