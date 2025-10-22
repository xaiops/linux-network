"""LangGraph nodes for the ambient agent."""

import logging
from datetime import datetime
from langchain_core.messages import SystemMessage, HumanMessage

from .state import NetworkSecurityState
from .llm_client import get_llm
from .config import load_config, get_prompt
from .mcp_tools import load_mcp_tools, get_mcp_tool_by_name

logger = logging.getLogger(__name__)

# Load config and initialize clients
config = load_config()
llm = get_llm(config["llm"])

# Global tools cache (loaded once)
_tools_cache = None

async def get_tools():
    """Get or load MCP tools."""
    global _tools_cache
    if _tools_cache is None:
        _tools_cache = await load_mcp_tools(
            endpoint=config["mcp"]["endpoint"],
            target_host=config["target"]["host"],
            target_username=config["target"]["username"]
        )
    return _tools_cache


async def monitor_events(state: NetworkSecurityState) -> NetworkSecurityState:
    """
    Fetch latest network events and stats from MCP using proper tool calling.
    """
    logger.info("📊 Monitoring network events")
    
    try:
        # Get MCP tools
        tools = await get_tools()
        
        # Get the specific tools we need
        events_tool = await get_mcp_tool_by_name(tools, "get_network_events_history")
        stats_tool = await get_mcp_tool_by_name(tools, "get_network_event_stats")
        
        # Call tools with proper parameters
        events_result = await events_tool.ainvoke({
            "minutes": config["agent"]["analysis_window"],
            "host": config["target"]["host"],
            "username": config["target"]["username"]
        })
        
        stats_result = await stats_tool.ainvoke({
            "minutes": config["agent"]["analysis_window"],
            "host": config["target"]["host"],
            "username": config["target"]["username"]
        })
        
        # Results are already strings from MCP tools
        events_text = str(events_result)
        stats_text = str(stats_result)
        
        logger.info(f" Fetched network data: {len(events_text)} chars (events), {len(stats_text)} chars (stats)")
        
        return {
            **state,
            "current_events": events_text,
            "current_stats": stats_text,
            "last_run": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to fetch events: {e}")
        return {
            **state,
            "current_events": f"Error: {str(e)}",
            "current_stats": "",
            "last_run": datetime.now().isoformat()
        }


async def analyze_anomalies(state: NetworkSecurityState) -> NetworkSecurityState:
    """
    Detect anomalies using MCP tool with proper tool calling.
    """
    logger.info("🔍 Analyzing for anomalies")
    
    try:
        # Get MCP tools
        tools = await get_tools()
        anomaly_tool = await get_mcp_tool_by_name(tools, "detect_network_anomalies")
        
        # Call tool
        result = await anomaly_tool.ainvoke({
            "minutes": config["agent"]["analysis_window"],
            "host": config["target"]["host"],
            "username": config["target"]["username"]
        })
        
        anomalies_text = str(result)
        
        # Count anomalies by checking for severity markers
        has_anomalies = ("HIGH" in anomalies_text or 
                        "CRITICAL" in anomalies_text or 
                        "MEDIUM" in anomalies_text)
        
        anomaly_list = [anomalies_text] if has_anomalies else []
        
        logger.info(f" Analysis complete: {len(anomaly_list)} anomalies detected")
        
        return {
            **state,
            "detected_anomalies": anomaly_list
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to analyze anomalies: {e}")
        return {
            **state,
            "detected_anomalies": []
        }


async def investigate_processes(state: NetworkSecurityState) -> NetworkSecurityState:
    """
    Investigate suspicious processes in detail.
    
    For now, this is a placeholder. We could extract PIDs from anomalies
    and call analyze_process_network_behavior for each.
    """
    logger.info("🔎 Investigating suspicious processes")
    
    # TODO: Extract PIDs from anomaly reports and investigate each
    # For now, just pass through
    
    return {
        **state,
        "investigated_pids": []
    }


async def llm_analysis(state: NetworkSecurityState) -> NetworkSecurityState:
    """
    Use LLM to analyze anomalies with prompts from config.
    """
    logger.info("🧠 Starting LLM analysis")
    
    if not state.get("detected_anomalies"):
        logger.info("No anomalies to analyze, skipping LLM")
        return state
    
    # Format anomalies
    anomalies_text = "\n\n".join([
        f"Anomaly {i+1}:\n{anomaly}"
        for i, anomaly in enumerate(state["detected_anomalies"])
    ])
    
    # Get prompts from config
    system_prompt_text, user_prompt_text = get_prompt(
        config,
        "anomaly_analysis",
        anomalies_text=anomalies_text
    )
    
    # Create messages
    system_prompt = SystemMessage(content=system_prompt_text)
    user_prompt = HumanMessage(content=user_prompt_text)
    
    try:
        response = await llm.ainvoke([system_prompt, user_prompt])
        analysis = response.content
        
        logger.info(f" LLM analysis complete: {len(analysis)} chars")
        
        # Extract recommendations
        recommendations = extract_recommendations(analysis)
        
        return {
            **state,
            "recommendations": recommendations,
            "messages": state.get("messages", []) + [system_prompt, user_prompt, response],
        }
        
    except Exception as e:
        logger.error(f"❌ LLM analysis failed: {e}")
        return {
            **state,
            "recommendations": [f"LLM analysis failed: {str(e)}"]
        }


async def generate_report(state: NetworkSecurityState) -> NetworkSecurityState:
    """
    Generate comprehensive security report using config prompt.
    """
    logger.info("📋 Generating security report")
    
    # Get the last LLM message if available
    llm_analysis_text = ""
    if state.get("messages"):
        for msg in reversed(state["messages"]):
            if hasattr(msg, 'content'):
                llm_analysis_text = msg.content
                break
    
    # Get report generation prompt from config
    system_prompt_text, user_prompt_text = get_prompt(
        config,
        "report_generation",
        anomalies="\n\n".join(state.get("detected_anomalies", [])) or "None",
        investigation_results=str(state.get("investigated_pids", [])) or "None",
        llm_analysis=llm_analysis_text or "None"
    )
    
    system_prompt = SystemMessage(content=system_prompt_text)
    user_prompt = HumanMessage(content=user_prompt_text)
    
    try:
        response = await llm.ainvoke([system_prompt, user_prompt])
        report = response.content
        
        logger.info(" Report generated successfully")
        
        return {
            **state,
            "alerts": state.get("alerts", []) + [report]
        }
        
    except Exception as e:
        logger.error(f"❌ Report generation failed: {e}")
        # Create a simple text report as fallback
        simple_report = f"""
Security Report - {datetime.now().isoformat()}

Anomalies Detected: {len(state.get('detected_anomalies', []))}
{chr(10).join(state.get('detected_anomalies', []))}

Recommendations:
{chr(10).join(f"- {r}" for r in state.get('recommendations', []))}
"""
        return {
            **state,
            "alerts": state.get("alerts", []) + [simple_report]
        }


async def send_alert(state: NetworkSecurityState) -> NetworkSecurityState:
    """
    Send alerts based on findings.
    """
    logger.info("🚨 Sending alerts")
    
    alerts_config = config.get("alerts", {})
    
    if not alerts_config.get("enabled", True):
        logger.info("Alerts disabled in config")
        return state
    
    # Write to log file
    log_file = alerts_config.get("log_file", "./logs/alerts.log")
    
    try:
        import os
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        with open(log_file, 'a') as f:
            f.write(f"\n{'='*80}\n")
            f.write(f"Alert at {datetime.now().isoformat()}\n")
            f.write(f"{'='*80}\n")
            for alert in state.get("alerts", []):
                f.write(f"{alert}\n")
        
        logger.info(f" Alert written to {log_file}")
    except Exception as e:
        logger.error(f"❌ Failed to write alert: {e}")
    
    return state


async def update_baseline(state: NetworkSecurityState) -> NetworkSecurityState:
    """
    Update baseline with learned patterns using MCP tools.
    """
    logger.info("📚 Updating baseline")
    
    try:
        # Get fresh stats if not in state
        if not state.get("current_stats"):
            tools = await get_tools()
            stats_tool = await get_mcp_tool_by_name(tools, "get_network_event_stats")
            
            stats_result = await stats_tool.ainvoke({
                "minutes": 60,  # Last hour for baseline
                "host": config["target"]["host"],
                "username": config["target"]["username"]
            })
            current_stats = str(stats_result)
        else:
            current_stats = state.get("current_stats", "No data")
        
        # Use LLM to suggest baseline updates
        system_prompt_text, user_prompt_text = get_prompt(
            config,
            "baseline_learning",
            current_stats=current_stats,
            baseline=str(state.get("historical_baseline", {}))
        )
        
        system_prompt = SystemMessage(content=system_prompt_text)
        user_prompt = HumanMessage(content=user_prompt_text)
        
        response = await llm.ainvoke([system_prompt, user_prompt])
        
        logger.info(" Baseline updated with LLM suggestions")
        
        # Update baseline with timestamp
        return {
            **state,
            "historical_baseline": {
                "last_update": datetime.now().isoformat(),
                "llm_suggestions": response.content[:500]  # Store snippet
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Baseline update failed: {e}")
        return state


def extract_recommendations(analysis: str) -> list[str]:
    """Extract action items from LLM response."""
    recommendations = []
    lines = analysis.split("\n")
    
    in_actions = False
    for line in lines:
        line = line.strip()
        if "recommended actions" in line.lower() or "actions:" in line.lower():
            in_actions = True
            continue
        
        if in_actions and line:
            # Look for numbered items like "1. ", "- ", etc.
            if line[0].isdigit() or line.startswith("-") or line.startswith("•"):
                recommendations.append(line.lstrip("0123456789.-•• "))
    
    return recommendations if recommendations else ["Review anomaly details manually"]


# Conditional routing functions
def should_investigate(state: NetworkSecurityState) -> str:
    """Decide if we need to investigate."""
    if state.get("detected_anomalies"):
        return "investigate"
    return "baseline"


def should_alert(state: NetworkSecurityState) -> str:
    """Decide if we need to alert."""
    # Check if any HIGH or CRITICAL in anomalies
    anomalies = state.get("detected_anomalies", [])
    for anomaly in anomalies:
        if "CRITICAL" in anomaly or "HIGH" in anomaly:
            return "alert"
    return "baseline"

