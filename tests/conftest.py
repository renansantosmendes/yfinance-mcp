"""Shared pytest fixtures and test doubles.

None of these tests hit the real Yahoo Finance API: every tool test replaces
`get_ticker` (or the relevant `yfinance` module-level function/class) with a
fake, so the suite is fast, deterministic, and safe to run in CI without
network access or rate-limit concerns.
"""

from __future__ import annotations

import pandas as pd
import pytest

from app.utils.ticker_cache import _get_ticker_cached  # pylint: disable=protected-access


@pytest.fixture(autouse=True)
def clear_ticker_cache():
    """Reset the lru_cache backing get_ticker so fakes never leak between tests."""
    _get_ticker_cached.cache_clear()
    yield
    _get_ticker_cached.cache_clear()


class FakeTicker:  # pylint: disable=too-many-instance-attributes
    """Minimal stand-in for yfinance.Ticker exposing only what our tools read.

    Every field defaults to an "empty" value matching what yfinance itself
    returns when no data is available, so tests only need to set the
    attribute(s) relevant to the tool under test.
    """

    def __init__(self, **kwargs):
        self.info = kwargs.get("info", {})
        self.fast_info = kwargs.get("fast_info", {})
        self.isin = kwargs.get("isin", "US0000000000")
        self._history = kwargs.get("history", pd.DataFrame())
        self.dividends = kwargs.get("dividends", pd.Series(dtype=float))
        self.splits = kwargs.get("splits", pd.Series(dtype=float))
        self.capital_gains = kwargs.get("capital_gains", pd.Series(dtype=float))
        self.actions = kwargs.get("actions", pd.DataFrame())
        self._shares_full = kwargs.get("shares_full")
        self.income_stmt = kwargs.get("income_stmt", pd.DataFrame())
        self.quarterly_income_stmt = kwargs.get("quarterly_income_stmt", pd.DataFrame())
        self.balance_sheet = kwargs.get("balance_sheet", pd.DataFrame())
        self.quarterly_balance_sheet = kwargs.get("quarterly_balance_sheet", pd.DataFrame())
        self.cashflow = kwargs.get("cashflow", pd.DataFrame())
        self.quarterly_cashflow = kwargs.get("quarterly_cashflow", pd.DataFrame())
        self.major_holders = kwargs.get("major_holders", pd.DataFrame())
        self.institutional_holders = kwargs.get("institutional_holders", pd.DataFrame())
        self.mutualfund_holders = kwargs.get("mutualfund_holders", pd.DataFrame())
        self.insider_transactions = kwargs.get("insider_transactions", pd.DataFrame())
        self.insider_purchases = kwargs.get("insider_purchases", pd.DataFrame())
        self.insider_roster_holders = kwargs.get("insider_roster_holders", pd.DataFrame())
        self.recommendations = kwargs.get("recommendations", pd.DataFrame())
        self.recommendations_summary = kwargs.get("recommendations_summary", pd.DataFrame())
        self.upgrades_downgrades = kwargs.get("upgrades_downgrades", pd.DataFrame())
        self.analyst_price_targets = kwargs.get("analyst_price_targets", {})
        self.earnings_estimate = kwargs.get("earnings_estimate", pd.DataFrame())
        self.revenue_estimate = kwargs.get("revenue_estimate", pd.DataFrame())
        self.earnings_history = kwargs.get("earnings_history", pd.DataFrame())
        self.eps_trend = kwargs.get("eps_trend", pd.DataFrame())
        self.eps_revisions = kwargs.get("eps_revisions", pd.DataFrame())
        self.growth_estimates = kwargs.get("growth_estimates", pd.DataFrame())
        self.calendar = kwargs.get("calendar", {})
        self._earnings_dates = kwargs.get("earnings_dates", pd.DataFrame())
        self.sustainability = kwargs.get("sustainability", pd.DataFrame())
        self.sec_filings = kwargs.get("sec_filings", [])
        self.news = kwargs.get("news", [])
        self.options = kwargs.get("options", ())
        self._option_chain = kwargs.get("option_chain")

    def history(self, **_kwargs):
        """Stand in for Ticker.history()."""
        return self._history

    def get_shares_full(self, start=None, end=None):  # noqa: D401 - test double
        """Stand in for Ticker.get_shares_full()."""
        del start, end
        return self._shares_full

    def get_earnings_dates(self, limit=12):
        """Stand in for Ticker.get_earnings_dates()."""
        del limit
        return self._earnings_dates

    def option_chain(self, date):
        """Stand in for Ticker.option_chain()."""
        del date
        return self._option_chain
