from pydantic_ai import Agent
from openai import AsyncOpenAI
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.mcp import MCPServerStdio
import os

from pydantic import BaseModel

class AgentOutput(BaseModel):
    output: str

system_prompt = """
You are an online music store agent tasked to retrieve a list of song tracks.
Only base your reply on the context provided.
"""

class QNAAgent:
    def __init__(self,nvidia_api_key,mcp_server_qna_path,inf_url):
        ## TODO
        ## define MCP server, model and agent
        pass

    async def run(self,query):
        ## TODO
        ## run agent with mcp servers and return output
        pass