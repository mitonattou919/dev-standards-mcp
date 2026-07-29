from pathlib import Path

import yaml
from pydantic import ValidationError

from src.domain.document import OkfDocument

_FRONTMATTER_DELIMITER = "---"
_STANDARD_REQUIRED_FIELDS = (
    "rule_level",
    "technologies",
    "applies_to",
    "version",
    "effective_date",
)


class OkfParseError(ValueError):
    pass


def parse_document(path: Path) -> OkfDocument:
    text = path.read_text(encoding="utf-8")
    frontmatter, body = _split_frontmatter(text, path)

    try:
        document = OkfDocument.model_validate({**frontmatter, "body": body})
    except ValidationError as exc:
        raise OkfParseError(f"{path}: invalid frontmatter\n{exc}") from exc

    _validate_standard_fields(document, path)
    return document


def parse_directory(directory: Path) -> list[OkfDocument]:
    return [parse_document(path) for path in sorted(directory.rglob("*.md"))]


def _split_frontmatter(text: str, path: Path) -> tuple[dict[str, object], str]:
    if not text.startswith(_FRONTMATTER_DELIMITER):
        raise OkfParseError(f"{path}: missing YAML frontmatter (expected leading '---')")

    _, _, rest = text.partition(_FRONTMATTER_DELIMITER)
    frontmatter_raw, separator, body = rest.partition(_FRONTMATTER_DELIMITER)
    if not separator:
        raise OkfParseError(f"{path}: unterminated YAML frontmatter (missing closing '---')")

    try:
        frontmatter = yaml.safe_load(frontmatter_raw)
    except yaml.YAMLError as exc:
        raise OkfParseError(f"{path}: invalid YAML frontmatter\n{exc}") from exc

    if not isinstance(frontmatter, dict):
        raise OkfParseError(f"{path}: frontmatter must be a YAML mapping")

    return frontmatter, body.strip()


def _validate_standard_fields(document: OkfDocument, path: Path) -> None:
    if document.type != "standard":
        return

    missing = [field for field in _STANDARD_REQUIRED_FIELDS if getattr(document, field) is None]
    if missing:
        raise OkfParseError(f"{path}: type=standard requires fields: {', '.join(missing)}")
