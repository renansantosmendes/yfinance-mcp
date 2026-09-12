"""Company profile / snapshot tools — includes the flagship `get_company_info`."""

from __future__ import annotations

from app.mcp_server import mcp
from app.utils.serialization import clean_dict, export_any
from app.utils.ticker_cache import get_ticker


@mcp.tool()
def get_company_info(ticker: str) -> dict:
    """Get the complete company/security profile for a ticker symbol.

    This is the main "give me everything about this company" tool. It returns
    a comprehensive dict with fields such as: long/short name, sector, industry,
    business summary, website, country, employee count, valuation metrics
    (market cap, trailing/forward P/E, PEG, price-to-book, EV/EBITDA), price
    data (current price, 52-week high/low, day range, volume), dividend info
    (yield, rate, ex-dividend date, payout ratio), profitability margins,
    analyst target prices/recommendations, and more — exactly as provided by
    Yahoo Finance's quote summary.

    Args:
        ticker: Stock ticker symbol, e.g. "AAPL", "MSFT", "PETR4.SA", "VALE3.SA".
    """
    t = get_ticker(ticker)
    info = t.info or {}
    return {"ticker": ticker.strip().upper(), "info": clean_dict(info)}


@mcp.tool()
def get_fast_info(ticker: str) -> dict:
    """Get a fast/lightweight price snapshot for a ticker.

    Much cheaper than get_company_info: returns current price, previous close,
    day/year high-low, market cap, shares outstanding, volume and currency.
    Use this when you just need current price data quickly.

    Args:
        ticker: Stock ticker symbol, e.g. "AAPL".
    """
    t = get_ticker(ticker)
    fast_info = dict(t.fast_info) if t.fast_info is not None else {}
    return {"ticker": ticker.strip().upper(), "fast_info": clean_dict(fast_info)}


@mcp.tool()
def get_isin(ticker: str) -> dict:
    """Get the ISIN (International Securities Identification Number) for a ticker.

    Args:
        ticker: Stock ticker symbol.
    """
    t = get_ticker(ticker)
    return {"ticker": ticker.strip().upper(), "isin": export_any(t.isin)}
