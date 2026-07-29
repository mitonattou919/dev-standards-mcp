import asyncio
from typing import Any

import pytest
from fastmcp import FastMCP
from fastmcp.tools import FunctionTool

from src.services.standards_service import StandardsService
from src.tools.standards_tools import register_tools


@pytest.fixture
def registered_mcp(standards_service: StandardsService) -> FastMCP:
    mcp = FastMCP(name="test")
    register_tools(mcp, standards_service)
    return mcp


def _call_tool(mcp: FastMCP, name: str, **kwargs: Any) -> Any:
    async def _run() -> Any:
        tool = await mcp.get_tool(name)
        assert isinstance(tool, FunctionTool)
        return tool.fn(**kwargs)

    return asyncio.run(_run())


def test_search_standards_tool_returns_results(registered_mcp: FastMCP) -> None:
    results = _call_tool(registered_mcp, "search_standards", query="共通ルール")

    assert len(results) == 1
    assert results[0].id == "standard-all-python"
    assert isinstance(results[0].score, float)


def test_get_standard_tool_returns_body(registered_mcp: FastMCP) -> None:
    body = _call_tool(registered_mcp, "get_standard", id="standard-all-python")

    assert body == "Pythonプロジェクト全体に適用する共通ルールを定める。"


def test_get_standard_tool_raises_for_missing_id(registered_mcp: FastMCP) -> None:
    with pytest.raises(ValueError, match="standard not found"):
        _call_tool(registered_mcp, "get_standard", id="does-not-exist")


def test_get_applicable_standards_tool_groups_by_rule_level(registered_mcp: FastMCP) -> None:
    result = _call_tool(
        registered_mcp, "get_applicable_standards", project="backend", files=["app.py"], task=""
    )

    assert [s.id for s in result.must] == ["standard-all-python"]
    assert result.should == []
    assert [s.id for s in result.reference] == ["standard-general-reference"]


def test_get_review_checklist_tool_returns_items(registered_mcp: FastMCP) -> None:
    items = _call_tool(registered_mcp, "get_review_checklist")

    assert [item.id for item in items] == ["checklist-service-test"]
    assert items[0].body == "- [ ] チェック項目1\n- [ ] チェック項目2"
