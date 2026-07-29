from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict

DocumentType = Literal[
    "standard",
    "guideline",
    "decision",
    "template",
    "checklist",
    "reference",
    "example",
    "concept",
    "howto",
    "exception",
]

RuleLevel = Literal["must", "should", "may", "reference"]


class OkfDocument(BaseModel):
    model_config = ConfigDict(frozen=True)

    type: DocumentType
    id: str
    title: str
    summary: str
    status: str
    owner: str
    tags: list[str]
    body: str
    rule_level: RuleLevel | None = None
    technologies: list[str] | None = None
    applies_to: list[str] | None = None
    version: str | None = None
    effective_date: date | None = None
