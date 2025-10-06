from pydantic import BaseModel, Field, EmailStr, ValidationError
from typing import Optional
from dotenv import load_dotenv
import os, yaml

class RetryConfig(BaseModel):
    max_attempts: int = Field(default=3, ge=1)
    backoff_base: float = Field(default=2.0, gt=0)
    jitter: bool = True

class AppConfig(BaseModel):
    app_env: str = "production"
    headless: bool = False
    user_data_dir: str = ".dp_profile"
    download_dir: str = "downloads"
    screenshot_dir: str = "screenshots"
    log_level: str = "DEBUG"

    base_url: str
    cart_url: str

    login_email: EmailStr
    login_password: str

    # Telegram
    telegram_enabled: bool = False
    telegram_bot_token: Optional[str] = None
    telegram_chat_id: Optional[str] = None
    telegram_parse_mode: str = "HTML"  # ou "Markdown"

    wait_qr_sleep: int = Field(default=10, ge=1)
    renew_wait_minutes: int = Field(default=20, ge=1)
    navigation_timeout: int = Field(default=30, ge=5)
    element_timeout: int = Field(default=20, ge=5)

    retry: RetryConfig = RetryConfig()

def load_config() -> AppConfig:
    load_dotenv(override=True)

    # Base de ENV
    env = {
        "app_env": os.getenv("APP_ENV", "production"),
        "headless": os.getenv("HEADLESS", "false").lower() == "true",
        "user_data_dir": os.getenv("USER_DATA_DIR", ".dp_profile"),
        "download_dir": os.getenv("DOWNLOAD_DIR", "downloads"),
        "screenshot_dir": os.getenv("SCREENSHOT_DIR", "screenshots"),
        "log_level": os.getenv("LOG_LEVEL", "DEBUG"),

        "base_url": os.getenv("BASE_URL", "https://vasco.eleventickets.com/?lang=pt_BR#!/home"),
        "cart_url": os.getenv("CART_URL", "https://vasco.eleventickets.com/#!/carrinho"),

        "login_email": os.getenv("LOGIN_EMAIL", "user@example.com"),
        "login_password": os.getenv("LOGIN_PASSWORD", "change_me"),
        
        "telegram_enabled": os.getenv("TELEGRAM_ENABLED", "false").lower() == "true",
        "telegram_bot_token": os.getenv("TELEGRAM_BOT_TOKEN"),
        "telegram_chat_id": os.getenv("TELEGRAM_CHAT_ID"),
        "telegram_parse_mode": os.getenv("TELEGRAM_PARSE_MODE", "HTML"),
        
        "wait_qr_sleep": int(os.getenv("WAIT_QR_SLEEP", "10")),
        "renew_wait_minutes": int(os.getenv("RENEW_WAIT_MINUTES", "20")),
        "navigation_timeout": int(os.getenv("NAVIGATION_TIMEOUT", "30")),
        "element_timeout": int(os.getenv("ELEMENT_TIMEOUT", "20")),

        "retry": {
            "max_attempts": int(os.getenv("RETRY_MAX_ATTEMPTS", "3")),
            "backoff_base": float(os.getenv("RETRY_BACKOFF_BASE", "2")),
            "jitter": os.getenv("RETRY_BACKOFF_JITTER", "true").lower() == "true",
        }
    }

    # Sobreposição opcional via YAML
    if os.path.exists("config.yaml"):
        with open("config.yaml", "r", encoding="utf-8") as f:
            y = yaml.safe_load(f) or {}
        # campos simples
        for k in ("headless", "renew_wait_minutes", "wait_qr_sleep", "navigation_timeout",
                  "element_timeout", "user_data_dir", "download_dir", "screenshot_dir", "log_level"):
            if k in y:
                env[k] = y[k]
        # retry
        if "retry" in y:
            env["retry"].update(y["retry"])

    try:
        return AppConfig(**env)
    except ValidationError as e:
        from ticket_refresher.logging_config import logger
        logger.error(f"Config inválida: {e}")
        raise
