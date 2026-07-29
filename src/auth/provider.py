import os

from fastmcp.server.auth.providers.azure import AzureProvider

_REQUIRED_ENV_VARS = ("AZURE_CLIENT_ID", "AZURE_CLIENT_SECRET", "AZURE_TENANT_ID")


def build_auth_provider(auth_enabled: bool) -> AzureProvider | None:
    if not auth_enabled:
        return None

    missing = [name for name in _REQUIRED_ENV_VARS if name not in os.environ]
    if missing:
        raise RuntimeError(
            f"AUTH_ENABLED=true requires the following environment variables: {', '.join(missing)}"
        )

    return AzureProvider(
        client_id=os.environ["AZURE_CLIENT_ID"],
        client_secret=os.environ["AZURE_CLIENT_SECRET"],
        tenant_id=os.environ["AZURE_TENANT_ID"],
        base_url=os.environ.get("MCP_BASE_URL", "http://localhost:8000"),
        required_scopes=[os.environ.get("AZURE_REQUIRED_SCOPE", "mcp-access")],
    )
