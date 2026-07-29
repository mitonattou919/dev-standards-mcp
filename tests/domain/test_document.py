import pytest
from pydantic import ValidationError

from src.domain.document import OkfDocument


def test_okf_document_requires_base_fields() -> None:
    with pytest.raises(ValidationError):
        OkfDocument.model_validate({"type": "guideline"})


def test_okf_document_accepts_minimal_non_standard_document() -> None:
    document = OkfDocument.model_validate(
        {
            "type": "guideline",
            "id": "guideline-001",
            "title": "title",
            "summary": "summary",
            "status": "active",
            "owner": "team",
            "tags": ["tag"],
            "body": "body",
        }
    )

    assert document.rule_level is None
    assert document.technologies is None
