"""Unit tests for app.tools.price."""

from __future__ import annotations

import pandas as pd

from app.tools import price
from tests.conftest import FakeTicker


def _history_df() -> pd.DataFrame:
    idx = pd.to_datetime(["2024-01-01", "2024-01-02"])
    return pd.DataFrame({"Open": [1.0, 2.0], "Close": [1.5, 2.5]}, index=idx)


def test_get_history_returns_rows(monkeypatch):
    fake = FakeTicker(history=_history_df())
    monkeypatch.setattr(price, "get_ticker", lambda ticker: fake)

    result = price.get_history.fn(ticker="AAPL", period="5d")

    assert result["ticker"] == "AAPL"
    assert len(result["rows"]) == 2
    assert result["rows"][0]["Close"] == 1.5


def test_get_dividends_empty_series(monkeypatch):
    fake = FakeTicker(dividends=pd.Series(dtype=float))
    monkeypatch.setattr(price, "get_ticker", lambda ticker: fake)

    result = price.get_dividends.fn(ticker="AAPL")

    assert result["dividends"] == []


def test_get_dividends_with_data(monkeypatch):
    idx = pd.to_datetime(["2024-02-09"])
    fake = FakeTicker(dividends=pd.Series([0.24], index=idx))
    monkeypatch.setattr(price, "get_ticker", lambda ticker: fake)

    result = price.get_dividends.fn(ticker="AAPL")

    assert result["dividends"][0]["dividend"] == 0.24
    assert result["dividends"][0]["date"] == idx[0].isoformat()


def test_get_splits(monkeypatch):
    idx = pd.to_datetime(["2020-08-31"])
    fake = FakeTicker(splits=pd.Series([4.0], index=idx))
    monkeypatch.setattr(price, "get_ticker", lambda ticker: fake)

    result = price.get_splits.fn(ticker="AAPL")

    assert result["splits"][0]["split_ratio"] == 4.0


def test_get_capital_gains(monkeypatch):
    idx = pd.to_datetime(["2023-12-01"])
    fake = FakeTicker(capital_gains=pd.Series([1.1], index=idx))
    monkeypatch.setattr(price, "get_ticker", lambda ticker: fake)

    result = price.get_capital_gains.fn(ticker="VFIAX")

    assert result["capital_gains"][0]["capital_gain"] == 1.1


def test_get_actions(monkeypatch):
    fake = FakeTicker(actions=_history_df())
    monkeypatch.setattr(price, "get_ticker", lambda ticker: fake)

    result = price.get_actions.fn(ticker="AAPL")

    assert len(result["actions"]) == 2


def test_get_shares_outstanding_with_date_range(monkeypatch):
    idx = pd.to_datetime(["2024-01-01"])
    fake = FakeTicker(shares_full=pd.Series([1000.0], index=idx))
    monkeypatch.setattr(price, "get_ticker", lambda ticker: fake)

    result = price.get_shares_outstanding.fn(ticker="AAPL", start="2024-01-01", end="2024-01-02")

    assert result["shares"][0]["shares_outstanding"] == 1000.0


def test_get_shares_outstanding_no_data_in_range_returns_empty_list(monkeypatch):
    fake = FakeTicker(shares_full=None)
    monkeypatch.setattr(price, "get_ticker", lambda ticker: fake)

    result = price.get_shares_outstanding.fn(ticker="AAPL", start="2024-01-01")

    assert result["shares"] == []


def test_get_shares_outstanding_falls_back_to_info_fields(monkeypatch):
    fake = FakeTicker(info={"sharesOutstanding": 900, "floatShares": 800, "impliedSharesOutstanding": 950})
    monkeypatch.setattr(price, "get_ticker", lambda ticker: fake)

    result = price.get_shares_outstanding.fn(ticker="AAPL")

    assert result["shares_outstanding"] == 900
    assert result["float_shares"] == 800
    assert result["implied_shares_outstanding"] == 950
