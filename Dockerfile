FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH="/app/.venv/bin:$PATH" \
    MCP_HOST=0.0.0.0 \
    MCP_PORT=8000

COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-install-project --no-dev

COPY main.py ./
COPY src/ ./src/
COPY sample-knowledge/ ./sample-knowledge/
RUN uv sync --locked --no-dev

EXPOSE 8000

CMD ["python", "main.py"]
