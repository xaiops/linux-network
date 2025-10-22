"""Conversational ReAct agent for network security queries."""

import asyncio
import logging
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from src.config import load_config
from src.mcp_tools import load_mcp_tools

logger = logging.getLogger(__name__)


async def build_agent():
    """
    Build a conversational ReAct agent with MCP tools.
    
    This agent can answer questions about network security by:
    - Calling MCP tools to get data
    - Reasoning about the data
    - Providing helpful answers
    
    Returns:
        Compiled ReAct agent
    """
    logger.info("Building conversational ReAct agent...")
    
    # Load configuration (run in thread to avoid blocking)
    config = await asyncio.to_thread(load_config)
    
    # Initialize LLM
    llm = ChatOpenAI(
        base_url=config["llm"]["base_url"],
        model=config["llm"]["model"],
        api_key=config["llm"]["api_key"],
        temperature=config["llm"]["temperature"],
        max_tokens=config["llm"]["max_tokens"],
        timeout=60.0,
    )
    
    logger.info(f"LLM initialized: {config['llm']['model']}")
    
    # Load MCP tools
    tools = await load_mcp_tools(
        endpoint=config["mcp"]["endpoint"],
        target_host=config["target"]["host"],
        target_username=config["target"]["username"]
    )
    
    logger.info(f"Loaded {len(tools)} MCP tools")
    
    # Create ReAct agent with tools
    # This agent will:
    # 1. Receive a question
    # 2. Think about what tools to use
    # 3. Call the tools
    # 4. Observe the results
    # 5. Repeat until it has an answer
    # 6. Respond to the user
    
    # Load system prompt from config and format with target details
    system_prompt = config["prompt"]["system"].format(
        target_host=config["target"]["host"],
        target_username=config["target"]["username"]
    )
    
    agent = create_react_agent(
        llm,
        tools,
        prompt=system_prompt
    )
    
    logger.info(" ReAct agent built successfully")
    
    return agent

