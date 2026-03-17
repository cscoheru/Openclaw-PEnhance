#!/usr/bin/env python3
"""
PEnhance Proxy - Programming Enhancement Proxy for Claude Code

A local HTTP proxy that intercepts Claude Code requests and enhances them
before forwarding to GLM-4.7/5 API.

Usage:
    python penhance_proxy.py

Environment Variables:
    GLM_API_URL: GLM API endpoint (default: https://open.bigmodel.cn/api/anthropic/v1)
    GLM_API_KEY: GLM API key
    PROXY_PORT: Port to listen on (default: 8080)
    ENABLE_OPENCLAW: Enable OpenClaw enhancement (default: false)
"""

import asyncio
import json
import logging
import time
import sys
from pathlib import Path
from typing import Dict, Any, Optional

import httpx
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import StreamingResponse
import uvicorn

# Setup path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import (
    PROXY_HOST,
    PROXY_PORT,
    GLM_API_URL,
    GLM_API_KEY,
    GLM_TIMEOUT,
    LOG_FILE,
    LOG_LEVEL,
    ENABLE_OPENCLAW,
    FALLBACK_ON_ERROR,
)
from enhancer import Enhancer, detect_request_type, detect_language

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="PEnhance Proxy",
    description="Programming Enhancement Proxy for Claude Code",
    version="1.0.0",
)

# Create enhancer instance
enhancer = Enhancer()

# HTTP client for forwarding requests
http_client: Optional[httpx.AsyncClient] = None


@app.on_event("startup")
async def startup_event():
    """Initialize HTTP client on startup."""
    global http_client
    http_client = httpx.AsyncClient(
        timeout=httpx.Timeout(GLM_TIMEOUT),
        follow_redirects=True,
    )
    logger.info(f"PEnhance Proxy starting on http://{PROXY_HOST}:{PROXY_PORT}")
    logger.info(f"Target API: {GLM_API_URL}")
    logger.info(f"OpenClaw enhancement: {'enabled' if ENABLE_OPENCLAW else 'disabled'}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    global http_client
    if http_client:
        await http_client.aclose()
    logger.info("PEnhance Proxy shutting down")


async def forward_to_glm(
    request_body: Dict[str, Any],
    headers: Dict[str, str]
) -> Response:
    """Forward enhanced request to GLM API."""
    # Prepare headers for GLM
    glm_headers = {
        "Content-Type": "application/json",
        "x-api-key": GLM_API_KEY,
        "anthropic-version": headers.get("anthropic-version", "2023-06-01"),
    }

    # Forward request
    try:
        response = await http_client.post(
            f"{GLM_API_URL}/messages",
            headers=glm_headers,
            json=request_body,
        )

        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers),
        )

    except httpx.TimeoutException:
        logger.error("Request to GLM timed out")
        raise HTTPException(status_code=504, detail="GLM API timeout")
    except httpx.RequestError as e:
        logger.error(f"Request to GLM failed: {e}")
        if FALLBACK_ON_ERROR:
            raise HTTPException(status_code=502, detail=f"GLM API error: {str(e)}")
        raise


async def stream_to_glm(
    request_body: Dict[str, Any],
    headers: Dict[str, str]
):
    """Stream response from GLM API."""
    glm_headers = {
        "Content-Type": "application/json",
        "x-api-key": GLM_API_KEY,
        "anthropic-version": headers.get("anthropic-version", "2023-06-01"),
    }

    request_body["stream"] = True

    async with http_client.stream(
        "POST",
        f"{GLM_API_URL}/messages",
        headers=glm_headers,
        json=request_body,
    ) as response:
        async for chunk in response.aiter_bytes():
            yield chunk


@app.post("/v1/messages")
async def proxy_messages(request: Request):
    """
    Main proxy endpoint for Anthropic Messages API.

    This intercepts Claude Code requests, enhances them, and forwards to GLM.
    """
    start_time = time.time()

    try:
        # Parse request body
        body = await request.json()
        headers = dict(request.headers)

        logger.info(f"Received request: model={body.get('model', 'unknown')}")
        logger.debug(f"Request body keys: {list(body.keys())}")

        # Enhance the request
        enhanced_body = await enhancer.enhance(body)

        # Log enhancement stats
        request_type = detect_request_type(enhanced_body.get("messages", []))
        language = detect_language(enhanced_body.get("messages", []))
        logger.info(f"Enhanced: type={request_type}, lang={language}")

        # Check if streaming is requested
        stream = body.get("stream", False)

        if stream:
            # Stream response
            return StreamingResponse(
                stream_to_glm(enhanced_body, headers),
                media_type="text/event-stream",
            )
        else:
            # Regular response
            response = await forward_to_glm(enhanced_body, headers)

            elapsed = time.time() - start_time
            logger.info(f"Request completed in {elapsed:.2f}s")

            return response

    except json.JSONDecodeError:
        logger.error("Invalid JSON in request body")
        raise HTTPException(status_code=400, detail="Invalid JSON")
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/v1/messages")
async def messages_get():
    """Handle GET requests (not supported)."""
    raise HTTPException(status_code=405, detail="Method not allowed")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    stats = enhancer.get_stats()
    return {
        "status": "healthy",
        "proxy": "PEnhance",
        "version": "1.0.0",
        "target": GLM_API_URL,
        "openclaw_enabled": ENABLE_OPENCLAW,
        "stats": stats,
    }


@app.get("/stats")
async def get_stats():
    """Get enhancement statistics."""
    return enhancer.get_stats()


@app.post("/v1/complete")
async def proxy_complete(request: Request):
    """Proxy for legacy complete endpoint (if needed)."""
    # Just forward without enhancement
    body = await request.json()
    headers = dict(request.headers)

    glm_headers = {
        "Content-Type": "application/json",
        "x-api-key": GLM_API_KEY,
    }

    response = await http_client.post(
        f"{GLM_API_URL}/complete",
        headers=glm_headers,
        json=body,
    )

    return Response(
        content=response.content,
        status_code=response.status_code,
        headers=dict(response.headers),
    )


# Catch-all for other endpoints
@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def catch_all(path: str, request: Request):
    """Catch-all for unmapped endpoints."""
    logger.warning(f"Unmapped endpoint: {path}")
    raise HTTPException(
        status_code=404,
        detail=f"Endpoint not found: {path}. PEnhance Proxy only supports /v1/messages"
    )


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="PEnhance Proxy")
    parser.add_argument(
        "--port",
        type=int,
        default=PROXY_PORT,
        help=f"Port to listen on (default: {PROXY_PORT})"
    )
    parser.add_argument(
        "--host",
        type=str,
        default=PROXY_HOST,
        help=f"Host to bind to (default: {PROXY_HOST})"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )

    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    print(f"""
╔═══════════════════════════════════════════════════════════════╗
║                    PEnhance Proxy v1.0.0                      ║
║                                                               ║
║  A Programming Enhancement Proxy for Claude Code              ║
║                                                               ║
║  Listening: http://{args.host}:{args.port}                            ║
║  Target API: {GLM_API_URL[:40]}...
║  OpenClaw: {'enabled' if ENABLE_OPENCLAW else 'disabled'}
║                                                               ║
║  Endpoints:                                                   ║
║    POST /v1/messages  - Main API proxy                       ║
║    GET  /health       - Health check                         ║
║    GET  /stats        - Enhancement statistics               ║
╚═══════════════════════════════════════════════════════════════╝
    """)

    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
        log_level="info",
    )


if __name__ == "__main__":
    main()
