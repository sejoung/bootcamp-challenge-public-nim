import os
import sys
import logging
import contextlib
from collections.abc import AsyncIterator
from typing import Any
import asyncio

from mcp.server import InitializationOptions
from mcp.server.lowlevel import Server, NotificationOptions
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from starlette.applications import Starlette
from starlette.routing import Mount
from starlette.types import Receive, Scope, Send
import uvicorn
import mcp.types as types


logger = logging.getLogger('simple-math')

def main():
    server = Server("simple-math")

    @server.list_tools()
    async def handle_list_tools() -> list[types.Tool]:
        """List available tools"""
        return [
            types.Tool(
                name="add",
                description="addition",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "a": {"type": "number", "description": "1st integer"},
                        "b": {"type": "number", "description": "2nd integer"}
                    },
                    "required": ["a","b"],
                },
            ),
            types.Tool(
                name="subtract",
                description="subtraction",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "a": {"type": "number", "description": "1st integer"},
                        "b": {"type": "number", "description": "2nd integer"}
                    },
                    "required": ["a","b"]
                },
            ),
        ]

    @server.call_tool()
    async def handle_call_tool(
        name: str, arguments: dict[str, Any] | None
    ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        """Handle tool execution requests"""
        try:
            if name == "add":
                if not arguments or "a" not in arguments or "b" not in arguments:
                    raise ValueError("Missing arguments a or b")
                results = arguments['a'] + arguments['b']
                return [types.TextContent(type="text", text=str(results))]

            elif name == "subtract":
                if not arguments or "a" not in arguments or "b" not in arguments:
                    raise ValueError("Missing arguments a or b")
                results = arguments['a'] - arguments['b']
                return [types.TextContent(type="text", text=str(results))]
            else:
                raise ValueError(f"Unknown tool: {name}")
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]

    # Create the session manager with true stateless mode
    session_manager = StreamableHTTPSessionManager(
        app=server,
        event_store=None,
        json_response=True,
        stateless=True,
    )

    async def handle_streamable_http(
        scope: Scope, receive: Receive, send: Send
    ) -> None:
        await session_manager.handle_request(scope, receive, send)

    @contextlib.asynccontextmanager
    async def lifespan(app: Starlette) -> AsyncIterator[None]:
        """Context manager for session manager."""
        async with session_manager.run():
            logger.info("Application started with StreamableHTTP session manager!")
            try:
                yield
            finally:
                logger.info("Application shutting down...")

    # Create an ASGI application using the transport
    starlette_app = Starlette(
        debug=True,
        routes=[
            Mount("/mcp", app=handle_streamable_http),
        ],
        lifespan=lifespan,
    )

    uvicorn.run(starlette_app, host="127.0.0.1")

asyncio.run(main())