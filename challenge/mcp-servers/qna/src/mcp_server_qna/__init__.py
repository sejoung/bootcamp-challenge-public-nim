from . import server
import asyncio
import argparse

def main():
    parser = argparse.ArgumentParser(description='QNA MCP Server')
    parser.add_argument('--db-path', 
                       default="data/chinook.db",
                       help='Path to SQLite database file')
    args = parser.parse_args()
    
    # stdio MCP server
    asyncio.run(server.main(args.db_path))

__all__ = ['main','server']