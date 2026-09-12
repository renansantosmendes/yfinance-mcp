"""Unit tests for app.tools.market (module-level yfinance features)."""

from __future__ import annotations

import pandas as pd

from app.tools import market


def test_download_history_empty_result(monkeypatch):
    monkeypatch.setattr(market.yf, "download", lambda **kwargs: pd.DataFrame())

    result = market.download_history.fn(tickers="AAPL MSFT")

    assert result["rows"] == []


def test_download_history_flattens_multiindex_columns(monkeypatch):
    idx = pd.to_datetime(["2024-01-01"])
    columns = pd.MultiIndex.from_tuples([("Close", "AAPL"), ("Close", "MSFT")])
    df = pd.DataFrame([[150.0, 300.0]], index=idx, columns=columns)
    monkeypatch.setattr(market.yf, "download", lambda **kwargs: df)

    result = market.download_history.fn(tickers="AAPL MSFT", period="5d")

    row = result["rows"][0]
    assert row["Close.AAPL"] == 150.0
    assert row["Close.MSFT"] == 300.0


def test_download_history_passes_explicit_date_range(monkeypatch):
    captured = {}

    def fake_download(**kwargs):
        captured.update(kwargs)
        return pd.DataFrame()

    monkeypatch.setattr(market.yf, "download", fake_download)

    market.download_history.fn(tickers="AAPL", start="2024-01-01", end="2024-02-01")

    assert captured["start"] == "2024-01-01"
    assert captured["end"] == "2024-02-01"
    assert "period" not in captured


class FakeSearch:
    """Stand-in for yfinance.Search."""

    def __init__(self, query, max_results=8):
        self.query = query
        self.max_results = max_results
        self.quotes = [{"symbol": "AAPL"}]
        self.news = [{"title": "Apple news"}]


def test_search_symbols(monkeypatch):
    monkeypatch.setattr(market.yf, "Search", FakeSearch)

    result = market.search_symbols.fn(query="Apple")

    assert result["quotes"][0]["symbol"] == "AAPL"
    assert result["news"][0]["title"] == "Apple news"


class FakeLookup:
    """Stand-in for yfinance.Lookup, covering every asset-type getter the tool wires up."""

    def __init__(self, query):
        self.query = query

    def get_stock(self, count=10):
        del count
        return [{"symbol": "AAPL"}]

    def get_etf(self, count=10):
        del count
        return []

    def get_mutualfund(self, count=10):
        del count
        return []

    def get_index(self, count=10):
        del count
        return []

    def get_future(self, count=10):
        del count
        return []

    def get_currency(self, count=10):
        del count
        return []

    def get_cryptocurrency(self, count=10):
        del count
        return []

    def get_all(self, count=10):
        del count
        return [{"symbol": "AAPL"}, {"symbol": "AAPL.MX"}]


def test_lookup_symbols_with_explicit_type(monkeypatch):
    monkeypatch.setattr(market.yf, "Lookup", FakeLookup)

    result = market.lookup_symbols.fn(query="apple", lookup_type="stock")

    assert result["type"] == "stock"
    assert result["results"][0]["symbol"] == "AAPL"


def test_lookup_symbols_without_type_searches_all(monkeypatch):
    monkeypatch.setattr(market.yf, "Lookup", FakeLookup)

    result = market.lookup_symbols.fn(query="apple")

    assert result["type"] == "all"
    assert len(result["results"]) == 2


def test_lookup_symbols_rejects_unknown_type(monkeypatch):
    monkeypatch.setattr(market.yf, "Lookup", FakeLookup)

    result = market.lookup_symbols.fn(query="apple", lookup_type="bogus")

    assert "error" in result
    assert "valid_types" in result


class FakeMarket:
    """Stand-in for yfinance.Market."""

    def __init__(self, market_id):
        self.market_id = market_id
        self.status = {"status": "open"}
        self.summary = {"^GSPC": {"price": 5000}}


def test_get_market_status(monkeypatch):
    monkeypatch.setattr(market.yf, "Market", FakeMarket)

    result = market.get_market_status.fn(market="US")

    assert result["status"]["status"] == "open"
    assert result["summary"]["^GSPC"]["price"] == 5000


class _RaisingFastInfo:
    """A ticker whose fast_info access fails, e.g. a delisted symbol."""

    @property
    def fast_info(self):
        raise RuntimeError("no data")


class FakeFastInfoTicker:
    """Stand-in for a yfinance.Ticker exposing only fast_info."""

    def __init__(self, fast_info):
        self.fast_info = fast_info


class FakeTickers:
    """Stand-in for yfinance.Tickers."""

    def __init__(self, symbols):
        del symbols
        self.tickers = {
            "AAPL": FakeFastInfoTicker({"lastPrice": 190.0}),
            "ZZZZ": _RaisingFastInfo(),
        }


def test_get_multiple_quotes_reports_per_ticker_errors_without_failing_batch(monkeypatch):
    monkeypatch.setattr(market.yf, "Tickers", FakeTickers)

    result = market.get_multiple_quotes.fn(tickers="AAPL ZZZZ")

    assert result["quotes"]["AAPL"]["lastPrice"] == 190.0
    assert "error" in result["quotes"]["ZZZZ"]
