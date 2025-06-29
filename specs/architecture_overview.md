# Alpaca MCP Gold Standard - Architecture Overview

This document provides a comprehensive overview of the Alpaca MCP server architecture following gold standard patterns.

## Architectural Principles

### 1. Modular Organization
The server is organized into distinct modules with clear responsibilities:

```
src/mcp_server/
├── config/           # Configuration management
├── models/           # Data models and business logic
├── tools/            # MCP tools (functions AI can call)
├── resources/        # MCP resources (data endpoints)
├── prompts/          # MCP prompts (conversation starters)
└── server.py         # Central registration point
```

### 2. Gold Standard Patterns Implemented

#### Adaptive Discovery Pattern
- **DatasetSchema equivalent**: `TradingPortfolioSchema` with `EntityInfo`
- **Auto-discovery**: Stocks and positions automatically classified by characteristics
- **Role assignment**: Growth candidates, volatile assets, income generators, etc.
- **Dynamic insights**: Portfolio suggestions update based on composition

#### Resource Mirror Pattern
- **Universal compatibility**: Every resource has a corresponding tool
- **Zero maintenance**: Mirrors wrap existing functions without code duplication
- **Future-proof**: Easy to deprecate mirrors when client support improves
- **Consistent interface**: Same data through resources or tools

#### Context-Aware Prompts
- **Portfolio adaptation**: Prompts reference actual holdings and values
- **Strategy customization**: Guidance adapts to current portfolio composition
- **Actionable commands**: Specific tool suggestions based on available data
- **Business context**: Strategy workshops adapt to trading focus areas

#### Comprehensive State Management
- **Centralized storage**: `StateManager` handles all portfolio and symbol data
- **Memory tracking**: Built-in usage monitoring and cleanup
- **Entity persistence**: Symbols and characteristics maintained across calls
- **Test isolation**: Automatic state cleanup between tests

#### Safe Execution Patterns
- **Input validation**: All tools validate required parameters
- **Error isolation**: Exceptions don't propagate beyond tool boundaries
- **Graceful degradation**: Missing data doesn't break workflows
- **Client health monitoring**: Automatic health checks for Alpaca connections

## Component Architecture

### Configuration Layer
```python
# Hierarchical configuration with environment override
class Settings(BaseSettings):
    alpaca: AlpacaSettings
    mcp: MCPSettings
    
    # Validates credentials on startup
    # Supports .env files and environment variables
```

### Models Layer
```python
# Entity classification system
class EntityInfo(BaseModel):
    @classmethod
    def from_stock_data(cls, symbol: str, data: Dict) -> 'EntityInfo':
        # Auto-discovers characteristics and assigns roles
        
class TradingPortfolioSchema(BaseModel):
    @classmethod
    def from_account_data(cls, data: Dict) -> 'TradingPortfolioSchema':
        # Analyzes portfolio metrics and generates suggestions
        
class StateManager:
    # Centralized state with memory tracking
    # Thread-safe portfolio and symbol management
```

### Tools Layer
Organized by functional categories:

- **Account Tools**: Portfolio analysis with adaptive insights
- **Market Data Tools**: Real-time quotes with entity classification
- **Order Management Tools**: Trading operations with risk tracking
- **Resource Mirror Tools**: Universal compatibility layer

### Resources Layer
URI-based data access with comprehensive coverage:

```
trading://account/info           # Account information
trading://account/positions      # All positions
trading://portfolio/summary      # Portfolio analysis
trading://symbols/active         # Tracked symbols
trading://system/health          # System status
```

### Prompts Layer
Context-aware conversation starters:

- **Portfolio First Look**: Adapts to actual holdings and metrics
- **Strategy Workshop**: Customizes guidance by trading focus
- **Market Analysis**: References currently tracked symbols
- **Capability Overview**: Complete feature documentation

## Data Flow Architecture

### 1. Tool Execution Flow
```
Client Request → Tool Function → Alpaca API → Entity Classification → State Update → Response
```

