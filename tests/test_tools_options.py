"""Unit tests for app.tools.options."""

from __future__ import annotations

from collections import namedtuple

import pandas as pd

from app.tools import options
from tests.conftest import FakeTicker

Chain = namedtuple("Chain", ["calls", "puts"])


def test_get_options_expirations(monkeypatch):
    fake = FakeTicker(options=("2024-06-21", "2024-07-19"))
    monkeypatch.setattr(options, "get_ticker", lambda ticker: fake)

    result = options.get_options_expirations.fn(ticker="AAPL")

    assert result["expirations"] == ["2024-06-21", "2024-07-19"]


def test_get_option_chain_defaults_to_nearest_expiration(monkeypatch):
    calls = pd.DataFrame({"strike": [150.0]})
    puts = pd.DataFrame({"strike": [140.0]})
    fake = FakeTicker(options=("2024-06-21", "2024-07-19"), option_chain=Chain(calls=calls, puts=puts))
    monkeypatch.setattr(options, "get_ticker", lambda ticker: fake)

    result = options.get_option_chain.fn(ticker="AAPL")

    assert result["expiration_date"] == "2024-06-21"
    assert result["calls"][0]["strike"] == 150.0
    assert result["puts"][0]["strike"] == 140.0


def test_get_option_chain_with_explicit_expiration(monkeypatch):
    calls = pd.DataFrame({"strike": [150.0]})
    puts = pd.DataFrame({"strike": [140.0]})
    fake = FakeTicker(options=("2024-06-21", "2024-07-19"), option_chain=Chain(calls=calls, puts=puts))
    monkeypatch.setattr(options, "get_ticker", lambda ticker: fake)

    result = options.get_option_chain.fn(ticker="AAPL", expiration_date="2024-07-19")

    assert result["expiration_date"] == "2024-07-19"


def test_get_option_chain_no_options_available(monkeypatch):
    fake = FakeTicker(options=())
    monkeypatch.setattr(options, "get_ticker", lambda ticker: fake)

    result = options.get_option_chain.fn(ticker="AAPL")

    assert "error" in result


def test_get_option_chain_rejects_invalid_expiration(monkeypatch):
    fake = FakeTicker(options=("2024-06-21",))
    monkeypatch.setattr(options, "get_ticker", lambda ticker: fake)

    result = options.get_option_chain.fn(ticker="AAPL", expiration_date="2099-01-01")

    assert "error" in result
    assert result["available_expirations"] == ["2024-06-21"]
