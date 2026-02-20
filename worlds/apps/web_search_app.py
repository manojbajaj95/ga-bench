"""Web search application — dummy MCP server with hardcoded search results."""

from __future__ import annotations

from fastmcp import FastMCP

# ---------------------------------------------------------------------------
# Hardcoded search index
# ---------------------------------------------------------------------------

_SEARCH_INDEX: list[dict] = [
    # Weather
    {
        "keywords": ["weather", "san francisco", "sf"],
        "title": "Current Weather in San Francisco, CA",
        "url": "https://weather.example.com/san-francisco",
        "snippet": "San Francisco, CA: 58°F, Partly Cloudy. High 62°F, Low 54°F. "
        "Wind: 12 mph from the west. Humidity: 78%. Fog advisory in effect through morning.",
        "category": "weather",
        "source": "Weather Service",
    },
    {
        "keywords": ["weather", "new york", "nyc"],
        "title": "Current Weather in New York, NY",
        "url": "https://weather.example.com/new-york",
        "snippet": "New York, NY: 34°F, Overcast. High 38°F, Low 29°F. "
        "Wind: 8 mph from the north. Humidity: 65%. Winter storm watch in effect this weekend.",
        "category": "weather",
        "source": "Weather Service",
    },
    {
        "keywords": ["weather", "los angeles", "la"],
        "title": "Current Weather in Los Angeles, CA",
        "url": "https://weather.example.com/los-angeles",
        "snippet": "Los Angeles, CA: 72°F, Sunny. High 76°F, Low 60°F. "
        "Wind: 5 mph from the southwest. Humidity: 42%. Beautiful day expected.",
        "category": "weather",
        "source": "Weather Service",
    },
    {
        "keywords": ["weather", "chicago"],
        "title": "Current Weather in Chicago, IL",
        "url": "https://weather.example.com/chicago",
        "snippet": "Chicago, IL: 18°F, Heavy Snow. High 22°F, Low 10°F. "
        "Wind: 20 mph from the northwest. Blizzard warning in effect. 8–12 inches of snow expected.",
        "category": "weather",
        "source": "Weather Service",
    },
    # Sports
    {
        "keywords": ["warriors", "game", "nba", "score", "basketball"],
        "title": "Golden State Warriors vs. Los Angeles Lakers — Game Recap",
        "url": "https://sports.example.com/nba/warriors-lakers-recap",
        "snippet": "Warriors defeat Lakers 118–104. Stephen Curry led all scorers with 38 points, "
        "8 assists, and 5 rebounds. LeBron James finished with 28 points and 9 assists. "
        "Golden State improves to 31–17 on the season.",
        "category": "sports",
        "source": "Sports Network",
    },
    {
        "keywords": ["49ers", "game", "nfl", "score", "football", "super bowl"],
        "title": "San Francisco 49ers Season Update",
        "url": "https://sports.example.com/nfl/49ers-season",
        "snippet": "The 49ers finished the regular season 12–5, clinching the NFC West division title. "
        "Brock Purdy threw for 4,280 yards and 31 TDs. The team hosts their divisional playoff "
        "game next weekend at Levi's Stadium.",
        "category": "sports",
        "source": "Sports Network",
    },
    {
        "keywords": ["chelsea", "manchester", "premier league", "soccer", "football", "match"],
        "title": "Chelsea vs. Manchester City — Premier League Match Report",
        "url": "https://sports.example.com/soccer/chelsea-mancity",
        "snippet": "Chelsea held Manchester City to a 1–1 draw at Stamford Bridge. Erling Haaland "
        "opened the scoring in the 23rd minute; Cole Palmer equalized with a stunning free kick "
        "in the 67th. Both sides remain in contention for a top-four finish.",
        "category": "sports",
        "source": "Sports Network",
    },
    {
        "keywords": ["f1", "formula 1", "race", "grand prix", "verstappen", "ferrari"],
        "title": "F1 Season Standings Update",
        "url": "https://sports.example.com/f1/standings",
        "snippet": "Max Verstappen leads the Drivers' Championship with 287 points. "
        "Charles Leclerc is second with 261 points, and Lando Norris third with 248. "
        "Ferrari leads the Constructors' Championship by 34 points over Red Bull.",
        "category": "sports",
        "source": "Sports Network",
    },
    # News
    {
        "keywords": ["ai", "artificial intelligence", "openai", "anthropic", "llm", "news"],
        "title": "Latest AI Industry News",
        "url": "https://news.example.com/technology/ai-roundup",
        "snippet": "Anthropic releases Claude 3.7 with enhanced reasoning capabilities. "
        "OpenAI announces GPT-5 research preview for enterprise customers. "
        "Google DeepMind publishes new research on multi-modal agents. "
        "AI chip demand drives NVIDIA revenue to record $39B quarterly earnings.",
        "category": "technology",
        "source": "Tech News Daily",
    },
    {
        "keywords": ["stock", "market", "nasdaq", "dow", "s&p", "finance"],
        "title": "Stock Market Summary — Today's Close",
        "url": "https://finance.example.com/market-summary",
        "snippet": "Markets closed mixed. Dow Jones: 43,218 (+0.4%). S&P 500: 5,891 (+0.1%). "
        "Nasdaq: 19,340 (–0.3%). Tech stocks pulled back on inflation data; "
        "energy and financial sectors gained. Treasury 10-year yield at 4.42%.",
        "category": "finance",
        "source": "Financial Times",
    },
    {
        "keywords": ["bitcoin", "crypto", "ethereum", "cryptocurrency"],
        "title": "Cryptocurrency Prices — Live Update",
        "url": "https://finance.example.com/crypto",
        "snippet": "Bitcoin (BTC): $97,450 (+2.1%). Ethereum (ETH): $3,280 (+1.4%). "
        "Solana (SOL): $182 (+3.8%). Total crypto market cap: $3.2 trillion. "
        "Bitcoin ETF inflows reached $800M this week.",
        "category": "finance",
        "source": "CryptoWatch",
    },
    {
        "keywords": ["election", "politics", "congress", "senate", "president"],
        "title": "Political News Roundup",
        "url": "https://news.example.com/politics/roundup",
        "snippet": "Senate passes bipartisan infrastructure maintenance bill 68–32. "
        "House committee advances tech antitrust legislation. "
        "Polling shows approval ratings stable ahead of midterm season. "
        "Several governors announce 2028 presidential exploratory committees.",
        "category": "politics",
        "source": "National Press",
    },
    {
        "keywords": ["movie", "film", "box office", "cinema", "oscar"],
        "title": "Box Office & Entertainment News",
        "url": "https://entertainment.example.com/movies",
        "snippet": "This weekend's top film grossed $74M domestically. Oscar nominations announced "
        "with 12 films receiving multiple nods. Streaming wars heat up as three major "
        "platforms report subscriber growth. A24's latest release earns 97% on Rotten Tomatoes.",
        "category": "entertainment",
        "source": "Entertainment Weekly",
    },
    {
        "keywords": ["restaurant", "food", "eat", "dining", "san francisco"],
        "title": "Top Restaurants in San Francisco 2026",
        "url": "https://food.example.com/sf-restaurants",
        "snippet": "San Francisco's dining scene continues to thrive. Top picks: Zuni Café (Mission), "
        "State Bird Provisions (Western Addition), Nopa (NoPa), and Bix (Jackson Square). "
        "New Michelin stars awarded to three restaurants in the Mission District.",
        "category": "food",
        "source": "Eater SF",
    },
    {
        "keywords": ["covid", "flu", "health", "disease", "cdc"],
        "title": "CDC Health Update — Respiratory Illness Season",
        "url": "https://health.example.com/cdc-update",
        "snippet": "CDC reports flu activity at moderate levels nationally, with the West seeing "
        "higher-than-average cases. RSV activity declining. COVID variants continue "
        "circulating at low levels. Current vaccines remain effective against severe illness.",
        "category": "health",
        "source": "CDC / Health News",
    },
    {
        "keywords": ["apple", "iphone", "macbook", "ios", "wwdc"],
        "title": "Apple News — Latest Products and Updates",
        "url": "https://tech.example.com/apple",
        "snippet": "Apple announces iOS 19.3 update with enhanced AI features powered by on-device "
        "models. New MacBook Pro with M4 Ultra chip ships next month. Apple Vision Pro 2 "
        "rumored for fall launch. App Store revenue reaches $100B milestone.",
        "category": "technology",
        "source": "9to5Mac",
    },
]


