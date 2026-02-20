"""Yahoo Finance application — dummy MCP server with hardcoded market data."""

from __future__ import annotations

from fastmcp import FastMCP

# ---------------------------------------------------------------------------
# Hardcoded market data (snapshot as of 2026-02-20)
# ---------------------------------------------------------------------------

_STOCKS: dict[str, dict] = {
    "AAPL": {
        "symbol": "AAPL",
        "name": "Apple Inc.",
        "sector": "Technology",
        "price": 228.50,
        "change": +2.30,
        "change_pct": +1.02,
        "market_cap": "3.51T",
        "pe_ratio": 34.2,
        "dividend_yield": 0.51,
        "52w_high": 245.61,
        "52w_low": 164.08,
        "volume": 54_320_000,
        "avg_volume": 62_100_000,
        "description": "Apple designs and sells consumer electronics, software, and online services. "
        "Core products include iPhone, Mac, iPad, and Apple Watch.",
    },
    "MSFT": {
        "symbol": "MSFT",
        "name": "Microsoft Corporation",
        "sector": "Technology",
        "price": 415.80,
        "change": +4.20,
        "change_pct": +1.02,
        "market_cap": "3.09T",
        "pe_ratio": 36.8,
        "dividend_yield": 0.73,
        "52w_high": 441.76,
        "52w_low": 344.79,
        "volume": 22_450_000,
        "avg_volume": 21_800_000,
        "description": "Microsoft develops software, cloud services, and hardware. "
        "Azure is the second-largest cloud platform globally.",
    },
    "GOOGL": {
        "symbol": "GOOGL",
        "name": "Alphabet Inc.",
        "sector": "Communication Services",
        "price": 195.40,
        "change": -1.80,
        "change_pct": -0.91,
        "market_cap": "2.41T",
        "pe_ratio": 24.1,
        "dividend_yield": 0.47,
        "52w_high": 208.70,
        "52w_low": 130.67,
        "volume": 18_600_000,
        "avg_volume": 24_300_000,
        "description": "Alphabet operates Google Search, YouTube, Google Cloud, and various "
        "other ventures. Advertising is the primary revenue driver.",
    },
    "AMZN": {
        "symbol": "AMZN",
        "name": "Amazon.com Inc.",
        "sector": "Consumer Discretionary",
        "price": 230.10,
        "change": +3.60,
        "change_pct": +1.59,
        "market_cap": "2.44T",
        "pe_ratio": 44.7,
        "dividend_yield": 0.0,
        "52w_high": 242.52,
        "52w_low": 153.35,
        "volume": 35_200_000,
        "avg_volume": 38_500_000,
        "description": "Amazon operates e-commerce, AWS cloud services, Prime Video, "
        "and Alexa devices. AWS is the world's largest cloud platform.",
    },
    "NVDA": {
        "symbol": "NVDA",
        "name": "NVIDIA Corporation",
        "sector": "Technology",
        "price": 875.40,
        "change": +28.90,
        "change_pct": +3.42,
        "market_cap": "2.15T",
        "pe_ratio": 56.3,
        "dividend_yield": 0.03,
        "52w_high": 974.00,
        "52w_low": 475.09,
        "volume": 42_800_000,
        "avg_volume": 45_100_000,
        "description": "NVIDIA designs GPUs for gaming, professional visualization, data centers, "
        "and automotive. Dominant supplier for AI training infrastructure.",
    },
    "TSLA": {
        "symbol": "TSLA",
        "name": "Tesla Inc.",
        "sector": "Consumer Discretionary",
        "price": 312.60,
        "change": -8.40,
        "change_pct": -2.62,
        "market_cap": "998B",
        "pe_ratio": 78.1,
        "dividend_yield": 0.0,
        "52w_high": 488.54,
        "52w_low": 138.80,
        "volume": 88_100_000,
        "avg_volume": 92_300_000,
        "description": "Tesla manufactures electric vehicles, energy storage products, "
        "and solar panels. FSD autonomous driving is a key strategic initiative.",
    },
    "META": {
        "symbol": "META",
        "name": "Meta Platforms Inc.",
        "sector": "Communication Services",
        "price": 712.30,
        "change": +11.20,
        "change_pct": +1.60,
        "market_cap": "1.81T",
        "pe_ratio": 29.4,
        "dividend_yield": 0.27,
        "52w_high": 740.91,
        "52w_low": 414.50,
        "volume": 16_900_000,
        "avg_volume": 17_200_000,
        "description": "Meta owns Facebook, Instagram, WhatsApp, and Threads. "
        "Reality Labs division develops VR/AR hardware.",
    },
    "BRK.B": {
        "symbol": "BRK.B",
        "name": "Berkshire Hathaway Inc.",
        "sector": "Financials",
        "price": 489.70,
        "change": +1.30,
        "change_pct": +0.27,
        "market_cap": "1.07T",
        "pe_ratio": 22.6,
        "dividend_yield": 0.0,
        "52w_high": 502.60,
        "52w_low": 360.00,
        "volume": 4_200_000,
        "avg_volume": 3_800_000,
        "description": "Berkshire Hathaway is a conglomerate holding company. "
        "Key subsidiaries: BNSF Railway, Geico, and Berkshire Energy.",
    },
    "JPM": {
        "symbol": "JPM",
        "name": "JPMorgan Chase & Co.",
        "sector": "Financials",
        "price": 248.90,
        "change": +3.10,
        "change_pct": +1.26,
        "market_cap": "703B",
        "pe_ratio": 13.8,
        "dividend_yield": 1.85,
        "52w_high": 280.25,
        "52w_low": 183.14,
        "volume": 9_800_000,
        "avg_volume": 10_200_000,
        "description": "JPMorgan Chase is the largest U.S. bank by assets, "
        "with operations in investment banking, commercial banking, and wealth management.",
    },
    "V": {
        "symbol": "V",
        "name": "Visa Inc.",
        "sector": "Financials",
        "price": 344.20,
        "change": +2.80,
        "change_pct": +0.82,
        "market_cap": "703B",
        "pe_ratio": 31.5,
        "dividend_yield": 0.73,
        "52w_high": 365.40,
        "52w_low": 267.93,
        "volume": 6_500_000,
        "avg_volume": 5_900_000,
        "description": "Visa operates the world's largest retail electronic payments network, "
        "processing over 200 billion transactions annually.",
    },
    "SPY": {
        "symbol": "SPY",
        "name": "SPDR S&P 500 ETF Trust",
        "sector": "ETF",
        "price": 594.30,
        "change": +2.10,
        "change_pct": +0.35,
        "market_cap": "N/A",
        "pe_ratio": 24.8,
        "dividend_yield": 1.22,
        "52w_high": 613.23,
        "52w_low": 490.57,
        "volume": 72_300_000,
        "avg_volume": 68_400_000,
        "description": "SPY tracks the S&P 500 index, holding 503 large-cap U.S. stocks.",
    },
    "QQQ": {
        "symbol": "QQQ",
        "name": "Invesco QQQ Trust",
        "sector": "ETF",
        "price": 504.80,
        "change": +3.40,
        "change_pct": +0.68,
        "market_cap": "N/A",
        "pe_ratio": 31.2,
        "dividend_yield": 0.56,
        "52w_high": 540.81,
        "52w_low": 406.50,
        "volume": 38_700_000,
        "avg_volume": 42_100_000,
        "description": "QQQ tracks the Nasdaq-100 index, focused on large non-financial "
        "Nasdaq-listed companies. Heavy technology weighting.",
    },
}

