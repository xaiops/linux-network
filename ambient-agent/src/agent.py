"""Main LangGraph agent definition."""

import logging
from langgraph.graph import StateGraph, START, END

from .state import NetworkSecurityState
from .nodes import (
    monitor_events,
    analyze_anomalies,
    investigate_processes,
    llm_analysis,
    generate_report,
    send_alert,
    update_baseline,
    should_investigate,
    should_alert,
)

logger = logging.getLogger(__name__)


def build_agent():
    """
    Build the LangGraph state machine for network security monitoring.
    
    Flow:
        START → monitor → analyze → {threats?}
          → No: baseline → END
          → Yes: investigate → llm_analysis → report → {critical?}
              → Yes: alert → baseline → END
              → No: baseline → END
    
    Returns:
        Compiled LangGraph agent
    """
    logger.info("Building LangGraph agent...")
    
    # Create the state graph
    workflow = StateGraph(NetworkSecurityState)
    
    # Add nodes
    workflow.add_node("monitor", monitor_events)
    workflow.add_node("analyze", analyze_anomalies)
    workflow.add_node("investigate", investigate_processes)
    workflow.add_node("llm_analysis", llm_analysis)
    workflow.add_node("report", generate_report)
    workflow.add_node("alert", send_alert)
    workflow.add_node("baseline", update_baseline)
    
    # Define edges
    workflow.add_edge(START, "monitor")
    workflow.add_edge("monitor", "analyze")
    
    # Conditional: Should we investigate?
    workflow.add_conditional_edges(
        "analyze",
        should_investigate,
        {
            "investigate": "investigate",
            "baseline": "baseline"
        }
    )
    
    workflow.add_edge("investigate", "llm_analysis")
    workflow.add_edge("llm_analysis", "report")
    
    # Conditional: Should we alert?
    workflow.add_conditional_edges(
        "report",
        should_alert,
        {
            "alert": "alert",
            "baseline": "baseline"
        }
    )
    
    workflow.add_edge("alert", "baseline")
    workflow.add_edge("baseline", END)
    
    # Compile the graph
    agent = workflow.compile()
    
    logger.info(" LangGraph agent compiled successfully")
    
    return agent

