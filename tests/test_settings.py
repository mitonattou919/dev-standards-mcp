import pytest

from src.api.settings import load_settings


def test_load_settings_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("KNOWLEDGE_SOURCE", raising=False)
    monkeypatch.delenv("KNOWLEDGE_PATH", raising=False)
    monkeypatch.delenv("AUTH_ENABLED", raising=False)
    monkeypatch.delenv("MCP_HOST", raising=False)
    monkeypatch.delenv("MCP_PORT", raising=False)

    settings = load_settings()

    assert settings.knowledge_source == "sample"
    assert settings.knowledge_path == "./sample-knowledge"
    assert settings.auth_enabled is False
    assert settings.host == "127.0.0.1"
    assert settings.port == 8000


def test_load_settings_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KNOWLEDGE_SOURCE", "github")
    monkeypatch.setenv("KNOWLEDGE_PATH", "/data/knowledge")
    monkeypatch.setenv("AUTH_ENABLED", "true")
    monkeypatch.setenv("MCP_HOST", "0.0.0.0")
    monkeypatch.setenv("MCP_PORT", "9000")

    settings = load_settings()

    assert settings.knowledge_source == "github"
    assert settings.knowledge_path == "/data/knowledge"
    assert settings.auth_enabled is True
    assert settings.host == "0.0.0.0"
    assert settings.port == 9000


@pytest.mark.parametrize("value", ["true", "TRUE", "1", "yes", "YES"])
def test_load_settings_auth_enabled_truthy_values(
    monkeypatch: pytest.MonkeyPatch, value: str
) -> None:
    monkeypatch.setenv("AUTH_ENABLED", value)

    assert load_settings().auth_enabled is True


@pytest.mark.parametrize("value", ["false", "0", "no", ""])
def test_load_settings_auth_enabled_falsy_values(
    monkeypatch: pytest.MonkeyPatch, value: str
) -> None:
    monkeypatch.setenv("AUTH_ENABLED", value)

    assert load_settings().auth_enabled is False
