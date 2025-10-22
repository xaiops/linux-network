# Linux Network Security Monitoring with AI Agents

An intelligent network security monitoring system using **LangGraph AI agents**, **eBPF network monitoring**, and **Model Context Protocol (MCP)** for RHEL systems.

## 🎯 Overview

This project provides two complementary AI agents for network security monitoring:

1. **Conversational Agent**: Interactive Q&A for security investigation
2. **Ambient Agent**: Autonomous continuous monitoring and alerting

Both agents use LangGraph, connect to MCP tools, and leverage LLM intelligence for security analysis.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     AI Agents (LangGraph)                       │
├──────────────────────────┬──────────────────────────────────────┤
│  Conversational Agent    │    Ambient Agent                     │
│  (Interactive ReAct)     │    (Autonomous Monitor)              │
└────────────┬─────────────┴────────────┬─────────────────────────┘
             │                          │
             └──────────┬───────────────┘
                        │
              ┌─────────▼──────────┐
              │   MCP Server       │
              │   (RHEL)      │
              └─────────┬──────────┘
                        │ SSH
              ┌─────────▼──────────┐
              │  RHEL Target       │
              │  - eBPF Agent      │
              │  - Network Events  │
              └────────────────────┘
```

### Components

- **eBPF Agent**: Captures network events (TCP/UDP) on target RHEL system
- **MCP Server**: Exposes 24+ diagnostic tools via Model Context Protocol
- **AI Agents**: LangGraph-based agents for security monitoring
- **LLM**: Llama-4-Scout via LlamaStack for intelligent analysis

## 📂 Project Structure

```
linux-network/
├── conversational-agent/     # Interactive Q&A agent
│   ├── src/
│   │   ├── agent.py          # ReAct agent builder
│   │   ├── config.py         # Config loader
│   │   └── mcp_tools.py      # MCP client
│   ├── config.yaml           # ✨ All prompts configurable here
│   ├── langgraph.json        # LangGraph dev config
│   └── pyproject.toml        # Dependencies
│
├── ambient-agent/            # Autonomous monitoring agent
│   ├── src/
│   │   ├── agent.py          # State machine
│   │   ├── nodes.py          # LangGraph nodes
│   │   ├── state.py          # State definition
│   │   ├── config.py         # Config + prompt loader
│   │   └── mcp_client.py     # MCP client
│   ├── config.yaml           # ✨ All prompts configurable here
│   ├── langgraph.json        # LangGraph dev config
│   └── pyproject.toml        # Dependencies
│
└── README.md                 # This file
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+** (required for `langgraph-cli[inmem]`)
- **SSH access** to target RHEL system
- **MCP Server** deployed and accessible
- **LlamaStack** endpoint for LLM access

### 1. Conversational Agent (Interactive)

Perfect for security investigations and ad-hoc queries.

```bash
cd conversational-agent

# Create virtual environment with Python 3.11+
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -U "langgraph-cli[inmem]"
pip install -e .

# Start LangGraph dev server
langgraph dev
```

Open: http://127.0.0.1:2024 or use [LangSmith Studio](https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024)

**Example queries:**
- "Show me network events from the last 10 minutes"
- "Check for network anomalies"
- "What processes are listening on network ports?"
- "Analyze network behavior and detect security threats"

### 2. Ambient Agent (Autonomous)

Runs continuously in the background, monitoring for threats.

```bash
cd ambient-agent

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e .

# Start monitoring (runs every 5 minutes)
python -m src

# Or use LangGraph dev for testing
langgraph dev
```

## ⚙️ Configuration

### Both agents use `config.yaml` for all configuration (NO hardcoded values!)

#### Conversational Agent Config

```yaml
# conversational-agent/config.yaml

mcp:
  endpoint: "https://your-mcp-server.com/mcp"
  
target:
  host: "your-rhel-server.com"
  username: "student"

llm:
  provider: "openai"
  base_url: "https://your-llm-endpoint/v1"
  model: "llama-4-scout-17b-16e-w4a16"
  temperature: 0.1
  max_tokens: 2000

# System prompt - fully customizable!
prompt:
  system: |
    You are a network security assistant...
    [Customize the agent's behavior here]
```

#### Ambient Agent Config

```yaml
# ambient-agent/config.yaml

agent:
  monitoring_interval: 300  # 5 minutes
  analysis_window: 10       # Last 10 minutes
  critical_threshold: "HIGH"

# Multiple prompts for different analysis tasks
prompts:
  anomaly_analysis:
    system: |
      You are a cybersecurity expert...
    user_template: |
      Analyze these anomalies: {anomalies_text}
      
  process_investigation:
    system: |
      You are a security analyst...
    user_template: |
      Investigate this process: {process_data}
```

