import asyncio
from typing import Optional
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

import asyncio

class MCPClient:
    def __init__(self):
        # Initialize session and client objects
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()

    """
    Connect to the MCP Server using the context library from python
    The context library simplifies the creation and usage of context managers, 
    which are objects that define methods for setting up and tearing down resources, 
    ensuring proper cleanup even if exceptions occur. 
    """
    async def connect_to_server(self, server_script_path: str):
        server_params = StdioServerParameters(
            command="uv",
            args=[
                "run",
                server_script_path
            ]
        )

        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))
        await self.session.initialize()
    
    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()
