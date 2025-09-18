from contextlib import AsyncExitStack

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


class MCPHTTPCLIENT:
    def __init__(self, url):
        ## TODO
        ## initialize any required class variables
        self.exit_stack = AsyncExitStack()
        self.session = None
        self._client = None
        self.url = url

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.__aexit__(exc_type, exc_val, exc_tb)
        if self._client:
            await self._client.__aexit__(exc_type, exc_val, exc_tb)

    async def connect(self):
        self._client = streamablehttp_client(self.url)
        self._receive, self._send, self._transport = await self._client.__aenter__()
        session = ClientSession(self._receive, self._send)
        self.session = await session.__aenter__()
        await self.session.initialize()

    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()
