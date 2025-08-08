# Agentic workflows

## Basics of LangGraph

Go through the following for an introduction to LangGraph.  
For each of the sections, replace code using `init_chat_model` with the below to utilise NIMs.

```python
# specify base_url if using locally hosted nims
llm = init_chat_model(model='nvidia/llama-3.3-nemotron-super-49b-v1',model_provider="nvidia")
```

1) [build a basic chatbot](https://langchain-ai.github.io/langgraph/tutorials/get-started/1-build-basic-chatbot/)
2) [provide tools to the agent](https://langchain-ai.github.io/langgraph/tutorials/get-started/2-add-tools/)
3) [add memory to graph](https://langchain-ai.github.io/langgraph/tutorials/get-started/3-add-memory/)
4) [add human in the loop](https://langchain-ai.github.io/langgraph/tutorials/get-started/4-human-in-the-loop/)

## Invoking NVIDIA NIMs using langGraph/LangChain

Refer to [langgraph-demo](./langgraph-demo/) for an example using LangGraph/LangChain with NVIDIA NIMs.

## Tool calling with MCP

Refer to [nim-demo](./nim-demo/).  

This example demonstrates the following.  
1) Get the list of tools available from the [mcp server](./mcp-server-demo/server_low_level.py) using the [mcp client](./nim-demo/client.py).
2) Feed the list of available tools to the LLM (NVIDIA NIM) together with the prompt for the LLM to decide the tool to call and also the arguments to use.
3) Invoke the tool with arguments and obtain the results of the tool call.