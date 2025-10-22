"""MCP client for calling tools on the remote server."""

import logging
from contextlib import asynccontextmanager
from typing import Any, Dict

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

logger = logging.getLogger(__name__)


class MCPClient:
    """Client for connecting to MCP server and calling tools."""
    
    def __init__(self, endpoint: str):
        """
        Initialize MCP client.
        
        Args:
            endpoint: MCP server endpoint URL
        """
        self.endpoint = endpoint
        logger.info(f"MCPClient initialized with endpoint: {endpoint}")
    
    @asynccontextmanager
    async def get_session(self):
        """
        Get an MCP session.
        
        Yields:
            ClientSession: Active MCP session
        """
        logger.debug(f"Connecting to MCP server: {self.endpoint}")
        
        async with streamablehttp_client(self.endpoint) as (read, write, _):
            async with ClientSession(read, write) as session:
                await session.initialize()
                logger.debug("MCP session initialized")
                yield session
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]):
        """
        Call an MCP tool and return the result.
        
        Args:
            tool_name: Name of the tool to call
            arguments: Dictionary of tool arguments
        
        Returns:
            Tool result
        """
        logger.info(f"Calling MCP tool: {tool_name} with args: {list(arguments.keys())}")
        
        try:
            async with self.get_session() as session:
                result = await session.call_tool(tool_name, arguments)
                
                logger.info(f"Tool {tool_name} completed successfully")
                return result
                
        except Exception as e:
            logger.error(f"Tool {tool_name} failed: {e}")
            raise
    
    async def list_tools(self):
        """
        List available tools from the MCP server.
        
        Returns:
            List of available tools
        """
        logger.info("Listing available MCP tools")
        
        try:
            async with self.get_session() as session:
                tools = await session.list_tools()
                logger.info(f"Found {len(tools.tools)} tools")
                return tools.tools
                
        except Exception as e:
            logger.error(f"Failed to list tools: {e}")
            raise

