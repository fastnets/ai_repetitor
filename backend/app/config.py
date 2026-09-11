from functools import lru_cache
from pathlib import Path

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    llm_base_url: str = Field(
        default="https://api.openai.com/v1",
        validation_alias=AliasChoices("LLM_BASE_URL", "AI_API_URL"),
    )
    llm_api_key: str = Field(default="", validation_alias=AliasChoices("LLM_API_KEY", "AI_API_KEY"))
    llm_model: str = Field(default="gpt-4o-mini", validation_alias=AliasChoices("LLM_MODEL", "AI_MODEL"))
    database_url: str = "sqlite:///./data/tutor.db"
    textbook_index: Path = Path("../data/textbooks/index.json")
    llm_timeout_seconds: float = 45
    llm_max_tokens: int = 250
    llm_disable_thinking: bool = True

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
