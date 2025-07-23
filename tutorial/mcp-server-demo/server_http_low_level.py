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
    
    """
    handle_list_tools() returns the name, description and input schema of all available tools.
    we have defined 2 tools here, addition and subtraction that requires 2 arguments - a and b.
    similar to server_http.py, you can define the schema for additional methods like multiply and divide.
    """
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

    """
    handle_call_tool() takes in the name and arguments, performs computation and returns the result
    for the 'add' tool, we perform addition of a and b.
    for the 'subtract' tool, we perform subtraction of b from a.
    similar to server_http.py, you can define additional methods for multiply and divide
    """
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

    """
    Create the session manager with true stateless mode
    """
    session_manager = StreamableHTTPSessionManager(
        app=server,
        event_store=None,
        json_response=True,
        stateless=True,
    )

    """
    Method to handle incoming http requests
    """
    async def handle_streamable_http(
        scope: Scope, receive: Receive, send: Send
    ) -> None:
        await session_manager.handle_request(scope, receive, send)


    """
    Method to define actions on startup and shutdown
    """
    @contextlib.asynccontextmanager
    async def lifespan(app: Starlette) -> AsyncIterator[None]:
        """Context manager for session manager."""
        async with session_manager.run():
            logger.info("Application started with StreamableHTTP session manager!")
            try:
                yield
            finally:
                logger.info("Application shutting down...")

    """
    Create ASGI application with /mcp as endpoint to mcp server
    """
    starlette_app = Starlette(
        debug=True,
        routes=[
            Mount("/mcp", app=handle_streamable_http),
        ],
        lifespan=lifespan,
    )

    """
    Initialise starlette web application
    """
    uvicorn.run(starlette_app, host="127.0.0.1")

asyncio.run(main())