"""Yahoo Finance application — dummy MCP server with hardcoded market data."""

from __future__ import annotations

from fastmcp import FastMCP

from worlds.utils import load_seed_data


class YahooFinanceApp:
    """Dummy Yahoo Finance application with hardcoded market data."""

    def __init__(self) -> None:
        self.name = "yahoo_finance"
        self.data = load_seed_data("finance")
        self._stocks = self.data["_STOCKS"]
        self._indices = self.data["_INDICES"]
        self._price_history = self.data["_PRICE_HISTORY"]
        self._news = self.data["_NEWS"]

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
        stock = self._stocks.get(symbol.upper())
        if stock is None:
            return {"error": f"Symbol '{symbol}' not found. Available: {', '.join(sorted(self._stocks))}"}
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
        return {sym: dict(data) for sym, data in self._indices.items()}

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
        history = self._price_history.get(symbol)
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
        for stock in self._stocks.values():
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
        news = self._news
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
        for stock in self._stocks.values():
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
