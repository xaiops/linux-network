"""Test the conversational agent."""

import asyncio
import sys
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.agent import build_agent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)


async def test_agent():
    """Test the conversational agent with sample questions."""
    
    print("="*80)
    print("Building Conversational Network Security Agent")
    print("="*80)
    print()
    
    try:
        # Build the agent
        agent = await build_agent()
        
        print(" Agent built successfully!\n")
        
        # Test questions
        test_questions = [
            "What network activity has happened in the last 5 minutes?",
            "Are there any security anomalies I should know about?",
            "Show me network statistics for the last 10 minutes",
        ]
        
        for i, question in enumerate(test_questions, 1):
            print(f"\n{'='*80}")
            print(f"Test {i}/{len(test_questions)}")
            print(f"{'='*80}")
            print(f"Question: {question}\n")
            
            try:
                # Invoke the agent
                response = await agent.ainvoke({
                    "messages": [{"role": "user", "content": question}]
                })
                
                # Get the last message (agent's response)
                if response and "messages" in response:
                    last_message = response["messages"][-1]
                    print(f"Agent: {last_message.content}\n")
                else:
                    print(f"Agent: {response}\n")
                
            except Exception as e:
                print(f"❌ Error: {e}")
                logger.error(f"Failed to process question: {e}", exc_info=True)
        
        print(f"\n{'='*80}")
        print("Testing Complete!")
        print(f"{'='*80}\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Failed to build agent: {e}")
        logger.error(f"Agent build failed: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    success = asyncio.run(test_agent())
    sys.exit(0 if success else 1)

