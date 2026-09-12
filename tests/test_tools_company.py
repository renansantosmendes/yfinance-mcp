"""Unit tests for app.tools.company (includes the flagship get_company_info)."""

from __future__ import annotations

from app.tools import company
from tests.conftest import FakeTicker


def test_get_company_info_returns_ticker_and_cleaned_info(monkeypatch):
    fake = FakeTicker(info={"shortName": "Apple Inc.", "sector": "Technology", "marketCap": 4849207869440})
    monkeypatch.setattr(company, "get_ticker", lambda ticker: fake)

    result = company.get_company_info.fn(ticker="aapl")

    assert result["ticker"] == "AAPL"
    assert result["info"]["shortName"] == "Apple Inc."
    assert result["info"]["sector"] == "Technology"
    assert result["info"]["marketCap"] == 4849207869440


def test_get_company_info_handles_missing_info_gracefully(monkeypatch):
    fake = FakeTicker(info=None)
    monkeypatch.setattr(company, "get_ticker", lambda ticker: fake)

    result = company.get_company_info.fn(ticker="ZZZZ")

    assert result["ticker"] == "ZZZZ"
    assert result["info"] == {}


def test_get_fast_info_returns_snapshot(monkeypatch):
    fake = FakeTicker(fast_info={"lastPrice": 123.45, "currency": "USD"})
    monkeypatch.setattr(company, "get_ticker", lambda ticker: fake)

    result = company.get_fast_info.fn(ticker="AAPL")

    assert result["ticker"] == "AAPL"
    assert result["fast_info"]["lastPrice"] == 123.45


def test_get_fast_info_handles_none(monkeypatch):
    fake = FakeTicker(fast_info=None)
    monkeypatch.setattr(company, "get_ticker", lambda ticker: fake)

    result = company.get_fast_info.fn(ticker="AAPL")

    assert result["fast_info"] == {}


def test_get_isin_returns_value(monkeypatch):
    fake = FakeTicker(isin="US0378331005")
    monkeypatch.setattr(company, "get_ticker", lambda ticker: fake)

    result = company.get_isin.fn(ticker="AAPL")

    assert result["ticker"] == "AAPL"
    assert result["isin"] == "US0378331005"
