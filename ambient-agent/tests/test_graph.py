"""Test graph building."""

import sys
from pathlib import Path

# Add parent to path so we can import src as a package
sys.path.insert(0, str(Path(__file__).parent))

from src.agent import build_agent


def test_graph():
    """Test that the graph builds without errors."""
    print("Testing graph building...\n")
    
    try:
        agent = build_agent()
        
        print(" Graph built successfully!")
        print(f"   Type: {type(agent)}")
        
        # Try to get graph representation
        try:
            print("\nGraph structure:")
            print(agent.get_graph().draw_ascii())
        except:
            print("   (ASCII graph not available)")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_graph()
    sys.exit(0 if success else 1)

