from src.api.server import create_server
from src.api.settings import load_settings


def main() -> None:  # pragma: no cover
    settings = load_settings()
    create_server().run(transport="http", host=settings.host, port=settings.port, path="/mcp")


if __name__ == "__main__":
    main()
