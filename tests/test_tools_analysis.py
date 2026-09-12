"""Unit tests for app.tools.analysis."""

from __future__ import annotations

import pandas as pd

from app.tools import analysis
from tests.conftest import FakeTicker


def test_get_recommendations(monkeypatch):
    df = pd.DataFrame({"period": ["0m"], "strongBuy": [10]})
    fake = FakeTicker(recommendations=df)
    monkeypatch.setattr(analysis, "get_ticker", lambda ticker: fake)

    result = analysis.get_recommendations.fn(ticker="AAPL")

    assert result["recommendations"][0]["strongBuy"] == 10


def test_get_recommendations_summary(monkeypatch):
    df = pd.DataFrame({"strongBuy": [5]})
    fake = FakeTicker(recommendations_summary=df)
    monkeypatch.setattr(analysis, "get_ticker", lambda ticker: fake)

    result = analysis.get_recommendations_summary.fn(ticker="AAPL")

    assert result["recommendations_summary"][0]["strongBuy"] == 5


def test_get_upgrades_downgrades(monkeypatch):
    idx = pd.to_datetime(["2024-01-01"])
    df = pd.DataFrame({"Firm": ["Morgan Stanley"], "ToGrade": ["Overweight"]}, index=idx)
    fake = FakeTicker(upgrades_downgrades=df)
    monkeypatch.setattr(analysis, "get_ticker", lambda ticker: fake)

    result = analysis.get_upgrades_downgrades.fn(ticker="AAPL")

    assert result["upgrades_downgrades"][0]["Firm"] == "Morgan Stanley"


def test_get_analyst_price_targets_dict_shaped_result(monkeypatch):
    fake = FakeTicker(analyst_price_targets={"current": 200.0, "mean": 210.0})
    monkeypatch.setattr(analysis, "get_ticker", lambda ticker: fake)

    result = analysis.get_analyst_price_targets.fn(ticker="AAPL")

    assert result["analyst_price_targets"]["mean"] == 210.0


def test_get_earnings_estimate(monkeypatch):
    df = pd.DataFrame({"avg": [1.5]}, index=["0q"])
    fake = FakeTicker(earnings_estimate=df)
    monkeypatch.setattr(analysis, "get_ticker", lambda ticker: fake)

    result = analysis.get_earnings_estimate.fn(ticker="AAPL")

    assert len(result["earnings_estimate"]) == 1


def test_get_revenue_estimate(monkeypatch):
    df = pd.DataFrame({"avg": [1_000_000]}, index=["0q"])
    fake = FakeTicker(revenue_estimate=df)
    monkeypatch.setattr(analysis, "get_ticker", lambda ticker: fake)

    result = analysis.get_revenue_estimate.fn(ticker="AAPL")

    assert len(result["revenue_estimate"]) == 1


def test_get_earnings_history(monkeypatch):
    df = pd.DataFrame({"epsActual": [1.2]})
    fake = FakeTicker(earnings_history=df)
    monkeypatch.setattr(analysis, "get_ticker", lambda ticker: fake)

    result = analysis.get_earnings_history.fn(ticker="AAPL")

    assert len(result["earnings_history"]) == 1


def test_get_eps_trend(monkeypatch):
    df = pd.DataFrame({"current": [1.5]}, index=["0q"])
    fake = FakeTicker(eps_trend=df)
    monkeypatch.setattr(analysis, "get_ticker", lambda ticker: fake)

    result = analysis.get_eps_trend.fn(ticker="AAPL")

    assert len(result["eps_trend"]) == 1


def test_get_eps_revisions(monkeypatch):
    df = pd.DataFrame({"upLast7days": [3]}, index=["0q"])
    fake = FakeTicker(eps_revisions=df)
    monkeypatch.setattr(analysis, "get_ticker", lambda ticker: fake)

    result = analysis.get_eps_revisions.fn(ticker="AAPL")

    assert len(result["eps_revisions"]) == 1


def test_get_growth_estimates(monkeypatch):
    df = pd.DataFrame({"stock": [0.1]}, index=["0q"])
    fake = FakeTicker(growth_estimates=df)
    monkeypatch.setattr(analysis, "get_ticker", lambda ticker: fake)

    result = analysis.get_growth_estimates.fn(ticker="AAPL")

    assert len(result["growth_estimates"]) == 1


def test_get_calendar_with_dict_result(monkeypatch):
    fake = FakeTicker(calendar={"Dividend Date": "2024-05-01"})
    monkeypatch.setattr(analysis, "get_ticker", lambda ticker: fake)

    result = analysis.get_calendar.fn(ticker="AAPL")

    assert result["calendar"]["Dividend Date"] == "2024-05-01"


def test_get_calendar_with_non_dict_result(monkeypatch):
    df = pd.DataFrame({"value": [1]})
    fake = FakeTicker(calendar=df)
    monkeypatch.setattr(analysis, "get_ticker", lambda ticker: fake)

    result = analysis.get_calendar.fn(ticker="AAPL")

    assert result["calendar"] == [{"date": 0, "value": 1}]


def test_get_earnings_dates(monkeypatch):
    idx = pd.to_datetime(["2024-01-25"])
    df = pd.DataFrame({"EPS Estimate": [1.5]}, index=idx)
    fake = FakeTicker(earnings_dates=df)
    monkeypatch.setattr(analysis, "get_ticker", lambda ticker: fake)

    result = analysis.get_earnings_dates.fn(ticker="AAPL", limit=5)

    assert result["earnings_dates"][0]["EPS Estimate"] == 1.5


def test_get_sustainability(monkeypatch):
    df = pd.DataFrame({"Value": [50]}, index=["totalEsg"])
    fake = FakeTicker(sustainability=df)
    monkeypatch.setattr(analysis, "get_ticker", lambda ticker: fake)

    result = analysis.get_sustainability.fn(ticker="AAPL")

    assert len(result["sustainability"]) == 1


def test_get_sec_filings(monkeypatch):
    fake = FakeTicker(sec_filings=[{"type": "10-K"}])
    monkeypatch.setattr(analysis, "get_ticker", lambda ticker: fake)

    result = analysis.get_sec_filings.fn(ticker="AAPL")

    assert result["sec_filings"] == [{"type": "10-K"}]


def test_get_news(monkeypatch):
    fake = FakeTicker(news=[{"title": "Apple releases new product"}])
    monkeypatch.setattr(analysis, "get_ticker", lambda ticker: fake)

    result = analysis.get_news.fn(ticker="AAPL")

    assert result["news"][0]["title"] == "Apple releases new product"
