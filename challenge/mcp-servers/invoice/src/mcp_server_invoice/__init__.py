from . import server_http
import asyncio
import argparse

def main():
    parser = argparse.ArgumentParser(description='Invoice MCP Server')
    parser.add_argument('--db-path', 
                       default="data/chinook.db",
                       help='Path to SQLite database file')
    parser.add_argument('--nvidia-api-key', 
                       default="dummy",
                       help='your nvidia api key')
    parser.add_argument('--mcp-server-qna-path', 
                       default="",
                       help='your mcp server directory')
    parser.add_argument('--inf-url', 
                       default="https://integrate.api.nvidia.com/v1",
                       help='base url for inference')

    args = parser.parse_args()

    # streamable http MCP server
    asyncio.run(server_http.main(args.db_path,args.nvidia_api_key,args.mcp_server_qna_path,args.inf_url))

__all__ = ['main','server']