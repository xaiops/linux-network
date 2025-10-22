"""Test configuration loading."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from config import load_config, get_prompt


def test_config():
    """Test loading configuration."""
    print("Testing config loading...")
    
    try:
        config = load_config()
        
        print(f" Config loaded successfully")
        print(f"   MCP Endpoint: {config['mcp']['endpoint']}")
        print(f"   Target Host: {config['target']['host']}")
        print(f"   LLM Model: {config['llm']['model']}")
        print(f"   LLM Base URL: {config['llm']['base_url']}")
        
        # Test prompt loading
        print("\nTesting prompt loading...")
        system, user = get_prompt(config, "anomaly_analysis", anomalies_text="Test anomaly")
        
        print(f" Prompt loaded successfully")
        print(f"   System prompt length: {len(system)} chars")
        print(f"   User prompt length: {len(user)} chars")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_config()
    sys.exit(0 if success else 1)

