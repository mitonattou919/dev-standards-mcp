---
type: guideline
id: guideline-001
title: Python開発ツールガイド（uv / Ruff / mypy / poethepoet / pre-commit）
summary: uv・Ruff・mypy・poethepoet・pre-commitの役割分担と設定例をまとめた実践ガイド。
status: active
owner: platform-team
tags:
  - python
  - uv
  - ruff
  - mypy
---

# L2: Setting Up a Python Development Environment

## About This Document

A practical guide for writing Python alongside AI.
Written from "why we chose this," not "use this tool."

## 1. Tool Overview

Four roles, each assigned to a dedicated tool.

| Role | Tool |
|---|---|
| Environment & dependency management | `uv` |
| Linting & formatting | `Ruff` |
| Type checking | `mypy` |
| Task runner | `poethepoet` |

Each tool does one thing well — splitting responsibilities is faster and less brittle than loading everything into a single tool.

## 2. uv — Environment and Dependency Management

The era of running `pip` + `pyenv` + `pip-tools` separately is over. Consolidate to `uv`.

**Why uv**

- Written in Rust — blazing fast (nearly zero wait time)
- Handles Python version management, virtual environments, and package management all in one
- `uv.lock` records Python version and OS-level binaries, so "works on my machine" problems rarely happen

**Basic Commands**

```bash
uv python install 3.13        # Install a Python version
uv init --python 3.13         # Create a project
uv sync                       # Sync environment to uv.lock state
uv add {package}              # Add a dependency
uv run {command}              # Run a command in the project's virtual environment
```

Commit `uv.lock`. It's the record of the canonical environment.

## 3. Ruff — Linting and Formatting

Replace `Flake8` and `Black` with a single Ruff. Also written in Rust — finishes in milliseconds.

**Two roles**

- **Lint (`ruff check`)**: Catches logical mistakes — unused imports, `==` comparisons with `None`, unused variables, etc.
- **Format (`ruff format`)**: Normalizes appearance — quote style, indentation, spacing, etc.

**`pyproject.toml` configuration**

```toml
[tool.ruff]
select = ["E", "F", "UP", "B"]
ignore = []

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
```

The `--fix` flag auto-fixes what it can, keeping PR diffs clean.

## 4. mypy — Type Checking

Write type hints and let `mypy` run static analysis. Verify "is this correct as a type?" before running, not just "does it run?"

**Why bother**

Python sometimes doesn't raise errors at runtime even with wrong types. For example:

```python
def repeat_message(message: str, times: int) -> str:
    return message * times

repeat_message(3, 4)  # Python runs it; mypy stops it
```

AI-generated code can be loose with types. Running `mypy` reduces "works but broken" code.

**Run**

```bash
uv run mypy .  # Check the whole directory (single-file checks miss cross-module issues)
```

## 5. poethepoet — Task Runner

Use `poe` to bundle lint, format, and type-check commands so you don't need to memorize them.

**`pyproject.toml` configuration**

```toml
[tool.poe.tasks]
format     = "uv run ruff format ."
lint       = "uv run ruff check --fix ."
type-check = "uv run mypy ."
check      = ["format", "lint", "type-check"]  # Run all together
```

`uv run poe check` runs "format → lint → type check" in sequence. Stops at the first type error.

## 6. pre-commit — Automatic Check Before Every Commit

Wire `poe check` into a pre-commit hook and quality checks run automatically on every `git commit`.

**`.pre-commit-config.yaml`**

```yaml
repos:
  - repo: local
    hooks:
      - id: poe-check
        name: poe-check
        entry: uv run poe check
        language: system
        types: [python]
```

Key point: use `language: system`. The hook uses the project's `uv` environment, so no version drift between the hook and the dev environment.

If there's a problem, the commit is blocked. Fixing things on the spot beats batch-fixing later.

## Quick Reference

| What to do | Command | When |
|---|---|---|
| Sync environment | `uv sync` | When dependencies change |
| Lint + auto-fix | `uv run ruff check --fix .` | After code changes |
| Format | `uv run ruff format .` | After code changes |
| Type check | `uv run mypy .` | After code changes |
| Run all checks | `uv run poe check` | Before committing |
| (Auto) pre-commit check | `git commit` | pre-commit runs automatically |

出典: [mitonattou919/engineering-with-ai](https://github.com/mitonattou919/engineering-with-ai/blob/main/L2-practices/guide-python-dev.md)
