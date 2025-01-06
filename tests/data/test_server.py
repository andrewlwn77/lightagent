"""Test MCP server implementation."""

import asyncio
from pathlib import Path
from mirascope.mcp import MCPServer
from mcp.types import Resource
from pydantic import AnyUrl

# Create test server
app = MCPServer("test-server")

@app.tool()
async def get_data(query: str) -> dict:
    """Get test data based on query.
    
    Args:
        query: Search query
    """
    return {
        "result": f"Test result for {query}",
        "timestamp": "2024-01-05T12:00:00Z"
    }

@app.tool()
async def process_data(data: dict) -> dict:
    """Process provided data.
    
    Args:
        data: Data to process
    """
    return {
        "processed": data,
        "status": "success"
    }

@app.resource(
    uri="file://test_data.txt",
    name="Test Data",
    mime_type="text/plain",
    description="Test resource data"
)
async def read_test_data():
    """Read test data file."""
    return "Test resource content"

@app.prompt()
def analyze_data(query: str) -> str:
    """Generate analysis prompt.
    
    Args:
        query: Analysis query
    """
    return f"Analyze the following data: {query}"

async def main():
    """Run the test server."""
    await app.run()

if __name__ == "__main__":
    asyncio.run(main())