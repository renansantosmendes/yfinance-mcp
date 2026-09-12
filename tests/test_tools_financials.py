"""Unit tests for app.tools.financials."""

from __future__ import annotations

import pandas as pd

from app.tools import financials
from tests.conftest import FakeTicker


def _stmt_df() -> pd.DataFrame:
    return pd.DataFrame({pd.Timestamp("2023-12-31"): [100.0]}, index=["TotalRevenue"])


def test_get_income_statement_annual_by_default(monkeypatch):
    fake = FakeTicker(income_stmt=_stmt_df())
    monkeypatch.setattr(financials, "get_ticker", lambda ticker: fake)

    result = financials.get_income_statement.fn(ticker="AAPL")

    assert result["quarterly"] is False
    assert len(result["income_statement"]) == 1


def test_get_income_statement_quarterly_flag_selects_quarterly_data(monkeypatch):
    fake = FakeTicker(quarterly_income_stmt=_stmt_df())
    monkeypatch.setattr(financials, "get_ticker", lambda ticker: fake)

    result = financials.get_income_statement.fn(ticker="AAPL", quarterly=True)

    assert result["quarterly"] is True
    assert len(result["income_statement"]) == 1


def test_get_balance_sheet(monkeypatch):
    fake = FakeTicker(balance_sheet=_stmt_df())
    monkeypatch.setattr(financials, "get_ticker", lambda ticker: fake)

    result = financials.get_balance_sheet.fn(ticker="AAPL")

    assert len(result["balance_sheet"]) == 1


def test_get_balance_sheet_quarterly(monkeypatch):
    fake = FakeTicker(quarterly_balance_sheet=_stmt_df())
    monkeypatch.setattr(financials, "get_ticker", lambda ticker: fake)

    result = financials.get_balance_sheet.fn(ticker="AAPL", quarterly=True)

    assert result["quarterly"] is True
    assert len(result["balance_sheet"]) == 1


def test_get_cashflow(monkeypatch):
    fake = FakeTicker(cashflow=_stmt_df())
    monkeypatch.setattr(financials, "get_ticker", lambda ticker: fake)

    result = financials.get_cashflow.fn(ticker="AAPL")

    assert len(result["cashflow"]) == 1


def test_get_cashflow_quarterly(monkeypatch):
    fake = FakeTicker(quarterly_cashflow=_stmt_df())
    monkeypatch.setattr(financials, "get_ticker", lambda ticker: fake)

    result = financials.get_cashflow.fn(ticker="AAPL", quarterly=True)

    assert len(result["cashflow"]) == 1
