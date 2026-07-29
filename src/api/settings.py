import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    knowledge_source: str
    knowledge_path: str
    auth_enabled: bool


def load_settings() -> Settings:
    return Settings(
        knowledge_source=os.environ.get("KNOWLEDGE_SOURCE", "sample"),
        knowledge_path=os.environ.get("KNOWLEDGE_PATH", "./sample-knowledge"),
        auth_enabled=os.environ.get("AUTH_ENABLED", "false").lower() == "true",
    )
