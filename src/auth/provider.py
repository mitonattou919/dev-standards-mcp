import os

from fastmcp.server.auth.providers.azure import AzureProvider


def build_auth_provider(auth_enabled: bool) -> AzureProvider | None:
    if not auth_enabled:
        return None

    return AzureProvider(
        client_id=os.environ["AZURE_CLIENT_ID"],
        client_secret=os.environ["AZURE_CLIENT_SECRET"],
        tenant_id=os.environ["AZURE_TENANT_ID"],
        base_url=os.environ.get("MCP_BASE_URL", "http://localhost:8000"),
        required_scopes=[os.environ.get("AZURE_REQUIRED_SCOPE", "mcp-access")],
    )
