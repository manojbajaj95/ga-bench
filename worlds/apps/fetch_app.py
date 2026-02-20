"""Fetch application — MCP server for real HTTP requests to the web."""

from __future__ import annotations

import urllib.error
import urllib.request
from html.parser import HTMLParser

from fastmcp import FastMCP

# ---------------------------------------------------------------------------
# HTML → plain text stripper
# ---------------------------------------------------------------------------


class _HTMLStripper(HTMLParser):
    """Minimal HTML-to-text converter."""

    _SKIP_TAGS = {"script", "style", "head", "meta", "link", "noscript"}

    def __init__(self) -> None:
        super().__init__()
        self._skip = False
        self._skip_stack: list[str] = []
        self._parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list) -> None:
        if tag in self._SKIP_TAGS:
            self._skip_stack.append(tag)
        if tag in {"p", "br", "div", "h1", "h2", "h3", "h4", "li", "tr"}:
            self._parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if self._skip_stack and self._skip_stack[-1] == tag:
            self._skip_stack.pop()

    def handle_data(self, data: str) -> None:
        if not self._skip_stack:
            self._parts.append(data)

    def get_text(self) -> str:
        raw = "".join(self._parts)
        lines = [line.strip() for line in raw.splitlines()]
        # collapse blank lines
        result: list[str] = []
        blank = False
        for line in lines:
            if line:
                result.append(line)
                blank = False
            elif not blank:
                result.append("")
                blank = True
        return "\n".join(result).strip()


def _fetch_url(url: str, timeout: int = 10) -> tuple[str, str, int]:
    """Return (content, content_type, status_code). Raises on network error."""
    req = urllib.request.Request(
        url,
        headers={"User-Agent": ("Mozilla/5.0 (compatible; ga-bench-fetch/1.0; +https://github.com/example/ga-bench)")},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310
        status = resp.status
        ctype: str = resp.headers.get("Content-Type", "text/plain")
        raw = resp.read()
    content = raw.decode("utf-8", errors="replace")
    return content, ctype, status


class FetchApp:
    """Real HTTP fetch application — retrieves live content from the web."""

    def __init__(self) -> None:
        self.name = "fetch"

    # ------------------------------------------------------------------
    # Tools
    # ------------------------------------------------------------------

    def get(
        self,
        url: str,
        as_text: bool = True,
        max_chars: int = 8000,
        timeout: int = 10,
    ) -> dict:
        """Fetch the contents of any public URL over HTTP/HTTPS.

        Args:
            url: Fully-qualified URL to fetch (must start with http:// or https://).
            as_text: When True (default), strips HTML tags and returns plain text.
                     When False, returns raw response body (useful for JSON APIs).
            max_chars: Maximum number of characters to return (default 8000).
                       Longer responses are truncated.
            timeout: Request timeout in seconds (default 10, max 30).

        Returns:
            dict: Contains 'url', 'status_code', 'content_type', 'content', and
                  'truncated' (bool). Returns error dict on failure.

        Tags:
            fetch, http, web, url, get, request
        """
        if not url.startswith(("http://", "https://")):
            return {"error": "URL must start with http:// or https://"}
        timeout = min(timeout, 30)
        try:
            body, ctype, status = _fetch_url(url, timeout=timeout)
        except urllib.error.HTTPError as exc:
            return {"error": f"HTTP {exc.code}: {exc.reason}", "url": url, "status_code": exc.code}
        except urllib.error.URLError as exc:
            return {"error": f"Network error: {exc.reason}", "url": url}
        except TimeoutError:
            return {"error": f"Request timed out after {timeout}s", "url": url}
        except Exception as exc:  # noqa: BLE001
            return {"error": f"Unexpected error: {exc}", "url": url}

        is_html = "html" in ctype.lower()
        if as_text and is_html:
            stripper = _HTMLStripper()
            stripper.feed(body)
            content = stripper.get_text()
        else:
            content = body

        truncated = len(content) > max_chars
        return {
            "url": url,
            "status_code": status,
            "content_type": ctype,
            "content": content[:max_chars],
            "truncated": truncated,
        }

    def head(self, url: str, timeout: int = 10) -> dict:
        """Fetch only the HTTP headers for a URL without downloading the body.

        Args:
            url: Fully-qualified URL to check.
            timeout: Request timeout in seconds (default 10).

        Returns:
            dict: Contains 'url', 'status_code', 'content_type', 'content_length',
                  and 'headers' dict. Returns error dict on failure.

        Tags:
            fetch, http, head, headers, check, url
        """
        if not url.startswith(("http://", "https://")):
            return {"error": "URL must start with http:// or https://"}
        timeout = min(timeout, 30)
        try:
            req = urllib.request.Request(
                url,
                method="HEAD",
                headers={"User-Agent": "Mozilla/5.0 (compatible; ga-bench-fetch/1.0)"},
            )
            with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310
                headers = dict(resp.headers)
                return {
                    "url": url,
                    "status_code": resp.status,
                    "content_type": headers.get("Content-Type", "unknown"),
                    "content_length": headers.get("Content-Length", "unknown"),
                    "headers": headers,
                }
        except urllib.error.HTTPError as exc:
            return {"error": f"HTTP {exc.code}: {exc.reason}", "url": url, "status_code": exc.code}
        except urllib.error.URLError as exc:
            return {"error": f"Network error: {exc.reason}", "url": url}
        except Exception as exc:  # noqa: BLE001
            return {"error": f"Unexpected error: {exc}", "url": url}

    def get_json(self, url: str, timeout: int = 10) -> dict:
        """Fetch a JSON endpoint and return the parsed response.

        Args:
            url: URL of a JSON API endpoint.
            timeout: Request timeout in seconds (default 10, max 30).

        Returns:
            dict: Contains 'url', 'status_code', and 'data' (parsed JSON). Returns
                  error dict on failure or if response is not valid JSON.

        Tags:
            fetch, json, api, http, request, parse
        """
        result = self.get(url, as_text=False, max_chars=100_000, timeout=timeout)
        if "error" in result:
            return result
        import json

        try:
            data = json.loads(result["content"])
        except json.JSONDecodeError as exc:
            return {"error": f"Response is not valid JSON: {exc}", "url": url}
        return {"url": url, "status_code": result["status_code"], "data": data}

    # ------------------------------------------------------------------

    def list_tools(self) -> list:
        return [self.get, self.head, self.get_json]

    def create_mcp_server(self) -> FastMCP:
        mcp = FastMCP(self.name)
        for tool_fn in self.list_tools():
            mcp.tool()(tool_fn)
        return mcp


if __name__ == "__main__":
    app = FetchApp()
    server = app.create_mcp_server()
    server.run()
