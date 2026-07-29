from fastmcp import FastMCP

from src.api.settings import load_settings
from src.auth.provider import build_auth_provider


def create_server() -> FastMCP:
    settings = load_settings()
    auth = build_auth_provider(settings.auth_enabled)
    return FastMCP(name="dev-standards-mcp", auth=auth)