**✨ Key Feature: All prompts are in YAML files, not hardcoded!**

## 🔧 Available MCP Tools

Both agents have access to 24+ MCP tools:

### Historical Analysis (Requires eBPF Log File)
- `get_network_events_history` - Retrieve past network events
- `detect_network_anomalies` - Pattern-based anomaly detection
- `analyze_process_network_behavior` - Deep process analysis
- `get_network_event_stats` - Aggregated statistics

### Real-Time Diagnostics
- `get_network_connections` - Current active connections
- `get_listening_ports` - Open ports
- `get_processes` - Running processes
- `get_system_info` - System details
- `get_service_status` - Service states
- `get_journal_logs` - System logs
- And 14 more...

## 🤖 Agent Comparison

| Feature | Conversational Agent | Ambient Agent |
|---------|---------------------|---------------|
| **Type** | Built-in ReAct | Custom State Machine |
| **Purpose** | Interactive Q&A | Autonomous Monitoring |
| **Trigger** | User questions | Timer (5 min) |
| **LLM Calls** | Per query | When anomalies detected |
| **Tools** | All 24+ tools | Focused subset |
| **Output** | Chat responses | Alerts + Reports |
| **Use Case** | Investigation | Continuous monitoring |
| **Deployment** | LangGraph Studio | Background service |

## 🔐 SSH Authentication Setup

The MCP server needs SSH access to the target system:

```bash
# 1. Extract MCP server's public key (from OpenShift secret)
oc get secret linux-mcp-ssh-keys -n rhel-mcp -o jsonpath='{.data.id_rsa}' | base64 -d > /tmp/mcp_key
ssh-keygen -y -f /tmp/mcp_key > /tmp/mcp_key.pub

# 2. Add to target system
ssh student@your-target-host "cat >> ~/.ssh/authorized_keys" < /tmp/mcp_key.pub

# 3. Restart MCP server
oc rollout restart deployment linux-mcp-server -n rhel-mcp

# 4. Clean up
rm /tmp/mcp_key*
```

## 📊 Testing

### Conversational Agent
```bash
cd conversational-agent
source .venv/bin/activate
python test_agent.py
```

### Ambient Agent
```bash
cd ambient-agent
source .venv/bin/activate

# Test individual components
python test_config.py
python test_mcp.py
python test_llm.py
python test_graph.py
```

## 🎭 Key Features

### ✨ Configurable Prompts
- All agent instructions in YAML files
- No hardcoded prompts in code
- Easy to customize without code changes
- Template variables for dynamic content

### 🧠 Intelligent Analysis
- LLM-powered security assessment
- Context-aware recommendations
- Severity classification
- Root cause analysis

### 🔄 ReAct Pattern (Conversational)
- Think → Act → Observe loop
- Autonomous tool selection
- Multi-step reasoning
- Self-correcting

### 🔁 State Machine (Ambient)
- Monitor → Analyze → Investigate → Alert
- Baseline learning
- False positive reduction
- Continuous improvement

## 📖 Documentation

- [Conversational Agent README](./conversational-agent/README.md)
- [Ambient Agent README](./ambient-agent/README.md)
- [MCP Server Documentation](https://github.com/raghurambanda/linux-mcp-server)

## 🛠️ Development

### Requirements
- Python 3.11+ (for LangGraph in-memory server)
- OpenShift CLI (`oc`) for deployments
- SSH access to target systems

### Running Locally
Both agents support `langgraph dev` for local development with hot-reload and LangGraph Studio UI.

### Environment Variables
Both agents support environment variable overrides:
- `LLAMASTACK_BASE_URL`
- `LLAMASTACK_MODEL`
- `MCP_ENDPOINT`
- `TARGET_HOST`
- `TARGET_USERNAME`

## 🚦 Status

| Component | Status |
|-----------|--------|
| Conversational Agent |  **Working** |
| Ambient Agent |  **Working** |
| MCP Server |  **Deployed** |
| eBPF Agent |  **Running** |
| SSH Auth |  **Configured** |
| Config-based Prompts |  **Implemented** |

## 📝 License

Apache 2.0

## 🙏 Acknowledgments

- **LangGraph**: Agent orchestration framework
- **Model Context Protocol**: Tool integration standard
- **LlamaStack**: LLM serving infrastructure
- **eBPF**: Network monitoring technology

---

**Built with ❤️ for intelligent network security monitoring**
