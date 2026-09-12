"""Tests for the FastAPI app shell (non-MCP routes)."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root_returns_service_info():
    resp = client.get("/")
    assert resp.status_code == 200
    body = resp.json()
    assert body["name"] == "yfinance-mcp"
    assert body["mcp_endpoint"] == "/mcp"
    assert body["docs"] == "/docs"


def test_health_returns_healthy():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "healthy"}


def test_docs_page_is_served():
    resp = client.get("/docs")
    assert resp.status_code == 200