def _matches(query: str, item: dict) -> bool:
    """Return True if any keyword appears in the query string."""
    q = query.lower()
    return any(kw in q for kw in item["keywords"])


def _score(query: str, item: dict) -> int:
    """Count how many keywords match — used for ranking."""
    q = query.lower()
    return sum(1 for kw in item["keywords"] if kw in q)


class WebSearchApp:
    """Dummy web search application with hardcoded results for common queries."""

    def __init__(self) -> None:
        self.name = "web_search"

    # ------------------------------------------------------------------
    # Tools
    # ------------------------------------------------------------------

    def search(self, query: str, max_results: int = 5) -> list[dict]:
        """Search the web for information about a topic.

        Args:
            query: Natural language search query (e.g. "weather in San Francisco").
            max_results: Maximum number of results to return (default 5, max 10).

        Returns:
            list[dict]: Ranked search results, each with title, url, snippet, source, category.

        Tags:
            search, web, query, find, information
        """
        max_results = min(max_results, 10)
        matches = [(item, _score(query, item)) for item in _SEARCH_INDEX if _matches(query, item)]
        matches.sort(key=lambda x: x[1], reverse=True)
        return [
            {
                "title": item["title"],
                "url": item["url"],
                "snippet": item["snippet"],
                "source": item["source"],
                "category": item["category"],
            }
            for item, _ in matches[:max_results]
        ]

    def get_page(self, url: str) -> dict:
        """Retrieve the full content of a search result page by its URL.

        Args:
            url: The URL of the page to retrieve (must be a URL from a previous search call).

        Returns:
            dict: Page content with title, url, full_content, and source. Returns an error
                  dict if the URL is not found.

        Tags:
            web, fetch, page, content, read
        """
        for item in _SEARCH_INDEX:
            if item["url"] == url:
                return {
                    "title": item["title"],
                    "url": item["url"],
                    "full_content": item["snippet"],
                    "source": item["source"],
                    "category": item["category"],
                }
        return {"error": f"Page not found: '{url}'. Only URLs from search results are available."}

    def trending_topics(self, category: str = "all") -> list[dict]:
        """Return currently trending topics, optionally filtered by category.

        Args:
            category: Category filter — one of: all, weather, sports, technology, finance,
                      politics, entertainment, food, health. Defaults to 'all'.

        Returns:
            list[dict]: Trending topics with title, url, source, and category.

        Tags:
            trending, popular, news, topics, discovery
        """
        items = _SEARCH_INDEX if category == "all" else [item for item in _SEARCH_INDEX if item["category"] == category]
        return [
            {
                "title": item["title"],
                "url": item["url"],
                "source": item["source"],
                "category": item["category"],
            }
            for item in items
        ]

    def list_categories(self) -> list[str]:
        """List all available content categories in the search index.

        Returns:
            list[str]: Sorted list of unique category names.

        Tags:
            categories, search, filter, index
        """
        return sorted({item["category"] for item in _SEARCH_INDEX})

    # ------------------------------------------------------------------

    def list_tools(self) -> list:
        """Return all tool methods exposed by this application.

        Returns:
            list: Callable tool methods.
        """
        return [
            self.search,
            self.get_page,
            self.trending_topics,
            self.list_categories,
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
    app = WebSearchApp()
    server = app.create_mcp_server()
    server.run()
