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

"""
Try adding your own tools here
E.g. multiply(a,b) and divide(a,b)
"""

# initialise mcp server using streamable-http as a web server
mcp.run(transport='streamable-http')