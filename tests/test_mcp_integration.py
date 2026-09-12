"""End-to-end tests exercising the real MCP protocol path (in-memory transport).

These complement the per-tool unit tests by verifying that every tool is
actually registered on the FastMCP server and that a full call — including
MCP request/response (de)serialization — round-trips correctly.
"""

from __future__ import annotations

import pytest
from fastmcp import Client

from app.mcp_server import mcp
from app.tools import company
from tests.conftest import FakeTicker

EXPECTED_TOOL_NAMES = {
    "get_company_info",
    "get_fast_info",
    "get_isin",
    "get_history",
    "get_dividends",
    "get_splits",
    "get_capital_gains",
    "get_actions",
    "get_shares_outstanding",
    "get_income_statement",
    "get_balance_sheet",
    "get_cashflow",
    "get_major_holders",
    "get_institutional_holders",
    "get_mutualfund_holders",
    "get_insider_transactions",
    "get_insider_purchases",
    "get_insider_roster_holders",
    "get_recommendations",
    "get_recommendations_summary",
    "get_upgrades_downgrades",
    "get_analyst_price_targets",
    "get_earnings_estimate",
    "get_revenue_estimate",
    "get_earnings_history",
    "get_eps_trend",
    "get_eps_revisions",
    "get_growth_estimates",
    "get_calendar",
    "get_earnings_dates",
    "get_sustainability",
    "get_sec_filings",
    "get_news",
    "get_options_expirations",
    "get_option_chain",
    "download_history",
    "search_symbols",
    "lookup_symbols",
    "get_market_status",
    "get_multiple_quotes",
}


@pytest.mark.asyncio
async def test_every_expected_tool_is_registered():
    async with Client(mcp) as client:
        tools = await client.list_tools()

    names = {t.name for t in tools}
    assert names == EXPECTED_TOOL_NAMES


@pytest.mark.asyncio
async def test_get_company_info_round_trips_through_the_mcp_protocol(monkeypatch):
    fake = FakeTicker(info={"shortName": "Apple Inc.", "sector": "Technology"})
    monkeypatch.setattr(company, "get_ticker", lambda ticker: fake)

    async with Client(mcp) as client:
        result = await client.call_tool("get_company_info", {"ticker": "AAPL"})

    assert result.data["ticker"] == "AAPL"
    assert result.data["info"]["shortName"] == "Apple Inc."


@pytest.mark.asyncio
async def test_calling_an_unknown_tool_raises():
    async with Client(mcp) as client:
        with pytest.raises(Exception):  # pylint: disable=broad-exception-caught
            await client.call_tool("not_a_real_tool", {})
