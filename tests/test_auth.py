import pytest
from fastmcp.server.auth.providers.azure import AzureProvider

from src.auth.provider import build_auth_provider


def test_build_auth_provider_disabled() -> None:
    assert build_auth_provider(auth_enabled=False) is None


def test_build_auth_provider_enabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AZURE_CLIENT_ID", "dummy-client-id")
    monkeypatch.setenv("AZURE_CLIENT_SECRET", "dummy-client-secret")
    monkeypatch.setenv("AZURE_TENANT_ID", "dummy-tenant-id")
    monkeypatch.setenv("MCP_BASE_URL", "http://localhost:9000")
    monkeypatch.setenv("AZURE_REQUIRED_SCOPE", "dummy-scope")

    provider = build_auth_provider(auth_enabled=True)

    assert isinstance(provider, AzureProvider)


def test_build_auth_provider_enabled_missing_env_vars(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("AZURE_CLIENT_ID", raising=False)
    monkeypatch.delenv("AZURE_CLIENT_SECRET", raising=False)
    monkeypatch.delenv("AZURE_TENANT_ID", raising=False)

    with pytest.raises(RuntimeError, match="AZURE_CLIENT_ID"):
        build_auth_provider(auth_enabled=True)
