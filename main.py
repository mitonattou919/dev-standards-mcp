from src.api.server import create_server


def main() -> None:  # pragma: no cover
    create_server().run(transport="http", host="127.0.0.1", port=8000, path="/mcp")


if __name__ == "__main__":
    main()
