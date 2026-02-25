# WORLD SERVER & APPS

## OVERVIEW
Simulates the operating environment (Email, Calendar, File System) using the Model Context Protocol (MCP).

## STRUCTURE
```
worlds/
├── server.py           # Main server (FastMCP), mounts apps
└── apps/               # Individual apps (Tools)
    ├── email_app.py    # Email tools
    ├── calendar_app.py # Calendar tools
    └── ...
```

## APP PATTERN
Each app is a class:
```python
class MyApp:
    def __init__(self):
        self.name = "myapp" # Namespace prefix

    def list_tools(self): ...
    def create_mcp_server(self): ... # Returns FastMCP
```

## CONVENTIONS
- **Namespacing**: Tools become `<appname>_<method>` (e.g., `email_list`).
- **State**: In-memory state (dicts) persists for the server lifecycle.
- **Seed Data**: Initialize with realistic dummy data (`_EMAILS`, etc.).
- **Docstrings**: CRITICAL. Used as tool descriptions for the agent.

## INFRASTRUCTURE
- **Port**: `7331` (fixed in `run.py`).
- **Transport**: SSE / HTTP.
- **Lifecycle**: Started by `run.py`, killed after run.
