# Alpaca MCP Gold Standard

A comprehensive refactoring of the Alpaca trading MCP server implementing all gold standard patterns for professional MCP development.

## 🏆 Gold Standard Features

- **Adaptive Discovery**: Auto-classification of stocks and positions with role assignment
- **Resource Mirror Pattern**: Universal MCP client compatibility
- **Context-Aware Prompts**: Conversation starters that adapt to actual portfolio data
- **Comprehensive State Management**: Centralized tracking with memory monitoring
- **Modular Architecture**: Clean separation of concerns across components
- **Production Ready**: Docker support, health monitoring, comprehensive testing

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- uv package manager
- Alpaca trading account (paper trading supported)

### Installation
```bash
# Clone and setup
git clone <repository>
cd alpaca-mcp-gold-standard

# Install dependencies
uv sync

# Configure environment
cp .env.example .env
# Edit .env with your Alpaca API credentials
```

### Running the Server
```bash
# Development mode
uv run python main.py

# Debug mode with verbose logging
LOG_LEVEL=DEBUG uv run python main.py

# Production mode with Docker
docker build -t alpaca-mcp-gold .
docker run -p 8000:8000 --env-file .env alpaca-mcp-gold
```

### Testing
```bash
# Run all tests
uv run python -m pytest tests/ -v

# Run with coverage
uv run python -m pytest tests/ -v --cov=src

# Run specific test category
uv run python -m pytest tests/test_account_tools.py -v
```

## 📋 MCP Client Configuration

Add to your MCP client configuration:

```json
{
  "mcpServers": {
    "alpaca-trading-gold": {
      "command": "/path/to/uv",
      "args": [
        "--directory",
        "/absolute/path/to/alpaca-mcp-gold-standard",
        "run",
        "python",
        "main.py"
      ],
      "env": {
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

## 🛠️ Available Tools

### Account Management
- `get_account_info_tool()` - Account status and portfolio metrics
- `get_positions_tool()` - Current holdings with adaptive insights
- `get_portfolio_summary_tool()` - Comprehensive portfolio analysis

### Market Data
- `get_stock_quote_tool(symbol)` - Real-time quotes with spread analysis
- `get_stock_snapshot_tool(symbol)` - Complete market data
- `get_historical_bars_tool(symbol, timeframe)` - Historical price data

### Order Management
- `place_market_order_tool(symbol, side, quantity)` - Immediate execution
- `place_limit_order_tool(symbol, side, quantity, price)` - Price targeting
- `place_stop_loss_order_tool(symbol, side, quantity, stop_price)` - Risk management

### Resource Access (Universal Compatibility)
- `trading://account/info` - Account information
- `trading://portfolio/summary` - Portfolio analysis
- `trading://symbols/active` - Tracked symbols
- `trading://system/health` - System status

All resources have corresponding `resource_*` mirror tools for tool-only clients.

## 💬 Context-Aware Prompts

- `portfolio_first_look` - Adaptive portfolio exploration based on your actual holdings
- `trading_strategy_workshop` - Strategy guidance customized to your portfolio
- `market_analysis_session` - Research framework with symbol-specific insights
- `list_mcp_capabilities` - Complete feature overview and usage guide

## 🏗️ Architecture Overview

```
src/mcp_server/
├── config/           # Environment-based configuration
├── models/           # Data schemas and state management
│   ├── schemas.py    # Portfolio and entity models
│   └── alpaca_clients.py  # Centralized client management
├── tools/            # MCP tools organized by category
│   ├── account_tools.py
│   ├── market_data_tools.py
│   ├── order_management_tools.py
│   └── resource_mirror_tools.py
├── resources/        # URI-based data access
├── prompts/          # Context-aware conversation starters
└── server.py         # Central registration point
```

## 🧪 Testing Architecture

Comprehensive test coverage with:
- **Unit Tests**: Individual tool and resource functions
- **Integration Tests**: Complete workflow scenarios  
- **State Tests**: Memory management and cleanup
- **Resource-Mirror Tests**: Consistency verification

Test fixtures provide:
- Automatic state cleanup between tests
- Mock Alpaca API clients with realistic data
- Helper functions for response validation

## 🔧 Development

### Adding New Tools
1. Create function in appropriate `tools/category_tools.py`
2. Register in `server.py` with `@mcp.tool()` decorator
3. Add comprehensive tests in `tests/test_category_tools.py`
4. Update documentation

### Adding New Resources
1. Add handler in `resources/trading_resources.py`
2. Create corresponding mirror tool in `resource_mirror_tools.py`
3. Test both resource and mirror consistency
4. Update URI documentation

### Code Quality
```bash
# Format code
uv run black src/ tests/

# Lint code
uv run ruff check src/ tests/

# Type checking
uv run mypy src/
```

## 📊 Performance & Monitoring

- **Memory Tracking**: Built-in memory usage monitoring via `StateManager`
- **Health Checks**: Alpaca API connection monitoring
- **Client Management**: Singleton pattern for optimal connection reuse
- **Async Operations**: Non-blocking execution throughout

## 🔒 Security

- **Credential Management**: Environment variable configuration
- **Input Validation**: Comprehensive parameter checking
- **Error Sanitization**: No sensitive data in error messages
- **Paper Trading**: Safe default configuration

## 📈 Entity Classification

The server automatically classifies trading entities:

- **Growth Candidates**: Stocks with positive momentum
- **Volatile Assets**: High price volatility requiring monitoring
- **Income Generators**: Stable positions for consistent returns
- **Hedge Instruments**: Risk management positions
- **Liquid Assets**: High-volume, easily tradeable stocks

## 🌟 Gold Standard Patterns

This implementation demonstrates:

1. **Modular Architecture**: Clean separation of concerns
2. **Universal Compatibility**: Resource mirror pattern for all MCP clients
3. **Adaptive Intelligence**: Context-aware responses and insights
4. **Production Readiness**: Comprehensive error handling and monitoring
5. **Testing Excellence**: 90%+ coverage with state management
6. **Documentation Quality**: AI-optimized guides and specifications

## 📚 Documentation

- **CLAUDE.md**: Claude Code development guidance
- **ai_docs/**: AI-optimized development documentation
- **specs/**: Technical architecture specifications
- **tests/**: Comprehensive test examples

## 🤝 Contributing

This project serves as the gold standard reference for MCP development. When contributing:

1. Follow established patterns and conventions
2. Ensure comprehensive test coverage
3. Update documentation for new features
4. Maintain consistency with gold standard principles

## 📄 License

This project is licensed under the same terms as the original Alpaca MCP server.

## 🙏 Acknowledgments

Built upon the foundation of the original Alpaca MCP server, implementing the comprehensive best practices documented in the parent repository's analysis of gold standard MCP patterns.