"""LLM client configuration for LlamaStack."""

import os
import logging
from langchain_openai import ChatOpenAI
from typing import Dict, Any

logger = logging.getLogger(__name__)


def get_llm(config: Dict[str, Any]) -> ChatOpenAI:
    """
    Initialize LLM client for LlamaStack.
    
    Args:
        config: LLM configuration from config.yaml
    
    Returns:
        Configured ChatOpenAI instance pointing to LlamaStack
    """
    base_url = config.get("base_url", "https://lss-lss.apps.prod.rhoai.rh-aiservices-bu.com/v1/openai/v1")
    model = config.get("model", "llama-4-scout-17b-16e-w4a16")
    api_key = config.get("api_key", "not-needed")
    temperature = config.get("temperature", 0.1)
    max_tokens = config.get("max_tokens", 2000)
    
    # Allow override from environment
    base_url = os.getenv("LLAMASTACK_BASE_URL", base_url)
    api_key = os.getenv("LLAMASTACK_API_KEY", api_key)
    model = os.getenv("LLAMASTACK_MODEL", model)
    
    logger.info(f"Initializing LLM client: {model} at {base_url}")
    
    llm = ChatOpenAI(
        base_url=base_url,
        model=model,
        api_key=api_key,
        temperature=temperature,
        max_tokens=max_tokens,
        timeout=60.0,  # 60 second timeout
    )
    
    return llm

