"""Test MCP tools loading with langchain-mcp-adapters."""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.config import load_config
from src.mcp_tools import load_mcp_tools


async def test_mcp_tools():
    """Test loading MCP tools using langchain-mcp-adapters."""
    print("Testing MCP tools loading with langchain-mcp-adapters...\n")
    
    try:
        # Load config
        config = load_config()
        
        # Load MCP tools
        print("Loading tools...")
        tools = await load_mcp_tools(
            endpoint=config["mcp"]["endpoint"],
            target_host=config["target"]["host"],
            target_username=config["target"]["username"]
        )
        
        print(f" Successfully loaded {len(tools)} tools:\n")
        
        # List all tools
        for i, tool in enumerate(tools, 1):
            print(f"{i}. {tool.name}")
            print(f"   Description: {tool.description[:100]}...")
            print()
        
        # Test calling a tool
        print("\nTesting tool invocation...")
        print("Calling get_network_event_stats...")
        
        stats_tool = None
        for tool in tools:
            if tool.name == "get_network_event_stats":
                stats_tool = tool
                break
        
        if stats_tool:
            result = await stats_tool.ainvoke({
                "minutes": 5,
                "host": config["target"]["host"],
                "username": config["target"]["username"]
            })
            
            print(f" Tool invocation successful!")
            print(f"Result preview (first 300 chars):")
            print(f"{str(result)[:300]}...")
        else:
            print("⚠️  Tool 'get_network_event_stats' not found")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_mcp_tools())
    sys.exit(0 if success else 1)

