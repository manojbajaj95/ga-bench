"""Main MCP world server — mounts all application sub-servers."""

from fastmcp import FastMCP

from worlds.apps.calendar_app import CalendarApp
from worlds.apps.email_app import EmailApp

# ---------------------------------------------------------------------------
# Build sub-servers from app instances
# ---------------------------------------------------------------------------

_apps = [
    EmailApp(),
    CalendarApp(),
]

# ---------------------------------------------------------------------------
# Main server — mount each sub-server under its app name as namespace
# ---------------------------------------------------------------------------

main = FastMCP("World")

for app in _apps:
    sub = app.create_mcp_server()
    main.mount(sub, namespace=app.name)

# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    main.run(transport="http", port=args.port)
