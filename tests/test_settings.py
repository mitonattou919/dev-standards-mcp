import pytest

from src.api.settings import load_settings


def test_load_settings_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("KNOWLEDGE_SOURCE", raising=False)
    monkeypatch.delenv("KNOWLEDGE_PATH", raising=False)
    monkeypatch.delenv("AUTH_ENABLED", raising=False)

    settings = load_settings()

    assert settings.knowledge_source == "sample"
    assert settings.knowledge_path == "./sample-knowledge"
    assert settings.auth_enabled is False


def test_load_settings_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KNOWLEDGE_SOURCE", "github")
    monkeypatch.setenv("KNOWLEDGE_PATH", "/data/knowledge")
    monkeypatch.setenv("AUTH_ENABLED", "true")

    settings = load_settings()

    assert settings.knowledge_source == "github"
    assert settings.knowledge_path == "/data/knowledge"
    assert settings.auth_enabled is True
