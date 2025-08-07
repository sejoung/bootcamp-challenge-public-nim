from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class MCPClient:
    def __init__(self,server_params: StdioServerParameters,inf_url="https://integrate.api.nvidia.com/v1"):
        self.server_params = server_params
        self.session = None
        self._client = None
    
    async def __aenter__(self):
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.__aexit__(exc_type, exc_val, exc_tb)
        if self._client:
            await self._client.__aexit__(exc_type, exc_val, exc_tb)

    async def connect(self):
        self._client = stdio_client(self.server_params)
        self.read,self.write = await self._client.__aenter__()
        session = ClientSession(self.read, self.write)
        self.session = await session.__aenter__()
        await self.session.initialize()

    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()
