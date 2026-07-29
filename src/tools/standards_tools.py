"""Phase 1で最低限必要な4つのMCP Toolを定義し、FastMCPサーバへ登録する。

ToolはStandardsService経由でのみ知識にアクセスし、Repository/SearchBackendへ直接依存しない。
"""

from fastmcp import FastMCP
from pydantic import BaseModel

from src.domain.document import RuleLevel
from src.services.standards_service import StandardsService, StandardSummary


class SearchStandardResult(BaseModel):
    id: str
    title: str
    summary: str
    score: float


class StandardSummaryOutput(BaseModel):
    id: str
    title: str
    summary: str


class ApplicableStandardsOutput(BaseModel):
    must: list[StandardSummaryOutput]
    should: list[StandardSummaryOutput]
    reference: list[StandardSummaryOutput]


class ChecklistItemOutput(BaseModel):
    id: str
    title: str
    body: str


def register_tools(mcp: FastMCP, service: StandardsService) -> None:
    @mcp.tool
    def search_standards(
        query: str,
        technology: str | None = None,
        rule_level: RuleLevel | None = None,
    ) -> list[SearchStandardResult]:
        """開発標準・ガイドラインをキーワード検索する。"""
        results = service.search_standards(query, technology=technology, rule_level=rule_level)
        return [
            SearchStandardResult(id=result.id, title=result.title, summary=result.summary, score=result.score)
            for result in results
        ]

    @mcp.tool
    def get_standard(id: str) -> str:
        """指定したIDのドキュメント本文(Markdown)を取得する。"""
        return service.get_standard(id)

    @mcp.tool
    def get_applicable_standards(project: str, files: list[str], task: str) -> ApplicableStandardsOutput:
        """プロジェクト・対象ファイル・タスク内容から適用すべき標準をmust/should/referenceで返す。"""
        result = service.get_applicable_standards(project=project, files=files, task=task)
        return ApplicableStandardsOutput(
            must=[_to_summary_output(s) for s in result.must],
            should=[_to_summary_output(s) for s in result.should],
            reference=[_to_summary_output(s) for s in result.reference],
        )

    @mcp.tool
    def get_review_checklist() -> list[ChecklistItemOutput]:
        """レビュー用チェックリストを取得する。"""
        return [
            ChecklistItemOutput(id=item.id, title=item.title, body=item.body)
            for item in service.get_review_checklist()
        ]


def _to_summary_output(summary: StandardSummary) -> StandardSummaryOutput:
    return StandardSummaryOutput(id=summary.id, title=summary.title, summary=summary.summary)
