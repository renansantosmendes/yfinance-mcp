"""Module-level yfinance features: multi-ticker download, search, lookup, market status."""

from __future__ import annotations

from typing import Optional

import yfinance as yf

from app.mcp_server import mcp
from app.utils.params import build_period_kwargs
from app.utils.serialization import clean_dict, export_any


@mcp.tool()
def download_history(
    tickers: str,
    period: str = "1mo",
    interval: str = "1d",
    start: Optional[str] = None,
    end: Optional[str] = None,
    group_by: str = "ticker",
    auto_adjust: bool = True,
) -> dict:
    """Download historical OHLCV data for one or more tickers in a single call.

    Args:
        tickers: Space-separated ticker symbols, e.g. "AAPL MSFT GOOG".
        period: One of 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max. Ignored if start/end are given.
        interval: One of 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo.
        start: Optional start date "YYYY-MM-DD".
        end: Optional end date "YYYY-MM-DD".
        group_by: "ticker" or "column" — how result columns are grouped.
        auto_adjust: Adjust OHLC prices for splits and dividends.
    """
    kwargs = {
        "tickers": tickers,
        "interval": interval,
        "group_by": group_by,
        "auto_adjust": auto_adjust,
        "progress": False,
        **build_period_kwargs(period, start, end),
    }
    df = yf.download(**kwargs)
    if df is None or df.empty:
        return {"tickers": tickers, "rows": []}
    df = df.reset_index()
    df.columns = [
        ".".join(str(part) for part in col if part not in (None, "")) if isinstance(col, tuple) else str(col)
        for col in df.columns
    ]
    return {"tickers": tickers, "rows": export_any(df)}


@mcp.tool()
def search_symbols(query: str, max_results: int = 8) -> dict:
    """Search Yahoo Finance for tickers, companies and related news matching a free-text query.

    Args:
        query: Free-text search query, e.g. "Apple" or "bitcoin".
        max_results: Maximum number of quote results to return.
    """
    s = yf.Search(query, max_results=max_results)
    return {
        "query": query,
        "quotes": export_any(s.quotes),
        "news": export_any(s.news),
    }


@mcp.tool()
def lookup_symbols(query: str, lookup_type: Optional[str] = None, count: int = 10) -> dict:
    """Look up ticker symbols by name or keyword, optionally filtered by asset type.

    Args:
        query: Free-text search query, e.g. "microsoft".
        lookup_type: Optional filter — one of "stock", "etf", "mutualfund", "index",
            "future", "currency", "cryptocurrency". Omit to search across all types.
        count: Maximum number of results to return.
    """
    lookup = yf.Lookup(query)
    type_map = {
        "stock": lookup.get_stock,
        "etf": lookup.get_etf,
        "mutualfund": lookup.get_mutualfund,
        "index": lookup.get_index,
        "future": lookup.get_future,
        "currency": lookup.get_currency,
        "cryptocurrency": lookup.get_cryptocurrency,
    }
    if lookup_type:
        lookup_type = lookup_type.strip().lower()
        if lookup_type not in type_map:
            return {"query": query, "error": f"Unknown lookup_type '{lookup_type}'.", "valid_types": list(type_map)}
        result = type_map[lookup_type](count=count)
        return {"query": query, "type": lookup_type, "results": export_any(result)}
    result = lookup.get_all(count=count)
    return {"query": query, "type": "all", "results": export_any(result)}


@mcp.tool()
def get_market_status(market: str = "US") -> dict:
    """Get trading session status and index summary for a market.

    Args:
        market: Market identifier, e.g. "US", "GB", "JP", "BR", "CA".
    """
    m = yf.Market(market)
    return {
        "market": market,
        "status": clean_dict(m.status) if isinstance(m.status, dict) else export_any(m.status),
        "summary": export_any(m.summary),
    }


@mcp.tool()
def get_multiple_quotes(tickers: str) -> dict:
    """Get a fast price snapshot (fast_info) for several tickers at once.

    Args:
        tickers: Space-separated ticker symbols, e.g. "AAPL MSFT GOOG".
    """
    ts = yf.Tickers(tickers)
    result = {}
    for symbol, t in ts.tickers.items():
        try:
            result[symbol] = clean_dict(dict(t.fast_info))
        except Exception as exc:  # pylint: disable=broad-exception-caught
            # A single bad/delisted ticker must not fail the whole batch;
            # its error is reported inline instead.
            result[symbol] = {"error": str(exc)}
    return {"tickers": tickers, "quotes": result}
