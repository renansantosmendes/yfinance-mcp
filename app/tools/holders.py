"""Ownership tools: major/institutional/mutual fund holders and insider activity."""

from __future__ import annotations

from app.mcp_server import mcp
from app.utils.serialization import export_any
from app.utils.ticker_cache import get_ticker


@mcp.tool()
def get_major_holders(ticker: str) -> dict:
    """Get the major-holders breakdown (percent held by insiders, institutions, etc.).

    Args:
        ticker: Stock ticker symbol.
    """
    t = get_ticker(ticker)
    return {"ticker": ticker.strip().upper(), "major_holders": export_any(t.major_holders)}


@mcp.tool()
def get_institutional_holders(ticker: str) -> dict:
    """Get the top institutional holders of a stock (fund name, shares, value, % held).

    Args:
        ticker: Stock ticker symbol.
    """
    t = get_ticker(ticker)
    return {"ticker": ticker.strip().upper(), "institutional_holders": export_any(t.institutional_holders)}


@mcp.tool()
def get_mutualfund_holders(ticker: str) -> dict:
    """Get the top mutual fund holders of a stock.

    Args:
        ticker: Stock ticker symbol.
    """
    t = get_ticker(ticker)
    return {"ticker": ticker.strip().upper(), "mutualfund_holders": export_any(t.mutualfund_holders)}


@mcp.tool()
def get_insider_transactions(ticker: str) -> dict:
    """Get recent insider transactions (buys/sells by company officers and directors).

    Args:
        ticker: Stock ticker symbol.
    """
    t = get_ticker(ticker)
    return {"ticker": ticker.strip().upper(), "insider_transactions": export_any(t.insider_transactions)}


@mcp.tool()
def get_insider_purchases(ticker: str) -> dict:
    """Get a summary of recent insider purchase activity (net shares bought/sold).

    Args:
        ticker: Stock ticker symbol.
    """
    t = get_ticker(ticker)
    return {"ticker": ticker.strip().upper(), "insider_purchases": export_any(t.insider_purchases)}


@mcp.tool()
def get_insider_roster_holders(ticker: str) -> dict:
    """Get the roster of individual company insiders and their current holdings.

    Args:
        ticker: Stock ticker symbol.
    """
    t = get_ticker(ticker)
    return {"ticker": ticker.strip().upper(), "insider_roster_holders": export_any(t.insider_roster_holders)}
