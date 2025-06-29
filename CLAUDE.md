# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the **Alpaca MCP Gold Standard** - a comprehensive refactoring of the original Alpaca MCP server implementing all best practice patterns documented in the parent repository's MD files. This serves as the definitive reference implementation for professional MCP development.

## Development Commands

```bash
# Setup environment
uv sync

# Run server
uv run python main.py

# Run with debug logging
LOG_LEVEL=DEBUG uv run python main.py

# Testing (Real API Integration)
uv run python -m pytest tests/ -v          # 91 tests using real Alpaca API
uv run python -m pytest tests/test_account_tools.py -v
uv run python -m pytest tests/ -v --cov=src

# All tests use real Alpaca API in paper trading mode
# No mocks - maximum confidence in actual functionality

# Code quality
uv run black src/ tests/
uv run ruff check src/ tests/
uv run mypy src/
```

## Gold Standard Architecture

### Key Patterns Implemented
1. **Adaptive Discovery**: Auto-classification of stocks, positions, and entities with role assignment
2. **Resource Mirror Pattern**: Universal MCP client compatibility through dual access methods
3. **Context-Aware Prompts**: Conversation starters that adapt to actual portfolio data
4. **Comprehensive State Management**: Centralized tracking with memory monitoring
5. **Consistent Error Handling**: Standardized response formats across all components
6. **Safe Execution**: Input validation, error isolation, and graceful degradation

### Directory Structure
```
src/mcp_server/
├── config/           # Environment-based configuration management
├── models/           # Data schemas, state management, Alpaca clients
├── tools/            # Categorized MCP tools with adaptive insights
├── resources/        # URI-based data access with trading:// scheme
├── prompts/          # Context-aware conversation starters
└── server.py         # Central registration point for all components

tests/
├── conftest.py       # State management fixtures and test utilities
├── test_account_tools.py      # Account management testing
├── test_resources.py          # Resource access testing
├── test_resource_mirrors.py   # Mirror consistency testing
├── test_state_management.py   # State and memory testing
└── test_integration.py        # Complete workflow testing

ai_docs/             # AI-optimized development documentation
specs/               # Technical architecture specifications
```

## Core Implementation Patterns

### Tool Pattern Template
```python
async def your_tool_name(param: str, optional_param: Optional[float] = None) -> dict:
    """Clear description for AI understanding."""
    try:
        # Input validation
        if not param:
            return {"status": "error", "message": "Parameter cannot be empty"}
        
        # Get client and perform operation
        client = AlpacaClientManager.get_trading_client()
        result = client.operation(param, optional_param)
        
        # Track entity with adaptive insights
        entity_info = EntityInfo.from_stock_data(param, result_data)
        StateManager.add_symbol(param, entity_info)
        
        return {
            "status": "success",
            "data": process_result(result),
            "metadata": {
                "operation": "your_tool_name",
                "entity_insights": entity_info.characteristics
            }
        }
    except Exception as e:
        logger.error(f"Error in tool: {e}")
        return {
            "status": "error",
            "message": f"Operation failed: {str(e)}",
            "error_type": type(e).__name__
        }
```

### Resource + Mirror Pattern
```python
# Resource function
async def get_trading_resource(uri: str) -> dict:
    """trading://category/resource URI handler"""
    # Parse URI and route to appropriate handler
    # Return {"resource_data": data} or {"error": "message"}

# Mirror tool (zero maintenance overhead)
async def resource_mirror_tool() -> dict:
    """Tool mirror for universal compatibility."""
    try:
        result = await get_trading_resource("trading://category/resource")
        if "error" in result:
            return {"status": "error", "message": result["error"]}
        return {
            "status": "success", 
            "data": result["resource_data"],
            "metadata": {"source": "trading://category/resource"}
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
```

### State Management Pattern
```python
# Always use StateManager for persistence
portfolio = StateManager.get_portfolio()
StateManager.set_portfolio(new_portfolio)
StateManager.add_symbol(symbol, entity_info)

# Memory tracking
memory_usage = StateManager.get_memory_usage()

# Essential for testing
StateManager.clear_all()  # In test fixtures
```

## Available Capabilities

