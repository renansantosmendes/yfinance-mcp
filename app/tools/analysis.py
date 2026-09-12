"""Analyst research tools: recommendations, estimates, calendar, ESG, news, filings."""

from __future__ import annotations

from app.mcp_server import mcp
from app.utils.serialization import clean_dict, export_any
from app.utils.ticker_cache import get_ticker


@mcp.tool()
def get_recommendations(ticker: str) -> dict:
    """Get the historical trend of analyst recommendations (counts of strongBuy/buy/hold/sell/strongSell by month).

    Args:
        ticker: Stock ticker symbol.
    """
    t = get_ticker(ticker)
    return {"ticker": ticker.strip().upper(), "recommendations": export_any(t.recommendations)}


@mcp.tool()
def get_recommendations_summary(ticker: str) -> dict:
    """Get a summarized snapshot of current analyst recommendations.

    Args:
        ticker: Stock ticker symbol.
    """
    t = get_ticker(ticker)
    return {"ticker": ticker.strip().upper(), "recommendations_summary": export_any(t.recommendations_summary)}


@mcp.tool()
def get_upgrades_downgrades(ticker: str) -> dict:
    """Get the history of analyst rating upgrades/downgrades (firm, from-grade, to-grade, action, date).

    Args:
        ticker: Stock ticker symbol.
    """
    t = get_ticker(ticker)
    return {"ticker": ticker.strip().upper(), "upgrades_downgrades": export_any(t.upgrades_downgrades)}


@mcp.tool()
def get_analyst_price_targets(ticker: str) -> dict:
    """Get analyst price targets (current, low, high, mean, median).

    Args:
        ticker: Stock ticker symbol.
    """
    t = get_ticker(ticker)
    return {"ticker": ticker.strip().upper(), "analyst_price_targets": export_any(t.analyst_price_targets)}


@mcp.tool()
def get_earnings_estimate(ticker: str) -> dict:
    """Get analyst EPS (earnings-per-share) estimates by period (current/next quarter, current/next year).

    Args:
        ticker: Stock ticker symbol.
    """
    t = get_ticker(ticker)
    return {"ticker": ticker.strip().upper(), "earnings_estimate": export_any(t.earnings_estimate)}


@mcp.tool()
def get_revenue_estimate(ticker: str) -> dict:
    """Get analyst revenue estimates by period (current/next quarter, current/next year).

    Args:
        ticker: Stock ticker symbol.
    """
    t = get_ticker(ticker)
    return {"ticker": ticker.strip().upper(), "revenue_estimate": export_any(t.revenue_estimate)}


@mcp.tool()
def get_earnings_history(ticker: str) -> dict:
    """Get historical earnings surprises (EPS estimate vs. actual and surprise %).

    Args:
        ticker: Stock ticker symbol.
    """
    t = get_ticker(ticker)
    return {"ticker": ticker.strip().upper(), "earnings_history": export_any(t.earnings_history)}


@mcp.tool()
def get_eps_trend(ticker: str) -> dict:
    """Get the trend of EPS estimate values over recent revision periods (7/30/60/90 days ago vs. now).

    Args:
        ticker: Stock ticker symbol.
    """
    t = get_ticker(ticker)
    return {"ticker": ticker.strip().upper(), "eps_trend": export_any(t.eps_trend)}


@mcp.tool()
def get_eps_revisions(ticker: str) -> dict:
    """Get the count of recent EPS estimate revisions (analysts revising up/down).

    Args:
        ticker: Stock ticker symbol.
    """
    t = get_ticker(ticker)
    return {"ticker": ticker.strip().upper(), "eps_revisions": export_any(t.eps_revisions)}


@mcp.tool()
def get_growth_estimates(ticker: str) -> dict:
    """Get growth estimates for the company compared to its industry, sector and the S&P 500.

    Args:
        ticker: Stock ticker symbol.
    """
    t = get_ticker(ticker)
    return {"ticker": ticker.strip().upper(), "growth_estimates": export_any(t.growth_estimates)}


@mcp.tool()
def get_calendar(ticker: str) -> dict:
    """Get upcoming calendar events: next earnings date, ex-dividend date, projected revenue/earnings range.

    Args:
        ticker: Stock ticker symbol.
    """
    t = get_ticker(ticker)
    calendar = t.calendar
    data = clean_dict(calendar) if isinstance(calendar, dict) else export_any(calendar)
    return {"ticker": ticker.strip().upper(), "calendar": data}


@mcp.tool()
def get_earnings_dates(ticker: str, limit: int = 12) -> dict:
    """Get past and upcoming earnings dates along with EPS estimate/actual and surprise %.

    Args:
        ticker: Stock ticker symbol.
        limit: Maximum number of earnings dates to return.
    """
    t = get_ticker(ticker)
    return {"ticker": ticker.strip().upper(), "earnings_dates": export_any(t.get_earnings_dates(limit=limit))}


@mcp.tool()
def get_sustainability(ticker: str) -> dict:
    """Get ESG (Environmental, Social, Governance) sustainability scores for a company.

    Args:
        ticker: Stock ticker symbol.
    """
    t = get_ticker(ticker)
    return {"ticker": ticker.strip().upper(), "sustainability": export_any(t.sustainability)}


@mcp.tool()
def get_sec_filings(ticker: str) -> dict:
    """Get a list of recent SEC filings (10-K, 10-Q, 8-K, etc.) for the company.

    Args:
        ticker: Stock ticker symbol.
    """
    t = get_ticker(ticker)
    return {"ticker": ticker.strip().upper(), "sec_filings": export_any(t.sec_filings)}


@mcp.tool()
def get_news(ticker: str) -> dict:
    """Get recent news articles related to a ticker.

    Args:
        ticker: Stock ticker symbol.
    """
    t = get_ticker(ticker)
    return {"ticker": ticker.strip().upper(), "news": export_any(t.news)}
