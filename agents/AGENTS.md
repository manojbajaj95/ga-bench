# AGENT IMPLEMENTATION GUIDE

## OVERVIEW
Contains agent implementations. Each agent adapts a framework (LangChain, Claude SDK) to the `ga-bench` protocol.

## STRUCTURE
```
agents/
├── base.py                 # Protocol: Agent, AgentResult
├── types.py                # Data models
├── langchain/              # LangChain-based agents
│   ├── react.py            # ReAct agent (MCP-aware)
│   └── deepagent.py        # Deep agent implementation
└── claude_agent_sdk/       # Claude SDK agents
```

## IMPLEMENTATION CHECKLIST
1. **Interface**: Implement `async def run(task: Task, system_prompt: str) -> AgentResult`.
2. **Factory**: Expose `async def get_agent(mcp_server: dict | None) -> Agent`.
3. **MCP Support**: Use `mcp_server` dict (transport config) to connect tools.
4. **Model**: Read `AGENT_MODEL` from env (default to `anthropic:claude...`).

## CRITICAL PATTERNS
- **Gemini Compatibility**: MUST handle `content` as list of blocks.
  ```python
  # Example handling
  content = msg.content
  if isinstance(content, list):
      text = "".join(b["text"] for b in content if b["type"] == "text")
  ```
- **Error Handling**: Catch tool errors and return them to the model, don't crash.
- **Tracing**: Use `loguru` to trace steps (automatically captured in `run.py`).

## ANTI-PATTERNS
- **NO Global State**: Agents are instantiated per run or per task.
- **NO Hardcoded Models**: Always respect `AGENT_MODEL`.
