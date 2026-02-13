# Microsoft Agent Framework — CultureBridge AI Orchestrator

This package contains the agent orchestration layer for CultureBridge AI, built on Microsoft Agent Framework patterns.

## Architecture

The orchestrator implements a **sequential pipeline** pattern:

```
AdaptRequest
    → Cultural Intelligence Agent
        → UX Adaptation Agent
            → Copy & Framing Agent
                → Compliance & Bias Auditor Agent
                    → Experimentation Agent
                        → VariantSpec
```

## Agent Definitions

Each agent follows the Microsoft Agent Framework contract:
- **System prompt**: Defines role, rules, and output format
- **Structured tool calls**: Agents can invoke data tools (cultural priors, mapping rules)
- **JSON output**: Every agent returns machine-readable JSON with a `rationale` field
- **Correlation IDs**: All calls are traced for observability

## Agent Registration

Agents are registered with the orchestrator in `apps/api/orchestrator.py`. Each agent:
1. Receives a typed input from the orchestrator
2. Processes using LLM + data tools
3. Returns structured JSON output
4. Passes output to the next agent in the pipeline

## Local Development

The agent implementations are in `apps/api/agents/`. Run from the API directory:

```bash
cd apps/api
python -m pytest ../tests/ -v
```