### Account & Portfolio Management
- `get_account_info_tool()` - Account status with portfolio insights
- `get_positions_tool()` - Holdings with adaptive role classification
- `get_portfolio_summary_tool()` - Comprehensive analysis with suggestions

### Market Data & Research
- `get_stock_quote_tool(symbol)` - Real-time quotes with spread analysis
- `get_stock_snapshot_tool(symbol)` - Complete market data with volatility insights
- `get_historical_bars_tool(symbol, timeframe)` - Price history with statistics

### Order Management
- `place_market_order_tool(symbol, side, quantity)` - Immediate execution
- `place_limit_order_tool(symbol, side, quantity, price)` - Price targeting
- `place_stop_loss_order_tool(symbol, side, quantity, stop_price)` - Risk management

### Resource Access (Universal Compatibility)
- Resources: `trading://account/info`, `trading://portfolio/summary`, etc.
- Mirror Tools: `resource_account_info_tool()`, `resource_portfolio_summary_tool()`, etc.

### Context-Aware Prompts
- `portfolio_first_look_prompt()` - Adaptive portfolio exploration
- `trading_strategy_workshop_prompt(focus)` - Strategy-specific guidance
- `market_analysis_session_prompt()` - Research framework

## Testing Standards (Real API Integration)

Every new feature requires:
- **Success case testing** with real Alpaca API calls
- **Error case testing** with actual API error scenarios
- **State management testing** verifying memory usage
- **Resource-mirror consistency** for new resource pairs
- **Integration testing** for complete workflows
- **Paper trading safety** ensuring all tests run in safe environment

### Test Fixture Usage (Real API)
```python
@pytest.mark.asyncio
async def test_your_feature(real_api_test):
    # Uses real Alpaca API in paper trading mode
    result = await your_tool_function("AAPL")
    assert_success_response(result)  # Helper function
    
    # Verify state changes with real data
    entity = StateManager.get_symbol("AAPL")
    assert entity is not None
    
    # Tests automatically handle varying real API responses
    # No hardcoded values - flexible assertions for real data
```

## Configuration Management

### Environment Variables
```bash
# Required Alpaca credentials
ALPACA_API_KEY=your_api_key
ALPACA_SECRET_KEY=your_secret_key
ALPACA_PAPER_TRADE=True

# Optional MCP server config
MCP_SERVER_NAME=alpaca-trading-gold
LOG_LEVEL=INFO
```

### Client Configuration
```json
{
  "mcpServers": {
    "alpaca-trading-gold": {
      "command": "/path/to/uv",
      "args": ["--directory", "/absolute/path/to/this/project", "run", "python", "main.py"],
      "env": {"LOG_LEVEL": "INFO"}
    }
  }
}
```

## Key Differentiators from Original

### 🔧 **Modular Architecture**
- Tools organized by category instead of single monolithic file
- Clear separation of concerns with dedicated modules
- Centralized client and state management

### 🔄 **Universal Compatibility**
- Resource mirror pattern ensures all MCP clients work
- Dual access to same data through resources or tools
- Zero maintenance overhead for compatibility layer

### 🧠 **Adaptive Intelligence**
- Automatic entity classification with role assignment
- Portfolio suggestions based on actual composition
- Context-aware prompts referencing real data

### 🏗️ **Production Ready**
- Comprehensive error handling with consistent formats
- Memory management with usage tracking
- Health monitoring for Alpaca API connections
- Docker support with environment configuration

### 🧪 **Testing Excellence**
- 91 tests with 100% pass rate using real Alpaca API
- Integration tests for complete workflows with actual data
- Real Alpaca API calls in paper trading environment
- Automatic state cleanup between tests
- No mocks - maximum confidence in production readiness

### 📚 **Documentation Excellence**
- AI-optimized development guides
- Technical architecture specifications
- Comprehensive usage examples
- Pattern templates for extension

## Performance Considerations

- **Client Management**: Singleton pattern for Alpaca API clients
- **Memory Efficiency**: Bounded entity storage with cleanup mechanisms
- **Async Operations**: Non-blocking execution throughout
- **State Optimization**: Selective data storage for performance

This gold standard implementation demonstrates how MCP servers should be architected for professional deployment, optimal Claude Code integration, and long-term maintainability.