_INDICES = {
    "^GSPC": {"name": "S&P 500", "value": 5891.20, "change": +12.40, "change_pct": +0.21},
    "^DJI": {"name": "Dow Jones Industrial Average", "value": 43218.50, "change": +175.30, "change_pct": +0.41},
    "^IXIC": {"name": "Nasdaq Composite", "value": 19340.10, "change": -58.20, "change_pct": -0.30},
    "^VIX": {"name": "CBOE Volatility Index", "value": 17.84, "change": -0.63, "change_pct": -3.41},
    "^TNX": {"name": "10-Year Treasury Yield", "value": 4.42, "change": +0.03, "change_pct": +0.68},
}

_PRICE_HISTORY: dict[str, list[dict]] = {
    "NVDA": [
        {"date": "2026-02-14", "open": 820.10, "high": 850.30, "low": 815.20, "close": 846.50, "volume": 38_200_000},
        {"date": "2026-02-17", "open": 848.00, "high": 870.40, "low": 840.10, "close": 862.10, "volume": 40_100_000},
        {"date": "2026-02-18", "open": 860.20, "high": 880.60, "low": 855.00, "close": 875.40, "volume": 42_800_000},
        {"date": "2026-02-19", "open": 875.40, "high": 912.00, "low": 870.00, "close": 902.80, "volume": 51_400_000},
        {"date": "2026-02-20", "open": 900.00, "high": 920.50, "low": 870.20, "close": 875.40, "volume": 42_800_000},
    ],
    "AAPL": [
        {"date": "2026-02-14", "open": 220.10, "high": 225.80, "low": 219.40, "close": 224.60, "volume": 50_100_000},
        {"date": "2026-02-17", "open": 224.80, "high": 228.40, "low": 222.10, "close": 226.30, "volume": 48_700_000},
        {"date": "2026-02-18", "open": 226.50, "high": 230.20, "low": 224.80, "close": 228.80, "volume": 53_200_000},
        {"date": "2026-02-19", "open": 228.90, "high": 231.40, "low": 226.70, "close": 227.10, "volume": 55_000_000},
        {"date": "2026-02-20", "open": 227.20, "high": 230.10, "low": 226.00, "close": 228.50, "volume": 54_320_000},
    ],
    "TSLA": [
        {"date": "2026-02-14", "open": 330.20, "high": 342.10, "low": 326.50, "close": 338.80, "volume": 90_100_000},
        {"date": "2026-02-17", "open": 338.50, "high": 345.00, "low": 325.30, "close": 328.40, "volume": 95_300_000},
        {"date": "2026-02-18", "open": 328.60, "high": 335.20, "low": 318.90, "close": 322.10, "volume": 88_700_000},
        {"date": "2026-02-19", "open": 322.00, "high": 328.40, "low": 310.50, "close": 321.00, "volume": 92_500_000},
        {"date": "2026-02-20", "open": 321.10, "high": 323.80, "low": 308.20, "close": 312.60, "volume": 88_100_000},
    ],
}

