"""GitHub application — dummy MCP server exposing GitHub-like tools."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta
from typing import Literal

from fastmcp import FastMCP

# ---------------------------------------------------------------------------
# Dummy seed data
# ---------------------------------------------------------------------------

_now = datetime.now()

_REPOS: dict[str, dict] = {
    "octocat/hello-world": {
        "id": "r001",
        "full_name": "octocat/hello-world",
        "owner": "octocat",
        "name": "hello-world",
        "description": "My first repository on GitHub!",
        "language": "Ruby",
        "stars": 2100,
        "forks": 890,
        "open_issues": 3,
        "default_branch": "main",
        "private": False,
        "archived": False,
        "created_at": "2011-01-26T19:01:12",
        "updated_at": (_now - timedelta(days=10)).isoformat(),
    },
    "myorg/backend-api": {
        "id": "r002",
        "full_name": "myorg/backend-api",
        "owner": "myorg",
        "name": "backend-api",
        "description": "REST API for the main product.",
        "language": "Python",
        "stars": 45,
        "forks": 8,
        "open_issues": 12,
        "default_branch": "main",
        "private": True,
        "archived": False,
        "created_at": "2022-03-15T10:00:00",
        "updated_at": (_now - timedelta(hours=2)).isoformat(),
    },
    "myorg/frontend": {
        "id": "r003",
        "full_name": "myorg/frontend",
        "owner": "myorg",
        "name": "frontend",
        "description": "React-based frontend application.",
        "language": "TypeScript",
        "stars": 12,
        "forks": 2,
        "open_issues": 5,
        "default_branch": "main",
        "private": True,
        "archived": False,
        "created_at": "2023-01-10T08:30:00",
        "updated_at": (_now - timedelta(hours=6)).isoformat(),
    },
    "myorg/legacy-service": {
        "id": "r004",
        "full_name": "myorg/legacy-service",
        "owner": "myorg",
        "name": "legacy-service",
        "description": "Old monolith — do not touch.",
        "language": "Java",
        "stars": 3,
        "forks": 1,
        "open_issues": 0,
        "default_branch": "master",
        "private": True,
        "archived": True,
        "created_at": "2015-06-01T00:00:00",
        "updated_at": (_now - timedelta(days=365)).isoformat(),
    },
}

_ISSUES: dict[str, dict] = {
    "i001": {
        "id": "i001",
        "number": 42,
        "repo": "myorg/backend-api",
        "title": "API returns 500 when user has no profile picture",
        "body": (
            "Steps to reproduce: create a new user without uploading an avatar,"
            " then call GET /users/{id}. The server throws a NullPointerException."
        ),
        "author": "alice",
        "assignees": ["bob"],
        "labels": ["bug", "high-priority"],
        "state": "open",
        "comments": 4,
        "created_at": (_now - timedelta(days=3)).isoformat(),
        "updated_at": (_now - timedelta(hours=5)).isoformat(),
    },
    "i002": {
        "id": "i002",
        "number": 43,
        "repo": "myorg/backend-api",
        "title": "Add pagination to /products endpoint",
        "body": (
            "Currently the products endpoint returns all records."
            " We need cursor-based pagination to handle large catalogs."
        ),
        "author": "carol",
        "assignees": [],
        "labels": ["enhancement"],
        "state": "open",
        "comments": 1,
        "created_at": (_now - timedelta(days=7)).isoformat(),
        "updated_at": (_now - timedelta(days=6)).isoformat(),
    },
    "i003": {
        "id": "i003",
        "number": 38,
        "repo": "myorg/backend-api",
        "title": "Update README with deployment instructions",
        "body": "The README is outdated. We need to document docker-compose and k8s setup.",
        "author": "dave",
        "assignees": ["dave"],
        "labels": ["documentation"],
        "state": "closed",
        "comments": 2,
        "created_at": (_now - timedelta(days=14)).isoformat(),
        "updated_at": (_now - timedelta(days=2)).isoformat(),
    },
    "i004": {
        "id": "i004",
        "number": 17,
        "repo": "myorg/frontend",
        "title": "Dark mode flickers on initial page load",
        "body": (
            "When dark mode is enabled and the page first loads there is a brief white flash"
            " before the theme is applied."
        ),
        "author": "alice",
        "assignees": ["alice"],
        "labels": ["bug", "ui"],
        "state": "open",
        "comments": 6,
        "created_at": (_now - timedelta(days=5)).isoformat(),
        "updated_at": (_now - timedelta(hours=1)).isoformat(),
    },
    "i005": {
        "id": "i005",
        "number": 18,
        "repo": "myorg/frontend",
        "title": "Add loading skeleton to product cards",
        "body": "Product cards should show a shimmer skeleton while data is being fetched.",
        "author": "bob",
        "assignees": [],
        "labels": ["enhancement", "ui"],
        "state": "open",
        "comments": 0,
        "created_at": (_now - timedelta(days=1)).isoformat(),
        "updated_at": (_now - timedelta(days=1)).isoformat(),
    },
}

_PULL_REQUESTS: dict[str, dict] = {
    "pr001": {
        "id": "pr001",
        "number": 55,
        "repo": "myorg/backend-api",
        "title": "Fix null pointer in user profile endpoint",
        "body": "Adds a null check for the avatar field before constructing the response. Fixes #42.",
        "author": "bob",
        "reviewers": ["alice", "carol"],
        "labels": ["bug"],
        "state": "open",
        "draft": False,
        "mergeable": True,
        "base": "main",
        "head": "fix/null-avatar",
        "commits": 2,
        "changed_files": 3,
        "additions": 18,
        "deletions": 4,
        "created_at": (_now - timedelta(hours=10)).isoformat(),
        "updated_at": (_now - timedelta(hours=2)).isoformat(),
    },
    "pr002": {
        "id": "pr002",
        "number": 54,
        "repo": "myorg/backend-api",
        "title": "Refactor database layer to use SQLAlchemy 2.x",
        "body": "Modernises our DB access to use the new async session API.",
        "author": "carol",
        "reviewers": ["bob"],
        "labels": ["refactor"],
        "state": "open",
        "draft": True,
        "mergeable": True,
        "base": "main",
        "head": "refactor/sqlalchemy-2",
        "commits": 14,
        "changed_files": 22,
        "additions": 340,
        "deletions": 289,
        "created_at": (_now - timedelta(days=4)).isoformat(),
        "updated_at": (_now - timedelta(days=1)).isoformat(),
    },
    "pr003": {
        "id": "pr003",
        "number": 19,
        "repo": "myorg/frontend",
        "title": "Fix dark mode flash on load",
        "body": "Inlines the theme class into the HTML head to prevent FOUC. Resolves #17.",
        "author": "alice",
        "reviewers": [],
        "labels": ["bug", "ui"],
        "state": "open",
        "draft": False,
        "mergeable": True,
        "base": "main",
        "head": "fix/dark-mode-flash",
        "commits": 1,
        "changed_files": 2,
        "additions": 9,
        "deletions": 1,
        "created_at": (_now - timedelta(hours=4)).isoformat(),
        "updated_at": (_now - timedelta(hours=1)).isoformat(),
    },
}

_COMMENTS: dict[str, dict] = {
    "ic001": {
        "id": "ic001",
        "target_id": "i001",
        "target_type": "issue",
        "author": "bob",
        "body": "I can reproduce this. The avatar URL field is None when not set and we call .length on it.",
        "created_at": (_now - timedelta(days=2)).isoformat(),
    },
    "ic002": {
        "id": "ic002",
        "target_id": "i001",
        "target_type": "issue",
        "author": "alice",
        "body": "Working on a fix, PR coming soon.",
        "created_at": (_now - timedelta(hours=8)).isoformat(),
    },
    "ic003": {
        "id": "ic003",
        "target_id": "pr001",
        "target_type": "pr",
        "author": "alice",
        "body": "LGTM — can you add a unit test for the null case?",
        "created_at": (_now - timedelta(hours=3)).isoformat(),
    },
}


class GitHubApp:
    """Dummy GitHub-like application with repos, issues, and pull requests."""

    def __init__(self) -> None:
        self.name = "github"
        self._repos: dict[str, dict] = {k: dict(v) for k, v in _REPOS.items()}
        self._issues: dict[str, dict] = {k: dict(v) for k, v in _ISSUES.items()}
        self._prs: dict[str, dict] = {k: dict(v) for k, v in _PULL_REQUESTS.items()}
        self._comments: dict[str, dict] = {k: dict(v) for k, v in _COMMENTS.items()}

    # ------------------------------------------------------------------
    # Tools
    # ------------------------------------------------------------------

    def list_repos(self, owner: str | None = None, include_archived: bool = False) -> list[dict]:
        """List repositories, optionally filtered by owner.

        Args:
            owner: GitHub username or org name to filter by (optional).
            include_archived: When True, include archived repositories (default False).

        Returns:
            list[dict]: Repository summaries with full_name, description, language, stars, open_issues.

        Tags:
            github, repos, list, browse, repositories
        """
        repos = [
            r
            for r in self._repos.values()
            if (owner is None or r["owner"] == owner) and (include_archived or not r["archived"])
        ]
        repos.sort(key=lambda r: r["updated_at"], reverse=True)
        return [{k: v for k, v in r.items() if k != "id"} for r in repos]

    def get_repo(self, repo: str) -> dict:
        """Get full details for a repository.

        Args:
            repo: Repository full name in 'owner/name' format, e.g. 'myorg/backend-api'.

        Returns:
            dict: Full repository details, or error dict if not found.

        Tags:
            github, repo, get, detail, info
        """
        r = self._repos.get(repo)
        if r is None:
            return {"error": f"Repository '{repo}' not found."}
        return dict(r)

    def list_issues(
        self,
        repo: str,
        state: Literal["open", "closed", "all"] = "open",
        labels: list[str] | None = None,
        assignee: str | None = None,
    ) -> list[dict]:
        """List issues in a repository.

        Args:
            repo: Repository full name, e.g. 'myorg/backend-api'.
            state: Filter by state — 'open' (default), 'closed', or 'all'.
            labels: Optional list of label names to filter by.
            assignee: Optional GitHub username to filter by assignee.

        Returns:
            list[dict]: Issue summaries with number, title, author, labels, state, comments.

        Tags:
            github, issues, list, bugs, tasks
        """
        issues = [
            i
            for i in self._issues.values()
            if i["repo"] == repo
            and (state == "all" or i["state"] == state)
            and (labels is None or all(lb in i["labels"] for lb in labels))
            and (assignee is None or assignee in i["assignees"])
        ]
        issues.sort(key=lambda i: i["updated_at"], reverse=True)
        return [{k: v for k, v in i.items() if k not in {"id", "body"}} for i in issues]

    def get_issue(self, repo: str, issue_number: int) -> dict:
        """Get full details for an issue, including body.

        Args:
            repo: Repository full name, e.g. 'myorg/backend-api'.
            issue_number: The issue number (integer shown in the URL).

        Returns:
            dict: Full issue dict including body, or error dict if not found.

        Tags:
            github, issue, get, detail, read
        """
        for issue in self._issues.values():
            if issue["repo"] == repo and issue["number"] == issue_number:
                return dict(issue)
        return {"error": f"Issue #{issue_number} not found in '{repo}'."}

    def create_issue(
        self,
        repo: str,
        title: str,
        body: str = "",
        labels: list[str] | None = None,
        assignees: list[str] | None = None,
    ) -> dict:
        """Create a new issue in a repository.

        Args:
            repo: Repository full name, e.g. 'myorg/backend-api'.
            title: Issue title.
            body: Issue description (optional).
            labels: List of label names to attach (optional).
            assignees: List of GitHub usernames to assign (optional).

        Returns:
            dict: Confirmation with the new issue number and id.

        Tags:
            github, issue, create, report, open
        """
        if repo not in self._repos:
            return {"error": f"Repository '{repo}' not found."}
        issue_id = "i" + str(uuid.uuid4())[:6]
        existing_numbers = [i["number"] for i in self._issues.values() if i["repo"] == repo]
        number = max(existing_numbers, default=0) + 1
        self._issues[issue_id] = {
            "id": issue_id,
            "number": number,
            "repo": repo,
            "title": title,
            "body": body,
            "author": "me",
            "assignees": assignees or [],
            "labels": labels or [],
            "state": "open",
            "comments": 0,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }
        self._repos[repo]["open_issues"] += 1
        return {"id": issue_id, "number": number, "repo": repo, "status": "created"}

    def close_issue(self, repo: str, issue_number: int) -> dict:
        """Close an open issue.

        Args:
            repo: Repository full name, e.g. 'myorg/backend-api'.
            issue_number: The issue number to close.

        Returns:
            dict: Confirmation with updated state, or error dict.

        Tags:
            github, issue, close, resolve, done
        """
        for issue in self._issues.values():
            if issue["repo"] == repo and issue["number"] == issue_number:
                if issue["state"] == "closed":
                    return {"number": issue_number, "state": "closed", "status": "already closed"}
                issue["state"] = "closed"
                issue["updated_at"] = datetime.now().isoformat()
                self._repos[repo]["open_issues"] = max(0, self._repos[repo]["open_issues"] - 1)
                return {"number": issue_number, "state": "closed", "status": "updated"}
        return {"error": f"Issue #{issue_number} not found in '{repo}'."}

    def list_pull_requests(
        self,
        repo: str,
        state: Literal["open", "closed", "all"] = "open",
        include_drafts: bool = True,
    ) -> list[dict]:
        """List pull requests in a repository.

        Args:
            repo: Repository full name, e.g. 'myorg/backend-api'.
            state: Filter by state — 'open' (default), 'closed', or 'all'.
            include_drafts: When False, exclude draft PRs (default True).

        Returns:
            list[dict]: PR summaries with number, title, author, state, draft, commits, changed_files.

        Tags:
            github, pull_requests, list, prs, reviews
        """
        prs = [
            pr
            for pr in self._prs.values()
            if pr["repo"] == repo and (state == "all" or pr["state"] == state) and (include_drafts or not pr["draft"])
        ]
        prs.sort(key=lambda pr: pr["updated_at"], reverse=True)
        return [{k: v for k, v in pr.items() if k not in {"id", "body"}} for pr in prs]

    def get_pull_request(self, repo: str, pr_number: int) -> dict:
        """Get full details for a pull request, including body.

        Args:
            repo: Repository full name, e.g. 'myorg/backend-api'.
            pr_number: The pull request number.

        Returns:
            dict: Full PR dict including body, or error dict if not found.

        Tags:
            github, pull_request, get, detail, review
        """
        for pr in self._prs.values():
            if pr["repo"] == repo and pr["number"] == pr_number:
                return dict(pr)
        return {"error": f"PR #{pr_number} not found in '{repo}'."}

    def add_comment(self, target_type: Literal["issue", "pr"], repo: str, number: int, body: str) -> dict:
        """Add a comment to an issue or pull request.

        Args:
            target_type: Whether the target is an 'issue' or 'pr'.
            repo: Repository full name, e.g. 'myorg/backend-api'.
            number: Issue or PR number.
            body: Comment text.

        Returns:
            dict: Confirmation with the new comment id, or error dict.

        Tags:
            github, comment, add, reply, discuss
        """
        collection = self._issues if target_type == "issue" else self._prs
        for item in collection.values():
            if item["repo"] == repo and item["number"] == number:
                comment_id = "ic" + str(uuid.uuid4())[:6]
                self._comments[comment_id] = {
                    "id": comment_id,
                    "target_id": item["id"],
                    "target_type": target_type,
                    "author": "me",
                    "body": body,
                    "created_at": datetime.now().isoformat(),
                }
                if target_type == "issue":
                    item["comments"] += 1
                return {"id": comment_id, "status": "created"}
        return {"error": f"{target_type.upper()} #{number} not found in '{repo}'."}

    def get_comments(self, target_type: Literal["issue", "pr"], repo: str, number: int) -> list[dict]:
        """Get all comments on an issue or pull request.

        Args:
            target_type: Whether the target is an 'issue' or 'pr'.
            repo: Repository full name, e.g. 'myorg/backend-api'.
            number: Issue or PR number.

        Returns:
            list[dict]: Comments sorted by created_at ascending, or error dict in a list.

        Tags:
            github, comments, get, discussion, thread
        """
        collection = self._issues if target_type == "issue" else self._prs
        target_id = None
        for item in collection.values():
            if item["repo"] == repo and item["number"] == number:
                target_id = item["id"]
                break
        if target_id is None:
            return [{"error": f"{target_type.upper()} #{number} not found in '{repo}'."}]
        comments = [
            c for c in self._comments.values() if c["target_id"] == target_id and c["target_type"] == target_type
        ]
        comments.sort(key=lambda c: c["created_at"])
        return comments

    # ------------------------------------------------------------------

    def list_tools(self) -> list:
        """Return all tool methods exposed by this application.

        Returns:
            list: Callable tool methods.
        """
        return [
            self.list_repos,
            self.get_repo,
            self.list_issues,
            self.get_issue,
            self.create_issue,
            self.close_issue,
            self.list_pull_requests,
            self.get_pull_request,
            self.add_comment,
            self.get_comments,
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
    app = GitHubApp()
    server = app.create_mcp_server()
    server.run()
