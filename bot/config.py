import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    bot_token: str
    log_level: str = "INFO"

    @classmethod
    def from_env(cls) -> "Settings":
        token = os.environ.get("BOT_TOKEN")
        if not token:
            raise RuntimeError("BOT_TOKEN environment variable is required")
        return cls(
            bot_token=token,
            log_level=os.environ.get("LOG_LEVEL", "INFO"),
        )
