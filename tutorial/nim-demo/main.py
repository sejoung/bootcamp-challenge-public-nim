from openai import AsyncOpenAI
import os
import asyncio
from client import MCPClient
import json

async def main(path_to_server_file):
    openai_client = AsyncOpenAI(
        base_url = "https://integrate.api.nvidia.com/v1",
        api_key = os.environ["NVIDIA_API_KEY"]
    )
    mcp_client = MCPClient()
    await mcp_client.connect_to_server(path_to_server_file)
    res_tools = await mcp_client.session.list_tools()
    available_tools = [{
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description,
            "parameters": {
                **tool.inputSchema
            }
        }
    } for tool in res_tools.tools]

    messages = [
        {'role':'user','content':'what is 2+3?'}
    ]

    response = await openai_client.chat.completions.create(
            model='nvidia/llama-3.3-nemotron-super-49b-v1',
            messages=messages,
            tools=available_tools,
            tool_choice="auto",
            stream=False
        )

    stop_reason = (
        "tool_calls"
        if response.choices[0].message.tool_calls is not None
        else response.choices[0].finish_reason
    )

    if stop_reason == 'tool_calls':
        for tool_call in response.choices[0].message.tool_calls:
            tool_name = tool_call.function.name
            arguments = (
                json.loads(tool_call.function.arguments)
                if isinstance(tool_call.function.arguments, str)
                else tool_call.function.arguments
            )

            # Execute tool call
            print(f"[Calling tool {tool_name} with args {arguments}]")
            tool_result = await mcp_client.session.call_tool(tool_name, arguments)
            result = tool_result.content[0].text
            print(f'tool call result: {result}')

    await mcp_client.cleanup()

asyncio.run(main('./tutorial/mcp-server-demo/server_low_level.py'))

    
