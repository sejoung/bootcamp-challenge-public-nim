from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider


class AgentOutput(BaseModel):
    output: str


system_prompt = """
You are an online music store agent tasked to retrieve a list of song tracks.
Only base your reply on the context provided.
"""


class QNAAgent:
    def __init__(self, nvidia_api_key, mcp_server_qna_path, inf_url):
        ## TODO
        ## define MCP server, model and agent
        print(f"Starting QNA Agent... {nvidia_api_key}")
        provider = OpenAIProvider(base_url=inf_url, api_key=nvidia_api_key)
        model = OpenAIModel(model_name="gpt-4o", provider=provider)
        mcp_server = MCPServerStdio("qna_server", mcp_server_qna_path)
        self.agent = Agent(model, mcp_servers=[mcp_server])

    async def run(self, query):
        ## TODO
        ## run agent with mcp servers and return output
        response = await self.agent.arun(input=query)
        return response.output
