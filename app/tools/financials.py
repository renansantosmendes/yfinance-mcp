"""Financial statement tools: income statement, balance sheet, cash flow."""

from __future__ import annotations

from app.mcp_server import mcp
from app.utils.serialization import export_any
from app.utils.ticker_cache import get_ticker


@mcp.tool()
def get_income_statement(ticker: str, quarterly: bool = False) -> dict:
    """Get the income statement (revenue, gross profit, operating income, net income, EPS, etc.).

    Args:
        ticker: Stock ticker symbol.
        quarterly: If True, return quarterly figures instead of annual.
    """
    t = get_ticker(ticker)
    stmt = t.quarterly_income_stmt if quarterly else t.income_stmt
    return {"ticker": ticker.strip().upper(), "quarterly": quarterly, "income_statement": export_any(stmt)}


@mcp.tool()
def get_balance_sheet(ticker: str, quarterly: bool = False) -> dict:
    """Get the balance sheet (total assets, liabilities, equity, cash, debt, etc.).

    Args:
        ticker: Stock ticker symbol.
        quarterly: If True, return quarterly figures instead of annual.
    """
    t = get_ticker(ticker)
    stmt = t.quarterly_balance_sheet if quarterly else t.balance_sheet
    return {"ticker": ticker.strip().upper(), "quarterly": quarterly, "balance_sheet": export_any(stmt)}


@mcp.tool()
def get_cashflow(ticker: str, quarterly: bool = False) -> dict:
    """Get the cash flow statement (operating/investing/financing cash flow, free cash flow, capex, etc.).

    Args:
        ticker: Stock ticker symbol.
        quarterly: If True, return quarterly figures instead of annual.
    """
    t = get_ticker(ticker)
    stmt = t.quarterly_cashflow if quarterly else t.cashflow
    return {"ticker": ticker.strip().upper(), "quarterly": quarterly, "cashflow": export_any(stmt)}
