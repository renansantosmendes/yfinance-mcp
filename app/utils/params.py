"""Shared helpers for building yfinance call kwargs from tool parameters."""

from __future__ import annotations

from typing import Optional


def build_period_kwargs(period: str, start: Optional[str], end: Optional[str]) -> dict:
    """Build the period/start/end kwargs for a yfinance history-style call.

    If either `start` or `end` is provided, they take precedence and `period`
    is omitted (matching yfinance's own precedence rule); otherwise `period`
    is used on its own.
    """
    if start or end:
        return {"start": start, "end": end}
    return {"period": period}
