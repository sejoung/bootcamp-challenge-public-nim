from typing import Annotated

from langchain.chat_models import init_chat_model
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages

class State(TypedDict):
    messages: Annotated[list, add_messages]

model_id = 'nvidia/llama-3.3-nemotron-super-49b-v1'

graph_builder = StateGraph(State)
# specify base_url if using locally hosted nims
llm = init_chat_model(model=model_id,model_provider="nvidia")
def chatbot(state: State):
    return {"messages": [llm.invoke(state["messages"])]}

# The first argument is the unique node name
# The second argument is the function or object that will be called whenever
# the node is used.
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_edge(START, "chatbot")
graph = graph_builder.compile()

def stream_graph_updates(user_input: str):
    for event in graph.stream({"messages": [{"role": "user", "content": user_input}]}):
        for value in event.values():
            print("Assistant:", value["messages"][-1].content)

stream_graph_updates("what is langgraph?")

from pydantic import BaseModel
from typing import Literal

class UserIntent(BaseModel):
    """The user's current intent in the conversation"""
    intent: Literal["naruto", "bleach"]

"""
Applications need output from LLMs to be parseable
The most common format is json.
Different providers have different ways of enabling this.
For NVIDIA NIMs, this is done through extra_body={"nvext": {"guided_json": json_schema}}
Refer to the following link for more information
https://docs.nvidia.com/nim/large-language-models/latest/structured-generation.html
"""
# specify base_url if using locally hosted nims
llm_structured = init_chat_model(model=model_id,model_provider="nvidia").with_structured_output(
    UserIntent, strict=True
)

res = llm_structured.invoke([
    {'role':'system','content':'You are an anime encyclopedia. Classify if the user is asking a question on naruto or bleach.'},
    {'role':'user','content':'who is sasuke?'}
])

print(f'intent: {res.intent}')