"""Files application — MCP server for reading local files from the filesystem."""

from __future__ import annotations

import csv
import io
import os

from fastmcp import FastMCP

# Directories the tool is allowed to read from (prefix-matched).
_ALLOWED_PREFIXES = (
    os.path.abspath("tasks/"),
    os.path.abspath("worlds/"),
    "/tmp/",
)


def _allowed(path: str) -> bool:
    abs_path = os.path.abspath(path)
    return any(abs_path.startswith(p) for p in _ALLOWED_PREFIXES)


class FilesApp:
    """Local filesystem reader — exposes tools to read text and CSV files."""

    def __init__(self) -> None:
        self.name = "files"

    # ------------------------------------------------------------------
    # Tools
    # ------------------------------------------------------------------

    def read_text(self, path: str, max_chars: int = 20000) -> dict:
        """Read a local text file and return its contents as a string.

        Args:
            path: Absolute or relative path to the file. Must be inside the
                  tasks/ or worlds/ directory tree.
            max_chars: Maximum number of characters to return (default 20000).
                       Longer files are truncated.

        Returns:
            dict: Contains 'path', 'content', 'size_bytes', and 'truncated' (bool).
                  Returns error dict if the file cannot be read.

        Tags:
            files, read, text, local, filesystem
        """
        if not _allowed(path):
            return {"error": f"Access denied: '{path}' is outside the allowed directory."}
        try:
            size = os.path.getsize(path)
        except OSError as exc:
            return {"error": str(exc), "path": path}
        try:
            with open(path, encoding="utf-8", errors="replace") as fh:
                content = fh.read(max_chars + 1)
        except OSError as exc:
            return {"error": str(exc), "path": path}
        truncated = len(content) > max_chars
        return {
            "path": path,
            "content": content[:max_chars],
            "size_bytes": size,
            "truncated": truncated,
        }

    def read_csv(self, path: str, max_rows: int = 500) -> dict:
        """Read a CSV file and return its rows as a list of dicts.

        Args:
            path: Absolute or relative path to the CSV file. Must be inside the
                  tasks/ or worlds/ directory tree.
            max_rows: Maximum number of data rows to return (default 500, excludes header).

        Returns:
            dict: Contains 'path', 'headers' (list of column names), 'rows' (list of
                  dicts keyed by header), 'total_rows' (int), and 'truncated' (bool).
                  Returns error dict if the file cannot be read or parsed.

        Tags:
            files, read, csv, table, data, parse
        """
        if not _allowed(path):
            return {"error": f"Access denied: '{path}' is outside the allowed directory."}
        try:
            with open(path, encoding="utf-8", errors="replace") as fh:
                raw = fh.read()
        except OSError as exc:
            return {"error": str(exc), "path": path}
        try:
            reader = csv.DictReader(io.StringIO(raw))
            headers = reader.fieldnames or []
            all_rows = list(reader)
        except csv.Error as exc:
            return {"error": f"CSV parse error: {exc}", "path": path}
        total = len(all_rows)
        truncated = total > max_rows
        return {
            "path": path,
            "headers": list(headers),
            "rows": all_rows[:max_rows],
            "total_rows": total,
            "truncated": truncated,
        }

    def list_files(self, directory: str, extension: str | None = None) -> dict:
        """List files in a directory, optionally filtered by extension.

        Args:
            directory: Path to the directory to list. Must be inside tasks/ or worlds/.
            extension: Optional file extension to filter by (e.g. '.csv', '.json').

        Returns:
            dict: Contains 'directory' and 'files' (list of dicts with name, path,
                  size_bytes). Returns error dict if directory cannot be listed.

        Tags:
            files, list, directory, browse, filesystem
        """
        if not _allowed(directory):
            return {"error": f"Access denied: '{directory}' is outside the allowed directory."}
        try:
            entries = os.listdir(directory)
        except OSError as exc:
            return {"error": str(exc), "directory": directory}
        files = []
        for entry in sorted(entries):
            if extension and not entry.endswith(extension):
                continue
            full = os.path.join(directory, entry)
            if os.path.isfile(full):
                files.append({"name": entry, "path": full, "size_bytes": os.path.getsize(full)})
        return {"directory": directory, "files": files}

    # ------------------------------------------------------------------

    def list_tools(self) -> list:
        """Return all tool methods exposed by this application."""
        return [self.read_text, self.read_csv, self.list_files]

    def create_mcp_server(self) -> FastMCP:
        """Create and return a FastMCP server with all tools registered."""
        mcp = FastMCP(self.name)
        for tool_fn in self.list_tools():
            mcp.tool()(tool_fn)
        return mcp


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app = FilesApp()
    server = app.create_mcp_server()
    server.run()
