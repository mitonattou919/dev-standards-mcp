---
type: guideline
id: guideline-002
title: pytestベストプラクティス
summary: pytestでテストを書く際の実践的な指針。フィクスチャ、パラメータ化、モック、マーカーの使い分け。
status: active
owner: platform-team
tags:
  - python
  - pytest
  - testing
---

# L2: Testing with pytest

## About This Document

A practical guide for writing tests with [pytest](https://docs.pytest.org/).
Read this not as "you must do it this way," but as "here's what's worth knowing before you start."

## 1. Just Write Tests First

pytest is flexible enough that you can spend a lot of time setting up the "right" structure before writing a single test. That's usually a mistake.

Start with a plain function in a `test_*.py` file. No fixtures, no plugins, no config. Get something running. The structure that actually helps you will emerge from what's annoying.

```python
def test_add():
    assert add(1, 2) == 3
```

That's a valid test. Start there.

## 2. Fixtures Are for Setup You'd Otherwise Repeat

Fixtures aren't a design goal — they're a solution to repetition. If you're writing the same setup code in three tests, that's the moment to reach for a fixture.

```python
import pytest

@pytest.fixture
def sample_user():
    return {"id": 1, "name": "Alice", "role": "member"}

def test_user_display_name(sample_user):
    assert display_name(sample_user) == "Alice"
```

**Fixture scope matters**

- `scope="function"` (default) — recreated for every test. Safe, predictable.
- `scope="session"` — created once per test run. Useful for expensive setup (DB connections, loaded models), but watch for state leaking between tests.

Start with `function` scope. Move to wider scope only when slowness becomes a real problem.

## 3. Parametrize for Multiple Cases

When you want to run the same test logic with different inputs, `@pytest.mark.parametrize` keeps things clean.

```python
@pytest.mark.parametrize("input,expected", [
    ("hello", "HELLO"),
    ("world", "WORLD"),
    ("", ""),
])
def test_uppercase(input, expected):
    assert to_uppercase(input) == expected
```

This is usually better than writing three nearly-identical test functions. Each case gets its own result in the output, so failures are easy to isolate.

## 4. Mocks: Use Them at the Boundary, Not Inside

Mocking is useful for isolating code from external systems — HTTP calls, databases, file I/O. It becomes a problem when you mock so much that your test is no longer testing real behavior.

**A useful rule of thumb**

Mock things your code calls, not things your code *is*.

```python
from unittest.mock import patch

def test_fetch_user_calls_api(mock_get):
    with patch("myapp.client.requests.get") as mock_get:
        mock_get.return_value.json.return_value = {"id": 1}
        result = fetch_user(1)
        assert result["id"] == 1
```

If you find yourself mocking three layers deep, it's often a sign the code under test is doing too much.

## 5. Use Markers to Organize Tests

Markers let you categorize tests and run subsets selectively.

```python
@pytest.mark.slow
def test_heavy_computation():
    ...
```

```bash
# Run everything except slow tests
pytest -m "not slow"
```

Register custom markers in `pyproject.toml` to avoid warnings:

```toml
[tool.pytest.ini_options]
markers = [
    "slow: tests that take a long time",
    "integration: tests that hit external services",
]
```

A few well-chosen markers go a long way. Don't over-categorize.

## 6. Configuration in pyproject.toml

Keep pytest config in `pyproject.toml` alongside your other tooling. Avoids having yet another config file.

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-v --tb=short"
```

`--tb=short` gives you enough traceback to understand a failure without the wall of text. Adjust to taste.

## What's Next

Once your basic test suite is running, the questions that tend to come up:

- How do you test code that depends on environment variables or config files?
- When does `pytest-mock` make more sense than `unittest.mock`?
- How do you structure tests for async code (`pytest-asyncio`)?

Find the friction in your specific codebase, then dig in.

出典: [mitonattou919/engineering-with-ai](https://github.com/mitonattou919/engineering-with-ai/blob/main/L2-practices/guide-pytest.md)
