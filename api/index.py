"""Vercel serverless entrypoint.

Vercel's Python runtime auto-detects an ASGI application exposed as a
module-level `app` variable in a file under `api/`. This file just imports
the real FastAPI app built in `app.main`.
"""

from __future__ import annotations

import os
import sys

# Ensure the project root (parent of this `api/` directory) is importable,
# so `import app` resolves to the `app/` package at the repo root.
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

# pylint: disable=wrong-import-position,unused-import
from app.main import app

__all__ = ["app"]
