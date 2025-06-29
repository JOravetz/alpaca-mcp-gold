## RUN
eza . --tree --level 5 --git-ignore

## READ
@README.md
@CLAUDE.md

## Alpaca MCP Gold Standard Structure

### Core Architecture
`src/mcp_server/` - Production-ready MCP server with 50+ tools
- `config/` - Environment-based configuration management
- `models/` - Alpaca clients, state management, entity schemas
- `tools/` - Categorized tools by function:
  - `account_tools.py` - Account management (4 tools)
  - `market_data_tools.py` - Market data access (4 tools)
  - `order_management_tools.py` - Order operations (5 tools)
  - `custom_strategy_execution.py` - Safe subprocess execution (3 tools)
  - `advanced_analysis_tools.py` - Portfolio health & correlation (2 tools)
  - `execute_custom_analytics_code_tool.py` - Universal dataset analytics (2 tools)
  - `resource_mirror_tools.py` - Universal compatibility (11 tools)
- `resources/` - URI-based trading:// resource handlers
- `prompts/` - Context-aware conversation starters (4 prompts)
- `server.py` - FastMCP registration point (31 total tools)

### Testing Excellence
`tests/` - Comprehensive test coverage
- `conftest.py` - Mock Alpaca API fixtures & state cleanup
- `test_account_tools.py` - Account operations testing
- `test_market_data_tools.py` - Market data testing
- `test_order_management_tools.py` - Order operations testing
- `test_resources.py` - Resource URI testing
- `test_resource_mirrors.py` - Mirror consistency validation
- `test_state_management.py` - Memory & state testing
- `test_integration.py` - Full workflow testing

### Documentation
`specs/` - Architectural specifications:
- `architecture_overview.md` - Gold standard patterns
- `custom_analytic_code.md` - Subprocess isolation design
- `poc_init_generic.md` - Universal dataset agnosticism
- `resource_workaround.md` - Resource mirror pattern

`ai_docs/` - AI-optimized reference:
- `alpaca_py_sdk_reference.md` - Alpaca SDK documentation
- `mcp_server_sdk_reference.md` - MCP patterns guide
- `README.md` - Documentation index

### Key Patterns Implemented
1. **Adaptive Discovery** - Auto-classification with role assignment
2. **Resource Mirror Pattern** - 11 mirror tools for compatibility
3. **Context-Aware Prompts** - 4 prompts with portfolio data
4. **Safe Code Execution** - 4 subprocess isolation tools
5. **Advanced Analysis** - Portfolio health & correlation
6. **Universal Analytics** - Dataset-agnostic patterns
7. **State Management** - Memory tracking & cleanup

### Quick Validation Commands
```bash
# Count total tools
grep -r "@mcp.tool()" src/mcp_server/server.py | wc -l  # Should be 31

# Run tests with coverage
uv run pytest tests/ -v --cov=src

# Check memory usage
uv run python -c "from src.mcp_server.models.schemas import StateManager; print(StateManager.get_memory_usage())"

# Validate tool registration
uv run python -c "from src.mcp_server.server import mcp; print(f'{len([attr for attr in dir(mcp) if attr.endswith(\"_tool\")])} tools registered')"
```