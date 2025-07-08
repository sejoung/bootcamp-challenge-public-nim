from typing import Literal
import json

from langchain.chat_models import init_chat_model
from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, StateGraph
from langgraph.graph.message import AnyMessage, add_messages
from langchain.schema import SystemMessage
from langchain_core.messages import convert_to_openai_messages
from langgraph.checkpoint.memory import InMemorySaver
from tabulate import tabulate
from typing_extensions import Annotated, TypedDict
from pydantic import BaseModel
from openai import AsyncOpenAI
import os
import argparse

from .mcp_http_client import MCPHTTPCLIENT

model_id='nvidia/llama-3.3-nemotron-super-49b-v1'

class State(TypedDict):
    """Agent state."""
    ## TODO
    ## define required graph states

# Instructions for extracting the user/purchase info from the conversation.
gather_info_instructions = """You are managing an online music store that sells song tracks. \
Customers can buy multiple tracks at a time and these purchases are recorded in a database as \
an Invoice per purchase and an associated set of Invoice Lines for each purchased track.

Your task is to help customers who would like a refund for one or more of the tracks they've \
purchased. In order for you to be able refund them, the customer must specify the Invoice ID \
to get a refund on all the tracks they bought in a single transaction, or one or more Invoice \
Line IDs if they would like refunds on individual tracks.

Often a user will not know the specific Invoice ID(s) or Invoice Line ID(s) for which they \
would like a refund. In this case you can help them look up their invoices by asking them to \
specify:
- Required: Their first name, last name, and phone number.
- Optionally: The track name, artist name, album name, or purchase date.

IMPORTANT: When extracting phone numbers:
- Preserve ALL spaces, dashes, parentheses, and formatting exactly as provided by the user
- Do NOT modify, standardize, or strip any characters from phone numbers
- Example: If user provides '+1 (204) 452-6452', store it exactly as '+1 (204) 452-6452'
- Do not convert formats like '555 123 4567' to '5551234567'

If the customer has not specified the required information (either Invoice/Invoice Line IDs \
or first name, last name, phone) then please ask them to specify it."""

async def store_agent(state:State,config: RunnableConfig):
    
    mcp_server_url = config.get("configurable", {}).get("mcp_server_url")
    inf_url = config.get("configurable", {}).get("inf_url")
    nvidia_api_key = config.get("configurable", {}).get("nvidia_api_key")
    openAI_client = AsyncOpenAI(
        base_url = inf_url,
        api_key = nvidia_api_key
    )

    mcp_client = MCPHTTPCLIENT(mcp_server_url)
    
    ## TODO
    ## implement agent tool calling

    output = {
            "messages": [{"role": "assistant", "content": ""}]
    }

    return output

class UserIntent(BaseModel):
    """The user's current intent in the conversation"""
    intent: Literal["valid", "unknown"]

router_llm = init_chat_model(model=model_id,model_provider="nvidia",configurable_fields=["base_url","api_key"]).with_structured_output(
    UserIntent, method="json_schema", strict=True
)

intent_classifier_instructions = """You are managing an online music store that sells song tracks. \
You can help customers by answering general questions about tracks sold at your store or help them get a refund on a purhcase they made at your store.

Return 'valid' if they are asking a general music question or trying to get a refund. Return 'unknown' otherwise. Do NOT return anything else. Do NOT try to respond to the user.
"""

# Node for routing.
async def intent_classifier(state: State,config: RunnableConfig):
    inf_url = config.get("configurable", {}).get("inf_url")
    nvidia_api_key = config.get("configurable", {}).get("nvidia_api_key")
    response = router_llm.with_config({"base_url":inf_url,"api_key":nvidia_api_key}).invoke(
        [{"role": "system", "content": intent_classifier_instructions}, *state["messages"]]
    )
    ask_human = False
    if response.intent == 'unknown':
        ask_human = True
    return {'intent':response.intent,'ask_human':ask_human}

# placeholder
def human_node(state: State):
    return {'ask_human':False}

def select_node(state: State):
    if 'ask_human' in state and state['ask_human']:
        return 'human'
    else:
        return 'continue' 

# Node for making sure the 'followup' key is set before our agent run completes.
def compile_followup(state: State) -> dict:
    """Set the followup to be the last message if it hasn't explicitly been set."""
    if not state.get("followup"):
        return {"followup": state["messages"][-1].content}
    return {}

def create_workflow(memory):
    # Agent definition
    workflow = StateGraph(State)
    
    ## TODO
    ## Define nodes and edges for graph

    #app = workflow.compile()
    #return app

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Invoice MCP Server')
    parser.add_argument('--nvidia-api-key', 
                       default="",
                       help='your nvidia api key')
    parser.add_argument('--mcp-server-url', 
                       default="http://localhost:8000/mcp",
                       help='mcp server url')
    parser.add_argument('--inf-url', 
                       default="https://integrate.api.nvidia.com/v1",
                       help='base url for inference')
    args = parser.parse_args()

    input_list = []
    output_list = []
    reasoning_list = []
    scores = []
    memory = InMemorySaver()
    config = {
        "configurable": {"thread_id": "1"},
        "env":"test",
        "nvidia_api_key":args.nvidia_api_key,
        "mcp_server_url":args.mcp_server_url,
        "inf_url":args.inf_url
    }
    app = create_workflow(memory=memory)

    ## TODO
    ## write your own test scripts