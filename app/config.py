from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 4000
    DEBUG: bool = False

    # Platform 1: Telegram
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    TELEGRAM_CHAT_ID: Optional[str] = None  # Channel username e.g. @mychannel or chat id

    # Platform 2: Discord
    DISCORD_WEBHOOK_URL: Optional[str] = None

    # Platform 3: Reddit
    REDDIT_CLIENT_ID: Optional[str] = None
    REDDIT_CLIENT_SECRET: Optional[str] = None
    REDDIT_USERNAME: Optional[str] = None
    REDDIT_PASSWORD: Optional[str] = None
    REDDIT_SUBREDDIT: Optional[str] = "test"  # Default test subreddit or user profile

    # Platform 4: GitHub (Create Public Gist or Public Issue)
    GITHUB_TOKEN: Optional[str] = None
    GITHUB_REPO: Optional[str] = None  # e.g. "octocat/Hello-World" for issues, or creates public Gist

    # Platform 5: Mastodon
    MASTODON_INSTANCE_URL: Optional[str] = "https://mastodon.social"
    MASTODON_ACCESS_TOKEN: Optional[str] = None

settings = Settings()

