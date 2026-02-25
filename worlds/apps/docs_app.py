"""Docs application — in-memory document store MCP server."""

from __future__ import annotations

import uuid
from datetime import datetime

from fastmcp import FastMCP

from worlds.utils import load_seed_data


class DocsApp:
    """In-memory document store for creating, finding, and managing documents."""

    def __init__(self) -> None:
        self.name = "docs"
        self.data = load_seed_data("docs")
        self._docs: dict[str, dict] = {d["id"]: d for d in self.data["_DOCS"]}

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
