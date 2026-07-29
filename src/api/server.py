import sqlite3
from pathlib import Path

from fastmcp import FastMCP

from src.api.settings import load_settings
from src.auth.provider import build_auth_provider
from src.repository.document_repository import SqliteDocumentRepository
from src.repository.index_builder import build_index_from_directory
from src.search.fts5_backend import Fts5SearchBackend
from src.services.standards_service import StandardsService
from src.tools.standards_tools import register_tools


def create_server() -> FastMCP:
    settings = load_settings()
    if settings.knowledge_source != "sample":
        raise NotImplementedError(
            f"knowledge_source={settings.knowledge_source!r} is not supported yet (PoC only supports 'sample')"
        )

    auth = build_auth_provider(settings.auth_enabled)
    mcp = FastMCP(name="dev-standards-mcp", auth=auth)

    conn = sqlite3.connect(":memory:", check_same_thread=False)
    build_index_from_directory(conn, Path(settings.knowledge_path))

    repository = SqliteDocumentRepository(conn)
    search_backend = Fts5SearchBackend(conn)
    service = StandardsService(repository, search_backend)
    register_tools(mcp, service)

    return mcp
