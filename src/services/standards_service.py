"""ToolがRepository/SearchBackendに直接依存しないためのService層。"""

from dataclasses import dataclass
from pathlib import Path

from src.domain.document import OkfDocument, RuleLevel
from src.repository.document_repository import DocumentRepository
from src.search.backend import SearchBackend, SearchQuery, SearchResult

_ALL_PROJECTS = "all-projects"

_EXTENSION_TECHNOLOGIES: dict[str, str] = {
    ".py": "python",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".bicep": "azure",
    ".tf": "azure",
}


@dataclass(frozen=True)
class StandardSummary:
    id: str
    title: str
    summary: str


@dataclass(frozen=True)
class ApplicableStandards:
    must: list[StandardSummary]
    should: list[StandardSummary]
    reference: list[StandardSummary]


@dataclass(frozen=True)
class ChecklistItem:
    id: str
    title: str
    body: str


class StandardsService:
    def __init__(self, repository: DocumentRepository, search_backend: SearchBackend) -> None:
        self._repository = repository
        self._search_backend = search_backend

    def search_standards(
        self,
        query: str,
        technology: str | None = None,
        rule_level: RuleLevel | None = None,
    ) -> list[SearchResult]:
        return self._search_backend.search(
            SearchQuery(text=query, technology=technology, rule_level=rule_level)
        )

    def get_standard(self, document_id: str) -> str:
        document = self._repository.get(document_id)
        if document is None:
            raise ValueError(f"standard not found: {document_id}")
        return document.body

    def get_applicable_standards(self, project: str, files: list[str], task: str) -> ApplicableStandards:
        candidates = [
            document
            for document in self._repository.list_by_metadata(status="active")
            if _applies_to_project(document.applies_to, project)
        ]

        technologies = _infer_technologies(files) | _technologies_mentioned_in_task(task, candidates)
        if technologies:
            candidates = [
                document
                for document in candidates
                if document.technologies is None or set(document.technologies) & technologies
            ]

        return ApplicableStandards(
            must=[_to_summary(d) for d in candidates if d.rule_level == "must"],
            should=[_to_summary(d) for d in candidates if d.rule_level == "should"],
            reference=[_to_summary(d) for d in candidates if d.rule_level == "reference"],
        )

    def get_review_checklist(self) -> list[ChecklistItem]:
        return [
            ChecklistItem(id=document.id, title=document.title, body=document.body)
            for document in self._repository.list_by_metadata(type="checklist")
        ]


def _to_summary(document: OkfDocument) -> StandardSummary:
    return StandardSummary(id=document.id, title=document.title, summary=document.summary)


def _applies_to_project(applies_to: list[str] | None, project: str) -> bool:
    if applies_to is None:
        return True
    return _ALL_PROJECTS in applies_to or project in applies_to


def _infer_technologies(files: list[str]) -> set[str]:
    technologies = set()
    for file in files:
        technology = _EXTENSION_TECHNOLOGIES.get(Path(file).suffix.lower())
        if technology is not None:
            technologies.add(technology)
    return technologies


def _technologies_mentioned_in_task(task: str, candidates: list[OkfDocument]) -> set[str]:
    task_lower = task.lower()
    known_technologies = {
        technology
        for document in candidates
        if document.technologies is not None
        for technology in document.technologies
    }
    return {technology for technology in known_technologies if technology.lower() in task_lower}
