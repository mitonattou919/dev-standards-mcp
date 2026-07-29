import asyncio

import pytest
from fastmcp import FastMCP

from src.api.server import create_server


def test_create_server_returns_fastmcp_instance(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("AUTH_ENABLED", raising=False)

    server = create_server()

    assert isinstance(server, FastMCP)
    assert server.name == "dev-standards-mcp"
    assert server.auth is None


def test_create_server_registers_all_tools(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("AUTH_ENABLED", raising=False)

    server = create_server()

    async def _tool_names() -> set[str]:
        return {
            name
            for name in ("search_standards", "get_standard", "get_applicable_standards", "get_review_checklist")
            if await server.get_tool(name) is not None
        }

    assert asyncio.run(_tool_names()) == {
        "search_standards",
        "get_standard",
        "get_applicable_standards",
        "get_review_checklist",
    }


def test_create_server_raises_for_unsupported_knowledge_source(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KNOWLEDGE_SOURCE", "github")

    with pytest.raises(NotImplementedError, match="knowledge_source"):
        create_server()
