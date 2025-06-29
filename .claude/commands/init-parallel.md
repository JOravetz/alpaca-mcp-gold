# Initialize parallel git worktree directories

## Variables
FEATURE_NAME: $ARGUMENTS
NUMBER_OF_PARALLEL_WORKTREES: $ARGUMENTS

## Execute these commands
> Execute the loop in parallel with the Batch and Task tool

- create a new dir `trees/`
- for i in NUMBER_OF_PARALLEL_WORKTREES
  - RUN `git worktree add -b FEATURE_NAME-i ./trees/FEATURE_NAME-i`
  - RUN `cd ./trees/FEATURE_NAME-i/`, `uv sync`
  - RUN `cd trees/FEATURE_NAME-i`, `git ls-files` to validate
- RUN `git worktree list` to verify all trees were created properly

## Alpaca MCP Gold Standard Setup

After creating worktrees, perform additional setup for each:

- for i in NUMBER_OF_PARALLEL_WORKTREES
  - RUN `cd ./trees/FEATURE_NAME-i/`
  - Create .env file: `echo "ALPACA_API_KEY=test_key\nALPACA_SECRET_KEY=test_secret\nALPACA_PAPER_TRADE=True\nLOG_LEVEL=DEBUG" > .env`
  - Validate client setup: `uv run python -c "from src.mcp_server.models.alpaca_clients import AlpacaClientManager; print('✅ Alpaca client configured')"`
  - Check state manager: `uv run python -c "from src.mcp_server.models.schemas import StateManager; print(f'✅ StateManager ready, memory: {StateManager.get_memory_usage()}')"`
  - Validate MCP tools: `uv run python -c "from src.mcp_server.server import mcp; print(f'✅ MCP server configured with {len([t for t in dir(mcp) if t.endswith(\"_tool\")])} tools')"`
  - Quick test run: `uv run pytest tests/test_state_management.py -v` to ensure environment is ready

## Validation Checklist

After initialization, verify each worktree has:
- [ ] Dependencies installed (uv sync completed)
- [ ] .env file with Alpaca credentials
- [ ] StateManager accessible and functioning
- [ ] All 50+ MCP tools registered
- [ ] Tests passing for state management
- [ ] Proper git branch structure