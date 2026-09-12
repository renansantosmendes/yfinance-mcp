"""Helpers to convert pandas/numpy objects returned by yfinance into
plain JSON-serializable Python structures (dict/list/str/int/float/bool/None).

yfinance's return types have shifted across versions (some fields moved from
DataFrame to plain dict/list, or vice-versa). ``export_any`` inspects the
runtime type of the value and converts it appropriately, so tools stay robust
even if the underlying library's return type changes.
"""

from __future__ import annotations

import math
from typing import Any, Optional

import numpy as np
import pandas as pd


def _clean_scalar(value: Any) -> Any:  # pylint: disable=too-many-return-statements
    """Convert a single pandas/numpy scalar into a plain JSON-safe value.

    Dispatches by runtime type (Timestamp, numpy int/float/bool, NaN, ndarray)
    since pandas/numpy scalars are not natively JSON-serializable.
    """
    if value is None:
        return None
    if value is pd.NaT:
        return None
    if isinstance(value, (pd.Timestamp, np.datetime64)):
        ts = pd.Timestamp(value)
        return None if pd.isna(ts) else ts.isoformat()
    if isinstance(value, pd.Timedelta):
        return str(value)
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        f = float(value)
        return None if math.isnan(f) else f
    if isinstance(value, np.bool_):
        return bool(value)
    if isinstance(value, float) and math.isnan(value):
        return None
    if isinstance(value, np.ndarray):
        return [_clean_scalar(v) for v in value.tolist()]
    return value


def clean_any(value: Any) -> Any:
    """Recursively clean a scalar/dict/list value for JSON serialization."""
    if isinstance(value, dict):
        return {str(_clean_scalar(k)): clean_any(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [clean_any(v) for v in value]
    if isinstance(value, pd.DataFrame):
        return dataframe_to_records(value)
    if isinstance(value, pd.Series):
        return series_to_dict(value)
    return _clean_scalar(value)


def clean_dict(data: Optional[dict]) -> dict:
    """Clean every key/value pair of a flat dict for JSON serialization."""
    if not data:
        return {}
    return {str(_clean_scalar(k)): clean_any(v) for k, v in data.items()}


def dataframe_to_records(
    df: Optional[pd.DataFrame],
    reset_index: bool = True,
    index_name: str = "date",
    drop_index: bool = False,
) -> list:
    """Convert a DataFrame into a list of row dicts.

    Args:
        df: source DataFrame (may be None or empty).
        reset_index: whether to bring the index in as a column.
        index_name: name to give the former-index column.
        drop_index: if True, the index is discarded instead of becoming a column
            (useful for DataFrames whose index is meaningless, e.g. 0..N).
    """
    if df is None or not isinstance(df, pd.DataFrame) or df.empty:
        return []
    if drop_index:
        frame = df.reset_index(drop=True)
    elif reset_index:
        frame = df.reset_index()
        first_col = frame.columns[0]
        if first_col != index_name and (isinstance(first_col, str) and first_col.lower() in ("index",)):
            frame = frame.rename(columns={first_col: index_name})
        elif first_col not in df.columns:
            frame = frame.rename(columns={first_col: index_name})
    else:
        frame = df.copy()

    frame.columns = [str(c) for c in frame.columns]
    records = frame.to_dict(orient="records")
    return [clean_any(r) for r in records]


def series_to_dict(series: Optional[pd.Series]) -> dict:
    """Convert a pandas Series into a plain {index: value} dict."""
    if series is None or not isinstance(series, pd.Series) or series.empty:
        return {}
    return {str(_clean_scalar(k)): clean_any(v) for k, v in series.to_dict().items()}


def export_any(value: Any) -> Any:
    """Best-effort conversion of any yfinance return value into JSON-safe data."""
    if value is None:
        return None
    if isinstance(value, pd.DataFrame):
        return dataframe_to_records(value)
    if isinstance(value, pd.Series):
        return series_to_dict(value)
    if isinstance(value, dict):
        return clean_dict(value)
    if isinstance(value, (list, tuple, set)):
        return [export_any(v) for v in value]
    return clean_any(value)
