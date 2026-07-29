import shutil
import socket
import subprocess
import time
from pathlib import Path

import httpx
import pytest

pytestmark = pytest.mark.skipif(shutil.which("docker") is None, reason="Docker is not available")

IMAGE_TAG = "dev-standards-mcp:pytest-integration"
PROJECT_ROOT = Path(__file__).resolve().parent.parent


def test_docker_build_and_mcp_health_check() -> None:
    subprocess.run(
        ["docker", "build", "-t", IMAGE_TAG, "."],
        cwd=PROJECT_ROOT,
        check=True,
        capture_output=True,
        timeout=300,
    )

    port = _free_port()
    result = subprocess.run(
        ["docker", "run", "-d", "--rm", "-p", f"{port}:8000", IMAGE_TAG],
        cwd=PROJECT_ROOT,
        check=True,
        capture_output=True,
        text=True,
        timeout=30,
    )
    container_id = result.stdout.strip()

    try:
        response = _wait_for_mcp_response(port)
        assert response.status_code == 200
        assert "serverInfo" in response.text
    finally:
        subprocess.run(["docker", "stop", container_id], check=False, capture_output=True, timeout=30)


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("", 0))
        return int(sock.getsockname()[1])


def _wait_for_mcp_response(port: int, timeout: float = 20.0) -> httpx.Response:
    deadline = time.monotonic() + timeout
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2025-06-18",
            "capabilities": {},
            "clientInfo": {"name": "pytest-integration", "version": "1.0"},
        },
    }
    headers = {"Accept": "application/json, text/event-stream"}
    last_error: Exception | None = None
    while time.monotonic() < deadline:
        try:
            return httpx.post(f"http://localhost:{port}/mcp", json=payload, headers=headers, timeout=5.0)
        except httpx.TransportError as exc:
            last_error = exc
            time.sleep(0.5)
    raise TimeoutError(f"MCP server did not become ready in time: {last_error}")
