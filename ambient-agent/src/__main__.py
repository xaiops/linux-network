"""Main entry point for the ambient agent.

This module is used when running the agent directly (not via cron).
For cron-based scheduling, use langgraph dev + cron API.
"""

import asyncio
import logging
from datetime import datetime

from .agent import build_agent
from .state import NetworkSecurityState

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)


async def run_once():
    """
    Run the agent once (for single execution or cron).
    """
    logger.info("🚀 Running Ambient Network Security Agent (single execution)")
    
    agent = build_agent()
    
    # Initialize state
    initial_state = NetworkSecurityState(
        current_events="",
        current_stats="",
        detected_anomalies=[],
        investigated_pids=[],
        messages=[],
        recommendations=[],
        alerts=[],
        historical_baseline={},
        iteration=1,
        last_run=datetime.now().isoformat()
    )
    
    # Run the agent
    result = await agent.ainvoke(initial_state)
    
    # Log summary
    logger.info(f"\n{'='*80}")
    logger.info(f"Execution complete")
    logger.info(f"  Anomalies detected: {len(result.get('detected_anomalies', []))}")
    logger.info(f"  Alerts sent: {len(result.get('alerts', []))}")
    logger.info(f"  Recommendations: {len(result.get('recommendations', []))}")
    logger.info(f"{'='*80}\n")
    
    return result


async def run_loop():
    """
    Run the agent continuously in a loop (for non-cron deployment).
    """
    logger.info("🚀 Starting Ambient Network Security Agent (continuous mode)")
    
    agent = build_agent()
    iteration = 0
    
    while True:
        try:
            iteration += 1
            logger.info(f"\n{'='*80}")
            logger.info(f"Starting monitoring cycle #{iteration}")
            logger.info(f"{'='*80}\n")
            
            # Initialize state for this cycle
            initial_state = NetworkSecurityState(
                current_events="",
                current_stats="",
                detected_anomalies=[],
                investigated_pids=[],
                messages=[],
                recommendations=[],
                alerts=[],
                historical_baseline={},
                iteration=iteration,
                last_run=datetime.now().isoformat()
            )
            
            # Run the agent
            result = await agent.ainvoke(initial_state)
            
            # Log summary
            logger.info(f"\n{'='*80}")
            logger.info(f"Cycle #{iteration} complete")
            logger.info(f"  Anomalies detected: {len(result.get('detected_anomalies', []))}")
            logger.info(f"  Alerts sent: {len(result.get('alerts', []))}")
            logger.info(f"  Recommendations: {len(result.get('recommendations', []))}")
            logger.info(f"{'='*80}\n")
            
            # Sleep for configured interval
            from .config import load_config
            config = load_config()
            sleep_time = config["agent"]["monitoring_interval"]
            
            logger.info(f"😴 Sleeping for {sleep_time} seconds...\n")
            await asyncio.sleep(sleep_time)
            
        except KeyboardInterrupt:
            logger.info("\n\n🛑 Agent stopped by user")
            break
        except Exception as e:
            logger.error(f"❌ Error in agent loop: {e}", exc_info=True)
            logger.info("Retrying in 60 seconds...")
            await asyncio.sleep(60)


def main():
    """Entry point - defaults to continuous loop mode."""
    import sys
    
    # Check if --once flag is provided
    if "--once" in sys.argv:
        try:
            asyncio.run(run_once())
        except KeyboardInterrupt:
            logger.info("Exiting...")
    else:
        try:
            asyncio.run(run_loop())
        except KeyboardInterrupt:
            logger.info("Exiting...")


if __name__ == "__main__":
    main()
