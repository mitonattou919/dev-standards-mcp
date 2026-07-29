import pytest
from fastmcp import FastMCP

from src.api.server import create_server


def test_create_server_returns_fastmcp_instance(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("AUTH_ENABLED", raising=False)

    server = create_server()

    assert isinstance(server, FastMCP)
    assert server.name == "dev-standards-mcp"
    assert server.auth is None
