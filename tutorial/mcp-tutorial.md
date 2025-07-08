# Model Context Protocol (MCP)

Model Context Protocol (MCP) is an open standard that enables AI applications to connect with external data sources and tools.  
Think of it as a standardized way for AI models to interact with the world beyond their training data.

## Key Components

The protocol operates on a client-server architecture where:

* MCP Clients are AI applications (e.g. Claude Desktop) that want to access external data
* MCP Servers are lightweight programs that provide access to specific resources or tools
* Resources can be files, database records, API endpoints, or any structured data
* Tools are functions the AI can execute, like running queries or performing calculations

## Practical Applications

Common use cases include connecting AI assistants to:

* Business databases and CRM systems
* File storage and document repositories
* Development tools and code repositories
* APIs and web services
* Local system resources
* Content creation tools - e.g. [Claude Desktop with Blender MCP](https://www.youtube.com/watch?v=DqgKuLYUv00)

## Examples

Go through the below examples in order to understand the basic workings of the MCP protocol.  

### Claude for Desktop intergration to MCP Servers

For each of the examples below, you can connect an MCP client to the MCP server by using the below configuration.

```bash
"Demo": {
    "command": "uv",
    "args": [
    "run",
    "--with",
    "mcp[cli]",
    "mcp",
    "run",
    "<project_folder>/mcp-server-demo/server.py"
    ]
}
```

In claude for Desktop, you can place this in claude_desktop_config.json.  
You should see the tool 'Demo' available in the UI.
![claude demo mcp server](./images/claude-mcp-server.png)

You can now test out a prompt that utilises the tool.  
E.g. what is 2+3?

![claude prompt](./images/claude-prompt.png)

Allow tool calling

![claude prompt](./images/claude-trust-tool.png)

Output

![claude prompt](./images/claude-output.png)

#### Note:

You can test your MCP Servers for the assignment using a similar setup.

You can also generate synthetic test cases to test your workflow and MCP Servers.  
A convenient approach is to allow Claude for Desktop to read the database schema through [sqlite mcp server](https://github.com/modelcontextprotocol/servers-archived/blob/main/src/sqlite) and using your created MCP server to return sample output.

### Example of a stdio MCP Server using the high level SDK (fastmcp)

Refer to [mcp-server-demo](./mcp-server-demo/server.py).  
This mcp server enables simple addition and subtraction of 2 integers.  

### Example of a stdio MCP Server using the low level SDK

Refer to [mcp-server-low-level-demo](./mcp-server-demo/server_low_level.py).  
Compared to the high level SDK, the low level SDK allows you
1) Maximum control over protocol behavior
2) Custom transport implementations
3) Implementation of non standard features  

An example of a useful low level mcp server that enables querying of an sqlite database through natural language can be found [here](https://github.com/modelcontextprotocol/servers-archived/blob/main/src/sqlite).  

### Example of an MCP Client utilising the high/low level SDKs

Refer to [mcp-client-demo](./mcp-client-demo/client.py).  
This mcp server initializes the mcp server, lists the tools and calls the tools.  

### Example of a Streamable HTTP MCP Server using the high level SDK (fastmcp)

Refer to [mcp-server-http-demo](./mcp-server-demo/server_http.py).  
This is a 'real server' that can be run remotely.  
The mcp servers based on stdio are actually background processes that run locally.

### Example of a Streamable HTTP MCP Server using the low level SDK (fastmcp)

Refer to [mcp-server-http-low-level-demo](./mcp-server-demo/server_http_low_level.py).  
This is a 'real server' that can be run remotely.  
The mcp servers based on stdio are actually background processes that run locally.

### More examples

Refer to the [official mcp python sdk](https://github.com/modelcontextprotocol/python-sdk/tree/main) for more examples and features.

## Vulnerabilities

The MCP protocol is not perfect and does come with a set of well known vulnerabilities.  
Make sure to validate external/3rd party MCP Servers before using them.  
Below's an illustration courtesy of [Rakesh Gohel](https://www.linkedin.com/in/rakeshgohel01).  
![MCP Vulnerabilities](./images/mcp-vulnerabilities.gif)