import asyncio
from typing import Optional
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.streamable_http import streamablehttp_client

import asyncio

class MCPClient:
    def __init__(self):
        # Initialize session and client objects
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()

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
    
    async def connect_to_server_http(self, url: str):
        streamablehttp_transport = await self.exit_stack.enter_async_context(streamablehttp_client(url))
        self.read, self.write, _ = streamablehttp_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.read, self.write))
        await self.session.initialize()

    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()

async def main(path_to_server_file):
    mcp_client = MCPClient()
    await mcp_client.connect_to_server(path_to_server_file)
    res_tools = await mcp_client.session.list_tools()
    tools = res_tools.tools
    print("\nConnected to server with tools:", [tool.name for tool in tools])

    print("\nCalling add tool with a=2,b=3")
    res_add = await mcp_client.session.call_tool('add',{'a':2,'b':3})
    print(f"\nResult from add tool: {res_add.content[0].text} ")

    print("\nCalling subtract tool with a=7,b=4")
    res_add = await mcp_client.session.call_tool('subtract',{'a':7,'b':4})
    print(f"\nResult from subtract tool: {res_add.content[0].text} ")
    await mcp_client.cleanup()

async def main_http(url):
    mcp_client = MCPClient()
    await mcp_client.connect_to_server_http(url)
    res_tools = await mcp_client.session.list_tools()
    tools = res_tools.tools
    print("\nConnected to server with tools:", [tool.name for tool in tools])

    print("\nCalling add tool with a=2,b=3")
    res_add = await mcp_client.session.call_tool('add',{'a':2,'b':3})
    print(f"\nResult from add tool: {res_add.content[0].text} ")

    print("\nCalling subtract tool with a=7,b=4")
    res_add = await mcp_client.session.call_tool('subtract',{'a':7,'b':4})
    print(f"\nResult from subtract tool: {res_add.content[0].text} ")
    await mcp_client.cleanup()

if __name__ == '__main__':
    # stdio high level sdk
    asyncio.run(main('./tutorial/mcp-server-demo/server.py'))

    # stdio low level sdk
    # asyncio.run(main('./tutorial/mcp-server-demo/server_low_level.py'))

    # streamable http low/high level sdk
    # asyncio.run(main_http("http://localhost:8000/mcp"))
