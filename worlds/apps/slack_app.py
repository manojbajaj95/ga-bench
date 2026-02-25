"""Slack application — dummy MCP server simulating a Slack workspace."""

from __future__ import annotations

import uuid
from datetime import datetime

from fastmcp import FastMCP

from worlds.utils import load_seed_data


class SlackApp:
    """Dummy Slack workspace providing tools to read channels, messages, and users."""

    def __init__(self) -> None:
        self.name = "slack"
        self.data = load_seed_data("slack")
        self._channels: dict[str, dict] = self.data["_CHANNELS"]
        self._messages: list[dict] = self.data["_MESSAGES"]
        self._dms: list[dict] = self.data["_DMS"]
        self._users: dict[str, dict] = self.data["_USERS"]

    # ------------------------------------------------------------------
    # Tools
    # ------------------------------------------------------------------

    def list_channels(self, include_private: bool = False) -> list[dict]:
        """List all Slack channels in the workspace.

        Args:
            include_private: When True, also return private channels. Default False.

        Returns:
            list[dict]: Channels with id, name, topic, is_private, and member count.

        Tags:
            slack, channels, list, workspace
        """
        results = []
        for ch in self._channels.values():
            if not include_private and ch["is_private"]:
                continue
            results.append(
                {
                    "id": ch["id"],
                    "name": ch["name"],
                    "topic": ch["topic"],
                    "is_private": ch["is_private"],
                    "member_count": len(ch["members"]),
                }
            )
        return results

    def get_channel_messages(
        self,
        channel_id: str,
        limit: int = 10,
        include_threads: bool = False,
    ) -> list[dict]:
        """Retrieve recent messages from a Slack channel.

        Args:
            channel_id: The channel ID (e.g. 'C001').
            limit: Maximum number of messages to return (default 10).
            include_threads: When True, include thread replies alongside top-level messages.

        Returns:
            list[dict]: Messages sorted newest first with id, user, text, timestamp, reactions.
                        Returns error dict if channel not found.

        Tags:
            slack, messages, channel, read, history
        """
        if channel_id not in self._channels:
            return [{"error": f"Channel '{channel_id}' not found."}]
        msgs = [m for m in self._messages if m["channel"] == channel_id and (include_threads or m["thread_ts"] is None)]
        msgs.sort(key=lambda m: m["timestamp"], reverse=True)
        return [{k: v for k, v in m.items() if k != "channel"} for m in msgs[:limit]]

    def get_thread(self, parent_message_id: str) -> list[dict]:
        """Get all replies in a message thread.

        Args:
            parent_message_id: The ID of the parent (top-level) message.

        Returns:
            list[dict]: Thread messages ordered oldest first, including the parent.

        Tags:
            slack, thread, replies, messages, read
        """
        parent = next((m for m in self._messages if m["id"] == parent_message_id), None)
        if parent is None:
            return [{"error": f"Message '{parent_message_id}' not found."}]
        replies = [m for m in self._messages if m["thread_ts"] == parent_message_id]
        thread = [parent] + sorted(replies, key=lambda m: m["timestamp"])
        return [{k: v for k, v in m.items() if k != "channel"} for m in thread]

    def send_message(self, channel_id: str, text: str, thread_ts: str | None = None) -> dict:
        """Send a message to a Slack channel or reply in a thread.

        Args:
            channel_id: The channel ID to post to.
            text: The message text.
            thread_ts: Optional parent message ID to reply in a thread.

        Returns:
            dict: Confirmation with the new message id and timestamp.

        Tags:
            slack, send, post, message, write
        """
        if channel_id not in self._channels:
            return {"error": f"Channel '{channel_id}' not found."}
        msg_id = f"msg{uuid.uuid4().hex[:6]}"
        msg = {
            "id": msg_id,
            "channel": channel_id,
            "user": "U002",  # current user is bob
            "text": text,
            "timestamp": datetime.now().isoformat(),
            "reactions": [],
            "thread_ts": thread_ts,
        }
        self._messages.append(msg)
        return {"id": msg_id, "timestamp": msg["timestamp"], "status": "sent"}

    def search_messages(self, query: str, channel_id: str | None = None) -> list[dict]:
        """Search for messages across channels by keyword.

        Args:
            query: Search string matched against message text (case-insensitive).
            channel_id: Optional channel ID to restrict the search.

        Returns:
            list[dict]: Matching messages sorted newest first.

        Tags:
            slack, search, messages, find, query
        """
        q = query.lower()
        results = [
            m for m in self._messages if q in m["text"].lower() and (channel_id is None or m["channel"] == channel_id)
        ]
        results.sort(key=lambda m: m["timestamp"], reverse=True)
        return [{k: v for k, v in m.items() if k != "channel"} for m in results]

    def list_users(self, status: str | None = None) -> list[dict]:
        """List workspace users, optionally filtered by status.

        Args:
            status: Filter by status: 'active', 'away', or 'offline'. None returns all.

        Returns:
            list[dict]: Users with id, name, display_name, email, and status.

        Tags:
            slack, users, list, workspace, people
        """
        users = list(self._users.values())
        if status:
            users = [u for u in users if u["status"] == status]
        return users

    def get_direct_messages(self, user_id: str) -> list[dict]:
        """Get direct message history with a specific user.

        Args:
            user_id: The ID of the other user in the DM conversation.

        Returns:
            list[dict]: DM messages sorted oldest first.

        Tags:
            slack, dm, direct, messages, private
        """
        dms = [m for m in self._dms if user_id in m["participants"]]
        dms.sort(key=lambda m: m["timestamp"])
        return dms

    def add_reaction(self, message_id: str, emoji: str) -> dict:
        """Add an emoji reaction to a message.

        Args:
            message_id: The ID of the message to react to.
            emoji: Emoji name without colons (e.g. 'thumbsup', 'fire').

        Returns:
            dict: Confirmation or error dict.

        Tags:
            slack, reaction, emoji, message, interact
        """
        msg = next((m for m in self._messages if m["id"] == message_id), None)
        if msg is None:
            return {"error": f"Message '{message_id}' not found."}
        for r in msg["reactions"]:
            if r["emoji"] == emoji:
                r["count"] += 1
                return {"message_id": message_id, "emoji": emoji, "count": r["count"]}
        msg["reactions"].append({"emoji": emoji, "count": 1})
        return {"message_id": message_id, "emoji": emoji, "count": 1}

    # ------------------------------------------------------------------

    def list_tools(self) -> list:
        return [
            self.list_channels,
            self.get_channel_messages,
            self.get_thread,
            self.send_message,
            self.search_messages,
            self.list_users,
            self.get_direct_messages,
            self.add_reaction,
        ]

    def create_mcp_server(self) -> FastMCP:
        mcp = FastMCP(self.name)
        for tool_fn in self.list_tools():
            mcp.tool()(tool_fn)
        return mcp


if __name__ == "__main__":
    app = SlackApp()
    server = app.create_mcp_server()
    server.run()
