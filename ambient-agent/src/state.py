"""State definition for the ambient agent."""

from typing import TypedDict, Annotated
from datetime import datetime
from langgraph.graph.message import add_messages


class NetworkSecurityState(TypedDict):
    """State for the ambient network security agent."""
    
    # Current monitoring data
    current_events: str  # Raw text from get_network_events_history
    current_stats: str   # Raw text from get_network_event_stats
    
    # Analysis results
    detected_anomalies: list[str]  # List of anomaly descriptions
    investigated_pids: list[int]   # PIDs that were investigated
    
    # LLM analysis
    messages: Annotated[list, add_messages]  # LangGraph messages
    recommendations: list[str]  # Action recommendations from LLM
    
    # Alerts and reporting
    alerts: list[str]  # Alert messages to send
    
    # Baseline learning
    historical_baseline: dict  # Known-good patterns
    
    # Metadata
    iteration: int  # Monitoring cycle number
    last_run: str   # ISO timestamp of last run

