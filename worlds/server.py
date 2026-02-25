"""Main MCP world server — mounts all application sub-servers."""

from fastmcp import FastMCP

from worlds.apps.arxiv_app import ArxivApp
from worlds.apps.calculator_app import CalculatorApp
from worlds.apps.calendar_app import CalendarApp
from worlds.apps.docs_app import DocsApp
from worlds.apps.email_app import EmailApp
from worlds.apps.fetch_app import FetchApp
from worlds.apps.github_app import GitHubApp
from worlds.apps.reddit_app import RedditApp
from worlds.apps.slack_app import SlackApp
from worlds.apps.sqlite_app import SQLiteApp
from worlds.apps.web_search_app import WebSearchApp
from worlds.apps.yahoo_finance_app import YahooFinanceApp

# ---------------------------------------------------------------------------
# Build sub-servers from app instances
# ---------------------------------------------------------------------------

_apps = [
    EmailApp(),
    CalendarApp(),
    WebSearchApp(),
    SlackApp(),
    ArxivApp(),
    FetchApp(),
    YahooFinanceApp(),
    DocsApp(),
    CalculatorApp(),
    SQLiteApp(),
    RedditApp(),
    GitHubApp(),
    #    FilesApp(),
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
