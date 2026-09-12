"""FastMCP server instance for the yfinance MCP.

The `mcp` instance defined here is imported by every module under
`app.tools`, which register their functions as tools via the `@mcp.tool()`
decorator. Importing those modules at the bottom of this file (after `mcp`
exists) is what triggers that registration.
"""

from __future__ import annotations

from fastmcp import FastMCP

mcp = FastMCP(
    name="yfinance-mcp",
    instructions=(
        "MCP server exposing Yahoo Finance market data via the yfinance Python "
        "library. Use `get_company_info` to fetch a full company/security "
        "profile for a given ticker (name, sector, valuation, price, dividends, "
        "etc.) — this is usually the best starting point for a single ticker. "
        "Other tools cover price history, dividends/splits, financial "
        "statements, ownership/holders, analyst estimates and recommendations, "
        "options chains, news, SEC filings, and market-wide search/lookup/status. "
        "Ticker symbols follow Yahoo Finance conventions, e.g. 'AAPL', 'MSFT', "
        "'PETR4.SA' (B3/Brazil), '^GSPC' (indices), 'BTC-USD' (crypto)."
    ),
)

# Import tool modules so their @mcp.tool() decorators run and register the
# tools on `mcp`. The imports are intentionally placed after `mcp` is defined
# and are unused directly in this module (registration is a side effect).
from app.tools import (  # noqa: E402,F401
    analysis,
    company,
    financials,
    holders,
    market,
    options,
    price,
)
