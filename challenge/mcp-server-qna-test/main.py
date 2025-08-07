import json
import asyncio
from mcp_client import MCPClient
from mcp import StdioServerParameters

async def test_mcp_qna_server(mcp_server_path):
    server_params = StdioServerParameters(
        command="uv",
        args=[
            "--directory",
            mcp_server_path,
            "run",
            "mcp-server-qna",
            "--db-path",
            "data/chinook.db"
        ],
        env=None
    )
    
    async with MCPClient(server_params) as mcp_client:
        # Execute tool call
        tool_result = await mcp_client.session.call_tool("lookup_track",{"track_name":"For Those About To Rock (We Salute You)"})
        output = json.loads(tool_result.content[0].text)
        print(output)

if __name__ == '__main__':
    asyncio.run(test_mcp_qna_server("../mcp-servers/qna"))
    
    
    