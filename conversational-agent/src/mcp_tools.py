"""MCP tools loader using langchain-mcp-adapters."""

import logging
from typing import List
from langchain_core.tools import BaseTool

try:
    from langchain_mcp_adapters.client import MultiServerMCPClient
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    logging.warning("langchain-mcp-adapters not installed. Install with: pip install langchain-mcp-adapters")

logger = logging.getLogger(__name__)


async def load_mcp_tools(endpoint: str, target_host: str, target_username: str) -> List[BaseTool]:
    """
    Load MCP tools using langchain-mcp-adapters.
    
    Args:
        endpoint: MCP server endpoint URL
        target_host: Target RHEL host for MCP tools
        target_username: SSH username for target host
    
    Returns:
        List of LangChain-compatible tools
    """
    if not MCP_AVAILABLE:
        raise ImportError("langchain-mcp-adapters is required. Install with: pip install langchain-mcp-adapters")
    
    logger.info(f"Loading MCP tools from {endpoint}")
    
    try:
        # Configure MCP client
        # Using streamable_http transport (SSE variant) for HTTP-based MCP server
        client = MultiServerMCPClient({
            "linux_diagnostics": {
                "transport": "streamable_http",
                "url": endpoint,
                "headers": {
                    # Add any required headers if needed
                }
            }
        })
        
        # Get tools from MCP server
        tools = await client.get_tools()
        
        logger.info(f" Successfully loaded {len(tools)} MCP tools")
        
        # Log available tools
        for tool in tools:
            logger.debug(f"  - {tool.name}: {tool.description[:80]}...")
        
        return tools
        
    except Exception as e:
        logger.error(f"❌ Failed to load MCP tools: {e}")
        raise


async def get_mcp_tool_by_name(tools: List[BaseTool], name: str) -> BaseTool:
    """
    Get a specific tool by name.
    
    Args:
        tools: List of tools
        name: Tool name to find
    
    Returns:
        The requested tool
    
    Raises:
        ValueError: If tool not found
    """
    for tool in tools:
        if tool.name == name:
            return tool
    
    raise ValueError(f"Tool '{name}' not found. Available tools: {[t.name for t in tools]}")

