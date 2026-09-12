"""Price history, dividends, splits and shares outstanding tools."""

from __future__ import annotations

from typing import Optional

from app.mcp_server import mcp
from app.utils.serialization import clean_dict, dataframe_to_records, export_any
from app.utils.ticker_cache import get_ticker


@mcp.tool()
def get_history(
    ticker: str,
    period: str = "1mo",
    interval: str = "1d",
    start: Optional[str] = None,
    end: Optional[str] = None,
    auto_adjust: bool = True,
    prepost: bool = False,
    actions: bool = True,
) -> dict:
    """Get historical OHLCV (open/high/low/close/volume) price data for a ticker.

    Args:
        ticker: Stock ticker symbol.
        period: One of 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max. Ignored if start/end are given.
        interval: One of 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo. Intraday
            intervals (<1d) are only available for the last ~60 days.
        start: Optional start date "YYYY-MM-DD", overrides period.
        end: Optional end date "YYYY-MM-DD".
        auto_adjust: Adjust OHLC prices for splits and dividends.
        prepost: Include pre/post market data (intraday intervals only).
        actions: Include dividends/splits columns in the result.
    """
    t = get_ticker(ticker)
    kwargs: dict = dict(interval=interval, auto_adjust=auto_adjust, prepost=prepost, actions=actions)
    if start or end:
        kwargs["start"] = start
        kwargs["end"] = end
    else:
        kwargs["period"] = period
    df = t.history(**kwargs)
    return {"ticker": ticker.strip().upper(), "rows": dataframe_to_records(df, index_name="date")}


@mcp.tool()
def get_dividends(ticker: str) -> dict:
    """Get the full historical dividend payment record for a ticker.

    Args:
        ticker: Stock ticker symbol.
    """
    t = get_ticker(ticker)
    series = t.dividends
    frame = series.to_frame(name="dividend") if series is not None else None
    return {"ticker": ticker.strip().upper(), "dividends": dataframe_to_records(frame, index_name="date")}


@mcp.tool()
def get_splits(ticker: str) -> dict:
    """Get the full historical stock split record for a ticker.

    Args:
        ticker: Stock ticker symbol.
    """
    t = get_ticker(ticker)
    series = t.splits
    frame = series.to_frame(name="split_ratio") if series is not None else None
    return {"ticker": ticker.strip().upper(), "splits": dataframe_to_records(frame, index_name="date")}


@mcp.tool()
def get_capital_gains(ticker: str) -> dict:
    """Get the historical capital gains distribution record (relevant for mutual funds/ETFs).

    Args:
        ticker: Stock ticker symbol.
    """
    t = get_ticker(ticker)
    series = t.capital_gains
    frame = series.to_frame(name="capital_gain") if series is not None else None
    return {"ticker": ticker.strip().upper(), "capital_gains": dataframe_to_records(frame, index_name="date")}


@mcp.tool()
def get_actions(ticker: str) -> dict:
    """Get the combined corporate actions history (dividends + stock splits) for a ticker.

    Args:
        ticker: Stock ticker symbol.
    """
    t = get_ticker(ticker)
    return {"ticker": ticker.strip().upper(), "actions": dataframe_to_records(t.actions, index_name="date")}


@mcp.tool()
def get_shares_outstanding(ticker: str, start: Optional[str] = None, end: Optional[str] = None) -> dict:
    """Get shares outstanding for a ticker.

    If start/end are given, returns the historical daily shares-outstanding
    series in that window. Otherwise, returns the latest known shares
    outstanding figure (from the company info).

    Args:
        ticker: Stock ticker symbol.
        start: Optional start date "YYYY-MM-DD".
        end: Optional end date "YYYY-MM-DD".
    """
    t = get_ticker(ticker)
    if start or end:
        shares = t.get_shares_full(start=start, end=end)
        if shares is None:
            return {"ticker": ticker.strip().upper(), "shares": []}
        frame = shares.to_frame(name="shares_outstanding")
        return {"ticker": ticker.strip().upper(), "shares": dataframe_to_records(frame, index_name="date")}
    info = t.info or {}
    return {
        "ticker": ticker.strip().upper(),
        "shares_outstanding": info.get("sharesOutstanding"),
        "float_shares": info.get("floatShares"),
        "implied_shares_outstanding": info.get("impliedSharesOutstanding"),
    }
