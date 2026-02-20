"""Slack application — dummy MCP server simulating a Slack workspace."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta

from fastmcp import FastMCP

# ---------------------------------------------------------------------------
# Dummy seed data
# ---------------------------------------------------------------------------

_NOW = datetime(2026, 2, 20, 17, 0, 0)


def _ts(minutes_ago: int) -> str:
    return (_NOW - timedelta(minutes=minutes_ago)).isoformat()


_USERS: dict[str, dict] = {
    "U001": {
        "id": "U001",
        "name": "alice",
        "display_name": "Alice Chen",
        "email": "alice@example.com",
        "status": "active",
    },
    "U002": {"id": "U002", "name": "bob", "display_name": "Bob Smith", "email": "bob@example.com", "status": "active"},
    "U003": {
        "id": "U003",
        "name": "carol",
        "display_name": "Carol Jones",
        "email": "carol@example.com",
        "status": "away",
    },
    "U004": {
        "id": "U004",
        "name": "dave",
        "display_name": "Dave Park",
        "email": "dave@example.com",
        "status": "active",
    },
    "U005": {"id": "U005", "name": "eve", "display_name": "Eve Kumar", "email": "eve@example.com", "status": "offline"},
}

_CHANNELS: dict[str, dict] = {
    "C001": {
        "id": "C001",
        "name": "general",
        "topic": "Company-wide announcements and discussion",
        "is_private": False,
        "members": ["U001", "U002", "U003", "U004", "U005"],
    },
    "C002": {
        "id": "C002",
        "name": "engineering",
        "topic": "Engineering team discussions",
        "is_private": False,
        "members": ["U001", "U002", "U003", "U004"],
    },
    "C003": {
        "id": "C003",
        "name": "product",
        "topic": "Product roadmap and design",
        "is_private": False,
        "members": ["U001", "U003", "U005"],
    },
    "C004": {
        "id": "C004",
        "name": "random",
        "topic": "Non-work banter and fun stuff",
        "is_private": False,
        "members": ["U001", "U002", "U003", "U004", "U005"],
    },
    "C005": {
        "id": "C005",
        "name": "incident-response",
        "topic": "On-call and incident management",
        "is_private": True,
        "members": ["U001", "U002", "U004"],
    },
}

_MESSAGES: list[dict] = [
    # #general
    {
        "id": "msg001",
        "channel": "C001",
        "user": "U001",
        "text": "Good morning everyone! Don't forget we have all-hands at 3pm today.",
        "timestamp": _ts(240),
        "reactions": [{"emoji": "wave", "count": 4}, {"emoji": "thumbsup", "count": 2}],
        "thread_ts": None,
    },
    {
        "id": "msg002",
        "channel": "C001",
        "user": "U003",
        "text": "Thanks Alice! I'll be joining remotely.",
        "timestamp": _ts(230),
        "reactions": [],
        "thread_ts": "msg001",
    },
    {
        "id": "msg003",
        "channel": "C001",
        "user": "U005",
        "text": "Reminder: Q1 OKR check-in docs are due by EOD Friday.",
        "timestamp": _ts(180),
        "reactions": [{"emoji": "check", "count": 5}],
        "thread_ts": None,
    },
    # #engineering
    {
        "id": "msg004",
        "channel": "C002",
        "user": "U002",
        "text": "PR #412 is ready for review — adds retry logic to the payment service.",
        "timestamp": _ts(120),
        "reactions": [{"emoji": "eyes", "count": 2}],
        "thread_ts": None,
    },
    {
        "id": "msg005",
        "channel": "C002",
        "user": "U001",
        "text": "On it! Looking now.",
        "timestamp": _ts(115),
        "reactions": [],
        "thread_ts": "msg004",
    },
    {
        "id": "msg006",
        "channel": "C002",
        "user": "U004",
        "text": "Heads up: prod deploy at 6pm. Please hold any merges from 5:30.",
        "timestamp": _ts(90),
        "reactions": [{"emoji": "thumbsup", "count": 3}],
        "thread_ts": None,
    },
    {
        "id": "msg007",
        "channel": "C002",
        "user": "U001",
        "text": "The CI pipeline is failing on the `main` branch due to a flaky test in auth_service. Investigating.",
        "timestamp": _ts(60),
        "reactions": [{"emoji": "pray", "count": 1}],
        "thread_ts": None,
    },
    {
        "id": "msg008",
        "channel": "C002",
        "user": "U002",
        "text": "Fixed! It was a race condition in the mock server setup. Pushed a fix.",
        "timestamp": _ts(45),
        "reactions": [{"emoji": "tada", "count": 4}, {"emoji": "rocket", "count": 2}],
        "thread_ts": "msg007",
    },
    # #product
    {
        "id": "msg009",
        "channel": "C003",
        "user": "U005",
        "text": "New Figma mockups for the onboarding flow are ready. Feedback welcome by Thursday.",
        "timestamp": _ts(300),
        "reactions": [{"emoji": "fire", "count": 3}],
        "thread_ts": None,
    },
    {
        "id": "msg010",
        "channel": "C003",
        "user": "U003",
        "text": "Love the new color scheme! One question — will the mobile version match exactly?",
        "timestamp": _ts(280),
        "reactions": [],
        "thread_ts": "msg009",
    },
    # #random
    {
        "id": "msg011",
        "channel": "C004",
        "user": "U004",
        "text": "Anyone catch the Warriors game last night? What a comeback!",
        "timestamp": _ts(400),
        "reactions": [{"emoji": "basketball", "count": 3}],
        "thread_ts": None,
    },
    {
        "id": "msg012",
        "channel": "C004",
        "user": "U002",
        "text": "Curry was on fire 🔥 38 points!",
        "timestamp": _ts(390),
        "reactions": [{"emoji": "fire", "count": 5}],
        "thread_ts": "msg011",
    },
    {
        "id": "msg013",
        "channel": "C004",
        "user": "U001",
        "text": "PSA: There are leftover donuts in the kitchen on the 3rd floor. First come first served!",
        "timestamp": _ts(50),
        "reactions": [{"emoji": "donut", "count": 8}, {"emoji": "running", "count": 3}],
        "thread_ts": None,
    },
    # #incident-response
    {
        "id": "msg014",
        "channel": "C005",
        "user": "U001",
        "text": "🚨 P1 incident: Payment service latency spike detected. p99 > 5s. Investigating.",
        "timestamp": _ts(30),
        "reactions": [],
        "thread_ts": None,
    },
    {
        "id": "msg015",
        "channel": "C005",
        "user": "U002",
        "text": "Confirmed — looks like the DB connection pool is exhausted. Rolling back last deploy.",
        "timestamp": _ts(25),
        "reactions": [],
        "thread_ts": "msg014",
    },
    {
        "id": "msg016",
        "channel": "C005",
        "user": "U004",
        "text": "Rollback complete. Latency returning to normal. Monitoring closely.",
        "timestamp": _ts(15),
        "reactions": [{"emoji": "phew", "count": 2}],
        "thread_ts": "msg014",
    },
]

_DMS: list[dict] = [
    {
        "id": "dm001",
        "participants": ["U001", "U002"],
        "text": "Hey Bob, can you review my PR when you get a chance?",
        "user": "U001",
        "timestamp": _ts(200),
    },
    {
        "id": "dm002",
        "participants": ["U001", "U002"],
        "text": "Sure! Give me 15 min.",
        "user": "U002",
        "timestamp": _ts(195),
    },
    {
        "id": "dm003",
        "participants": ["U001", "U003"],
        "text": "Carol, are you joining the design review tomorrow?",
        "user": "U001",
        "timestamp": _ts(150),
    },
    {
        "id": "dm004",
        "participants": ["U001", "U003"],
        "text": "Yes! Putting it on my calendar now.",
        "user": "U003",
        "timestamp": _ts(145),
    },
]


class SlackApp:
    """Dummy Slack workspace providing tools to read channels, messages, and users."""

    def __init__(self) -> None:
        self.name = "slack"
        self._channels: dict[str, dict] = dict(_CHANNELS)
        self._messages: list[dict] = list(_MESSAGES)
        self._dms: list[dict] = list(_DMS)
        self._users: dict[str, dict] = dict(_USERS)

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
