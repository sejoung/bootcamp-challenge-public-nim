import os
import sys
import logging
from contextlib import closing
from pathlib import Path
from pydantic import AnyUrl
from typing import Any
import asyncio

from mcp.server import InitializationOptions
from mcp.server.lowlevel import Server, NotificationOptions
from mcp.server.stdio import stdio_server
import mcp.types as types


logger = logging.getLogger('simple-math')

async def main():
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

    async with stdio_server() as (read_stream, write_stream):
        logger.info("Server running with stdio transport")
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="sqlite",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

asyncio.run(main())