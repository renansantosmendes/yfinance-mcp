"""Unit tests for app.utils.ticker_cache.

yfinance.Ticker's constructor does not perform any network I/O (data is
fetched lazily on first attribute access), so these tests can safely
construct real Ticker objects without hitting the network.
"""

from __future__ import annotations

import pytest

from app.utils.ticker_cache import get_ticker


def test_get_ticker_normalizes_symbol():
    ticker = get_ticker(" aapl ")
    assert ticker.ticker == "AAPL"


def test_get_ticker_returns_same_cached_instance_for_same_symbol():
    assert get_ticker("MSFT") is get_ticker("MSFT")


def test_get_ticker_is_case_insensitive_for_caching():
    assert get_ticker("msft") is get_ticker("MSFT")


def test_get_ticker_rejects_empty_symbol():
    with pytest.raises(ValueError):
        get_ticker("   ")


def test_get_ticker_rejects_none():
    with pytest.raises(ValueError):
        get_ticker(None)  # type: ignore[arg-type]
