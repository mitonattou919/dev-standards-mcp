from pathlib import Path

import pytest

from src.parser.okf_parser import OkfParseError, parse_directory, parse_document

_VALID_GUIDELINE = """---
type: guideline
id: guideline-999
title: テストガイドライン
summary: テスト用のダミーガイドライン
status: active
owner: test-team
tags:
  - test
---

# 本文
テスト本文。
"""

_VALID_STANDARD = """---
type: standard
id: standard-999
title: テスト標準
summary: テスト用のダミー標準
status: active
owner: test-team
tags:
  - test
rule_level: must
technologies:
  - python
applies_to:
  - all-projects
version: "1.0.0"
effective_date: 2026-07-29
---

# 本文
テスト本文。
"""


def _write(tmp_path: Path, name: str, content: str) -> Path:
    path = tmp_path / name
    path.write_text(content, encoding="utf-8")
    return path


def test_parse_document_guideline(tmp_path: Path) -> None:
    path = _write(tmp_path, "guideline.md", _VALID_GUIDELINE)

    document = parse_document(path)

    assert document.type == "guideline"
    assert document.id == "guideline-999"
    assert document.body == "# 本文\nテスト本文。"
    assert document.rule_level is None


def test_parse_document_standard(tmp_path: Path) -> None:
    path = _write(tmp_path, "standard.md", _VALID_STANDARD)

    document = parse_document(path)

    assert document.type == "standard"
    assert document.rule_level == "must"
    assert document.technologies == ["python"]


def test_parse_document_missing_frontmatter(tmp_path: Path) -> None:
    path = _write(tmp_path, "no-frontmatter.md", "# タイトルだけ\n本文\n")

    with pytest.raises(OkfParseError, match="missing YAML frontmatter"):
        parse_document(path)


def test_parse_document_unterminated_frontmatter(tmp_path: Path) -> None:
    path = _write(tmp_path, "unterminated.md", "---\ntype: guideline\n")

    with pytest.raises(OkfParseError, match="unterminated YAML frontmatter"):
        parse_document(path)


def test_parse_document_invalid_yaml(tmp_path: Path) -> None:
    content = "---\ntype: guideline\n  bad indent: [unclosed\n---\nbody\n"
    path = _write(tmp_path, "invalid-yaml.md", content)

    with pytest.raises(OkfParseError, match="invalid YAML frontmatter"):
        parse_document(path)


def test_parse_document_frontmatter_not_mapping(tmp_path: Path) -> None:
    path = _write(tmp_path, "list-frontmatter.md", "---\n- a\n- b\n---\nbody\n")

    with pytest.raises(OkfParseError, match="must be a YAML mapping"):
        parse_document(path)


def test_parse_document_missing_required_field(tmp_path: Path) -> None:
    content = """---
type: guideline
id: guideline-999
title: テストガイドライン
status: active
owner: test-team
tags: [test]
---

本文
"""
    path = _write(tmp_path, "missing-summary.md", content)

    with pytest.raises(OkfParseError, match="invalid frontmatter"):
        parse_document(path)


def test_parse_document_standard_missing_rule_level(tmp_path: Path) -> None:
    content = """---
type: standard
id: standard-999
title: テスト標準
summary: テスト用のダミー標準
status: active
owner: test-team
tags: [test]
---

本文
"""
    path = _write(tmp_path, "standard-missing-fields.md", content)

    with pytest.raises(OkfParseError, match="type=standard requires fields"):
        parse_document(path)


def test_parse_document_standard_empty_list_field_is_treated_as_missing(tmp_path: Path) -> None:
    content = """---
type: standard
id: standard-999
title: テスト標準
summary: テスト用のダミー標準
status: active
owner: test-team
tags: [test]
rule_level: must
technologies: []
applies_to:
  - all-projects
version: "1.0.0"
effective_date: 2026-07-29
---

本文
"""
    path = _write(tmp_path, "standard-empty-list-field.md", content)

    with pytest.raises(OkfParseError, match="type=standard requires fields: technologies"):
        parse_document(path)


def test_parse_document_frontmatter_value_containing_delimiter_substring(tmp_path: Path) -> None:
    content = """---
type: guideline
id: guideline-999
title: テストガイドライン
summary: "before---after"
status: active
owner: test-team
tags:
  - test
---

# 本文

区切り線の前

---

区切り線の後
"""
    path = _write(tmp_path, "delimiter-substring.md", content)

    document = parse_document(path)

    assert document.summary == "before---after"
    assert "区切り線の前" in document.body
    assert "区切り線の後" in document.body


def test_parse_directory_sample_knowledge() -> None:
    sample_knowledge = Path(__file__).parent.parent.parent / "sample-knowledge"

    documents = parse_directory(sample_knowledge)

    assert len(documents) == 9
    ids = {document.id for document in documents}
    assert "standard-001" in ids
    assert "index" in ids
