import asyncio
import logging
from typing import Any

import mcp.types as types
from mcp.server import InitializationOptions
from mcp.server.lowlevel import Server, NotificationOptions
from mcp.server.stdio import stdio_server

logger = logging.getLogger('simple-math')


async def main():
    server = Server("simple-math")

    """
    handle_list_tools() returns the name, description and input schema of all available tools.
    we have defined 2 tools here, addition and subtraction that requires 2 arguments - a and b.
    similar to server.py, you can define the schema for additional methods like multiply and divide.
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
                    "required": ["a", "b"],
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
                    "required": ["a", "b"]
                },
            ),
        ]

    """
    handle_call_tool() takes in the name and arguments, performs computation and returns the result
    for the 'add' tool, we perform addition of a and b.
    for the 'subtract' tool, we perform subtraction of b from a.
    similar to server.py, you can define additional methods for multiply and divide
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
    Initialize stdio server with read and write stream to receive and send data
    """
    async with stdio_server() as (read_stream, write_stream):
        logger.info("Server running with stdio transport")
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="simple-math",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


# the main() method is asynchronous and hence needs to be wrapped in asyncio
asyncio.run(main())
