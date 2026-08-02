import re
from pathlib import Path

import yaml
from pydantic import ValidationError

from src.domain.document import OkfDocument

_FRONTMATTER_DELIMITER = "---"
_FRONTMATTER_PATTERN = re.compile(
    r"\A---[ \t]*\r?\n(?P<frontmatter>.*?)\r?\n---[ \t]*\r?\n?(?P<body>.*)\Z",
    re.DOTALL,
)
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
    """directory配下の*.mdをパースする。1件でもパースに失敗すると例外を送出して停止する(fail-fast)。"""
    documents: list[OkfDocument] = []
    seen: dict[str, Path] = {}

    for path in sorted(directory.rglob("*.md")):
        document = parse_document(path)
        duplicated = seen.get(document.id)
        if duplicated is not None:
            raise OkfParseError(f"{path}: duplicate id '{document.id}' (already used by {duplicated})")
        seen[document.id] = path
        documents.append(document)

    return documents


def _split_frontmatter(text: str, path: Path) -> tuple[dict[str, object], str]:
    if not text.startswith(_FRONTMATTER_DELIMITER):
        raise OkfParseError(f"{path}: missing YAML frontmatter (expected leading '---')")

    match = _FRONTMATTER_PATTERN.match(text)
    if match is None:
        raise OkfParseError(f"{path}: unterminated YAML frontmatter (missing closing '---')")

    frontmatter_raw = match.group("frontmatter")
    body = match.group("body")

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

    missing = [field for field in _STANDARD_REQUIRED_FIELDS if _is_unset(getattr(document, field))]
    if missing:
        raise OkfParseError(f"{path}: type=standard requires fields: {', '.join(missing)}")


def _is_unset(value: object) -> bool:
    if value is None:
        return True
    if isinstance(value, list):
        return len(value) == 0
    return False
