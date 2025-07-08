# server.py
from mcp.server.fastmcp import FastMCP

# Create an MCP server
mcp = FastMCP("simple-math")

# Add an addition tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

# Add a subtraction tool
@mcp.tool()
def subtract(a: int, b: int) -> int:
    """Add two numbers"""
    return a - b

mcp.run(transport='stdio')