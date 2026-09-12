"""Unit tests for app.tools.holders."""

from __future__ import annotations

import pandas as pd

from app.tools import holders
from tests.conftest import FakeTicker


def test_get_major_holders(monkeypatch):
    df = pd.DataFrame({"Value": [0.1, 0.6]}, index=["insidersPercentHeld", "institutionsPercentHeld"])
    fake = FakeTicker(major_holders=df)
    monkeypatch.setattr(holders, "get_ticker", lambda ticker: fake)

    result = holders.get_major_holders.fn(ticker="AAPL")

    assert len(result["major_holders"]) == 2


def test_get_institutional_holders(monkeypatch):
    df = pd.DataFrame({"Holder": ["Vanguard"], "pctHeld": [0.08]})
    fake = FakeTicker(institutional_holders=df)
    monkeypatch.setattr(holders, "get_ticker", lambda ticker: fake)

    result = holders.get_institutional_holders.fn(ticker="AAPL")

    assert result["institutional_holders"][0]["Holder"] == "Vanguard"


def test_get_mutualfund_holders_empty(monkeypatch):
    fake = FakeTicker(mutualfund_holders=pd.DataFrame())
    monkeypatch.setattr(holders, "get_ticker", lambda ticker: fake)

    result = holders.get_mutualfund_holders.fn(ticker="AAPL")

    assert result["mutualfund_holders"] == []


def test_get_insider_transactions(monkeypatch):
    df = pd.DataFrame({"Insider": ["Tim Cook"], "Shares": [1000]})
    fake = FakeTicker(insider_transactions=df)
    monkeypatch.setattr(holders, "get_ticker", lambda ticker: fake)

    result = holders.get_insider_transactions.fn(ticker="AAPL")

    assert result["insider_transactions"][0]["Insider"] == "Tim Cook"


def test_get_insider_purchases(monkeypatch):
    df = pd.DataFrame({"Header": ["Purchases"], "Shares": [500]})
    fake = FakeTicker(insider_purchases=df)
    monkeypatch.setattr(holders, "get_ticker", lambda ticker: fake)

    result = holders.get_insider_purchases.fn(ticker="AAPL")

    assert len(result["insider_purchases"]) == 1


def test_get_insider_roster_holders(monkeypatch):
    df = pd.DataFrame({"Name": ["Tim Cook"], "Position": ["CEO"]})
    fake = FakeTicker(insider_roster_holders=df)
    monkeypatch.setattr(holders, "get_ticker", lambda ticker: fake)

    result = holders.get_insider_roster_holders.fn(ticker="AAPL")

    assert result["insider_roster_holders"][0]["Position"] == "CEO"