_NEWS: list[dict] = [
    {
        "symbol": "NVDA",
        "headline": "NVIDIA beats Q4 estimates; data center revenue surges 78% YoY",
        "source": "Reuters",
        "timestamp": "2026-02-20T16:30:00",
    },
    {
        "symbol": "NVDA",
        "headline": "Analysts raise NVDA price targets ahead of GTC developer conference",
        "source": "Barron's",
        "timestamp": "2026-02-20T09:15:00",
    },
    {
        "symbol": "AAPL",
        "headline": "Apple Vision Pro 2 supply chain ramp confirmed by suppliers",
        "source": "Bloomberg",
        "timestamp": "2026-02-20T11:00:00",
    },
    {
        "symbol": "TSLA",
        "headline": "Tesla February delivery numbers disappoint; shares slide",
        "source": "CNBC",
        "timestamp": "2026-02-20T14:00:00",
    },
    {
        "symbol": "META",
        "headline": "Meta's AI assistant crosses 1 billion monthly active users",
        "source": "WSJ",
        "timestamp": "2026-02-19T17:00:00",
    },
    {
        "symbol": "MSFT",
        "headline": "Microsoft Azure revenue grows 31% in latest quarter",
        "source": "MarketWatch",
        "timestamp": "2026-02-19T08:30:00",
    },
    {
        "symbol": "GOOGL",
        "headline": "Alphabet faces EU antitrust probe over AI search integration",
        "source": "FT",
        "timestamp": "2026-02-18T12:00:00",
    },
]


