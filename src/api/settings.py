import os
from dataclasses import dataclass

_TRUTHY_VALUES = {"true", "1", "yes"}


@dataclass(frozen=True)
class Settings:
    knowledge_source: str
    knowledge_path: str
    auth_enabled: bool
    host: str
    port: int


def load_settings() -> Settings:
    return Settings(
        knowledge_source=os.environ.get("KNOWLEDGE_SOURCE", "sample"),
        knowledge_path=os.environ.get("KNOWLEDGE_PATH", "./sample-knowledge"),
        auth_enabled=os.environ.get("AUTH_ENABLED", "false").lower() in _TRUTHY_VALUES,
        host=os.environ.get("MCP_HOST", "127.0.0.1"),
        port=int(os.environ.get("MCP_PORT", "8000")),
    )
