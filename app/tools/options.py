"""Options chain tools."""

from __future__ import annotations

from typing import Optional

from app.mcp_server import mcp
from app.utils.serialization import export_any
from app.utils.ticker_cache import get_ticker


@mcp.tool()
def get_options_expirations(ticker: str) -> dict:
    """Get the list of available options expiration dates for a ticker.

    Args:
        ticker: Stock ticker symbol.
    """
    t = get_ticker(ticker)
    return {"ticker": ticker.strip().upper(), "expirations": list(t.options)}


@mcp.tool()
def get_option_chain(ticker: str, expiration_date: Optional[str] = None) -> dict:
    """Get the full options chain (calls and puts) for a ticker at a given expiration.

    Args:
        ticker: Stock ticker symbol.
        expiration_date: Expiration date "YYYY-MM-DD". If omitted, the nearest
            available expiration date is used.
    """
    t = get_ticker(ticker)
    expirations = t.options
    if not expirations:
        return {"ticker": ticker.strip().upper(), "error": "No options data available for this ticker."}
    if not expiration_date:
        expiration_date = expirations[0]
    elif expiration_date not in expirations:
        return {
            "ticker": ticker.strip().upper(),
            "error": f"'{expiration_date}' is not a valid expiration date.",
            "available_expirations": list(expirations),
        }
    chain = t.option_chain(expiration_date)
    return {
        "ticker": ticker.strip().upper(),
        "expiration_date": expiration_date,
        "calls": export_any(chain.calls),
        "puts": export_any(chain.puts),
    }
