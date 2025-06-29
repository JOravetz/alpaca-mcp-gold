# Setup Guide - Alpaca MCP Gold Standard

## Quick Setup for Claude Code

### 1. Configure Environment
```bash
# Copy environment template
cp .env.example .env

# Edit with your Alpaca credentials
nano .env
```

Add your Alpaca API credentials to `.env`:
```env
ALPACA_API_KEY=your_api_key_here
ALPACA_SECRET_KEY=your_secret_key_here
ALPACA_PAPER_TRADE=True
MCP_SERVER_NAME=alpaca-trading-gold
LOG_LEVEL=INFO
```

### 2. Install Dependencies
```bash
# Install dependencies
uv sync

# Verify installation
uv run python -c "from src.mcp_server.server import mcp; print('✓ Server imports successfully')"
```

### 3. Test the Server
```bash
# Run basic test
uv run python main.py &
SERVER_PID=$!

# Kill test server
kill $SERVER_PID

# Run comprehensive tests
uv run python -m pytest tests/ -v
```

### 4. Connect with Claude Code

The `.mcp.json` file is already configured for this project. To connect:

1. **Start Claude Code** in this directory:
   ```bash
   claude-code /home/jjoravet/mcp_server_best_practices/alpaca-mcp-gold-standard
   ```

2. **The server will auto-connect** using the `.mcp.json` configuration

3. **Verify connection** by trying a command:
   ```
   Test the MCP server connection
   ```

### 5. Alternative: Manual MCP Configuration

If you prefer manual configuration, add to your MCP client config:

```json
{
  "mcpServers": {
    "alpaca-trading-gold": {
      "command": "/home/jjoravet/.local/bin/uv",
      "args": [
        "--directory",
        "/home/jjoravet/mcp_server_best_practices/alpaca-mcp-gold-standard",
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

## Getting Started Commands

Once connected, try these commands with Claude Code:

### Basic Portfolio Analysis
```
Get my account information and current positions
```

### Market Research
```
Get a comprehensive snapshot for AAPL
```

### Interactive Prompts
```
Start a portfolio first look session
```

### Resource Access
```
Show me all available trading resources
```

## Troubleshooting

### Common Issues

**Server won't start:**
```bash
# Check dependencies
uv sync

# Verify Python version
python --version  # Should be 3.12+

# Check for syntax errors
uv run python -m py_compile src/mcp_server/server.py
```

**API Connection Issues:**
```bash
# Verify credentials in .env file
cat .env | grep ALPACA

# Test API connection
uv run python -c "
from src.mcp_server.models.alpaca_clients import AlpacaClientManager
health = AlpacaClientManager.health_check()
print(health)
"
```

**MCP Connection Issues:**
```bash
# Check uv path
which uv

# Update .mcp.json if uv path differs
# Restart Claude Code
```

### Debug Mode

For detailed logging:
```bash
LOG_LEVEL=DEBUG uv run python main.py
```

### Health Check

Verify all components:
```bash
uv run python -c "
from src.mcp_server.server import mcp
from src.mcp_server.models.alpaca_clients import AlpacaClientManager

print('🔍 Server Health Check:')
print(f'✓ Server name: {mcp.name}')
print(f'✓ Tools registered: {len(list(mcp.list_tools()))}')
print(f'✓ Resources registered: {len(list(mcp.list_resources()))}')
print(f'✓ Prompts registered: {len(list(mcp.list_prompts()))}')

health = AlpacaClientManager.health_check()
print(f'✓ Alpaca health: {health}')
"
```

## Security Notes

- **Never commit** your `.env` file with real credentials
- **Use paper trading** (`ALPACA_PAPER_TRADE=True`) for development
- **Validate** all API credentials before live trading
- **Monitor** your account for unexpected activity

## Support

For issues specific to this gold standard implementation:
1. Check the comprehensive test suite: `uv run python -m pytest tests/ -v`
2. Review the AI development guide: `ai_docs/development_guide.md`
3. Examine the architecture documentation: `specs/architecture_overview.md`

This setup provides you with the complete Alpaca MCP Gold Standard experience with full Claude Code integration!