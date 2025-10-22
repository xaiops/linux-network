"""Test LLM client connection."""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from config import load_config
from llm_client import get_llm
from langchain_core.messages import HumanMessage


async def test_llm():
    """Test LLM client connection to LlamaStack."""
    print("Testing LLM connection to LlamaStack...\n")
    
    try:
        # Load config
        config = load_config()
        
        # Initialize LLM
        llm = get_llm(config["llm"])
        
        print(f" LLM client initialized")
        print(f"   Model: {config['llm']['model']}")
        print(f"   Base URL: {config['llm']['base_url']}")
        
        # Test with a simple prompt
        print("\nSending test message...")
        response = await llm.ainvoke([
            HumanMessage(content="Hello! Please respond with 'Connection successful' and nothing else.")
        ])
        
        print(f" Response received!")
        print(f"   Response: {response.content}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_llm())
    sys.exit(0 if success else 1)