### 2. Resource Access Flow
```
Resource URI → URI Parser → Category Handler → Data Retrieval → Resource Response
```

### 3. State Management Flow
```
API Data → Entity Creation → Characteristic Analysis → Role Assignment → State Storage
```

### 4. Adaptive Insights Flow
```
Portfolio State → Entity Analysis → Pattern Recognition → Suggestion Generation → Context-Aware Output
```

## Integration Patterns

### MCP Client Integration
The server supports all MCP client types through dual access patterns:

1. **Modern Clients**: Use resources via URI scheme
2. **Tool-Only Clients**: Use resource mirror tools
3. **Universal Support**: Identical data through both methods

### Alpaca API Integration
Centralized client management with health monitoring:

```python
class AlpacaClientManager:
    # Singleton pattern for client instances
    # Automatic health checks and error handling
    # Support for paper and live trading modes
```

### Testing Integration
Comprehensive test coverage with state isolation:

- **Unit Tests**: Individual tool and resource functions
- **Integration Tests**: Complete workflow scenarios
- **State Tests**: Memory management and cleanup
- **Mock Integration**: Realistic Alpaca API simulation

## Scalability Considerations

### Memory Management
- **Efficient Storage**: Entities store only essential characteristics
- **Memory Monitoring**: Built-in usage tracking and reporting
- **Cleanup Mechanisms**: Automatic state cleanup for testing
- **Bounded Growth**: Portfolio entities have natural limits

### Performance Optimization
- **Client Reuse**: Singleton Alpaca clients reduce connection overhead
- **Async Operations**: Non-blocking execution throughout
- **Selective Data**: Only fetch required data for each operation
- **State Caching**: Avoid redundant API calls for same symbols

### Extensibility Design
- **Plugin Architecture**: Easy to add new tool categories
- **Resource Extensibility**: Simple URI scheme extension
- **Entity Types**: Extensible classification system
- **Prompt Templates**: Reusable patterns for new prompts

## Security Architecture

### Data Protection
- **Credential Management**: Environment-based configuration
- **Error Sanitization**: No sensitive data in error messages
- **Input Validation**: Comprehensive parameter checking
- **Paper Trading**: Safe default configuration

### API Security
- **Client Isolation**: Centralized connection management
- **Health Monitoring**: Automatic client health checks
- **Error Boundaries**: Exceptions contained within tools
- **Rate Limiting**: Natural rate limiting through async patterns

## Monitoring and Observability

### Built-in Monitoring
- **System Health**: Comprehensive health check endpoints
- **Memory Usage**: Real-time memory tracking
- **Client Status**: Alpaca API connection monitoring
- **State Inspection**: Portfolio and entity examination

### Logging Strategy
- **Structured Logging**: Consistent log formats throughout
- **Error Tracking**: Detailed error context and types
- **Operation Tracing**: Tool execution tracking
- **Debug Support**: Configurable log levels

## Deployment Architecture

### Development Deployment
```bash
# Local development with hot reload
LOG_LEVEL=DEBUG uv run python main.py

# Testing with coverage
uv run python -m pytest tests/ -v --cov=src
```

### Production Deployment
```bash
# Docker containerization
docker build -t alpaca-mcp-gold .
docker run -p 8000:8000 --env-file .env alpaca-mcp-gold

# Environment configuration
ALPACA_API_KEY=xxx
ALPACA_SECRET_KEY=xxx
ALPACA_PAPER_TRADE=false  # Live trading
LOG_LEVEL=INFO
```

### Client Configuration
```json
{
  "mcpServers": {
    "alpaca-trading-gold": {
      "command": "/path/to/uv",
      "args": ["--directory", "/path/to/project", "run", "python", "main.py"],
      "env": {"LOG_LEVEL": "INFO"}
    }
  }
}
```

This architecture provides a robust, scalable, and maintainable foundation for professional MCP server development, implementing all gold standard patterns for optimal Claude Code integration.