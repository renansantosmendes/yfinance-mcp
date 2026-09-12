"""FastAPI application that exposes the yfinance FastMCP server over HTTP.

The MCP server is mounted as a sub-ASGI-app at /mcp using FastMCP's
streamable-HTTP transport in stateless mode, which is a good fit for
serverless platforms like Vercel (no in-memory session affinity required
between requests).
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.mcp_server import mcp

# Stateless HTTP: every request is self-contained, no server-side session
# state is required between calls — required for a serverless deployment
# where consecutive requests may hit different function instances.
mcp_app = mcp.http_app(path="/mcp", stateless_http=True)

app = FastAPI(
    title="yfinance MCP Server",
    description=(
        "MCP (Model Context Protocol) server exposing Yahoo Finance data "
        "through the yfinance library, built with FastAPI + FastMCP."
    ),
    version="1.0.0",
    lifespan=mcp_app.lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["meta"])
async def root() -> dict:
    """Basic service info and pointers to the MCP endpoint and docs."""
    return {
        "name": "yfinance-mcp",
        "status": "ok",
        "mcp_endpoint": "/mcp",
        "transport": "streamable-http",
        "docs": "/docs",
    }


@app.get("/health", tags=["meta"])
async def health() -> dict:
    """Liveness probe used by uptime checks and the Vercel deployment."""
    return {"status": "healthy"}


# Mounted last so the explicit routes above ("/", "/health", "/docs", ...)
# are matched first; everything else (notably "/mcp") is delegated to the
# MCP ASGI app.
app.mount("/", mcp_app)
