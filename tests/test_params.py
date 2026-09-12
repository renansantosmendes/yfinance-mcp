"""Unit tests for app.utils.params."""

from __future__ import annotations

from app.utils.params import build_period_kwargs


def test_returns_period_when_no_start_or_end():
    assert build_period_kwargs("1mo", None, None) == {"period": "1mo"}


def test_start_switches_to_range_mode_and_drops_period():
    kwargs = build_period_kwargs("1mo", "2024-01-01", None)
    assert kwargs == {"start": "2024-01-01", "end": None}
    assert "period" not in kwargs


def test_end_alone_also_switches_to_range_mode():
    kwargs = build_period_kwargs("1mo", None, "2024-02-01")
    assert kwargs == {"start": None, "end": "2024-02-01"}
    assert "period" not in kwargs


def test_both_start_and_end_given():
    kwargs = build_period_kwargs("1y", "2024-01-01", "2024-02-01")
    assert kwargs == {"start": "2024-01-01", "end": "2024-02-01"}