class YahooFinanceApp:
    """Dummy Yahoo Finance application with hardcoded market data."""

    def __init__(self) -> None:
        self.name = "yahoo_finance"

    # ------------------------------------------------------------------
    # Tools
    # ------------------------------------------------------------------

    def get_quote(self, symbol: str) -> dict:
        """Get the current stock quote for a ticker symbol.

        Args:
            symbol: Stock ticker symbol (e.g. 'AAPL', 'NVDA', 'SPY'). Case-insensitive.

        Returns:
            dict: Full quote with price, change, market cap, PE ratio, 52-week range, etc.
                  Returns error dict if symbol not found.

        Tags:
            finance, stock, quote, price, ticker
        """
        stock = _STOCKS.get(symbol.upper())
        if stock is None:
            return {"error": f"Symbol '{symbol}' not found. Available: {', '.join(sorted(_STOCKS))}"}
        return dict(stock)

    def get_multiple_quotes(self, symbols: list[str]) -> list[dict]:
        """Get quotes for multiple ticker symbols at once.

        Args:
            symbols: List of ticker symbols (e.g. ['AAPL', 'MSFT', 'NVDA']).

        Returns:
            list[dict]: Quote dicts in the same order as input symbols.

        Tags:
            finance, stocks, quotes, batch, compare
        """
        return [self.get_quote(sym) for sym in symbols]

    def get_market_summary(self) -> dict:
        """Get a summary of major market indices.

        Returns:
            dict: Current values and changes for S&P 500, Dow Jones, Nasdaq, VIX, and 10-year yield.

        Tags:
            finance, market, indices, summary, overview
        """
        return {sym: dict(data) for sym, data in _INDICES.items()}

    def get_price_history(self, symbol: str, period: str = "5d") -> dict:
        """Get historical OHLCV price data for a stock.

        Args:
            symbol: Ticker symbol (e.g. 'AAPL', 'NVDA', 'TSLA').
            period: Time period — only '5d' (5 trading days) is supported.

        Returns:
            dict: Contains 'symbol' and 'history' list with date, open, high, low,
                  close, volume per day. Returns error dict if symbol not found.

        Tags:
            finance, history, ohlcv, price, chart
        """
        symbol = symbol.upper()
        history = _PRICE_HISTORY.get(symbol)
        if history is None:
            return {"error": f"No history available for '{symbol}'. Try: AAPL, NVDA, TSLA."}
        return {"symbol": symbol, "period": period, "history": history}

    def search_stocks(self, query: str) -> list[dict]:
        """Search for stocks by company name or sector.

        Args:
            query: Search string matched against company name, symbol, and sector (case-insensitive).

        Returns:
            list[dict]: Matching stocks with symbol, name, sector, and current price.

        Tags:
            finance, search, stocks, screener, find
        """
        q = query.lower()
        results = []
        for stock in _STOCKS.values():
            if q in stock["symbol"].lower() or q in stock["name"].lower() or q in stock["sector"].lower():
                results.append(
                    {
                        "symbol": stock["symbol"],
                        "name": stock["name"],
                        "sector": stock["sector"],
                        "price": stock["price"],
                        "change_pct": stock["change_pct"],
                    }
                )
        return results

    def get_news(self, symbol: str | None = None, limit: int = 5) -> list[dict]:
        """Get latest financial news headlines, optionally filtered by stock symbol.

        Args:
            symbol: Ticker symbol to filter news for, or None for all news.
            limit: Maximum number of headlines to return (default 5).

        Returns:
            list[dict]: News items with headline, source, symbol, and timestamp.

        Tags:
            finance, news, headlines, market, stocks
        """
        news = _NEWS
        if symbol:
            news = [n for n in news if n["symbol"] == symbol.upper()]
        news = sorted(news, key=lambda n: n["timestamp"], reverse=True)
        return news[:limit]

    def get_sector_performance(self) -> list[dict]:
        """Get performance summary grouped by market sector.

        Returns:
            list[dict]: Each entry has sector name, stock count, and average price change %.

        Tags:
            finance, sectors, performance, market, overview
        """
        from collections import defaultdict

        sector_changes: dict[str, list[float]] = defaultdict(list)
        for stock in _STOCKS.values():
            sector_changes[stock["sector"]].append(stock["change_pct"])
        results = []
        for sector, changes in sorted(sector_changes.items()):
            avg = sum(changes) / len(changes)
            results.append(
                {
                    "sector": sector,
                    "stock_count": len(changes),
                    "avg_change_pct": round(avg, 2),
                }
            )
        return sorted(results, key=lambda x: x["avg_change_pct"], reverse=True)

    # ------------------------------------------------------------------

    def list_tools(self) -> list:
        return [
            self.get_quote,
            self.get_multiple_quotes,
            self.get_market_summary,
            self.get_price_history,
            self.search_stocks,
            self.get_news,
            self.get_sector_performance,
        ]

    def create_mcp_server(self) -> FastMCP:
        mcp = FastMCP(self.name)
        for tool_fn in self.list_tools():
            mcp.tool()(tool_fn)
        return mcp


if __name__ == "__main__":
    app = YahooFinanceApp()
    server = app.create_mcp_server()
    server.run()
