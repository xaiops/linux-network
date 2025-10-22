# Conversational Network Security Agent

**Status**:  **WORKING**

A conversational ReAct agent that answers security questions by calling MCP tools.

##  What Works

1. **Agent builds successfully** - Loads 24 MCP tools
2. **LLM integration** - Uses Llama-4-Scout via LlamaStack  
3. **Tool calling** - Agent decides which tools to call based on questions
4. **ReAct pattern** - Think → Act → Observe loop working
5. **MCP integration** - Proper use of `langchain-mcp-adapters`

## 📊 Test Results

```bash
$ python test_agent.py

 Agent built successfully!
 Loaded 24 MCP tools
 LLM responding to questions
 Calling MCP tools (get_system_info, get_journal_logs, get_network_connections, etc.)
```

## 💬 Example Conversations

**You**: "What network activity has happened in the last 5 minutes?"  
**Agent**: *Calls get_network_event_stats tool* → Provides statistics

**You**: "Are there any security anomalies?"  
**Agent**: *Calls detect_network_anomalies tool* → Reports findings

**You**: "Show me network statistics"  
**Agent**: *Calls get_network_connections + get_listening_ports* → Shows data

## 🎯 Usage

### Test Locally
```bash
cd /Users/raghurambanda/playground/linux-network/conversational-agent
python test_agent.py
```

### Run with LangGraph Dev
```bash
langgraph dev
# Open http://localhost:8123
# Test interactively in LangGraph Studio
```

## 🏗️ Architecture

```
User Question
    ↓
ReAct Agent (Llama-4-Scout)
    ↓
Decides which MCP tools to call
    ↓
MCP Server (OpenShift)
    ↓
Executes on RHEL Server
    ↓
Returns Results
    ↓
Agent analyzes and responds
```

## 🔧 Components

- **LLM**: Llama-4-Scout-17B via LlamaStack
- **Tools**: 24 MCP tools from linux-mcp-server
- **Pattern**: ReAct (Reason + Act) 
- **Framework**: LangGraph `create_react_agent`
- **Transport**: Streamable HTTP to MCP server

## 📦 Available Tools

All 24 MCP tools including:
- `get_network_events_history`
- `detect_network_anomalies`
- `analyze_process_network_behavior`
- `get_network_event_stats`
- `list_processes`, `get_process_info`
- `list_services`, `get_service_status`
- And 17 more...

## ⚠️ Known Issues

1. **SSH access** - MCP tools need SSH to bastion server (works from deployed environment)
2. **Tool name hallucination** - LLM sometimes invents tool names (e.g., `get_network_anomalies` instead of `detect_network_anomalies`) - this is normal LLM behavior

## 🚀 Next Steps

1. Deploy to environment with SSH access to bastion
2. Add chat interface (web UI or CLI)
3. Add memory/conversation history
4. Fine-tune system prompt
5. Add cron-based scheduling if needed

## 📝 Configuration

Edit `config.yaml` to configure:
- MCP endpoint
- LLM settings
- Target RHEL server

## License

Apache 2.0

