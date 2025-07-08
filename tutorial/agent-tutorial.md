# Agentic workflows

## LangGraph

LangGraph is a framework for building stateful, multi-step conversational AI applications as graphs.  

### Core Concepts

#### Graph-Based Architecture

LangGraph models AI workflows as directed graphs where nodes represent different agents or processing steps, and edges define the flow of information and control between them.

#### Stateful Execution

Unlike simple chains, LangGraph maintains state across the entire conversation or workflow, allowing agents to remember context and build upon previous interactions.

#### Multi-Agent Coordination

Multiple specialized agents can work together, each handling different aspects of a complex task while sharing information through the graph structure.

### Key Features

#### Checkpointing and Persistence

The framework can save execution state at any point, allowing for interruption, resumption, and branching of workflows.

#### Human-in-the-Loop

Built-in support for human intervention at specific points in the workflow, enabling approval steps or manual input.

#### Conditional Routing

Dynamic routing between nodes based on current state, agent outputs, or external conditions.

#### Error Handling and Retry Logic

Robust error handling with configurable retry mechanisms and fallback strategies.

### Common Use Cases

#### Customer Support Systems

Route inquiries to specialized agents (technical support, billing, general inquiries) based on intent classification.

#### Research and Analysis

Coordinate research agents that gather information, fact-checkers that verify claims, and writers that synthesize findings.

#### Content Creation Pipelines

Orchestrate planning agents, writers, editors, and reviewers in a structured workflow.

#### Decision-Making Systems

Build complex decision trees with multiple evaluation criteria and stakeholder input.

## Basic construct of langgraph

Follow the tutorials below to get an idea of how langgraph works.  
You will need to replace the llm invocations to use NVIDIA NIMs.  

Refer to [langgraph-demo](./langgraph-demo/) for an example using langchain to invoke NVIDIA NIMs.  

1) [build a basic chatbot](https://langchain-ai.github.io/langgraph/tutorials/get-started/1-build-basic-chatbot/)
2) [provide tools to the agent](https://langchain-ai.github.io/langgraph/tutorials/get-started/2-add-tools/)
3) [add memory to graph](https://langchain-ai.github.io/langgraph/tutorials/get-started/3-add-memory/)
4) [add human in the loop](https://langchain-ai.github.io/langgraph/tutorials/get-started/4-human-in-the-loop/)

## Tool calling with MCP

Refer to [nim-demo](./nim-demo/).  

This example demonstrates the following.  
1) Get the list of tools available from the [mcp server](./mcp-server-demo/server_low_level.py) using the [mcp client](./nim-demo/client.py).
2) Feed the list of available tools to the LLM (NVIDIA NIM) together with the prompt for the LLM to decide the tool to call and also the arguments to use.
3) Invoke the tool with arguments and obtain the results of the tool call.