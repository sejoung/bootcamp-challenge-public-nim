import json
import asyncio
from mcp_http_client import MCPHTTPCLIENT

async def test_mcp_invoice_server(mcp_server_url):
    async with MCPHTTPCLIENT(mcp_server_url) as mcp_client:
        # Execute tool call
        tool_result = await mcp_client.session.call_tool("media_lookup", {"query":"tracks by James Brown"})
        output = tool_result.content[0].text
        print(output)

        tool_result = await mcp_client.session.call_tool("invoice_lookup", {
            "customer_first_name": "Madalena",
            "customer_last_name": "Sampaio",
            "customer_phone": "+351 (225) 022-448",
            "artist_name": "U2"
        })
        output = json.loads(tool_result.content[0].text)
        print(json.dumps(output,indent=4))

if __name__ == '__main__':
    asyncio.run(test_mcp_invoice_server("http://localhost:8000/mcp"))