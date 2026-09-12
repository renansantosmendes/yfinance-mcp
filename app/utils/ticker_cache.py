"""Helpers to obtain (and reuse) yfinance Ticker objects."""

from __future__ import annotations

from functools import lru_cache

import yfinance as yf


def get_ticker(symbol: str) -> yf.Ticker:
    """Return a cached yfinance.Ticker instance for the given symbol.

    Caching avoids re-instantiating (and re-hitting Yahoo Finance's session
    handshake) for repeated calls to the same ticker within the same
    serverless invocation. The symbol is normalized (stripped/uppercased)
    *before* hitting the cache, so "aapl" and "AAPL" share one cached
    instance instead of creating two.
    """
    if not symbol or not symbol.strip():
        raise ValueError("ticker must be a non-empty string")
    return _get_ticker_cached(symbol.strip().upper())


@lru_cache(maxsize=256)
def _get_ticker_cached(normalized_symbol: str) -> yf.Ticker:
    return yf.Ticker(normalized_symbol)
