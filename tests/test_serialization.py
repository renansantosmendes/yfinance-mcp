"""Unit tests for app.utils.serialization."""

from __future__ import annotations

import numpy as np
import pandas as pd

from app.utils.serialization import (
    clean_any,
    clean_dict,
    dataframe_to_records,
    export_any,
    series_to_dict,
)


def test_clean_any_handles_numpy_scalars():
    assert clean_any(np.int64(5)) == 5
    assert clean_any(np.float64(2.5)) == 2.5
    assert clean_any(np.bool_(True)) is True


def test_clean_any_handles_nan_and_nat():
    assert clean_any(float("nan")) is None
    assert clean_any(np.nan) is None
    assert clean_any(pd.NaT) is None


def test_clean_any_handles_timedelta():
    assert clean_any(pd.Timedelta(days=1)) == "1 days 00:00:00"


def test_clean_any_handles_timestamp_and_ndarray():
    ts = pd.Timestamp("2024-01-15T00:00:00")
    assert clean_any(ts) == ts.isoformat()
    assert clean_any(np.array([1, 2, 3])) == [1, 2, 3]


def test_clean_any_passes_through_plain_values():
    assert clean_any("plain string") == "plain string"
    assert clean_any(42) == 42
    assert clean_any(None) is None


def test_clean_any_recurses_into_nested_structures():
    data = {"a": np.float64(1.5), "b": {"c": np.int64(3)}, "d": [np.int64(1), np.int64(2)]}
    assert clean_any(data) == {"a": 1.5, "b": {"c": 3}, "d": [1, 2]}


def test_clean_any_converts_dataframe_and_series():
    # DataFrames go through dataframe_to_records(), which by default renames
    # an unnamed index column to "date" (the common case for our tools).
    df = pd.DataFrame({"x": [1, 2]})
    assert clean_any(df) == [{"date": 0, "x": 1}, {"date": 1, "x": 2}]

    s = pd.Series({"a": 1, "b": 2})
    assert clean_any(s) == {"a": 1, "b": 2}


def test_clean_dict_empty_and_none():
    assert clean_dict(None) == {}
    assert clean_dict({}) == {}


def test_dataframe_to_records_empty_and_none():
    assert dataframe_to_records(None) == []
    assert dataframe_to_records(pd.DataFrame()) == []
    assert dataframe_to_records("not a dataframe") == []


def test_dataframe_to_records_resets_datetime_index_as_named_column():
    idx = pd.to_datetime(["2024-01-01", "2024-01-02"])
    df = pd.DataFrame({"Close": [1.0, 2.0]}, index=idx)

    records = dataframe_to_records(df, index_name="date")

    assert records[0] == {"date": idx[0].isoformat(), "Close": 1.0}
    assert records[1] == {"date": idx[1].isoformat(), "Close": 2.0}


def test_dataframe_to_records_without_resetting_index():
    df = pd.DataFrame({"x": [1, 2]}, index=["a", "b"])

    records = dataframe_to_records(df, reset_index=False)

    assert records == [{"x": 1}, {"x": 2}]


def test_dataframe_to_records_drop_index_discards_meaningless_index():
    df = pd.DataFrame({"Holder": ["Vanguard"], "pctHeld": [0.1]})

    records = dataframe_to_records(df, drop_index=True)

    assert records == [{"Holder": "Vanguard", "pctHeld": 0.1}]


def test_dataframe_to_records_cleans_nan_values():
    df = pd.DataFrame({"value": [1.0, float("nan")]})

    records = dataframe_to_records(df, drop_index=True)

    assert records == [{"value": 1.0}, {"value": None}]


def test_series_to_dict_empty_and_none():
    assert series_to_dict(None) == {}
    assert series_to_dict(pd.Series(dtype=float)) == {}


def test_series_to_dict_converts_values():
    s = pd.Series({"a": np.float64(1.1), "b": np.nan})
    assert series_to_dict(s) == {"a": 1.1, "b": None}


def test_export_any_dispatches_by_runtime_type():
    assert export_any(None) is None
    assert export_any(pd.DataFrame()) == []
    assert export_any(pd.Series(dtype=float)) == {}
    assert export_any({"a": np.int64(1)}) == {"a": 1}
    assert export_any([np.int64(1), np.int64(2)]) == [1, 2]
    assert export_any("plain") == "plain"


def test_export_any_handles_dict_with_dataframe_value():
    df = pd.DataFrame({"x": [1]})
    result = export_any({"table": df})
    assert result == {"table": [{"date": 0, "x": 1}]}
