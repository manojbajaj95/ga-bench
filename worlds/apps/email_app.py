"""Email application — dummy MCP server exposing email tools."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Literal

from fastmcp import FastMCP

from worlds.utils import load_seed_data

# ---------------------------------------------------------------------------
# Dummy seed data
# ---------------------------------------------------------------------------

_FOLDERS = {"inbox", "sent", "drafts", "spam", "trash", "archive"}


class EmailApp:
    """Dummy email application providing tools to read, search, and manage emails."""

    def __init__(self) -> None:
        self.name = "email"
        self.data = load_seed_data("email")
        self._emails: dict[str, dict] = self.data["_EMAILS"]

    # ------------------------------------------------------------------
    # Tools
    # ------------------------------------------------------------------

    def list_emails(
        self,
        folder: str = "inbox",
        limit: int = 10,
        unread_only: bool = False,
    ) -> list[dict]:
        """List emails in a folder.

        Args:
            folder: Folder to list emails from (inbox, sent, drafts, spam, trash, archive).
            limit: Maximum number of emails to return (default 10).
            unread_only: When True, return only unread emails.

        Returns:
            list[dict]: List of email summary dicts with id, from, subject, timestamp, read.

        Tags:
            email, list, inbox, folder, read
        """
        results = [
            {k: v for k, v in msg.items() if k != "body"}
            for msg in self._emails.values()
            if msg["folder"] == folder and (not unread_only or not msg["read"])
        ]
        results.sort(key=lambda m: m["timestamp"], reverse=True)
        return results[:limit]

    def get_email(self, email_id: str) -> dict:
        """Retrieve a single email by its ID, including the full body.

        Args:
            email_id: The unique ID of the email.

        Returns:
            dict: Full email dict or an error dict if not found.

        Tags:
            email, get, read, body, detail
        """
        email = self._emails.get(email_id)
        if email is None:
            return {"error": f"Email '{email_id}' not found."}
        return dict(email)

    def mark_as_read(self, email_id: str) -> dict:
        """Mark an email as read.

        Args:
            email_id: The unique ID of the email to mark as read.

        Returns:
            dict: Updated email summary or error dict.

        Tags:
            email, mark, read, status, update
        """
        email = self._emails.get(email_id)
        if email is None:
            return {"error": f"Email '{email_id}' not found."}
        email["read"] = True
        return {"id": email_id, "read": True, "status": "updated"}

    def search_emails(self, query: str, folder: str | None = None) -> list[dict]:
        """Search emails by keyword in subject or body.

        Args:
            query: Search string matched against subject and body (case-insensitive).
            folder: Optional folder to restrict the search to.

        Returns:
            list[dict]: Matching email summaries (without body).

        Tags:
            email, search, query, find, filter
        """
        q = query.lower()
        results = []
        for msg in self._emails.values():
            if folder and msg["folder"] != folder:
                continue
            if q in msg["subject"].lower() or q in msg["body"].lower():
                results.append({k: v for k, v in msg.items() if k != "body"})
        results.sort(key=lambda m: m["timestamp"], reverse=True)
        return results

    def send_email(self, to: list[str], subject: str, body: str) -> dict:
        """Send a new email.

        Args:
            to: List of recipient email addresses.
            subject: Email subject line.
            body: Plain-text email body.

        Returns:
            dict: Confirmation with the newly created email id.

        Tags:
            email, send, compose, create, outbox
        """
        email_id = str(uuid.uuid4())[:8]
        self._emails[email_id] = {
            "id": email_id,
            "from": "me@example.com",
            "to": to,
            "subject": subject,
            "body": body,
            "folder": "sent",
            "read": True,
            "timestamp": datetime.now().isoformat(),
        }
        return {"id": email_id, "status": "sent"}

    def delete_email(self, email_id: str) -> dict:
        """Delete an email by moving it to the trash folder.

        Args:
            email_id: The unique ID of the email to delete.

        Returns:
            dict: Confirmation or error dict.

        Tags:
            email, delete, trash, remove
        """
        email = self._emails.get(email_id)
        if email is None:
            return {"error": f"Email '{email_id}' not found."}
        if email["folder"] == "trash":
            return {"id": email_id, "status": "already in trash"}
        email["folder"] = "trash"
        return {"id": email_id, "status": "moved to trash"}

    def move_email(
        self,
        email_id: str,
        folder: Literal["inbox", "sent", "drafts", "spam", "trash", "archive"],
    ) -> dict:
        """Move an email to a different folder.

        Args:
            email_id: The unique ID of the email to move.
            folder: Target folder name.

        Returns:
            dict: Confirmation with old and new folder, or error dict.

        Tags:
            email, move, folder, organize, archive
        """
        email = self._emails.get(email_id)
        if email is None:
            return {"error": f"Email '{email_id}' not found."}
        old_folder = email["folder"]
        email["folder"] = folder
        return {"id": email_id, "from_folder": old_folder, "to_folder": folder, "status": "moved"}

    def get_folders(self) -> list[dict]:
        """List all folders with unread and total email counts.

        Returns:
            list[dict]: Each entry has folder name, total count, and unread count.

        Tags:
            email, folders, inbox, counts, summary
        """
        counts: dict[str, dict] = {f: {"folder": f, "total": 0, "unread": 0} for f in _FOLDERS}
        for msg in self._emails.values():
            folder = msg["folder"]
            if folder not in counts:
                counts[folder] = {"folder": folder, "total": 0, "unread": 0}
            counts[folder]["total"] += 1
            if not msg["read"]:
                counts[folder]["unread"] += 1
        return sorted(counts.values(), key=lambda x: x["folder"])

    # ------------------------------------------------------------------

    def list_tools(self) -> list:
        """Return all tool methods exposed by this application.

        Returns:
            list: Callable tool methods.
        """
        return [
            self.list_emails,
            self.get_email,
            self.mark_as_read,
            self.search_emails,
            self.send_email,
            self.delete_email,
            self.move_email,
            self.get_folders,
        ]

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
    app = EmailApp()
    server = app.create_mcp_server()
    server.run()
