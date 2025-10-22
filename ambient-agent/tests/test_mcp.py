"""Test MCP client connection."""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from config import load_config
from mcp_client import MCPClient


async def test_mcp():
    """Test MCP client connection and tool calls."""
    print("Testing MCP connection...\n")
    
    try:
        # Load config
        config = load_config()
        
        # Initialize MCP client
        mcp = MCPClient(config["mcp"]["endpoint"])
        
        # List available tools
        print("1. Listing available tools...")
        tools = await mcp.list_tools()
        print(f" Found {len(tools)} tools:")
        for tool in tools:
            print(f"   - {tool.name}")
        
        # Test get_network_event_stats (smallest/quickest tool)
        print("\n2. Testing get_network_event_stats tool...")
        result = await mcp.call_tool("get_network_event_stats", {
            "minutes": 5,
            "host": config["target"]["host"],
            "username": config["target"]["username"]
        })
        
        # Extract text from result
        if hasattr(result, 'content') and len(result.content) > 0:
            text = result.content[0].text if hasattr(result.content[0], 'text') else str(result.content[0])
            print(f" Tool call successful!")
            print(f"   Result preview (first 500 chars):")
            print(f"   {text[:500]}...")
        else:
            print(f" Tool call successful (result: {result})")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_mcp())
    sys.exit(0 if success else 1)

