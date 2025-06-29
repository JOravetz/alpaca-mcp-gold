# AI Development Guide - Alpaca MCP Gold Standard

This document provides AI-optimized guidance for developing with the Alpaca MCP server.

## Quick Start for AI Assistants

When working with this Alpaca MCP project, Claude should:

1. **Understand the Gold Standard Architecture**: This server implements all best practice patterns
2. **Follow Established Patterns**: Use the modular tool organization and consistent error handling
3. **Leverage State Management**: Utilize the adaptive portfolio and entity tracking
4. **Test Everything**: Comprehensive test coverage with state cleanup is essential

## Common AI Tasks

### Adding a New Trading Tool
```python
# 1. Create the tool function in appropriate category file
# File: src/mcp_server/tools/[category]_tools.py

async def new_trading_tool(symbol: str, additional_param: float) -> dict:
    """Clear description for AI to understand when to use this tool."""
    try:
        # Input validation
        if not symbol:
            return {"status": "error", "message": "Symbol parameter cannot be empty"}
        
        # Get Alpaca client
        client = AlpacaClientManager.get_trading_client()
        
        # Perform operation
        result = client.some_operation(symbol, additional_param)
        
        # Track entity if applicable
        entity_info = EntityInfo.from_stock_data(symbol, result_data)
        StateManager.add_symbol(symbol, entity_info)
        
        return {
            "status": "success",
            "data": process_result(result),
            "metadata": {
                "operation": "new_trading_tool",
                "entity_insights": entity_info.characteristics
            }
        }
        
    except Exception as e:
        logger.error(f"Error in new trading tool: {e}")
        return {
            "status": "error",
            "message": f"Operation failed: {str(e)}",
            "error_type": type(e).__name__
        }

# 2. Register in server.py
@mcp.tool()
async def new_trading_tool_registered(symbol: str, additional_param: float) -> dict:
    """Tool description for MCP registration."""
    return await new_trading_tool(symbol, additional_param)

# 3. Add comprehensive tests
class TestNewTradingTool:
    @pytest.mark.asyncio
    async def test_success_case(self, mock_alpaca_clients):
        result = await new_trading_tool("AAPL", 100.0)
        assert result["status"] == "success"
        
    @pytest.mark.asyncio
    async def test_error_handling(self):
        result = await new_trading_tool("", 100.0)
        assert result["status"] == "error"
```

### Adding a New Resource
```python
# 1. Add to trading_resources.py
async def _handle_new_category_resource(resource: str) -> Dict[str, Any]:
    """Handle new category resources."""
    if resource == "new_data":
        data = fetch_new_data()
        return {"resource_data": data}
    else:
        return {"error": f"Unknown new category resource: {resource}"}

# 2. Add to main resource handler
# In get_trading_resource function:
elif category == "new_category":
    return await _handle_new_category_resource(resource)

# 3. Create resource mirror tool
async def resource_new_category_data() -> Dict[str, Any]:
    """Tool mirror of trading://new_category/data resource."""
    try:
        result = await get_trading_resource("trading://new_category/data")
        if "error" in result:
            return {"status": "error", "message": result["error"]}
        return {
            "status": "success",
            "data": result["resource_data"],
            "metadata": {"source": "trading://new_category/data"}
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
```

## AI Code Generation Guidelines

### Tool Development Standards
- **Always include type hints** for all parameters and return values
- **Provide clear docstrings** that help AI understand when to use the tool
- **Use consistent error handling** with status/message format
- **Return structured data** with metadata for insights
- **Track entities** when dealing with symbols or trading data

### Resource Development Standards
- **Support the trading:// URI scheme** with clear path structure
- **Return data in consistent format** (resource_data or error)
- **Handle URI parsing errors** gracefully with helpful messages
- **Create corresponding mirror tools** for universal compatibility

### State Management Guidelines
- **Use StateManager** for all portfolio and symbol tracking
- **Create EntityInfo objects** for adaptive insights
- **Update characteristics** when new data becomes available
- **Clear state in tests** using the autouse fixture

### Testing Requirements
- **Test both success and failure scenarios** for every function
- **Use async patterns** with pytest-asyncio
- **Mock Alpaca clients** using provided fixtures
- **Verify state changes** when applicable
- **Test resource-mirror consistency** for new resource pairs

## Performance Considerations

- **Client Management**: Use AlpacaClientManager for singleton client access
- **Memory Tracking**: StateManager provides memory usage monitoring
- **Entity Caching**: Symbols and entities are cached in memory for performance
- **Async Operations**: All tools are async for non-blocking execution

## Security Patterns

- **Input Validation**: All tools validate required parameters
- **Error Sanitization**: Sensitive information is not exposed in error messages
- **Client Isolation**: Alpaca clients are managed centrally with health checks
- **Paper Trading**: Default configuration uses paper trading for safety

## Integration with Claude Code

This project is optimized for Claude Code development:

### Command Structure
```bash
# Setup and testing
uv sync                                    # Install dependencies
uv run python main.py                     # Start server
LOG_LEVEL=DEBUG uv run python main.py     # Debug mode
uv run python -m pytest tests/ -v         # Run all tests
uv run python -m pytest tests/test_account_tools.py -v  # Specific tests
```

### Architecture Benefits
- **Modular organization** makes it easy for AI to understand component boundaries
- **Consistent patterns** across all tools/resources reduce learning overhead
- **Comprehensive testing** gives AI confidence to make modifications
- **Clear documentation** provides context for complex operations

### Gold Standard Features
- **Adaptive Discovery**: Entities automatically classified based on characteristics
- **Resource Mirrors**: Universal compatibility across all MCP clients
- **Context-Aware Prompts**: Conversation starters adapt to actual portfolio data
- **State Management**: Persistent tracking of portfolio and symbol information
- **Error Handling**: Consistent format across all components

## Common Development Patterns

### Entity Classification
```python
# Stocks are automatically classified based on characteristics
entity = EntityInfo.from_stock_data(symbol, {
    "price_change_percent": 5.0,  # High change = volatile
    "volume": 50000000,           # High volume = liquid
    "market_cap": 100000000000    # Large cap = stable
})
# Results in appropriate suggested_role assignment
```

### Portfolio Analysis
```python
# Portfolio automatically generates insights
portfolio = TradingPortfolioSchema.from_account_data(account_data)
# Analyzes cash allocation, suggests operations
# Updates suggestions when entities are added
```

### Memory Management
```python
# Always clear state in tests
@pytest.fixture(autouse=True)
def clear_state():
    StateManager.clear_all()
    yield
    StateManager.clear_all()

# Check memory usage
memory_stats = StateManager.get_memory_usage()
```

## Error Handling Best Practices

### Tool Errors
```python
return {
    "status": "error",
    "message": "Human-readable description",
    "error_type": "ExceptionClassName"
}
```

### Resource Errors
```python
return {
    "error": "Failed to get resource: specific reason"
}
```

### Exception Handling
```python
try:
    # Operation
    pass
except ValueError as e:
    # Specific handling for expected errors
    pass
except Exception as e:
    # General handling with logging
    logger.error(f"Unexpected error: {e}")
    return error_response
```

This guide ensures that AI assistants can effectively develop with and extend the Alpaca MCP gold standard implementation.