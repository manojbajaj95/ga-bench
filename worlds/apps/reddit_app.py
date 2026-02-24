"""Reddit application — dummy MCP server exposing Reddit-like social media tools."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta
from typing import Literal

from fastmcp import FastMCP

# ---------------------------------------------------------------------------
# Dummy seed data
# ---------------------------------------------------------------------------

_SUBREDDITS: dict[str, dict] = {
    "python": {
        "name": "python",
        "display_name": "r/python",
        "description": "News about the Python programming language.",
        "subscribers": 1_200_000,
        "created": "2008-01-01T00:00:00",
    },
    "machinelearning": {
        "name": "machinelearning",
        "display_name": "r/MachineLearning",
        "description": "Research and news about machine learning.",
        "subscribers": 2_500_000,
        "created": "2010-03-12T00:00:00",
    },
    "worldnews": {
        "name": "worldnews",
        "display_name": "r/worldnews",
        "description": "A place for major news from around the world.",
        "subscribers": 28_000_000,
        "created": "2008-06-20T00:00:00",
    },
    "AskReddit": {
        "name": "AskReddit",
        "display_name": "r/AskReddit",
        "description": "Ask and answer thought-provoking questions.",
        "subscribers": 42_000_000,
        "created": "2008-01-25T00:00:00",
    },
    "technology": {
        "name": "technology",
        "display_name": "r/technology",
        "description": "Subreddit dedicated to the news and discussions about technology.",
        "subscribers": 15_000_000,
        "created": "2008-04-15T00:00:00",
    },
}

_now = datetime.now()

_POSTS: dict[str, dict] = {
    "p001": {
        "id": "p001",
        "title": "Python 3.14 released — major performance improvements",
        "author": "u/pythonista99",
        "subreddit": "python",
        "selftext": (
            "The Python core team just released 3.14 with significant speed-ups thanks to the new optimizer."
            " Benchmarks show 20-40% improvement on typical workloads."
        ),
        "url": "https://python.org/news/python-3-14",
        "score": 4823,
        "upvote_ratio": 0.97,
        "num_comments": 312,
        "flair": "News",
        "is_self": False,
        "saved": False,
        "hidden": False,
        "timestamp": (_now - timedelta(hours=5)).isoformat(),
    },
    "p002": {
        "id": "p002",
        "title": "What's your go-to Python library for data validation?",
        "author": "u/dev_curious",
        "subreddit": "python",
        "selftext": (
            "I've been using Pydantic for a while, but heard good things about marshmallow and cerberus."
            " What do you all prefer and why?"
        ),
        "url": None,
        "score": 892,
        "upvote_ratio": 0.91,
        "num_comments": 145,
        "flair": "Discussion",
        "is_self": True,
        "saved": True,
        "hidden": False,
        "timestamp": (_now - timedelta(hours=12)).isoformat(),
    },
    "p003": {
        "id": "p003",
        "title": "New paper: LLMs achieve human-level reasoning on ARC-AGI benchmark",
        "author": "u/ml_researcher",
        "subreddit": "machinelearning",
        "selftext": (
            "Our team's latest paper demonstrates that a combination of chain-of-thought prompting and tool use"
            " enables LLMs to solve 95% of ARC-AGI tasks. Pre-print on arXiv."
        ),
        "url": "https://arxiv.org/abs/2501.99999",
        "score": 9201,
        "upvote_ratio": 0.93,
        "num_comments": 876,
        "flair": "Research",
        "is_self": False,
        "saved": False,
        "hidden": False,
        "timestamp": (_now - timedelta(hours=8)).isoformat(),
    },
    "p004": {
        "id": "p004",
        "title": "Rant: stop using LLMs for everything — they're not magic",
        "author": "u/skeptical_dev",
        "subreddit": "machinelearning",
        "selftext": (
            "Tired of seeing every startup pitch 'AI-powered' products that are just GPT wrappers."
            " LLMs hallucinate and should not be used as ground truth in production systems."
        ),
        "url": None,
        "score": -43,
        "upvote_ratio": 0.34,
        "num_comments": 302,
        "flair": "Discussion",
        "is_self": True,
        "saved": False,
        "hidden": False,
        "timestamp": (_now - timedelta(hours=20)).isoformat(),
    },
    "p005": {
        "id": "p005",
        "title": "Global renewable energy capacity hits record high in 2025",
        "author": "u/green_reporter",
        "subreddit": "worldnews",
        "selftext": "",
        "url": "https://news.example.com/renewable-record-2025",
        "score": 18400,
        "upvote_ratio": 0.96,
        "num_comments": 1204,
        "flair": "Environment",
        "is_self": False,
        "saved": False,
        "hidden": False,
        "timestamp": (_now - timedelta(hours=3)).isoformat(),
    },
    "p006": {
        "id": "p006",
        "title": "What's a skill you learned during quarantine that you still use today?",
        "author": "u/nostalgic_ask",
        "subreddit": "AskReddit",
        "selftext": "",
        "url": None,
        "score": 52100,
        "upvote_ratio": 0.98,
        "num_comments": 8902,
        "flair": None,
        "is_self": True,
        "saved": True,
        "hidden": False,
        "timestamp": (_now - timedelta(hours=14)).isoformat(),
    },
    "p007": {
        "id": "p007",
        "title": "Tech layoffs continue: 10,000 jobs cut at major firms this quarter",
        "author": "u/tech_reporter",
        "subreddit": "technology",
        "selftext": "",
        "url": "https://techcrunch.example.com/layoffs-2025",
        "score": 7350,
        "upvote_ratio": 0.88,
        "num_comments": 945,
        "flair": "Article",
        "is_self": False,
        "saved": False,
        "hidden": True,
        "timestamp": (_now - timedelta(days=1)).isoformat(),
    },
    "p008": {
        "id": "p008",
        "title": "Show r/python: I built a zero-dependency HTTP server in 200 lines",
        "author": "u/minimalist_coder",
        "subreddit": "python",
        "selftext": (
            "Tired of heavy frameworks, so I wrote a tiny HTTP server using only stdlib."
            " It handles routing, middleware, and JSON responses. GitHub link in comments."
        ),
        "url": None,
        "score": 2103,
        "upvote_ratio": 0.95,
        "num_comments": 88,
        "flair": "Showcase",
        "is_self": True,
        "saved": False,
        "hidden": False,
        "timestamp": (_now - timedelta(hours=30)).isoformat(),
    },
}

_COMMENTS: dict[str, dict] = {
    "c001": {
        "id": "c001",
        "post_id": "p001",
        "parent_id": None,
        "author": "u/speed_freak",
        "body": "Finally! The new optimizer has been in development for 2 years. Totally worth the wait.",
        "score": 1203,
        "saved": False,
        "timestamp": (_now - timedelta(hours=4, minutes=30)).isoformat(),
    },
    "c002": {
        "id": "c002",
        "post_id": "p001",
        "parent_id": "c001",
        "author": "u/skeptic42",
        "body": "Benchmarks always look good in isolation. Let's see how it performs on real-world workloads.",
        "score": 432,
        "saved": False,
        "timestamp": (_now - timedelta(hours=4)).isoformat(),
    },
    "c003": {
        "id": "c003",
        "post_id": "p001",
        "parent_id": None,
        "author": "u/async_advocate",
        "body": "Did they fix the GIL situation for async workloads?",
        "score": 891,
        "saved": True,
        "timestamp": (_now - timedelta(hours=3, minutes=45)).isoformat(),
    },
    "c004": {
        "id": "c004",
        "post_id": "p002",
        "parent_id": None,
        "author": "u/pydantic_fan",
        "body": "Pydantic v2 is a massive upgrade. The performance improvements alone make it worth switching.",
        "score": 312,
        "saved": False,
        "timestamp": (_now - timedelta(hours=11)).isoformat(),
    },
    "c005": {
        "id": "c005",
        "post_id": "p002",
        "parent_id": None,
        "author": "u/attrs_user",
        "body": "I prefer attrs + cattrs for pure Python dataclasses. Much lighter than Pydantic.",
        "score": 178,
        "saved": False,
        "timestamp": (_now - timedelta(hours=10)).isoformat(),
    },
    "c006": {
        "id": "c006",
        "post_id": "p003",
        "parent_id": None,
        "author": "u/agi_watcher",
        "body": "ARC-AGI was supposed to be AGI-proof. Interesting times we live in.",
        "score": 2041,
        "saved": True,
        "timestamp": (_now - timedelta(hours=7)).isoformat(),
    },
    "c007": {
        "id": "c007",
        "post_id": "p006",
        "parent_id": None,
        "author": "u/bread_baker",
        "body": "Sourdough bread. I now bake every weekend and it's genuinely one of my favorite hobbies.",
        "score": 15830,
        "saved": False,
        "timestamp": (_now - timedelta(hours=13)).isoformat(),
    },
    "c008": {
        "id": "c008",
        "post_id": "p006",
        "parent_id": None,
        "author": "u/guitar_convert",
        "body": "Guitar. Still play for 30 minutes every evening. Best thing to come out of 2020.",
        "score": 12400,
        "saved": False,
        "timestamp": (_now - timedelta(hours=13, minutes=20)).isoformat(),
    },
}


class RedditApp:
    """Dummy Reddit-like social media application with posts, comments, and voting."""

    def __init__(self) -> None:
        self.name = "reddit"
        self._subreddits: dict[str, dict] = dict(_SUBREDDITS)
        self._posts: dict[str, dict] = {k: dict(v) for k, v in _POSTS.items()}
        self._comments: dict[str, dict] = {k: dict(v) for k, v in _COMMENTS.items()}

    # ------------------------------------------------------------------
    # Tools
    # ------------------------------------------------------------------

    def list_subreddits(self) -> list[dict]:
        """List all available subreddits with subscriber counts.

        Returns:
            list[dict]: Each entry has name, display_name, description, subscribers.

        Tags:
            reddit, subreddits, list, browse, communities
        """
        return sorted(self._subreddits.values(), key=lambda s: s["subscribers"], reverse=True)

    def list_posts(
        self,
        subreddit: str,
        sort: Literal["hot", "new", "top"] = "hot",
        limit: int = 10,
        include_hidden: bool = False,
    ) -> list[dict]:
        """List posts in a subreddit.

        Args:
            subreddit: Subreddit name (without r/ prefix), e.g. 'python'.
            sort: Sort order — 'hot' (default), 'new', or 'top'.
            limit: Maximum number of posts to return (default 10).
            include_hidden: When True, include hidden posts (default False).

        Returns:
            list[dict]: Post summaries with id, title, author, score, num_comments, timestamp.

        Tags:
            reddit, posts, list, browse, feed, subreddit
        """
        posts = [p for p in self._posts.values() if p["subreddit"] == subreddit and (include_hidden or not p["hidden"])]
        if sort == "new":
            posts.sort(key=lambda p: p["timestamp"], reverse=True)
        elif sort == "top":
            posts.sort(key=lambda p: p["score"], reverse=True)
        else:  # hot — approximate by score / age
            posts.sort(key=lambda p: p["score"], reverse=True)
        return [{k: v for k, v in p.items() if k not in {"selftext", "url"}} for p in posts[:limit]]

    def get_post(self, post_id: str) -> dict:
        """Retrieve a single post by its ID, including full text.

        Args:
            post_id: The unique ID of the post (e.g. 'p001').

        Returns:
            dict: Full post dict including selftext and url, or error dict if not found.

        Tags:
            reddit, post, get, detail, read
        """
        post = self._posts.get(post_id)
        if post is None:
            return {"error": f"Post '{post_id}' not found."}
        return dict(post)

    def get_comments(self, post_id: str, limit: int = 20) -> list[dict]:
        """Get top-level and reply comments for a post.

        Args:
            post_id: The unique ID of the post.
            limit: Maximum number of comments to return (default 20).

        Returns:
            list[dict]: Comments sorted by score descending, each with id, parent_id,
                        author, body, score, timestamp.

        Tags:
            reddit, comments, get, replies, thread
        """
        comments = [c for c in self._comments.values() if c["post_id"] == post_id]
        comments.sort(key=lambda c: c["score"], reverse=True)
        return comments[:limit]

    def submit_post(
        self,
        subreddit: str,
        title: str,
        selftext: str = "",
        url: str | None = None,
        flair: str | None = None,
    ) -> dict:
        """Submit a new post to a subreddit.

        Args:
            subreddit: Subreddit name to post in (without r/ prefix).
            title: Post title.
            selftext: Body text for self-posts (optional).
            url: External URL for link posts (optional).
            flair: Post flair label (optional).

        Returns:
            dict: Confirmation with newly created post id and permalink.

        Tags:
            reddit, post, submit, create, publish
        """
        if subreddit not in self._subreddits:
            return {"error": f"Subreddit '{subreddit}' not found."}
        post_id = "p" + str(uuid.uuid4())[:6]
        self._posts[post_id] = {
            "id": post_id,
            "title": title,
            "author": "u/me",
            "subreddit": subreddit,
            "selftext": selftext,
            "url": url,
            "score": 1,
            "upvote_ratio": 1.0,
            "num_comments": 0,
            "flair": flair,
            "is_self": url is None,
            "saved": False,
            "hidden": False,
            "timestamp": datetime.now().isoformat(),
        }
        return {"id": post_id, "permalink": f"/r/{subreddit}/comments/{post_id}", "status": "submitted"}

    def submit_comment(self, post_id: str, body: str, parent_id: str | None = None) -> dict:
        """Submit a comment on a post or reply to an existing comment.

        Args:
            post_id: The unique ID of the post to comment on.
            body: Comment text content.
            parent_id: ID of the comment to reply to, or None for a top-level comment.

        Returns:
            dict: Confirmation with the newly created comment id, or error dict.

        Tags:
            reddit, comment, submit, reply, create
        """
        if post_id not in self._posts:
            return {"error": f"Post '{post_id}' not found."}
        if parent_id is not None and parent_id not in self._comments:
            return {"error": f"Parent comment '{parent_id}' not found."}
        comment_id = "c" + str(uuid.uuid4())[:6]
        self._comments[comment_id] = {
            "id": comment_id,
            "post_id": post_id,
            "parent_id": parent_id,
            "author": "u/me",
            "body": body,
            "score": 1,
            "saved": False,
            "timestamp": datetime.now().isoformat(),
        }
        self._posts[post_id]["num_comments"] += 1
        return {"id": comment_id, "status": "submitted"}

    def vote(
        self,
        target_id: str,
        direction: Literal["up", "down", "none"],
    ) -> dict:
        """Vote on a post or comment.

        Args:
            target_id: ID of the post (e.g. 'p001') or comment (e.g. 'c001') to vote on.
            direction: 'up' to upvote, 'down' to downvote, 'none' to remove vote.

        Returns:
            dict: Updated score and vote direction, or error dict.

        Tags:
            reddit, vote, upvote, downvote, karma
        """
        delta = {"up": 1, "down": -1, "none": 0}[direction]
        if target_id in self._posts:
            self._posts[target_id]["score"] += delta
            return {"id": target_id, "type": "post", "score": self._posts[target_id]["score"], "vote": direction}
        if target_id in self._comments:
            self._comments[target_id]["score"] += delta
            return {"id": target_id, "type": "comment", "score": self._comments[target_id]["score"], "vote": direction}
        return {"error": f"Target '{target_id}' not found."}

    def save_item(self, target_id: str, saved: bool = True) -> dict:
        """Save or unsave a post or comment.

        Args:
            target_id: ID of the post or comment to save/unsave.
            saved: True to save (default), False to unsave.

        Returns:
            dict: Updated saved status, or error dict.

        Tags:
            reddit, save, bookmark, collection
        """
        if target_id in self._posts:
            self._posts[target_id]["saved"] = saved
            return {"id": target_id, "type": "post", "saved": saved}
        if target_id in self._comments:
            self._comments[target_id]["saved"] = saved
            return {"id": target_id, "type": "comment", "saved": saved}
        return {"error": f"Target '{target_id}' not found."}

    def search_posts(
        self,
        query: str,
        subreddit: str | None = None,
        sort: Literal["relevance", "top", "new"] = "relevance",
    ) -> list[dict]:
        """Search posts by keyword across all subreddits or within one.

        Args:
            query: Search string matched against title and selftext (case-insensitive).
            subreddit: Optional subreddit name to restrict the search to.
            sort: Sort order — 'relevance' (default), 'top', or 'new'.

        Returns:
            list[dict]: Matching post summaries (without selftext/url).

        Tags:
            reddit, search, find, query, filter, posts
        """
        q = query.lower()
        results = []
        for post in self._posts.values():
            if subreddit and post["subreddit"] != subreddit:
                continue
            if q in post["title"].lower() or q in post["selftext"].lower():
                results.append({k: v for k, v in post.items() if k not in {"selftext", "url"}})
        if sort == "top":
            results.sort(key=lambda p: p["score"], reverse=True)
        elif sort == "new":
            results.sort(key=lambda p: p["timestamp"], reverse=True)
        return results

    def hide_post(self, post_id: str, hidden: bool = True) -> dict:
        """Hide or unhide a post from your feed.

        Args:
            post_id: The unique ID of the post to hide or unhide.
            hidden: True to hide (default), False to unhide.

        Returns:
            dict: Updated hidden status, or error dict.

        Tags:
            reddit, hide, filter, feed, manage
        """
        post = self._posts.get(post_id)
        if post is None:
            return {"error": f"Post '{post_id}' not found."}
        post["hidden"] = hidden
        return {"id": post_id, "hidden": hidden, "status": "updated"}

    # ------------------------------------------------------------------

    def list_tools(self) -> list:
        """Return all tool methods exposed by this application.

        Returns:
            list: Callable tool methods.
        """
        return [
            self.list_subreddits,
            self.list_posts,
            self.get_post,
            self.get_comments,
            self.submit_post,
            self.submit_comment,
            self.vote,
            self.save_item,
            self.search_posts,
            self.hide_post,
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
    app = RedditApp()
    server = app.create_mcp_server()
    server.run()
