# Ambient Network Security Agent

LangGraph-based autonomous agent for continuous network security monitoring using eBPF data and MCP tools.

## Architecture

```
Monitor Events → Analyze Anomalies → {Threats?}
  ├─ No  → Update Baseline → End
  └─ Yes → Investigate → LLM Analysis → Generate Report → {Critical?}
             ├─ Yes → Send Alert → Update Baseline → End
             └─ No  → Update Baseline → End
```

## Prerequisites

- Python 3.11+
- Access to:
  - MCP Server: `https://linux-mcp-server-rhel-mcp.apps.prod.rhoai.rh-aiservices-bu.com/mcp`
  - LlamaStack: `https://lss-lss.apps.prod.rhoai.rh-aiservices-bu.com/v1/openai/v1`
  - Target RHEL Server: `bastion.r42dl.sandbox5417.opentlc.com`

## Installation

```bash
# Install dependencies
pip install langgraph langchain langchain-openai mcp pydantic pyyaml httpx

# Or use uv
uv pip install langgraph langchain langchain-openai mcp pydantic pyyaml httpx
```

## Configuration

Edit `config.yaml` to configure:
- MCP endpoint
- Target server
- LLM settings
- Alert thresholds
- LLM prompts

## Testing Components

```bash
# Test configuration loading
python test_config.py

# Test MCP connection
python test_mcp.py

# Test LLM connection
python test_llm.py
```

## Running

### Option 1: LangGraph Dev (Recommended for Development)

```bash
# Start the LangGraph dev server
langgraph dev

# Open in browser: http://localhost:8123
# The LangGraph Studio UI will show the graph and allow testing
```

### Option 2: Direct Execution

```bash
# Run the agent in continuous loop
python -m src

# Stop with Ctrl+C
```

## What It Does

1. **Monitor** (every 5 minutes):
   - Fetches network events from eBPF collector
   - Gets network statistics

2. **Analyze**:
   - Calls MCP `detect_network_anomalies` tool
   - Identifies suspicious patterns

3. **Investigate** (if anomalies found):
   - Deep dives into suspicious processes
   - Calls MCP `analyze_process_network_behavior`

4. **LLM Analysis**:
   - Sends anomalies to Llama-4-Scout model
   - Gets contextual security assessment
   - Receives recommendations

5. **Report**:
   - Generates comprehensive security report

6. **Alert** (if critical):
   - Writes to alert log file
   - Can send to Slack/email (configurable)

7. **Learn**:
   - Updates baseline of normal behavior
   - Reduces false positives over time

## Alerts

Alerts are written to: `./logs/alerts.log`

## Project Structure

```
ambient-agent/
├── config.yaml           # Main configuration
├── langgraph.json        # LangGraph CLI config
├── pyproject.toml        # Dependencies
├── README.md
├── src/
│   ├── __init__.py
│   ├── __main__.py       # Main entry point
│   ├── agent.py          # LangGraph state machine
│   ├── config.py         # Configuration loader
│   ├── llm_client.py     # LLM initialization
│   ├── mcp_client.py     # MCP client
│   ├── nodes.py          # LangGraph nodes
│   └── state.py          # State definition
├── test_config.py        # Config test
├── test_llm.py           # LLM test
└── test_mcp.py           # MCP test
```

## Development

- All prompts are in `config.yaml` under `prompts:` section
- No hardcoded prompts in code
- LLM uses OpenAI-compatible API (LlamaStack)
- MCP client uses Streamable HTTP transport

## Deployment

For production deployment, run as a systemd service:

```bash
sudo cp ambient-agent.service /etc/systemd/system/
sudo systemctl enable ambient-agent
sudo systemctl start ambient-agent
```

## License

Apache 2.0

