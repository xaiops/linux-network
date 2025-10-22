"""Configuration management."""

import os
import yaml
from pathlib import Path
from typing import Dict, Any


def load_config(config_path: str = None) -> Dict[str, Any]:
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Path to config file. If None, looks in default locations.
    
    Returns:
        Configuration dictionary
    """
    if config_path is None:
        # Try default locations
        possible_paths = [
            Path("config.yaml"),
            Path("../config.yaml"),
            Path("/etc/ambient-agent/config.yaml"),
        ]
        
        for path in possible_paths:
            if path.exists():
                config_path = path
                break
        
        if config_path is None:
            raise FileNotFoundError("Config file not found. Expected config.yaml in current directory.")
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Apply environment variable overrides
    config = _apply_env_overrides(config)
    
    return config


def _apply_env_overrides(config: Dict[str, Any]) -> Dict[str, Any]:
    """Apply environment variable overrides to config."""
    
    # LlamaStack overrides
    if os.getenv("LLAMASTACK_BASE_URL"):
        config["llm"]["base_url"] = os.getenv("LLAMASTACK_BASE_URL")
    if os.getenv("LLAMASTACK_API_KEY"):
        config["llm"]["api_key"] = os.getenv("LLAMASTACK_API_KEY")
    if os.getenv("LLAMASTACK_MODEL"):
        config["llm"]["model"] = os.getenv("LLAMASTACK_MODEL")
    
    # MCP overrides
    if os.getenv("MCP_ENDPOINT"):
        config["mcp"]["endpoint"] = os.getenv("MCP_ENDPOINT")
    
    # Target overrides
    if os.getenv("TARGET_HOST"):
        config["target"]["host"] = os.getenv("TARGET_HOST")
    if os.getenv("TARGET_USERNAME"):
        config["target"]["username"] = os.getenv("TARGET_USERNAME")
    
    # Alert overrides
    if os.getenv("SLACK_WEBHOOK_URL"):
        config.setdefault("alerts", {})["slack_webhook"] = os.getenv("SLACK_WEBHOOK_URL")
    if os.getenv("ALERT_EMAIL"):
        config.setdefault("alerts", {})["email"] = os.getenv("ALERT_EMAIL")
    
    return config


def get_prompt(config: Dict[str, Any], prompt_name: str, **kwargs) -> tuple[str, str]:
    """
    Get a prompt from config and format it with variables.
    
    Args:
        config: Configuration dictionary
        prompt_name: Name of the prompt (e.g., 'anomaly_analysis')
        **kwargs: Variables to format into the user template
    
    Returns:
        Tuple of (system_prompt, user_prompt)
    """
    prompt_config = config["prompts"].get(prompt_name)
    
    if not prompt_config:
        raise ValueError(f"Prompt '{prompt_name}' not found in config")
    
    system_prompt = prompt_config["system"].strip()
    user_template = prompt_config["user_template"].strip()
    
    # Format the user template with provided variables
    user_prompt = user_template.format(**kwargs)
    
    return system_prompt, user_prompt

