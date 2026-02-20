"""Docs application — in-memory document store MCP server."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta

from fastmcp import FastMCP

# ---------------------------------------------------------------------------
# Dummy seed data
# ---------------------------------------------------------------------------

_NOW = datetime(2026, 2, 20, 17, 0, 0)


def _ago(days: int = 0, hours: int = 0) -> str:
    return (_NOW - timedelta(days=days, hours=hours)).isoformat()


_SEED_DOCS: list[dict] = [
    {
        "id": "doc001",
        "title": "Q1 2026 OKR Review",
        "content": (
            "# Q1 2026 OKR Review\n\n"
            "## Objective 1: Launch v2.0 of the platform\n"
            "- KR1: Ship 3 major features — **2/3 complete**\n"
            "- KR2: Reduce API latency p99 < 200ms — **On track (currently 245ms)**\n"
            "- KR3: Achieve 99.9% uptime — **Met (99.92%)**\n\n"
            "## Objective 2: Grow user base\n"
            "- KR1: Reach 50K DAU — **38K (76%)**\n"
            "- KR2: Reduce churn below 3% — **3.4% (needs work)**\n"
        ),
        "owner": "alice@example.com",
        "tags": ["okr", "q1", "review", "planning"],
        "folder": "Planning",
        "created_at": _ago(days=30),
        "updated_at": _ago(days=2),
    },
    {
        "id": "doc002",
        "title": "Engineering Onboarding Guide",
        "content": (
            "# Engineering Onboarding Guide\n\n"
            "Welcome to the team! This guide covers your first two weeks.\n\n"
            "## Week 1: Setup\n"
            "1. Request GitHub, Slack, and AWS access from IT\n"
            "2. Clone the main repo: `git clone git@github.com:acme/platform.git`\n"
            "3. Follow `README.md` to get your dev environment running\n"
            "4. Shadow a teammate for 2 days\n\n"
            "## Week 2: Ramp\n"
            "1. Pick up a 'good first issue' from the backlog\n"
            "2. Attend sprint planning and standup\n"
            "3. Complete your first PR and get it merged\n"
        ),
        "owner": "carol@example.com",
        "tags": ["onboarding", "engineering", "guide"],
        "folder": "HR",
        "created_at": _ago(days=90),
        "updated_at": _ago(days=14),
    },
    {
        "id": "doc003",
        "title": "Architecture Decision Record: Move to Microservices",
        "content": (
            "# ADR-014: Migrate Monolith to Microservices\n\n"
            "**Status:** Accepted\n"
            "**Date:** 2026-01-15\n\n"
            "## Context\n"
            "The monolith has grown to 500K LOC. Deploy times exceed 45 minutes. "
            "Teams are stepping on each other's changes.\n\n"
            "## Decision\n"
            "Incrementally extract services starting with: Auth, Payments, and Notifications.\n\n"
            "## Consequences\n"
            "- (+) Independent deployability per service\n"
            "- (+) Team autonomy\n"
            "- (-) Increased operational complexity (service mesh, distributed tracing)\n"
            "- (-) Network latency between services\n"
        ),
        "owner": "bob@example.com",
        "tags": ["adr", "architecture", "microservices", "engineering"],
        "folder": "Engineering",
        "created_at": _ago(days=36),
        "updated_at": _ago(days=36),
    },
    {
        "id": "doc004",
        "title": "Product Roadmap H1 2026",
        "content": (
            "# Product Roadmap — H1 2026\n\n"
            "## February\n"
            "- Launch redesigned onboarding flow\n"
            "- A/B test new pricing page\n\n"
            "## March\n"
            "- Release mobile app v3.0 (iOS + Android)\n"
            "- Integrate Stripe for payments\n\n"
            "## April\n"
            "- Launch team collaboration features\n"
            "- API v2 public release\n\n"
            "## May–June\n"
            "- Enterprise SSO support\n"
            "- Analytics dashboard v2\n"
            "- Data export (CSV, Parquet)\n"
        ),
        "owner": "eve@example.com",
        "tags": ["roadmap", "product", "h1", "2026"],
        "folder": "Product",
        "created_at": _ago(days=20),
        "updated_at": _ago(hours=6),
    },
    {
        "id": "doc005",
        "title": "Incident Post-Mortem: Payment Outage 2026-02-15",
        "content": (
            "# Post-Mortem: Payment Service Outage\n"
            "**Date:** 2026-02-15 | **Duration:** 47 minutes | **Severity:** P1\n\n"
            "## Summary\n"
            "Payment processing was unavailable for 47 minutes due to a DB connection pool exhaustion "
            "triggered by a misconfigured deploy.\n\n"
            "## Timeline\n"
            "- 14:32 — Deploy v2.4.1 to production\n"
            "- 14:38 — Alerts fire: p99 latency > 5s\n"
            "- 14:41 — On-call acknowledges incident\n"
            "- 14:58 — Root cause identified: max_connections set to 5 instead of 50\n"
            "- 15:19 — Rollback complete, service restored\n\n"
            "## Action Items\n"
            "1. Add config validation in CI pipeline (owner: alice, due: 2026-02-22)\n"
            "2. Lower alert threshold to p99 > 1s (owner: bob, due: 2026-02-20)\n"
            "3. Add runbook for DB connection pool issues (owner: carol, due: 2026-03-01)\n"
        ),
        "owner": "alice@example.com",
        "tags": ["post-mortem", "incident", "payments", "outage"],
        "folder": "Engineering",
        "created_at": _ago(days=5),
        "updated_at": _ago(days=4),
    },
    {
        "id": "doc006",
        "title": "Meeting Notes: All-Hands Feb 20, 2026",
        "content": (
            "# All-Hands Meeting Notes\n"
            "**Date:** 2026-02-20 | **Facilitator:** Alice Chen\n\n"
            "## Agenda\n"
            "1. Q1 progress update\n"
            "2. New hire introductions\n"
            "3. Office policy changes\n\n"
            "## Key Takeaways\n"
            "- Revenue is tracking 12% above forecast\n"
            "- Three new engineers joining next week: Dan, Mei, and Raj\n"
            "- New PTO policy: unlimited PTO effective March 1\n"
            "- Remote work policy updated: 2 days in-office required\n\n"
            "## Action Items\n"
            "- All managers to communicate new PTO policy by Feb 25\n"
            "- IT to provision accounts for new hires by Feb 24\n"
        ),
        "owner": "alice@example.com",
        "tags": ["meeting", "all-hands", "notes", "february"],
        "folder": "Meetings",
        "created_at": _ago(hours=2),
        "updated_at": _ago(hours=1),
    },
]


class DocsApp:
    """In-memory document store for creating, finding, and managing documents."""

    def __init__(self) -> None:
        self.name = "docs"
        self._docs: dict[str, dict] = {d["id"]: d for d in _SEED_DOCS}

    # ------------------------------------------------------------------
    # Tools
    # ------------------------------------------------------------------

    def list_docs(self, folder: str | None = None, limit: int = 20) -> list[dict]:
        """List documents, optionally filtered by folder.

        Args:
            folder: Folder name to filter by (e.g. 'Planning', 'Engineering',
                    'Product', 'HR', 'Meetings'). None returns all folders.
            limit: Maximum number of documents to return (default 20).

        Returns:
            list[dict]: Documents sorted newest-updated first, without content body.

        Tags:
            docs, list, documents, browse, folder
        """
        docs = list(self._docs.values())
        if folder:
            docs = [d for d in docs if d["folder"].lower() == folder.lower()]
        docs.sort(key=lambda d: d["updated_at"], reverse=True)
        return [{k: v for k, v in d.items() if k != "content"} for d in docs[:limit]]

    def get_doc(self, doc_id: str) -> dict:
        """Retrieve the full content of a document by its ID.

        Args:
            doc_id: The document ID (e.g. 'doc001').

        Returns:
            dict: Full document including content, or error dict if not found.

        Tags:
            docs, get, read, content, document
        """
        doc = self._docs.get(doc_id)
        if doc is None:
            return {"error": f"Document '{doc_id}' not found."}
        return dict(doc)

    def create_doc(
        self,
        title: str,
        content: str,
        folder: str = "General",
        tags: list[str] | None = None,
        owner: str = "me@example.com",
    ) -> dict:
        """Create a new document.

        Args:
            title: Document title.
            content: Document body — supports Markdown.
            folder: Folder to save the document in (default 'General').
            tags: Optional list of tag strings for categorization.
            owner: Owner email address (default 'me@example.com').

        Returns:
            dict: The newly created document (without content body).

        Tags:
            docs, create, new, write, document
        """
        doc_id = f"doc{uuid.uuid4().hex[:6]}"
        now = datetime.now().isoformat()
        doc = {
            "id": doc_id,
            "title": title,
            "content": content,
            "owner": owner,
            "tags": tags or [],
            "folder": folder,
            "created_at": now,
            "updated_at": now,
        }
        self._docs[doc_id] = doc
        return {k: v for k, v in doc.items() if k != "content"}

    def update_doc(
        self,
        doc_id: str,
        title: str | None = None,
        content: str | None = None,
        folder: str | None = None,
        tags: list[str] | None = None,
    ) -> dict:
        """Update an existing document's title, content, folder, or tags.

        Args:
            doc_id: The document ID to update.
            title: New title, or None to leave unchanged.
            content: New content body, or None to leave unchanged.
            folder: New folder, or None to leave unchanged.
            tags: New tag list, or None to leave unchanged.

        Returns:
            dict: Updated document metadata (without content), or error dict.

        Tags:
            docs, update, edit, modify, document
        """
        doc = self._docs.get(doc_id)
        if doc is None:
            return {"error": f"Document '{doc_id}' not found."}
        if title is not None:
            doc["title"] = title
        if content is not None:
            doc["content"] = content
        if folder is not None:
            doc["folder"] = folder
        if tags is not None:
            doc["tags"] = tags
        doc["updated_at"] = datetime.now().isoformat()
        return {k: v for k, v in doc.items() if k != "content"}

    def delete_doc(self, doc_id: str) -> dict:
        """Permanently delete a document.

        Args:
            doc_id: The document ID to delete.

        Returns:
            dict: Confirmation with deleted document title, or error dict.

        Tags:
            docs, delete, remove, document
        """
        doc = self._docs.pop(doc_id, None)
        if doc is None:
            return {"error": f"Document '{doc_id}' not found."}
        return {"id": doc_id, "title": doc["title"], "status": "deleted"}

    def search_docs(self, query: str, folder: str | None = None) -> list[dict]:
        """Search documents by keyword in title, content, or tags.

        Args:
            query: Search string (case-insensitive), matched against title, content, and tags.
            folder: Optional folder to restrict the search.

        Returns:
            list[dict]: Matching documents sorted by relevance, without content body.

        Tags:
            docs, search, find, query, keyword
        """
        q = query.lower()
        results = []
        for doc in self._docs.values():
            if folder and doc["folder"].lower() != folder.lower():
                continue
            score = 0
            if q in doc["title"].lower():
                score += 3
            if q in doc["content"].lower():
                score += 1
            if any(q in tag.lower() for tag in doc["tags"]):
                score += 2
            if score > 0:
                results.append((score, doc))
        results.sort(key=lambda x: x[0], reverse=True)
        return [{k: v for k, v in d.items() if k != "content"} for _, d in results]

    def list_folders(self) -> list[dict]:
        """List all folders with document counts.

        Returns:
            list[dict]: Folders sorted alphabetically with name and doc count.

        Tags:
            docs, folders, list, organize, browse
        """
        from collections import Counter

        counts: Counter[str] = Counter(d["folder"] for d in self._docs.values())
        return [{"folder": folder, "doc_count": count} for folder, count in sorted(counts.items())]

    # ------------------------------------------------------------------

    def list_tools(self) -> list:
        return [
            self.list_docs,
            self.get_doc,
            self.create_doc,
            self.update_doc,
            self.delete_doc,
            self.search_docs,
            self.list_folders,
        ]

    def create_mcp_server(self) -> FastMCP:
        mcp = FastMCP(self.name)
        for tool_fn in self.list_tools():
            mcp.tool()(tool_fn)
        return mcp


if __name__ == "__main__":
    app = DocsApp()
    server = app.create_mcp_server()
    server.run()
