from openai import AsyncOpenAI
import os
import asyncio
from client import MCPClient
import json
import pathlib

async def main(path_to_server_file):

    # Initialise openai client to invoke NVIDIA NIMs (LLM)
    openai_client = AsyncOpenAI(
        base_url = "https://integrate.api.nvidia.com/v1",
        api_key = os.environ["NVIDIA_API_KEY"]
    )

    # Initialise MCP Client
    mcp_client = MCPClient()

    # Connect to the Stdio MCP Server
    await mcp_client.connect_to_server(path_to_server_file)

    # List tools available in the Stdio MCP Server
    res_tools = await mcp_client.session.list_tools()

    # Create json for each of the tools using the name, description and inputSchema returned from the MCP Server's list_tools() method
    # This format follows OpenAI's function calling schema - https://platform.openai.com/docs/guides/function-calling?api-mode=responses
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

    # Construct message in the format of the messages API
    # https://docs.nvidia.com/nim/large-language-models/latest/system-example.html
    messages = [
        {'role':'user','content':'what is 2+3?'}
    ]

    # Invoke the NIM using the chat completions API
    # https://docs.nvidia.com/nim/large-language-models/latest/system-example.html
    response = await openai_client.chat.completions.create(
            model='nvidia/llama-3.3-nemotron-super-49b-v1',
            messages=messages,
            tools=available_tools,
            tool_choice="auto",
            stream=False
        )

    """
    Determine the stop reason of the output generation.
    We specify `tool_calls` if the LLM decides to invoke a tool.
    Else, this can be `stop` if the model hit a natural stop point or a provided stop
    sequence, `length` if the maximum number of tokens specified in the request was
    reached, or `content_filter` if content was omitted due to a flag from our
    content filters
    """ 
    stop_reason = (
        "tool_calls"
        if response.choices[0].message.tool_calls is not None
        else response.choices[0].finish_reason
    )

    """
    From the LLM's response, obtain the function name and arguments.
    Invoke the tool through the MCP Client by providing the function name and arguments
    """
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

tutorial_path = pathlib.Path().resolve().parent
asyncio.run(main(str(tutorial_path / 'mcp-server-demo/server_low_level.py')))

    
